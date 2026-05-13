from datetime import datetime, timedelta, timezone

from fastapi import BackgroundTasks, HTTPException
from sqlalchemy.orm import Session

from app.models.models import (
    Order, OrderStatus, Product, ProductStatus,
    Wallet, Transaction, TransactionType, User, UserRole,
    MessageType,
)
from app.core.websocket_manager import manager
from app.services.chat_service import find_or_create_conversation, create_message


def _get_commission(price: int) -> int:
    return max(price // 100, 1)  # 1%, minimum 1 cent


def place_order(
    *,
    db: Session,
    product_id: int,
    current_user: User,
    background_tasks: BackgroundTasks,
) -> Order:
    """下单：仅创建订单，状态=ordered，不扣款"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")
    if product.status != ProductStatus.APPROVED:
        raise HTTPException(status_code=400, detail="该商品暂不可购买")
    if product.stock < 1:
        raise HTTPException(status_code=400, detail="商品库存不足")
    if product.merchant_id == current_user.id:
        raise HTTPException(status_code=400, detail="不能购买自己发布的商品")

    # 下单即扣库存（防止超卖）
    product.stock -= 1
    if product.stock == 0:
        product.status = ProductStatus.SOLD_OUT

    order = Order(
        buyer_id=current_user.id,
        product_id=product.id,
        total_price=product.price,
        status=OrderStatus.ORDERED,
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    # 通知商家
    background_tasks.add_task(
        manager.send_personal_message,
        {"type": "new_order", "message": f"您有新的订单！商品：{product.name}",
         "data": {"order_id": order.id, "product_name": product.name}},
        product.merchant_id,
    )

    return order


def pay_order(
    *,
    db: Session,
    order_id: int,
    current_user: User,
    background_tasks: BackgroundTasks,
) -> Order:
    """付款：扣钱包，状态 → paid，资金暂由平台托管"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if order.buyer_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权操作此订单")
    if order.status != OrderStatus.ORDERED:
        raise HTTPException(status_code=400, detail="订单状态不正确，无法付款")

    # 检查超时（30 分钟未付款自动取消）
    expire_time = order.created_at + timedelta(minutes=30)
    if datetime.now(timezone.utc).replace(tzinfo=None) > expire_time:
        order.status = OrderStatus.CANCELLED
        db.commit()
        raise HTTPException(status_code=400, detail="订单已超时自动取消")

    wallet = db.query(Wallet).filter(Wallet.user_id == current_user.id).first()
    if not wallet or wallet.balance < order.total_price:
        raise HTTPException(status_code=400, detail="钱包余额不足")

    # 扣款（资金暂由平台托管，待确认收货后结算给商家）
    wallet.balance -= order.total_price
    txn = Transaction(
        wallet_id=current_user.id,
        amount=-order.total_price,
        type=TransactionType.PURCHASE,
        description=f"购买订单 #{order.id}（资金托管中）",
    )
    db.add(txn)

    order.status = OrderStatus.PAID
    order.paid_at = datetime.now(timezone.utc).replace(tzinfo=None)
    db.commit()
    db.refresh(order)

    # 自动创建对话 + 通知
    product = db.query(Product).filter(Product.id == order.product_id).first()
    if product:
        conv = find_or_create_conversation(db, current_user.id, product.merchant_id)
        create_message(
            db, conv.id, current_user.id,
            f"我已付款购买商品「{product.name}」(订单号: {order.id})",
            MessageType.TEXT,
        )

        background_tasks.add_task(
            manager.send_personal_message,
            {"type": "new_order", "message": f"买家已付款！商品：{product.name}",
             "data": {"order_id": order.id}},
            product.merchant_id,
        )

    return order


