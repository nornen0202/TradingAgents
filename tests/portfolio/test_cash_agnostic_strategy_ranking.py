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
        settled_cash_krw=200_000,
        available_cash_krw=200_000,
        buying_power_krw=200_000,
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
        trigger_budget_krw=0,
        constraints=snapshot.constraints,
    )


def _candidate(snapshot_id: str, ticker: str, name: str, confidence: float) -> PortfolioCandidate:
    return PortfolioCandidate(
        snapshot_id=snapshot_id,
        instrument=_identity(ticker, name),
        is_held=False,
        market_value_krw=0,
        quantity=0,
        available_qty=0,
        sector="Semiconductors",
        structured_decision=None,
        data_coverage={"company_news_count": 3, "disclosures_count": 1, "social_source": "dedicated"},
        quality_flags=tuple(),
        vendor_health={"vendor_calls": {}, "fallback_count": 0},
        suggested_action_now="WATCH",
        suggested_action_if_triggered="ADD_IF_TRIGGERED",
        trigger_conditions=("close above breakout",),
        confidence=confidence,
        stance="BULLISH",
        entry_action="WAIT",
        setup_quality="DEVELOPING",
        rationale=f"{name} ranking candidate",
        strategy_state="add_if_triggered",
        execution_feasibility_now="not_actionable_now",
        decision_source="RULE_ONLY",
    )


def test_cash_agnostic_strategy_ranking():
    snapshot = _snapshot()
    candidates = [
        _candidate(snapshot.snapshot_id, "005930.KS", "Samsung Electronics", 0.91),
        _candidate(snapshot.snapshot_id, "000660.KS", "SK Hynix", 0.71),
    ]

    recommendation, _ = build_recommendation(
        candidates=candidates,
        snapshot=snapshot,
        batch_metrics={"entry_action_distribution": {"WAIT": 2}, "stance_distribution": {"BULLISH": 2}},
        warnings=[],
        profile=_profile(snapshot),
        report_date="2026-04-24",
    )

    ranking = recommendation.scenario_plan["cash_agnostic"]["strategy_ranking"]

    assert ranking
    assert ranking[0]["canonical_ticker"] == "005930.KS"
    assert recommendation.scenario_plan["cash_agnostic"]["label"] == "Cash-agnostic"
