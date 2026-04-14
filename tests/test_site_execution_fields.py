from tradingagents.scheduled.site import _execution_badge_label, _execution_display_state


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
