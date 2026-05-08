from typing import Any, List
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session

from app.api import deps
from app.models.models import Order, Product, User
from app.schemas import schemas
from app.db.session import get_db
from app.services.order_service import create_order as create_order_service

router = APIRouter()


@router.post("/", response_model=schemas.Order)
def create_order(
    *,
    db: Session = Depends(get_db),
    order_in: schemas.OrderCreate,
    current_user: User = Depends(deps.get_current_user),
    background_tasks: BackgroundTasks,
) -> Any:
    """Create a new order (Purchase Product)."""
    return create_order_service(
        db=db,
        product_id=order_in.product_id,
        current_user=current_user,
        background_tasks=background_tasks,
    )


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
