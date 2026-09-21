import json
from dataclasses import replace
from datetime import datetime, timedelta

import pytest

from tradingagents.execution.contract_builder import build_execution_contract
from tradingagents.execution.overlay import evaluate_execution_state
from tradingagents.schemas import (
    parse_structured_decision,
    StructuredDecisionValidationError,
    IntradayMarketSnapshot,
)
from tradingagents.scheduled.runner import _ExecutionContractShim


def decision(**changes):
    return {
        "rating": "HOLD",
        "portfolio_stance": "BULLISH",
        "entry_action": "WAIT",
        "risk_action": "HOLD",
        "setup_quality": "DEVELOPING",
        "confidence": 0.7,
        "time_horizon": "short",
        "entry_logic": "Above the stated trigger",
        "exit_logic": "Below invalidation",
        "position_sizing": "Separate deterministic sizing",
        "risk_limits": "Existing risk limits",
        "catalysts": [],
        "invalidators": [],
        "watchlist_triggers": [],
        "data_coverage": {},
        "conditional_entry_action": "STARTER",
        "conditional_entry_valid_until": "2026-09-21T15:00:00+09:00",
        "execution_levels": {
            "levels": [
                {"level_type": "BREAKOUT", "price": 100, "confirmation": "intraday"}
            ],
            "earliest_pilot_time_local": "10:30",
            "min_relative_volume": 1.1,
        },
        **changes,
    }


def contract(**changes):
    return build_execution_contract(
        ticker="TEST",
        analysis_payload={
            "decision": json.dumps(decision(**changes)),
            "finished_at": "2026-09-21T10:00:00+09:00",
        },
    )


def market(at):
    return IntradayMarketSnapshot(
        ticker="TEST",
        asof=at.isoformat(),
        provider="test",
        interval="1m",
        last_price=101,
        session_vwap=100,
        day_high=102,
        day_low=100,
        volume=100,
        avg20_daily_volume=100,
        relative_volume=1.2,
        market_session="regular",
    )


def test_wait_retains_explicit_conditional_intent_and_fires_only_after_confirmation():
    c = contract()
    assert c.entry_action_base == "WAIT" and c.action_if_triggered.value == "STARTER"
    at = datetime.fromisoformat("2026-09-21T11:00:00+09:00")
    update = evaluate_execution_state(c, market(at), now=at, max_data_age_seconds=120)
    assert update.decision_now.value == "STARTER_NOW"
    blocked = evaluate_execution_state(
        c, replace(market(at), relative_volume=0.8), now=at, max_data_age_seconds=120
    )
    assert blocked.decision_now.value == "NONE"


def test_legacy_bullish_wait_still_does_not_create_buy_intent():
    assert contract(conditional_entry_action="NONE").action_if_triggered.value == "NONE"


@pytest.mark.parametrize(
    "changes",
    [
        {"portfolio_stance": "BEARISH"},
        {"risk_action": "EXIT"},
        {"entry_action": "ADD"},
        {"conditional_entry_valid_until": None},
        {"conditional_entry_valid_until": "2026-09-21T15:00:00"},
        {"conditional_entry_action": "EXIT"},
        {"execution_levels": {"levels": []}},
        {"execution_levels": "invalid"},
        {"execution_levels": {"levels": None}},
        {
            "execution_levels": {
                "levels": [{"level_type": "BREAKOUT", "price": "above 100"}]
            }
        },
    ],
)
def test_invalid_or_implicit_conditional_intent_rejected(changes):
    with pytest.raises(StructuredDecisionValidationError):
        parse_structured_decision(decision(**changes))


def test_expired_intent_and_future_quote_cannot_fire():
    c = contract()
    at = datetime.fromisoformat("2026-09-21T15:00:00+09:00")
    result = evaluate_execution_state(c, market(at), now=at, max_data_age_seconds=120)
    assert "conditional_entry_expired_or_unavailable" in result.reason_codes
    at -= timedelta(hours=1)
    result = evaluate_execution_state(
        c, market(at + timedelta(seconds=1)), now=at, max_data_age_seconds=120
    )
    assert "future_market_data" in result.reason_codes


def test_archived_contract_keeps_expiry():
    c = contract()
    restored = _ExecutionContractShim(c.to_dict()).to_contract()
    assert restored.entry_valid_until == c.entry_valid_until


@pytest.mark.parametrize("confirmation", ["close", "two_bar", "next_day"])
def test_support_zone_cannot_bypass_unproven_confirmation(confirmation):
    c = contract(
        execution_levels={
            "levels": [
                {"level_type": "BREAKOUT", "price": 100, "confirmation": confirmation},
                {
                    "level_type": "SUPPORT",
                    "low": 100,
                    "high": 102,
                    "confirmation": "intraday",
                },
            ]
        }
    )
    at = datetime.fromisoformat("2026-09-21T11:00:00+09:00")
    update = evaluate_execution_state(c, market(at), now=at, max_data_age_seconds=120)
    assert update.decision_now.value == "NONE"
    assert "conditional_entry_confirmation_unavailable" in update.reason_codes


def test_conditional_entry_does_not_synthesize_another_entry_from_prose():
    c = contract(watchlist_triggers=["pullback buy zone 100-102"])
    assert c.pullback_buy_zone is None
    c = contract(
        execution_levels={
            "levels": [
                {"level_type": "BREAKOUT", "price": 103, "confirmation": "intraday"},
                {
                    "level_type": "SUPPORT",
                    "low": 100,
                    "high": 102,
                    "confirmation": "intraday",
                },
            ]
        }
    )
    at = datetime.fromisoformat("2026-09-21T11:00:00+09:00")
    update = evaluate_execution_state(
        c, replace(market(at), day_high=104), now=at, max_data_age_seconds=120
    )
    assert update.decision_now.value == "NONE"
    assert "failed_breakout" in update.reason_codes
