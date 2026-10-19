"""Reproducible cash-policy sensitivity with trusted local raw-price CSVs."""

import argparse
import hashlib
import json
from pathlib import Path
import pandas as pd
from tradingagents.execution.account_cost_replay import CostScenario, simulate_account


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prices", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--analysis-as-of", required=True)
    args = parser.parse_args()
    cutoff = pd.Timestamp(args.analysis_as_of).normalize()
    config = json.loads(
        Path("config/account_cost_replay_20260929.json").read_text(encoding="utf8")
    )
    rows = []
    evidence = {}
    fxdata = pd.read_csv(args.prices / "KRW_X_raw.csv", index_col=0, parse_dates=True)
    fxdata = fxdata.loc[fxdata.index <= cutoff].dropna(subset=["Close"])
    cases = [
        ("fixed_2500000", None, 2500000),
        *[(f"nav_{p}", p / 100, 100000) for p in (5, 10, 15, 20, 25)],
    ]
    periods = [
        ("development", "2020-01-01", "2023-12-31"),
        ("validation", "2024-01-01", "2026-09-18"),
        ("validation_pre2026", "2024-01-01", "2025-12-31"),
        ("drawdown_2022", "2022-01-01", "2022-12-31"),
    ]
    for market, ticker, nav in [("KR", "069500.KS", 9676532), ("US", "SPY", 24752712)]:
        path = args.prices / f"{ticker}_raw.csv"
        prices = pd.read_csv(path, index_col=0, parse_dates=True)
        if prices.index.hasnans or not prices.index.is_unique:
            raise ValueError("Invalid source dates")
        prices = prices.loc[prices.index <= cutoff]
        absent = prices[["Open", "Close"]].isna().all(axis=1)
        excluded = int(absent.sum())
        prices = prices.loc[~absent]
        c = config["markets"][market]
        evidence[market] = {
            "ticker": ticker,
            "rows": len(prices),
            "joint_calendar_absent_rows": excluded,
            "large_moves_over_15pct": {
                str(d.date()): float(v)
                for d, v in prices.Close.pct_change().items()
                if abs(v) > 0.15
            },
            "start": str(prices.index.min().date()),
            "end": str(prices.index.max().date()),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "initial_krw": nav,
        }
        fx = (
            fxdata.Close
            if market == "US"
            else pd.Series(1.0, index=pd.date_range("2018-01-01", cutoff))
        )
        for period, start, end in periods:
            end = min(end, str(cutoff.date()))
            for slip in (0.0005, 0.0015):
                for delay in (0, 1):
                    for name, ratio, fixed in cases:
                        for rounding in ("legacy_delta_floor", "target_floor"):
                            scenario = CostScenario(
                                commission_rate=c["commission_rate"],
                                sell_levy_rate=c["sell_levy_rate"],
                                fx_base_spread=c["fx_base_spread"],
                                fx_discount=c["fx_discount"],
                                slippage_rate=slip,
                                dividend_withholding=c["dividend_withholding"],
                                capital_gains_rate=c["capital_gains_rate"],
                                annual_allowance_krw=0,
                            )
                            metrics, curve, trades = simulate_account(
                                prices,
                                "balanced_80_20",
                                start=start,
                                end=end,
                                initial_krw=nav,
                                scenario=scenario,
                                fx_krw_per_unit=fx,
                                price_basis="unadjusted_no_splits",
                                execution_delay_sessions=delay,
                                cash_reserve_ratio=ratio,
                                fixed_cash_reserve_krw=fixed,
                                sell_rounding=rounding,
                            )
                            years = (
                                pd.Timestamp(metrics["end"])
                                - pd.Timestamp(metrics["start"])
                            ).days / 365.25
                            cagr = (
                                (metrics["final_krw"] / nav) ** (1 / years) - 1
                            ) * 100
                            rows.append(
                                {
                                    "market": market,
                                    "period": period,
                                    "policy": name,
                                    "rounding": rounding,
                                    "slippage": slip,
                                    "delay": delay,
                                    "cagr_pct": cagr,
                                    "max_drawdown_pct": metrics["max_drawdown_pct"],
                                    "return_pct": metrics["total_return_pct"],
                                    "cost_krw": metrics["trading_cost_krw"]
                                    + metrics["slippage_cost_krw"]
                                    + metrics["entry_fx_cost_krw"]
                                    + metrics["exit_fx_cost_krw"],
                                    "trades": metrics["trades"],
                                    "tax_krw": metrics["tax_reserve_krw"],
                                }
                            )
    args.output.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(args.output / "cash_policy_results.csv", index=False)
    (args.output / "cash_policy_evidence.json").write_text(
        json.dumps(
            {
                "analysis_as_of": args.analysis_as_of,
                "inputs": evidence,
                "fx_sha256": hashlib.sha256(
                    (args.prices / "KRW_X_raw.csv").read_bytes()
                ).hexdigest(),
                "experiments": len(rows),
                "limitations": [
                    "Account-sized single-ETF proxy, not reconstruction of current holdings or archived LLM signals",
                    "Retrospective comparison; validation period was not untouched prospective evidence",
                    "Current fee/tax scenarios replayed over history; annual allowance assumed exhausted",
                    "No dividend pay dates: receivables never reused; cash earns zero; USD cash carries FX exposure",
                    "Quarterly review with five percentage point band; trading at next open; delays 0/1 sessions",
                    "KR historical source not independently verified; no optimality claim",
                ],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf8",
    )
    print(
        pd.DataFrame(rows)
        .groupby(["market", "period", "policy"])[
            ["cagr_pct", "max_drawdown_pct", "trades"]
        ]
        .mean()
        .round(3)
        .to_string()
    )


if __name__ == "__main__":
    main()
