"""Validate fixed research hypotheses without fitting or selecting new parameters."""

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd

from tradingagents.execution.research_backtest import targets, simulate
from tradingagents.execution.research_validation import (
    prefix_invariance,
    warmup_invariance,
)

CASES = [
    ("US_SPY_HOLD", ["SPY"], "buy_hold", "once"),
    ("US_SPY_TREND200", ["SPY"], "trend_200", "monthly"),
    ("US_DIVERSIFIED_MOM126", ["SPY", "IEF", "GLD"], "momentum_126_top2", "monthly"),
    ("KR_KOSPI200_HOLD", ["069500.KS"], "buy_hold", "once"),
    ("KR_KOSPI200_TREND200", ["069500.KS"], "trend_200", "monthly"),
    ("KR_MOM126", ["069500.KS", "229200.KS"], "momentum_126_top2", "monthly"),
]


def run(prices: Path, output: Path):
    raw = pd.read_pickle(
        prices
    )  # Locally created trusted cache only, never downloaded pickle.
    rows, temporal = [], []
    for name, symbols, strategy, frequency in CASES:
        close = raw["Close"][symbols].dropna()
        opening = raw["Open"][symbols].reindex(close.index)
        target_function = lambda data: targets(data, strategy)  # noqa: E731
        temporal.append(
            {
                "strategy": name,
                "prefix": prefix_invariance(close, target_function),
                "warmup": warmup_invariance(close, target_function),
            }
        )
        weights = target_function(close)
        for year in (2024, 2025, 2026):
            end = min(pd.Timestamp(f"{year}-12-31"), close.index[-1]).date().isoformat()
            if end < f"{year}-01-01":
                continue
            for cost in (10, 30, 100):
                metrics, _, _ = simulate(
                    opening,
                    close,
                    weights,
                    start=f"{year}-01-01",
                    end=end,
                    cost_bps=cost,
                    rebalance=frequency,
                )
                rows.append({"strategy": name, "year": year, **metrics})
    result = {
        "price_sha256": hashlib.sha256(prices.read_bytes()).hexdigest(),
        "temporal_checks": temporal,
        "annual_stress": rows,
        "limitations": [
            "Retrospective fixed hypotheses, not untouched forward evidence or a parameter search",
            "Each year independently starts in cash; annual results must not be compounded as a continuous strategy",
            "Adjusted fractional total-return units, not account-level executable shares; no cash interest, subscription fees, tax or FX",
            "Prefix/warmup checks do not establish point-in-time data availability or eliminate survivorship bias",
        ],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "strategies": len(temporal),
                "prefix_checks_passed": sum(x["prefix"]["passed"] for x in temporal),
                "annual_scenarios": len(rows),
            }
        )
    )
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prices", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    run(args.prices, args.output)
