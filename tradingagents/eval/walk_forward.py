from __future__ import annotations

import argparse
import json
import math
from copy import deepcopy
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable

import pandas as pd
import yfinance as yf

from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.dataflows.integrity import safe_symbol
from tradingagents.eval.decision_scores import daily_bar_available_at, evaluation_sessions, _price

# Retail cash-account policy: SELL reduces exposure; it is not a short sale.
RATING_TO_EXPOSURE = {"BUY": 1.0, "OVERWEIGHT": 0.5, "HOLD": 0.0,
                      "UNDERWEIGHT": 0.0, "SELL": 0.0, "NO_TRADE": 0.0}


def _fetch_forward_window(symbol: str, trade_date: str, holding_period: int) -> dict | None:
    if holding_period < 1:
        raise ValueError("holding_period must be positive")
    symbol = safe_symbol(symbol)
    market = "KR" if _regional_benchmark(symbol) == "069500.KS" else "US"
    sessions = evaluation_sessions(market, trade_date, holding_period)
    entry, exit_ = sessions[0][0], sessions[-1][0]
    available = daily_bar_available_at(market, exit_, sessions[-1][2])
    if datetime.now(timezone.utc) < available:
        return None
    end = (date.fromisoformat(exit_) + timedelta(days=1)).isoformat()
    history = yf.Ticker(symbol).history(start=entry, end=end, auto_adjust=True)
    first, last = _price(history, entry, "Open"), _price(history, exit_, "Close")
    if first is None or last is None:
        return None
    return {"return": last / first - 1, "entry_date": entry, "exit_date": exit_,
            "entry_price": first, "exit_price": last, "matures_at": available.isoformat()}


def _fetch_forward_return(symbol: str, trade_date: str, holding_period: int) -> float | None:
    window = _fetch_forward_window(symbol, trade_date, holding_period)
    return None if window is None else window["return"]


def _compute_max_drawdown(returns: Iterable[float]) -> float:
    # Include initial capital: a first-period loss is a drawdown, too.
    equity = pd.Series([1.0, *[1.0 + value for value in returns]]).cumprod()
    return float((equity / equity.cummax() - 1).min())


def _regional_benchmark(symbol: str) -> str:
    if symbol.endswith((".KS", ".KQ")) or (symbol.isdigit() and len(symbol) == 6):
        return "069500.KS"
    return "SPY"


