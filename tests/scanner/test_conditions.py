from datetime import datetime
import json

import pytest

from tradingagents.external.prism_models import PrismExternalSignal, PrismSignalAction
from tradingagents.scanner.conditions import evaluate_condition, validate_condition
from tradingagents.scanner.condition_editor import main
from tradingagents.scanner.prism_like_scanner import run_prism_like_scanner


def row(**overrides):
    return {"ticker": "000660", "observed_at": "2026-02-01T02:00:00+00:00", "market": "KR",
            "open": 100, "high": 110, "low": 99, "close": 109, "prev_close": 100,
            "volume": 20_000_000, "prev_volume": 10_000_000, "trading_value": 20_000_000_000,
            "market_cap": 1000_000_000_000, "halted": False, **overrides}


def scan(rows, **kwargs):
    return run_prism_like_scanner(ohlcv_rows=rows, asof="2026-02-01T02:05:00+00:00", **kwargs)


def test_compound_filter_and_scanner_integration():
    condition = {"all": [{"field": "volume_ratio", "op": "gte", "value": 1.5},
                         {"any": [{"field": "sector", "op": "eq", "value": "tech"},
                                  {"field": "daily_change_pct", "op": "gt", "value": 8}]},
                         {"not": {"field": "halted", "op": "eq", "value": True}}]}
    assert len(scan([row()], condition=condition).candidates) == 1
    assert scan([row(prev_volume=20_000_000)], condition=condition).source_counts["scanner_excluded_conditions"] == 1


@pytest.mark.parametrize("actual", [None, "nan", float("nan"), float("inf"), True, {}, []])
def test_invalid_numeric_data_is_unknown_even_under_not(actual):
    leaf = {"field": "close", "op": "gt", "value": 10}
    assert not evaluate_condition(leaf, {"close": actual})
    assert not evaluate_condition({"not": leaf}, {"close": actual})


@pytest.mark.parametrize("condition", [
    {}, {"all": []}, {"all": "bad"}, {"unknown": []},
    {"field": "__class__", "op": "eq", "value": 1},
    {"field": "close", "op": "eval", "value": "__import__('os')"},
    {"field": "close", "op": "gt", "value": "10"},
    {"field": "close", "op": "gt", "value": float("nan")},
    {"field": "halted", "op": "eq", "value": 0},
    {"field": "market", "op": "in", "value": []},
    {"field": "market", "op": "in", "value": ["KR", 1]},
    {"field": [], "op": "eq", "value": 1},
    {"field": "close", "op": [], "value": 1},
    {"field": "market", "op": "eq", "value": "KR", "code": "x"},
])
def test_bad_grammar_types_and_injection_fail_closed(condition):
    with pytest.raises(ValueError):
        validate_condition(condition)
    with pytest.raises(ValueError):
        scan([row()], condition=condition)


def test_bounded_condition_depth_and_node_count():
    condition = {"field": "close", "op": "gt", "value": 0}
    for _ in range(10):
        condition = {"not": condition}
    with pytest.raises(ValueError):
        validate_condition(condition)
    with pytest.raises(ValueError):
        validate_condition({"all": [{"field": "close", "op": "gt", "value": 0}] * 101})


@pytest.mark.parametrize("dates", [
    {"observed_at": None}, {"observed_at": "bad"}, {"observed_at": "2026-02-01"},
    {"observed_at": "2026-02-01T02:06:00+00:00"},
    {"available_at": "2026-02-01T02:06:00+00:00"},
    {"corrected_at": "2026-02-01T02:06:00+00:00"},
    {"published_at": "bad"},
])
def test_future_missing_invalid_and_delayed_dates_excluded(dates):
    result = scan([row(**dates)])
    assert result.candidates == ()
    assert result.source_counts["scanner_excluded_unavailable_rows"] == 1


def test_empty_undated_and_boundary_snapshot():
    assert not scan([]).candidates
    undated = row()
    undated.pop("observed_at")
    assert not scan([undated]).candidates
    assert len(scan([row(observed_at="2026-02-01T02:05:00+00:00")]).candidates) == 1
    with pytest.raises(ValueError):
        run_prism_like_scanner(ohlcv_rows=[], asof="2026-02-01")


@pytest.mark.parametrize("change", [{"market_cap": float("nan")}, {"market_cap": "garbage"},
                                    {"volume": -1}, {"close": 0}, {"high": 100},
                                    {"date": "2027-01-01T00:00:00+00:00"}])
def test_invalid_declared_data_cannot_bypass_gates(change):
    assert not scan([row(**change)]).candidates


def test_future_signal_does_not_change_ranking_or_score():
    normal = scan([row()])
    future = PrismExternalSignal(canonical_ticker="000660.KS", market="KR", signal_action=PrismSignalAction.BUY,
                                source_asof=datetime.fromisoformat("2026-02-01T02:06:00+00:00"),
                                ingested_at=datetime.fromisoformat("2026-02-01T02:06:00+00:00"), confidence=1)
    with_future = scan([row()], external_signals=[future])
    assert with_future.candidates == normal.candidates
    assert with_future.source_counts["prism_excluded_unavailable_signals"] == 1


def test_cli_edits_and_scans_local_fixture(tmp_path, capsys):
    rules, snapshot, output = (tmp_path / name for name in ("rules.json", "snapshot.json", "out.json"))
    assert main(["create", "--output", str(rules), "--rule", "volume_ratio", "gte", "1.5"]) == 0
    assert main(["validate", str(rules)]) == 0
    snapshot.write_text(json.dumps([row()]), encoding="utf-8")
    assert main(["scan", "--condition", str(rules), "--ohlcv", str(snapshot),
                 "--as-of", "2026-02-01T02:05:00+00:00", "--output", str(output)]) == 0
    assert len(json.loads(output.read_text(encoding="utf-8"))["candidates"]) == 1
    with pytest.raises(SystemExit):
        main(["create", "--output", str(rules), "--rule", "close", "eval", '"bad"'])
