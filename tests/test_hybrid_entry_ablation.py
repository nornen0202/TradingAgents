from datetime import date, datetime, timedelta
from types import SimpleNamespace

import pytest

from tools.compare_hybrid_entries import EntryStudy, period_diagnostics
from tools.hybrid_entry_evidence import NO_OBSERVATION, bind_action, load_observations
from tools.hybrid_audit_inputs import digest
from tools.run_hybrid_quant_backtest import simulate_after_tax_walk_forward
from tradingagents.backtest import _digest


def bars(n=115):
    return [{"date": (date(2024, 1, 1) + timedelta(days=i)).isoformat(),
             "open": 100 + i, "close": 101 + i, "volume": 10, "executable_volume": 10} for i in range(n)]


def test_breakout_uses_only_observed_history_and_preserves_core():
    rows = bars()
    cutoff = rows[70]["date"]
    spec = {"core": ["ETF"], "satellite": ["A", "B", "C", "D"]}
    panels = {s: rows for s in spec["satellite"]}
    signals = EntryStudy(panels, spec, {}).targets(cutoff, {"ETF": .5, "OLD": .1})
    assert signals == {"ETF": .5, "A": .1, "B": .1, "C": .1}
    panels["A"] = [r for r in rows if r["date"] != cutoff]
    panels["B"] = [r | {"executable_volume": 0} if r["date"] == cutoff else r for r in rows]
    panels["C"] = [r | {"close": 999999} if r["date"] > cutoff else r for r in rows]
    assert EntryStudy(panels, spec, {}).targets(cutoff, {}) == {"C": .1, "D": .1}
    policy = {"budget_satellite": .3, "asset_cap": .65, "annual_volatility_target": .22,
              "volatility_window": 20, "satellite_limit": 3}
    assert EntryStudy(panels, spec, {}).targets(cutoff, {}, sizing_policy=policy) == {"C": .15, "D": .15}


@pytest.mark.parametrize("bad,expected", [("hash", "manifest_unverified"), ("future", "unavailable_by_signal"),
                                          ("missing", "no_explicit_risk_action"), ("altered", "decision_unverified"),
                                          ("normal", "verified")])
def test_explicit_bound_decision_only(bad, expected):
    day = "2024-01-01"
    stamp = day + "T20:00:00+00:00"
    decision = {} if bad == "missing" else {"risk_action": "STOP_LOSS"}
    row = {"ticker": "A", "finished_at": stamp, "decision": decision}
    manifest = {"finished_at": day + ("T23:00:00+00:00" if bad == "future" else "T21:00:00+00:00"), "tickers": [row]}
    record = {"ticker": "A", "executed_at": stamp, "original_decision_sha256": "other" if bad == "altered" else _digest(decision)}
    bound, status = bind_action(record, manifest, b"receipt", "wrong" if bad == "hash" else digest(b"receipt"),
                                datetime.fromisoformat(day + "T22:00:00+00:00"))
    assert status == expected
    assert (bound is None) == (expected != "verified")


@pytest.mark.parametrize("field", ["record", "manifest", "row"])
@pytest.mark.parametrize("invalid", [None, "not-a-date", "2024-01-01"])
def test_missing_malformed_or_naive_times_cannot_certify_an_observation(field, invalid):
    stamp = "2024-01-01T20:00:00+00:00"
    decision = {"risk_action": "EXIT"}
    row = {"ticker": "A", "finished_at": stamp, "decision": decision}
    manifest = {"finished_at": stamp, "tickers": [row]}
    record = {"ticker": "A", "executed_at": stamp, "original_decision_sha256": _digest(decision)}
    container, key = {"record": (record, "executed_at"), "manifest": (manifest, "finished_at"),
                      "row": (row, "finished_at")}[field]
    if invalid is None:
        del container[key]
    else:
        container[key] = invalid
    bound, _ = bind_action(record, manifest, b"receipt", digest(b"receipt"), datetime.fromisoformat(stamp))
    assert bound is None


def test_empty_evidence_response_keeps_no_observation(monkeypatch, tmp_path):
    evaluation = {"manifest": {"settlement_cutoff": "2024-01-01T22:00:00+00:00"}, "records": []}
    monkeypatch.setattr("tools.hybrid_entry_evidence.frozen_json",
                        lambda path, hash_: evaluation if path.name == "evaluation.json" else [])
    observations, counts = load_observations(tmp_path, tmp_path, "US", {"ETF"}, {"2024-01-01"})
    assert (observations, counts) == ({}, {})
    assert EntryStudy({}, {"core": [], "satellite": []}, observations).risk_at("2024-01-01", "ETF") == NO_OBSERVATION


def test_veto_only_blocks_incremental_buys_and_attribution_reconciles(monkeypatch):
    monkeypatch.setattr("tools.run_hybrid_quant_backtest.evaluate_hybrid_portfolio_proposal",
                        lambda *args, **kwargs: {"after_veto": {"weights": {}}})
    rows = bars()
    days = [r["date"] for r in rows]
    def target(day, original, **kwargs):
        return {"A": .1 if day == days[70] else .4 if day == days[91] else 0}
    study = SimpleNamespace(targets=target, risk_at=lambda d, t: "EXIT" if d == days[91] else NO_OBSERVATION)
    traces = {}
    simulate_after_tax_walk_forward({"A": rows, "ETF": rows}, market="US", core_tickers=["ETF"],
                                    satellite_tickers=["A"], benchmark_ticker="ETF", fill_timing="next_open",
                                    audit_traces=traces, entry_study=study)
    q, v = traces["quant_breakout"], traces["quant_breakout_veto"]
    assert v["signals"] == q["signals"]
    assert [f[3] for f in q["fills"]] == ["buy", "buy", "sell"]
    assert [f[3] for f in v["fills"]] == ["buy", "sell"]
    assert v["opportunities"] == [(days[70], days[71], "A", NO_OBSERVATION, False, "new"),
                                  (days[91], days[92], "A", "EXIT", True, "add")]
    benchmark = {days[i]: rows[i]["close"] / rows[i - 1]["close"] - 1 for i in range(1, len(rows))}
    result = period_diagnostics(v, [days[70], days[-1]], dict.fromkeys(days, 86400), benchmark)
    assert result["buy_opportunities"] == 2 and result["observed"] == result["blocked"] == 1
    assert result["new_positions"] == result["adds"] == result["observed_adds"] == 1
    assert result["observed_new_positions"] == 0
    assert result["benchmark_return"] + sum(result["linked_return_contributions"].values()) == pytest.approx(result["net_time_weighted_return"])
    assert sum(result["mean_close_weight"].values()) == pytest.approx(1)
    assert sum(result["elapsed_time_weight"].values()) == pytest.approx(1)
