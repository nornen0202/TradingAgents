from tradingagents.portfolio.account_models import (
    AccountConstraints,
    AccountSnapshot,
    InstrumentIdentity,
    PortfolioCandidate,
    PortfolioProfile,
    Position,
)
from tradingagents.portfolio.allocation import build_recommendation
from tradingagents.portfolio.reporting import render_portfolio_report_markdown


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


def _snapshot(*, cash: int = 5_000_000, positions=()) -> AccountSnapshot:
    constraints = AccountConstraints(min_cash_buffer_krw=2_500_000, min_trade_krw=100_000)
    return AccountSnapshot(
        snapshot_id="snap",
        as_of="2026-04-17T14:00:00+09:00",
        broker="manual",
        account_id="test",
        currency="KRW",
        settled_cash_krw=cash,
        available_cash_krw=cash,
        buying_power_krw=cash,
        total_equity_krw=cash + sum(position.market_value_krw for position in positions),
        constraints=constraints,
        positions=tuple(positions),
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
        intraday_pilot_max_krw=600_000,
        intraday_pilot_min_time_kst="10:30",
    )


def test_intraday_pilot_rule_emits_small_starter_only():
    snapshot = _snapshot(cash=5_000_000)
    candidate = PortfolioCandidate(
        snapshot_id=snapshot.snapshot_id,
        instrument=_identity("064400.KS", "LG CNS"),
        is_held=False,
        market_value_krw=0,
        quantity=0,
        available_qty=0,
        sector="IT Services",
        structured_decision=None,
        data_coverage={"company_news_count": 3, "disclosures_count": 1, "social_source": "dedicated"},
        quality_flags=tuple(),
        vendor_health={"vendor_calls": {}, "fallback_count": 0},
        suggested_action_now="STARTER_NOW",
        suggested_action_if_triggered="ADD_IF_TRIGGERED",
        trigger_conditions=("장중 trigger 상회 + VWAP 위",),
        confidence=0.85,
        stance="BULLISH",
        entry_action="STARTER",
        setup_quality="COMPELLING",
        rationale="장중 조건 충족 시 소액 starter만 허용합니다.",
        strategy_state="add_now",
        execution_feasibility_now="executable_now",
        data_health={
            "session_vwap_ok": True,
            "relative_volume_ok": True,
            "execution_timing_state": "SUPPORT_HOLD",
        },
    )

    recommendation, _ = build_recommendation(
        candidates=[candidate],
        snapshot=snapshot,
        batch_metrics={"entry_action_distribution": {"STARTER": 1}, "stance_distribution": {"BULLISH": 1}},
        warnings=[],
        profile=_profile(snapshot),
        report_date="2026-04-17",
    )

    action = recommendation.actions[0]
    assert action.action_now == "STARTER_NOW"
    assert 300_000 <= action.delta_krw_now <= 600_000


def test_switch_scenario_generates_buy_and_trim_lists():
    held = Position(
        broker_symbol="005930",
        canonical_ticker="005930.KS",
        display_name="삼성전자",
        sector="Semiconductors",
        quantity=20,
        available_qty=20,
        avg_cost_krw=70_000,
        market_price_krw=75_000,
        market_value_krw=1_500_000,
        unrealized_pnl_krw=100_000,
    )
    snapshot = _snapshot(cash=1_000_000, positions=(held,))
    candidates = [
        PortfolioCandidate(
            snapshot_id=snapshot.snapshot_id,
            instrument=_identity("005930.KS", "삼성전자"),
            is_held=True,
            market_value_krw=1_500_000,
            quantity=20,
            available_qty=20,
            sector="Semiconductors",
            structured_decision=None,
            data_coverage={"company_news_count": 3, "disclosures_count": 1, "social_source": "dedicated"},
            quality_flags=tuple(),
            vendor_health={"vendor_calls": {}, "fallback_count": 0},
            suggested_action_now="HOLD",
            suggested_action_if_triggered="NONE",
            trigger_conditions=tuple(),
            confidence=0.45,
            stance="NEUTRAL",
            entry_action="WAIT",
            setup_quality="WEAK",
            rationale="강한 후보 재배치를 위해 먼저 줄일 후보입니다.",
            strategy_state="hold_or_watch",
        ),
        PortfolioCandidate(
            snapshot_id=snapshot.snapshot_id,
            instrument=_identity("064400.KS", "LG CNS"),
            is_held=False,
            market_value_krw=0,
            quantity=0,
            available_qty=0,
            sector="IT Services",
            structured_decision=None,
            data_coverage={"company_news_count": 5, "disclosures_count": 1, "social_source": "dedicated"},
            quality_flags=tuple(),
            vendor_health={"vendor_calls": {}, "fallback_count": 0},
            suggested_action_now="WATCH",
            suggested_action_if_triggered="STARTER_IF_TRIGGERED",
            trigger_conditions=("종가 trigger 상회",),
            confidence=0.85,
            stance="BULLISH",
            entry_action="WAIT",
            setup_quality="COMPELLING",
            rationale="조건 충족 시 우선 늘릴 후보입니다.",
            strategy_state="add_if_triggered",
        ),
    ]

    recommendation, _ = build_recommendation(
        candidates=candidates,
        snapshot=snapshot,
        batch_metrics={"entry_action_distribution": {"WAIT": 2}, "stance_distribution": {"BULLISH": 1, "NEUTRAL": 1}},
        warnings=[],
        profile=_profile(snapshot),
        report_date="2026-04-17",
    )

    switch = recommendation.scenario_plan["switch"]
    assert switch["would_buy_if_funded"]
    assert switch["would_trim_first"]
    assert recommendation.funding_plan["would_buy_if_funded"]
    assert recommendation.funding_plan["trim_first_candidates"]


def test_portfolio_report_rationales_are_korean():
    snapshot = _snapshot(cash=1_000_000)
    candidate = PortfolioCandidate(
        snapshot_id=snapshot.snapshot_id,
        instrument=_identity("064400.KS", "LG CNS"),
        is_held=False,
        market_value_krw=0,
        quantity=0,
        available_qty=0,
        sector="IT Services",
        structured_decision=None,
        data_coverage={"company_news_count": 5, "disclosures_count": 1, "social_source": "dedicated"},
        quality_flags=tuple(),
        vendor_health={"vendor_calls": {}, "fallback_count": 0},
        suggested_action_now="WATCH",
        suggested_action_if_triggered="STARTER_IF_TRIGGERED",
        trigger_conditions=("종가 trigger 상회",),
        confidence=0.8,
        stance="BULLISH",
        entry_action="WAIT",
        setup_quality="COMPELLING",
        rationale="조건 충족 전까지 대기합니다.",
        strategy_state="add_if_triggered",
    )

    recommendation, scored = build_recommendation(
        candidates=[candidate],
        snapshot=snapshot,
        batch_metrics={"entry_action_distribution": {"WAIT": 1}, "stance_distribution": {"BULLISH": 1}},
        warnings=[],
        profile=_profile(snapshot),
        report_date="2026-04-17",
    )
    markdown = render_portfolio_report_markdown(snapshot=snapshot, recommendation=recommendation, candidates=scored)

    assert "conditions met" not in markdown.lower()
    assert "조건" in markdown

