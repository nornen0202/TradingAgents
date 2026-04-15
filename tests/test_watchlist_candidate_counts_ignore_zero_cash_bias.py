from tradingagents.portfolio.account_models import (
    AccountSnapshot,
    InstrumentIdentity,
    PortfolioAction,
    PortfolioCandidate,
    PortfolioRecommendation,
)
from tradingagents.portfolio.reporting import render_portfolio_report_markdown


def _identity() -> InstrumentIdentity:
    return InstrumentIdentity(
        broker_symbol="AAPL",
        canonical_ticker="AAPL",
        yahoo_symbol="AAPL",
        krx_code=None,
        dart_corp_code=None,
        display_name="Apple",
        exchange="NASDAQ",
        country="US",
        currency="USD",
    )


def test_triggerable_count_includes_zero_delta_candidates():
    snapshot = AccountSnapshot(
        snapshot_id="s1",
        as_of="2026-04-15T00:00:00+09:00",
        broker="watchlist",
        account_id="w1",
        currency="KRW",
        settled_cash_krw=0,
        available_cash_krw=0,
        buying_power_krw=0,
        total_equity_krw=0,
        snapshot_health="WATCHLIST_ONLY",
    )
    action = PortfolioAction(
        canonical_ticker="AAPL",
        display_name="Apple",
        priority=1,
        confidence=0.7,
        action_now="WATCH",
        delta_krw_now=0,
        target_weight_now=0.0,
        action_if_triggered="STARTER_IF_TRIGGERED",
        delta_krw_if_triggered=0,
        target_weight_if_triggered=0.0,
        trigger_conditions=("breakout",),
        rationale="watch",
        data_health={},
        decision_source="RULE_ONLY",
    )
    recommendation = PortfolioRecommendation(
        snapshot_id="s1",
        report_date="2026-04-15",
        account_value_krw=0,
        recommended_cash_after_now_krw=0,
        recommended_cash_after_triggered_krw=0,
        market_regime="wait_and_watch",
        actions=(action,),
        portfolio_risks=tuple(),
        data_health_summary={},
    )
    candidate = PortfolioCandidate(
        snapshot_id="s1",
        instrument=_identity(),
        is_held=False,
        market_value_krw=0,
        quantity=0,
        available_qty=0,
        sector=None,
        structured_decision=None,
        data_coverage={},
        quality_flags=tuple(),
        vendor_health={},
        suggested_action_now="WATCH",
        suggested_action_if_triggered="STARTER_IF_TRIGGERED",
        trigger_conditions=("breakout",),
        confidence=0.7,
        stance="BULLISH",
        entry_action="WAIT",
        setup_quality="DEVELOPING",
        rationale="watch",
    )
    markdown = render_portfolio_report_markdown(
        snapshot=snapshot,
        recommendation=recommendation,
        candidates=[candidate],
    )
    assert "조건부 실행 후보: 1개" in markdown
    assert "조건부 실행 예산 반영 후보: 0개" in markdown
    assert "트리거형 후보(현금과 무관): 1개" in markdown
