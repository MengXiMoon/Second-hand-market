from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
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
    background_tasks: BackgroundTasks,
) -> Any:
    """Create a new order (Purchase Product)."""
    product = db.query(Product).filter(Product.id == order_in.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product.status != ProductStatus.APPROVED:
        raise HTTPException(status_code=400, detail="Product is not available for purchase")
    if product.stock < 1:
        raise HTTPException(status_code=400, detail="Product is out of stock")
    
    # NEW: Prevent self-purchase to avoid logical confusion
    if product.merchant_id == current_user.id:
        raise HTTPException(status_code=400, detail="不能购买自己发布的商品")
    
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

    # Platform Commission (1%)
    commission = product.price * 0.01
    merchant_amount = product.price - commission

    # Find an admin to receive the commission
    admin_user = db.query(User).filter(User.role == UserRole.ADMIN).first()
    if admin_user:
        admin_wallet = db.query(Wallet).filter(Wallet.user_id == admin_user.id).first()
        if admin_wallet:
            admin_wallet.balance += commission
            admin_transaction = Transaction(
                wallet_id=admin_user.id,
                amount=commission,
                type=TransactionType.COMMISSION,
                description=f"Commission from {product.name} sale (Buyer: {current_user.username})"
            )
            db.add(admin_transaction)

    # Transaction: Add to merchant (net of commission)
    merchant_wallet = db.query(Wallet).filter(Wallet.user_id == product.merchant_id).first()
    if merchant_wallet:
        merchant_wallet.balance += merchant_amount
        merchant_transaction = Transaction(
            wallet_id=product.merchant_id,
            amount=merchant_amount,
            type=TransactionType.SALE,
            description=f"Sold {product.name} (Platform fee: {commission})"
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

    # Automated Chat Message when order is placed
    from app.models.models import Conversation, ChatMessage, MessageType, get_beijing_time
    from sqlalchemy import or_, and_
    from datetime import datetime

    # Find or Create Conversation
    conv = db.query(Conversation).filter(
        or_(
            and_(Conversation.participant_one_id == current_user.id, Conversation.participant_two_id == product.merchant_id),
            and_(Conversation.participant_one_id == product.merchant_id, Conversation.participant_two_id == current_user.id)
        )
    ).first()

    if not conv:
        conv = Conversation(
            participant_one_id=current_user.id,
            participant_two_id=product.merchant_id
        )
        db.add(conv)
        db.commit()
        db.refresh(conv)
    
    # Create the automated message
    now = get_beijing_time()
    chat_msg = ChatMessage(
        conversation_id=conv.id,
        sender_id=current_user.id,
        content=f"我已下单商品：{product.name} (订单号: {order.id})",
        msg_type=MessageType.TEXT,
        timestamp=now
    )
    db.add(chat_msg)
    conv.updated_at = now
    db.commit()
    db.refresh(chat_msg)

    # Real-time Notification    # Notify Merchant about new order
    from app.core.websocket_manager import manager
    notification_payload = {
        "type": "new_order",
        "message": f"您有新的订单！商品：{product.name}",
        "data": {"order_id": order.id, "product_name": product.name}
    }
    background_tasks.add_task(manager.send_personal_message, notification_payload, product.merchant_id)

    # Notify Chat Participants via WebSocket
    chat_payload = {
        "type": "chat_message",
        "data": {
            "id": chat_msg.id,
            "conversation_id": conv.id,
            "sender_id": current_user.id,
            "sender_name": current_user.username,
            "content": chat_msg.content,
            "msg_type": "text",
            "timestamp": chat_msg.timestamp.isoformat()
        }
    }
    background_tasks.add_task(manager.send_personal_message, chat_payload, current_user.id)
    background_tasks.add_task(manager.send_personal_message, chat_payload, product.merchant_id)

    # Notify Admin about site-wide order
    admin_notification = {
        "type": "admin_event",
        "message": f"管理提醒：全站新订单！用户 [{current_user.username}] 购买了 [{product.name}]。",
        "data": {"order_id": order.id, "product_name": product.name}
    }
    background_tasks.add_task(manager.broadcast, admin_notification)

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
