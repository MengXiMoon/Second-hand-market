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

# Allowed image extensions and their magic bytes
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
MAGIC_BYTES = {
    b'\xff\xd8\xff': '.jpg',       # JPEG
    b'\x89PNG\r\n\x1a\n': '.png',  # PNG
    b'GIF87a': '.gif',             # GIF87a
    b'GIF89a': '.gif',             # GIF89a
    b'RIFF': '.webp',              # WEBP (RIFF....WEBP)
}


def validate_image(file: UploadFile) -> None:
    """Validate uploaded file is a real image by extension, magic bytes, and size."""
    # Check file extension
    _, ext = os.path.splitext(file.filename or '')
    ext = ext.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    # Check magic bytes (read first 16 bytes to cover all formats)
    header = file.file.read(16)
    file.file.seek(0)  # Reset for later reading

    if not header:
        raise HTTPException(status_code=400, detail="Empty file")

    matched = False
    for magic, _ in MAGIC_BYTES.items():
        if header.startswith(magic):
            matched = True
            # Extra check for WebP: bytes 8-11 should be 'WEBP'
            if magic == b'RIFF' and header[8:12] != b'WEBP':
                matched = False
            break

    if not matched:
        raise HTTPException(status_code=400, detail="File content does not match a valid image format")

    # Check file size (read in chunks to enforce limit)
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset

    if file_size > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE // (1024 * 1024)}MB",
        )

router = APIRouter()

@router.get("/conversations", response_model=List[chat_schemas.Conversation])
def get_conversations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all conversations for the current user with efficient queries."""
    conversations = db.query(Conversation).filter(
        or_(
            Conversation.participant_one_id == current_user.id,
            Conversation.participant_two_id == current_user.id
        )
    ).order_by(desc(Conversation.updated_at)).all()

    if not conversations:
        return []

    conv_ids = [c.id for c in conversations]

    # Fetch last messages for all conversations in one query
    # Subquery: max timestamp per conversation
    from sqlalchemy import tuple_
    last_msg_subq = (
        db.query(
            ChatMessage.conversation_id,
            ChatMessage.id,
            ChatMessage.sender_id,
            ChatMessage.content,
            ChatMessage.msg_type,
            ChatMessage.timestamp,
            ChatMessage.is_read,
        )
        .filter(ChatMessage.conversation_id.in_(conv_ids))
        .order_by(ChatMessage.conversation_id, desc(ChatMessage.timestamp))
        .distinct(ChatMessage.conversation_id)
        .subquery()
    )

    # Actually let's use a simpler approach: get latest message per conversation via window function
    # SQLite doesn't support window functions well, so use a correlated subquery approach
    last_msgs = {}
    for conv_id in conv_ids:
        msg = (
            db.query(ChatMessage)
            .filter(ChatMessage.conversation_id == conv_id)
            .order_by(desc(ChatMessage.timestamp))
            .first()
        )
        if msg:
            last_msgs[conv_id] = msg

    # Fetch all relevant sender usernames in one query
    sender_ids = {m.sender_id for m in last_msgs.values()}
    sender_ids.update(
        c.participant_two_id if c.participant_one_id == current_user.id else c.participant_one_id
        for c in conversations
    )
    users = {
        u.id: u
        for u in db.query(User).filter(User.id.in_(sender_ids)).all()
    }

    # Enrich conversations
    for conv in conversations:
        last_msg = last_msgs.get(conv.id)
        if last_msg:
            sender = users.get(last_msg.sender_id)
            last_msg.sender_name = sender.username if sender else "Unknown"
        conv.last_message = last_msg

        other_uid = (
            conv.participant_two_id if conv.participant_one_id == current_user.id
            else conv.participant_one_id
        )
        other_user = users.get(other_uid)
        if other_user:
            conv.other_user = {
                "id": other_user.id,
                "username": other_user.username,
                "role": other_user.role,
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

    # Fetch all sender usernames in one query (instead of N queries)
    sender_ids = {m.sender_id for m in messages}
    senders = db.query(User).filter(User.id.in_(sender_ids)).all()
    sender_map = {u.id: u.username for u in senders}
    for msg in messages:
        msg.sender_name = sender_map.get(msg.sender_id, "Unknown")

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

    from app.services.chat_service import find_or_create_conversation
    conv = find_or_create_conversation(db, current_user.id, recipient_id)
    return conv

@router.post("/upload")
async def upload_chat_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload an image for chat. Validates file type by magic bytes, not just Content-Type."""
    validate_image(file)

    # Generate unique filename with safe extension
    _, ext = os.path.splitext(file.filename or '')
    ext = ext.lower()
    filename = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, filename)

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"url": f"/static/uploads/{filename}"}
