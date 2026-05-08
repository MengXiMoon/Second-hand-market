from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.models.models import User, UserRole, Transaction, Wallet, Order, Product
from app.schemas import schemas
from app.db.session import get_db

router = APIRouter()

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
