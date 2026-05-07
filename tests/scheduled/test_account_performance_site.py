from __future__ import annotations

import json
from pathlib import Path

from tradingagents.scheduled.config import SiteSettings
from tradingagents.scheduled.site import build_site


def test_portfolio_page_renders_account_performance_and_masks_identifiers(tmp_path: Path):
    archive = tmp_path / "archive"
    site = tmp_path / "site"
    run_dir = archive / "runs" / "2026" / "20260401T090000_test"
    private_dir = run_dir / "portfolio-private"
    private_dir.mkdir(parents=True)

    (private_dir / "status.json").write_text(
        json.dumps(
            {
                "status": "success",
                "profile": "kr_kis_default",
                "snapshot_health": "VALID",
                "generated_at": "2026-04-01T09:00:00+09:00",
            }
        ),
        encoding="utf-8",
    )
    (private_dir / "portfolio_report.md").write_text("# TradingAgents 계좌 운용 리포트\n", encoding="utf-8")
    (private_dir / "portfolio_report.json").write_text(json.dumps({"actions": []}), encoding="utf-8")
    (private_dir / "account_snapshot.json").write_text(
        json.dumps(
            {
                "snapshot_id": "20260401T090000_kis_12345678-01",
                "account_id": "12345678-01",
                "pending_orders": [{"broker_order_id": "ODNO-SECRET"}],
                "warnings": ["CANO=12345678 ACNT_PRDT_CD=01"],
            }
        ),
        encoding="utf-8",
    )
    performance_payload = {
        "status": "ok",
        "generated_at": "2026-04-01T09:00:00+09:00",
        "market_scope": "KR",
        "benchmarks": ["KOSPI", "KOSDAQ"],
        "summary": {
            "default_period": "ALL",
            "actual_return": 0.2,
            "best_excess": {"benchmark": "KOSDAQ", "excess_return": 0.3, "excess_krw": 300000},
            "worst_excess": {"benchmark": "KOSPI", "excess_return": 0.1, "excess_krw": 100000},
        },
        "periods": [
            {
                "period": "YTD",
                "requested_start_date": "2026-01-01",
                "start_date": "2026-02-01",
                "end_date": "2026-04-01",
                "partial": True,
                "partial_reasons": ["requested_start=2026-01-01:available_start=2026-02-01"],
                "status": "insufficient_history",
                "actual_return": None,
                "mdd": None,
                "volatility": None,
                "simple_benchmarks": [],
                "cashflow_benchmarks": [],
                "best_excess": {},
                "worst_excess": {},
            },
            {
                "period": "ALL",
                "requested_start_date": "2026-01-01",
                "start_date": "2026-02-01",
                "partial": True,
                "actual_return": 0.2,
                "mdd": -0.05,
                "volatility": 0.01,
                "simple_benchmarks": [
                    {"benchmark": "KOSPI", "benchmark_return": 0.1, "excess_return": 0.1, "excess_krw": 100000},
                    {"benchmark": "KOSDAQ", "benchmark_return": -0.1, "excess_return": 0.3, "excess_krw": 300000},
                ],
                "cashflow_benchmarks": [],
            }
        ],
        "chart_data": {
            "benchmarks": ["KOSPI", "KOSDAQ"],
            "series": [
                {"date": "2026-01-01", "account_return": 0, "KOSPI": 0, "KOSDAQ": 0},
                {"date": "2026-04-01", "account_return": 0.2, "KOSPI": 0.1, "KOSDAQ": -0.1},
            ],
        },
        "costs": {"fees_krw": 1000, "taxes_krw": 2000, "total_cost_krw": 3000},
        "contribution_by_ticker": [
            {"ticker": "000660.KS", "total_contribution_krw": 100000, "realized_pnl_krw": 0, "unrealized_pnl_krw": 100000}
        ],
        "data_quality": {"snapshot_count": 2, "ledger_event_count": 0, "benchmark_provider": "local_json", "warnings": []},
        "public_sanitization": "mask_identifiers",
    }
    (private_dir / "account_performance_public.json").write_text(json.dumps(performance_payload), encoding="utf-8")
    (private_dir / "account_performance_chart_data.json").write_text(json.dumps(performance_payload["chart_data"]), encoding="utf-8")
    (private_dir / "account_performance_report.md").write_text("## 계좌 성과 vs 지수/ETF\n", encoding="utf-8")

    manifest = {
        "run_id": "20260401T090000_test",
        "label": "test",
        "status": "success",
        "started_at": "2026-04-01T09:00:00+09:00",
        "finished_at": "2026-04-01T09:05:00+09:00",
        "timezone": "Asia/Seoul",
        "settings": {"output_language": "Korean"},
        "summary": {"total_tickers": 0, "successful_tickers": 0, "failed_tickers": 0},
        "warnings": [],
        "tickers": [],
        "portfolio": {
            "status": "success",
            "account_performance": {"enabled": True, "publish_to_site": True, "status": "ok"},
            "artifacts": {
                "account_snapshot_json": (private_dir / "account_snapshot.json").as_posix(),
                "portfolio_report_md": (private_dir / "portfolio_report.md").as_posix(),
                "portfolio_report_json": (private_dir / "portfolio_report.json").as_posix(),
                "account_performance_public_json": (private_dir / "account_performance_public.json").as_posix(),
                "account_performance_chart_data_json": (private_dir / "account_performance_chart_data.json").as_posix(),
                "account_performance_report_md": (private_dir / "account_performance_report.md").as_posix(),
            },
        },
    }
    (run_dir / "run.json").write_text(json.dumps(manifest), encoding="utf-8")

    build_site(archive, site, SiteSettings())

    public_html = (site / "runs" / manifest["run_id"] / "portfolio.html").read_text(encoding="utf-8")
    published_snapshot = (site / "downloads" / manifest["run_id"] / "portfolio" / "account_snapshot.json").read_text(
        encoding="utf-8"
    )
    assert "계좌 성과 vs 지수/ETF" in public_html
    assert "성과 기준 기간" in public_html
    assert "계좌 수익률" in public_html
    assert "YTD (부분)" in public_html
    assert "데이터 부족" in public_html
    assert "요청 기간 시작일의 계좌 스냅샷 없음" in public_html
    assert "사용 가능 전체 기간 (부분)" in public_html
    assert "부분 산출" in public_html
    assert "기간별 원시 산출" in public_html
    assert "사용 가능 기간 수익률" in public_html
    assert "보유/실현 손익 기여도" in public_html
    assert "KOSPI" in public_html
    assert "KOSDAQ" in public_html
    assert "account_performance_public.json" in public_html
    assert "account_snapshot.json" not in public_html
    assert "12345678" not in public_html
    assert "ODNO-SECRET" not in public_html
    assert "12345678" not in published_snapshot
    assert "ODNO-SECRET" not in published_snapshot
    assert (site / "downloads" / manifest["run_id"] / "portfolio" / "account_performance_public.json").exists()


