import json
from dataclasses import replace
from datetime import datetime, timedelta

import pytest

from tradingagents.atomic_io import atomic_write_json
from tradingagents.execution.archive_paper import build_step
from tradingagents.execution.contract_builder import build_execution_contract
from tradingagents.execution.overlay import evaluate_execution_state
from tradingagents.execution.session_confirmation import RECEIPT_SCHEMA
from tradingagents.portfolio.candidates import _apply_execution_overlay_risk_action
from tradingagents.schemas import (
    parse_structured_decision,
    StructuredDecisionValidationError,
    IntradayMarketSnapshot,
)
from tradingagents.scheduled.runner import _ExecutionContractShim
from tradingagents.scheduled.config import load_scheduled_config


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
        market="KR",
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


def test_independent_intraday_group_does_not_wait_for_close_alternative():
    levels = {"levels": [
        {"level_type": "BREAKOUT", "price": 100, "confirmation": "intraday", "confirmation_group": "pilot"},
        {"level_type": "PULLBACK", "low": 98, "high": 101, "confirmation": "close", "confirmation_group": "next-session"},
    ]}
    original = contract(execution_levels=levels)
    archived = _ExecutionContractShim(original.to_dict()).to_contract()
    at = datetime.fromisoformat("2026-09-21T11:00:00+09:00")
    snapshot = market(at)
    result = evaluate_execution_state(archived, snapshot, now=at, max_data_age_seconds=120)
    assert result.decision_now.value == "STARTER_NOW", result.reason_codes


@pytest.mark.parametrize(("action", "expected"), [("STARTER", "STARTER_NOW"), ("ADD", "ADD_NOW")])
def test_grouped_active_entries_do_not_require_conditional_wait_expiry(action, expected):
    original = contract(entry_action=action, conditional_entry_action="NONE", execution_levels={"levels": [
        {"level_type": "BREAKOUT", "price": 100, "confirmation": "intraday", "confirmation_group": "pilot"},
        {"level_type": "PULLBACK", "low": 98, "high": 101, "confirmation": "close", "confirmation_group": "overnight"},
    ]})
    saved = _ExecutionContractShim(original.to_dict()).to_contract()
    assert saved.entry_valid_until is None
    at = datetime.fromisoformat("2026-09-21T11:00:00+09:00")
    result = evaluate_execution_state(saved, market(at), now=at, max_data_age_seconds=120)
    assert result.decision_now.value == expected, result.reason_codes


@pytest.mark.parametrize(("level", "flag", "risk_reason"), [
    ({"level_type": "BREAKOUT", "price": 100, "confirmation": "intraday"}, "failed_breakout", "FAILED_BREAKOUT"),
    ({"level_type": "PULLBACK", "low": 100, "high": 101, "confirmation": "intraday"}, "support_fail", "SUPPORT_BROKEN"),
])
@pytest.mark.parametrize("grouped", [False, True])
def test_entry_groups_preserve_the_held_position_downside_signals(level, flag, risk_reason, grouped):
    if grouped:
        level = {**level, "confirmation_group": "pilot"}
    original = contract(entry_action="STARTER", conditional_entry_action="NONE",
                        execution_levels={"levels": [level]})
    saved = _ExecutionContractShim(original.to_dict()).to_contract()
    at = datetime.fromisoformat("2026-09-21T11:00:00+09:00")
    reduced = replace(market(at), last_price=99, day_low=98)
    update = evaluate_execution_state(saved, reduced, now=at, max_data_age_seconds=120)
    assert update.decision_now.value == "NONE"
    assert update.trigger_status[flag] is True
    rows = update.to_dict()
    assert _apply_execution_overlay_risk_action(risk_action="HOLD", risk_action_reason_codes=(),
        execution_update=rows, is_held=True) == ("REDUCE_RISK", (risk_reason,))
    assert _apply_execution_overlay_risk_action(risk_action="HOLD", risk_action_reason_codes=(),
        execution_update=rows, is_held=False) == ("HOLD", ())


@pytest.mark.parametrize("gate", ["expiry", "event"])
def test_buy_only_gates_preserve_grouped_downside_review(gate):
    from tradingagents.schemas.execution import EventGuard

    original = contract(execution_levels={"levels": [
        {"level_type": "PULLBACK", "low": 100, "high": 101, "confirmation": "intraday", "confirmation_group": "pilot"},
    ]})
    if gate == "expiry":
        original = replace(original, entry_valid_until="2026-09-21T10:58:00+09:00")
    else:
        original = replace(original, event_guard=EventGuard(earnings_date="2026-09-21", block_new_position_within_days=1))
    at = datetime.fromisoformat("2026-09-21T11:00:00+09:00")
    update = evaluate_execution_state(original, replace(market(at), last_price=99, day_low=98),
                                      now=at, max_data_age_seconds=120)
    assert update.trigger_status["support_fail"] and update.decision_now.value == "NONE"
    assert _apply_execution_overlay_risk_action(risk_action="HOLD", risk_action_reason_codes=(),
        execution_update=update.to_dict(), is_held=True) == ("REDUCE_RISK", ("SUPPORT_BROKEN",))


