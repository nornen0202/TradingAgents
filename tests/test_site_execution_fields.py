from tradingagents.scheduled.site import (
    _execution_badge_label,
    _execution_display_state,
    _execution_staleness,
)


def test_execution_badge_defaults_to_preopen():
    ticker_summary = {"ticker": "TSM", "status": "success"}
    assert _execution_badge_label(ticker_summary) == "Pre-open snapshot"
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
