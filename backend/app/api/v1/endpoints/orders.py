from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session

from app.api import deps
from app.db.session import get_db
from app.models.models import User, UserRole, ShoppingCart, Product
from app.schemas import schemas
from app.services import order_service

router = APIRouter()

# ==================== 订单 ====================


@router.post("/", response_model=schemas.Order)
def create_order(
    *,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    order_in: schemas.OrderCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """下单（状态=ordered，不扣款）"""
    return order_service.place_order(
        db=db, product_id=order_in.product_id,
        current_user=current_user, background_tasks=background_tasks,
    )


@router.put("/{order_id}/pay", response_model=schemas.Order)
def pay_order(
    order_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """付款（扣钱包，状态→paid，资金托管）"""
    return order_service.pay_order(
        db=db, order_id=order_id, current_user=current_user,
        background_tasks=background_tasks,
    )


@router.put("/{order_id}/ship", response_model=schemas.Order)
def ship_order(
    order_id: int,
    background_tasks: BackgroundTasks,
    tracking_number: str = Query(..., description="物流单号"),
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_merchant),
) -> Any:
    """卖家发货（状态→shipped）"""
    return order_service.ship_order(
        db=db, order_id=order_id, tracking_number=tracking_number,
        current_user=current_user, background_tasks=background_tasks,
    )


@router.put("/{order_id}/complete", response_model=schemas.Order)
def complete_order(
    order_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """确认收货（状态→completed，结算给商家）"""
    return order_service.complete_order(
        db=db, order_id=order_id, current_user=current_user,
        background_tasks=background_tasks,
    )


@router.put("/{order_id}/cancel", response_model=schemas.Order)
def cancel_order(
    order_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """取消订单/退款"""
    return order_service.cancel_order(
        db=db, order_id=order_id, current_user=current_user,
        background_tasks=background_tasks,
    )


@router.get("/my", response_model=List[schemas.Order])
def read_my_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """我的订单（按时间倒序）"""
    from sqlalchemy import desc
    return db.query(order_service.Order).filter(
        order_service.Order.buyer_id == current_user.id
    ).order_by(desc(order_service.Order.created_at)).all()


@router.get("/sales", response_model=List[schemas.Order])
def read_sales(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_merchant),
) -> Any:
    """商家销售记录"""
    from sqlalchemy import desc
    merchant_products = db.query(Product.id).filter(
        Product.merchant_id == current_user.id
    ).subquery()
    return db.query(order_service.Order).filter(
        order_service.Order.product_id.in_(merchant_products)
    ).order_by(desc(order_service.Order.created_at)).all()


@router.get("/all", response_model=List[schemas.Order])
def read_all_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """管理员查看全站订单"""
    from sqlalchemy import desc
    return db.query(order_service.Order).order_by(desc(order_service.Order.created_at)).all()


# ==================== 购物车 ====================


@router.get("/cart", response_model=List[schemas.CartItem])
def get_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """获取我的购物车（自动合并同商品的重复行）"""
    rows = db.query(ShoppingCart).filter(
        ShoppingCart.user_id == current_user.id
    ).order_by(ShoppingCart.created_at).all()

    # 合并同一商品的重复行
    seen = {}
    for r in rows:
        if r.product_id in seen:
            seen[r.product_id].quantity += r.quantity
            db.delete(r)
        else:
            seen[r.product_id] = r
    db.commit()

    items = list(seen.values())
    # Refresh items that were modified
    for item in items:
        db.refresh(item)
        _ = item.product
    return items


@router.post("/cart", response_model=schemas.CartItem)
def add_to_cart(
    cart_in: schemas.CartItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """加入购物车（同一商品去重累加数量，不超过库存上限）"""
    from sqlalchemy import func

    product = db.query(Product).filter(Product.id == cart_in.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="商品不存在")

    # 查询该商品所有购物车行（可能有历史遗留的重复行）
    rows = db.query(ShoppingCart).filter(
        ShoppingCart.user_id == current_user.id,
        ShoppingCart.product_id == cart_in.product_id,
    ).all()

    # 汇总已有数量
    existing_total = sum(r.quantity for r in rows)
    new_total = existing_total + cart_in.quantity
    if new_total > product.stock:
        new_total = product.stock
        if existing_total >= product.stock:
            raise HTTPException(status_code=400, detail=f"已达到库存上限 ({product.stock} 件)")

    # 合并为一行：保留第一条，删除其余
    first = rows[0] if rows else None
    for extra in rows[1:]:
        db.delete(extra)

    if first:
        first.quantity = new_total
        db.commit()
        db.refresh(first)
        _ = first.product
        return first

    item = ShoppingCart(
        user_id=current_user.id,
        product_id=cart_in.product_id,
        quantity=new_total,
    db.add(item)
    db.commit()
    db.refresh(item)
    _ = item.product
    return item


@router.put("/cart/{item_id}", response_model=schemas.CartItem)
def update_cart_item(
    item_id: int,
    update: schemas.CartItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """修改购物车商品数量"""
    item = db.query(ShoppingCart).filter(
        ShoppingCart.id == item_id, ShoppingCart.user_id == current_user.id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="购物车项不存在")
    if update.quantity <= 0:
        db.delete(item)
        db.commit()
        raise HTTPException(status_code=200, detail="已移除")
    item.quantity = update.quantity
    db.commit()
    db.refresh(item)
    _ = item.product
    return item


@router.delete("/cart/{item_id}")
def remove_cart_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """从购物车移除"""
    item = db.query(ShoppingCart).filter(
        ShoppingCart.id == item_id, ShoppingCart.user_id == current_user.id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="购物车项不存在")
    db.delete(item)
    db.commit()
    return {"message": "已移除"}


@router.post("/cart/checkout", response_model=List[schemas.Order])
def cart_checkout(
    *,
    background_tasks: BackgroundTasks,
    checkout: schemas.CartCheckout,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """购物车批量结算：勾选的商品一键生成多笔订单"""
    if not checkout.item_ids:
        raise HTTPException(status_code=400, detail="请选择要结算的商品")

    cart_items = db.query(ShoppingCart).filter(
        ShoppingCart.id.in_(checkout.item_ids),
        ShoppingCart.user_id == current_user.id,
    ).all()

    if not cart_items:
        raise HTTPException(status_code=400, detail="购物车中没有选中的商品")

    # 第一步：逐项生成订单（不提交、不删购物车）
    orders = []
    failed = []
    success_ids = []
    for item in cart_items:
        try:
            order = order_service.place_order(
                db=db, product_id=item.product_id,
                current_user=current_user, background_tasks=background_tasks,
                auto_commit=False,
            )
            orders.append(order)
            success_ids.append(item.id)
        except HTTPException as e:
            failed.append(f"#{item.product_id}: {e.detail}")

    if not orders:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"全部失败：{'；'.join(failed)}")

    # 第二步：统一提交订单 + 删除购物车项
    for item_id in success_ids:
        it = db.query(ShoppingCart).filter(ShoppingCart.id == item_id).first()
        if it:
            db.delete(it)
    db.commit()

    for order in orders:
        db.refresh(order)

    if failed:
        raise HTTPException(
            status_code=400,
            detail=f"{len(orders)} 笔下単成功，{len(failed)} 笔失败：{'；'.join(failed)}"
        )
    return orders
