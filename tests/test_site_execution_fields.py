from tradingagents.scheduled.site import (
    _compute_health_metrics,
    _execution_badge_label,
    _execution_display_state,
    _execution_staleness,
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
