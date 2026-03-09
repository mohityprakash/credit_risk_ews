from __future__ import annotations

from typing import Any

from openai import OpenAI

from app.core.config import Settings
from app.utils.json_parser import safe_parse_model_output
from app.utils.taxonomy import RISK_TAXONOMY

REQUIRED_KEYS = {
    "summary",
    "sentiment_label",
    "sentiment_score",
    "risk_level",
    "risk_score",
    "risk_categories",
    "primary_entity",
    "affected_entities",
    "time_horizon",
    "key_signals",
    "rationale",
    "confidence",
}


def _fallback_payload() -> dict[str, Any]:
    return {
        "summary": "No LLM summary available. Rule-based fallback used.",
        "sentiment_label": "neutral",
        "sentiment_score": 0.0,
        "risk_level": "medium",
        "risk_score": 50,
        "risk_categories": ["Sector Stress"],
        "primary_entity": None,
        "affected_entities": [],
        "time_horizon": "near_term",
        "key_signals": ["Fallback analysis due to unavailable or malformed model output."],
        "rationale": "LLM output parsing failed or LLM disabled.",
        "confidence": 0.4,
    }


def validate_payload(payload: dict[str, Any]) -> dict[str, Any]:
    if not REQUIRED_KEYS.issubset(payload.keys()):
        return _fallback_payload()
    payload["risk_categories"] = [x for x in payload.get("risk_categories", []) if x in RISK_TAXONOMY] or ["Sector Stress"]
    payload["risk_score"] = max(0, min(int(payload.get("risk_score", 50)), 100))
    payload["sentiment_score"] = max(-1.0, min(float(payload.get("sentiment_score", 0.0)), 1.0))
    payload["confidence"] = max(0.0, min(float(payload.get("confidence", 0.4)), 1.0))
    return payload


def enrich_article(article_text: str, settings: Settings) -> tuple[dict[str, Any], str]:
    if not settings.enable_llm_enrichment or not settings.openai_api_key:
        return _fallback_payload(), "rule_based_v1"

    prompt = (
        "Return JSON only with keys: summary, sentiment_label, sentiment_score, risk_level, risk_score, risk_categories, "
        "primary_entity, affected_entities, time_horizon, key_signals, rationale, confidence. "
        "Use credit risk taxonomy categories only. Keep rationale concise.\n"
        f"Article:\n{article_text[:4500]}"
    )

    client = OpenAI(api_key=settings.openai_api_key)
    response = client.responses.create(
        model=settings.openai_model,
        temperature=0,
        input=prompt,
    )
    parsed = safe_parse_model_output(response.output_text)
    if not parsed:
        return _fallback_payload(), settings.openai_model
    return validate_payload(parsed), settings.openai_model
