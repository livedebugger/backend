#

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

@router.post("/sessions/{id}/logs")
def push_log(id: int, text: str, db: Session = Depends(get_db)):
    log = models.LogEntry(session_id=id, text=text)
    db.add(log)
    db.commit()
    db.refresh(log)
    return log

@router.post("/sessions/{id}/suggestions")
def post_suggestion(id: int, suggestion: str, db: Session = Depends(get_db)):
    s = models.Suggestion(session_id=id, suggestion=suggestion)
    db.add(s)
    db.commit()
    db.refresh(s)
    return s
