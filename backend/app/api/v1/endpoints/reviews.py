from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session, joinedload

from app.api import deps
from app.db.session import get_db
from app.models.models import User, Review, Order, OrderStatus, MessageType
from app.schemas import schemas
from app.core.websocket_manager import manager
from app.services.chat_service import find_or_create_conversation, create_message
from app.services.notification_service import push_notification

router = APIRouter()


@router.post("/", response_model=schemas.Review)
def create_review(
    *,
    review_in: schemas.ReviewCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """确认收货后评价订单"""
    if review_in.rating < 1 or review_in.rating > 5:
        raise HTTPException(status_code=400, detail="评分须在 1-5 之间")

    # 未填写评论时自动默认
    comment = review_in.comment.strip() if review_in.comment else ""
    if not comment:
        defaults = {5: "非常好", 4: "不错", 3: "一般般", 2: "不太好", 1: "很差"}
        comment = defaults.get(review_in.rating, "无评价")

    order = db.query(Order).filter(Order.id == review_in.order_id).first()
    if not order or order.buyer_id != current_user.id:
        raise HTTPException(status_code=404, detail="订单不存在")
    if order.status != OrderStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="仅可评价已完成的订单")

    existing = db.query(Review).filter(Review.order_id == review_in.order_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="该订单已评价")

    review = Review(
        order_id=review_in.order_id,
        reviewer_id=current_user.id,
        merchant_id=order.product.merchant_id,
        product_id=order.product_id,
        rating=review_in.rating,
        comment=comment,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    review.reviewer_name = current_user.username

    # 通知商家
    conversation = find_or_create_conversation(db, current_user.id, order.product.merchant_id)
    create_message(
        db, conversation.id, current_user.id,
        f"【评价通知】买家对订单 #{order.id} 给出 {review_in.rating} 星评价：{comment}",
        MessageType.SYSTEM,
    )

    return review


@router.put("/{review_id}/reply", response_model=schemas.Review)
def reply_review(
    review_id: int,
    reply_in: schemas.ReviewReply,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_merchant),
) -> Any:
    """商家回复评价"""
    review = db.query(Review).filter(
        Review.id == review_id, Review.merchant_id == current_user.id
    ).first()
    if not review:
        raise HTTPException(status_code=404, detail="评价不存在")
    review.reply = reply_in.reply
    db.commit()
    db.refresh(review)
    review.reviewer_name = current_user.username

    # 通知买家
    push_notification(db, review.reviewer_id, "商家回复了你的评价",
                      f"商家对订单 #{review.order_id} 的评价回复：{reply_in.reply}", "review_reply")

    return review


@router.get("/check/{order_id}")
def check_reviewed(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user),
) -> Any:
    """检查某订单是否已评价"""
    existing = db.query(Review).filter(Review.order_id == order_id).first()
    return {"reviewed": existing is not None}


@router.get("/product/{product_id}", response_model=List[schemas.Review])
def get_product_reviews(
    product_id: int,
    db: Session = Depends(get_db),
) -> Any:
    """获取某商品的所有评价"""
    reviews = db.query(Review).filter(
        Review.product_id == product_id
    ).order_by(Review.created_at.desc()).all()
    for r in reviews:
        r.reviewer_name = db.query(User).filter(User.id == r.reviewer_id).first().username
    return reviews


@router.get("/my", response_model=List[schemas.Review])
def get_my_reviews(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_merchant),
) -> Any:
    """商家查看自己的评价"""
    reviews = db.query(Review).filter(
        Review.merchant_id == current_user.id
    ).order_by(Review.created_at.desc()).all()
    for r in reviews:
        r.reviewer_name = db.query(User).filter(User.id == r.reviewer_id).first().username
    return reviews
