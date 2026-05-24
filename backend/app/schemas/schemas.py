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
    amount: int  # Amount in cents
    type: TransactionType
    description: str

class Transaction(TransactionBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class Wallet(BaseModel):
    balance: int  # Balance in cents
    transactions: List[Transaction] = []

    class Config:
        from_attributes = True

# Product schemas
class ProductBase(BaseModel):
    name: str
    description: str
    price: int  # Price in cents (e.g., 10000 = 100.00 yuan)
    stock: int = 1
    image_url: Optional[str] = None
    images: Optional[str] = None  # JSON array string
    category: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    id: int
    status: ProductStatus
    merchant_id: int
    merchant_name: Optional[str] = None
    audit_remark: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Favorite schemas
class FavoriteCreate(BaseModel):
    product_id: int

class Favorite(BaseModel):
    id: int
    user_id: int
    product_id: int
    created_at: datetime
    product: Optional[Product] = None

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
    total_price: int
    status: OrderStatus
    tracking_number: Optional[str] = None
    paid_at: Optional[datetime] = None
    shipped_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

# ShoppingCart schemas
class CartItemCreate(BaseModel):
    product_id: int
    quantity: int = 1

class CartItemUpdate(BaseModel):
    quantity: int

class CartItem(BaseModel):
    id: int
    user_id: int
    product_id: int
    quantity: int
    created_at: datetime
    product: Optional[Product] = None

    class Config:
        from_attributes = True

class CartCheckout(BaseModel):
    item_ids: List[int]  # cart item ids to checkout


# Review schemas
class ReviewCreate(BaseModel):
    order_id: int
    rating: int  # 1-5
    comment: str

class ReviewReply(BaseModel):
    reply: str

class Review(BaseModel):
    id: int
    order_id: int
    reviewer_id: int
    merchant_id: int
    product_id: int
    rating: int
    comment: str
    reply: Optional[str] = None
    created_at: datetime
    reviewer_name: Optional[str] = None

    class Config:
        from_attributes = True


# Notification schemas
class Notification(BaseModel):
    id: int
    user_id: int
    title: str
    content: str
    n_type: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Dashboard stats
class DashboardStats(BaseModel):
    total_users: int
    total_orders: int
    total_revenue: int  # cents
    pending_users: int
    pending_products: int
    today_orders: int
    today_revenue: int
