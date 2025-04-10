from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from db.database import SessionLocal
from models import models

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db 
    finally:
        db.close()

@router.post("/sessions/")
def create_session(created_by: str, db: Session = Depends(get_db)):
    session = models.Session(created_by=created_by)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

@router.post("/sessions/{id}/end")
def end_session(id: int, db: Session = Depends(get_db)):
    session = db.query(models.Session).get(id)
    session.ended_at = datetime.utcnow()
    db.commit()
    return {"status": "im done :x"}
