import json

from tradingagents.execution.contract_builder import build_execution_contract


def test_contract_builder_extracts_numeric_levels():
    decision = {
        "rating": "HOLD",
        "portfolio_stance": "BULLISH",
        "entry_action": "WAIT",
        "setup_quality": "DEVELOPING",
        "confidence": 0.7,
        "time_horizon": "short",
        "entry_logic": "...",
        "exit_logic": "...",
        "position_sizing": "...",
        "risk_limits": "...",
        "catalysts": ["breakout above 410.5 with rvol 1.3", "above vwap preferred"],
        "invalidators": ["intraday below 395", "close below 398"],
        "watchlist_triggers": ["pullback buy zone 400 402", "earnings 2026-04-20"],
        "data_coverage": {
            "company_news_count": 1,
            "disclosures_count": 0,
            "social_source": "unavailable",
            "macro_items_count": 0,
        },
    }
    payload = {
        "decision": json.dumps(decision, ensure_ascii=False),
        "finished_at": "2026-04-14T10:00:00+09:00",
        "trade_date": "2026-04-14",
    }
    contract = build_execution_contract(ticker="TSM", analysis_payload=payload)

    assert contract.breakout_level == 410.5
    assert contract.pullback_buy_zone is not None
    assert contract.invalid_if_intraday_below == 395.0
    assert contract.invalid_if_close_below == 398.0
    assert contract.min_relative_volume == 1.3
    assert contract.event_guard is not None
    assert contract.event_guard.earnings_date == "2026-04-20"