def run_walk_forward_evaluation(
    symbols: list[str], trade_dates: list[str], *, holding_period: int = 5,
    benchmark_symbol: str | None = None, graph_config: dict | None = None,
    selected_analysts: list[str] | None = None, enable_reflection: bool = False,
    transaction_cost_bps: float = 10.0,
) -> dict:
    """Cost-aware signal study, not an executable portfolio backtest.

    Each decision enters at the next session open and exits after a complete
    holding window. Overlapping cohorts are never compounded as a portfolio.
    """
    if holding_period < 1 or not math.isfinite(transaction_cost_bps) or transaction_cost_bps < 0:
        raise ValueError("Invalid holding period or transaction cost")
    dates = sorted(set(trade_dates))
    for value in dates:
        date.fromisoformat(value)
    config = deepcopy(graph_config or DEFAULT_CONFIG)
    config.update(point_in_time_strict=True, memory_dir=None, checkpoint_enabled=False)
    graph = TradingAgentsGraph(config=config, selected_analysts=selected_analysts or ["market", "social", "news", "fundamentals"])
    records, excluded, pending = [], [], []
    previous_exposure = {}
    fee = transaction_cost_bps / 10000
    try:
        for trade_date in dates:
            if enable_reflection:
                ready = [item for item in pending if item[0] <= trade_date]
                pending = [item for item in pending if item[0] > trade_date]
                for known, state, outcome in ready:
                    graph.reflect_and_remember(outcome, state=state, outcome_known_at=known)
            for symbol in dict.fromkeys(symbols):
                try:
                    final_state, rating = graph.propagate(symbol, trade_date)
                except Exception as exc:
                    excluded.append({"symbol": symbol, "trade_date": trade_date,
                                     "reason": "decision_failure", "error_type": type(exc).__name__})
                    continue
                canonical = final_state["company_of_interest"]
                if rating not in RATING_TO_EXPOSURE:
                    excluded.append({"symbol": canonical, "trade_date": trade_date, "reason": "decision_unvalidated"})
                    continue
                try:
                    window = _fetch_forward_window(canonical, trade_date, holding_period)
                except Exception as exc:
                    excluded.append({"symbol": canonical, "trade_date": trade_date,
                                     "reason": "asset_provider_failure", "error_type": type(exc).__name__})
                    continue
                if window is None:
                    excluded.append({"symbol": canonical, "trade_date": trade_date, "reason": "incomplete_or_invalid_forward_window"})
                    continue
                benchmark = benchmark_symbol or _regional_benchmark(canonical)
                try:
                    benchmark_window = _fetch_forward_window(benchmark, trade_date, holding_period)
                except Exception:
                    benchmark_window = None
                matched = benchmark_window and all(window[k] == benchmark_window[k] for k in ("entry_date", "exit_date"))
                benchmark_return = benchmark_window["return"] - 2 * fee if matched else None
                exposure = RATING_TO_EXPOSURE.get(rating, 0.0)
                gross = exposure * window["return"]
                cost = 2 * exposure * fee  # independent round-trip episode
                net = gross - cost
                exposure_change = abs(exposure - previous_exposure.get(canonical, 0.0))
                previous_exposure[canonical] = exposure
                country = (final_state.get("instrument_profile") or {}).get("country", "UNKNOWN")
                records.append({"symbol": canonical, "country": country, "trade_date": trade_date,
                    "rating": rating, "exposure": exposure, "asset_return": window["return"],
                    "entry_date": window["entry_date"], "exit_date": window["exit_date"],
                    "gross_strategy_return": gross, "transaction_cost": cost, "strategy_return": net,
                    "benchmark_symbol": benchmark, "benchmark_return": benchmark_return,
                    "excess_return": net - benchmark_return if benchmark_return is not None else None,
                    "turnover": 2 * exposure, "exposure_change": exposure_change})
                if enable_reflection and exposure:
                    pending.append((window["exit_date"], deepcopy(final_state), net))
    finally:
        graph.close()
    assumptions = {"evaluation_type": "long_only_signal_study", "entry": "next_session_open",
        "exit": "holding_window_close", "transaction_cost_bps_per_side": transaction_cost_bps,
        "point_in_time_strict": True, "limitations": [
            "LLM pretraining can contain future knowledge; this is not a leak-free causal backtest.",
            "Historical filings without publication vintages are excluded. Price adjustments and surviving ticker selection may still bias results.",
            "Taxes, FX conversion, gap execution, market impact and cash competition are not simulated.",
            "HOLD is zero new exposure in this signal study, not liquidation of an existing real holding."]}
    if not records:
        return {"records": [], "excluded": excluded, "metrics": {}, "assumptions": assumptions}
    df = pd.DataFrame(records)
    cohorts = df.groupby("trade_date", sort=True).agg(net=("strategy_return", "mean"), entry=("entry_date", "min"), exit=("exit_date", "max"))
    overlap = any(cohorts.iloc[i]["entry"] <= cohorts.iloc[i-1]["exit"] for i in range(1, len(cohorts)))
    comparable = not overlap and df["country"].nunique() == 1
    active = df.loc[df["exposure"] > 0]
    metrics = {
        "sample_count": len(records), "excluded_count": len(excluded), "active_count": len(active),
        "hit_rate": float((active["strategy_return"] > 0).mean()) if len(active) else None,
        "forward_return_by_rating_bucket": df.groupby("rating")["asset_return"].mean().to_dict(),
        "turnover": float(df["turnover"].mean()),
        "max_drawdown": _compute_max_drawdown(cohorts["net"]) if comparable else None,
        "overlapping_cohorts": overlap,
        "benchmark_excess_return": float(df["excess_return"].dropna().mean()) if df["excess_return"].notna().any() else None,
        "abstain_frequency": float((df["exposure"] == 0).mean()),
        "region_split_metrics": df.groupby("country")["strategy_return"].agg(["mean", "count"]).rename(columns={"mean": "avg_strategy_return"}).to_dict(orient="index"),
    }
    return {"records": records, "excluded": excluded, "metrics": metrics, "assumptions": assumptions}

def main():
    parser = argparse.ArgumentParser(description="Run a simple walk-forward evaluation for TradingAgents.")
    parser.add_argument("--symbols", nargs="+", required=True, help="Instrument inputs, such as AAPL or 005930")
    parser.add_argument("--trade-dates", nargs="+", required=True, help="Trade dates in YYYY-MM-DD format")
    parser.add_argument("--holding-period", type=int, default=5, help="Forward holding period in trading days")
    parser.add_argument("--benchmark", default=None, help="Benchmark ticker for excess-return comparison")
    parser.add_argument("--transaction-cost-bps", type=float, default=10, help="Estimated cost per side in basis points")
    parser.add_argument("--enable-reflection", action="store_true", help="Call reflect_and_remember after each evaluated trade")
    parser.add_argument("--output", default=None, help="Optional JSON output path")
    parser.add_argument("--run-id", help="Resume a persisted dual-score backtest without reflection.")
    args = parser.parse_args()

    if args.run_id and args.enable_reflection:
        parser.error("Use the isolated backtest run without reflection when resuming.")
    if args.run_id:
        from tradingagents.backtest import run_backtest, summarize
        run = run_backtest(args.symbols, args.trade_dates, DEFAULT_CONFIG, run_id=args.run_id,
                           holding_period=args.holding_period, benchmark_symbol=args.benchmark,
                           transaction_cost_bps=args.transaction_cost_bps)
        result = summarize(run).data
    else:
        result = run_walk_forward_evaluation(
            symbols=args.symbols, trade_dates=args.trade_dates, holding_period=args.holding_period,
            benchmark_symbol=args.benchmark, enable_reflection=args.enable_reflection,
            transaction_cost_bps=args.transaction_cost_bps,
        )

    rendered = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        from tradingagents.atomic_io import atomic_write_bytes
        atomic_write_bytes(output_path, rendered.encode("utf-8"))
    else:
        print(rendered)


if __name__ == "__main__":
    main()
