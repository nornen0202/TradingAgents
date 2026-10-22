"""Offline point-in-time memory evidence and append-only retention checks."""
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import sqlite3
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from tradingagents.agents.utils.memory import FinancialSituationMemory
from tradingagents.agents.utils import memory as memory_module
from tradingagents.graph import reflection


NOW = datetime(2026, 3, 2, 12, tzinfo=timezone.utc)


def metadata(**changes):
    return {"trade_date": "2026-03-01", "outcome_known_at": "2026-03-02T10:00:00+00:00",
            "settlement_date": "2026-03-02T11:00:00+00:00", "available_at": NOW.isoformat(),
            "ingested_at": NOW.isoformat(), "sector": "technology", **changes}


def baseline(memory):
    memory.add_situations([
        ("alpha earnings volatility market", "first", metadata()),
        ("alpha guidance beta", "second", metadata()),
        ("delta interest rate market", "third", metadata()),
    ])


@pytest.mark.parametrize("as_of", ["2026-03-02", "2026-03-03", NOW + timedelta(hours=2), None])
@pytest.mark.parametrize("future_field", ["available_at", "ingested_at"])
@pytest.mark.parametrize("max_entries", [3, 500])
def test_actual_now_caps_current_and_future_asof_before_ranking_and_retention(
        monkeypatch, tmp_path, as_of, future_field, max_entries):
    monkeypatch.setattr(memory_module, "_utc_now", lambda: NOW, raising=False)
    config = {"memory_dir": str(tmp_path), "memory_max_entries": max_entries}
    memory = FinancialSituationMemory("current_day", config)
    memory.as_of = "2026-03-02"
    baseline(memory)
    kwargs = dict(n_matches=3, as_of=as_of)
    expected = memory.get_memories("alpha earnings volatility", **kwargs)
    assert len(expected) == 3  # Evidence available exactly now remains eligible.
    future = (NOW + timedelta(hours=1)).isoformat()
    clocks = metadata(ingested_at=future)
    if future_field == "available_at":
        clocks[future_field] = future
    memory.add_situations([("alpha earnings volatility " * 100, "same-day future", clocks)])
    assert memory.get_memories("alpha earnings volatility", **kwargs) == expected
    loaded = FinancialSituationMemory("current_day", config)
    loaded.as_of = "2026-03-02"
    assert loaded.get_memories("alpha earnings volatility", **kwargs) == expected
    assert len(loaded.documents) == 4


def test_actual_now_cap_preserves_historical_eod_and_exact_midnight_boundary(monkeypatch):
    clock = [NOW + timedelta(days=1)]
    monkeypatch.setattr(memory_module, "_utc_now", lambda: clock[0], raising=False)
    memory = FinancialSituationMemory("past_snapshot", {"memory_max_entries": 3})
    baseline(memory)
    end = "2026-03-02T23:59:59.999999Z"
    memory.add_situations([("alpha guidance", "end of past day", metadata(available_at=end, ingested_at=end))])
    expected = memory.get_memories("alpha earnings volatility", n_matches=3, as_of="2026-03-02")
    assert len(expected) == 3
    assert "end of past day" in {row["recommendation"] for row in expected}
    midnight = "2026-03-03T00:00:00Z"
    memory.add_situations([("alpha earnings volatility " * 100, "next midnight",
                           metadata(available_at=midnight, ingested_at=midnight))])
    clock[0] = datetime(2026, 3, 3, tzinfo=timezone.utc)
    assert memory.get_memories("alpha earnings volatility", n_matches=3, as_of="2026-03-02") == expected
    # The historical date upper bound excludes midnight even when it is now;
    # an exact aware upper bound includes that same verified instant.
    assert "next midnight" in {row["recommendation"] for row in memory.get_memories("alpha", n_matches=3, as_of=midnight)}


@pytest.mark.parametrize("field", ["outcome_known_at", "settlement_date", "settled_at", "available_at", "ingested_at"])
def test_future_clocks_cannot_change_results_or_bm25_and_tag_scores(field):
    memory = FinancialSituationMemory("clocks")
    baseline(memory)
    expected = memory.get_memories("alpha earnings volatility", n_matches=3, as_of=NOW)
    assert len(expected) == 3
    memory.add_situations([("alpha earnings volatility " * 100, "future",
                           metadata(**{field: (NOW + timedelta(microseconds=1)).isoformat()}))])
    assert memory.get_memories("alpha earnings volatility", n_matches=3, as_of=NOW) == expected


