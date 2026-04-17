from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Any

from app.api import deps
from app.core import security
from app.models.models import User, UserRole, Wallet, Transaction, TransactionType
from app.schemas import schemas
from app.db.session import get_db

router = APIRouter()

@router.post("/login/access-token", response_model=schemas.Token)
def login_access_token(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """OAuth2 compatible token login, retrieve an access token for future requests."""
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect username or password",
        )
    if not user.is_verified and user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Registration pending approval from Administrator",
        )
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            {"username": user.username, "role": user.role}, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

@router.post("/register", response_model=schemas.User)
def register_user(
    *,
    db: Session = Depends(get_db),
    user_in: schemas.UserCreate,
    background_tasks: BackgroundTasks,
) -> Any:
    """Create new user registration (Pending Administrator Approval)."""
    user = db.query(User).filter(User.username == user_in.username).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    
    # Check email
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )

    # Note: Admin users are auto-verified for the first time/manual setup
    # Regular users and merchants are not verified until an admin approves them.
    db_user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=security.get_password_hash(user_in.password),
        role=user_in.role,
        is_verified=False if user_in.role != UserRole.ADMIN else True,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Initialize wallet for every new user
    wallet = Wallet(user_id=db_user.id, balance=0.0)
    db.add(wallet)
    db.commit()

    # Notify Admin about new user registration
    from app.core.websocket_manager import manager
    notification_payload = {
        "type": "admin_event",
        "message": f"管理提醒：新用户 [{db_user.username}] 注册，等待审核。",
        "data": {"user_id": db_user.id, "username": db_user.username}
    }
    background_tasks.add_task(manager.broadcast, notification_payload)
    
    return db_user
