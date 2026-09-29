"""Offline current-cost replay. Private account-sized outputs must stay local.

Input: raw Yahoo-format CSV per ticker (Open, Close, Adj Close, Dividends,
Stock Splits), KRW_X_raw.csv for USD/KRW, and a saved account-review.json.
No broker access or execution. Current fees are not historical realized fees.
"""

from __future__ import annotations

import argparse
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import platform

import pandas as pd

from tradingagents.execution.account_cost_replay import (
    CostScenario,
    round_trip_loss,
    simulate_account,
)
from tradingagents.execution.account_strategy_research import STRATEGIES


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--price-dir", type=Path, required=True)
    parser.add_argument("--account-review", type=Path, required=True)
    parser.add_argument(
        "--cost-config",
        type=Path,
        default=Path("config/account_cost_replay_20260929.json"),
    )
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    cfg, account = read_json(args.cost_config), read_json(args.account_review)
    args.output.mkdir(parents=True, exist_ok=True)
    inputs = {
        "cost_config": sha(args.cost_config),
        "account_review": sha(args.account_review),
    }
    results, curves, quality, blocked = [], {}, {}, []
    fx_file = args.price_dir / "KRW_X_raw.csv"
    fx = pd.read_csv(fx_file, index_col=0, parse_dates=True).Close
    inputs[fx_file.name] = sha(fx_file)
    for market, setting in cfg["markets"].items():
        ticker = setting["ticker"]
        path = args.price_dir / f"{ticker}_raw.csv"
        prices = pd.read_csv(path, index_col=0, parse_dates=True)
        inputs[path.name] = sha(path)
        moves = prices.Close.pct_change(fill_method=None).loc[lambda s: s.abs() > 0.15]
        missing = prices.loc[prices[["Open", "Close", "Adj Close"]].isna().any(axis=1)]
        quality[market] = {
            "price_basis": "unadjusted_no_splits",
            "source": "Yahoo Finance auto_adjust=False; not broker-confirmed execution prices",
            "large_moves": {str(d.date()): float(v) for d, v in moves.items()},
            "missing_price_dates": [str(d.date()) for d in missing.index],
            "official_prices_verified": False,
            "adoption_blocked_by_price_anomaly": bool(len(moves)),
        }
        fx_used = (
            fx
            if market == "US"
            else pd.Series(1.0, index=pd.date_range(prices.index[0], prices.index[-1]))
        )
        base = CostScenario(
            **{
                k: setting[k]
                for k in [
                    "commission_rate",
                    "sell_levy_rate",
                    "fx_base_spread",
                    "fx_discount",
                    "dividend_withholding",
                    "capital_gains_rate",
                ]
            }
        )
        initial = account["markets"][market]["market_view_nav_krw"]
        for period in cfg["periods"]:
            period_prices = prices.loc[
                (prices.index >= pd.Timestamp(period["start"]) - pd.Timedelta(days=400))
                & (prices.index <= pd.Timestamp(period["end"]))
            ]
            for allowance in setting["annual_allowances_krw"]:
                for slip in cfg["slippage_bps_per_side"]:
                    scenario = replace(
                        base, annual_allowance_krw=allowance, slippage_rate=slip / 10000
                    )
                    for delay in cfg["additional_execution_delays"]:
                        for strategy in STRATEGIES:
                            key = f"{market}/{period['id']}/allowance{allowance}/slip{slip}/delay{delay}/{strategy}"
                            try:
                                metrics, curve, trades = simulate_account(
                                    period_prices,
                                    strategy,
                                    start=period["start"],
                                    end=period["end"],
                                    initial_krw=initial,
                                    scenario=scenario,
                                    fx_krw_per_unit=fx_used,
                                    price_basis="unadjusted_no_splits",
                                    execution_delay_sessions=delay,
                                )
                            except ValueError as exc:
                                blocked.append({"id": key, "reason": str(exc)})
                                continue
                            metrics.update(
                                {
                                    "id": key,
                                    "market": market,
                                    "period_id": period["id"],
                                    "ticker": ticker,
                                    "adoption_blocked_by_price_anomaly": bool(
                                        len(moves)
                                    ),
                                }
                            )
                            results.append(metrics)
                            curves[key] = {"curve": curve, "trades": trades}
    illustrations = {}
    stock = cfg["stock_cost_illustrations"]
    us = cfg["markets"]["US"]
    us_cost = CostScenario(
        us["commission_rate"],
        us["sell_levy_rate"],
        us["fx_base_spread"],
        us["fx_discount"],
    )
    for label, scenario, convert in [
        (
            "KR_stock_KRX",
            CostScenario(stock["kr_krx_commission"], stock["kr_common_stock_sell_tax"]),
            False,
        ),
        (
            "KR_stock_NXT",
            CostScenario(stock["kr_nxt_commission"], stock["kr_common_stock_sell_tax"]),
            False,
        ),
        (
            "KR_domestic_equity_ETF",
            CostScenario(cfg["markets"]["KR"]["commission_rate"]),
            False,
        ),
        ("US_reuse_USD", us_cost, False),
        ("US_KRW_roundtrip", us_cost, True),
    ]:
        loss = round_trip_loss(scenario, convert_currency=convert)
        illustrations[label] = {
            "flat_price_roundtrip_loss_pct": loss * 100,
            "flat_price_loss_per_1m_krw": loss * 1_000_000,
            "gain_to_break_even_pct": (1 / (1 - loss) - 1) * 100,
        }
    payload = {
        "schema": "tradingagents.account-cost-replay/v1",
        "evidence_as_of": cfg["evidence_as_of"],
        "specification": cfg,
        "input_sha256": inputs,
        "data_quality": quality,
        "runtime": {"python": platform.python_version(), "pandas": pd.__version__},
        "implementation_sha256": {
            "runner": sha(Path(__file__)),
            "ledger": sha(
                Path(__file__).resolve().parents[1]
                / "tradingagents/execution/account_cost_replay.py"
            ),
            "signals": sha(
                Path(__file__).resolve().parents[1]
                / "tradingagents/execution/account_strategy_research.py"
            ),
        },
        "account_as_of": {m: v["as_of"] for m, v in account["markets"].items()},
        "strategy_runs": len(results),
        "blocked_runs": blocked,
        "results": results,
        "roundtrip_illustrations": illustrations,
        "limitations": [
            "All-cash reset at saved market-view NAV size; not a replay of actual holdings or historical recommendations. Do not sum overlapping KR/US account views.",
            "Current commission, FX-spread and levy rates replayed over the whole history; not historical realized fees.",
            "Dividend entitlement accrued at ex-date, net assumed withholding, never reinvested; terminal value includes receivable, not withdrawable cash.",
            "FIFO and prior-day market FX are research proxies; actual broker tax lots and tax conversion rates unavailable.",
            "Annual KRW gains-tax liability reserved from buying capacity, with 0/2.5m allowance scenarios; no actual tax payment date or other-account gains modeled.",
            "US capital gains 22%, dividends 15%; KR domestic equity ETF gains exempt, dividends 15.4% are resident/general-account assumptions, not personal tax certification.",
            "No account-specific/API fee entitlement, expiry, fee minimum/rounding or additional broker-passed charges verified.",
            "No settlement calendar, bid/ask quote, payment-date liquidity, or return on cash; slippage 0/5/15bp is sensitivity only.",
            "Final shares liquidated hypothetically at close, all local NAV converted to KRW once at exit. No within-run recurring FX charges.",
        ],
    }
    (args.output / "cost_replay.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False),
        encoding="utf-8",
    )
    (args.output / "cost_replay_curves.json").write_text(
        json.dumps(curves, ensure_ascii=False, allow_nan=False), encoding="utf-8"
    )
    pd.DataFrame(results).drop(columns=["scenario", "realized_by_year_krw"]).to_csv(
        args.output / "cost_replay_summary.csv", index=False
    )
    print(
        json.dumps(
            {
                "strategy_runs": len(results),
                "blocked_runs": len(blocked),
                "output": str(args.output),
                "quality": quality,
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