@pytest.mark.parametrize("field", ["outcome_known_at", "available_at", "ingested_at"])
@pytest.mark.parametrize("value", [None, "", "broken", "2026-03-02", "2026-03-02T10:00:00"])
def test_missing_or_unverified_required_clocks_are_excluded(field, value):
    memory = FinancialSituationMemory("invalid")
    broken = metadata(**{field: value})
    absent = metadata()
    absent.pop(field)
    memory.add_situations([("earnings", "invalid", broken), ("earnings", "missing", absent)])
    assert memory.get_memories("earnings", as_of=NOW) == []


@pytest.mark.parametrize("changes", [
    {"settlement_date": None}, {"settlement_date": "bad"}, {"settlement_date": "2026-03-02"},
    {"trade_date": None}, {"trade_date": "bad"}, {"trade_date": "2026-03-03"},
    {"ingested_at": "2026-03-02T11:59:59+00:00"},
    {"available_at": "2026-03-02T09:59:59+00:00"},
])
def test_invalid_optional_clocks_and_reversed_chronology_are_excluded(changes):
    memory = FinancialSituationMemory("ordering")
    memory.add_situations([("earnings", "invalid", metadata(**changes))])
    assert memory.get_memories("earnings", as_of=NOW) == []


def test_timestamp_cutoff_is_exact_inclusive_and_timezone_aware():
    memory = FinancialSituationMemory("boundary")
    baseline(memory)
    expected = memory.get_memories("alpha", n_matches=3, as_of=NOW)
    assert len(expected) == 3
    assert memory.get_memories("alpha", n_matches=3, as_of="2026-03-02T21:00:00+09:00") == expected
    assert memory.get_memories("alpha", n_matches=3, as_of="2026-03-02T12:00:00Z") == expected
    assert memory.get_memories("alpha", as_of=NOW - timedelta(microseconds=1)) == []
    memory.as_of = NOW
    assert memory.get_memories("alpha", n_matches=3) == expected


@pytest.mark.parametrize("cutoff", ["", "broken", "2026-03-02T12:00:00", datetime(2026, 3, 2, 12)])
def test_invalid_query_clock_is_rejected_even_for_empty_memory(cutoff):
    with pytest.raises(ValueError):
        FinancialSituationMemory("empty").get_memories("alpha", as_of=cutoff)


def test_date_query_is_entire_utc_day_and_does_not_relax_available_or_ingested_clocks():
    memory = FinancialSituationMemory("dates")
    old = {"trade_date": "2026-03-01", "outcome_known_at": "2026-03-02", "settlement_date": "2026-03-02"}
    end = "2026-03-02T23:59:59.999999+00:00"
    memory.add_situations([
        ("earnings", "day", {**old, "available_at": end, "ingested_at": end}),
        ("earnings", "midnight", {**old, "available_at": "2026-03-03T00:00:00Z", "ingested_at": "2026-03-03T00:00:00Z"}),
        ("earnings", "legacy-missing", old),
        ("earnings", "date-availability", {**old, "available_at": "2026-03-02", "ingested_at": end}),
    ])
    assert [row["recommendation"] for row in memory.get_memories("earnings", as_of="2026-03-02")] == ["day"]
    # A date outcome is not proof of an exact intraday availability.
    assert memory.get_memories("earnings", as_of=end) == []


def test_retention_after_eligibility_preserves_history_and_scores_over_100_reloads(tmp_path):
    config = {"memory_dir": str(tmp_path), "memory_max_entries": 3}
    memory = FinancialSituationMemory("retention", config)
    baseline(memory)
    kwargs = dict(n_matches=3, as_of=NOW, metadata_filters={"sector": "technology"})
    expected = memory.get_memories("alpha earnings volatility", **kwargs)
    assert len(expected) == 3
    with sqlite3.connect(memory.store_path) as connection:
        originals = connection.execute("SELECT * FROM memories ORDER BY id").fetchall()
    for number in range(100):
        # Reload before every append: neither a load-time LIMIT nor a write-time
        # trim may evict earlier eligible evidence from the query's active cap.
        memory = FinancialSituationMemory("retention", config)
        assert memory.get_memories("alpha earnings volatility", **kwargs) == expected
        cases = [metadata(available_at=(NOW + timedelta(days=1)).isoformat()),
                 metadata(ingested_at=(NOW + timedelta(days=1)).isoformat()),
                 metadata(available_at=None), metadata(sector="unrelated")]
        memory.add_situations([("alpha earnings volatility " * (number + 1), f"excluded-{number}", cases[number % 4])])
        assert memory.get_memories("alpha earnings volatility", **kwargs) == expected
    loaded = FinancialSituationMemory("retention", config)
    assert len(loaded.documents) == 103
    assert loaded.get_memories("alpha earnings volatility", **kwargs) == expected
    with sqlite3.connect(memory.store_path) as connection:
        rows = connection.execute("SELECT * FROM memories ORDER BY id").fetchall()
    assert len(rows) == 103
    assert rows[:3] == originals


