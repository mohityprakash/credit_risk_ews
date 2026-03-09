from __future__ import annotations

from datetime import datetime, timedelta, timezone

import requests


def fetch_gdelt_articles(query: str, lookback_hours: int, max_records: int) -> list[dict]:
    start = (datetime.now(timezone.utc) - timedelta(hours=lookback_hours)).strftime("%Y%m%d%H%M%S")
    endpoint = "https://api.gdeltproject.org/api/v2/doc/doc"
    params = {
        "query": query,
        "mode": "ArtList",
        "maxrecords": max_records,
        "format": "json",
        "startdatetime": start,
        "sort": "DateDesc",
    }
    response = requests.get(endpoint, params=params, timeout=20)
    response.raise_for_status()
    data = response.json()
    articles = data.get("articles", [])
    return [
        {
            "source": item.get("sourceCommonName") or "unknown",
            "title": item.get("title") or "",
            "published_at": item.get("seendate") or datetime.now(timezone.utc).isoformat(),
            "url": item.get("url") or "",
            "snippet": item.get("socialimage") or "",
            "full_text": None,
        }
        for item in articles
        if item.get("url")
    ]
