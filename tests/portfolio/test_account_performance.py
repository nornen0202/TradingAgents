from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from tradingagents.portfolio.account_models import AccountConstraints, AccountSnapshot, PortfolioProfile, Position
from tradingagents.portfolio.performance import build_account_performance_outputs


def test_account_performance_reports_kospi_and_kosdaq(tmp_path: Path):
    payload = _build_report(
        tmp_path,
        market_scope="kr",
        benchmarks={
            "KOSPI": [{"date": "2026-01-01", "close": 100}, {"date": "2026-04-01", "close": 110}],
            "KOSDAQ": [{"date": "2026-01-01", "close": 100}, {"date": "2026-04-01", "close": 90}],
        },
    )

    assert payload["benchmarks"] == ["KOSPI", "KOSDAQ"]
    period = payload["periods"][0]
    simple = {item["benchmark"]: item for item in period["simple_benchmarks"]}
    assert period["period"] == "ALL"
    assert period["actual_return"] == 0.2
    assert simple["KOSPI"]["benchmark_return"] == 0.1
    assert simple["KOSPI"]["excess_return"] == 0.1
    assert simple["KOSDAQ"]["benchmark_return"] == -0.1
    assert simple["KOSDAQ"]["excess_return"] == 0.3


def test_account_performance_reports_spy_and_qqq(tmp_path: Path):
    payload = _build_report(
        tmp_path,
        market_scope="us",
        benchmarks={
            "SPY": [{"date": "2026-01-01", "close": 100}, {"date": "2026-04-01", "close": 112}],
            "QQQ": [{"date": "2026-01-01", "close": 100}, {"date": "2026-04-01", "close": 125}],
        },
    )

    assert payload["benchmarks"] == ["SPY", "QQQ"]
    period = payload["periods"][0]
    simple = {item["benchmark"]: item for item in period["simple_benchmarks"]}
    assert simple["SPY"]["benchmark_return"] == 0.12
    assert simple["QQQ"]["benchmark_return"] == 0.25
    assert simple["QQQ"]["excess_return"] == -0.05


def test_account_performance_cashflow_simulation_uses_trade_ledger(tmp_path: Path):
    client = Mock()
    client.fetch_domestic_order_fills.return_value = [
        {
            "ord_dt": "20260201",
            "pdno": "005930",
            "sll_buy_dvsn_cd": "02",
            "tot_ccld_qty": "10",
            "avg_prvs": "10000",
            "tot_ccld_amt": "100000",
        }
    ]
    client.fetch_domestic_period_profit.return_value = ([], {})
    client.fetch_domestic_period_trade_profit.return_value = ([], {})

    with patch("tradingagents.portfolio.kis.KisClient.from_api_keys", return_value=client):
        payload = _build_report(
            tmp_path,
            market_scope="kr",
            broker="kis",
            benchmarks={
                "KOSPI": [
                    {"date": "2026-01-01", "close": 100},
                    {"date": "2026-02-01", "close": 125},
                    {"date": "2026-04-01", "close": 200},
                ],
                "KOSDAQ": [
                    {"date": "2026-01-01", "close": 100},
                    {"date": "2026-02-01", "close": 100},
                    {"date": "2026-04-01", "close": 100},
                ],
            },
        )

    period = payload["periods"][0]
    cashflow = {item["benchmark"]: item for item in period["cashflow_benchmarks"]}
    assert cashflow["KOSPI"]["benchmark_return"] == 1.06
    assert cashflow["KOSPI"]["excess_return"] == -0.86


def _build_report(
    tmp_path: Path,
    *,
    market_scope: str,
    benchmarks: dict[str, list[dict[str, object]]],
    broker: str = "manual",
) -> dict[str, object]:
    archive = tmp_path / "archive"
    previous_run = archive / "runs" / "2026" / f"{market_scope}-previous"
    current_run = archive / "runs" / "2026" / f"{market_scope}-current"
    previous_private = previous_run / "portfolio-private"
    current_private = current_run / "portfolio-private"
    previous_private.mkdir(parents=True)
    current_private.mkdir(parents=True)

    profile_name = f"{market_scope}_profile"
    (previous_private / "status.json").write_text(json.dumps({"profile": profile_name}), encoding="utf-8")
    (previous_private / "account_snapshot.json").write_text(
        json.dumps(
            {
                "snapshot_id": "previous",
                "as_of": "2026-01-01T09:00:00+09:00",
                "account_value_krw": 1_000_000,
            }
        ),
        encoding="utf-8",
    )
    price_path = tmp_path / f"{market_scope}_prices.json"
    price_path.write_text(json.dumps(benchmarks), encoding="utf-8")

    profile = PortfolioProfile(
        name=profile_name,
        enabled=True,
        broker=broker,
        broker_environment="real",
        read_only=True,
        account_no="12345678" if broker == "kis" else None,
        product_code="01" if broker == "kis" else None,
        manual_snapshot_path=None,
        csv_positions_path=None,
        private_output_dirname="portfolio-private",
        watch_tickers=tuple(),
        trigger_budget_krw=500_000,
        constraints=AccountConstraints(),
        market_scope=market_scope,
    )
    snapshot = AccountSnapshot(
        snapshot_id="current",
        as_of="2026-04-01T09:00:00+09:00",
        broker="manual",
        account_id="manual",
        currency="KRW",
        settled_cash_krw=100_000,
        available_cash_krw=100_000,
        buying_power_krw=100_000,
        total_equity_krw=1_200_000,
        positions=(
            Position(
                broker_symbol="TEST",
                canonical_ticker="TEST",
                display_name="Test",
                sector=None,
                quantity=1,
                available_qty=1,
                avg_cost_krw=1_000_000,
                market_price_krw=1_100_000,
                market_value_krw=1_100_000,
                unrealized_pnl_krw=100_000,
            ),
        ),
        constraints=AccountConstraints(),
    )
    settings = SimpleNamespace(
        enabled=True,
        publish_to_site=True,
        public_sanitization="mask_identifiers",
        periods=("ALL",),
        kr_benchmarks=("KOSPI", "KOSDAQ"),
        us_benchmarks=("SPY", "QQQ"),
        price_provider="local_json",
        price_history_path=price_path,
        lookback_days=365,
        fetch_kis_ledger=broker == "kis",
    )

    artifacts = build_account_performance_outputs(
        private_dir=current_private,
        run_dir=current_run,
        snapshot=snapshot,
        profile=profile,
        settings=settings,
    )

    assert "account_performance_public_json" in artifacts
    return json.loads((current_private / "account_performance_public.json").read_text(encoding="utf-8"))
