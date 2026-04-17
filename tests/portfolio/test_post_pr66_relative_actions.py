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


def _identity(ticker: str, name: str, *, sector: str = "Technology") -> InstrumentIdentity:
    return InstrumentIdentity(
        broker_symbol=ticker,
        canonical_ticker=ticker,
        yahoo_symbol=ticker,
        krx_code=None,
        dart_corp_code=None,
        display_name=name,
        exchange="NASDAQ",
        country="US",
        currency="USD",
    )


def _snapshot(*, cash: int = 100_000, positions=()) -> AccountSnapshot:
    constraints = AccountConstraints(min_cash_buffer_krw=1_000_000, min_trade_krw=100_000)
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


def _profile(snapshot: AccountSnapshot, *, allow_pilot: bool = False) -> PortfolioProfile:
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
        trigger_budget_krw=600_000,
        constraints=snapshot.constraints,
        allow_intraday_pilot=allow_pilot,
        intraday_pilot_require_vwap=True,
        intraday_pilot_require_adjusted_rvol=True,
        intraday_pilot_min_time_kst="10:30",
    )


def _candidate(
    ticker: str,
    name: str,
    *,
    is_held: bool,
    action_now: str,
    action_if_triggered: str,
    stance: str = "BULLISH",
    entry_action: str = "WAIT",
    setup_quality: str = "DEVELOPING",
    confidence: float = 0.7,
    sector: str = "Technology",
    data_health=None,
    quality_flags=(),
) -> PortfolioCandidate:
    return PortfolioCandidate(
        snapshot_id="snap",
        instrument=_identity(ticker, name, sector=sector),
        is_held=is_held,
        market_value_krw=1_500_000 if is_held else 0,
        quantity=10 if is_held else 0,
        available_qty=10 if is_held else 0,
        sector=sector,
        structured_decision=None,
        data_coverage={"company_news_count": 3, "disclosures_count": 0, "social_source": "dedicated"},
        quality_flags=tuple(quality_flags),
        vendor_health={"vendor_calls": {}, "fallback_count": 0},
        suggested_action_now=action_now,
        suggested_action_if_triggered=action_if_triggered,
        trigger_conditions=("close above trigger",) if action_if_triggered != "NONE" else tuple(),
        confidence=confidence,
        stance=stance,
        entry_action=entry_action,
        setup_quality=setup_quality,
        rationale="조건 충족 전까지 대기합니다.",
        strategy_state="add_if_triggered" if action_if_triggered != "NONE" else "hold_or_watch",
        execution_feasibility_now="executable_now" if action_now in {"ADD_NOW", "STARTER_NOW"} else "not_actionable_now",
        data_health=data_health or {},
    )


def test_budget_blocked_actionable_is_counted():
    snapshot = _snapshot(cash=100_000)
    candidate = _candidate(
        "NVDA",
        "NVIDIA",
        is_held=False,
        action_now="ADD_NOW",
        action_if_triggered="NONE",
        entry_action="ADD",
        setup_quality="COMPELLING",
        confidence=0.9,
    )

    recommendation, _ = build_recommendation(
        candidates=[candidate],
        snapshot=snapshot,
        batch_metrics={"entry_action_distribution": {"ADD": 1}, "stance_distribution": {"BULLISH": 1}},
        warnings=[],
        profile=_profile(snapshot),
        report_date="2026-04-17",
    )

    assert recommendation.candidate_counts["immediate_actionable_count"] == 1
    assert recommendation.candidate_counts["immediate_budget_blocked_count"] == 1
    assert recommendation.actions[0].budget_blocked_actionable is True


