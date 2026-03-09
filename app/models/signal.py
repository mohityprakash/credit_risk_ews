from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class EntitySignal(Base):
    __tablename__ = "entity_signals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    entity_name: Mapped[str] = mapped_column(String(255), index=True)
    window_start: Mapped[datetime] = mapped_column(DateTime)
    window_end: Mapped[datetime] = mapped_column(DateTime, index=True)
    article_count_1d: Mapped[int] = mapped_column(Integer)
    article_count_7d: Mapped[int] = mapped_column(Integer)
    negative_share: Mapped[float] = mapped_column(Float)
    average_risk_score: Mapped[float] = mapped_column(Float)
    source_diversity: Mapped[float] = mapped_column(Float)
    sentiment_shift: Mapped[float] = mapped_column(Float)
    mention_velocity: Mapped[float] = mapped_column(Float)
    risk_momentum_score: Mapped[float] = mapped_column(Float, index=True)
    diagnostics: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
