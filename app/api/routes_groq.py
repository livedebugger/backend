from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from db.database import SessionLocal
from models import models
from utils.groq_analyze import analyze_image
from PIL import Image
import io

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/analyze/")
async def analyze(img: UploadFile = File(...)):
    contents = await img.read()
    image = Image.open(io.BytesIO(contents))
    text, analysis = analyze_image(image)
    return {"ocr_text": text, "groq_response": analysis}

@router.post("/sessions/{id}/feed/analyze")
async def analyze_and_post_to_feed(id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    contents = await file.read()
    image = Image.open(io.BytesIO(contents))

    text, analysis = analyze_image(image)

    content = {
        "ocr_text": text,
        "groq_analysis": analysis
    }
    f = models.FeedEvent(session_id=id, type="groq_analysis", content=content)
    db.add(f)
    db.commit()
    db.refresh(f)

    return f
