from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from app.models.models import UserRole, ProductStatus, OrderStatus, TransactionType

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[UserRole] = None

# User schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str
    role: UserRole = UserRole.USER

class User(UserBase):
    id: int
    role: UserRole
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Wallet & Transaction schemas
class TransactionBase(BaseModel):
    amount: float
    type: TransactionType
    description: str

class Transaction(TransactionBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class Wallet(BaseModel):
    balance: float
    transactions: List[Transaction] = []

    class Config:
        from_attributes = True

# Product schemas
class ProductBase(BaseModel):
    name: str
    description: str
    price: float
    stock: int = 1

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int
    status: ProductStatus
    merchant_id: int
    audit_remark: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Order schemas
class OrderBase(BaseModel):
    product_id: int

class OrderCreate(OrderBase):
    pass

class Order(OrderBase):
    id: int
    buyer_id: int
    total_price: float
    status: OrderStatus
    created_at: datetime

    class Config:
        from_attributes = True
