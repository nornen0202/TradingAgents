from __future__ import annotations

import json
from pathlib import Path

from tradingagents.scheduled.config import SiteSettings
from tradingagents.scheduled.site import (
    _account_benchmark_provider_label,
    _account_performance_svg,
    _render_account_performance_section,
    build_site,
)


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
    (private_dir / "decision_audit.json").write_text(json.dumps({"account_id": "12345678-01"}), encoding="utf-8")
    (private_dir / "portfolio_semantic_verdicts.json").write_text(
        json.dumps({"verdicts": [{"broker_order_id": "ODNO-SECRET"}]}),
        encoding="utf-8",
    )
    (private_dir / "summary_image_spec.json").write_text(
        json.dumps({"account_value_krw": 42_000_000}),
        encoding="utf-8",
    )
    (private_dir / "broker_performance_raw.json").write_text(json.dumps({"tot_rlzt_pfls": "1234"}), encoding="utf-8")
    (private_dir / "broker_performance_normalized.json").write_text(
        json.dumps({"raw_summary": {"tot_rlzt_pfls": "1234"}}),
        encoding="utf-8",
    )
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
                "decision_audit_json": (private_dir / "decision_audit.json").as_posix(),
                "portfolio_semantic_verdicts_json": (private_dir / "portfolio_semantic_verdicts.json").as_posix(),
                "summary_image_spec_json": (private_dir / "summary_image_spec.json").as_posix(),
                "broker_performance_raw_json": (private_dir / "broker_performance_raw.json").as_posix(),
                "broker_performance_normalized_json": (private_dir / "broker_performance_normalized.json").as_posix(),
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
    index_html = (site / "runs" / manifest["run_id"] / "index.html").read_text(encoding="utf-8")
    snapshot_download = site / "downloads" / manifest["run_id"] / "portfolio" / "account_snapshot.json"
    audit_download = site / "downloads" / manifest["run_id"] / "portfolio" / "decision_audit.json"
    semantic_download = site / "downloads" / manifest["run_id"] / "portfolio" / "portfolio_semantic_verdicts.json"
    summary_spec_download = site / "downloads" / manifest["run_id"] / "portfolio" / "summary_image_spec.json"
    broker_raw_download = site / "downloads" / manifest["run_id"] / "portfolio" / "broker_performance_raw.json"
    broker_normalized_download = (
        site / "downloads" / manifest["run_id"] / "portfolio" / "broker_performance_normalized.json"
    )
    assert "계좌 성과 vs 지수/ETF" in public_html
    assert public_html.index("TradingAgents 계좌 운용 리포트") < public_html.index("계좌 성과 vs 지수/ETF")
    assert "성과 기준 기간" in public_html
    assert "계좌 수익률" in public_html
    assert "YTD (부분)" not in public_html
    assert "데이터 부족" not in public_html
    assert "요청 기간 시작일의 계좌 스냅샷 없음" not in public_html
    assert "사용 가능 전체 기간 (부분)" in public_html
    assert "부분 산출" in public_html
    assert "기간별 원시 산출" not in public_html
    assert "데이터 품질 경고" not in public_html
    assert "사용 가능 기간 수익률" in public_html
    assert "보유/실현 손익 기여도" in public_html
    assert "KOSPI" in public_html
    assert "KOSDAQ" in public_html
    assert "account_performance_public.json" in public_html
    assert "Report vs latest intraday reanalysis" not in public_html
    assert "account_snapshot.json" not in public_html
    assert "account_snapshot.json" not in index_html
    assert "decision_audit.json" not in index_html
    assert "portfolio_semantic_verdicts.json" not in index_html
    assert "summary_image_spec.json" not in index_html
    assert "broker_performance_raw.json" not in index_html
    assert "broker_performance_normalized.json" not in index_html
    assert "12345678" not in public_html
    assert "ODNO-SECRET" not in public_html
    assert not snapshot_download.exists()
    assert not audit_download.exists()
    assert not semantic_download.exists()
    assert not summary_spec_download.exists()
    assert not broker_raw_download.exists()
    assert not broker_normalized_download.exists()
    assert (site / "downloads" / manifest["run_id"] / "portfolio" / "account_performance_public.json").exists()


