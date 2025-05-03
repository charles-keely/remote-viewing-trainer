from sqlalchemy import Float, JSON, TIMESTAMP, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base
class Session(Base):
    __tablename__ = "sessions"
    session_id:      Mapped[int]   = mapped_column(primary_key=True, autoincrement=True)
    target_id:       Mapped[str]   = mapped_column(String, ForeignKey("targets.target_id"))
    user_notes:      Mapped[str]   = mapped_column(String)
    sketch_path:     Mapped[str]   = mapped_column(String, nullable=True)
    stage_durations: Mapped[dict]  = mapped_column(JSON)
    rubric:          Mapped[dict]  = mapped_column(JSON)
    total_score:     Mapped[float] = mapped_column(Float)
    aols:            Mapped[list]  = mapped_column(JSON)
    ts:              Mapped[str]   = mapped_column(TIMESTAMP, server_default="NOW()") 