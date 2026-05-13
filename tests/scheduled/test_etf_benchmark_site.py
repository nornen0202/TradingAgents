from __future__ import annotations

from tests.portfolio.benchmarks.helpers import build_fixture_comparison, default_settings
from tradingagents.scheduled.site import _render_etf_alternative_comparison


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

    assert "입금일 원장 필요" in html
    assert "정확한 적립식 ETF 비교를 제공하지 않습니다" in html