def test_portfolio_page_prioritizes_broker_performance_and_hides_failed_snapshot_headline():
    payload = {
        "status": "ok",
        "market_scope": "KR",
        "benchmarks": ["KOSPI", "KOSDAQ"],
        "summary": {
            "default_period": "ALL_AVAILABLE",
            "default_period_label": "사용 가능 전체 기간",
            "start_date": "2026-04-13",
            "end_date": "2026-05-13",
            "actual_return": 1.6128,
            "simple_nav_return": 1.6128,
            "primary_return_method": "simple_nav_unadjusted",
            "return_method_warning": "broker_external_cashflow_unmodeled",
            "best_excess": {"benchmark": "KOSPI", "excess_return": 1.2, "excess_krw": 7_000_000},
            "hide_excess_headline": True,
            "show_snapshot_performance_when_unreconciled": False,
        },
        "broker_performance": {
            "broker": "kis",
            "account_scope": "KR domestic",
            "period_start": "2026-04-13",
            "period_end": "2026-05-12",
            "investment_pnl_krw": 4_552_630,
            "balance_return_pct": 12.08,
            "start_asset_krw": 2,
            "end_asset_krw": 42_218_247,
            "deposit_amount_krw": 37_665_615,
            "withdrawal_amount_krw": 0,
            "benchmark_returns": [
                {"benchmark": "KOSPI", "benchmark_return_pct": 30.45, "excess_return_pct": -18.37},
                {"benchmark": "KOSDAQ", "benchmark_return_pct": 7.83, "excess_return_pct": 4.25},
            ],
        },
        "broker_performance_comparison": {
            "comparison_status": "FAILED",
            "broker_end_asset_krw": 42_218_247,
            "tradingagents_account_value_krw": 15_813_494,
            "end_asset_delta_krw": -26_404_753,
            "end_asset_delta_pct": -62.546,
            "broker_balance_return_pct": 12.08,
            "tradingagents_simple_nav_return_pct": 161.28,
            "return_delta_pct": 149.20,
            "period_match_status": "MISMATCH",
            "scope_match_status": "MATCH",
        },
        "periods": [
            {
                "period": "ALL",
                "requested_start_date": "2026-04-13",
                "start_date": "2026-04-13",
                "end_date": "2026-05-13",
                "actual_return": 1.6128,
                "primary_return_method": "simple_nav_unadjusted",
                "return_method_warning": "broker_external_cashflow_unmodeled",
                "simple_benchmarks": [],
                "cashflow_benchmarks": [],
            }
        ],
        "chart_data": {"series": [{"date": "2026-04-13", "account_return": 0}, {"date": "2026-05-13", "account_return": 1.6128}]},
        "costs": {"fees_krw": 583, "taxes_krw": 14160, "total_cost_krw": 14743},
        "contribution_by_ticker": [
            {"ticker": "005930.KS", "display_name": "삼성전자", "total_contribution_krw": 1234}
        ],
        "reconciliation": {
            "reconciliation_status": "FAILED",
            "simple_nav_pnl_krw": 9_761_292,
            "sum_position_contribution_krw": 2_578_672,
            "external_cashflow_net_krw": 0,
            "explained_change_krw": 2_578_672,
            "cash_delta_krw": 7_000_000,
            "position_market_value_delta_krw": 2_761_292,
            "fees_taxes_krw": 14_743,
            "unexplained_difference_krw": 7_182_620,
            "resolution_actions": [
                {
                    "code": "kis_cashflow_api_gap",
                    "title": "날짜별 입출금 원장 자동화 상태",
                    "evidence": "KIS 공식 국내주식 주문/계좌 샘플에는 외부 입금/출금 원장 조회가 없습니다.",
                    "required_input": "브로커가 제공하는 날짜별 외부 입출금 API",
                    "suggested_file": "KIS API 원천 미제공: CSV/JSON은 선택적 fallback",
                }
            ],
        },
        "data_quality": {
            "snapshot_count": 2,
            "ledger_event_count": 56,
            "cashflow_event_count": 56,
            "external_capital_flow_count": 1,
            "warnings": [
                "account_performance_period_insufficient_history:YTD",
                "broker_performance_comparison:broker_end_asset_differs_from_tradingagents_account_value",
            ],
        },
    }

    html = _render_account_performance_section(
        {"run_id": "run1", "portfolio": {"account_performance": {"publish_to_site": True}}},
        {"account_performance": payload},
    )

    assert "한국투자증권 앱 기준 성과" in html
    assert "12.08%" in html
    assert "내부 스냅샷 수익률" not in html
    assert "검증 전 참고 불가" not in html
    assert "브로커 앱 기말자산과 TradingAgents 내부 계좌 평가액이 크게 다릅니다." not in html
    assert "정합성 상세" not in html
    assert "정합성 해결/자동화 상태" not in html
    assert "날짜별 입출금 원장 자동화 상태" not in html
    assert "KIS API 원천 미제공" not in html
    assert "<strong>삼성전자</strong>" not in html
    assert "<strong>005930.KS</strong>" not in html
    assert "broker_performance_comparison:broker_end_asset" not in html
    assert "account_performance_period_insufficient_history:YTD" not in html


