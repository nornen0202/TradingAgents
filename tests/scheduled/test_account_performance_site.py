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
    assert "ALL (부분)" in public_html
    assert "부분 산출" in public_html
    assert "KOSPI" in public_html
    assert "KOSDAQ" in public_html
    assert "account_performance_public.json" in public_html
    assert "account_snapshot.json" not in public_html
    assert "12345678" not in public_html
    assert "ODNO-SECRET" not in public_html
    assert "12345678" not in published_snapshot
    assert "ODNO-SECRET" not in published_snapshot
    assert (site / "downloads" / manifest["run_id"] / "portfolio" / "account_performance_public.json").exists()