def test_independent_pilot_is_not_vetoed_by_unmet_other_entry_group():
    original = contract(execution_levels={"levels": [
        {"level_type": "BREAKOUT", "price": 100, "confirmation": "intraday", "confirmation_group": "pilot"},
        {"level_type": "PULLBACK", "low": 150, "high": 151, "confirmation": "close", "confirmation_group": "other"},
    ]})
    at = datetime.fromisoformat("2026-09-21T11:00:00+09:00")
    update = evaluate_execution_state(original, market(at), now=at, max_data_age_seconds=120)
    assert update.decision_now.value == "STARTER_NOW"
    blocked = evaluate_execution_state(replace(original, min_relative_volume=1.1),
                                      replace(market(at), relative_volume=0.7), now=at, max_data_age_seconds=120)
    assert blocked.decision_now.value == "NONE" and blocked.trigger_status["support_fail"]


@pytest.mark.parametrize("confirmation", ["next_open", "next_session_quote"])
def test_ungrouped_active_next_session_entry_cannot_trigger_intraday(confirmation):
    original = contract(entry_action="STARTER", conditional_entry_action="NONE", execution_levels={"levels": [
        {"level_type": "PULLBACK", "low": 100, "high": 102, "confirmation": confirmation},
    ]})
    at = datetime.fromisoformat("2026-09-21T11:00:00+09:00")
    update = evaluate_execution_state(original, market(at), now=at, max_data_age_seconds=120)
    assert update.decision_now.value == "NONE"
    assert update.reason_codes == ("conditional_entry_confirmation_unavailable",)


@pytest.mark.parametrize("metadata", [{"confirmation_group": "pilot"}, {"entry_condition_role": "required"}])
def test_invalid_grouped_or_required_clause_cannot_be_silently_dropped(metadata):
    thesis = decision(execution_levels={"levels": [
        {"level_type": "BREAKOUT", "price": 100, "confirmation": "intraday", "confirmation_group": "pilot"},
        {"level_type": "SUPPORT", "price": 102, **metadata},
    ]})
    with pytest.raises(StructuredDecisionValidationError, match="(explicit confirmation|entry_condition_role)"):
        parse_structured_decision(json.dumps(thesis))


