from types import SimpleNamespace

from tradingagents.portfolio.pipeline import _build_semantic_health


def test_semantic_health_degrades_on_high_fallback_ratio():
    candidates = [
        SimpleNamespace(decision_source="RULE_ONLY_FALLBACK", review_required=True),
        SimpleNamespace(decision_source="RULE_ONLY_FALLBACK", review_required=True),
        SimpleNamespace(decision_source="RULE+DEEP", review_required=False),
    ]
    health = _build_semantic_health(candidates)
    assert health["judge_unavailable"] is True
    assert health["rule_only_fallback_count"] == 2
