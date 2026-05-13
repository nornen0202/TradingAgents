from __future__ import annotations

import json
from pathlib import Path

from .helpers import build_fixture_comparison, default_settings


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

    result = build_fixture_comparison(etf_fixture_dir, settings=settings)
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

    result = build_fixture_comparison(etf_fixture_dir, settings=settings)
    alternative = next(item for item in result.to_raw_dict()["alternatives"] if item["key"] == "KOSPI200_100")

    assert [item["side"] for item in alternative["transactions"]] == ["BUY", "SELL"]
    assert alternative["end_value_krw"] == 750_000
