from types import SimpleNamespace

from app.services.trend_engine import compute_risk_momentum


def test_risk_momentum_formula():
    settings = SimpleNamespace(
        mention_spike_weight=0.4,
        negative_share_weight=0.3,
        severity_weight=0.2,
        source_diversity_weight=0.1,
    )
    metrics = {"mention_spike": 0.5, "negative_share": 0.8, "severity": 0.6, "source_diversity": 0.4}
    assert compute_risk_momentum(metrics, settings) == 60.0
