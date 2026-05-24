from typing import Any, List, Optional

import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query, UploadFile, File
from sqlalchemy.orm import Session, joinedload

from app.api import deps
from app.models.models import Product, ProductStatus, User, UserRole, MessageType, Favorite
from app.schemas import schemas
from app.db.session import get_db
from app.core.websocket_manager import manager
from app.services.chat_service import find_or_create_conversation, create_message
from app.services.notification_service import push_notification
from app.core.config import settings

CATEGORIES = ["电子产品", "图书音像", "家具家居", "服装鞋帽", "家用电器", "运动户外", "其他"]

router = APIRouter()


def _enrich_merchant_name(products, db):
    """为商品列表填充 merchant_name"""
    ids = {p.merchant_id for p in products}
    users = {u.id: u.username for u in db.query(User).filter(User.id.in_(ids)).all()} if ids else {}
    for p in products:
        p.merchant_name = users.get(p.merchant_id, "未知")


# ==================== 商品 ====================


@router.get("/", response_model=List[schemas.Product])
def read_products(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    keyword: Optional[str] = Query(None, description="搜索关键词"),
    category: Optional[str] = Query(None, description="商品分类"),
    min_price: Optional[int] = Query(None, description="最低价格（元）"),
    max_price: Optional[int] = Query(None, description="最高价格（元）"),
    sort: Optional[str] = Query("newest", description="排序方式: newest / price_asc / price_desc"),
) -> Any:
    """检索已上架商品，支持搜索、分类、价格筛选、排序"""
    q = db.query(Product).options(joinedload(Product.merchant)).filter(Product.status == ProductStatus.APPROVED)

    if keyword:
        q = q.filter(Product.name.contains(keyword))
    if category:
        q = q.filter(Product.category == category)
    if min_price is not None:
        q = q.filter(Product.price >= min_price * 100)
    if max_price is not None:
        q = q.filter(Product.price <= max_price * 100)

    if sort == "price_asc":
        q = q.order_by(Product.price.asc())
    elif sort == "price_desc":
        q = q.order_by(Product.price.desc())
    else:
        q = q.order_by(Product.created_at.desc())

    products = q.offset(skip).limit(limit).all()
    _enrich_merchant_name(products, db)
    return products


@router.get("/categories")
def get_categories() -> Any:
    """获取商品分类列表"""
    return {"categories": CATEGORIES}


@router.post("/", response_model=schemas.Product)
def create_product(
    *,
    db: Session = Depends(get_db),
    product_in: schemas.ProductCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(deps.get_current_merchant),
) -> Any:
    """商品上架（需审核）"""
    product = Product(
        **product_in.dict(),
        merchant_id=current_user.id,
        status=ProductStatus.PENDING,
    )
    db.add(product)
    db.commit()
    db.refresh(product)

    notification_payload = {
        "type": "admin_event",
        "message": f"管理提醒：商家 [{current_user.username}] 发布了新商品 [{product.name}]，等待审核。",
        "data": {"product_id": product.id, "product_name": product.name},
    }
    background_tasks.add_task(manager.broadcast, notification_payload)

    return product


@router.get("/my", response_model=List[schemas.Product])
def read_my_products(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_merchant),
) -> Any:
    products = db.query(Product).options(joinedload(Product.merchant)).filter(
        Product.merchant_id == current_user.id
    ).order_by(Product.created_at.desc()).all()
    _enrich_merchant_name(products, db)
    return products


@router.get("/pending", response_model=List[schemas.Product])
def read_pending_products(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    products = db.query(Product).options(joinedload(Product.merchant)).filter(
        Product.status == ProductStatus.PENDING
    ).all()
    _enrich_merchant_name(products, db)
    return products


@router.put("/{product_id}/audit", response_model=schemas.Product)
def audit_product(
    product_id: int,
    approve: bool,
    background_tasks: BackgroundTasks,
    remark: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_admin),
) -> Any:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    status_label = "通过" if approve else "驳回"
    product.status = ProductStatus.APPROVED if approve else ProductStatus.REJECTED
    product.audit_remark = remark
    db.commit()
    db.refresh(product)

    notification_payload = {
        "type": "product_audit",
        "message": f"商品审核通知：您的商品 [{product.name}] 已被管理员{status_label}。{f'理由：{remark}' if remark else ''}",
        "data": {"product_id": product.id, "status": product.status, "product_name": product.name, "remark": remark},
    }
    background_tasks.add_task(manager.send_personal_message, notification_payload, product.merchant_id)

    push_notification(db, product.merchant_id, "商品审核通知",
                      f"您的商品「{product.name}」已{status_label}", "product_audit")

    conv = find_or_create_conversation(db, current_user.id, product.merchant_id)
    remark_text = f" 驳回原因：{remark}" if remark and not approve else ""
    create_message(
        db, conv.id, current_user.id,
        f"【审核通知】您的商品「{product.name}」已{status_label}{remark_text}",
        MessageType.SYSTEM,
    )

    return product


@router.put("/{product_id}", response_model=schemas.Product)
def update_product(
    *,
    db: Session = Depends(get_db),
    product_id: int,
    product_in: schemas.ProductBase,
    current_user: User = Depends(deps.get_current_merchant),
) -> Any:
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product.merchant_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")

    for field, value in product_in.dict().items():
        setattr(product, field, value)

    product.status = ProductStatus.PENDING
    product.audit_remark = None

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
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product.merchant_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")

    product.status = status
    db.commit()
    db.refresh(product)
    return product


@router.post("/upload-image")
def upload_product_image(
    file: UploadFile = File(...),
    current_user: User = Depends(deps.get_current_merchant),
) -> Any:
    allowed_types = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="仅支持 JPG、PNG、GIF、WebP 格式的图片")

    ext = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
    if ext.lower() not in [".jpg", ".jpeg", ".png", ".gif", ".webp"]:
        ext = ".jpg"

    filename = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, filename)

    with open(file_path, "wb") as f:
        f.write(file.file.read())

    image_url = f"/static/uploads/{filename}"
    return {"image_url": image_url}


# ==================== 收藏 ====================


@router.get("/favorites", response_model=List[schemas.Favorite])
def get_favorites(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    favs = db.query(Favorite).options(joinedload(Favorite.product)).filter(
        Favorite.user_id == current_user.id
    ).order_by(Favorite.created_at.desc()).all()
    for f in favs:
        if f.product:
            _enrich_merchant_name([f.product], db)
    return favs


@router.post("/favorites", response_model=schemas.Favorite)
def add_favorite(
    fav_in: schemas.FavoriteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    existing = db.query(Favorite).filter(
        Favorite.user_id == current_user.id, Favorite.product_id == fav_in.product_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="已收藏过此商品")

    fav = Favorite(user_id=current_user.id, product_id=fav_in.product_id)
    db.add(fav)
    db.commit()
    db.refresh(fav)
    _ = fav.product
    return fav


@router.delete("/favorites/{favorite_id}")
def remove_favorite(
    favorite_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    fav = db.query(Favorite).filter(
        Favorite.id == favorite_id, Favorite.user_id == current_user.id
    ).first()
    if not fav:
        raise HTTPException(status_code=404, detail="收藏不存在")
    db.delete(fav)
    db.commit()
    return {"message": "已取消收藏"}
