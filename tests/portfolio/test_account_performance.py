from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from tradingagents.portfolio.account_models import AccountConstraints, AccountSnapshot, PortfolioProfile, Position
from tradingagents.portfolio.performance import build_account_performance_outputs
from tradingagents.portfolio.performance.etf_alternatives import load_external_capital_flows


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
    assert period["simple_nav_return"] == 0.2
    assert period["primary_return_method"] == "available_history_twr_equivalent"
    assert period["twr_return"] == 0.2
    assert payload["summary"]["default_period"] == "ALL_AVAILABLE"
    assert payload["chart_data"]["return_method"] == "available_history_twr_equivalent"
    assert "coverage" in payload["chart_data"]
    assert payload["chart_data"]["final_return"] == payload["summary"]["actual_return"]
    assert payload["chart_data"]["consistency_status"] == "ok"
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


def test_twr_no_external_cashflows_equals_simple_nav_when_reconciled(tmp_path: Path):
    payload = _build_report(
        tmp_path,
        market_scope="kr",
        current_total_equity_krw=1_100_000,
        benchmarks={
            "KOSPI": [{"date": "2026-01-01", "close": 100}, {"date": "2026-04-01", "close": 110}],
            "KOSDAQ": [{"date": "2026-01-01", "close": 100}, {"date": "2026-04-01", "close": 100}],
        },
    )

    period = payload["periods"][0]
    assert payload["reconciliation"]["reconciliation_status"] == "OK"
    assert period["simple_nav_return"] == 0.1
    assert period["twr_return"] == 0.1
    assert period["primary_return_method"] == "available_history_twr_equivalent"
    assert payload["summary"]["performance_confidence"] == "high"


def test_account_performance_cashflow_simulation_ignores_internal_trade_ledger(tmp_path: Path):
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
    assert payload["data_quality"]["external_capital_flow_count"] == 0
    assert cashflow["KOSPI"]["benchmark_return"] == 1.0
    assert cashflow["KOSPI"]["cashflow_event_count"] == 0
    assert cashflow["KOSPI"]["comparison_basis"] == "no_external_cashflows"
    assert client.fetch_domestic_order_fills.call_args.kwargs["start_date"].isoformat() == "2026-01-01"


def test_account_performance_keeps_successful_kis_ledger_rows_when_endpoint_fails(tmp_path: Path):
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
    client.fetch_domestic_period_profit.side_effect = RuntimeError(
        "KIS API error: CANO=12345678&ACNT_PRDT_CD=01 service unavailable"
    )
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

    quality = payload["data_quality"]
    assert quality["ledger_event_count"] == 1
    assert any("domestic_period_profit" in warning for warning in quality["warnings"])
    assert all("12345678" not in warning for warning in quality["warnings"])

    period = payload["periods"][0]
    cashflow = {item["benchmark"]: item for item in period["cashflow_benchmarks"]}
    assert cashflow["KOSPI"]["benchmark_return"] == 1.0


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
    assert ytd_period["status"] == "insufficient_history"
    assert ytd_period["actual_return"] is None
    assert ytd_period["period_coverage"]["same_actual_window_as"] == "ALL_AVAILABLE"
    assert ytd_period["period_coverage"]["is_summary_eligible"] is False
    assert payload["summary"]["default_period"] == "ALL_AVAILABLE"
    assert payload["summary"]["source_period"] == "ALL"
    assert payload["summary"]["actual_return"] == 0.2
    assert any("account_performance_period_insufficient_history:YTD" in item for item in quality["warnings"])


