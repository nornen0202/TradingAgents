"""Run fixed baseline hypotheses on cached, adjusted ETF prices."""

import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd

from tradingagents.execution.research_backtest import simulate, targets


def run(prices: Path, output: Path):
    raw = pd.read_pickle(prices)  # Only a locally produced trusted research cache.
    results, curves = [], {}
    cases = [
        ("US_SPY_HOLD", ["SPY"], "buy_hold", "once"),
        ("US_SPY_TREND200", ["SPY"], "trend_200", "monthly"),
        (
            "US_DIVERSIFIED_MOM126",
            ["SPY", "IEF", "GLD"],
            "momentum_126_top2",
            "monthly",
        ),
        ("KR_KOSPI200_HOLD", ["069500.KS"], "buy_hold", "once"),
        ("KR_KOSPI200_TREND200", ["069500.KS"], "trend_200", "monthly"),
        ("KR_MOM126", ["069500.KS", "229200.KS"], "momentum_126_top2", "monthly"),
    ]
    for name, symbols, strategy, freq in cases:
        close = raw["Close"][symbols].dropna()
        open_ = raw["Open"][symbols].reindex(close.index)
        weights = targets(close, strategy)
        for period, start, end in [
            ("development", "2020-01-01", "2023-12-31"),
            ("evaluation", "2024-01-01", "2026-09-18"),
        ]:
            for cost in [10, 30]:
                metrics, curve, trades = simulate(
                    open_,
                    close,
                    weights,
                    start=start,
                    end=end,
                    cost_bps=cost,
                    rebalance=freq,
                )
                key = f"{name}_{period}_{cost}"
                results.append({"strategy": name, "period": period, **metrics})
                curves[key] = {"curve": curve, "trades": trades}
    output.mkdir(parents=True, exist_ok=True)
    (output / "candidate_backtests.json").write_text(
        json.dumps(
            {
                "price_sha256": hashlib.sha256(prices.read_bytes()).hexdigest(),
                "provider": "Yahoo Finance via yfinance; auto_adjust=True",
                "notes": [
                    "Retrospective evaluation, not genuinely untouched out-of-sample",
                    "Fractional adjusted total-return units; zero cash yield; no tax/FX/account cashflows",
                    "Fixed hypotheses; no parameter optimization; costs are assumptions",
                    "Signal at prior completed close, trade at next session open; monthly rebalance",
                    "No terminal liquidation; mark to last close",
                ],
                "results": results,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (output / "candidate_curves.json").write_text(json.dumps(curves), encoding="utf-8")
    print(
        pd.DataFrame(results)
        .query("period == 'evaluation'")[
            [
                "strategy",
                "cost_bps_per_side",
                "total_return_pct",
                "cagr_pct",
                "max_drawdown_pct",
                "sharpe_rf_zero",
                "order_legs",
            ]
        ]
        .to_string(index=False)
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prices", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    run(args.prices, args.output)
