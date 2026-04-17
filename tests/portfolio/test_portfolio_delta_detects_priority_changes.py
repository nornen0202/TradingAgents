from tradingagents.portfolio.delta import compute_portfolio_delta


def test_portfolio_delta_detects_priority_changes():
    previous = {
        "run_id": "run-a",
        "execution": {"top_priority_order": ["TSM", "NVDA", "AAPL", "GOOGL"]},
        "tickers": [
            {"ticker": "TSM", "execution_update": {"decision_state": "ACTIONABLE_NOW"}},
            {"ticker": "GOOGL", "execution_update": {"decision_state": "WAIT"}},
        ],
    }
    current = {
        "run_id": "run-b",
        "execution": {"top_priority_order": ["GOOGL", "NVDA", "TSM", "AAPL"]},
        "tickers": [
            {"ticker": "TSM", "execution_update": {"decision_state": "WAIT"}},
            {"ticker": "GOOGL", "execution_update": {"decision_state": "ACTIONABLE_NOW"}},
        ],
    }

    delta = compute_portfolio_delta(previous_manifest=previous, current_manifest=current)

    assert delta["from_run"] == "run-a"
    assert delta["to_run"] == "run-b"
    assert {"ticker": "GOOGL", "from": 4, "to": 1} in delta["priority_changes"]
    assert {"ticker": "TSM", "from": 1, "to": 3} in delta["priority_changes"]
    assert "GOOGL" in delta["newly_actionable"]
