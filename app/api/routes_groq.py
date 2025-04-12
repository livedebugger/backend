import io
import logging
import os
from pathlib import Path
from dotenv import load_dotenv
from db.database import SessionLocal
from fastapi import APIRouter, Depends, File, Header, HTTPException, UploadFile
from models import models
from PIL import Image
from pydantic import BaseModel
from sqlalchemy.orm import Session
from utils.groq_analyze import analyze_image
from utils.deps import verify_api_key
from groq import Groq
from pygments.lexers import guess_lexer
from pygments.util import ClassNotFound
from typing import Optional


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

groq_router = APIRouter(prefix="/groq")
groq = Groq(api_key=os.getenv("GROQ_API_KEY"))


# Project detection config
PROJECT_MARKERS = {
    "javascript": ["package.json", "yarn.lock", "pnpm-lock.yaml", "vite.config.js", "webpack.config.js"],
    "python": ["pyproject.toml", "requirements.txt", "Pipfile", "setup.py"],
    "go": ["go.mod", "go.sum"],
    "java": ["pom.xml", "build.gradle", "build.gradle.kts", "settings.gradle"],
    "rust": ["Cargo.toml", "Cargo.lock"],
    "node": ["package-lock.json", "node_modules"],
    "ruby": ["Gemfile", "Gemfile.lock"],
    "php": ["composer.json", "composer.lock"],
    "dotnet": ["*.csproj", "*.sln"],
    "c": ["Makefile", "CMakeLists.txt"],
    "cpp": ["CMakeLists.txt", "*.cpp"],
    "dart/flutter": ["pubspec.yaml"],
    "android": ["AndroidManifest.xml", "build.gradle"],
    "kotlin": ["build.gradle.kts"],
    "scala": ["build.sbt"],
    "haskell": ["stack.yaml", "*.cabal"]
}

# ---------------
# Helper Functions
# ---------------
def detect_project_type(file_path: str) -> str:
    """Detect project type by scanning parent directories for config files."""
    current_path = Path(file_path).parent.resolve()
    
    for parent in [current_path] + list(current_path.parents):
        for project_type, markers in PROJECT_MARKERS.items():
            if any((parent / marker).exists() for marker in markers):
                return project_type
        if (parent / ".git").exists():  # Stop at Git root
            break
            
    return "unknown"

def detect_language(context: str) -> Optional[str]:
    """Guess programming language using code content."""
    try:
        lexer = guess_lexer(context)
        return lexer.name.lower()  # e.g., 'python', 'javascript'
    except ClassNotFound:
        logger.warning("Language detection failed.")
        return None


class SuggestPayload(BaseModel):
    context: str 
    type: str  # 'code' or 'error' 
    language: str
    path: str 
    

# Dependency to verify API key
def verify_extension_api_key(x_api_key: str = Header(...)) -> None:
    if x_api_key != os.getenv("EXTENSION_API_KEY"):
        raise HTTPException(status_code=403, detail="Invalid API key")


@groq_router.post("/suggest", dependencies=[Depends(verify_extension_api_key)])
async def suggest(
    payload: SuggestPayload,
    x_api_key: str = Header(..., alias="x-api-key")
):
    # Dynamic detection
    language = payload.language or detect_language(payload.context)
    project_type = detect_project_type(payload.path)
    
    # Build context-aware prompt
    prompt_lines = [
        f"## Debugging Assistant ({project_type} project)",
        f"**File**: {payload.path}",
        f"**Language**: {language or 'unknown'}",
        f"**Context**:\n{payload.context}"
    ]
    
    if payload.type == "error":
        prompt_lines.append("Provide a concise fix for this error:")
    else:
        prompt_lines.append("Suggest improvements for this code:")

    try:
        response = groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{
                "role": "user", 
                "content": "\n".join(prompt_lines)
            }],
            temperature=0.2
        )
        return {"suggestion": response.choices[0].message.content.strip()}
    
    except Exception as e:
        logger.error(f"Groq API failure: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate suggestion")



# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


# @router.post("/analyze/")
# async def analyze(img: UploadFile = File(...)):
#     contents = await img.read()
#     image = Image.open(io.BytesIO(contents))
#     text, analysis = analyze_image(image)
#     return {"ocr_text": text, "groq_response": analysis}

# @router.post("/sessions/{id}/feed/analyze")
# async def analyze_and_post_to_feed(id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
#     contents = await file.read()
#     image = Image.open(io.BytesIO(contents))

#     text, analysis = analyze_image(image)

#     content = {
#         "ocr_text": text,
#         "groq_analysis": analysis
#     }
#     f = models.FeedEvent(session_id=id, type="groq_analysis", content=content)
#     db.add(f)
#     db.commit()
#     db.refresh(f)

#     return f
