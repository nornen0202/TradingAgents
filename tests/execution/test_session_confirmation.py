from datetime import datetime

import pytest

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
