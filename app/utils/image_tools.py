import subprocess
from PIL import Image 
import io
import logging 
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
