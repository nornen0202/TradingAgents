from tradingagents.portfolio.account_models import (
    AccountConstraints,
    AccountSnapshot,
    InstrumentIdentity,
    PortfolioCandidate,
    PortfolioProfile,
)
from tradingagents.portfolio.allocation import build_recommendation


def _identity(ticker: str, name: str) -> InstrumentIdentity:
    return InstrumentIdentity(
        broker_symbol=ticker.split(".")[0],
        canonical_ticker=ticker,
        yahoo_symbol=ticker,
        krx_code=ticker.split(".")[0],
        dart_corp_code=None,
        display_name=name,
        exchange="NASDAQ",
        country="US",
        currency="USD",
    )


def _snapshot() -> AccountSnapshot:
    constraints = AccountConstraints(min_cash_buffer_krw=2_500_000, min_trade_krw=100_000)
    return AccountSnapshot(
        snapshot_id="snap",
        as_of="2026-04-16T09:16:00+09:00",
        broker="manual",
        account_id="test",
        currency="KRW",
        settled_cash_krw=1_000_000,
        available_cash_krw=1_000_000,
        buying_power_krw=1_000_000,
        constraints=constraints,
    )


def _profile(snapshot: AccountSnapshot) -> PortfolioProfile:
    return PortfolioProfile(
        name="test",
        enabled=True,
        broker="manual",
        broker_environment="real",
        read_only=True,
        account_no=None,
        product_code=None,
        manual_snapshot_path=None,
        csv_positions_path=None,
        private_output_dirname="private",
        watch_tickers=tuple(),
        trigger_budget_krw=500_000,
        constraints=snapshot.constraints,
    )


def test_actionable_now_propagates_to_immediate_candidate_or_budget_blocked_bucket():
    snapshot = _snapshot()
    candidate = PortfolioCandidate(
        snapshot_id=snapshot.snapshot_id,
        instrument=_identity("NVDA", "NVIDIA"),
        is_held=False,
        market_value_krw=0,
        quantity=0,
        available_qty=0,
        sector="Semiconductors",
        structured_decision=None,
        data_coverage={"company_news_count": 3, "disclosures_count": 0, "social_source": "dedicated"},
        quality_flags=tuple(),
        vendor_health={"vendor_calls": {}, "fallback_count": 0},
        suggested_action_now="STARTER_NOW",
        suggested_action_if_triggered="NONE",
        trigger_conditions=tuple(),
        confidence=0.8,
        stance="BULLISH",
        entry_action="STARTER",
        setup_quality="COMPELLING",
        rationale="지금 바로 검토",
        strategy_state="add_now",
        execution_feasibility_now="actionable_now",
    )

    recommendation, _ = build_recommendation(
        candidates=[candidate],
        snapshot=snapshot,
        batch_metrics={"entry_action_distribution": {"STARTER": 1}, "stance_distribution": {"BULLISH": 1}},
        warnings=[],
        profile=_profile(snapshot),
        report_date="2026-04-16",
    )

    counts = recommendation.candidate_counts
    assert counts["immediate_actionable_count"] == 1
    assert counts["immediate_budgeted_count"] == 0
    assert counts["budget_blocked_actionable_count"] == 1
