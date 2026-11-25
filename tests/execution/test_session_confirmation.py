from datetime import datetime
import json

import pytest

from tradingagents.execution.archive_paper import build_step
from tradingagents.execution.session_confirmation import evaluate_plan


FRIDAY_CLOSE = "2026-11-27T18:00:00Z"
MONDAY_OPEN = "2026-11-30T14:30:00Z"
NOW = "2026-11-30T14:35:00Z"
PLAN = {"ticker": "ABC", "market": "US", "currency": "USD", "origin_session": "2026-11-27",
        "created_at": "2026-11-27T17:00:00Z", "valid_sessions": 2, "quote_max_age_seconds": 120,
        "max_open_delay_seconds": 60, "execution_window_seconds": 600, "max_gap_bps": 200,
        "alternatives": [[{"id": "close", "stage": "close", "direction": "above", "level": 100},
                          {"id": "follow", "stage": "next_day", "direction": "above", "level": 100}]]}


def _feed(kind, at, price=101, **changes):
    return {"kind": kind, "event_at": at, "observed_at": at, "price": price, "ticker": "ABC",
            "source": "synthetic", "market": "US", "currency": "USD", "session": at[:10], **changes}


def _evaluate(plan=PLAN, **changes):
    return evaluate_plan(plan, **{
        "analysis_as_of": NOW,
        "regular_close": _feed("final_regular_close", FRIDAY_CLOSE),
        "official_open": _feed("official_regular_open", MONDAY_OPEN),
        "live_quote": _feed("quote", NOW), **changes,
    })


def test_verified_early_close_and_next_real_session_without_live_authority():
    result = _evaluate()
    assert result["paper_candidate_ready"] and result["matched_alternatives"] == [0]
    assert result["conditions"]["close"]["observation_as_of"] == datetime.fromisoformat(FRIDAY_CLOSE).isoformat()
    assert result["conditions"]["follow"]["observation_as_of"] == datetime.fromisoformat(MONDAY_OPEN).isoformat()
    assert result["execution_authority"] is False


@pytest.mark.parametrize("change", [
    {"official_open": None},
    {"official_open": _feed("official_regular_open", MONDAY_OPEN, price=99)},
    {"official_open": _feed("official_regular_open", MONDAY_OPEN, price=1000)},
    {"regular_close": _feed("quote", FRIDAY_CLOSE)},
    {"regular_close": _feed("final_regular_close", "2026-11-27T21:00:00Z")},
    {"live_quote": _feed("quote", MONDAY_OPEN)},
    {"live_quote": _feed("quote", NOW, currency="KRW")},
    {"analysis_as_of": "2026-11-30T14:29:59Z"},
    {"analysis_as_of": "2026-11-30T15:00:00Z", "live_quote": _feed("quote", "2026-11-30T15:00:00Z")},
])
def test_no_quote_no_open_wrong_gap_wrong_basis_or_expired_window_cannot_activate(change):
    assert not _evaluate(**change)["paper_candidate_ready"]


def test_independent_intraday_alternative_does_not_require_close():
    pilot = {"id": "pilot", "stage": "intraday", "direction": "above", "level": 100}
    plan = {**PLAN, "alternatives": [*PLAN["alternatives"], [pilot]]}
    stamp = "2026-11-27T17:29:00Z"
    result = _evaluate(plan, analysis_as_of=stamp, live_quote=_feed("quote", stamp))
    assert result["matched_alternatives"] == [1] and result["paper_candidate_ready"]


def test_explicit_alternatives_distinguish_reference_shared_and_ambiguous_levels():
    from tradingagents.execution.session_confirmation import _entry_alternatives

    def level(price, **fields):
        return {"level_type": "BREAKOUT", "confirmation": "intraday", "price": price, **fields}

    pilot = level(100, confirmation_group="pilot")
    follow = level(100, confirmation_group="follow", confirmation="next_session_quote")
    reference = level(200, entry_condition_role="reference")
    shared = level(102, entry_condition_role="required")
    alternatives = _entry_alternatives([pilot, reference, follow, shared], "USD", True)
    assert len(alternatives) == 2
    assert [[rule["level"] for rule in group] for group in alternatives] == [[100, 102], [100, 102]]
    moment = "2026-11-27T17:29:00Z"
    plan = {**PLAN, "alternatives": alternatives}
    assert not _evaluate(plan, analysis_as_of=moment, live_quote=_feed("quote", moment))["paper_candidate_ready"]
    assert _evaluate(plan, analysis_as_of=moment, live_quote=_feed("quote", moment, price=103))["matched_alternatives"] == [0]
    assert _entry_alternatives([pilot, level(80)], "USD", True) == []
    assert _entry_alternatives([level(80), reference], "USD", True) == [[{
        "id": "entry-0", "stage": "intraday", "direction": "above", "level": 80,
    }]]
    assert _entry_alternatives([level(100, confirmation_group="ambiguous", confirmation="next_day")], "USD", True) == []
    assert _entry_alternatives([reference], "USD", True) == []


