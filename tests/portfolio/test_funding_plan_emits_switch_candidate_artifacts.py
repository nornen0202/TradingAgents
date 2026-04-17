from tradingagents.portfolio.account_models import (
    AccountConstraints,
    AccountSnapshot,
    InstrumentIdentity,
    PortfolioCandidate,
    PortfolioProfile,
    Position,
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


def test_funding_plan_emits_switch_candidate_artifacts():
    base_snapshot = _snapshot()
    snapshot = type(base_snapshot)(
        **{
            **base_snapshot.__dict__,
            "positions": (
                Position(
                    broker_symbol="005930",
                    canonical_ticker="005930.KS",
                    display_name="삼성전자",
                    sector="Semiconductors",
                    quantity=10,
                    available_qty=10,
                    avg_cost_krw=70000,
                    market_price_krw=75000,
                    market_value_krw=750000,
                    unrealized_pnl_krw=50000,
                ),
            ),
        }
    )
    candidates = [
        PortfolioCandidate(
            snapshot_id=snapshot.snapshot_id,
            instrument=_identity("005930.KS", "삼성전자"),
            is_held=True,
            market_value_krw=750000,
            quantity=10,
            available_qty=10,
            sector="Semiconductors",
            structured_decision=None,
            data_coverage={"company_news_count": 4, "disclosures_count": 1, "social_source": "dedicated"},
            quality_flags=tuple(),
            vendor_health={"vendor_calls": {}, "fallback_count": 0},
            suggested_action_now="HOLD",
            suggested_action_if_triggered="NONE",
            trigger_conditions=tuple(),
            confidence=0.5,
            stance="NEUTRAL",
            entry_action="WAIT",
            setup_quality="WEAK",
            rationale="유지",
            strategy_state="hold_or_watch",
        ),
        PortfolioCandidate(
            snapshot_id=snapshot.snapshot_id,
            instrument=_identity("000660.KS", "SK하이닉스"),
            is_held=False,
            market_value_krw=0,
            quantity=0,
            available_qty=0,
            sector="Semiconductors",
            structured_decision=None,
            data_coverage={"company_news_count": 4, "disclosures_count": 1, "social_source": "dedicated"},
            quality_flags=tuple(),
            vendor_health={"vendor_calls": {}, "fallback_count": 0},
            suggested_action_now="WATCH",
            suggested_action_if_triggered="STARTER_IF_TRIGGERED",
            trigger_conditions=("종가 215,500원 상회",),
            confidence=0.8,
            stance="BULLISH",
            entry_action="WAIT",
            setup_quality="COMPELLING",
            rationale="조건 확인",
            strategy_state="add_if_triggered",
        ),
    ]

    recommendation, _ = build_recommendation(
        candidates=candidates,
        snapshot=snapshot,
        batch_metrics={"entry_action_distribution": {"WAIT": 2}, "stance_distribution": {"BULLISH": 1, "NEUTRAL": 1}},
        warnings=[],
        profile=_profile(snapshot),
        report_date="2026-04-16",
    )

    funding_plan = recommendation.funding_plan
    assert "switch_candidates" in funding_plan
    assert "would_buy_if_funded" in funding_plan
    assert "trim_first_candidates" in funding_plan
