from tradingagents.scheduled.runner import _compute_run_quality


def test_run_quality_includes_judge_health_signal():
    manifest = {
        "summary": {"total_tickers": 10},
        "batch_metrics": {"company_news_zero_ratio": 0.2},
        "execution": {
            "overlay_phase": {"name": "CHECKPOINT_13_40"},
            "degraded": ["A"],
            "actionable_now": ["AAPL"],
            "triggered_pending_close": ["TSM"],
        },
        "portfolio": {"semantic_health": {"rule_only_fallback_ratio": 0.4}},
    }

    quality = _compute_run_quality(manifest=manifest)

    assert quality["signals"]["judge_health"] == "degraded"
    assert quality["signals"]["rule_only_fallback_ratio"] == 0.4
    assert 0.0 <= quality["run_quality_score"] <= 1.0
