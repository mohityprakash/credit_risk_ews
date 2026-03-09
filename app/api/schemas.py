from datetime import datetime

from pydantic import BaseModel


class ArticleOut(BaseModel):
    id: int
    source: str
    title: str
    published_at: datetime
    url: str
    snippet: str | None
    relevance_score: float | None
    is_credit_relevant: bool

    class Config:
        from_attributes = True


class AnalysisOut(BaseModel):
    summary: str
    sentiment_label: str
    sentiment_score: float
    risk_level: str
    risk_score: int
    risk_categories: list[str]
    primary_entity: str | None
    affected_entities: list[str]
    time_horizon: str
    key_signals: list[str]
    rationale: str
    confidence: float

    class Config:
        from_attributes = True


class EntitySignalOut(BaseModel):
    entity_name: str
    window_end: datetime
    article_count_1d: int
    article_count_7d: int
    negative_share: float
    average_risk_score: float
    source_diversity: float
    sentiment_shift: float
    mention_velocity: float
    risk_momentum_score: float

    class Config:
        from_attributes = True