def test_portfolio_page_renders_etf_dca_comparison_when_available():
    payload = {
        "status": "ok",
        "market_scope": "KR",
        "benchmarks": ["KOSPI", "KOSDAQ"],
        "summary": {
            "default_period": "ALL_AVAILABLE",
            "default_period_label": "사용 가능 전체 기간",
            "start_date": "2026-01-01",
            "end_date": "2026-04-01",
            "actual_return": 0.2,
            "primary_return_method": "simple_nav_unadjusted",
            "best_excess": {},
        },
        "broker_performance": {
            "broker": "kis",
            "account_scope": "KR domestic",
            "period_start": "2026-01-01",
            "period_end": "2026-04-01",
            "investment_pnl_krw": 6_000,
            "balance_return_pct": 20.0,
            "start_asset_krw": 20_000,
            "end_asset_krw": 36_000,
            "deposit_amount_krw": 10_000,
            "withdrawal_amount_krw": 0,
        },
        "etf_alternative_comparison": {
            "status": "OK",
            "period_start": "2026-01-01",
            "period_end": "2026-04-01",
            "actual_source": "broker_reported",
            "actual": {"balance_return_pct": 20.0, "investment_pnl_krw": 6_000},
            "cashflows": {"dated_flow_count": 1, "deposit_amount_krw": 10_000, "withdrawal_amount_krw": 0},
            "alternatives": [
                {
                    "key": "KOSPI200_100",
                    "label": "KOSPI200 ETF 100%",
                    "weights": {"KOSPI200": 1.0},
                    "status": "OK",
                    "end_value_krw": 42_500,
                    "investment_pnl_krw": 12_500,
                    "balance_return_pct": 41.666667,
                    "excess_return_pct": -21.666667,
                    "excess_pnl_krw": -6_500,
                    "mdd_pct": 0.0,
                },
                {
                    "key": "BLENDED",
                    "label": "혼합 벤치마크",
                    "weights": {"KOSPI200": 0.5, "SP500_KRW": 0.5},
                    "status": "OK",
                    "end_value_krw": 39_000,
                    "investment_pnl_krw": 9_000,
                    "balance_return_pct": 30.0,
                    "excess_return_pct": -10.0,
                    "excess_pnl_krw": -3_000,
                    "mdd_pct": 0.0,
                },
            ],
            "policy": {
                "mode": "report_only",
                "status": "ACTION_REQUIRED",
                "decisions": ["FREEZE_NEW_INDIVIDUAL_BUYS"],
                "checks": {
                    "three_month_consecutive_underperformance": {"status": "FAILED"},
                    "six_month_cumulative_excess": {"status": "INSUFFICIENT_DATA"},
                    "twelve_month_return_mdd_turnover": {"status": "INSUFFICIENT_DATA"},
                    "action_add_starter_vs_etf": {"status": "INSUFFICIENT_DATA"},
                },
            },
            "warnings": [],
        },
        "periods": [],
        "chart_data": {"series": []},
        "costs": {},
        "contribution_by_ticker": [],
        "reconciliation": {"reconciliation_status": "FAILED"},
        "data_quality": {"snapshot_count": 2, "warnings": []},
    }

    html = _render_account_performance_section(
        {"run_id": "run1", "portfolio": {"account_performance": {"publish_to_site": True}}},
        {"account_performance": payload},
    )

    assert "동일 입금일 ETF 대체 포트폴리오 비교" in html
    assert "KOSPI200 ETF 100%" in html
    assert "41.67%" in html
    assert "실제 대비 -10.00%" in html
    assert "FREEZE_NEW_INDIVIDUAL_BUYS" in html


