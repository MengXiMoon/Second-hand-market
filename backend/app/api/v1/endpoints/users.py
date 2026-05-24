from typing import Any, List
from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.core.session_manager import session_manager
from app.models.models import User, UserRole, Transaction, Wallet, Order, Product, MessageType
from app.schemas import schemas
from app.db.session import get_db
from app.services.chat_service import find_or_create_conversation, create_message
from app.services.notification_service import push_notification

router = APIRouter()

@router.post("/{user_id}/force-logout")
def force_logout(
    user_id: int,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """管理员强制下线某用户，释放其登录会话"""
    session_manager.logout(user_id)
    return {"message": f"用户 {user_id} 已被强制下线"}

@router.get("/", response_model=List[schemas.User])
def read_users(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """Retrieve all users (Admin only)."""
    users = db.query(User).offset(skip).limit(limit).all()
    return users

@router.get("/me", response_model=schemas.User)
def read_user_me(
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Get current user information."""
    return current_user

@router.put("/{user_id}/verify", response_model=schemas.User)
def verify_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """Verify (audit) a user registration (Admin only)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_verified = True
    db.commit()
    db.refresh(user)

    push_notification(db, user.id, "账号审核通过",
                      "您的注册申请已通过审核，欢迎加入！", "user_verified")

    # 自动发送审核通过欢迎消息
    conv = find_or_create_conversation(db, current_user.id, user.id)
    create_message(
        db, conv.id, current_user.id,
        f"【系统通知】您的账号「{user.username}」已通过审核，欢迎加入！如有问题可在此联系客服。",
        MessageType.SYSTEM,
    )

    return user

@router.get("/pending", response_model=List[schemas.User])
def read_pending_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """List users awaiting registration verification (Admin only)."""
    return db.query(User).filter(User.is_verified == False).all()

@router.delete("/{user_id}", response_model=schemas.User)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """Delete a user (Admin only). Used for rejecting user registration."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 不能删除管理员自己
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    
    # Delete user-related data (products, orders, wallet, transactions)
    db.query(Transaction).filter(Transaction.wallet_id == user_id).delete()
    db.query(Wallet).filter(Wallet.user_id == user_id).delete()
    db.query(Order).filter(Order.buyer_id == user_id).delete()
    db.query(Product).filter(Product.merchant_id == user_id).delete()
    
    # 最后删除用户
    db.delete(user)
    db.commit()
    return user


@router.get("/stats", response_model=schemas.DashboardStats)
def get_admin_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    today = datetime.now(timezone.utc).replace(tzinfo=None).replace(hour=0, minute=0, second=0, microsecond=0)
    from app.models.models import Order, Product

    total_users = db.query(User).count()
    total_orders = db.query(Order).count()
    total_revenue = db.query(Order).filter(Order.status == Order.OrderStatus.COMPLETED).all()
    total_revenue_cents = sum(o.total_price for o in total_revenue)
    pending_users = db.query(User).filter(User.is_verified == False).count()
    pending_products = db.query(Product).filter(Product.status == Product.ProductStatus.PENDING).count()
    today_orders = db.query(Order).filter(Order.created_at >= today).count()
    today_revenue = db.query(Order).filter(Order.created_at >= today, Order.status == Order.OrderStatus.COMPLETED).all()
    today_revenue_cents = sum(o.total_price for o in today_revenue)

    return schemas.DashboardStats(
        total_users=total_users,
        total_orders=total_orders,
        total_revenue=total_revenue_cents,
        pending_users=pending_users,
        pending_products=pending_products,
        today_orders=today_orders,
        today_revenue=today_revenue_cents,
    )
