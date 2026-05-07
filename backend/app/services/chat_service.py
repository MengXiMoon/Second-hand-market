from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from app.models.models import Conversation, ChatMessage, MessageType, get_beijing_time


def find_or_create_conversation(db: Session, user_id: int, other_user_id: int) -> Conversation:
    """Find an existing conversation between two users or create a new one."""
    conv = db.query(Conversation).filter(
        or_(
            and_(Conversation.participant_one_id == user_id,
                 Conversation.participant_two_id == other_user_id),
            and_(Conversation.participant_one_id == other_user_id,
                 Conversation.participant_two_id == user_id),
        )
    ).first()

    if not conv:
        conv = Conversation(
            participant_one_id=user_id,
            participant_two_id=other_user_id,
        )
        db.add(conv)
        db.commit()
        db.refresh(conv)

    return conv


def create_message(
    db: Session,
    conversation_id: int,
    sender_id: int,
    content: str,
    msg_type: MessageType = MessageType.TEXT,
) -> ChatMessage:
    """Create a chat message and update the conversation's updated_at timestamp."""
    now = get_beijing_time()
    msg = ChatMessage(
        conversation_id=conversation_id,
        sender_id=sender_id,
        content=content,
        msg_type=msg_type,
        timestamp=now,
    )
    db.add(msg)

    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if conv:
        conv.updated_at = now

    db.commit()
    db.refresh(msg)
    return msg
