import json

from tradingagents.schemas import parse_structured_decision


def test_execution_levels_numeric_passthrough():
    payload = {
        "rating": "HOLD",
        "portfolio_stance": "BULLISH",
        "entry_action": "WAIT",
        "setup_quality": "DEVELOPING",
        "confidence": 0.72,
        "time_horizon": "short",
        "entry_logic": "wait for confirmation",
        "exit_logic": "trim if invalidated",
        "position_sizing": "starter only",
        "risk_limits": "1R",
        "catalysts": [],
        "invalidators": [],
        "watchlist_triggers": [],
        "data_coverage": {
            "company_news_count": 1,
            "disclosures_count": 0,
            "social_source": "dedicated",
            "macro_items_count": 1,
        },
        "execution_levels": {
            "intraday_pilot_rule": "use a small starter only",
            "close_confirm_rule": "close must hold above breakout",
            "next_day_followthrough_rule": "next day must hold the first 30 minutes",
            "failed_breakout_rule": "do not chase failed breakouts",
            "trim_rule": "trim on invalidation",
            "levels": [
                {
                    "label": "breakout trigger",
                    "level_type": "breakout",
                    "price": 123.45,
                    "confirmation": "intraday",
                    "volume_rule": "rvol >= 1.3",
                },
                {
                    "label": "pullback zone",
                    "level_type": "pullback",
                    "low": 120.0,
                    "high": 121.5,
                    "confirmation": "close",
                },
            ],
            "min_relative_volume": 1.3,
            "vwap_required": True,
            "earliest_pilot_time_local": "10:30",
            "funding_priority": "high",
            "entry_window": "mid",
            "trigger_quality": "strong",
        },
    }

    parsed = parse_structured_decision(json.dumps(payload, ensure_ascii=False))

    assert parsed.execution_levels.levels[0].price == 123.45
    assert parsed.execution_levels.levels[1].low == 120.0
    assert parsed.execution_levels.min_relative_volume == 1.3
    assert parsed.execution_levels.vwap_required is True
    assert parsed.execution_levels.earliest_pilot_time_local == "10:30"
    assert parsed.execution_levels.to_dict()["levels"][0]["level_type"] == "breakout"
