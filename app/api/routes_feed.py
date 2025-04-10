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

@router.get("/sessions/{id}/feed")
def get_feed(id: int, db: Session = Depends(get_db)):
    return db.query(models.FeedEvent).filter_by(session_id=id).all()

@router.post("/sessions/{id}/feed")
def post_feed(id: int, type: str, content: dict, db: Session = Depends(get_db)):
    f = models.FeedEvent(session_id=id, type=type, content=content)
    db.add(f)
    db.commit()
    db.refresh(f)
    return f
