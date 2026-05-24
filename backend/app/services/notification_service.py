from sqlalchemy.orm import Session
from app.models.models import Notification


def push_notification(db: Session, user_id: int, title: str, content: str, n_type: str):
    """持久化一条通知"""
    n = Notification(user_id=user_id, title=title, content=content, n_type=n_type)
    db.add(n)
    db.commit()
