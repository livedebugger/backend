import asyncio
import io
import logging
import os
import subprocess

import pytesseract
import torch
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket
from groq import Groq
from PIL import Image
# from transformers import Blip2Processor, Blip2ForConditionalGeneration
from transformers import AutoModelForVision2Seq, AutoProcessor

# Load model + processor
processor = AutoProcessor.from_pretrained("llava-hf/llava-1.5-7b-hf")
model = AutoModelForVision2Seq.from_pretrained(
    "llava-hf/llava-1.5-7b-hf",
    torch_dtype=torch.float16,      # using half precision for efficiency 
    device_map="auto"   # auto detection of gpu // install cuda drivers 
).eval()    # setting model to evaluation mode 

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()
# FastAPI app
app = FastAPI()
groq = Groq(api_key=os.getenv("GROQ_API_KEY")) # init groq 

def get_cursor_pos():
        """Get current cursor position using Hyprland's CLI tool"""
    try:
        out = subprocess.check_output(["hyprctl", "cursorpos"]).decode().strip()
        x_str, y_str = out.replace(",", "").split()
        x, y = int(x_str), int(y_str)
        return x, y
    except Exception as e:
        logger.error(f"Cursor fetch failed: {e}")
        return 960, 540 # fallback to central pos 


def analyze_visual_content(image):
    try:
        prompt = "Describe this image in detail."

        inputs = processor(images=image, text=prompt, return_tensors="pt").to(model.device)

        with torch.no_grad():   # disabling gradient calculation 
            output = model.generate(**inputs, max_new_tokens=100)

        caption = processor.batch_decode(output, skip_special_tokens=True)[0]
        return caption

    except Exception as e:
        logger.error(f"Visual analysis failed: {e}")
        return "Visual analysis could not be performed."

    
def capture_fullscreen():
    """capturing full screen with grim // wayland compositer """
    try:
        proc = subprocess.run(["grim", "-"], stdout=subprocess.PIPE, timeout=2)
        return Image.open(io.BytesIO(proc.stdout))
    except Exception as e:
        logger.error(f"Grim failed: {e}")
        return None

def crop_around_cursor(img, cx, cy, size=400):
        """Crop 400x400 region around cursor position"""
    left = max(cx - size // 2, 0)
    upper = max(cy - size // 2, 0)
    right = left + size
    lower = upper + size
    return img.crop((left, upper, right, lower))

def save_image(img, filename):
    try:
        img.save(filename)
    except Exception as e:
        logger.error(f"Image save failed: {e}")
def analyze_image(img):
        """Analyze screen content using OCR + Groq AI"""
    try:
        # extracting text 
        text = pytesseract.image_to_string(img)

        # creating diagnostic prompt 
        prompt = (
            "You are a debugging assistant. Here's the OCR text from the user's screen:\n\n"
            f"{text.strip()}\n\n"
            "Explain what it likely means, whether it's code or an error message. Be concise and useful."
        )

        # getting AI analysis 
        response = groq.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
        return text.strip(), response.choices[0].message.content
    except Exception as e:
        logger.error(f"Groq failed: {e}")
        return "", "Groq analysis failed."

@app.get("/")
async def health():
    return {"status": "i am turned onn!!!!!", "endpoint": "/ws/debug"}

@app.websocket("/ws/debug")
async def ws_debug(websocket: WebSocket):
    await websocket.accept()
    logger.info("WebSocket connection established")

    try:
        while True:
            # capturing the screen region around the cursor
            img = capture_fullscreen()
            if img:
                cx, cy = get_cursor_pos()
                region = crop_around_cursor(img, cx, cy)

                # OCR to extract text
                extracted_text = pytesseract.image_to_string(region).strip()

                # analyzing visual content if no significant text is found
                if not extracted_text or len(extracted_text) < 10:
                    visual_analysis = analyze_visual_content(region)
                else:
                    # fallback 
                    visual_analysis = None

                # prepring the results via WebSocket
                await websocket.send_json({
                    "cursor_pos": [cx, cy],
                    "ocr_text": extracted_text,
                    "visual_analysis": visual_analysis
                })

            await asyncio.sleep(2)

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        await websocket.close()
        logger.info("WebSocket closed")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