def test_late_receipt_does_not_authorize_an_earlier_quote():
    result = _evaluate(official_open=_feed("official_regular_open", MONDAY_OPEN, observed_at=NOW),
                       live_quote=_feed("quote", "2026-11-30T14:34:59Z"))
    assert not result["paper_candidate_ready"]
    assert result["next_session_evidence_available_at"] == "2026-11-30T14:35:00+00:00"


def test_next_session_quote_and_open_are_distinct_conditions():
    open_rule = {"id": "opening", "stage": "next_open", "direction": "above", "level": 102}
    quote_rule = {"id": "reclaim", "stage": "next_session_quote", "direction": "above", "level": 102}
    result = _evaluate({**PLAN, "alternatives": [[open_rule], [quote_rule]]},
                       live_quote=_feed("quote", NOW, price=103))
    assert result["matched_alternatives"] == [1]


def test_future_price_revision_does_not_confirm_archived_open():
    result = _evaluate(official_open=_feed("official_regular_open", MONDAY_OPEN,
                                           revised_at="2026-11-30T15:00:00Z"))
    assert not result["verified_next_open"] and not result["paper_candidate_ready"]


@pytest.mark.parametrize("name,kind,clock", [
    ("regular_close", "final_regular_close", FRIDAY_CLOSE),
    ("official_open", "official_regular_open", MONDAY_OPEN),
    ("live_quote", "quote", NOW),
])
@pytest.mark.parametrize("field", ["event_at", "observed_at"])
@pytest.mark.parametrize("problem", ["missing", "invalid", "naive", "future"])
def test_unverified_stage_clocks_cannot_activate(name, kind, clock, field, problem):
    record = _feed(kind, clock)
    if problem == "missing":
        record.pop(field)
    else:
        record[field] = {"invalid": "invalid-date", "naive": clock.removesuffix("Z"),
                         "future": "2026-12-01T14:30:00Z"}[problem]
    assert not _evaluate(**{name: record})["paper_candidate_ready"]


@pytest.mark.parametrize("case", ["ready", "future_capture", "missing_open", "wrong_plan_currency", "wait",
                                  "near_deadline", "irrelevant_invalid_close"])
def test_archive_paper_entry_consumes_explicit_session_proof(tmp_path, case):
    proof = {"plan": PLAN, "regular_close": _feed("final_regular_close", FRIDAY_CLOSE),
             "official_open": _feed("official_regular_open", MONDAY_OPEN), "live_quote": _feed("quote", NOW)}
    if case == "future_capture":
        proof["official_open"]["observed_at"] = "2026-11-30T14:35:01Z"
    if case == "missing_open":
        proof.pop("official_open")
    if case == "wrong_plan_currency":
        proof["plan"] = PLAN | {"currency": "KRW"}
    generated_at, evaluated_at = NOW, "2026-11-30T14:35:15Z"
    if case == "near_deadline":
        generated_at = evaluated_at = "2026-11-30T14:39:59Z"
        proof["live_quote"] = _feed("quote", generated_at)
    if case == "irrelevant_invalid_close":
        intraday = {"id": "intraday", "stage": "intraday", "direction": "above", "level": 100}
        proof["plan"] = PLAN | {"alternatives": [*PLAN["alternatives"], [intraday]]}
        proof["regular_close"] = {"kind": "final_regular_close", "observed_at": "malformed"}
    docs = {
        "run.json": {"run_id": "test-session", "status": "success"},
        "decision_bundle_v2.json": {"market": "US", "generated_at": generated_at, "analysis_source_run_id": "test-session",
                                   "strategy_table": [{"ticker": "ABC", "market_data_asof": generated_at,
                                      "quality": {"execution_ready": True, "generated_in_current_run": True},
                                      "raw_codes": {"decision_now": "WAIT" if case == "wait" else "ADD_NOW"}}]},
        "portfolio-private/account_snapshot.json": {"as_of": NOW, "positions": [], "account_value_krw": 10_000_000},
        "portfolio-private/proposed_orders.json": {"orders": [{"canonical_ticker": "ABC", "side": "BUY", "estimated_qty": 1}]},
        "tickers/ABC/execution_contract.json": {"entry_confirmation_v2": proof},
    }
    for name, data in docs.items():
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data))
    _, result, _ = build_step(tmp_path, evaluated_at)
    if case == "wait":
        assert not result["signals"]
    else:
        signal, = result["signals"]
        ready = case in {"ready", "near_deadline", "irrelevant_invalid_close"}
        assert signal["execution_ready"] is ready
        assert signal["entry_confirmation"]["paper_candidate_ready"] is ready
        if case == "near_deadline":
            assert signal["valid_until"] == "2026-11-30T14:40:00+00:00"
