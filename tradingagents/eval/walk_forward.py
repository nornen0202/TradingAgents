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
from tradingagents.dataflows.integrity import safe_symbol, session_date

# Retail cash-account policy: SELL reduces exposure; it is not a short sale.
RATING_TO_EXPOSURE = {"BUY": 1.0, "OVERWEIGHT": 0.5, "HOLD": 0.0,
                      "UNDERWEIGHT": 0.0, "SELL": 0.0, "NO_TRADE": 0.0}


def _fetch_forward_window(symbol: str, trade_date: str, holding_period: int) -> dict | None:
    if holding_period < 1:
        raise ValueError("holding_period must be positive")
    symbol = safe_symbol(symbol)
    start = date.fromisoformat(trade_date) + timedelta(days=1)
    end = start + timedelta(days=max(holding_period * 4, 14))
    history = yf.Ticker(symbol).history(start=start.isoformat(), end=end.isoformat(), auto_adjust=True)
    if history.empty or not {"Open", "Close"}.issubset(history.columns):
        return None
    frame = history.copy()
    frame.index = pd.DatetimeIndex([session_date(value) for value in frame.index])
    frame = frame.loc[frame.index.notna() & (frame.index > pd.Timestamp(trade_date))]
    # Never settle an incomplete current-day bar, even if Yahoo already supplies it.
    frame = frame.loc[frame.index < pd.Timestamp(datetime.now(timezone.utc).date())]
    frame = frame.sort_index().loc[lambda x: ~x.index.duplicated(keep="last")]
    if len(frame) < holding_period:
        return None
    window = frame.iloc[:holding_period]
    prices = pd.to_numeric(window["Close"], errors="coerce")
    entry = pd.to_numeric(window["Open"], errors="coerce").iloc[0]
    if not math.isfinite(entry) or entry <= 0 or not all(math.isfinite(v) and v > 0 for v in prices):
        return None
    return {"return": float(prices.iloc[-1]) / entry - 1,
            "entry_date": window.index[0].date().isoformat(),
            "exit_date": window.index[-1].date().isoformat(),
            "entry_price": entry, "exit_price": float(prices.iloc[-1])}


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
                final_state, rating = graph.propagate(symbol, trade_date)
                canonical = final_state["company_of_interest"]
                if rating not in RATING_TO_EXPOSURE:
                    excluded.append({"symbol": canonical, "trade_date": trade_date, "reason": "decision_unvalidated"})
                    continue
                window = _fetch_forward_window(canonical, trade_date, holding_period)
                if window is None:
                    excluded.append({"symbol": canonical, "trade_date": trade_date, "reason": "incomplete_or_invalid_forward_window"})
                    continue
                benchmark = benchmark_symbol or _regional_benchmark(canonical)
                benchmark_window = _fetch_forward_window(benchmark, trade_date, holding_period)
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
    args = parser.parse_args()

    result = run_walk_forward_evaluation(
        symbols=args.symbols,
        trade_dates=args.trade_dates,
        holding_period=args.holding_period,
        benchmark_symbol=args.benchmark,
        enable_reflection=args.enable_reflection,
        transaction_cost_bps=args.transaction_cost_bps,
    )

    rendered = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered, encoding="utf-8")
    else:
        print(rendered)


if __name__ == "__main__":
    main()
