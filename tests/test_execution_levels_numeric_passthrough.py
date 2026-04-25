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


def test_execution_levels_normalize_live_llm_level_variants():
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
            "social_source": "available",
            "macro_items_count": 1,
        },
        "execution_levels": {
            "levels": [
                {
                    "label": "COST pullback zone",
                    "level_type": "pullback",
                    "price": "1008-1012",
                    "confirmation": "touch or close hold",
                },
                {
                    "label": "TSLA downside reference",
                    "level_type": "downside reference",
                    "price": "$250.00",
                    "confirmation": "intraday hold",
                },
            ],
            "min_relative_volume": "RVOL >= 1.2x",
            "vwap_required": "required above VWAP",
            "funding_priority": "medium-high",
            "entry_window": "after open",
            "trigger_quality": "high quality",
        },
    }

    parsed = parse_structured_decision(json.dumps(payload, ensure_ascii=False))
    levels = parsed.execution_levels.levels

    assert levels[0].price is None
    assert levels[0].low == 1008.0
    assert levels[0].high == 1012.0
    assert levels[0].confirmation == "close"
    assert levels[1].level_type == "support"
    assert levels[1].price == 250.0
    assert levels[1].confirmation == "intraday"
    assert parsed.data_coverage.social_source.value == "dedicated"
    assert parsed.execution_levels.min_relative_volume == 1.2
    assert parsed.execution_levels.vwap_required is True
    assert parsed.execution_levels.funding_priority == "high"
    assert parsed.execution_levels.entry_window.value == "open"
    assert parsed.execution_levels.trigger_quality.value == "strong"


def test_execution_levels_accept_observed_confirmation_phrases():
    observed_phrases = [
        "touch or close hold",
        "daily hold/reclaim",
        "intraday hold or close",
        "intraday hold then strong close",
        "intraday hold or daily close above",
        "touch or stall",
        "touch hold",
        "close back above after intraday test",
        "intraday hold then rebound or close back above",
        "intraday hold or close back above 176.0",
        "intraday hold or daily close back above zone",
        "close below",
        "touch or close",
    ]
    payload = {
        "rating": "HOLD",
        "portfolio_stance": "BULLISH",
        "entry_action": "WAIT",
        "setup_quality": "DEVELOPING",
        "confidence": 0.7,
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
            "levels": [
                {
                    "label": f"observed phrase {index}",
                    "level_type": "breakout",
                    "price": 100 + index,
                    "confirmation": phrase,
                }
                for index, phrase in enumerate(observed_phrases)
            ],
        },
    }

    parsed = parse_structured_decision(json.dumps(payload, ensure_ascii=False))

    assert len(parsed.execution_levels.levels) == len(observed_phrases)
    assert {level.confirmation for level in parsed.execution_levels.levels} <= {
        "intraday",
        "close",
        "two_bar",
        "next_day",
    }