def test_account_performance_short_history_marks_duplicate_windows_and_available_headline(tmp_path: Path):
    payload = _build_report(
        tmp_path,
        market_scope="kr",
        periods=("1M", "3M", "6M", "YTD", "1Y", "ALL"),
        current_as_of="2026-05-07T09:00:00+09:00",
        history_snapshots=[
            {
                "snapshot_id": "first-real",
                "as_of": "2026-04-13T09:00:00+09:00",
                "account_value_krw": 1_000_000,
                "snapshot_health": "VALID",
                "positions": [{"canonical_ticker": "TEST", "market_value_krw": 900_000}],
            }
        ],
        benchmarks={
            "KOSPI": [{"date": "2026-04-13", "close": 100}, {"date": "2026-05-07", "close": 110}],
            "KOSDAQ": [{"date": "2026-04-13", "close": 100}, {"date": "2026-05-07", "close": 90}],
        },
    )

    assert payload["summary"]["default_period"] == "ALL_AVAILABLE"
    assert payload["summary"]["source_period"] == "ALL"
    for period_name in ("1M", "3M", "6M", "YTD", "1Y"):
        period = next(item for item in payload["periods"] if item["period"] == period_name)
        assert period["actual_return"] is None
        assert period["period_coverage"]["is_summary_eligible"] is False
        assert period["period_coverage"]["same_actual_window_as"] == "ALL_AVAILABLE"
    assert any("account_performance_duplicate_actual_windows:ALL_AVAILABLE" in item for item in payload["data_quality"]["warnings"])


def test_min_coverage_ratio_zero_is_honored_by_engine(tmp_path: Path):
    payload = _build_report(
        tmp_path,
        market_scope="kr",
        periods=("1M",),
        current_as_of="2026-05-07T09:00:00+09:00",
        history_snapshots=[
            {
                "snapshot_id": "first-real",
                "as_of": "2026-04-13T09:00:00+09:00",
                "account_value_krw": 1_000_000,
                "snapshot_health": "VALID",
                "positions": [{"canonical_ticker": "TEST", "market_value_krw": 900_000}],
            }
        ],
        benchmarks={
            "KOSPI": [{"date": "2026-04-13", "close": 100}, {"date": "2026-05-07", "close": 110}],
            "KOSDAQ": [{"date": "2026-04-13", "close": 100}, {"date": "2026-05-07", "close": 90}],
        },
        min_coverage_ratio=0.0,
    )

    period = payload["periods"][0]
    assert payload["data_quality"]["min_coverage_ratio"] == 0.0
    assert period["period"] == "1M"
    assert period["actual_return"] == 0.2
    assert period["period_coverage"]["is_summary_eligible"] is True
    assert not any("account_performance_period_insufficient_history:1M" in item for item in payload["data_quality"]["warnings"])


def test_contribution_aggregates_bare_kr_code_with_canonical_position(tmp_path: Path):
    client = Mock()
    client.fetch_domestic_order_fills.return_value = []
    client.fetch_domestic_period_profit.return_value = ([], {})
    client.fetch_domestic_period_trade_profit.return_value = (
        [
            {"trad_dt": "20260201", "pdno": "000660", "realized_pnl": "574163"},
            {"trad_dt": "20260215", "pdno": "034020", "realized_pnl": "87926"},
        ],
        {},
    )
    positions = (
        Position(
            broker_symbol="000660",
            canonical_ticker="000660.KS",
            display_name="SK hynix",
            sector=None,
            quantity=1,
            available_qty=1,
            avg_cost_krw=1_000_000,
            market_price_krw=1_635_500,
            market_value_krw=1_635_500,
            unrealized_pnl_krw=635_500,
        ),
        Position(
            broker_symbol="034020",
            canonical_ticker="034020.KS",
            display_name="Doosan Energy",
            sector=None,
            quantity=1,
            available_qty=1,
            avg_cost_krw=1_000_000,
            market_price_krw=1_285_074,
            market_value_krw=1_285_074,
            unrealized_pnl_krw=285_074,
        ),
    )

    with patch("tradingagents.portfolio.kis.KisClient.from_api_keys", return_value=client):
        payload = _build_report(
            tmp_path,
            market_scope="kr",
            broker="kis",
            positions=positions,
            current_total_equity_krw=3_100_000,
            benchmarks={
                "KOSPI": [{"date": "2026-01-01", "close": 100}, {"date": "2026-04-01", "close": 110}],
                "KOSDAQ": [{"date": "2026-01-01", "close": 100}, {"date": "2026-04-01", "close": 100}],
            },
        )

    rows = {row["ticker"]: row for row in payload["contribution_by_ticker"]}
    assert "000660" not in rows
    assert "034020" not in rows
    assert rows["000660.KS"]["realized_pnl_krw"] == 574_163
    assert rows["000660.KS"]["unrealized_pnl_krw"] == 635_500
    assert rows["000660.KS"]["total_contribution_krw"] == 1_209_663
    assert rows["034020.KS"]["total_contribution_krw"] == 373_000


