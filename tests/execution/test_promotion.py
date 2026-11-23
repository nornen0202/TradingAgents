from datetime import datetime, timedelta, timezone
import sqlite3

import pytest

from tradingagents.execution.promotion import PromotionLedger, _sessions


START = datetime(2026, 9, 1, tzinfo=timezone.utc)
POLICY = {"version": "fixture-v1", "market": "US", "sample_kind": "round_trip",
          "minimum_sessions": 60, "cost_version": "cost-fixture-v1", "benchmark": "fixture-60-40"}


def _calendar(_market, start, now):
    for number in range(1, 66):
        opening = START + timedelta(days=number, hours=14)
        close = opening + timedelta(hours=6)
        if start < opening and close <= now:
            yield opening.date().isoformat(), opening, close


def _sample(index, **changes):
    return {"cost_version": POLICY["cost_version"], "benchmark": POLICY["benchmark"],
            "regime": "risk_on" if index % 2 else "risk_off", "net_return": 0.005 * (index % 2),
            "benchmark_net_return": -0.02 if index % 2 == 0 else 0.005, "samples": [f"sample-{index}"],
            "order_ids": [f"order-{index}"], "mismatches": 0, "monitored_seconds": 21600,
            "kill_switch_drill_id": "fixture-drill" if index == 1 else None, "source_id": f"paper-{index}",
            **changes}


def test_fixture_can_exercise_each_threshold_without_becoming_forward_evidence(tmp_path):
    clock = [START]
    with PromotionLedger(tmp_path / "promotion.sqlite", clock=lambda: clock[0], sessions=_calendar) as ledger:
        assert ledger.start(POLICY) == ledger.start(POLICY)
        with pytest.raises(ValueError, match="repurposed"):
            ledger.start({**POLICY, "minimum_sessions": 61})
        for day in range(1, 61):
            clock[0] = START + timedelta(days=day, hours=20)
            assert ledger.record(POLICY["version"], clock[0].date().isoformat(), _sample(day))
        result = ledger.status(POLICY["version"])
        assert result["expected_sessions"] == result["observed_sessions"] == 60
        assert result["availability"] == 1
        assert all(value for name, value in result["checks"].items() if name != "forward_observation")
        assert result["eligible_for_review"] is result["live_order_authority"] is False


def test_missing_days_and_duplicates_are_visible_in_the_denominator(tmp_path):
    clock = [START]
    with PromotionLedger(tmp_path / "promotion.sqlite", clock=lambda: clock[0], sessions=_calendar) as ledger:
        ledger.start(POLICY)
        for number in (1, 3):
            clock[0] = START + timedelta(days=number, hours=20)
            ledger.record(POLICY["version"], clock[0].date().isoformat(), _sample(number, order_ids=["same"]))
        result = ledger.status(POLICY["version"])
        assert (result["expected_sessions"], result["observed_sessions"], result["missing_sessions"]) == (3, 2, 1)
        assert result["duplicate_orders"] == 1
        assert result["availability"] == pytest.approx(2 / 3)
        assert result["checks"]["reconciliation"] is False


def test_future_late_edited_and_duplicate_observations(tmp_path):
    clock = [START]
    path = tmp_path / "promotion.sqlite"
    with PromotionLedger(path, clock=lambda: clock[0], sessions=_calendar) as ledger:
        ledger.start(POLICY)
        with pytest.raises(ValueError, match="before observation"):
            ledger.record(POLICY["version"], "2026-09-02", _sample(1))
        clock[0] += timedelta(days=1, hours=20)
        assert ledger.record(POLICY["version"], "2026-09-02", _sample(1))
        assert not ledger.record(POLICY["version"], "2026-09-02", _sample(1))
        with pytest.raises(ValueError, match="Conflicting"):
            ledger.record(POLICY["version"], "2026-09-02", _sample(1, mismatches=1))
        clock[0] += timedelta(days=2)
        with pytest.raises(ValueError, match="expired"):
            ledger.record(POLICY["version"], "2026-09-03", _sample(2))
    with sqlite3.connect(path) as db, pytest.raises(sqlite3.IntegrityError, match="append-only"):
        db.execute("DELETE FROM promotion_days")


def test_real_calendar_uses_early_close_and_holiday():
    start = datetime(2026, 11, 25, 22, tzinfo=timezone.utc)
    current = datetime(2026, 11, 27, 19, tzinfo=timezone.utc)
    assert [(day, close.hour) for day, _, close in _sessions("US", start, current)] == [("2026-11-27", 18)]


@pytest.mark.parametrize("day", [None, "", "malformed", "20260902", "2026-09-31"])
def test_unverified_session_dates_leave_promotion_evidence_empty(tmp_path, day):
    clock = [START]
    path = tmp_path / "promotion.sqlite"
    with PromotionLedger(path, clock=lambda: clock[0], sessions=_calendar) as ledger:
        ledger.start(POLICY)
        clock[0] += timedelta(days=1, hours=20)
        with pytest.raises(ValueError):
            ledger.record(POLICY["version"], day, _sample(1))
        result = ledger.status(POLICY["version"])
        assert result["observed_sessions"] == 0
        assert result["expected_sessions"] == result["missing_sessions"] == 1
    with sqlite3.connect(path) as db:
        assert db.execute("SELECT COUNT(*) FROM promotion_days").fetchone() == (0,)
