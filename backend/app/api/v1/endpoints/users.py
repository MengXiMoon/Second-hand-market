from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.models.models import User, UserRole
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
