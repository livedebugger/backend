import uvicorn
import asyncio
from fastapi import FastAPI, WebSocket
from groq import Groq
import pytesseract
import subprocess
from PIL import Image
import io
import os
import logging
from dotenv import load_dotenv
import torch
# from transformers import Blip2Processor, Blip2ForConditionalGeneration
from transformers import AutoProcessor, AutoModelForVision2Seq


# Load model + processor
processor = AutoProcessor.from_pretrained("llava-hf/llava-1.5-7b-hf")
model = AutoModelForVision2Seq.from_pretrained(
    "llava-hf/llava-1.5-7b-hf",
    torch_dtype=torch.float16,
    device_map="auto"
).eval()

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()
# FastAPI app
app = FastAPI()
groq = Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_cursor_pos():
    try:
        out = subprocess.check_output(["hyprctl", "cursorpos"]).decode().strip()
        x_str, y_str = out.replace(",", "").split()
        x, y = int(x_str), int(y_str)
        return x, y
    except Exception as e:
        logger.error(f"Cursor fetch failed: {e}")
        return 960, 540


def analyze_visual_content(image):
    try:
        prompt = "Describe this image in detail."

        inputs = processor(images=image, text=prompt, return_tensors="pt").to(model.device)

        with torch.no_grad():
            output = model.generate(**inputs, max_new_tokens=100)

        caption = processor.batch_decode(output, skip_special_tokens=True)[0]
        return caption

    except Exception as e:
        logger.error(f"Visual analysis failed: {e}")
        return "Visual analysis could not be performed."

    
def capture_fullscreen():
    try:
        proc = subprocess.run(["grim", "-"], stdout=subprocess.PIPE, timeout=2)
        return Image.open(io.BytesIO(proc.stdout))
    except Exception as e:
        logger.error(f"Grim failed: {e}")
        return None

def crop_around_cursor(img, cx, cy, size=400):
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

@app.get("/")
async def health():
    return {"status": "i am turned onn!!!!!", "endpoint": "/ws/debug"}

@app.websocket("/ws/debug")
async def ws_debug(websocket: WebSocket):
    await websocket.accept()
    logger.info("WebSocket connection established")

    try:
        while True:
            # Capture the screen region around the cursor
            img = capture_fullscreen()
            if img:
                cx, cy = get_cursor_pos()
                region = crop_around_cursor(img, cx, cy)

                # Perform OCR to extract text
                extracted_text = pytesseract.image_to_string(region).strip()

                # Analyze visual content if no significant text is found
                if not extracted_text or len(extracted_text) < 10:
                    visual_analysis = analyze_visual_content(region)
                else:
                    visual_analysis = None

                # Send the results via WebSocket
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
