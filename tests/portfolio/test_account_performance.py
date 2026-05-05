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
    assert client.fetch_domestic_order_fills.call_args.kwargs["start_date"].isoformat() == "2026-01-01"


def test_account_performance_excludes_watchlist_only_seed_snapshots(tmp_path: Path):
    payload = _build_report(
        tmp_path,
        market_scope="kr",
        periods=("1M", "YTD", "ALL"),
        current_as_of="2026-05-05T09:00:00+09:00",
        history_snapshots=[
            {
                "snapshot_id": "watchlist-seed",
                "as_of": "2026-04-10T09:00:00+09:00",
                "account_value_krw": 2,
                "snapshot_health": "WATCHLIST_ONLY",
                "positions": [],
            },
            {
                "snapshot_id": "first-real",
                "as_of": "2026-04-16T09:00:00+09:00",
                "account_value_krw": 1_000_000,
                "snapshot_health": "VALID",
                "positions": [{"canonical_ticker": "TEST", "market_value_krw": 900_000}],
            },
        ],
        benchmarks={
            "KOSPI": [
                {"date": "2026-04-10", "close": 100},
                {"date": "2026-04-16", "close": 100},
                {"date": "2026-05-05", "close": 110},
            ],
            "KOSDAQ": [
                {"date": "2026-04-10", "close": 100},
                {"date": "2026-04-16", "close": 100},
                {"date": "2026-05-05", "close": 90},
            ],
        },
    )

    quality = payload["data_quality"]
    assert quality["raw_snapshot_count"] == 3
    assert quality["snapshot_count"] == 2
    assert quality["excluded_snapshot_count"] == 1
    assert quality["excluded_snapshot_reasons"] == {"watchlist_only": 1}
    assert quality["min_snapshot_value_krw"] == 1_000_000
    assert "account_performance_snapshot_excluded:watchlist_only:1" in quality["warnings"]

    all_period = next(item for item in payload["periods"] if item["period"] == "ALL")
    assert all_period["start_date"] == "2026-04-16"
    assert all_period["actual_start_value_krw"] == 1_000_000
    assert all_period["actual_end_value_krw"] == 1_200_000
    assert all_period["actual_return"] == 0.2
    assert all_period["partial"] is False

    ytd_period = next(item for item in payload["periods"] if item["period"] == "YTD")
    assert ytd_period["requested_start_date"] == "2026-01-01"
    assert ytd_period["start_date"] == "2026-04-16"
    assert ytd_period["partial"] is True
    assert ytd_period["actual_return"] == 0.2


def _build_report(
    tmp_path: Path,
    *,
    market_scope: str,
    benchmarks: dict[str, list[dict[str, object]]],
    broker: str = "manual",
    periods: tuple[str, ...] = ("ALL",),
    history_snapshots: list[dict[str, object]] | None = None,
    current_as_of: str = "2026-04-01T09:00:00+09:00",
    current_total_equity_krw: int = 1_200_000,
    current_snapshot_health: str = "VALID",
) -> dict[str, object]:
    archive = tmp_path / "archive"
    current_run = archive / "runs" / "2026" / f"{market_scope}-current"
    current_private = current_run / "portfolio-private"
    current_private.mkdir(parents=True)

    profile_name = f"{market_scope}_profile"
    if history_snapshots is None:
        history_snapshots = [
            {
                "snapshot_id": "previous",
                "as_of": "2026-01-01T09:00:00+09:00",
                "account_value_krw": 1_000_000,
                "snapshot_health": "VALID",
                "positions": [{"canonical_ticker": "TEST", "market_value_krw": 900_000}],
            }
        ]
    for index, history_payload in enumerate(history_snapshots):
        previous_private = archive / "runs" / "2026" / f"{market_scope}-previous-{index}" / "portfolio-private"
        previous_private.mkdir(parents=True)
        (previous_private / "status.json").write_text(json.dumps({"profile": profile_name}), encoding="utf-8")
        (previous_private / "account_snapshot.json").write_text(json.dumps(history_payload), encoding="utf-8")
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
        as_of=current_as_of,
        broker="manual",
        account_id="manual",
        currency="KRW",
        settled_cash_krw=100_000,
        available_cash_krw=100_000,
        buying_power_krw=100_000,
        total_equity_krw=current_total_equity_krw,
        snapshot_health=current_snapshot_health,
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
        periods=periods,
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
