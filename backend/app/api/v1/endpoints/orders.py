from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.models.models import Order, OrderStatus, Product, ProductStatus, Wallet, Transaction, TransactionType, User, UserRole
from app.schemas import schemas
from app.db.session import get_db

router = APIRouter()

@router.post("/", response_model=schemas.Order)
def create_order(
    *,
    db: Session = Depends(get_db),
    order_in: schemas.OrderCreate,
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Create a new order (Purchase Product)."""
    product = db.query(Product).filter(Product.id == order_in.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product.status != ProductStatus.APPROVED:
        raise HTTPException(status_code=400, detail="Product is not available for purchase")
    if product.stock < 1:
        raise HTTPException(status_code=400, detail="Product is out of stock")
    
    # Check balance
    wallet = db.query(Wallet).filter(Wallet.user_id == current_user.id).first()
    if not wallet or wallet.balance < product.price:
        raise HTTPException(status_code=400, detail="Insufficient wallet balance")

    # Transaction: Deduct from buyer
    wallet.balance -= product.price
    buyer_transaction = Transaction(
        wallet_id=current_user.id,
        amount=-product.price,
        type=TransactionType.PURCHASE,
        description=f"Purchased {product.name}"
    )
    db.add(buyer_transaction)

    # Transaction: Add to merchant
    merchant_wallet = db.query(Wallet).filter(Wallet.user_id == product.merchant_id).first()
    if merchant_wallet:
        merchant_wallet.balance += product.price
        merchant_transaction = Transaction(
            wallet_id=product.merchant_id,
            amount=product.price,
            type=TransactionType.SALE,
            description=f"Sold {product.name}"
        )
        db.add(merchant_transaction)

    # Update product stock
    product.stock -= 1
    if product.stock == 0:
        product.status = ProductStatus.SOLD_OUT
    
    # Create order
    order = Order(
        buyer_id=current_user.id,
        product_id=product.id,
        total_price=product.price,
        status=OrderStatus.PAID # Assuming payment is immediate for simplicity
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order

@router.get("/my", response_model=List[schemas.Order])
def read_my_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """Retrieve orders purchased by the current user."""
    return db.query(Order).filter(Order.buyer_id == current_user.id).all()

@router.get("/sales", response_model=List[schemas.Order])
def read_my_sales(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_merchant),
) -> Any:
    """Retrieve orders for products owned by the current merchant."""
    return db.query(Order).join(Product).filter(Product.merchant_id == current_user.id).all()

@router.get("/all", response_model=List[schemas.Order])
def read_all_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """Retrieve all orders in the system (admin only)."""
    return db.query(Order).all()