def test_portfolio_page_renders_etf_dca_unavailable_without_dated_cashflows():
    payload = {
        "status": "ok",
        "summary": {"default_period": "ALL_AVAILABLE", "best_excess": {}, "hide_excess_headline": True},
        "periods": [],
        "chart_data": {"series": []},
        "costs": {},
        "contribution_by_ticker": [],
        "reconciliation": {"reconciliation_status": "FAILED"},
        "data_quality": {"warnings": []},
        "etf_alternative_comparison": {
            "status": "cashflow_dates_required",
            "period_start": "2026-04-13",
            "period_end": "2026-05-12",
            "actual_source": "broker_reported",
            "actual": {"balance_return_pct": 12.08},
            "cashflows": {
                "dated_flow_count": 0,
                "broker_deposit_amount_krw": 37_665_615,
                "missing_reason": "dated_external_capital_flows_required",
            },
            "alternatives": [],
            "policy": {"status": "INSUFFICIENT_DATA", "decisions": [], "checks": {}},
            "warnings": ["etf_alternative_cashflow_dates_required"],
        },
    }

    html = _render_account_performance_section(
        {"run_id": "run1", "portfolio": {"account_performance": {"publish_to_site": True}}},
        {"account_performance": payload},
    )

    assert html == ""


def test_build_site_generates_standalone_etf_benchmark_page(tmp_path: Path):
    archive = tmp_path / "archive"
    site = tmp_path / "site"
    run_dir = archive / "runs" / "2026" / "20260401T090000_test"
    private_dir = run_dir / "portfolio-private"
    private_dir.mkdir(parents=True)
    comparison = {
        "status": "OK",
        "period_start": "2026-01-01",
        "period_end": "2026-04-01",
        "actual_source": "broker_reported",
        "actual": {"balance_return_pct": 20.0, "investment_pnl_krw": 6_000},
        "cashflows": {"dated_flow_count": 1, "deposit_amount_krw": 10_000, "withdrawal_amount_krw": 0},
        "alternatives": [
            {
                "key": "KOSPI200_100",
                "label": "KOSPI200 ETF 100%",
                "weights": {"KOSPI200": 1.0},
                "status": "OK",
                "end_value_krw": 42_500,
                "investment_pnl_krw": 12_500,
                "balance_return_pct": 41.666667,
                "excess_return_pct": -21.666667,
                "excess_pnl_krw": -6_500,
                "mdd_pct": 0.0,
            }
        ],
        "policy": {"mode": "report_only", "status": "INSUFFICIENT_DATA", "decisions": [], "checks": {}},
        "warnings": [],
    }
    performance_payload = {
        "status": "ok",
        "summary": {"default_period": "ALL_AVAILABLE", "best_excess": {}},
        "periods": [],
        "chart_data": {"series": []},
        "costs": {},
        "contribution_by_ticker": [],
        "reconciliation": {"reconciliation_status": "OK"},
        "data_quality": {"warnings": []},
        "etf_alternative_comparison": comparison,
    }
    (private_dir / "status.json").write_text(json.dumps({"status": "success", "profile": "kr"}), encoding="utf-8")
    (private_dir / "account_performance_public.json").write_text(json.dumps(performance_payload), encoding="utf-8")
    (private_dir / "etf_dca_comparison.json").write_text(json.dumps(comparison), encoding="utf-8")
    (private_dir / "etf_dca_policy_recommendation.json").write_text(json.dumps(comparison["policy"]), encoding="utf-8")
    (run_dir / "run.json").write_text(
        json.dumps(
            {
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
                "portfolio": {"status": "success", "account_performance": {"enabled": True, "publish_to_site": True}},
            }
        ),
        encoding="utf-8",
    )

    build_site(archive, site, SiteSettings())

    run_html = (site / "runs" / "20260401T090000_test" / "index.html").read_text(encoding="utf-8")
    etf_html = (site / "runs" / "20260401T090000_test" / "etf_benchmark.html").read_text(encoding="utf-8")
    assert "etf_benchmark.html" in run_html
    assert "동일 입금일 ETF 대체 비교" in etf_html
    assert (site / "downloads" / "20260401T090000_test" / "portfolio" / "etf_dca_comparison.json").exists()


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
    assert "YTD (부분)" not in public_html
    assert "데이터 부족" not in public_html
    assert "요청 기간 시작일의 계좌 스냅샷 없음" not in public_html
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

    default_section = public_html
    assert "사용 가능 전체 기간" in default_section
    assert "1M (부분)" not in default_section
    assert "1M/3M/6M/YTD/1Y" in default_section
    assert "기간별 원시 산출" not in public_html
    assert "데이터 품질 경고" not in public_html


