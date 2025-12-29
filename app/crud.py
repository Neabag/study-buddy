from sqlalchemy.orm import Session
from app.models import Message

def save_message(
    db: Session,
    user_id: str,
    role: str,
    content: str
):
    msg = Message(
        user_id=user_id,
        role=role,
        content=content
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


def get_last_messages(
    db: Session,
    user_id: str,
    limit: int = 10
):
    return (
        db.query(Message)
        .filter(Message.user_id == user_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
        .all()
    )
