from dataclasses import dataclass

KEYWORDS = {
    "downgrade": 0.18,
    "default": 0.25,
    "missed payment": 0.25,
    "covenant": 0.2,
    "liquidity": 0.15,
    "capital shortfall": 0.2,
    "regulatory": 0.1,
    "fraud": 0.2,
    "bankruptcy": 0.25,
    "restructuring": 0.15,
    "sovereign": 0.1,
}


@dataclass
class RelevanceResult:
    score: float
    is_relevant: bool
    reason: str


def score_credit_relevance(title: str, snippet: str | None, full_text: str | None) -> RelevanceResult:
    corpus = " ".join([title or "", snippet or "", full_text or ""]).lower()
    score = 0.0
    hits: list[str] = []
    for key, weight in KEYWORDS.items():
        if key in corpus:
            score += weight
            hits.append(key)

    score = min(score, 1.0)
    is_relevant = score >= 0.2
    reason = f"keyword_hits={hits}" if hits else "no_credit_keywords"
    return RelevanceResult(score=score, is_relevant=is_relevant, reason=reason)
