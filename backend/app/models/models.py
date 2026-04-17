from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime, Enum
from sqlalchemy.orm import relationship
import enum
from datetime import datetime, timedelta
from app.db.session import Base

def get_beijing_time():
    # Offset UTC by 8 hours for Beijing Time
    return datetime.utcnow() + timedelta(hours=8)

class UserRole(str, enum.Enum):
    USER = "user"
    MERCHANT = "merchant"
    ADMIN = "admin"

class ProductStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    SOLD_OUT = "sold_out"

class OrderStatus(str, enum.Enum):
    ORDERED = "ordered"
    PAID = "paid"
    SHIPPED = "shipped"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class TransactionType(str, enum.Enum):
    RECHARGE = "recharge"
    PURCHASE = "purchase"
    SALE = "sale"
    REFUND = "refund"
    WITHDRAW = "withdraw"
    COMMISSION = "commission"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(Enum(UserRole), default=UserRole.USER)
    is_verified = Column(Boolean, default=False) # Admin must verify registration
    created_at = Column(DateTime, default=get_beijing_time)

    products = relationship("Product", back_populates="merchant")
    orders = relationship("Order", back_populates="buyer")
    wallet = relationship("Wallet", back_populates="user", uselist=False)

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    price = Column(Float)
    stock = Column(Integer, default=1)
    status = Column(Enum(ProductStatus), default=ProductStatus.PENDING)
    merchant_id = Column(Integer, ForeignKey("users.id"))
    audit_remark = Column(String, nullable=True)
    created_at = Column(DateTime, default=get_beijing_time)

    merchant = relationship("User", back_populates="products")

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    buyer_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    total_price = Column(Float)
    status = Column(Enum(OrderStatus), default=OrderStatus.ORDERED)
    created_at = Column(DateTime, default=get_beijing_time)

    buyer = relationship("User", back_populates="orders")
    product = relationship("Product")

class Wallet(Base):
    __tablename__ = "wallets"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    balance = Column(Float, default=0.0)

    user = relationship("User", back_populates="wallet")
    transactions = relationship("Transaction", back_populates="wallet")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    wallet_id = Column(Integer, ForeignKey("wallets.user_id"))
    amount = Column(Float)
    type = Column(Enum(TransactionType))
    description = Column(String)
    created_at = Column(DateTime, default=get_beijing_time)

    wallet = relationship("Wallet", back_populates="transactions")
