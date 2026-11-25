"""Offline #570 entry/exposure ablation on receipt-bound inputs; publish aggregates only."""
from __future__ import annotations

import argparse
from bisect import bisect_right
from collections import Counter
from datetime import datetime
import json
import math
from pathlib import Path
from statistics import fmean, stdev

from tools.compare_hybrid_execution import canonical_hash, period_stats, read_market_panel
from tools.hybrid_audit_inputs import PLAN
from tools.hybrid_entry_evidence import NO_OBSERVATION, cohort_coverage, load_observations
from tools.run_hybrid_quant_backtest import simulate_after_tax_walk_forward
from tradingagents.execution.research_study import research_sessions
from tradingagents.execution.quant_policy import _targets


class EntryStudy:
    def __init__(self, bars, spec, observations):
        self.core = spec["core"]
        self.observations = observations
        self.history = {}
        self.mark_history = {}
        for ticker in spec["satellite"]:
            rows = [r for r in bars[ticker] if r["executable_volume"] > 0]
            self.history[ticker] = ([r["date"] for r in rows], [r["close"] for r in rows])
            self.mark_history[ticker] = ([r["date"] for r in bars[ticker]], [r["close"] for r in bars[ticker]])

    def targets(self, day, original, *, sizing_policy=None):
        ranks = []
        for ticker, (days, closes) in self.history.items():
            end = bisect_right(days, day)
            if end < 60 or days[end - 1] != day:
                continue
            current = closes[end - 1]
            momentum = current / closes[end - 41] - 1
            if current > max(closes[end - 21:end - 1]) and current > fmean(closes[end - 60:end]) and momentum > 0:
                ranks.append((-momentum, ticker))
        targets = {t: original[t] for t in self.core if t in original}
        if sizing_policy is None:
            targets.update({ticker: .10 for _, ticker in sorted(ranks)[:3]})
        else:
            admitted = {}
            for negative_score, ticker in ranks:
                dates, prices = self.mark_history[ticker]
                end = bisect_right(dates, day)
                recent = prices[end - sizing_policy["volatility_window"] - 1:end]
                vol = stdev(b / a - 1 for a, b in zip(recent, recent[1:])) * math.sqrt(252)
                admitted[ticker] = (-negative_score, vol, True)
            targets.update(_targets(admitted, budget=sizing_policy["budget_satellite"], cap=sizing_policy["asset_cap"],
                                    volatility_target=sizing_policy["annual_volatility_target"],
                                    limit=sizing_policy["satellite_limit"]))
        return targets

    def risk_at(self, day, ticker):
        return self.observations.get(day, {}).get(ticker, {}).get("action", NO_OBSERVATION)


def period_diagnostics(trace, window, marks, benchmark):
    first, last = window
    result = period_stats(trace, first, last)
    previous_nav = trace["initial_nav"]
    previous_weights = {"cash": 1.0, "etfs": 0.0, "stocks": 0.0}
    totals = dict.fromkeys(previous_weights, 0.0)
    weighted = totals.copy()
    elapsed = turnover = notional = cost_paid = 0.0
    idle = longest = streak = 0
    growth = benchmark_growth = 1.0
    effects = {"cash": 0.0, "positions_and_timing": 0.0, "costs": 0.0}
    opportunities = [r for r in trace["opportunities"] if first <= r[1] <= last]
    actions = Counter(r[3] for r in opportunities)
    observed = len(opportunities) - actions[NO_OBSERVATION]
    hard_vetoes = actions["STOP_LOSS"] + actions["EXIT"]
    for day, nav, account in zip(trace["days"], trace["nav"], trace["account_marks"], strict=True):
        weights = {key: account[key] / nav for key in totals}
        if first <= day <= last:
            seconds = marks[day]
            for key in weights:
                totals[key] += weights[key]
                weighted[key] += previous_weights[key] * seconds
            elapsed += seconds
            all_cash = abs(1 - weights["cash"]) < 1e-10
            idle += int(all_cash)
            streak = streak + 1 if all_cash else 0
            longest = max(streak, longest)
            turnover += account["turnover"]
            notional += account["notional"]
            cost_paid += account["cost"]
            b = benchmark[day]
            net = nav / previous_nav - 1
            cash = -previous_weights["cash"] * b
            costs = -account["cost"] / previous_nav
            daily = {"cash": cash, "costs": costs, "positions_and_timing": net - b - cash - costs}
            # P_t - B_t = (P_prev - B_prev) * (1+b) + P_prev * (r-b).
            for key in effects:
                effects[key] = effects[key] * (1 + b) + growth * daily[key]
            growth *= 1 + net
            benchmark_growth *= 1 + b
        previous_nav, previous_weights = nav, weights
    return {**result, "mean_close_weight": {k: v / result["marks"] for k, v in totals.items()},
            "elapsed_time_weight": {k: v / elapsed for k, v in weighted.items()},
            "idle_sessions": idle, "longest_idle_sessions": longest, "turnover": turnover,
            "traded_notional": notional, "fees_and_tax": cost_paid,
            "buy_opportunities": len(opportunities), "observed": observed,
            "new_positions": sum(r[5] == "new" for r in opportunities),
            "adds": sum(r[5] == "add" for r in opportunities),
            "observed_new_positions": sum(r[5] == "new" and r[3] != NO_OBSERVATION for r in opportunities),
            "observed_adds": sum(r[5] == "add" and r[3] != NO_OBSERVATION for r in opportunities),
            "observed_hard_vetoes": hard_vetoes, "observed_hard_veto_rate": hard_vetoes / observed if observed else None,
            "risk_actions": dict(actions), "blocked": sum(r[4] for r in opportunities),
            "benchmark_return": benchmark_growth - 1, "linked_return_contributions": effects}


