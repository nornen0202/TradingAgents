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
        as_of="2026-04-24T10:45:00+09:00",
        broker="manual",
        account_id="test",
        currency="KRW",
        settled_cash_krw=5_000_000,
        available_cash_krw=5_000_000,
        buying_power_krw=5_000_000,
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
        allow_intraday_pilot=True,
    )


def test_pilot_ready_count_matches_action_table():
    snapshot = _snapshot()
    candidate = PortfolioCandidate(
        snapshot_id=snapshot.snapshot_id,
        instrument=_identity("278470.KS", "APR"),
        is_held=False,
        market_value_krw=0,
        quantity=0,
        available_qty=0,
        sector="Consumer",
        structured_decision=None,
        data_coverage={"company_news_count": 2, "disclosures_count": 1, "social_source": "dedicated"},
        quality_flags=tuple(),
        vendor_health={"vendor_calls": {}, "fallback_count": 0},
        suggested_action_now="STARTER_NOW",
        suggested_action_if_triggered="STARTER_IF_TRIGGERED",
        trigger_conditions=("breakout above 100",),
        confidence=0.86,
        stance="BULLISH",
        entry_action="WAIT",
        setup_quality="DEVELOPING",
        rationale="pilot candidate",
        strategy_state="add_if_triggered",
        execution_feasibility_now="executable_now",
        decision_source="RULE_ONLY",
        timing_readiness=1.0,
        data_health={
            "execution_timing_state": "PILOT_READY",
            "execution_data_quality": "REALTIME_EXECUTION_READY",
            "session_vwap_ok": True,
            "relative_volume_ok": True,
        },
    )

    recommendation, _ = build_recommendation(
        candidates=[candidate],
        snapshot=snapshot,
        batch_metrics={"entry_action_distribution": {"WAIT": 1}, "stance_distribution": {"BULLISH": 1}},
        warnings=[],
        profile=_profile(snapshot),
        report_date="2026-04-24",
    )

    actionable_pilots = [
        action
        for action in recommendation.actions
        if action.action_now in {"STARTER_NOW", "ADD_NOW"}
        and str(action.data_health.get("execution_timing_state") or "").upper() == "PILOT_READY"
    ]
    assert recommendation.candidate_counts["pilot_ready_count"] == len(actionable_pilots) == 1