def test_contribution_uses_period_unrealized_pnl_change_for_reconciliation(tmp_path: Path):
    positions = (
        Position(
            broker_symbol="TEST",
            canonical_ticker="TEST",
            display_name="Test",
            sector=None,
            quantity=1,
            available_qty=1,
            avg_cost_krw=1_000_000,
            market_price_krw=1_600_000,
            market_value_krw=1_600_000,
            unrealized_pnl_krw=600_000,
        ),
    )
    payload = _build_report(
        tmp_path,
        market_scope="kr",
        current_total_equity_krw=1_100_000,
        positions=positions,
        history_snapshots=[
            {
                "snapshot_id": "previous",
                "as_of": "2026-01-01T09:00:00+09:00",
                "account_value_krw": 1_000_000,
                "snapshot_health": "VALID",
                "positions": [
                    {
                        "broker_symbol": "TEST",
                        "canonical_ticker": "TEST",
                        "display_name": "Test",
                        "unrealized_pnl_krw": 500_000,
                    }
                ],
            }
        ],
        benchmarks={
            "KOSPI": [{"date": "2026-01-01", "close": 100}, {"date": "2026-04-01", "close": 110}],
            "KOSDAQ": [{"date": "2026-01-01", "close": 100}, {"date": "2026-04-01", "close": 100}],
        },
    )

    row = next(item for item in payload["contribution_by_ticker"] if item["ticker"] == "TEST")
    assert row["starting_unrealized_pnl_krw"] == 500_000
    assert row["ending_unrealized_pnl_krw"] == 600_000
    assert row["unrealized_pnl_change_krw"] == 100_000
    assert row["total_contribution_krw"] == 100_000
    assert payload["reconciliation"]["simple_nav_pnl_krw"] == 100_000
    assert payload["reconciliation"]["sum_position_contribution_krw"] == 100_000
    assert payload["reconciliation"]["reconciliation_status"] == "OK"


def test_overseas_period_profit_realized_pnl_is_not_fx_converted_twice(tmp_path: Path):
    client = Mock()
    client.fetch_overseas_order_fills.return_value = []
    client.fetch_overseas_period_transactions.return_value = []
    client.fetch_overseas_period_profit.return_value = (
        [{"trad_dt": "20260201", "pdno": "AAPL", "ovrs_rlzt_pfls_amt": "100000", "bass_exrt": "1400"}],
        {},
    )

    with patch("tradingagents.portfolio.kis.KisClient.from_api_keys", return_value=client):
        payload = _build_report(
            tmp_path,
            market_scope="us",
            broker="kis",
            current_total_equity_krw=1_100_000,
            positions=(),
            history_snapshots=[
                {
                    "snapshot_id": "previous",
                    "as_of": "2026-01-01T09:00:00+09:00",
                    "account_value_krw": 1_000_000,
                    "snapshot_health": "VALID",
                    "positions": [],
                }
            ],
            benchmarks={
                "SPY": [{"date": "2026-01-01", "close": 100}, {"date": "2026-04-01", "close": 112}],
                "QQQ": [{"date": "2026-01-01", "close": 100}, {"date": "2026-04-01", "close": 125}],
            },
        )

    rows = {row["ticker"]: row for row in payload["contribution_by_ticker"]}
    assert rows["AAPL"]["realized_pnl_krw"] == 100_000
    assert rows["AAPL"]["total_contribution_krw"] == 100_000
    assert payload["reconciliation"]["simple_nav_pnl_krw"] == 100_000
    assert payload["reconciliation"]["sum_position_contribution_krw"] == 100_000
    assert payload["reconciliation"]["reconciliation_status"] == "OK"


def test_contribution_keeps_unresolved_bare_code_with_warning(tmp_path: Path):
    client = Mock()
    client.fetch_domestic_order_fills.return_value = []
    client.fetch_domestic_period_profit.return_value = ([], {})
    client.fetch_domestic_period_trade_profit.return_value = (
        [{"trad_dt": "20260201", "pdno": "123456", "realized_pnl": "50000"}],
        {},
    )

    with patch("tradingagents.portfolio.kis.KisClient.from_api_keys", return_value=client):
        payload = _build_report(
            tmp_path,
            market_scope="kr",
            broker="kis",
            benchmarks={
                "KOSPI": [{"date": "2026-01-01", "close": 100}, {"date": "2026-04-01", "close": 110}],
                "KOSDAQ": [{"date": "2026-01-01", "close": 100}, {"date": "2026-04-01", "close": 100}],
            },
        )

    rows = {row["ticker"]: row for row in payload["contribution_by_ticker"]}
    assert rows["123456"]["realized_pnl_krw"] == 50_000
    assert "account_performance_contribution_unresolved_ticker:123456" in payload["data_quality"]["warnings"]