def mark_intervals(bars, benchmark_symbol, sessions):
    days = sorted({r["date"] for rows in bars.values() for r in rows})
    quotes = {r["date"]: r["close"] for r in bars[benchmark_symbol]}
    seconds, returns = {}, {}
    previous_day = previous_close = None
    for day in days:
        close = quotes.get(day, previous_close)
        if previous_day is not None and previous_close is not None:
            seconds[day] = (sessions[day][1] - sessions[previous_day][1]).total_seconds()
            returns[day] = close / previous_close - 1
        previous_day, previous_close = day, close
    return days, seconds, returns


def compare_market(root, archive, market, plan, frozen, sessions):
    spec = plan["markets"][market]
    bars, coverage, _ = read_market_panel(root / "yahoo", plan, market, sessions)
    if coverage != frozen["coverage"]:
        raise ValueError(f"{market} input differs from the #570 receipt")
    all_days, seconds, returns = mark_intervals(bars, spec["benchmark"], sessions)
    signal_days = set(all_days[70::21])
    observations, evidence = load_observations(root / "archive-553", archive, market, bars, signal_days)
    traces = {}
    simulate_after_tax_walk_forward(
        bars, market=market, core_tickers=spec["core"], satellite_tickers=spec["satellite"],
        benchmark_ticker=spec["benchmark"], fill_timing="next_open", audit_traces=traces,
        entry_study=EntryStudy(bars, spec, observations))
    for arm in ("quant_breakout", "quant_breakout_matched"):
        if traces[arm]["signals"] != traces[arm + "_veto"]["signals"]:
            raise ValueError("Veto changed the quantitative targets")
    summaries = {}
    for arm, trace in traces.items():
        windows = {w: period_diagnostics(trace, dates, seconds, returns) for w, dates in plan["periods"].items()}
        if arm in frozen["executions"]["next_open"]:
            old = frozen["executions"]["next_open"][arm]
            if canonical_hash(trace["signals"]) != old["target_sha256"] or any(
                    {k: windows[w][k] for k in metrics} != metrics for w, metrics in old["periods"].items()):
                raise ValueError(f"{market}/{arm} differs from frozen #570")
        summaries[arm] = {"target_sha256": canonical_hash(trace["signals"]), "periods": windows}
    return {"arms": summaries, "evidence_counts": evidence, "evidence_sha256": canonical_hash(observations),
            "merge_clock_candidate_archive": cohort_coverage(archive, market, bars),
            "signal_dates": len(signal_days)}, {"observations": observations, "traces": traces}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("frozen_inputs", type=Path)
    parser.add_argument("archive", type=Path, help="read-only historical run manifests")
    parser.add_argument("new_output", type=Path)
    parser.add_argument("--verify-published", action="store_true")
    args = parser.parse_args()
    plan = json.loads(PLAN.read_bytes())
    frozen = json.loads((PLAN.parent / "hybrid_execution_audit_results.json").read_bytes())
    schedules = research_sessions(datetime.fromisoformat(plan["end"] + "T23:59:59+00:00"))
    summary = {"plan_sha256": canonical_hash(json.loads((PLAN.parent / "hybrid_entry_ablation_plan.json").read_bytes())),
               "sizing_control_sha256": canonical_hash(json.loads((PLAN.parent / "hybrid_entry_sizing_control.json").read_bytes())),
               "baseline_result_sha256": canonical_hash(frozen), "admitted_forward_marks": 0, "markets": {}}
    args.new_output.mkdir(parents=True, exist_ok=False)
    for market in plan["markets"]:
        summary["markets"][market], detail = compare_market(
            args.frozen_inputs, args.archive, market, plan, frozen["569"][market], schedules[market])
        (args.new_output / f"private-{market}.json").write_text(json.dumps(detail, sort_keys=True), encoding="utf-8")
    (args.new_output / "summary.json").write_text(json.dumps(summary, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    if args.verify_published:
        published = json.loads((PLAN.parent / "hybrid_entry_ablation_results.json").read_bytes())
        if summary != published:
            raise SystemExit("Entry comparison differs from the published evidence or metrics")


if __name__ == "__main__":
    main()
