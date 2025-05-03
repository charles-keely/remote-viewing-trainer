import uuid, httpx, asyncio, logging
from pathlib import Path
from sqlalchemy import insert
from app.models.target import Target
from app.db.session import get_db

# Set up logging
logger = logging.getLogger(__name__)

async def _download_image():
    """Download a random image from Lorem Picsum and save it locally"""
    # Generate a random target number
    SEED = str(uuid.uuid4().int % 10**8).zfill(8)
    WIDTH = HEIGHT = 512
    URL = f"https://picsum.photos/seed/{SEED}/{WIDTH}/{HEIGHT}"
    img_path = Path("app/data/targets") / f"{SEED}.jpg"
    
    logger.info(f"Downloading random image (seed: {SEED})")
    
    # Download the image
    try:
        # Note: follow_redirects is critical for Picsum which returns 302s
        async with httpx.AsyncClient(follow_redirects=True) as c:
            response = await c.get(URL)
            response.raise_for_status()  # Raises exception for 4XX/5XX responses
            
            # Ensure the directory exists and write the file
            img_path.parent.mkdir(parents=True, exist_ok=True)
            img_path.write_bytes(response.content)
            
            logger.info(f"Image downloaded ({img_path.stat().st_size} bytes)")
            
    except Exception as e:
        logger.error(f"Error downloading image: {e}")
        # Use a fallback in case of failure
        SEED = "fallback"
        img_path = Path("app/data/targets") / "fallback.jpg"
        if not img_path.exists():
            # Create a minimal fallback image
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