def test_account_performance_external_deposit_and_withdrawal_drive_same_cashflow_benchmark(tmp_path: Path):
    client = Mock()
    client.fetch_domestic_order_fills.return_value = []
    client.fetch_domestic_period_trade_profit.return_value = ([], {})
    client.fetch_domestic_period_profit.return_value = (
        [
            {"date": "2026-02-01", "event_type": "deposit", "cashflow_amount": "500000"},
            {"date": "2026-03-01", "event_type": "withdrawal", "cashflow_amount": "200000"},
        ],
        {},
    )

    with patch("tradingagents.portfolio.kis.KisClient.from_api_keys", return_value=client):
        payload = _build_report(
            tmp_path,
            market_scope="kr",
            broker="kis",
            current_total_equity_krw=1_600_000,
            benchmarks={
                "KOSPI": [
                    {"date": "2026-01-01", "close": 100},
                    {"date": "2026-02-01", "close": 125},
                    {"date": "2026-03-01", "close": 160},
                    {"date": "2026-04-01", "close": 200},
                ],
                "KOSDAQ": [{"date": "2026-01-01", "close": 100}, {"date": "2026-04-01", "close": 100}],
            },
        )

    period = payload["periods"][0]
    assert payload["data_quality"]["external_capital_flow_count"] == 2
    assert period["simple_nav_return"] == 0.6
    assert period["twr_return"] == 0.3
    assert period["actual_return"] == 0.3
    assert period["primary_return_method"] == "twr"
    assert payload["chart_data"]["return_method"] == "twr"
    cashflow = {item["benchmark"]: item for item in period["cashflow_benchmarks"]}
    assert cashflow["KOSPI"]["cashflow_event_count"] == 2
    assert cashflow["KOSPI"]["benchmark_return"] == 1.55


def test_account_performance_unknown_cashflow_classification_flags_simple_nav(tmp_path: Path):
    client = Mock()
    client.fetch_domestic_order_fills.return_value = []
    client.fetch_domestic_period_trade_profit.return_value = ([], {})
    client.fetch_domestic_period_profit.return_value = ([{"date": "2026-02-01", "cashflow_amount": "500000"}], {})

    with patch("tradingagents.portfolio.kis.KisClient.from_api_keys", return_value=client):
        payload = _build_report(
            tmp_path,
            market_scope="kr",
            broker="kis",
            benchmarks={
                "KOSPI": [{"date": "2026-01-01", "close": 100}, {"date": "2026-04-01", "close": 110}],
                "KOSDAQ": [{"date": "2026-01-01", "close": 100}, {"date": "2026-04-01", "close": 100}],
            },
        )

    period = payload["periods"][0]
    assert period["primary_return_method"] == "simple_nav_unadjusted"
    assert period["return_method_warning"] == "cashflow_adjustment_unavailable"
    assert period["cashflow_benchmarks"] == []
    assert any("account_performance_cashflow_adjustment_unavailable:ALL" in item for item in payload["data_quality"]["warnings"])


def test_account_performance_contribution_mismatch_triggers_reconciliation_warning(tmp_path: Path):
    payload = _build_report(
        tmp_path,
        market_scope="us",
        current_total_equity_krw=1_500_000,
        benchmarks={
            "SPY": [{"date": "2026-01-01", "close": 100}, {"date": "2026-04-01", "close": 112}],
            "QQQ": [{"date": "2026-01-01", "close": 100}, {"date": "2026-04-01", "close": 125}],
        },
    )

    reconciliation = payload["reconciliation"]
    assert reconciliation["simple_nav_pnl_krw"] == 500_000
    assert reconciliation["sum_position_contribution_krw"] == 100_000
    assert reconciliation["reconciliation_status"] == "FAILED"
    assert payload["summary"]["performance_confidence"] == "low"
    assert payload["summary"]["hide_excess_headline"] is True
    assert payload["summary"]["requires_manual_reconciliation"] is True
    assert "account_performance_unreconciled_pnl" in payload["data_quality"]["warnings"]


