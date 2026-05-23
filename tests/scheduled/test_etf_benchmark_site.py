from __future__ import annotations

from tests.portfolio.benchmarks.helpers import build_fixture_comparison, default_settings
from tradingagents.scheduled.config import SiteSettings
from tradingagents.scheduled.site import (
    _portfolio_has_etf_benchmark_page,
    _render_etf_alternative_comparison,
    _render_etf_benchmark_page,
)


def test_etf_benchmark_site_renders_equity_curve_and_policy():
    html = _render_etf_alternative_comparison(build_fixture_comparison().to_public_dict())

    assert "동일 입금일 ETF 대체 포트폴리오 비교" in html
    assert "ETF 대체 포트폴리오 equity curve" in html
    assert "점선은 날짜별 입출금 이벤트" in html
    assert "개별 종목 비중 판단" in html
    assert "현재 권고" in html


def test_etf_benchmark_site_renders_dated_cashflow_unavailable_state():
    html = _render_etf_alternative_comparison(
        build_fixture_comparison(settings=default_settings(use_cashflows=False)).to_public_dict()
    )

    assert html == ""


def test_etf_benchmark_site_explains_actual_performance_unavailable_state():
    html = _render_etf_alternative_comparison(
        {
            "status": "actual_performance_unavailable",
            "reason": "actual_performance_unavailable",
            "actual_source": "unavailable",
            "actual": {},
            "cashflows": {"dated_flow_count": 0, "deposit_amount_krw": 0, "withdrawal_amount_krw": 0},
            "alternatives": [],
            "policy": {"mode": "report_only", "status": "INSUFFICIENT_DATA"},
            "warnings": ["etf_alternative_actual_performance_unavailable"],
        }
    )

    assert html == ""


def test_standalone_etf_benchmark_page_uses_friendly_status_labels():
    comparison = {
        "status": "actual_performance_unavailable",
        "reason": "actual_performance_unavailable",
        "actual_source": "unavailable",
        "actual": {},
        "cashflows": {"dated_flow_count": 0},
        "alternatives": [],
        "warnings": ["etf_alternative_actual_performance_unavailable"],
    }
    html = _render_etf_benchmark_page(
        {"run_id": "run1"},
        SiteSettings(),
        portfolio_summary={"status_class": "partial_failure", "account_performance": {"etf_alternative_comparison": comparison}},
    )

    assert "비교 데이터 없음" in html
    assert "실제 성과 출처" in html
    assert "비교 제외" in html
    assert "ETF 대체 비교 데이터가 없습니다." in html
    assert not _portfolio_has_etf_benchmark_page(
        {"account_performance": {"etf_alternative_comparison": comparison}}
    )
    assert "검증 전 참고 불가" not in html
    assert "actual_performance_unavailable</div>" not in html
    assert "Actual source" not in html
