import os, json, base64, numpy as np, openai
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv
import logging

# Load environment variables to get API key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

logger = logging.getLogger(__name__)

def embed(text: str) -> list[float]:
    """Generate embeddings for text using OpenAI's API"""
    r = openai.embeddings.create(
        model="text-embedding-3-small",
        input=text, 
        encoding_format="float"
    )
    return r.data[0].embedding

def describe_image(path: str) -> dict:
    """Generate a description of an image using GPT-4 Vision"""
    # Verify the image exists and is valid
    try:
        if not os.path.exists(path):
            logger.error(f"Image file does not exist: {path}")
            return _get_fallback_description()
            
        # Check if file is empty
        if os.path.getsize(path) == 0:
            logger.error(f"Image file is empty (0 bytes): {path}")
            return _get_fallback_description()
        
        # Load and convert the image to base64
        img = Image.open(path)
        # Verify it's a valid image
        img.verify()
        # Reopen after verify (verify closes the file)
        img = Image.open(path)
        buf = BytesIO()
        img.save(buf, "PNG")
        b64 = base64.b64encode(buf.getvalue()).decode()
        
        # Prepare message for GPT-4 Vision
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Return JSON with keys: objects, colors, shapes, materials, setting."},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}}
                ]
            }
        ]
        
        # Call the OpenAI API
        r = openai.chat.completions.create(
            model="gpt-4-vision-preview",  # Updated to available model
            messages=messages,
            max_tokens=256
        )
        
        # Parse and return the JSON response
        try:
            return json.loads(r.choices[0].message.content)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON response from OpenAI API")
            return _get_fallback_description()
            
    except Exception as e:
        logger.error(f"Error processing image {path}: {str(e)}")
        return _get_fallback_description()

def _get_fallback_description() -> dict:
    """Return a fallback description when image processing fails"""
    return {
        "objects": ["unknown"],
        "colors": ["unknown"],
        "shapes": ["unknown"],
        "materials": ["unknown"],
        "setting": "unknown"
    } 