def test_active_limit_applies_to_last_eligible_rows_without_deleting_older_ones(tmp_path):
    memory = FinancialSituationMemory("active", {"memory_dir": str(tmp_path), "memory_max_entries": 3})
    baseline(memory)
    memory.add_situations([("alpha earnings", "fourth", metadata())])
    found = memory.get_memories("alpha", n_matches=10, as_of=NOW)
    assert {row["recommendation"] for row in found} == {"second", "third", "fourth"}
    assert len(memory.documents) == 4
    with sqlite3.connect(memory.store_path) as connection:
        assert connection.execute("SELECT count(*) FROM memories").fetchone()[0] == 4


def test_metadata_copies_and_sqlite_reload_do_not_mutate_originals(tmp_path):
    memory = FinancialSituationMemory("copies", {"memory_dir": str(tmp_path)})
    original = metadata()
    memory.add_situations([("alpha", "kept", original)])
    original["ingested_at"] = (NOW + timedelta(days=1)).isoformat()
    expected = memory.get_memories("alpha", as_of=NOW)
    returned = memory.get_memories("alpha", as_of=NOW)
    returned[0]["metadata"]["ingested_at"] = original["ingested_at"]
    assert memory.get_memories("alpha", as_of=NOW) == expected
    with sqlite3.connect(memory.store_path) as connection:
        connection.execute("INSERT INTO memories (situation, advice, metadata) VALUES (?, ?, ?)", ("alpha", "legacy", "bad-json"))
    loaded = FinancialSituationMemory("copies", {"memory_dir": str(tmp_path)})
    assert loaded.get_memories("alpha", as_of=NOW) == expected
    with sqlite3.connect(memory.store_path) as connection:
        assert connection.execute("SELECT metadata FROM memories WHERE advice='legacy'").fetchone()[0] == "bad-json"


@pytest.mark.parametrize("component", ["bull_researcher", "bear_researcher", "trader", "invest_judge", "portfolio_manager"])
def test_reflection_stamps_actual_availability_after_model_completion(monkeypatch, component):
    clock = [NOW]
    class Clock(datetime):
        @classmethod
        def now(cls, tz=None):
            return clock[0].astimezone(tz)
    monkeypatch.setattr(reflection, "datetime", Clock)
    state = {"company_of_interest": "AAPL", "trade_date": "2026-03-01", "analysis_date": "2026-03-01",
             "outcome_known_at": "2026-03-02T10:00:00+00:00", "settlement_date": "2026-03-02T11:00:00+00:00",
             "available_at": "2026-03-01T00:00:00+00:00", "ingested_at": "2026-03-01T00:00:00+00:00",
             "market_report": "market", "sentiment_report": "sentiment", "news_report": "news",
             "fundamentals_report": "fundamentals", "trader_investment_plan": "legacy plan",
             "investment_debate_state": {"bull_history": "bull", "bear_history": "bear", "judge_decision": "judge"},
             "risk_debate_state": {"judge_decision": "risk"}}
    original = deepcopy(state)
    def complete(*args, **kwargs):
        clock[0] += timedelta(minutes=1)
        return SimpleNamespace(content="completed lesson")
    llm = Mock()
    llm.invoke.side_effect = complete
    memory = FinancialSituationMemory("reflected")
    getattr(reflection.Reflector(llm), f"reflect_{component}")(state, 0.01, memory)
    assert state == original
    assert memory.metadata[0]["available_at"] == memory.metadata[0]["ingested_at"] == clock[0].isoformat()
    assert memory.get_memories("market", as_of=NOW) == []
    assert len(memory.get_memories("market", as_of=clock[0])) == 1
    llm.invoke.assert_called_once()


@pytest.mark.parametrize("field,value", [
    ("outcome_known_at", "2099-01-01T00:00:00Z"), ("outcome_known_at", "2026-03-02T10:00:00"),
    ("outcome_known_at", None), ("settlement_date", "2099-01-01"), ("settlement_date", "bad"),
])
def test_reflection_rejects_unverified_or_future_outcome_before_model(field, value):
    llm, memory = Mock(), Mock()
    state = {"trade_date": "2026-03-01", "outcome_known_at": "2026-03-02", field: value}
    with pytest.raises(ValueError):
        reflection.Reflector(llm).reflect_bull_researcher(state, 0.1, memory)
    llm.invoke.assert_not_called()
    memory.add_situations.assert_not_called()
