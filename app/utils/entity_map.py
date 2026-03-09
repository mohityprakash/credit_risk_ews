CANONICAL_ENTITY_MAP = {
    "apple": "Apple Inc.",
    "apple inc": "Apple Inc.",
    "aapl": "Apple Inc.",
    "jpm": "JPMorgan Chase",
    "jpmorgan": "JPMorgan Chase",
    "jpmorgan chase": "JPMorgan Chase",
    "us": "United States",
    "u.s.": "United States",
    "usa": "United States",
    "fed": "Federal Reserve",
}


def normalize_entity(name: str) -> str:
    key = name.strip().lower()
    return CANONICAL_ENTITY_MAP.get(key, name.strip())