def test_broker_baseline_screenshot_period_return_and_mismatch_are_reported(tmp_path: Path):
    broker_baseline = {
        "period_start": "2026-04-13",
        "period_end": "2026-05-12",
        "start_asset_krw": 2,
        "end_asset_krw": 42_218_247,
        "deposit_amount_krw": 37_665_615,
        "withdrawal_amount_krw": 0,
    }
    payload = _build_report(
        tmp_path,
        market_scope="kr",
        periods=("1M", "ALL"),
        current_as_of="2026-05-13T09:00:00+09:00",
        current_total_equity_krw=15_813_494,
        history_snapshots=[
            {
                "snapshot_id": "previous",
                "as_of": "2026-04-13T09:00:00+09:00",
                "account_value_krw": 6_052_202,
                "snapshot_health": "VALID",
                "positions": [{"canonical_ticker": "TEST", "market_value_krw": 5_900_000}],
            }
        ],
        benchmarks={
            "KOSPI": [{"date": "2026-04-13", "close": 100}, {"date": "2026-05-12", "close": 130.45}],
            "KOSDAQ": [{"date": "2026-04-13", "close": 100}, {"date": "2026-05-12", "close": 107.83}],
        },
        broker_baseline=broker_baseline,
    )

    broker = payload["broker_performance"]
    assert broker["investment_pnl_krw"] == 4_552_630
    assert broker["investment_principal_krw"] == 37_665_617
    assert broker["balance_return_pct"] == round(4_552_630 / 37_665_617 * 100, 6)
    assert broker["end_asset_krw"] == 42_218_247
    assert payload["data_quality"]["external_capital_flow_count"] == 1
    assert payload["data_quality"]["snapshot_external_capital_flow_count"] == 0
    assert payload["data_quality"]["broker_external_capital_flow_count"] == 1
    assert "account_performance_broker_external_flows_not_in_snapshot_ledger" in payload["data_quality"]["warnings"]

    period_1m = next(item for item in payload["periods"] if item["period"] == "1M")
    assert period_1m["primary_return_method"] == "simple_nav_unadjusted"
    assert period_1m["return_method_warning"] == "broker_external_cashflow_unmodeled"

    comparison = payload["broker_performance_comparison"]
    assert comparison["comparison_status"] == "FAILED"
    assert comparison["broker_end_asset_krw"] == 42_218_247
    assert comparison["tradingagents_account_value_krw"] == 15_813_494
    assert comparison["period_match_status"] == "MISMATCH"
    assert payload["summary"]["hide_excess_headline"] is True


def test_broker_baseline_one_year_total_deposit_return_matches_screenshot(tmp_path: Path):
    payload = _build_report(
        tmp_path,
        market_scope="kr",
        current_as_of="2026-05-13T09:00:00+09:00",
        current_total_equity_krw=15_813_494,
        history_snapshots=[
            {
                "snapshot_id": "previous",
                "as_of": "2025-05-13T09:00:00+09:00",
                "account_value_krw": 6_052_202,
                "snapshot_health": "VALID",
                "positions": [{"canonical_ticker": "TEST", "market_value_krw": 5_900_000}],
            }
        ],
        benchmarks={
            "KOSPI": [{"date": "2025-05-13", "close": 100}, {"date": "2026-05-12", "close": 293.16}],
            "KOSDAQ": [{"date": "2025-05-13", "close": 100}, {"date": "2026-05-12", "close": 162.60}],
        },
        broker_baseline={
            "period_start": "2025-05-13",
            "period_end": "2026-05-12",
            "start_asset_krw": 2,
            "end_asset_krw": 42_218_247,
            "deposit_amount_krw": 37_865_615,
            "withdrawal_amount_krw": 200_000,
        },
    )

    broker = payload["broker_performance"]
    assert broker["investment_pnl_krw"] == 4_552_630
    assert broker["balance_return_pct"] == round(4_552_630 / 37_665_617 * 100, 6)
    assert broker["total_deposit_return_pct"] == round(4_552_630 / 37_865_617 * 100, 6)


