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
        exchange="KRX",
        country="KR",
        currency="KRW",
    )


def _snapshot() -> AccountSnapshot:
    constraints = AccountConstraints(min_cash_buffer_krw=2_500_000, min_trade_krw=100_000)
    return AccountSnapshot(
        snapshot_id="snap",
        as_of="2026-04-24T11:00:00+09:00",
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
        trigger_budget_krw=300_000,
        constraints=snapshot.constraints,
    )


def test_stale_triggerable_not_erased():
    snapshot = _snapshot()
    candidate = PortfolioCandidate(
        snapshot_id=snapshot.snapshot_id,
        instrument=_identity("064400.KS", "LG CNS"),
        is_held=False,
        market_value_krw=0,
        quantity=0,
        available_qty=0,
        sector="IT Services",
        structured_decision=None,
        data_coverage={"company_news_count": 2, "disclosures_count": 1, "social_source": "dedicated"},
        quality_flags=("stale_market_data",),
        vendor_health={"vendor_calls": {}, "fallback_count": 0},
        suggested_action_now="WATCH",
        suggested_action_if_triggered="STARTER_IF_TRIGGERED",
        trigger_conditions=("close above 80",),
        confidence=0.75,
        stance="BULLISH",
        entry_action="WAIT",
        setup_quality="DEVELOPING",
        rationale="stale but still strategically valid",
        strategy_state="add_if_triggered",
        execution_feasibility_now="blocked_stale_or_degraded_data",
        stale_but_triggerable=True,
        decision_source="RULE_ONLY",
        data_health={"execution_timing_state": "STALE_TRIGGERABLE"},
    )

    recommendation, _ = build_recommendation(
        candidates=[candidate],
        snapshot=snapshot,
        batch_metrics={"entry_action_distribution": {"WAIT": 1}, "stance_distribution": {"BULLISH": 1}},
        warnings=[],
        profile=_profile(snapshot),
        report_date="2026-04-24",
    )

    action = recommendation.actions[0]
    assert action.action_if_triggered == "STARTER_IF_TRIGGERED"
    assert action.stale_but_triggerable is True
    assert recommendation.candidate_counts["strategic_trigger_candidates_count"] == 1
