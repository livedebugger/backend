import torch
import logging
from transformers import AutoModelForVision2Seq, AutoProcessor
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load model + processor
processor = AutoProcessor.from_pretrained("llava-hf/llava-1.5-7b-hf")
model = AutoModelForVision2Seq.from_pretrained(
    "llava-hf/llava-1.5-7b-hf",
    torch_dtype=torch.float16,      # using half precision for efficiency 
    device_map="auto"   # auto detection of gpu // install cuda drivers 
).eval()    # setting model to evaluation mode 



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