def ship_order(
    *,
    db: Session,
    order_id: int,
    tracking_number: str,
    current_user: User,
    background_tasks: BackgroundTasks,
) -> Order:
    """卖家发货：填物流单号，状态 → shipped"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if order.status != OrderStatus.PAID:
        raise HTTPException(status_code=400, detail="订单状态不正确，无法发货")

    product = db.query(Product).filter(Product.id == order.product_id).first()
    if not product or product.merchant_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权操作此订单")

    order.tracking_number = tracking_number
    order.status = OrderStatus.SHIPPED
    order.shipped_at = datetime.now(timezone.utc).replace(tzinfo=None)
    db.commit()
    db.refresh(order)

    background_tasks.add_task(
        manager.send_personal_message,
        {"type": "admin_event", "message": f"订单 #{order.id} 已发货，物流单号：{tracking_number}",
         "data": {"order_id": order.id}},
        order.buyer_id,
    )

    return order


def complete_order(
    *,
    db: Session,
    order_id: int,
    current_user: User,
    background_tasks: BackgroundTasks,
) -> Order:
    """买家确认收货：状态 → completed，结算资金给商家"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if order.buyer_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权操作此订单")
    if order.status != OrderStatus.SHIPPED:
        raise HTTPException(status_code=400, detail="订单状态不正确，无法确认收货")

    # 结算：平台佣金 + 商家收款
    commission = _get_commission(order.total_price)
    merchant_amount = order.total_price - commission

    admin_user = db.query(User).filter(User.role == UserRole.ADMIN).first()
    if admin_user:
        admin_wallet = db.query(Wallet).filter(Wallet.user_id == admin_user.id).first()
        if admin_wallet:
            admin_wallet.balance += commission
            db.add(Transaction(
                wallet_id=admin_user.id, amount=commission,
                type=TransactionType.COMMISSION,
                description=f"订单 #{order.id} 平台佣金",
            ))

    merchant_wallet = db.query(Wallet).filter(Wallet.user_id == order.product.merchant_id).first()
    if merchant_wallet:
        merchant_wallet.balance += merchant_amount
        db.add(Transaction(
            wallet_id=merchant_wallet.user_id, amount=merchant_amount,
            type=TransactionType.SALE,
            description=f"订单 #{order.id} 销售收入（佣金 {commission}）",
        ))

    order.status = OrderStatus.COMPLETED
    order.completed_at = datetime.now(timezone.utc).replace(tzinfo=None)
    db.commit()
    db.refresh(order)

    background_tasks.add_task(
        manager.send_personal_message,
        {"type": "admin_event", "message": f"买家已确认收货，订单 #{order.id} 完成",
         "data": {"order_id": order.id}},
        order.product.merchant_id,
    )

    return order


def cancel_order(
    *,
    db: Session,
    order_id: int,
    current_user: User,
    background_tasks: BackgroundTasks,
) -> Order:
    """取消订单/退款"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    # 买家可取消自己的订单；管理员可取消任意订单
    is_admin = current_user.role == UserRole.ADMIN
    if order.buyer_id != current_user.id and not is_admin:
        raise HTTPException(status_code=403, detail="无权操作此订单")

    if order.status not in (OrderStatus.ORDERED, OrderStatus.PAID):
        raise HTTPException(status_code=400, detail="当前状态不可取消")

    # 已付款的需要退款
    if order.status == OrderStatus.PAID:
        buyer_wallet = db.query(Wallet).filter(Wallet.user_id == order.buyer_id).first()
        if buyer_wallet:
            buyer_wallet.balance += order.total_price
            db.add(Transaction(
                wallet_id=order.buyer_id, amount=order.total_price,
                type=TransactionType.REFUND,
                description=f"订单 #{order.id} 退款",
            ))

    # 取消后恢复库存（下单时已扣，取消时退回）
    product = db.query(Product).filter(Product.id == order.product_id).first()
    if product:
        product.stock += 1
        if product.status == ProductStatus.SOLD_OUT:
            product.status = ProductStatus.APPROVED

    order.status = OrderStatus.CANCELLED
    db.commit()
    db.refresh(order)

    reason = "退款" if order.paid_at else "取消"
    background_tasks.add_task(
        manager.send_personal_message,
        {"type": "admin_event", "message": f"订单 #{order.id} 已{reason}",
         "data": {"order_id": order.id}},
        order.product.merchant_id,
    )

    return order