@pytest.mark.parametrize("case", [
    "close_and_next_open", "missing_open", "unverified_close", "before_open", "holiday", "expired", "wait",
    "independent_intraday", "joint_required", "active_expiry_after_decision",
])
def test_standard_overlay_producer_archives_confirmed_entry_only(tmp_path, monkeypatch, case):
    from tradingagents.scheduled import runner

    ticker = "ABC"
    created = "2026-11-27T12:00:00-05:00"
    close = "2026-11-27T13:00:00-05:00"  # XNYS early close
    opening = "2026-11-30T09:30:00-05:00"
    current = "2026-11-30T09:32:00-05:00"
    expires = "2026-11-30T10:30:00-05:00"
    if case == "holiday":
        created, close = "2026-11-25T12:00:00-05:00", "2026-11-25T16:00:00-05:00"
        opening, current = "2026-11-26T09:30:00-05:00", "2026-11-26T09:32:00-05:00"
    if case == "before_open":
        current = "2026-11-30T09:29:00-05:00"
    if case == "expired":
        expires = "2026-11-30T09:31:00-05:00"
    conditioned = [{"level_type": "BREAKOUT", "price": 100, "confirmation": "close"}]
    if case in {"independent_intraday", "joint_required", "active_expiry_after_decision"}:
        created, current = "2026-11-27T09:31:00-05:00", "2026-11-27T10:31:00-05:00"
        conditioned = [
            {"level_type": "BREAKOUT", "price": 100, "confirmation": "intraday", "confirmation_group": "pilot"},
            {"level_type": "PULLBACK", "low": 99, "high": 102, "confirmation": "close",
             "confirmation_group": "pilot" if case == "joint_required" else "next-session"},
        ]
    if case == "active_expiry_after_decision":
        created, current = "2026-11-30T10:31:00-05:00", "2026-12-01T10:30:55-05:00"
        expires = "2026-12-01T10:31:00-05:00"
    plan = decision(conditional_entry_valid_until=expires, execution_levels={"levels": conditioned})
    if case == "wait":
        plan.update(conditional_entry_action="NONE", conditional_entry_valid_until=None)
    if case == "active_expiry_after_decision":
        plan.update(entry_action="STARTER", conditional_entry_action="NONE", conditional_entry_valid_until=None)
    original = build_execution_contract(ticker=ticker, analysis_payload={"finished_at": created, "decision": json.dumps(plan)})

    def observation(kind, clock):
        return {"kind": kind, "event_at": clock, "observed_at": clock, "price": 101,
                "ticker": ticker, "market": "US", "currency": "USD", "session": clock[:10],
                "source": "ALPACA_SIP_REGULAR_SESSION"}

    atomic_write_json(tmp_path / "observations/ABC.json", {
        "schema": RECEIPT_SCHEMA, "ticker": ticker, "market": "US", "price_basis": "unadjusted",
        "regular_close": observation("quote" if case == "unverified_close" else "final_regular_close", close),
        "official_open": None if case == "missing_open" else observation("official_regular_open", opening),
    })
    path = tmp_path / "scheduled.toml"
    path.write_text('[run]\ntickers=["ABC"]\nmarket="US"\n[storage]\narchive_dir="archive"\nsite_dir="site"\n'
                    '[execution]\nenabled=true\nsession_confirmation_receipts_dir="observations"\n', encoding="utf-8")
    config = load_scheduled_config(path)
    run = tmp_path / "archive/runs/2026/fixture"
    artifact = "tickers/ABC/execution_contract.json"
    atomic_write_json(run / artifact, original.to_dict())
    at = datetime.fromisoformat(current)

    class FixedDateTime(datetime):
        @classmethod
        def now(cls, tz=None):
            return at.astimezone(tz) if tz is not None else at.replace(tzinfo=None)

    monkeypatch.setattr(runner, "datetime", FixedDateTime)
    snapshot = replace(market(at), ticker=ticker, market="US", provider="kis")
    monkeypatch.setattr(runner, "_fetch_overlay_market_snapshots", lambda **_: {ticker: snapshot})
    summaries = [{"ticker": ticker, "status": "success", "artifacts": {"execution_contract_json": artifact}}]
    updates = runner._run_execution_overlay_passes(config=config, run_dir=run, ticker_summaries=summaries, checkpoints=["post_research"])
    update = updates[ticker]
    ready = case in {"close_and_next_open", "independent_intraday", "active_expiry_after_decision"}
    assert update["decision_now"] == ("STARTER_NOW" if ready else "NONE"), update
    if not ready:
        return

    proof = update["entry_confirmation_v2"]
    assert proof["evaluation"]["matched_alternatives"] == [0]
    if case == "close_and_next_open":
        close_rule = proof["evaluation"]["conditions"]["entry-0"]
        assert datetime.fromisoformat(close_rule["observation_as_of"]) == datetime.fromisoformat(close)
        assert proof["evaluation"]["verified_next_open"] is True

    generated = (at + timedelta(seconds=2)).isoformat()
    atomic_write_json(run / "run.json", {"run_id": "fixture", "status": "success"})
    atomic_write_json(run / "decision_bundle_v2.json", {"market": "US", "generated_at": generated,
        "analysis_source_run_id": "fixture", "strategy_table": [{
            "ticker": ticker, "last_price": update["last_price"], "market_data_asof": update["market_data_asof"],
            "quality": {"execution_ready": True, "generated_in_current_run": True},
            "raw_codes": {"decision_now": update["decision_now"]},
        }]})
    atomic_write_json(run / "portfolio-private/account_snapshot.json", {"as_of": generated, "account_value_krw": 10000000})
    atomic_write_json(run / "portfolio-private/proposed_orders.json", {"orders": [
        {"canonical_ticker": ticker, "side": "BUY", "estimated_qty": 1},
    ]})
    _, step, _ = build_step(run, generated)
    signal, = step["signals"]
    assert signal["execution_ready"] is True and signal["entry_confirmation"]["paper_candidate_ready"]
    if case == "active_expiry_after_decision":
        assert datetime.fromisoformat(signal["valid_until"]) == datetime.fromisoformat(expires)
        _, expired_step, _ = build_step(run, expires)
        assert expired_step["signals"][0]["execution_ready"] is False
        assert expired_step["signals"][0]["entry_confirmation"]["reason"] == "ENTRY_RESEARCH_EXPIRED"
    edited_proof = json.loads(json.dumps(proof))
    edited_proof["plan"]["alternatives"][0][0]["level"] -= 1
    atomic_write_json(run / "tickers/ABC/execution_update.json", {**update, "entry_confirmation_v2": edited_proof})
    _, step, _ = build_step(run, generated)
    assert step["signals"][0]["execution_ready"] is False
    atomic_write_json(run / "tickers/ABC/execution_update.json", {
        **update, "execution_asof": (at + timedelta(minutes=1)).isoformat(),
    })
    _, step, _ = build_step(run, generated)
    assert step["signals"][0]["execution_ready"] is False


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
