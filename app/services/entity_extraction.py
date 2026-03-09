import re

from app.utils.entity_map import normalize_entity

ENTITY_PATTERN = re.compile(r"\b([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z&.]+){0,2})\b")


def extract_entities(text: str) -> list[str]:
    raw_entities = ENTITY_PATTERN.findall(text)
    normalized = [normalize_entity(item) for item in raw_entities]
    unique = []
    seen = set()
    for entity in normalized:
        if len(entity) < 3:
            continue
        key = entity.lower()
        if key not in seen:
            seen.add(key)
            unique.append(entity)
    return unique[:10]
