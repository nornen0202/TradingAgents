from datetime import datetime
import sqlite3

import pytest

from tradingagents.execution.experiments import ExperimentRegistry, validate_spec, validate_chronological_research


def stamp(value):
    return datetime.fromisoformat(value)


@pytest.fixture
def spec():
    return {"id": "trial-01", "hypothesis": "AI reduces turnover against the fixed rule",
            "universe": ["AAPL"], "capital": 1000, "currency": "USD",
            "costs": {"fee_bps": 10, "slippage_bps": 10}, "benchmark": "SPY",
            "baseline_rules": {"strategy": "fixed-allocation", "weight": 0.5},
            "ai_rules": {"strategy": "fixed-rule-with-ai-veto", "model": "fixture"},
            "training_end": "2026-01-01T00:00:00+00:00",
            "forward_start": "2026-02-01T00:00:00+00:00",
            "forward_end": "2026-04-01T00:00:00+00:00"}


@pytest.fixture
def ledger(tmp_path, spec):
    clock = [stamp("2026-01-15T00:00:00+00:00")]
    registry = ExperimentRegistry(tmp_path / "trial.sqlite", clock=lambda: clock[0])
    registry.register(spec)
    yield registry, clock
    registry.close()


def decision(session_id="one", open_at="2026-02-02T14:30:00+00:00", **overrides):
    return {"session_id": session_id, "open_at": open_at, "data_as_of": "2026-01-31T20:00:00+00:00",
            "dataset_version": "fixture-v1", "baseline_weights": {"AAPL": 0.5},
            "ai_weights": {"AAPL": 0.5}, "model_cost": 0.1, "validation_seconds": 3, **overrides}


def session(session_id="one", close_at="2026-02-02T21:00:00+00:00", **overrides):
    return {"session_id": session_id, "close_at": close_at, "available_at": close_at,
            "opens": {"AAPL": 100}, "closes": {"AAPL": 110},
            "benchmark_open": 200, "benchmark_close": 210, **overrides}


def freeze_and_decide(ledger):
    registry, clock = ledger
    registry.freeze("trial-01")
    clock[0] = stamp("2026-02-02T14:29:00+00:00")
    registry.record_decision("trial-01", decision())


def test_forward_comparison_uses_identical_assumptions_and_counts_costs(ledger):
    freeze_and_decide(ledger)
    registry, clock = ledger
    clock[0] = stamp("2026-02-02T21:01:00+00:00")
    registry.record_session("trial-01", session())
    report = registry.report("trial-01", analysis_as_of=clock[0])
    assert report["sessions"] == 1
    assert report["arms"]["baseline"] == {key: value for key, value in report["arms"]["ai"].items() if key != "net_after_model_cost_pct"}
    arm = report["arms"]["baseline"]
    assert arm["execution_cost"] > 0
    assert 4.8 < arm["net_return_pct"] < 5
    assert arm["curve"][0]["cash"] >= 0
    assert arm["trade_count"] == 1
    assert arm["turnover_over_initial"] < 0.5
    assert report["arms"]["ai"]["net_after_model_cost_pct"] < arm["net_return_pct"]
    assert report["model_cost"] == 0.1
    assert report["validation_seconds"] == 3
    assert "not proof" in report["limitations"][0]


def test_past_report_is_unchanged_by_future_session(ledger):
    freeze_and_decide(ledger)
    registry, clock = ledger
    before = registry.report("trial-01", analysis_as_of=clock[0])
    clock[0] = stamp("2026-02-02T21:01:00+00:00")
    registry.record_session("trial-01", session())
    assert registry.report("trial-01", analysis_as_of="2026-02-02T14:29:00+00:00") == before
    assert before["sessions"] == 0 and before["pending_sessions"] == 1


def test_freeze_and_decision_must_precede_observations(ledger):
    registry, clock = ledger
    clock[0] = stamp("2026-02-02T14:29:00+00:00")
    with pytest.raises(ValueError, match="Freeze"):
        registry.record_decision("trial-01", decision())
    with pytest.raises(ValueError, match="before the forward start"):
        registry.freeze("trial-01")
    with pytest.raises(ValueError, match="paired decision"):
        registry.record_session("trial-01", session())


def test_records_and_frozen_spec_are_immutable(ledger):
    freeze_and_decide(ledger)
    registry, clock = ledger
    for sql in ("UPDATE experiments SET spec='{}'", "UPDATE experiments SET frozen_at=NULL",
                "DELETE FROM experiment_decisions", "UPDATE experiment_decisions SET payload='{}'",
                "DELETE FROM experiments"):
        with pytest.raises(sqlite3.IntegrityError):
            with registry.db:
                registry.db.execute(sql)
    with pytest.raises(ValueError):
        registry.freeze("trial-01")
    with pytest.raises(ValueError):
        registry.record_decision("trial-01", decision())


@pytest.mark.parametrize("change", [
    {"capital": float("nan")}, {"capital": -1}, {"universe": ["A", "A"]},
    {"training_end": "bad"}, {"forward_start": "2026-02-01"},
    {"costs": {"fee_bps": 0, "slippage_bps": float("inf")}},
    {"baseline_rules": {}}, {"unknown": 1},
])
def test_invalid_preregistration(spec, change):
    with pytest.raises((ValueError, TypeError)):
        validate_spec({**spec, **change})


