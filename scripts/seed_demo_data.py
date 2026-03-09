from datetime import datetime, timedelta, timezone

from app.core.config import get_settings
from app.db.init_db import init_db
from app.db.session import SessionLocal
from app.models.analysis import ArticleAnalysis
from app.models.article import Article
from app.services.trend_engine import build_entity_metrics
from app.utils.hashing import hash_url


def run() -> None:
    init_db()
    db = SessionLocal()

    db.query(ArticleAnalysis).delete()
    db.query(Article).delete()
    db.commit()

    demo_articles = [
        {
            "source": "Reuters",
            "title": "Acme Energy faces refinancing pressure amid weaker cash flow",
            "url": "https://example.com/acme-refinancing",
            "snippet": "Analysts cite heightened downgrade risk over the next two quarters.",
            "days_ago": 1,
            "analysis": {
                "summary": "Acme Energy faces near-term refinancing pressure with weaker liquidity metrics.",
                "sentiment_label": "negative",
                "sentiment_score": -0.7,
                "risk_level": "high",
                "risk_score": 78,
                "risk_categories": ["Refinancing Risk", "Liquidity Risk", "Downgrade Risk"],
                "primary_entity": "Acme Energy",
                "affected_entities": ["Acme Energy"],
                "time_horizon": "near_term",
                "key_signals": ["Debt maturities clustered in next 12 months", "Cash flow compression"],
                "rationale": "Debt stack and earnings softness raise credit pressure.",
                "confidence": 0.82,
            },
        },
        {
            "source": "Bloomberg",
            "title": "Sovereign bond spreads widen after budget uncertainty",
            "url": "https://example.com/sovereign-spread",
            "snippet": "Country X may face external funding stress if deficit expands.",
            "days_ago": 0,
            "analysis": {
                "summary": "Country X spreads widened as fiscal uncertainty drove concerns on funding stability.",
                "sentiment_label": "negative",
                "sentiment_score": -0.55,
                "risk_level": "high",
                "risk_score": 74,
                "risk_categories": ["Macro / Sovereign Risk", "Refinancing Risk"],
                "primary_entity": "Country X",
                "affected_entities": ["Country X", "Regional Banks"],
                "time_horizon": "immediate",
                "key_signals": ["Spread widening", "Deficit uncertainty"],
                "rationale": "Sovereign financing risk has increased on fiscal uncertainty.",
                "confidence": 0.79,
            },
        },
    ]

    for item in demo_articles:
        article = Article(
            url_hash=hash_url(item["url"]),
            source=item["source"],
            title=item["title"],
            published_at=datetime.now(timezone.utc) - timedelta(days=item["days_ago"]),
            url=item["url"],
            snippet=item["snippet"],
            full_text=item["snippet"],
            relevance_score=0.7,
            relevance_reason="seed_demo",
            is_credit_relevant=True,
        )
        db.add(article)
        db.flush()
        analysis = ArticleAnalysis(article_id=article.id, model_version="seed_demo", raw_output=item["analysis"], **item["analysis"])
        db.add(analysis)

    db.commit()
    metrics = build_entity_metrics(db, get_settings())
    print(f"Seeded {len(demo_articles)} articles and computed {len(metrics)} entity metrics.")


if __name__ == "__main__":
    run()