def test_portfolio_page_hides_provider_fallback_and_raw_error_from_investor_section(tmp_path: Path):
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
    investor_section = public_html
    assert "벤치마크 가격: SPY/QQQ = KIS 실패 후 yfinance fallback" not in investor_section
    assert "https://openapi" not in investor_section
    assert raw_error not in public_html


def test_reconciliation_failed_demotes_excess_headline():
    payload = {
        "status": "ok",
        "benchmarks": ["KOSDAQ"],
        "summary": {
            "default_period": "ALL_AVAILABLE",
            "default_period_label": "사용 가능 전체 기간",
            "start_date": "2026-04-13",
            "end_date": "2026-05-07",
            "actual_return": 0.2869,
            "primary_return_method": "available_history_twr_equivalent",
            "performance_confidence": "low",
            "hide_excess_headline": True,
            "mwr_unavailable_reason": "no_external_capital_flows_for_irr",
            "best_excess": {"benchmark": "KOSDAQ", "excess_return": 1.6107, "excess_krw": 12_345_678},
            "worst_excess": {"benchmark": "KOSDAQ", "excess_return": 1.6107, "excess_krw": 12_345_678},
            "period_coverage": {"coverage_ratio": 1.0},
        },
        "periods": [
            {
                "period": "ALL",
                "start_date": "2026-04-13",
                "end_date": "2026-05-07",
                "actual_return": 0.2869,
                "primary_return_method": "available_history_twr_equivalent",
                "simple_benchmarks": [
                    {"benchmark": "KOSDAQ", "benchmark_return": -1.3238, "excess_return": 1.6107, "excess_krw": 12_345_678}
                ],
                "cashflow_benchmarks": [],
            }
        ],
        "chart_data": {"benchmarks": [], "series": []},
        "costs": {},
        "contribution_by_ticker": [],
        "reconciliation": {
            "reconciliation_status": "FAILED",
            "reconciliation_severity": "critical",
            "unexplained_difference_pct_of_nav": 0.22,
        },
        "data_quality": {"snapshot_count": 2, "ledger_event_count": 0, "warnings": []},
    }

    html = _render_account_performance_section(
        {"run_id": "run1", "portfolio": {"account_performance": {"publish_to_site": True}}},
        {"account_performance": payload},
    )
    assert html == ""


def test_chart_peak_return_labeled_as_peak_not_headline():
    html = _account_performance_svg(
        {
            "title": "사용 가능 기간 수익률",
            "benchmarks": [],
            "final_return": 1.7048,
            "peak_return": 1.8922,
            "max_drawdown": -0.1145,
            "consistency_status": "ok",
            "series": [
                {"date": "2026-04-13", "account_return": 0.0},
                {"date": "2026-04-25", "account_return": 1.8922},
                {"date": "2026-05-07", "account_return": 1.7048},
            ],
        }
    )

    assert "최종 수익률: 170.48%" in html
    assert "기간 중 최고 수익률: 189.22%" in html
    assert "최대 낙폭: -11.45%" in html
    assert "189.22%0.00%" not in html
    assert "<text" not in html
    assert "aria-hidden='true'" in html


def test_benchmark_provider_label_uses_actual_provider_status():
    label = _account_benchmark_provider_label(
        {
            "benchmark_provider": "yfinance",
            "benchmark_provider_status": {
                "KOSPI": {"preferred_provider": "kis", "used_provider": "kis", "status": "ok"},
                "KOSDAQ": {"preferred_provider": "kis", "used_provider": "kis", "status": "ok"},
            },
        }
    )

    assert label == "KOSPI/KOSDAQ=kis"
    assert "yfinance" not in label
