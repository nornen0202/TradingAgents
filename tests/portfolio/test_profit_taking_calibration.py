from tradingagents.portfolio.account_models import (
    AccountConstraints,
    AccountSnapshot,
    InstrumentIdentity,
    PortfolioCandidate,
    PortfolioProfile,
    Position,
)
from tradingagents.portfolio.allocation import build_recommendation


def _identity() -> InstrumentIdentity:
    return InstrumentIdentity(
        broker_symbol="005930",
        canonical_ticker="005930.KS",
        yahoo_symbol="005930.KS",
        krx_code="005930",
        dart_corp_code=None,
        display_name="Samsung Electronics",
        exchange="KRX",
        country="KR",
        currency="KRW",
    )


def _snapshot() -> AccountSnapshot:
    position = Position(
        broker_symbol="005930",
        canonical_ticker="005930.KS",
        display_name="Samsung Electronics",
        sector="Technology",
        quantity=10,
        available_qty=10,
        avg_cost_krw=70000,
        market_price_krw=100000,
        market_value_krw=1000000,
        unrealized_pnl_krw=300000,
    )
    return AccountSnapshot(
        snapshot_id="snap",
        as_of="2026-04-24T10:30:00+09:00",
        broker="manual",
        account_id="test",
        currency="KRW",
        settled_cash_krw=1000000,
        available_cash_krw=1000000,
        buying_power_krw=1000000,
        total_equity_krw=2000000,
        constraints=AccountConstraints(min_cash_buffer_krw=100000, min_trade_krw=100000),
        positions=(position,),
    )


def _profile(snapshot: AccountSnapshot) -> PortfolioProfile:
    return PortfolioProfile(
        name="test",
        enabled=True,
        broker="manual",
        broker_environment="paper",
        read_only=True,
        account_no=None,
        product_code=None,
        manual_snapshot_path=None,
        csv_positions_path=None,
        private_output_dirname="portfolio-private",
        watch_tickers=tuple(),
        trigger_budget_krw=500000,
        constraints=snapshot.constraints,
        profit_take_stage1_fraction=0.50,
        profit_take_keep_core_fraction=0.80,
    )


def test_take_profit_now_uses_plan_fraction_capped_by_keep_core():
    snapshot = _snapshot()
    candidate = PortfolioCandidate(
        snapshot_id="snap",
        instrument=_identity(),
        is_held=True,
        market_value_krw=1000000,
        quantity=10,
        available_qty=10,
        sector="Technology",
        structured_decision=None,
        data_coverage={"company_news_count": 1, "disclosures_count": 0, "social_source": "dedicated", "macro_items_count": 1},
        quality_flags=tuple(),
        vendor_health={"vendor_calls": {}, "fallback_count": 0},
        suggested_action_now="TAKE_PROFIT_NOW",
        suggested_action_if_triggered="NONE",
        trigger_conditions=tuple(),
        confidence=0.8,
        stance="BULLISH",
        entry_action="WAIT",
        setup_quality="DEVELOPING",
        rationale="Protect extended profit.",
        portfolio_relative_action="TAKE_PROFIT",
        risk_action="TAKE_PROFIT",
        sell_intent="TAKE_PROFIT",
        sell_trigger_status="NOW",
        sell_size_plan="CUSTOM",
        thesis_after_sell="MAINTAIN",
        position_metrics={"unrealized_return_pct": 42.8571, "profit_protection_score": 0.8},
        profit_taking_plan={
            "enabled": True,
            "stage_1_price": 100000,
            "stage_1_fraction": 0.50,
            "keep_core_fraction": 0.80,
            "reason_codes": ["PROFIT_TAKING"],
        },
        score_now=0.9,
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
    assert action.delta_krw_now == -199999 or action.delta_krw_now == -200000
    assert action.profit_taking_plan["stage_1_fraction"] == 0.50
    assert action.sell_intent == "TAKE_PROFIT"