def test_etf_dca_cashflow_loader_ignores_internal_buy_sell_rows(tmp_path: Path):
    path = tmp_path / "cashflows.csv"
    path.write_text(
        "date,type,amount_krw\n"
        "2026-01-02,BUY,100000\n"
        "2026-01-03,SELL,50000\n"
        "2026-01-04,DEPOSIT,300000\n",
        encoding="utf-8",
    )

    flows = load_external_capital_flows(path)

    assert len(flows) == 1
    assert flows[0].flow_type == "deposit"
    assert flows[0].amount_krw == 300_000


def test_etf_dca_uses_dated_cashflows_and_broker_actual(tmp_path: Path):
    payload = _build_report(
        tmp_path,
        market_scope="kr",
        current_as_of="2026-04-01T09:00:00+09:00",
        current_total_equity_krw=36_000,
        history_snapshots=[
            {
                "snapshot_id": "previous",
                "as_of": "2026-01-01T09:00:00+09:00",
                "account_value_krw": 20_000,
                "snapshot_health": "VALID",
                "positions": [{"canonical_ticker": "005930.KS", "market_value_krw": 20_000}],
            }
        ],
        benchmarks={
            "KOSPI": [{"date": "2026-01-01", "close": 100}, {"date": "2026-04-01", "close": 110}],
            "KOSDAQ": [{"date": "2026-01-01", "close": 100}, {"date": "2026-04-01", "close": 100}],
        },
        broker_baseline={
            "period_start": "2026-01-01",
            "period_end": "2026-04-01",
            "start_asset_krw": 20_000,
            "end_asset_krw": 36_000,
            "deposit_amount_krw": 10_000,
            "withdrawal_amount_krw": 0,
        },
        cashflow_baseline=[
            {"date": "2026-02-01", "type": "DEPOSIT", "amount_krw": 10_000},
        ],
        etf_prices={
            "KOSPI200": [
                {"date": "2026-01-01", "close": 100},
                {"date": "2026-02-01", "close": 120},
                {"date": "2026-04-01", "close": 150},
            ],
            "KOSDAQ150": [
                {"date": "2026-01-01", "close": 100},
                {"date": "2026-02-01", "close": 100},
                {"date": "2026-04-01", "close": 100},
            ],
            "SP500_KRW": [
                {"date": "2026-01-01", "close": 100},
                {"date": "2026-02-01", "close": 110},
                {"date": "2026-04-01", "close": 121},
            ],
            "NASDAQ100_KRW": [
                {"date": "2026-01-01", "close": 100},
                {"date": "2026-02-01", "close": 125},
                {"date": "2026-04-01", "close": 150},
            ],
        },
    )

    comparison = payload["etf_alternative_comparison"]
    assert comparison["status"] == "OK"
    assert comparison["actual_source"] == "broker_reported"
    assert comparison["actual"]["balance_return_pct"] == 20.0
    assert comparison["cashflows"]["dated_flow_count"] == 1

    kospi200 = next(item for item in comparison["alternatives"] if item["key"] == "KOSPI200_100")
    assert kospi200["status"] == "OK"
    assert kospi200["end_value_krw"] == 42_500
    assert kospi200["investment_pnl_krw"] == 12_500
    assert kospi200["balance_return_pct"] == round(12_500 / 30_000 * 100, 6)
    assert kospi200["excess_return_pct"] == round(20.0 - 12_500 / 30_000 * 100, 6)
    assert kospi200["excess_pnl_krw"] == -6_500