def test_portfolio_page_normalizes_legacy_duplicate_account_performance_periods(tmp_path: Path):
    archive = tmp_path / "archive"
    site = tmp_path / "site"
    run_dir = archive / "runs" / "2026" / "20260402T090000_test"
    private_dir = run_dir / "portfolio-private"
    private_dir.mkdir(parents=True)

    (private_dir / "status.json").write_text(
        json.dumps(
            {
                "status": "success",
                "profile": "kr_kis_default",
                "snapshot_health": "VALID",
                "generated_at": "2026-04-02T09:00:00+09:00",
            }
        ),
        encoding="utf-8",
    )
    performance_payload = {
        "status": "ok",
        "generated_at": "2026-04-02T09:00:00+09:00",
        "market_scope": "KR",
        "benchmarks": ["KOSPI"],
        "summary": {
            "default_period": "YTD",
            "requested_start_date": "2026-01-01",
            "start_date": "2026-02-01",
            "end_date": "2026-04-02",
            "partial": True,
            "actual_return": 0.2,
            "best_excess": {"benchmark": "KOSPI", "excess_return": 0.1, "excess_krw": 100000},
            "worst_excess": {"benchmark": "KOSPI", "excess_return": 0.1, "excess_krw": 100000},
        },
        "periods": [
            {
                "period": "YTD",
                "requested_start_date": "2026-01-01",
                "start_date": "2026-02-01",
                "end_date": "2026-04-02",
                "partial": True,
                "partial_reasons": ["requested_start=2026-01-01:actual_start=2026-02-01"],
                "actual_return": 0.2,
                "mdd": -0.05,
                "volatility": 0.01,
                "simple_benchmarks": [
                    {"benchmark": "KOSPI", "benchmark_return": 0.1, "excess_return": 0.1, "excess_krw": 100000}
                ],
                "cashflow_benchmarks": [],
                "best_excess": {"benchmark": "KOSPI", "excess_return": 0.1, "excess_krw": 100000},
                "worst_excess": {"benchmark": "KOSPI", "excess_return": 0.1, "excess_krw": 100000},
            },
            {
                "period": "ALL",
                "requested_start_date": "2026-02-01",
                "start_date": "2026-02-01",
                "end_date": "2026-04-02",
                "partial": True,
                "actual_return": 0.2,
                "mdd": -0.05,
                "volatility": 0.01,
                "simple_benchmarks": [
                    {"benchmark": "KOSPI", "benchmark_return": 0.1, "excess_return": 0.1, "excess_krw": 100000}
                ],
                "cashflow_benchmarks": [],
                "best_excess": {"benchmark": "KOSPI", "excess_return": 0.1, "excess_krw": 100000},
                "worst_excess": {"benchmark": "KOSPI", "excess_return": 0.1, "excess_krw": 100000},
            },
        ],
        "chart_data": {
            "benchmarks": ["KOSPI"],
            "series": [
                {"date": "2026-02-01", "account_return": 0, "KOSPI": 0},
                {"date": "2026-04-02", "account_return": 0.2, "KOSPI": 0.1},
            ],
        },
        "costs": {},
        "contribution_by_ticker": [],
        "data_quality": {"snapshot_count": 2, "ledger_event_count": 0, "benchmark_provider": "local_json", "warnings": []},
    }
    performance_path = private_dir / "account_performance_public.json"
    performance_path.write_text(json.dumps(performance_payload), encoding="utf-8")

    manifest = {
        "run_id": "20260402T090000_test",
        "label": "test",
        "status": "success",
        "started_at": "2026-04-02T09:00:00+09:00",
        "finished_at": "2026-04-02T09:05:00+09:00",
        "timezone": "Asia/Seoul",
        "settings": {"output_language": "Korean"},
        "summary": {"total_tickers": 0, "successful_tickers": 0, "failed_tickers": 0},
        "warnings": [],
        "tickers": [],
        "portfolio": {
            "status": "success",
            "account_performance": {"enabled": True, "publish_to_site": True, "status": "ok"},
            "artifacts": {"account_performance_public_json": performance_path.as_posix()},
        },
    }
    (run_dir / "run.json").write_text(json.dumps(manifest), encoding="utf-8")

    build_site(archive, site, SiteSettings())

    public_html = (site / "runs" / manifest["run_id"] / "portfolio.html").read_text(encoding="utf-8")
    published_payload = json.loads(
        (site / "downloads" / manifest["run_id"] / "portfolio" / "account_performance_public.json").read_text(
            encoding="utf-8"
        )
    )
    ytd_period = next(period for period in published_payload["periods"] if period["period"] == "YTD")

    assert "사용 가능 전체 기간 (부분)" in public_html
    assert "20.00%" in public_html
    assert "YTD (부분)" in public_html
    assert "데이터 부족" in public_html
    assert "요청 기간 시작일의 계좌 스냅샷 없음" in public_html
    assert ytd_period["status"] == "insufficient_history"
    assert ytd_period["actual_return"] is None
    assert ytd_period["period_coverage"]["same_actual_window_as"] == "ALL_AVAILABLE"
    assert published_payload["summary"]["default_period"] == "ALL_AVAILABLE"
    assert published_payload["summary"]["source_period"] == "ALL"
    assert any(
        "account_performance_period_insufficient_history:YTD" in item
        for item in published_payload["data_quality"]["warnings"]
    )


