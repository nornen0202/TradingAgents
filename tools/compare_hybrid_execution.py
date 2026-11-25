"""Offline, paired #569 execution sensitivity and #553 preserved-ledger comparison."""
from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path
from statistics import fmean, median

from tools.hybrid_audit_inputs import PLAN, digest, parse_chart
from tools.run_hybrid_quant_backtest import simulate_after_tax_walk_forward
from tradingagents.execution.research_comparison import _stats, compare_market_benchmarks
from tradingagents.execution.research_study import research_sessions


def canonical_hash(value):
    return digest(json.dumps(value, sort_keys=True, separators=(",", ":")).encode())


def period_stats(trace, start, end):
    nav, prior_fills = trace["initial_nav"], 0
    returns, dates = [], []
    fills = 0
    for day, mark, cumulative in zip(trace["days"], trace["nav"], trace["cumulative_fills"], strict=True):
        if start <= day <= end:
            dates.append(day)
            returns.append(mark / nav - 1)
            fills += cumulative - prior_fills
        nav, prior_fills = mark, cumulative
    if not dates:
        raise ValueError("Empty evaluation window")
    return {"first": dates[0], "last": dates[-1], "marks": len(dates), "returns": len(returns),
            "fills": fills, **_stats(returns)}


def compare_fills(close_trace, open_trace):
    def keyed(trace):
        return {(signal, ticker, side): (day, price) for signal, day, ticker, side, price in trace["fills"]}

    closes, opens = keyed(close_trace), keyed(open_trace)
    pairs = sorted(closes.keys() & opens.keys())
    gaps = [10000 * (opens[k][1] / closes[k][1] - 1) for k in pairs]
    return {"matched_signal_symbol_side": len(pairs), "close_only": len(closes) - len(pairs),
            "open_only": len(opens) - len(pairs), "mean_open_minus_close_bps": fmean(gaps) if gaps else None,
            "median_open_minus_close_bps": median(gaps) if gaps else None}


def hybrid_results(root, plan, market, calendar):
    spec = plan["markets"][market]
    receipts = json.loads((root / "receipts.json").read_bytes())
    bars, coverage = {}, {}
    expected = {day for day in calendar if plan["input_start"] <= day <= plan["end"]}
    for ticker in spec["core"] + spec["satellite"]:
        raw = (root / f"{ticker}.json").read_bytes()
        if digest(raw) != receipts[ticker]["sha256"]:
            raise ValueError(f"Wrong input hash for {ticker}")
        rows, diagnostics = parse_chart(raw, ticker, market, plan["input_start"], plan["end"])
        days = {row["date"] for row in rows}
        if days - expected or plan["end"] not in days:
            raise ValueError(f"Non-session or missing terminal bar for {ticker}")
        bars[ticker] = rows
        coverage[ticker] = {**receipts[ticker], "missing_sessions": sorted(expected - days),
                            "diagnostics": diagnostics}
    original = json.loads((PLAN.parent / "HYBRID_QUANT_BACKTEST_20261125.json").read_bytes())[market]
    observed = sorted({row["date"] for rows in bars.values() for row in rows})
    if (observed[70], len(observed) - 70, observed[-1]) != (spec["first_mark"], spec["sessions"], plan["end"]):
        raise ValueError(f"Reconstructed {market} sample differs from the frozen evaluation dates")
    summary = {"coverage": coverage, "missing_all_symbols": sorted(expected - set(observed)), "executions": {}}
    all_traces = {}
    for timing in ("legacy_close", "same_close", "next_open"):
        traces = {}
        result = simulate_after_tax_walk_forward(
            bars, market=market, core_tickers=spec["core"], satellite_tickers=spec["satellite"],
            benchmark_ticker=spec["benchmark"], fill_timing=timing, audit_traces=traces)
        all_traces[timing] = traces
        if timing == "legacy_close":
            summary["published_vs_retrieved"] = {
                arm: {k: {"published": v, "replayed": result["strategies"][arm][k]}
                      for k, v in old.items() if v != result["strategies"][arm][k]}
                for arm, old in original["strategies"].items()}
        execution = {}
        for arm, trace in traces.items():
            execution[arm] = {"original_metric_convention": result["strategies"][arm],
                              "target_sha256": canonical_hash(trace["signals"]),
                              "missing_quotes": trace["missing_quotes"], "superseded": trace["superseded"],
                              "pending_at_end": trace["pending_at_end"],
                              "periods": {p: period_stats(trace, *window) for p, window in plan["periods"].items()}}
            if trace["signals"] != all_traces["legacy_close"][arm]["signals"]:
                raise ValueError(f"Execution changed the signal grid or weights: {arm}")
        summary["executions"][timing] = execution
    summary["fill_price_comparison"] = {
        arm: compare_fills(closes, all_traces["next_open"][arm])
        for arm, closes in all_traces["same_close"].items()}
    return summary, all_traces


def preserved_results(root, plan):
    curves = json.loads((root / "reference/independent-ledger.json").read_bytes())["curves"]
    hashes = {k: digest((root / k).read_bytes()) for k in (
        "research-plan.json", "long-inputs/market-inputs.json", "reference/independent-ledger.json",
        "reference/weights.json", "reference/study.json", "reference/lean-reconciliation.json")}
    periods = {}
    for name, (start, end) in plan["periods"].items():
        result = compare_market_benchmarks(curves, 100_000_000, start, end)
        periods[name] = {k: result[k] for k in ("start", "end", "sessions", "arms")}
    return {"hashes": hashes, "periods": periods}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_dir", type=Path)
    parser.add_argument("new_output_dir", type=Path)
    parser.add_argument("--verify-published", action="store_true",
                        help="Require the pinned input receipts and every published aggregate to match.")
    args = parser.parse_args()
    plan = json.loads(PLAN.read_bytes())
    calendar = research_sessions(datetime.fromisoformat(plan["end"] + "T23:59:59+00:00"))
    summary = {"plan": plan, "plan_object_sha256": canonical_hash(plan),
               "553": {}, "569": {}, "admitted_prospective_marks": 0}
    out = args.new_output_dir
    out.mkdir(parents=True, exist_ok=False)
    for name in ("original", "corrected"):
        summary["553"][name] = preserved_results(args.input_dir / name, plan)
    for market in plan["markets"]:
        summary["569"][market], traces = hybrid_results(args.input_dir / "yahoo", plan, market, calendar[market])
        (out / f"{market}-traces.json").write_text(json.dumps(traces, sort_keys=True), encoding="utf-8")
    (out / "comparison.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.verify_published:
        published = json.loads((PLAN.parent / "hybrid_execution_audit_results.json").read_bytes())
        if canonical_hash(published) != canonical_hash(summary):
            raise SystemExit("Frozen reproduction differs from the published receipts or metrics")
        print("Verified the pinned inputs and published comparison")


if __name__ == "__main__":
    main()
