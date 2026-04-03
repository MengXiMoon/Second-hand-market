from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

from app.db.session import get_db
from app.models.models import User, UserRole
from app.schemas.schemas import TokenData
from app.core import security

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "replace_me_with_something_secure")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl="v1/login/access-token"
)

def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> User:
    try:
        payload = jwt.decode(
            token, SECRET_KEY, algorithms=[ALGORITHM]
        )
        token_data = TokenData(**payload)
        if token_data.username is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Could not validate credentials",
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = db.query(User).filter(User.username == token_data.username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_verified and user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="User registration is pending approval")
    return user

def get_current_active_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user

def get_current_merchant(
    current_user: User = Depends(get_current_user),
) -> User:
    if current_user.role != UserRole.MERCHANT and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403, detail="Only merchants can perform this action"
        )
    return current_user
