from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    news_provider: str = Field(default="gdelt", alias="NEWS_PROVIDER")
    gdelt_query: str = Field(default="credit risk", alias="GDELT_QUERY")
    database_url: str = Field(default="sqlite:///./data/credit_risk_ews.db", alias="DATABASE_URL")
    enable_llm_enrichment: bool = Field(default=False, alias="ENABLE_LLM_ENRICHMENT")
    ingest_lookback_hours: int = Field(default=24, alias="INGEST_LOOKBACK_HOURS")
    max_articles_per_run: int = Field(default=50, alias="MAX_ARTICLES_PER_RUN")
    openai_model: str = Field(default="gpt-4o-mini", alias="OPENAI_MODEL")

    mention_spike_weight: float = Field(default=0.35, alias="RISK_MOMENTUM_MENTION_SPIKE_WEIGHT")
    negative_share_weight: float = Field(default=0.30, alias="RISK_MOMENTUM_NEGATIVE_SHARE_WEIGHT")
    severity_weight: float = Field(default=0.25, alias="RISK_MOMENTUM_SEVERITY_WEIGHT")
    source_diversity_weight: float = Field(default=0.10, alias="RISK_MOMENTUM_SOURCE_DIVERSITY_WEIGHT")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