def test_trim_to_fund_promoted_to_main_action_table():
    held = Position(
        broker_symbol="GLDM",
        canonical_ticker="GLDM",
        display_name="GLDM",
        sector="Gold",
        quantity=10,
        available_qty=10,
        avg_cost_krw=100_000,
        market_price_krw=100_000,
        market_value_krw=1_500_000,
        unrealized_pnl_krw=0,
    )
    snapshot = _snapshot(cash=100_000, positions=(held,))
    candidates = [
        _candidate(
            "GLDM",
            "GLDM",
            is_held=True,
            action_now="HOLD",
            action_if_triggered="NONE",
            setup_quality="WEAK",
            confidence=0.45,
            sector="Gold",
        ),
        _candidate(
            "NVDA",
            "NVIDIA",
            is_held=False,
            action_now="WATCH",
            action_if_triggered="STARTER_IF_TRIGGERED",
            setup_quality="COMPELLING",
            confidence=0.9,
            sector="Semiconductors",
        ),
    ]

    recommendation, scored = build_recommendation(
        candidates=candidates,
        snapshot=snapshot,
        batch_metrics={"entry_action_distribution": {"WAIT": 2}, "stance_distribution": {"BULLISH": 2}},
        warnings=[],
        profile=_profile(snapshot),
        report_date="2026-04-17",
    )
    trim_action = next(action for action in recommendation.actions if action.canonical_ticker == "GLDM")
    markdown = render_portfolio_report_markdown(snapshot=snapshot, recommendation=recommendation, candidates=scored)

    assert trim_action.portfolio_relative_action == "TRIM_TO_FUND"
    assert trim_action.action_now == "TRIM_TO_FUND"
    assert "줄여서 강한 후보로 자금 이동" in markdown
    assert recommendation.funding_plan["trim_first_candidates"][0]["canonical_ticker"] == "GLDM"


def test_missing_intraday_confirmation_blocks_pilot():
    snapshot = _snapshot(cash=2_000_000)
    candidate = _candidate(
        "VRT",
        "Vertiv",
        is_held=False,
        action_now="STARTER_NOW",
        action_if_triggered="NONE",
        entry_action="STARTER",
        setup_quality="COMPELLING",
        confidence=0.85,
        data_health={"execution_timing_state": "SUPPORT_HOLD"},
    )

    recommendation, _ = build_recommendation(
        candidates=[candidate],
        snapshot=snapshot,
        batch_metrics={"entry_action_distribution": {"STARTER": 1}, "stance_distribution": {"BULLISH": 1}},
        warnings=[],
        profile=_profile(snapshot, allow_pilot=True),
        report_date="2026-04-17",
    )

    action = recommendation.actions[0]
    assert action.action_now == "STARTER_NOW"
    assert action.delta_krw_now == 0
    assert recommendation.candidate_counts["immediate_budget_blocked_count"] == 0


def test_missing_analysis_trim_reason_is_explicit():
    held = Position(
        broker_symbol="ETHU",
        canonical_ticker="ETHU",
        display_name="ETHU",
        sector="Crypto",
        quantity=10,
        available_qty=10,
        avg_cost_krw=100_000,
        market_price_krw=100_000,
        market_value_krw=1_500_000,
        unrealized_pnl_krw=0,
    )
    snapshot = _snapshot(cash=100_000, positions=(held,))
    candidates = [
        _candidate(
            "ETHU",
            "ETHU",
            is_held=True,
            action_now="HOLD",
            action_if_triggered="NONE",
            stance="NEUTRAL",
            setup_quality="WEAK",
            confidence=0.3,
            sector="Crypto",
            quality_flags=("missing_analysis_for_held_position",),
        ),
        _candidate(
            "VRT",
            "Vertiv",
            is_held=False,
            action_now="WATCH",
            action_if_triggered="STARTER_IF_TRIGGERED",
            setup_quality="COMPELLING",
            confidence=0.88,
            sector="Industrials",
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

    trim_item = recommendation.funding_plan["trim_first_candidates"][0]
    assert trim_item["canonical_ticker"] == "ETHU"
    assert "NO_COVERAGE" in trim_item["funding_reason_codes"]
    assert "OPPORTUNITY_COST" not in trim_item["funding_reason_codes"]