@pytest.mark.parametrize("change", [
    {"data_as_of": "2026-02-03T00:00:00+00:00"},
    {"data_as_of": "2026-02-01"}, {"data_as_of": None},
    {"baseline_weights": {"UNKNOWN": 1}}, {"ai_weights": {"AAPL": 1.1}},
    {"ai_weights": {"AAPL": -0.1}}, {"ai_weights": {"AAPL": float("nan")}},
    {"model_cost": -1}, {"validation_seconds": True}, {"dataset_version": ""},
    {"open_at": "2026-02-02T14:28:00+00:00"},
])
def test_invalid_or_contaminated_decision_fails_closed(ledger, change):
    registry, clock = ledger
    registry.freeze("trial-01")
    clock[0] = stamp("2026-02-02T14:29:00+00:00")
    with pytest.raises((ValueError, TypeError)):
        registry.record_decision("trial-01", decision(**change))
    assert registry.db.execute("SELECT COUNT(*) FROM experiment_decisions").fetchone()[0] == 0


@pytest.mark.parametrize("change", [
    {"close_at": None}, {"available_at": "bad"}, {"close_at": "2026-02-02"},
    {"available_at": "2026-02-03T00:00:00+00:00"}, {"opens": {}},
    {"closes": {"AAPL": float("nan")}}, {"benchmark_close": 0},
])
def test_invalid_empty_or_future_price_observation_fails_closed(ledger, change):
    freeze_and_decide(ledger)
    registry, clock = ledger
    clock[0] = stamp("2026-02-02T21:01:00+00:00")
    with pytest.raises((ValueError, TypeError)):
        registry.record_session("trial-01", session(**change))
    assert registry.db.execute("SELECT COUNT(*) FROM experiment_sessions").fetchone()[0] == 0


def test_future_freeze_hidden_in_historical_report(ledger):
    registry, clock = ledger
    clock[0] = stamp("2026-01-16T00:00:00+00:00")
    registry.freeze("trial-01")
    result = registry.report("trial-01", analysis_as_of="2026-01-15T00:00:00+00:00")
    assert result["frozen_at"] is None
    assert result["sessions"] == 0


def test_later_observation_cannot_skip_losing_or_missing_session(ledger):
    freeze_and_decide(ledger)
    registry, clock = ledger
    clock[0] = stamp("2026-02-03T14:29:00+00:00")
    registry.record_decision("trial-01", decision("two", "2026-02-03T14:30:00+00:00"))
    clock[0] = stamp("2026-02-03T21:01:00+00:00")
    with pytest.raises(ValueError, match="all earlier sessions"):
        registry.record_session("trial-01", session("two", "2026-02-03T21:00:00+00:00"))


def test_forward_drawdown_and_turnover_and_chronology(ledger):
    freeze_and_decide(ledger)
    registry, clock = ledger
    clock[0] = stamp("2026-02-02T21:01:00+00:00")
    registry.record_session("trial-01", session(closes={"AAPL": 120}))
    clock[0] = stamp("2026-02-03T14:29:00+00:00")
    registry.record_decision("trial-01", decision("two", "2026-02-03T14:30:00+00:00", ai_weights={"AAPL": 0}))
    clock[0] = stamp("2026-02-03T21:01:00+00:00")
    registry.record_session("trial-01", session("two", "2026-02-03T21:00:00+00:00", opens={"AAPL": 120}, closes={"AAPL": 80}))
    report = registry.report("trial-01", analysis_as_of=clock[0])
    assert report["arms"]["baseline"]["max_drawdown_pct"] < -10
    assert report["arms"]["ai"]["trade_count"] == 2
    assert report["arms"]["ai"]["turnover_over_initial"] > 1
    assert all(row["cash"] >= -1e-9 for arm in report["arms"].values() for row in arm["curve"])
    with pytest.raises(ValueError, match="future"):
        registry.report("trial-01", analysis_as_of="2027-01-01T00:00:00+00:00")


def research_inputs():
    import pandas as pd

    prices = pd.DataFrame({"AAPL": [100, 105, 110, 90, 99999]},
                          index=pd.date_range("2026-02-01T21:00:00+00:00", periods=5))
    options = {"training_end": "2026-02-01T21:00:00+00:00", "evaluation_start": "2026-02-02T21:00:00+00:00",
               "evaluation_end": "2026-02-04T21:00:00+00:00", "analysis_as_of": "2026-02-04T22:00:00+00:00",
               "initial": 1000, "cost_bps": 10}
    return prices, options


def test_offline_holdout_is_chronological_and_future_independent():
    prices, options = research_inputs()
    rule = lambda panel: panel * 0 + 0.5
    result = validate_chronological_research(prices, prices, rule, rule, **options)
    assert result["arms"]["baseline"] == result["arms"]["ai"]
    assert result["arms"]["baseline"]["prefix_validation"]["checked_prefixes"] == 2
    prices.iloc[-1] = float("nan")
    assert validate_chronological_research(prices, prices, rule, rule, **options) == result


def test_offline_holdout_rejects_future_reading_rule():
    prices, options = research_inputs()
    normal = lambda panel: panel * 0 + 0.5
    lookahead = lambda panel: panel * 0 + (0.8 if panel.iloc[-1, 0] > 100 else 0.1)
    with pytest.raises(ValueError, match="changes past decisions"):
        validate_chronological_research(prices, prices, normal, lookahead, **options)
    with pytest.raises(ValueError, match="research cutoff"):
        validate_chronological_research(prices, prices, normal, normal,
                                        **{**options, "training_end": options["evaluation_start"]})
    prices.index = prices.index.tz_localize(None)
    with pytest.raises(ValueError, match="timezone-aware"):
        validate_chronological_research(prices, prices, normal, normal, **options)
