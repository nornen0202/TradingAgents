"""Compare fixed research strategies using an explicitly trusted local cache.

No API calls or account access. Pickle input must be a trusted local file;
untrusted pickle files can execute code and must not be supplied.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
from pathlib import Path

import numpy as np
import pandas as pd

from tradingagents.execution.account_strategy_research import (
    SPECIFICATION,
    STRATEGIES,
    open_signals,
    pareto_strategies,
    price_hash,
    simulate,
    specification_hash,
)


def extract_market_prices(cache: pd.DataFrame, ticker: str):
    """Drop joint calendar non-observations, never fill unavailable quotes."""
    prices = pd.DataFrame(
        {"Open": cache[("Open", ticker)], "Close": cache[("Close", ticker)]}
    )
    partial = prices.isna().any(axis=1) & ~prices.isna().all(axis=1)
    if partial.any():
        raise ValueError(f"{ticker}: partial price observations")
    absent_dates = prices.index[prices.isna().all(axis=1)]
    prices = prices.dropna()
    returns = prices.Close.pct_change(fill_method=None).dropna()
    review_moves = returns[returns.abs() > 0.15]
    return prices, {
        "joint_calendar_rows_without_any_quote": len(absent_dates),
        "observation_start": prices.index.min().date().isoformat(),
        "observation_end": prices.index.max().date().isoformat(),
        "sessions": len(prices),
        "price_sha256": price_hash(prices),
        "max_absolute_daily_close_return_pct": float(returns.abs().max() * 100)
        if not returns.empty
        else None,
        "large_move_review_threshold_pct": 15.0,
        "large_moves_requiring_source_review": [
            {"date": date.date().isoformat(), "return_pct": float(value * 100)}
            for date, value in review_moves.items()
        ],
        "independent_source_verified": False,
        "calendar_limitation": "absent joint-calendar rows excluded; holidays versus missing sessions not independently verified",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trusted-price-cache", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--include-curves", action="store_true")
    args = parser.parse_args(argv)
    cache = pd.read_pickle(args.trusted_price_cache)
    if not isinstance(cache, pd.DataFrame):
        raise ValueError("Trusted cache must contain a DataFrame")
    args.output.mkdir(parents=True, exist_ok=True)
    periods = [
        ("2020_2023", "2020-01-01", "2023-12-31"),
        ("2024_2026", "2024-01-01", "2026-09-18"),
        *[
            (str(year), f"{year}-01-01", min(f"{year}-12-31", "2026-09-18"))
            for year in range(2020, 2027)
        ],
    ]
    inputs, results, frontiers, details = {}, [], [], {}
    for ticker in ("SPY", "069500.KS"):
        prices, input_metadata = extract_market_prices(cache, ticker)
        inputs[ticker] = input_metadata
        prices.to_csv(
            args.output / f"research_prices_{ticker}.csv", float_format="%.17g"
        )
        signals = {strategy: open_signals(prices, strategy) for strategy in STRATEGIES}
        for period_id, start, end in periods:
            for cost_bps in (10, 30, 100):
                for delay in (0, 1):
                    scenario = []
                    for strategy in STRATEGIES:
                        metrics, curve, orders = simulate(
                            prices,
                            strategy,
                            start=start,
                            end=end,
                            cost_bps=cost_bps,
                            execution_delay_sessions=delay,
                            signals=signals[strategy],
                        )
                        key = f"{ticker}/{period_id}/{cost_bps}bps/delay{delay}/{strategy}"
                        config = {
                            "specification_sha256": specification_hash(),
                            "price_sha256": input_metadata["price_sha256"],
                            "ticker": ticker,
                            "period_id": period_id,
                            "requested_start": start,
                            "requested_end": end,
                            "cost_bps_per_side": cost_bps,
                            "execution_delay_sessions": delay,
                            "strategy": strategy,
                            "initial_nav": 100000.0,
                        }
                        metrics.update(
                            {
                                "id": key,
                                "ticker": ticker,
                                "period_id": period_id,
                                "config_sha256": hashlib.sha256(
                                    json.dumps(config, sort_keys=True).encode()
                                ).hexdigest(),
                            }
                        )
                        results.append(metrics)
                        scenario.append(metrics)
                        if args.include_curves:
                            details[key] = {
                                "config": config,
                                "curve": curve,
                                "trades": orders,
                            }
                    frontiers.append(
                        {
                            "ticker": ticker,
                            "period_id": period_id,
                            "cost_bps_per_side": cost_bps,
                            "execution_delay_sessions": delay,
                            "objectives": [
                                "maximize_total_return",
                                "minimize_maximum_drawdown_magnitude",
                            ],
                            "strategies": pareto_strategies(scenario),
                        }
                    )
    payload = {
        "specification": SPECIFICATION,
        "specification_sha256": specification_hash(),
        "source_cache_sha256": hashlib.sha256(
            args.trusted_price_cache.read_bytes()
        ).hexdigest(),
        "runtime": {
            "python": platform.python_version(),
            "pandas": pd.__version__,
            "numpy": np.__version__,
        },
        "inputs": inputs,
        "scenario_count": len(frontiers),
        "strategy_run_count": len(results),
        "periods": [
            {"id": pid, "start": start, "end": end} for pid, start, end in periods
        ],
        "cost_bps_per_side": [10, 30, 100],
        "additional_execution_delays": [0, 1],
        "limitations": [
            "Retrospective fixed-rule sensitivity analysis; not a locked out-of-sample test.",
            "Each period starts from all cash with normalized 100000 capital; existing holdings are not replayed.",
            "Cash yields zero. Tax, FX, settlement, bid-ask microstructure and initial portfolio conversion are not modeled.",
            "Adjusted fractional units approximate total-return exposure; they are not executable integer shares.",
            "No terminal liquidation, so open gains and exit costs remain unrealized.",
            "Quotes use the current adjusted-history vintage; point-in-time adjustment revisions are not reconstructed.",
            "Past-session availability is assumed from observed per-market dates; independent exchange-calendar validation remains outstanding.",
            "No global winner selected; Pareto frontiers use return and drawdown only within matched scenarios.",
        ],
        "results": results,
        "pareto_frontiers": frontiers,
    }
    output_path = args.output / "fixed_strategy_review.json"
    output_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False),
        encoding="utf-8",
    )
    if args.include_curves:
        (args.output / "fixed_strategy_curves.json").write_text(
            json.dumps(
                details, ensure_ascii=False, separators=(",", ":"), allow_nan=False
            ),
            encoding="utf-8",
        )
    print(
        f"Completed {len(results)} strategy runs / {len(frontiers)} matched scenarios"
    )
    print(
        "Retrospective research only; fractional adjusted units; cash yield 0; no tax/FX/conversion costs"
    )
    for ticker, info in inputs.items():
        if info["large_moves_requiring_source_review"]:
            print(
                f"SOURCE REVIEW REQUIRED: {ticker} has {len(info['large_moves_requiring_source_review'])} daily moves above 15%; not independently verified"
            )
    print(
        "ticker      period      strategy          return%     MDD%    underwater_days  legs"
    )
    for row in results:
        if (
            row["period_id"] in {"2020_2023", "2024_2026"}
            and row["cost_bps_per_side"] == 10
            and row["execution_delay_sessions"] == 0
        ):
            print(
                f"{row['ticker']:<11} {row['period_id']:<11} {row['strategy']:<17} {row['total_return_pct']:>8.2f} {row['max_drawdown_pct']:>8.2f} {row['max_underwater_calendar_days']:>18} {row['order_legs']:>5}"
            )
    print(f"JSON: {output_path}")
    return payload


if __name__ == "__main__":
    main()