def test_portfolio_page_hides_duplicate_periods_by_default_and_preserves_diagnostics(tmp_path: Path):
    archive = tmp_path / "archive"
    site = tmp_path / "site"
    run_dir = archive / "runs" / "2026" / "20260507T090000_test"
    private_dir = run_dir / "portfolio-private"
    private_dir.mkdir(parents=True)
    (private_dir / "status.json").write_text(json.dumps({"status": "success", "profile": "kr"}), encoding="utf-8")
    periods = []
    for name in ["1M", "3M", "6M", "YTD", "1Y"]:
        periods.append(
            {
                "period": name,
                "requested_start_date": "2026-01-01",
                "start_date": "2026-04-13",
                "end_date": "2026-05-07",
                "partial": True,
                "status": "insufficient_history",
                "actual_return": None,
                "period_coverage": {
                    "period": name,
                    "requested_start_date": "2026-01-01",
                    "actual_start_date": "2026-04-13",
                    "end_date": "2026-05-07",
                    "coverage_ratio": 0.25,
                    "is_partial": True,
                    "same_actual_window_as": "ALL_AVAILABLE",
                    "is_summary_eligible": False,
                    "insufficient_reason": "account history starts after requested period start",
                },
                "simple_benchmarks": [],
                "cashflow_benchmarks": [],
            }
        )
    periods.append(
        {
            "period": "ALL",
            "requested_start_date": "2026-04-13",
            "start_date": "2026-04-13",
            "end_date": "2026-05-07",
            "partial": False,
            "actual_return": 0.2,
            "primary_return_method": "available_history_simple_nav",
            "simple_benchmarks": [{"benchmark": "KOSPI", "benchmark_return": 0.1, "excess_return": 0.1, "excess_krw": 100000}],
            "cashflow_benchmarks": [],
            "best_excess": {"benchmark": "KOSPI", "excess_return": 0.1, "excess_krw": 100000},
            "worst_excess": {"benchmark": "KOSPI", "excess_return": 0.1, "excess_krw": 100000},
            "period_coverage": {"period": "ALL", "is_summary_eligible": True, "coverage_ratio": 1.0},
        }
    )
    performance_payload = {
        "status": "ok",
        "market_scope": "KR",
        "benchmarks": ["KOSPI"],
        "summary": {
            "default_period": "ALL_AVAILABLE",
            "source_period": "ALL",
            "default_period_label": "사용 가능 전체 기간",
            "start_date": "2026-04-13",
            "end_date": "2026-05-07",
            "actual_return": 0.2,
            "primary_return_method": "available_history_simple_nav",
            "best_excess": {"benchmark": "KOSPI", "excess_return": 0.1, "excess_krw": 100000},
            "worst_excess": {"benchmark": "KOSPI", "excess_return": 0.1, "excess_krw": 100000},
            "period_coverage": {"coverage_ratio": 1.0},
        },
        "periods": periods,
        "chart_data": {"benchmarks": ["KOSPI"], "series": []},
        "costs": {},
        "contribution_by_ticker": [],
        "reconciliation": {"reconciliation_status": "OK"},
        "data_quality": {
            "snapshot_count": 2,
            "ledger_event_count": 0,
            "benchmark_provider": "local_json",
            "warnings": ["account_performance_duplicate_actual_windows:ALL_AVAILABLE:1M,3M,6M,YTD,1Y"],
        },
    }
    performance_path = private_dir / "account_performance_public.json"
    performance_path.write_text(json.dumps(performance_payload), encoding="utf-8")
    (run_dir / "run.json").write_text(
        json.dumps(
            {
                "run_id": "20260507T090000_test",
                "label": "test",
                "status": "success",
                "started_at": "2026-05-07T09:00:00+09:00",
                "finished_at": "2026-05-07T09:05:00+09:00",
                "timezone": "Asia/Seoul",
                "settings": {"output_language": "Korean"},
                "summary": {"total_tickers": 0, "successful_tickers": 0, "failed_tickers": 0},
                "warnings": [],
                "tickers": [],
                "portfolio": {
                    "status": "success",
                    "account_performance": {"enabled": True, "publish_to_site": True, "status": "ok"},
                    "artifacts": {"account_performance_public_json": performance_path.as_posix()},
                },
            }
        ),
        encoding="utf-8",
    )

    build_site(archive, site, SiteSettings())
    public_html = (site / "runs" / "20260507T090000_test" / "portfolio.html").read_text(encoding="utf-8")

    default_section = public_html.split("기간별 원시 산출", 1)[0]
    assert "사용 가능 전체 기간" in default_section
    assert "1M (부분)" not in default_section
    assert "1M/3M/6M/YTD/1Y" in default_section
    assert "기간별 원시 산출" in public_html
    assert "1M (부분)" in public_html


