from __future__ import annotations

import json
from pathlib import Path

from tradingagents.portfolio.performance.broker_models import BrokerPerformanceSummary

from .helpers import build_fixture_comparison, default_settings


def _matching_broker_cashflows(*, withdrawn=0):
    deposited = 1_000_000
    return BrokerPerformanceSummary(
        broker="fixture", account_scope="fixture-scope", period_start="2026-04-13", period_end="2026-05-12",
        start_asset_krw=0, end_asset_krw=deposited - withdrawn, balance_return_pct=0.0,
        deposit_amount_krw=deposited, withdrawal_amount_krw=withdrawn,
    )


def test_deposit_on_holiday_buys_next_trading_day(tmp_path: Path, etf_fixture_dir: Path):
    cashflows = tmp_path / "cashflows.csv"
    cashflows.write_text("date,type,amount_krw\n2026-04-18,DEPOSIT,1000000\n", encoding="utf-8")
    prices = tmp_path / "prices.json"
    prices.write_text(
        json.dumps(
            {
                "KOSPI200": [
                    {"date": "2026-04-20", "close": 100.0},
                    {"date": "2026-05-12", "close": 110.0},
                ]
            }
        ),
        encoding="utf-8",
    )
    settings = default_settings(
        etf_fixture_dir,
        cashflow_path=cashflows,
        price_path=prices,
        portfolios={"KOSPI200_100": {"KOSPI200": 1.0}},
    )

    result = build_fixture_comparison(etf_fixture_dir, settings=settings, broker_summary=_matching_broker_cashflows())
    raw = result.to_raw_dict()
    alternative = next(item for item in raw["alternatives"] if item["key"] == "KOSPI200_100")

    assert alternative["status"] == "OK"
    assert alternative["transactions"][0]["requested_date"] == "2026-04-18"
    assert alternative["transactions"][0]["trade_date"] == "2026-04-20"


def test_withdrawal_sells_benchmark_pro_rata(tmp_path: Path, etf_fixture_dir: Path):
    cashflows = tmp_path / "cashflows.csv"
    cashflows.write_text(
        "\n".join(
            [
                "date,type,amount_krw",
                "2026-04-13,DEPOSIT,1000000",
                "2026-04-20,WITHDRAWAL,250000",
            ]
        ),
        encoding="utf-8",
    )
    prices = tmp_path / "prices.json"
    prices.write_text(
        json.dumps(
            {
                "KOSPI200": [
                    {"date": "2026-04-13", "close": 100.0},
                    {"date": "2026-04-20", "close": 100.0},
                    {"date": "2026-05-12", "close": 100.0},
                ]
            }
        ),
        encoding="utf-8",
    )
    settings = default_settings(
        etf_fixture_dir,
        cashflow_path=cashflows,
        price_path=prices,
        portfolios={"KOSPI200_100": {"KOSPI200": 1.0}},
    )

    result = build_fixture_comparison(etf_fixture_dir, settings=settings,
                                      broker_summary=_matching_broker_cashflows(withdrawn=250_000))
    alternative = next(item for item in result.to_raw_dict()["alternatives"] if item["key"] == "KOSPI200_100")

    assert [item["side"] for item in alternative["transactions"]] == ["BUY", "SELL"]
    assert alternative["end_value_krw"] == 750_000


def test_shorter_period_keeps_verified_opening_capital(tmp_path, etf_fixture_dir):
    prices = tmp_path / "prices.json"
    prices.write_text(json.dumps({"KOSPI200": [{"date": "2026-04-13", "close": 100},
                                               {"date": "2026-04-20", "close": 110}]}))
    settings = default_settings(etf_fixture_dir, use_cashflows=False, price_path=prices,
                                portfolios={"KOSPI200_100": {"KOSPI200": 1.0}})
    settings.etf_dca_period_start = "2026-04-13"
    settings.etf_dca_period_end = "2026-04-20"
    broker = BrokerPerformanceSummary(broker="fixture", account_scope="fixture-scope", period_start="2026-04-13",
                                      period_end="2026-05-12", start_asset_krw=20_000, balance_return_pct=0.0)
    result = build_fixture_comparison(etf_fixture_dir, settings=settings, broker_summary=broker)
    assert result.actual["period_match_status"] == "MISMATCH"
    alternative = next(item for item in result.alternatives if item.key == "KOSPI200_100")
    assert alternative.end_value_krw == 22_000 and alternative.excess_return_pct is None
