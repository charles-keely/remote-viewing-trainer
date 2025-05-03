import uuid, httpx, asyncio, logging, os
from pathlib import Path
from sqlalchemy import insert
from app.models.target import Target
from app.db.session import get_db
from PIL import Image

# Set up logging
logger = logging.getLogger(__name__)

async def _download_image(max_retries=3):
    """Download a random image from Lorem Picsum and save it locally"""
    retries = 0
    
    while retries < max_retries:
        # Generate a random target number
        SEED = str(uuid.uuid4().int % 10**8).zfill(8)
        WIDTH = HEIGHT = 512
        URL = f"https://picsum.photos/seed/{SEED}/{WIDTH}/{HEIGHT}"
        img_path = Path("app/data/targets") / f"{SEED}.jpg"
        
        logger.info(f"Downloading random image (seed: {SEED}), attempt {retries + 1}/{max_retries}")
        
        # Download the image
        try:
            # Note: follow_redirects is critical for Picsum which returns 302s
            async with httpx.AsyncClient(follow_redirects=True) as c:
                response = await c.get(URL)
                response.raise_for_status()  # Raises exception for 4XX/5XX responses
                
                # Ensure the directory exists and write the file
                img_path.parent.mkdir(parents=True, exist_ok=True)
                img_path.write_bytes(response.content)
                
                # Get file size
                file_size = img_path.stat().st_size
                logger.info(f"Image downloaded ({file_size} bytes)")
                
                # Validate image is not empty and is a valid image file
                if file_size == 0:
                    logger.warning(f"Downloaded image is empty (0 bytes), retrying...")
                    if img_path.exists():
                        os.remove(img_path)
                    retries += 1
                    continue
                
                # Verify it's a valid image by trying to open it
                try:
                    img = Image.open(img_path)
                    img.verify()  # Verify it's a valid image
                    # If we reach here, we have a valid, non-empty image
                    return SEED, str(img_path)
                except Exception as img_err:
                    logger.warning(f"Downloaded file is not a valid image: {img_err}")
                    if img_path.exists():
                        os.remove(img_path)
                    retries += 1
                    continue
                
        except Exception as e:
            logger.error(f"Error downloading image: {e}")
            if img_path.exists():
                os.remove(img_path)
            retries += 1
    
    # If we exhausted all retries, use a fallback
    logger.error(f"Failed to download a valid image after {max_retries} attempts, using fallback")
    SEED = "fallback"
    img_path = Path("app/data/targets") / "fallback.jpg"
    if not img_path.exists():
        # Create a minimal valid fallback image (1×1 black pixel)
        try:
            img = Image.new('RGB', (1, 1), color='black')
            img_path.parent.mkdir(parents=True, exist_ok=True)
            img.save(img_path)
            logger.info(f"Created fallback image ({img_path.stat().st_size} bytes)")
        except Exception as e:
            logger.error(f"Error creating fallback image: {e}")
            # Just create an empty file as last resort
            img_path.touch()
    
    return SEED, str(img_path)

def create_target():
    """Create a new random target with a Lorem Picsum image"""
    # Run the async download in a new event loop
    loop = asyncio.new_event_loop()
    try:
        SEED, img_path = loop.run_until_complete(_download_image())
    finally:
        loop.close()
    
    # Save to database with placeholder caption (GPT-Vision will fill later)
    caption = {"placeholder": "unknown"}
    
    with get_db() as s:
        s.execute(insert(Target).values(
            target_id=SEED,
            image_url=img_path,
            caption=caption
        ))
    
    return SEED 