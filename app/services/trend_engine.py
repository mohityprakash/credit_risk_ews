from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone

def compute_risk_momentum(metrics: dict[str, float], settings) -> float:
    score = (
        metrics["mention_spike"] * settings.mention_spike_weight
        + metrics["negative_share"] * settings.negative_share_weight
        + metrics["severity"] * settings.severity_weight
        + metrics["source_diversity"] * settings.source_diversity_weight
    )
    return round(score * 100, 2)


def build_entity_metrics(db, settings) -> list[dict]:
    from sqlalchemy import select

    from app.models.analysis import ArticleAnalysis
    from app.models.article import Article

    now = datetime.now(timezone.utc)
    one_day = now - timedelta(days=1)
    seven_day = now - timedelta(days=7)

    stmt = (
        select(Article, ArticleAnalysis)
        .join(ArticleAnalysis, Article.id == ArticleAnalysis.article_id)
        .where(Article.published_at >= seven_day)
    )

    by_entity: dict[str, list[tuple[object, object]]] = defaultdict(list)
    for article, analysis in db.execute(stmt).all():
        entity = analysis.primary_entity or "Unknown"
        by_entity[entity].append((article, analysis))

    output = []
    for entity, rows in by_entity.items():
        count_1d = sum(1 for art, _ in rows if art.published_at >= one_day)
        count_7d = len(rows)
        negatives = [a for _, a in rows if a.sentiment_label == "negative"]
        negative_share = len(negatives) / count_7d if count_7d else 0.0
        avg_risk = sum(a.risk_score for _, a in rows) / count_7d if count_7d else 0.0
        sources = {art.source for art, _ in rows}
        source_diversity = min(len(sources) / max(count_7d, 1), 1.0)

        recent_sentiment = [a.sentiment_score for art, a in rows if art.published_at >= one_day]
        old_sentiment = [a.sentiment_score for art, a in rows if art.published_at < one_day]
        sentiment_shift = (sum(recent_sentiment) / len(recent_sentiment) if recent_sentiment else 0.0) - (
            sum(old_sentiment) / len(old_sentiment) if old_sentiment else 0.0
        )

        mention_velocity = count_1d / max(count_7d / 7, 1)
        metrics = {
            "mention_spike": min(mention_velocity / 3, 1.0),
            "negative_share": negative_share,
            "severity": avg_risk / 100,
            "source_diversity": source_diversity,
        }
        momentum = compute_risk_momentum(metrics, settings)

        output.append(
            {
                "entity_name": entity,
                "window_start": seven_day,
                "window_end": now,
                "article_count_1d": count_1d,
                "article_count_7d": count_7d,
                "negative_share": round(negative_share, 3),
                "average_risk_score": round(avg_risk, 2),
                "source_diversity": round(source_diversity, 3),
                "sentiment_shift": round(sentiment_shift, 3),
                "mention_velocity": round(mention_velocity, 3),
                "risk_momentum_score": momentum,
                "diagnostics": metrics,
            }
        )

    return sorted(output, key=lambda x: x["risk_momentum_score"], reverse=True)
