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


def _action(ticker, *, relative="ADD", prism="no_prism_signal"):
    return PortfolioAction(
        canonical_ticker=ticker,
        display_name=ticker,
        priority=1,
        confidence=0.7,
        action_now="WATCH",
        delta_krw_now=0,
        target_weight_now=0.0,
        action_if_triggered="STARTER_IF_TRIGGERED",
        delta_krw_if_triggered=100_000,
        target_weight_if_triggered=0.1,
        trigger_conditions=("종가 확인",),
        rationale="조건 충족 전까지 대기합니다.",
        data_health={"prism_agreement": prism},
        portfolio_relative_action=relative,
        prism_agreement=prism,
    )


def _recommendation(actions):
    return PortfolioRecommendation(
        snapshot_id="snap",
        report_date="2026-04-30",
        account_value_krw=1_000_000,
        recommended_cash_after_now_krw=1_000_000,
        recommended_cash_after_triggered_krw=900_000,
        market_regime="mixed",
        actions=tuple(actions),
        portfolio_risks=tuple(),
        data_health_summary={},
    )


def test_investor_report_no_duplicate_sell_heading():
    markdown = render_portfolio_report_markdown(
        snapshot=_snapshot(),
        recommendation=_recommendation([_action("AAPL")]),
        candidates=[],
    )

    assert "오늘 즉시 매도/축소 후보 / 오늘 바로 매도/축소 후보" not in markdown


def test_raw_action_labels_are_localized():
    markdown = render_portfolio_report_markdown(
        snapshot=_snapshot(),
        recommendation=_recommendation([_action("AAPL", relative="ADD")]),
        candidates=[],
    )

    assert "조건부 소액 진입" in markdown
    assert " / add" not in markdown.lower()


def test_prism_no_signal_not_repeated_for_every_candidate():
    markdown = render_portfolio_report_markdown(
        snapshot=_snapshot(),
        recommendation=_recommendation([_action("AAPL"), _action("MSFT")]),
        candidates=[],
    )

    assert markdown.count("PRISM 신호 없음") == 0
    assert "이 섹션 후보들은 현재 같은 시장의 PRISM 매칭 신호가 없습니다." in markdown
