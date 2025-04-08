import uvicorn 
import asyncio
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from groq import Groq
import pytesseract 
from mss import mss
import subprocess
import logging 
from dotenv import load_dotenv
import os



# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Initialize the FastAPI app
app = FastAPI()

class AnalysisRequest(BaseModel):
    session_id: str
    log_path: str = "/var/log/syslog"
    
# Screen capture service

class ScreenCapture:
    def __init__(self):
        self.sct = mss()
        self.monitor = self.sct.monitors[1] # primary monitor

    def capture_screen(self):
        try:
            sct_img = self.sct.grab(self.monitor)
            return sct_img
        except Exception as e:
            logger.error(f"Error capturing screen: {e}")
            raise 
        
# OCR service
def extract_text(image):
    try:
        return pytesseract.image_to_string(image)
    except pytesseract.TesseractNotFoundError:
        logger.error("Tesseract OCR not found. Please install Tesseract.")
        return ""
    

# Log collector 
async def tail_logs(file_path):
    cmd = ["tail", "-F", "n", "10", file_path]
    process = subprocess.Popen(
        cmd, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.PIPE,
        universe_newlines=True
        )
    
    while True: 
        line = process.stdout.readline()
        if not line:
            await asyncio.sleep(0.1)
            continue
        yield line.strip()
        
# Groq service

async def groq_analysis(context: str, logs: list):
    client = Groq()
    try:
        chat_completion = client.chat.completions.create(
            messages=[{
                "role": "user",
                "content": f"Analyze the following logs: \n{context}\n{logs}"
            }],
            model="mixtral-8x7b-32768",
            temperature=0.3,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        logger.error(f"Groq API error: {str(e)}")
        return "Analysis failed due to an error with the Groq API."
    
@app.websocket("/ws/session/{session_id}")
async def websocket_session(websocket: WebSocket):
    await websocket.accept()
    screen_capture = ScreenCapture()
    log_gen = tail_logs("/var/log/syslog")
    
    try:
        while True: 
            # Capture screen
            screen_img = screen_capture.capture_screen()
            text = extract_text(screen_img)
            
            # Get latest logs
            logs = [log async for log in log_gen]
            
            # Get AI analysis
            analysis = await groq_analysis(text, logs)
            
            # Send data to the client
            await websocket.send_json({
                "screen_text": text,
                "logs": logs[-10:],
                "analysis": analysis               
            })
            await asyncio.sleep(1)  # Adjust the sleep time as needed
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
    finally:
        await websocket.close()
            
@app.get("/")
async def health_check():
    return {"status": "i am turned on!!!!!"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7000)