def test_portfolio_page_shows_friendly_provider_fallback_and_keeps_raw_error_in_diagnostics(tmp_path: Path):
    archive = tmp_path / "archive"
    site = tmp_path / "site"
    run_dir = archive / "runs" / "2026" / "20260506T090000_test"
    private_dir = run_dir / "portfolio-private"
    private_dir.mkdir(parents=True)
    (private_dir / "status.json").write_text(json.dumps({"status": "success", "profile": "us"}), encoding="utf-8")
    raw_error = "account_performance_kis_benchmark_failed:SPY:https://openapi.koreainvestment.com/error/500"
    performance_payload = {
        "status": "ok",
        "market_scope": "US",
        "benchmarks": ["SPY", "QQQ"],
        "summary": {
            "default_period": "ALL_AVAILABLE",
            "source_period": "ALL",
            "default_period_label": "사용 가능 전체 기간",
            "start_date": "2026-04-16",
            "end_date": "2026-05-06",
            "actual_return": 0.1,
            "primary_return_method": "available_history_simple_nav",
            "best_excess": {"benchmark": "SPY", "excess_return": 0.02, "excess_krw": 20000},
            "worst_excess": {"benchmark": "QQQ", "excess_return": -0.01, "excess_krw": -10000},
            "period_coverage": {"coverage_ratio": 1.0},
        },
        "periods": [
            {
                "period": "ALL",
                "start_date": "2026-04-16",
                "end_date": "2026-05-06",
                "actual_return": 0.1,
                "primary_return_method": "available_history_simple_nav",
                "simple_benchmarks": [],
                "cashflow_benchmarks": [],
            }
        ],
        "chart_data": {"benchmarks": ["SPY"], "series": []},
        "costs": {},
        "contribution_by_ticker": [],
        "reconciliation": {"reconciliation_status": "OK"},
        "data_quality": {
            "snapshot_count": 2,
            "ledger_event_count": 0,
            "benchmark_provider": "yfinance",
            "benchmark_provider_status": {
                "SPY": {"preferred_provider": "kis", "used_provider": "yfinance", "status": "fallback", "warnings": ["kis_failed:500"]},
                "QQQ": {"preferred_provider": "kis", "used_provider": "yfinance", "status": "fallback", "warnings": ["kis_failed:500"]},
            },
            "warnings": [raw_error],
        },
    }
    performance_path = private_dir / "account_performance_public.json"
    performance_path.write_text(json.dumps(performance_payload), encoding="utf-8")
    (run_dir / "run.json").write_text(
        json.dumps(
            {
                "run_id": "20260506T090000_test",
                "label": "test",
                "status": "success",
                "started_at": "2026-05-06T09:00:00+09:00",
                "finished_at": "2026-05-06T09:05:00+09:00",
                "timezone": "Asia/Seoul",
                "settings": {"output_language": "Korean"},
                "summary": {"total_tickers": 0, "successful_tickers": 0, "failed_tickers": 0},
                "warnings": [],
                "tickers": [],
                "portfolio": {
                    "status": "success",
                    "account_performance": {"enabled": True, "publish_to_site": True, "status": "ok"},
                    "artifacts": {"account_performance_public_json": performance_path.as_posix()},
                },
            }
        ),
        encoding="utf-8",
    )

    build_site(archive, site, SiteSettings())
    public_html = (site / "runs" / "20260506T090000_test" / "portfolio.html").read_text(encoding="utf-8")
    investor_section = public_html.split("데이터 품질 경고", 1)[0]
    assert "SPY/QQQ 가격은 선호 provider 조회 실패 후 yfinance로 대체했습니다." in investor_section
    assert "https://openapi" not in investor_section
    assert raw_error in public_html
