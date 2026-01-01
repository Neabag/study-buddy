from sqlalchemy.orm import Session
from app.models import Message, Thread
import uuid
from datetime import datetime, timezone

def save_message(
    db: Session,
    user_id: str,
    role: str,
    thread_id: str,
    content: str
):
    msg = Message(
        user_id=user_id,
        role=role,
        content=content,
        thread_id=thread_id
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


def get_last_messages(
    db: Session,
    user_id: str,
    thread_id: str,
    limit: int = 10
):
    return (
        db.query(Message)
        .filter(Message.user_id == user_id, Message.thread_id == thread_id)
        .order_by(Message.created_at.asc())
        .limit(limit)
        .all()
    )

def create_thread(db: Session, user_id: str, title: str):
    thread = Thread(
        id=str(uuid.uuid4()),
        user_id=user_id,
        title=title,
        updated_at=datetime.now(timezone.utc)
    )
    db.add(thread)
    db.commit()
    db.refresh(thread)
    return thread

def get_thread_by_id(db: Session, thread_id: str):
    return (
        db.query(Thread)
        .filter(Thread.id == thread_id)
        .first()
    )

def get_threads_by_user_id(db: Session, user_id: str):
    return (
        db.query(Thread)
        .filter(Thread.user_id == user_id)
        .order_by(Thread.updated_at.desc())
        .all()
    )