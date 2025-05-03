from sqlalchemy import String, JSON, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base
class Target(Base):
    __tablename__ = "targets"
    target_id: Mapped[str] = mapped_column(String, primary_key=True)
    image_url:  Mapped[str] = mapped_column(String)
    caption:    Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[str] = mapped_column(TIMESTAMP, server_default="NOW()") 