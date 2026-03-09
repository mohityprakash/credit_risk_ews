import json
import re
from typing import Any


JSON_BLOCK_RE = re.compile(r"\{.*\}", re.DOTALL)


def safe_parse_model_output(raw_text: str) -> dict[str, Any]:
    candidate = raw_text.strip()
    if candidate.startswith("```"):
        candidate = candidate.strip("`")
        candidate = candidate.replace("json", "", 1).strip()

    try:
        parsed = json.loads(candidate)
    except json.JSONDecodeError:
        match = JSON_BLOCK_RE.search(raw_text)
        if not match:
            return {}
        try:
            parsed = json.loads(match.group(0))
        except json.JSONDecodeError:
            return {}

    return parsed if isinstance(parsed, dict) else {}
