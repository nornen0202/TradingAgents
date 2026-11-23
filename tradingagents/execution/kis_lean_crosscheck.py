"""Cross-check a small after-cost fixture across the KIS LEAN input format."""

from __future__ import annotations

import argparse
from decimal import Decimal, ROUND_DOWN
import hashlib
import json
from pathlib import Path
import runpy
import shutil

import pandas as pd

from tradingagents.calendar_access import get_exchange_calendar
from .account_cost_replay import CostScenario, simulate_account

FIXTURE_VERSION = "krw-broad-hold-crosscheck-v1"
_INITIAL = Decimal("3000000")
_COMMISSION, _LEVY, _SLIPPAGE = Decimal(".001"), Decimal(".002"), Decimal(".001")
_DIVIDEND_WITHHOLDING, _GAIN_TAX, _ALLOWANCE = Decimal(".10"), Decimal(".15"), Decimal("75000")
_PRODUCT = "000001"


def _fixture_prices():
    dates = get_exchange_calendar("XKRX").sessions_in_range("2026-06-01", "2026-06-12")
    prices = pd.DataFrame(index=dates)
    prices["Open"] = [99000, *(100000 + 1500 * index for index in range(len(dates) - 1))]
    prices["Close"] = prices["Open"] + 500
    prices["High"], prices["Low"] = prices["Close"] + 500, prices["Open"] - 500
    prices["Adj Close"] = prices["Close"]
    prices["Volume"] = 10000
    prices["Dividends"], prices["Stock Splits"] = 0, 0
    prices.loc[dates[3], "Dividends"] = 500
    return prices


def _convert_and_verify(prices, converter, output_root):
    output_root.mkdir(parents=True, exist_ok=True)
    raw = prices[["Open", "High", "Low", "Close", "Volume"]].rename(columns=str.lower)
    raw = raw.reset_index(names="date")
    source = raw.to_csv(index=False, date_format="%Y-%m-%d").encode("utf-8")
    target = converter.export({_PRODUCT: raw}, str(output_root), market_type="krx")[_PRODUCT]
    converted = pd.read_csv(target, names=["date", "open", "high", "low", "close", "volume"], dtype={"date": str})
    if converted["date"].tolist() != raw["date"].dt.strftime("%Y%m%d").tolist():
        raise ValueError("KIS LEAN conversion changed the exchange session sequence")
    if not converted.drop(columns="date").equals(raw.drop(columns="date")):
        raise ValueError("KIS LEAN conversion changed the fixture prices or volume")
    return {
        "fixture_sha256": hashlib.sha256(source).hexdigest(),
        "lean_csv_sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
        "sessions": len(converted),
        "start": raw.date.iloc[0].date().isoformat(),
        "end": raw.date.iloc[-1].date().isoformat(),
    }


def _independent_round_trip(prices, *, costs, tax):
    buy = Decimal(int(prices.Open.iloc[1])) * (1 + (_SLIPPAGE if costs else 0))
    sell = Decimal(int(prices.Close.iloc[-1])) * (1 - (_SLIPPAGE if costs else 0))
    fee, levy = (_COMMISSION, _LEVY) if costs else (Decimal(0), Decimal(0))
    quantity = (_INITIAL / (buy * (1 + fee))).to_integral_value(rounding=ROUND_DOWN)
    basis = quantity * buy * (1 + fee)
    proceeds = quantity * sell * (1 - fee - levy)
    dividends = quantity * Decimal(int(prices.Dividends.sum())) * (1 - (_DIVIDEND_WITHHOLDING if costs else 0))
    taxes = max(Decimal(0), proceeds - basis - _ALLOWANCE) * _GAIN_TAX if tax else Decimal(0)
    return {"quantity": int(quantity), "tax_reserve_krw": float(taxes), "dividend_receivable_krw": float(dividends),
            "final_krw": float(_INITIAL - basis + proceeds + dividends - taxes)}


def compare_fixture(converter, output_root: Path):
    prices = _fixture_prices()
    receipt = _convert_and_verify(prices, converter, output_root)
    results = []
    for name, costs, tax in (("gross_fixture", False, False), ("transaction_costs", True, False),
                             ("transaction_costs_and_tax_reserve", True, True)):
        scenario = CostScenario(
            commission_rate=float(_COMMISSION) if costs else 0,
            sell_levy_rate=float(_LEVY) if costs else 0,
            slippage_rate=float(_SLIPPAGE) if costs else 0,
            dividend_withholding=float(_DIVIDEND_WITHHOLDING) if costs else 0,
            capital_gains_rate=float(_GAIN_TAX) if tax else 0,
            annual_allowance_krw=float(_ALLOWANCE),
        )
        metrics, _, orders = simulate_account(
            prices, "broad_hold", start=prices.index[1].date().isoformat(), end=receipt["end"],
            initial_krw=float(_INITIAL), scenario=scenario, fx_krw_per_unit=pd.Series(1.0, index=prices.index),
            price_basis="unadjusted_no_splits",
        )
        expected = _independent_round_trip(prices, costs=costs, tax=tax)
        if ([order["side"] for order in orders] != ["BUY", "SELL"]
                or orders[0]["quantity"] != expected["quantity"] or orders[1]["quantity"] != expected["quantity"]
                or orders[0]["signal_date"] >= orders[0]["date"]
                or abs(metrics["final_krw"] - expected["final_krw"]) > .000001
                or abs(metrics["tax_reserve_krw"] - expected["tax_reserve_krw"]) > .000001
                or abs(metrics["dividends_net_local"] - expected["dividend_receivable_krw"]) > .000001):
            raise ValueError(f"Independent integer-share ledger differs in {name}")
        results.append({"scenario": name, "ledger_matches": True, "decimal_reference": expected, "results": metrics})
    return {
        "version": FIXTURE_VERSION, "input": receipt, "cases": results, "evidence_scope": "SYNTHETIC_ENGINE_CHECK",
        "lean_input_conversion_executed": True, "lean_backtest_executed": False,
        "docker_executable_available": shutil.which("docker") is not None,
        "market_performance_verified": False,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--converter", type=Path, required=True, help="Verified KIS DataConverter Python source.")
    parser.add_argument("--converter-sha256", required=True, help="Expected SHA-256 of the source artifact.")
    parser.add_argument("--output", type=Path, required=True, help="Dedicated fixture output directory.")
    args = parser.parse_args(argv)
    digest = hashlib.sha256(args.converter.read_bytes()).hexdigest()
    if digest != args.converter_sha256.lower():
        parser.error("KIS conversion source hash differs")
    args.output.mkdir(parents=True, exist_ok=False)
    converted = runpy.run_path(str(args.converter))["DataConverter"]
    receipt = {**compare_fixture(converted, args.output), "converter_sha256": digest}
    (args.output / "crosscheck.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    print(json.dumps(receipt))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
