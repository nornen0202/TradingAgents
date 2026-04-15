from datetime import datetime, timedelta, timezone

from tradingagents.scheduled.site import (
    _analysis_review_required_label,
    _compute_health_metrics,
    _execution_badge_label,
    _execution_display_state,
    _execution_staleness,
    _historical_view_label,
    _portfolio_review_required_label,
)


def test_execution_badge_defaults_to_preopen():
    ticker_summary = {"ticker": "TSM", "status": "success"}
    assert _execution_badge_label(ticker_summary) == "PRE_OPEN SNAPSHOT"
    assert _execution_display_state(ticker_summary).startswith("WAIT")


def test_execution_display_state_blocks_stale_actionable():
    ticker_summary = {
        "ticker": "TSM",
        "status": "success",
        "execution_update": {
            "decision_state": "ACTIONABLE_NOW",
            "staleness_seconds": 999,
        },
    }
    assert _execution_display_state(ticker_summary) == "WAIT (stale overlay)"


def test_execution_display_state_explains_stale_degraded():
    ticker_summary = {
        "ticker": "TSM",
        "status": "success",
        "execution_update": {
            "decision_state": "DEGRADED",
            "reason_codes": ["stale_market_data"],
            "data_health": "STALE",
            "staleness_seconds": 10848,
        },
    }
    assert _execution_display_state(ticker_summary) == "DEGRADED (stale market data)"
    assert _execution_staleness(ticker_summary) == "3h 0m 48s"


def test_identity_integrity_checks_portfolio_candidate_layer():
    manifest = {
        "summary": {"total_tickers": 1},
        "tickers": [{"ticker": "AAPL"}],
        "execution": {"overlay_phase": {"name": "CHECKPOINT_22_50"}, "degraded": []},
        "batch_metrics": {"company_news_zero_ratio": 0.0},
    }
    portfolio_summary = {
        "semantic_health": {},
        "candidate_canonical_symbols": ["APPLE"],
        "candidate_identity_pairs": [{"broker_symbol": "AAPL", "canonical_ticker": "APPLE"}],
    }
    metrics = _compute_health_metrics(manifest=manifest, portfolio_summary=portfolio_summary)
    assert metrics["identity_integrity"] == "warning"


def test_review_labels_are_split_by_layer():
    ticker_summary = {
        "review_required": False,
        "execution_update": {"review_required": True},
    }
    assert _analysis_review_required_label(ticker_summary) == "no"
    assert _portfolio_review_required_label(ticker_summary) == "yes"


def test_historical_view_label_uses_published_time_age():
    now = datetime.now(timezone.utc)
    recent_manifest = {"finished_at": (now - timedelta(hours=2)).isoformat()}
    older_manifest = {"finished_at": (now - timedelta(hours=12)).isoformat()}
    assert _historical_view_label(recent_manifest) == "no"
    assert _historical_view_label(older_manifest) == "yes"
