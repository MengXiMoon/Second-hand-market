from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc
from typing import List, Optional
import os
import uuid
import shutil
from datetime import datetime

from app.db.session import get_db
from app.models.models import Conversation, ChatMessage, User, MessageType
from app.schemas import chat_schemas
from app.api.deps import get_current_user
from app.core.config import settings

router = APIRouter()

@router.get("/conversations", response_model=List[chat_schemas.Conversation])
def get_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all conversations for the current user."""
    conversations = db.query(Conversation).filter(
        or_(
            Conversation.participant_one_id == current_user.id,
            Conversation.participant_two_id == current_user.id
        )
    ).order_by(desc(Conversation.updated_at)).all()
    
    # Enrich with last message and other user info
    for conv in conversations:
        last_msg = db.query(ChatMessage).filter(
            ChatMessage.conversation_id == conv.id
        ).order_by(desc(ChatMessage.timestamp)).first()
        
        if last_msg:
            sender = db.query(User).filter(User.id == last_msg.sender_id).first()
            last_msg.sender_name = sender.username if sender else "Unknown"
        
        conv.last_message = last_msg
        
        # Get other user info
        other_uid = conv.participant_two_id if conv.participant_one_id == current_user.id else conv.participant_one_id
        other_user = db.query(User).filter(User.id == other_uid).first()
        if other_user:
            conv.other_user = {
                "id": other_user.id,
                "username": other_user.username,
                "role": other_user.role
            }
            
    return conversations

@router.get("/messages/{conversation_id}", response_model=List[chat_schemas.ChatMessage])
def get_messages(
    conversation_id: int,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get message history for a conversation with pagination."""
    # Verify access
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conv or (conv.participant_one_id != current_user.id and conv.participant_two_id != current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to view this conversation")
        
    messages = db.query(ChatMessage).filter(
        ChatMessage.conversation_id == conversation_id
    ).order_by(desc(ChatMessage.timestamp)).offset(skip).limit(limit).all()
    
    # Enrich with sender names
    for msg in messages:
        sender = db.query(User).filter(User.id == msg.sender_id).first()
        msg.sender_name = sender.username if sender else "Unknown"
    
    # Return in chronological order
    return messages[::-1]

@router.post("/start", response_model=chat_schemas.Conversation)
def start_conversation(
    recipient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Start or retrieve a conversation with another user."""
    if recipient_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot chat with yourself")
        
    # Check if exists
    conv = db.query(Conversation).filter(
        or_(
            and_(Conversation.participant_one_id == current_user.id, Conversation.participant_two_id == recipient_id),
            and_(Conversation.participant_one_id == recipient_id, Conversation.participant_two_id == current_user.id)
        )
    ).first()
    
    if not conv:
        conv = Conversation(
            participant_one_id=current_user.id,
            participant_two_id=recipient_id
        )
        db.add(conv)
        db.commit()
        db.refresh(conv)
        
    return conv

@router.post("/upload")
async def upload_chat_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload an image for chat."""
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
        
    # Generate unique filename
    file_ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, filename)
    
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Return the URL
    return {"url": f"/static/uploads/{filename}"}