def test_etf_dca_requires_dated_cashflows_when_broker_reports_aggregate_deposits(tmp_path: Path):
    payload = _build_report(
        tmp_path,
        market_scope="kr",
        current_as_of="2026-05-13T09:00:00+09:00",
        current_total_equity_krw=15_813_494,
        history_snapshots=[
            {
                "snapshot_id": "previous",
                "as_of": "2026-04-13T09:00:00+09:00",
                "account_value_krw": 6_052_202,
                "snapshot_health": "VALID",
                "positions": [{"canonical_ticker": "TEST", "market_value_krw": 5_900_000}],
            }
        ],
        benchmarks={
            "KOSPI": [{"date": "2026-04-13", "close": 100}, {"date": "2026-05-12", "close": 130.45}],
            "KOSDAQ": [{"date": "2026-04-13", "close": 100}, {"date": "2026-05-12", "close": 107.83}],
        },
        broker_baseline={
            "period_start": "2026-04-13",
            "period_end": "2026-05-12",
            "start_asset_krw": 2,
            "end_asset_krw": 42_218_247,
            "deposit_amount_krw": 37_665_615,
            "withdrawal_amount_krw": 0,
        },
    )

    comparison = payload["etf_alternative_comparison"]
    assert comparison["status"] == "cashflow_dates_required"
    assert comparison["cashflows"]["missing_reason"] == "dated_external_capital_flows_required"
    assert comparison["alternatives"] == []
    assert "etf_alternative_cashflow_dates_required" in payload["data_quality"]["warnings"]


def test_etf_dca_flags_fx_missing_for_us_etf_without_fx_series(tmp_path: Path):
    payload = _build_report(
        tmp_path,
        market_scope="kr",
        current_total_equity_krw=22_000,
        history_snapshots=[
            {
                "snapshot_id": "previous",
                "as_of": "2026-01-01T09:00:00+09:00",
                "account_value_krw": 20_000,
                "snapshot_health": "VALID",
                "positions": [{"canonical_ticker": "005930.KS", "market_value_krw": 20_000}],
            }
        ],
        benchmarks={
            "KOSPI": [{"date": "2026-01-01", "close": 100}, {"date": "2026-04-01", "close": 110}],
            "KOSDAQ": [{"date": "2026-01-01", "close": 100}, {"date": "2026-04-01", "close": 100}],
        },
        broker_baseline={
            "period_start": "2026-01-01",
            "period_end": "2026-04-01",
            "start_asset_krw": 20_000,
            "end_asset_krw": 22_000,
            "deposit_amount_krw": 0,
            "withdrawal_amount_krw": 0,
        },
        etf_prices={
            "SP500": [{"date": "2026-01-01", "close": 100}, {"date": "2026-04-01", "close": 110}],
        },
        etf_portfolios={"SP500_US": {"SP500": 1.0}},
    )

    comparison = payload["etf_alternative_comparison"]
    sp500 = next(item for item in comparison["alternatives"] if item["key"] == "SP500_US")
    assert sp500["status"] == "fx_missing"
    assert any("etf_alternative_fx_missing:USD" in item for item in sp500["warnings"])


