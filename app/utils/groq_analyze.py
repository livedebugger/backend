import pytesseract
from groq import Groq
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from dotenv import load_dotenv
load_dotenv()

groq = Groq(api_key=os.getenv("GROQ_API_KEY"))

def analyze_image(img):
    try:
        text = pytesseract.image_to_string(img)
        prompt = (
            "You are a debugging assistant. Here's the OCR text from the user's screen:\n\n"
            f"{text.strip()}\n\n"
            "Explain what it likely means, whether it's code or an error message. Be concise and useful."
        )
        response = groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
        return text.strip(), response.choices[0].message.content
    except Exception as e:
        logger.error(f"Groq failed: {e}")
        return "", "Groq analysis failed."
