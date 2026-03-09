from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.ingestion.news_provider import fetch_gdelt_articles
from app.models.analysis import ArticleAnalysis
from app.models.article import Article
from app.models.signal import EntitySignal
from app.services.entity_extraction import extract_entities
from app.services.llm_enrichment import enrich_article
from app.services.relevance import score_credit_relevance
from app.services.trend_engine import build_entity_metrics
from app.utils.hashing import hash_url


def _parse_datetime(value: str) -> datetime:
    try:
        if len(value) == 14 and value.isdigit():
            return datetime.strptime(value, "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc)
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return datetime.now(timezone.utc)


def ingest_articles(db: Session, settings: Settings) -> dict:
    records = fetch_gdelt_articles(settings.gdelt_query, settings.ingest_lookback_hours, settings.max_articles_per_run)

    inserted = 0
    duplicates = 0
    for record in records:
        url_hash = hash_url(record["url"])
        existing = db.execute(select(Article).where(Article.url_hash == url_hash)).scalar_one_or_none()
        if existing:
            duplicates += 1
            continue

        relevance = score_credit_relevance(record["title"], record.get("snippet"), record.get("full_text"))
        article = Article(
            url_hash=url_hash,
            source=record["source"],
            title=record["title"],
            published_at=_parse_datetime(record["published_at"]),
            url=record["url"],
            snippet=record.get("snippet"),
            full_text=record.get("full_text"),
            relevance_score=relevance.score,
            relevance_reason=relevance.reason,
            is_credit_relevant=relevance.is_relevant,
        )
        db.add(article)
        inserted += 1

    db.commit()
    return {"fetched": len(records), "inserted": inserted, "duplicates": duplicates}


def analyze_article(db: Session, article: Article, settings: Settings) -> ArticleAnalysis:
    combined_text = f"{article.title}\n{article.snippet or ''}\n{article.full_text or ''}"
    extracted_entities = extract_entities(combined_text)
    payload, model_version = enrich_article(combined_text, settings)
    if not payload.get("primary_entity") and extracted_entities:
        payload["primary_entity"] = extracted_entities[0]
    payload["affected_entities"] = list(set(payload.get("affected_entities", []) + extracted_entities))

    analysis = ArticleAnalysis(article_id=article.id, model_version=model_version, raw_output=payload, **payload)
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return analysis


def analyze_pending(db: Session, settings: Settings) -> dict:
    stmt = (
        select(Article)
        .outerjoin(ArticleAnalysis, Article.id == ArticleAnalysis.article_id)
        .where(Article.is_credit_relevant.is_(True), ArticleAnalysis.id.is_(None))
    )
    pending = db.execute(stmt).scalars().all()
    for article in pending:
        analyze_article(db, article, settings)

    metrics = build_entity_metrics(db, settings)
    db.query(EntitySignal).delete()
    for row in metrics:
        db.add(EntitySignal(**row))
    db.commit()

    return {"analyzed": len(pending), "signals_updated": len(metrics)}
