from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ArticleAnalysis(Base):
    __tablename__ = "article_analyses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    article_id: Mapped[int] = mapped_column(ForeignKey("articles.id"), unique=True, index=True)
    summary: Mapped[str] = mapped_column(Text)
    sentiment_label: Mapped[str] = mapped_column(String(32))
    sentiment_score: Mapped[float] = mapped_column()
    risk_level: Mapped[str] = mapped_column(String(32), index=True)
    risk_score: Mapped[int] = mapped_column(Integer, index=True)
    risk_categories: Mapped[list[str]] = mapped_column(JSON)
    primary_entity: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    affected_entities: Mapped[list[str]] = mapped_column(JSON)
    time_horizon: Mapped[str] = mapped_column(String(32))
    key_signals: Mapped[list[str]] = mapped_column(JSON)
    rationale: Mapped[str] = mapped_column(Text)
    confidence: Mapped[float] = mapped_column()
    model_version: Mapped[str] = mapped_column(String(64), default="rule_based_v1")
    raw_output: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    article: Mapped["Article"] = relationship(back_populates="analysis")
