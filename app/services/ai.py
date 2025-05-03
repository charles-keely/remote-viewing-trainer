import os, json, base64, numpy as np, openai
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv

# Load environment variables to get API key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

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
    # Load and convert the image to base64
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
        # Fallback if response is not valid JSON
        return {
            "objects": ["unknown"],
            "colors": ["unknown"],
            "shapes": ["unknown"],
            "materials": ["unknown"],
            "setting": "unknown"
        } 