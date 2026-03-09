from app.services.relevance import score_credit_relevance


def test_relevance_detects_credit_terms():
    result = score_credit_relevance("Issuer faces default risk", "", "")
    assert result.is_relevant is True
    assert result.score >= 0.2


def test_relevance_rejects_non_credit():
    result = score_credit_relevance("Company launches new product", "", "")
    assert result.is_relevant is False
