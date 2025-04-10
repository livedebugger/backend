from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models import models

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/sessions/{id}/chat")
def get_chat(id: int, db: Session = Depends(get_db)):
    return db.query(models.ChatMessage).filter_by(session_id=id).all()

@router.post("/sessions/{id}/chat")
def post_chat(id: int, sender: str, message: str, db: Session = Depends(get_db)):
    msg = models.ChatMessage(session_id=id, sender=sender, message=message)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg
