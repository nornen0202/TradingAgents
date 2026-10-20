"""Offline current-weight historical analogues and stress checks, not a signal backtest."""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd


def price_series(path, cutoff):
    frame = pd.read_csv(path, index_col=0, parse_dates=True)
    if (
        not isinstance(frame.index, pd.DatetimeIndex)
        or frame.index.hasnans
        or not frame.index.is_unique
    ):
        raise ValueError(f"Unverified dates: {path.name}")
    frame = frame.loc[frame.index <= cutoff].sort_index()
    series = frame["Close"]
    if series.empty or not np.isfinite(series).all() or (series <= 0).any():
        raise ValueError(f"Invalid close: {path.name}")
    return series


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, required=True)
    ap.add_argument("--plan", type=Path, required=True)
    ap.add_argument("--prices", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--analysis-as-of", required=True)
    args = ap.parse_args()
    cutoff = pd.Timestamp(args.analysis_as_of).normalize()
    inputs = json.loads(args.input.read_text(encoding="utf8"))
    plans = json.loads(args.plan.read_text(encoding="utf8"))
    summaries, stresses, evidence = [], [], {}
    fx_series = price_series(args.prices / "KRW_X.csv", cutoff)
    for market, proposal in plans.items():
        if proposal["status"] != "CONDITIONAL_FUNDED":
            continue
        payload = inputs["markets"][market]
        rows = {r["ticker"]: r for r in payload["rows"]}
        ledger = proposal["cash_ledger"]
        nav = ledger["nav_krw"]
        fx_now = payload["trade_plan"]["fx_krw_per_usd"] if market == "us" else 1
        baseline = {}
        for ticker, row in rows.items():
            if not row.get("is_held"):
                continue
            metrics = row["portfolio_action"].get("position_metrics") or {}
            value = metrics.get("market_value_krw")
            if value is None or value < 0:
                raise ValueError("Missing holding value " + ticker)
            baseline[ticker] = float(value)
        residual = nav - ledger["initial_cash_krw"] - sum(baseline.values())
        if abs(residual) > nav * 0.005:
            raise ValueError("Unclassified NAV residual exceeds 0.5% tolerance")
        sell_only = baseline.copy()
        for leg in proposal["sell_legs"]:
            # Account amount is authoritative, avoiding quote/snapshot rounding drift.
            sell_only[leg["ticker"]] -= (
                baseline[leg["ticker"]] * leg["quantity"] / leg["holding_quantity"]
            )
        rotation = sell_only.copy()
        for leg in proposal["buy_legs"]:
            rotation[leg["ticker"]] = rotation.get(leg["ticker"], 0) + leg["gross_krw"]
        all_tickers = sorted(rotation)
        prices = pd.concat(
            {t: price_series(args.prices / (t + ".csv"), cutoff) for t in all_tickers},
            axis=1,
        ).dropna()
        if prices.empty:
            raise ValueError("No shared history")
        evidence[market] = {
            "source_run": payload["run_id"],
            "nav_krw": nav,
            "unclassified_nav_residual_krw": residual,
            "residual_treatment": "Held constant for analogue only; excluded from funding",
            "current_fx": fx_now,
            "input_hashes": {
                t: hashlib.sha256((args.prices / (t + ".csv")).read_bytes()).hexdigest()
                for t in all_tickers
            },
            "shared_start": str(prices.index.min().date()),
            "shared_end": str(prices.index.max().date()),
            "large_adjusted_daily_moves": {
                t: {
                    str(d.date()): float(v)
                    for d, v in prices[t].pct_change().items()
                    if abs(v) > 0.30
                }
                for t in all_tickers
            },
        }
        gross_proceeds = (
            ledger["net_sale_funding_krw"] + ledger["capital_tax_reserve_krw"]
        )
        policies = [
            ("hold", baseline, 0, 0),
            ("sell_only", sell_only, gross_proceeds, ledger["capital_tax_reserve_krw"]),
            (
                "funded_rotation",
                rotation,
                gross_proceeds - ledger["buy_total_krw"],
                ledger["capital_tax_reserve_krw"],
            ),
        ]
        for period, start, end in (
            ("2024_2025", "2024-01-01", "2025-12-31"),
            ("2025", "2025-01-01", "2025-12-31"),
            ("2026_sensitivity", "2026-01-01", str(cutoff.date())),
        ):
            segment = prices.loc[start:end]
            if len(segment) < 40:
                continue
            quality_issue = bool((segment.pct_change().abs() > 0.30).any().any())
            native = segment / segment.iloc[0]
            fx_path = (
                fx_series.reindex(fx_series.index.union(segment.index))
                .sort_index()
                .ffill(limit=5)
                .reindex(segment.index)
            )
            if market == "us" and fx_path.isna().any():
                raise ValueError("FX gap")
            fx_growth = (
                fx_path / fx_path.iloc[0]
                if market == "us"
                else pd.Series(1.0, index=segment.index)
            )
            growth = native.mul(fx_growth, axis=0)
            for name, assets, proceeds_cash, tax in policies:
                values = growth.mul(
                    pd.Series(assets).reindex(all_tickers).fillna(0), axis=1
                ).sum(axis=1)
                values += (
                    ledger["initial_cash_krw"] + residual + proceeds_cash * fx_growth
                )
                duration = (segment.index[-1] - segment.index[0]).days / 365.25
                peak = values.cummax().clip(lower=nav)
                summaries.append(
                    {
                        "market": market,
                        "period": period,
                        "policy": name,
                        "start": str(segment.index[0].date()),
                        "end": str(segment.index[-1].date()),
                        "observations": len(segment),
                        "quality_status": "UNVERIFIED_PRICE_JUMP"
                        if quality_issue
                        else "NO_LARGE_JUMP_DETECTED",
                        "usable_as_selection_evidence": not quality_issue
                        and period != "2026_sensitivity",
                        "total_return_pct": (values.iloc[-1] / nav - 1) * 100,
                        "cagr_pct": ((values.iloc[-1] / nav) ** (1 / duration) - 1)
                        * 100,
                        "max_drawdown_pct": (values / peak - 1).min() * 100,
                        "initial_implementation_loss_krw": nav - values.iloc[0],
                        "tax_upper_reserve_krw": tax,
                        "terminal_return_if_upper_tax_paid_pct": (
                            (values.iloc[-1] - tax * fx_growth.iloc[-1]) / nav - 1
                        )
                        * 100,
                    }
                )
        # Uniform asset-price shocks include bond/gold ETF prices. They are not
        # predictions of equity beta, nor estimates of scenario probabilities.
        defensive = {"033780.KS", "PG", "ABBV", "SGOV", "GLDM"}
        for scenario, broad, safe, fx_shock in (
            ("all_equity_minus20", -0.20, -0.20, 0),
            ("all_equity_plus20", 0.20, 0.20, 0),
            ("growth_minus30_defensive_minus10", -0.30, -0.10, 0),
            ("growth_plus30_defensive_plus10", 0.30, 0.10, 0),
            ("usd_minus10", 0, 0, -0.10),
            ("usd_plus10", 0, 0, 0.10),
        ):
            for name, assets, proceeds_cash, tax in policies:
                growth_fx = 1 + fx_shock if market == "us" else 1
                equity = sum(
                    v * (1 + (safe if t in defensive else broad))
                    for t, v in assets.items()
                )
                value = (
                    (equity + proceeds_cash) * growth_fx
                    + ledger["initial_cash_krw"]
                    + residual
                )
                stresses.append(
                    {
                        "market": market,
                        "scenario": scenario,
                        "policy": name,
                        "return_pct": (value / nav - 1) * 100,
                        "pnl_krw": value - nav,
                        "pnl_if_upper_tax_paid_krw": value - nav - tax * growth_fx,
                    }
                )
    args.output.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(summaries).to_csv(
        args.output / "historical_analogues.csv", index=False
    )
    pd.DataFrame(stresses).to_csv(args.output / "stress_results.csv", index=False)
    (args.output / "evidence.json").write_text(
        json.dumps(
            {
                "analysis_as_of": args.analysis_as_of,
                "source": "Yahoo Finance adjusted Close, downloaded with yfinance; local date/finite checks",
                "fx_sha256": hashlib.sha256(
                    (args.prices / "KRW_X.csv").read_bytes()
                ).hexdigest(),
                "markets": evidence,
                "limits": [
                    "Current holdings and current selection mapped to past return paths; not historical signal backtest.",
                    "Survivorship/selection bias; adjusted historical prices not point-in-time revision safe.",
                    "Current integer trade sizes and source entry/exit limits assumed filled together; no historical fill probability.",
                    "Historical analogues include adjusted dividend reinvestment; no new annual tax optimization.",
                    "Capital tax upper reserve remains idle cash in main wealth curve; paid-upper scenario reported separately.",
                    "Periods overlap and are not independent trials; 2026 is sensitivity only, not policy-selection evidence.",
                ],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf8",
    )
    print(pd.DataFrame(summaries).to_string(index=False))


if __name__ == "__main__":
    main()
