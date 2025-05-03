import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from contextlib import contextmanager

# Load environment variables
load_dotenv()

# Get database URL from environment or use default with current user
user = os.getenv("USER", os.getenv("USERNAME", "postgres"))
db_url = os.getenv("DATABASE_URL", f"postgresql://{user}@localhost:5432/rv")

# Convert from asyncpg URL if needed
if "asyncpg" in db_url:
    db_url = db_url.replace("asyncpg", "psycopg")

engine = create_engine(db_url, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# This is for use with 'with' statements
@contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

# This is for use with FastAPI Depends
def get_db_session():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close() 