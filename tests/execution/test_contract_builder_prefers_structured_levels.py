import json

from tradingagents.execution.contract_builder import build_execution_contract


def test_contract_builder_prefers_structured_levels():
    decision = {
        "rating": "HOLD",
        "portfolio_stance": "BULLISH",
        "entry_action": "WAIT",
        "setup_quality": "DEVELOPING",
        "confidence": 0.7,
        "time_horizon": "short",
        "entry_logic": "watch for the breakout",
        "exit_logic": "respect invalidation",
        "position_sizing": "starter",
        "risk_limits": "1R",
        "catalysts": ["breakout above 999.0 with rvol 3.0"],
        "invalidators": ["close below 80"],
        "watchlist_triggers": ["pullback buy zone 81 82"],
        "data_coverage": {
            "company_news_count": 2,
            "disclosures_count": 0,
            "social_source": "dedicated",
            "macro_items_count": 1,
        },
        "execution_levels": {
            "intraday_pilot_rule": "starter only",
            "close_confirm_rule": "close must confirm",
            "next_day_followthrough_rule": "next day must hold",
            "failed_breakout_rule": "stop chasing failed breakouts",
            "trim_rule": "trim on invalidation",
            "levels": [
                {"label": "breakout", "level_type": "breakout", "price": 123.4, "confirmation": "intraday"},
                {"label": "pullback", "level_type": "pullback", "low": 118.0, "high": 120.0},
                {"label": "invalid", "level_type": "invalidation", "price": 115.0, "confirmation": "close"},
            ],
            "min_relative_volume": 1.1,
            "vwap_required": True,
            "earliest_pilot_time_local": "10:45",
            "funding_priority": "high",
            "entry_window": "mid",
            "trigger_quality": "strong",
        },
    }
    payload = {
        "decision": json.dumps(decision, ensure_ascii=False),
        "finished_at": "2026-04-24T10:00:00+09:00",
        "trade_date": "2026-04-23",
    }

    contract = build_execution_contract(ticker="005930.KS", analysis_payload=payload)

    assert contract.breakout_level == 123.4
    assert contract.pullback_buy_zone is not None
    assert contract.pullback_buy_zone.low == 118.0
    assert contract.invalid_if_close_below == 115.0
    assert contract.min_relative_volume == 1.1
    assert contract.vwap_required is True
    assert contract.earliest_pilot_time_local == "10:45"
    assert "execution_level_regex_fallback" not in contract.reason_codes


def test_contract_builder_marks_regex_fallback_and_missing_machine_level():
    decision = {
        "rating": "HOLD",
        "portfolio_stance": "BULLISH",
        "entry_action": "WAIT",
        "setup_quality": "DEVELOPING",
        "confidence": 0.65,
        "time_horizon": "short",
        "entry_logic": "watch only",
        "exit_logic": "be careful",
        "position_sizing": "starter",
        "risk_limits": "1R",
        "catalysts": ["breakout above 410.5 with rvol 1.3"],
        "invalidators": ["close below 398"],
        "watchlist_triggers": [],
        "data_coverage": {
            "company_news_count": 1,
            "disclosures_count": 0,
            "social_source": "dedicated",
            "macro_items_count": 1,
        },
    }
    payload = {
        "decision": json.dumps(decision, ensure_ascii=False),
        "finished_at": "2026-04-24T10:00:00+09:00",
        "trade_date": "2026-04-23",
    }

    contract = build_execution_contract(ticker="TSM", analysis_payload=payload)

    assert contract.breakout_level == 410.5
    assert "execution_level_regex_fallback" in contract.reason_codes

    decision["catalysts"] = []
    decision["invalidators"] = []
    decision["watchlist_triggers"] = []
    payload["decision"] = json.dumps(decision, ensure_ascii=False)
    contract_without_level = build_execution_contract(ticker="TSM", analysis_payload=payload)

    assert "no_machine_actionable_level" in contract_without_level.reason_codes
