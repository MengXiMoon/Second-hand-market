from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.models.models import Product, ProductStatus, User, UserRole
from app.schemas import schemas
from app.db.session import get_db

router = APIRouter()

@router.get("/", response_model=List[schemas.Product])
def read_products(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """Retrieve all approved products (Public)."""
    return db.query(Product).filter(Product.status == ProductStatus.APPROVED).offset(skip).limit(limit).all()

@router.post("/", response_model=schemas.Product)
def create_product(
    *,
    db: Session = Depends(get_db),
    product_in: schemas.ProductCreate,
    current_user: User = Depends(deps.get_current_merchant),
) -> Any:
    """Upload a new product (Merchant only, Pending Audit)."""
    product = Product(
        **product_in.dict(),
        merchant_id=current_user.id,
        status=ProductStatus.PENDING # Default to pending for audit
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

@router.get("/my", response_model=List[schemas.Product])
def read_my_products(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_merchant),
) -> Any:
    """Retrieve products owned by the current merchant."""
    return db.query(Product).filter(Product.merchant_id == current_user.id).all()

@router.get("/pending", response_model=List[schemas.Product])
def read_pending_products(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """List products awaiting audit (Admin only)."""
    return db.query(Product).filter(Product.status == ProductStatus.PENDING).all()

@router.put("/{product_id}/audit", response_model=schemas.Product)
def audit_product(
    product_id: int,
    approve: bool,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """Approve or reject a product listing (Admin only)."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product.status = ProductStatus.APPROVED if approve else ProductStatus.REJECTED
    db.commit()
    db.refresh(product)
    return product

@router.put("/{product_id}/status", response_model=schemas.Product)
def update_product_status(
    product_id: int,
    status: ProductStatus,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_merchant),
) -> Any:
    """Update product status (e.g., Sold out, Merchant only). Administrators can also modify."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check ownership
    if product.merchant_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized to modify this product")
    
    product.status = status
    db.commit()
    db.refresh(product)
    return product
