from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
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
    background_tasks: BackgroundTasks,
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

    # Notify Admin about new product audit request
    from app.core.websocket_manager import manager
    notification_payload = {
        "type": "admin_event",
        "message": f"管理提醒：商家 [{current_user.username}] 发布了新商品 [{product.name}]，等待审核。",
        "data": {"product_id": product.id, "product_name": product.name}
    }
    background_tasks.add_task(manager.broadcast, notification_payload)

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
    background_tasks: BackgroundTasks,
    remark: str = None, # Optional reason
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    """Approve or reject a product listing (Admin only)."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    status_label = "通过" if approve else "驳回"
    product.status = ProductStatus.APPROVED if approve else ProductStatus.REJECTED
    product.audit_remark = remark
    db.commit()
    db.refresh(product)

    # Real-time Notification for Merchant
    from app.core.websocket_manager import manager
    notification_payload = {
        "type": "product_audit",
        "message": f"商品审核通知：您的商品 [{product.name}] 已被管理员{status_label}。{f'理由：{remark}' if remark else ''}",
        "data": {
            "product_id": product.id,
            "status": product.status,
            "product_name": product.name,
            "remark": remark
        }
    }
    background_tasks.add_task(manager.send_personal_message, notification_payload, product.merchant_id)

    return product

@router.put("/{product_id}", response_model=schemas.Product)
def update_product(
    *,
    db: Session = Depends(get_db),
    product_id: int,
    product_in: schemas.ProductBase,
    current_user: User = Depends(deps.get_current_merchant),
) -> Any:
    """Update a product and reset status to pending (Merchant only)."""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product.merchant_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Update fields from product_in
    for field, value in product_in.dict().items():
        setattr(product, field, value)
    
    # Reset status to pending for re-audit if it was rejected or approved
    product.status = ProductStatus.PENDING
    product.audit_remark = None # Clear old remark
    
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