def test_etf_dca_policy_triggers_report_only_decisions(tmp_path: Path):
    payload = _build_report(
        tmp_path,
        market_scope="kr",
        current_total_equity_krw=36_000,
        history_snapshots=[
            {
                "snapshot_id": "previous",
                "as_of": "2026-01-01T09:00:00+09:00",
                "account_value_krw": 20_000,
                "snapshot_health": "VALID",
                "positions": [{"canonical_ticker": "005930.KS", "market_value_krw": 20_000}],
            }
        ],
        benchmarks={
            "KOSPI": [{"date": "2026-01-01", "close": 100}, {"date": "2026-04-01", "close": 110}],
            "KOSDAQ": [{"date": "2026-01-01", "close": 100}, {"date": "2026-04-01", "close": 100}],
        },
        broker_baseline={
            "period_start": "2026-01-01",
            "period_end": "2026-04-01",
            "start_asset_krw": 20_000,
            "end_asset_krw": 36_000,
            "deposit_amount_krw": 10_000,
            "withdrawal_amount_krw": 0,
        },
        cashflow_baseline=[{"date": "2026-02-01", "type": "DEPOSIT", "amount_krw": 10_000}],
        etf_prices={
            "KOSPI200": [{"date": "2026-01-01", "close": 100}, {"date": "2026-02-01", "close": 100}, {"date": "2026-04-01", "close": 100}],
            "KOSDAQ150": [{"date": "2026-01-01", "close": 100}, {"date": "2026-02-01", "close": 100}, {"date": "2026-04-01", "close": 100}],
            "SP500_KRW": [{"date": "2026-01-01", "close": 100}, {"date": "2026-02-01", "close": 100}, {"date": "2026-04-01", "close": 100}],
            "NASDAQ100_KRW": [{"date": "2026-01-01", "close": 100}, {"date": "2026-02-01", "close": 100}, {"date": "2026-04-01", "close": 100}],
        },
        alpha_policy_inputs={
            "monthly_blended_excess_return_pct": [-1.0, -2.0, -0.5],
            "six_month_blended_excess_return_pct": -0.1,
            "twelve_month_actual_return_pct": 5.0,
            "twelve_month_blended_return_pct": 8.0,
            "twelve_month_actual_mdd_pct": -20.0,
            "twelve_month_blended_mdd_pct": -10.0,
            "twelve_month_actual_turnover_pct": 120.0,
            "twelve_month_blended_turnover_pct": 5.0,
            "action_add_starter_vs_etf": {"sample_count": 5, "avg_excess_return_pct": -1.2},
        },
    )

    decisions = payload["etf_alternative_comparison"]["policy"]["decisions"]
    assert "FREEZE_NEW_INDIVIDUAL_BUYS" in decisions
    assert "REDUCE_INDIVIDUAL_STOCK_TARGET_TO_15PCT" in decisions
    assert "ETF_CORE_REQUIRED" in decisions
    assert "ACTION_SIGNALS_OBSERVATION_ONLY" in decisions


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
    positions: tuple[Position, ...] | None = None,
    min_coverage_ratio: float | None = None,
    broker_baseline: dict[str, object] | None = None,
    cashflow_baseline: list[dict[str, object]] | None = None,
    etf_prices: dict[str, list[dict[str, object]]] | None = None,
    etf_fx: dict[str, list[dict[str, object]]] | None = None,
    etf_symbols: dict[str, str] | None = None,
    etf_portfolios: dict[str, dict[str, float]] | None = None,
    alpha_policy_inputs: dict[str, object] | None = None,
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
    broker_baseline_path = None
    if broker_baseline is not None:
        broker_baseline_path = tmp_path / f"{market_scope}_broker_baseline.json"
        broker_baseline_path.write_text(json.dumps(broker_baseline), encoding="utf-8")
    cashflow_baseline_path = None
    if cashflow_baseline is not None:
        cashflow_baseline_path = tmp_path / f"{market_scope}_cashflows.json"
        cashflow_baseline_path.write_text(json.dumps(cashflow_baseline), encoding="utf-8")
    etf_price_path = None
    if etf_prices is not None:
        etf_price_path = tmp_path / f"{market_scope}_etf_prices.json"
        etf_price_path.write_text(json.dumps(etf_prices), encoding="utf-8")
    etf_fx_path = None
    if etf_fx is not None:
        etf_fx_path = tmp_path / f"{market_scope}_etf_fx.json"
        etf_fx_path.write_text(json.dumps(etf_fx), encoding="utf-8")

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
    if positions is None:
        positions = (
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
        positions=positions,
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
        broker_return_baseline_path=broker_baseline_path,
        broker_period_start=str((broker_baseline or {}).get("period_start") or ""),
        broker_period_end=str((broker_baseline or {}).get("period_end") or ""),
        prefer_broker_reported_performance=True,
        show_snapshot_performance_when_unreconciled=False,
        etf_alternative_enabled=True,
        cashflow_baseline_path=cashflow_baseline_path,
        etf_price_history_path=etf_price_path,
        etf_fx_history_path=etf_fx_path,
        etf_alternative_include_start_asset=True,
        etf_alternative_transaction_cost_bps=0.0,
        etf_alternative_symbols=etf_symbols or {},
        etf_alternative_currencies={},
        etf_alternative_labels={},
        etf_alternative_portfolios=etf_portfolios or {},
        etf_alternative_blended_weights={},
        etf_dca_min_initial_seed_krw=10_000,
        etf_dca_reinvest_dividends=True,
        alpha_policy_mode="report_only",
        alpha_policy_reduce_target_pct=15.0,
        alpha_policy_min_action_samples=5,
        alpha_policy_inputs=alpha_policy_inputs or {},
    )
    if min_coverage_ratio is not None:
        settings.min_coverage_ratio = min_coverage_ratio

    artifacts = build_account_performance_outputs(
        private_dir=current_private,
        run_dir=current_run,
        snapshot=snapshot,
        profile=profile,
        settings=settings,
    )

    assert "account_performance_public_json" in artifacts
    return json.loads((current_private / "account_performance_public.json").read_text(encoding="utf-8"))
