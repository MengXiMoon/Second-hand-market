from fastapi import BackgroundTasks, HTTPException
from sqlalchemy.orm import Session

from app.models.models import (
    Order, OrderStatus, Product, ProductStatus,
    Wallet, Transaction, TransactionType, User, UserRole,
    MessageType,
)
from app.core.websocket_manager import manager
from app.services.chat_service import find_or_create_conversation, create_message


def create_order(
    *,
    db: Session,
    product_id: int,
    current_user: User,
    background_tasks: BackgroundTasks,
) -> Order:
    """Create an order: validate, deduct funds, process commission, update stock, notify."""

    # --- Validate product ---
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product.status != ProductStatus.APPROVED:
        raise HTTPException(status_code=400, detail="Product is not available for purchase")
    if product.stock < 1:
        raise HTTPException(status_code=400, detail="Product is out of stock")
    if product.merchant_id == current_user.id:
        raise HTTPException(status_code=400, detail="不能购买自己发布的商品")

    # --- Validate wallet ---
    wallet = db.query(Wallet).filter(Wallet.user_id == current_user.id).first()
    if not wallet or wallet.balance < product.price:
        raise HTTPException(status_code=400, detail="Insufficient wallet balance")

    # --- Deduct from buyer ---
    wallet.balance -= product.price
    buyer_txn = Transaction(
        wallet_id=current_user.id,
        amount=-product.price,
        type=TransactionType.PURCHASE,
        description=f"Purchased {product.name}",
    )
    db.add(buyer_txn)

    # --- Platform commission (1%) ---
    commission = max(product.price // 100, 1)  # at least 1 cent
    merchant_amount = product.price - commission

    # Pay commission to admin
    admin_user = db.query(User).filter(User.role == UserRole.ADMIN).first()
    if admin_user:
        admin_wallet = db.query(Wallet).filter(Wallet.user_id == admin_user.id).first()
        if admin_wallet:
            admin_wallet.balance += commission
            admin_txn = Transaction(
                wallet_id=admin_user.id,
                amount=commission,
                type=TransactionType.COMMISSION,
                description=f"Commission from {product.name} sale (Buyer: {current_user.username})",
            )
            db.add(admin_txn)

    # --- Pay merchant (net of commission) ---
    merchant_wallet = db.query(Wallet).filter(Wallet.user_id == product.merchant_id).first()
    if merchant_wallet:
        merchant_wallet.balance += merchant_amount
        merchant_txn = Transaction(
            wallet_id=product.merchant_id,
            amount=merchant_amount,
            type=TransactionType.SALE,
            description=f"Sold {product.name} (Platform fee: {commission})",
        )
        db.add(merchant_txn)

    # --- Update stock ---
    product.stock -= 1
    if product.stock == 0:
        product.status = ProductStatus.SOLD_OUT

    # --- Create order ---
    order = Order(
        buyer_id=current_user.id,
        product_id=product.id,
        total_price=product.price,
        status=OrderStatus.PAID,
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    # --- Auto-create conversation & chat message ---
    conv = find_or_create_conversation(db, current_user.id, product.merchant_id)
    chat_msg = create_message(
        db,
        conversation_id=conv.id,
        sender_id=current_user.id,
        content=f"我已下单商品：{product.name} (订单号: {order.id})",
        msg_type=MessageType.TEXT,
    )

    # --- WebSocket notifications ---
    # Notify merchant
    background_tasks.add_task(
        manager.send_personal_message,
        {"type": "new_order", "message": f"您有新的订单！商品：{product.name}",
         "data": {"order_id": order.id, "product_name": product.name}},
        product.merchant_id,
    )

    # Chat message to both participants
    chat_payload = {
        "type": "chat_message",
        "data": {
            "id": chat_msg.id,
            "conversation_id": conv.id,
            "sender_id": current_user.id,
            "sender_name": current_user.username,
            "content": chat_msg.content,
            "msg_type": "text",
            "timestamp": chat_msg.timestamp.isoformat(),
        },
    }
    background_tasks.add_task(manager.send_personal_message, chat_payload, current_user.id)
    background_tasks.add_task(manager.send_personal_message, chat_payload, product.merchant_id)

    # Notify admins
    background_tasks.add_task(
        manager.broadcast,
        {"type": "admin_event",
         "message": f"管理提醒：全站新订单！用户 [{current_user.username}] 购买了 [{product.name}]。",
         "data": {"order_id": order.id, "product_name": product.name}},
    )

    return order
