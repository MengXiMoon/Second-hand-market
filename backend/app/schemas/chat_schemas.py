from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.models import MessageType

class ChatMessageBase(BaseModel):
    content: str
    msg_type: MessageType = MessageType.TEXT

class ChatMessageCreate(ChatMessageBase):
    conversation_id: int

class ChatMessage(ChatMessageBase):
    id: int
    conversation_id: int
    sender_id: int
    sender_name: Optional[str] = None
    is_read: bool
    timestamp: datetime

    class Config:
        from_attributes = True

class ConversationBase(BaseModel):
    participant_one_id: int
    participant_two_id: int

class ConversationCreate(ConversationBase):
    pass

class Conversation(ConversationBase):
    id: int
    created_at: datetime
    updated_at: datetime
    last_message: Optional[ChatMessage] = None
    other_user: Optional[dict] = None # {id, username, role}

    class Config:
        from_attributes = True

# WebSocket Events
class WSBaseEvent(BaseModel):
    type: str

class WSMessageEvent(WSBaseEvent):
    type: str = "message"
    data: ChatMessage

class WSTypingEvent(WSBaseEvent):
    type: str = "typing"
    data: dict # {"user_id": int, "is_typing": bool, "conversation_id": int}
