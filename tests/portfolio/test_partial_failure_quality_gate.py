from tradingagents.portfolio.account_models import AccountConstraints, AccountSnapshot, PortfolioAction, PortfolioRecommendation
from tradingagents.portfolio.reporting import render_portfolio_report_markdown


def _snapshot():
    return AccountSnapshot(
        snapshot_id="snap",
        as_of="2026-04-30T15:00:00+09:00",
        broker="manual",
        account_id="test",
        currency="KRW",
        settled_cash_krw=1_000_000,
        available_cash_krw=1_000_000,
        buying_power_krw=1_000_000,
        total_equity_krw=1_000_000,
        constraints=AccountConstraints(min_cash_buffer_krw=100_000),
    )


def _action(ticker="AAPL", *, now="WATCH", delta=0):
    return PortfolioAction(
        canonical_ticker=ticker,
        display_name=ticker,
        priority=1,
        confidence=0.3,
        action_now=now,
        delta_krw_now=delta,
        target_weight_now=0.0,
        action_if_triggered="NONE",
        delta_krw_if_triggered=0,
        target_weight_if_triggered=0.0,
        trigger_conditions=tuple(),
        rationale="재분석 필요",
        data_health={"reanalysis_required": True, "reanalysis_reason": "decision payload missing required fields"},
        portfolio_relative_action="WATCH",
    )


def _recommendation():
    return PortfolioRecommendation(
        snapshot_id="snap",
        report_date="2026-04-30",
        account_value_krw=1_000_000,
        recommended_cash_after_now_krw=1_000_000,
        recommended_cash_after_triggered_krw=1_000_000,
        market_regime="mixed",
        actions=(_action("COST"),),
        portfolio_risks=tuple(),
        data_health_summary={
            "partial_failure_rate": 0.42,
            "partial_failure_warning": True,
            "reanalysis_required_tickers": [
                {"ticker": "COST", "reason": "decision payload missing required fields"},
                {"ticker": "ETN", "reason": "decision payload missing required fields"},
            ],
        },
    )


def test_partial_failure_report_adds_warning():
    markdown = render_portfolio_report_markdown(snapshot=_snapshot(), recommendation=_recommendation(), candidates=[])

    assert "이 리포트는 부분 실패가 큽니다" in markdown


def test_failed_decisions_not_actionable():
    markdown = render_portfolio_report_markdown(snapshot=_snapshot(), recommendation=_recommendation(), candidates=[])

    assert "### 오늘 바로 매수 후보\n- 없음" in markdown
    assert "### 오늘 바로 매도/축소 후보\n- 없음" in markdown


def test_failed_tickers_listed_for_rerun():
    markdown = render_portfolio_report_markdown(snapshot=_snapshot(), recommendation=_recommendation(), candidates=[])

    assert "## 재분석 필요 종목" in markdown
    assert "- COST: decision payload missing required fields" in markdown
    assert "- ETN: decision payload missing required fields" in markdown
