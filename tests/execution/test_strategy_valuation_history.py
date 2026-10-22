"""Bounded valuation display windows; no broker, model or external data calls."""
from contextlib import closing
from datetime import datetime, timedelta, timezone
import json
import sqlite3

import pytest

from tradingagents.execution import demo_runtime
from tests.execution.test_demo_runtime import Harness


NOW = datetime(2026, 10, 19, 15, tzinfo=timezone.utc)


def add(db, moment, **payload):
    text = moment.isoformat() if isinstance(moment, datetime) else moment
    value = {"observed_at": text, **payload}
    db.execute("INSERT INTO strategy_valuations VALUES (?,?)", (text, json.dumps(value)))
    return value


def test_future_valuations_cannot_evict_past_history_or_change_past_summary():
    with closing(sqlite3.connect(":memory:")) as db:
        db.row_factory = sqlite3.Row
        demo_runtime.initialize(db)
        past = [add(db, NOW - timedelta(minutes=3-i), value=i) for i in range(3)]
        before = demo_runtime.summary(db, NOW, "US")
        assert before["performance_history"] == past
        for i in range(60):
            # An unavailable future payload must not even be decoded.
            db.execute("INSERT INTO strategy_valuations VALUES (?,?)", ((NOW + timedelta(minutes=i+1)).isoformat(), "not-json"))
        assert demo_runtime.summary(db, NOW, "US") == before


def test_offset_clocks_select_actual_latest_sixty_and_display_ascending():
    with closing(sqlite3.connect(":memory:")) as db:
        demo_runtime.initialize(db)
        rows = []
        for i in range(61):
            moment = NOW - timedelta(minutes=61-i)
            # Latest instant's text sorts before every older UTC value.
            if i == 60:
                moment = moment.astimezone(timezone(timedelta(hours=-8)))
            rows.append(add(db, moment, number=i))
        result = demo_runtime._performance_history(db, NOW)
        assert result == rows[1:]
        assert len(result) == 60


@pytest.mark.parametrize("count", [0, 1, 59, 60, 61, 120])
def test_history_limit_exactly_sixty_after_cutoff_filter(count):
    with closing(sqlite3.connect(":memory:")) as db:
        demo_runtime.initialize(db)
        rows = [add(db, NOW - timedelta(seconds=count-i), number=i) for i in range(count)]
        assert demo_runtime._performance_history(db, NOW) == rows[-60:]


@pytest.mark.parametrize("clock", [None, "", "bad", "2026-02-30T14:00:00Z", "2026-10-19T14:00:00", "2026-10-19"])
def test_undated_invalid_or_naive_valuation_is_excluded_before_payload_decode(clock):
    with closing(sqlite3.connect(":memory:")) as db:
        demo_runtime.initialize(db)
        wanted = add(db, NOW)
        db.execute("INSERT INTO strategy_valuations VALUES (?,?)", (clock, "not-json"))
        assert demo_runtime._performance_history(db, NOW) == [wanted]


@pytest.mark.parametrize("clock", [None, "bad", "2026-10-19T15:00:00", "2026-02-30T15:00:00Z"])
def test_history_requires_valid_aware_cutoff(clock):
    with closing(sqlite3.connect(":memory:")) as db:
        demo_runtime.initialize(db)
        with pytest.raises(ValueError):
            demo_runtime._performance_history(db, clock)


def test_only_selected_payloads_are_decoded_and_no_ledger_rows_change():
    with closing(sqlite3.connect(":memory:")) as db:
        demo_runtime.initialize(db)
        db.execute("INSERT INTO strategy_valuations VALUES (?,?)", ((NOW - timedelta(days=1)).isoformat(), "not-json"))
        wanted = [add(db, NOW - timedelta(seconds=60-i)) for i in range(60)]
        before = db.execute("SELECT * FROM strategy_valuations ORDER BY observed_at").fetchall()
        assert demo_runtime._performance_history(db, NOW) == wanted
        assert db.execute("SELECT * FROM strategy_valuations ORDER BY observed_at").fetchall() == before


@pytest.mark.parametrize("market", ["KR", "US"])
def test_post_valuation_write_uses_same_cutoff_safe_history_reader(tmp_path, market):
    h = Harness(tmp_path, market)
    h.tick()
    h.now += timedelta(seconds=20)
    h.fill()
    before = h.tick()
    with closing(sqlite3.connect(h.root / f"{market.lower()}-strategy.sqlite")) as db:
        for i in range(60):
            db.execute("INSERT INTO strategy_valuations VALUES (?,?)", ((h.now + timedelta(days=1, seconds=i)).isoformat(), "not-json"))
        db.commit()
    h.now += timedelta(seconds=20)
    after = h.tick()
    assert after["performance_history"][:-1] == before["performance_history"]
    assert all(demo_runtime.at(row["observed_at"]) <= h.now for row in after["performance_history"])
    assert after["performance_history"][-1] == after["performance"]
