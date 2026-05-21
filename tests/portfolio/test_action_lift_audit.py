from tradingagents.portfolio.account_models import (
    AccountConstraints,
    AccountSnapshot,
    InstrumentIdentity,
    PortfolioAction,
    PortfolioCandidate,
    PortfolioProfile,
    PortfolioRecommendation,
    Position,
)
from tradingagents.portfolio.action_lift import attach_action_lift_audit
from tradingagents.portfolio.reporting import render_portfolio_report_markdown
from tradingagents.portfolio.state_store import save_portfolio_outputs


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
        as_of="2026-05-21T16:10:00+09:00",
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


def _profile(snapshot: AccountSnapshot, *, opportunity: bool = False) -> PortfolioProfile:
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
        private_output_dirname="portfolio-private",
        watch_tickers=tuple(),
        trigger_budget_krw=500_000,
        constraints=snapshot.constraints,
        opportunity_capture_enabled=opportunity,
        opportunity_capture_per_pilot_nav_pct=1.0,
    )


def _candidate(ticker="009150.KS", name="삼성전기", *, held=False, timing="PILOT_READY") -> PortfolioCandidate:
    return PortfolioCandidate(
        snapshot_id="snap",
        instrument=_identity(ticker, name),
        is_held=held,
        market_value_krw=1_000_000 if held else 0,
        quantity=1 if held else 0,
        available_qty=1 if held else 0,
        sector="Semiconductors",
        structured_decision=None,
        data_coverage={"company_news_count": 3, "disclosures_count": 1, "social_source": "dedicated"},
        quality_flags=tuple(),
        vendor_health={"vendor_calls": {}, "fallback_count": 0},
        suggested_action_now="WATCH",
        suggested_action_if_triggered="NONE",
        trigger_conditions=("1,100,000원 위 유지",),
        confidence=0.82,
        stance="BULLISH",
        entry_action="STARTER",
        setup_quality="COMPELLING",
        rationale="pilot ready",
        data_health={
            "execution_decision_state": "ACTIONABLE_NOW",
            "execution_timing_state": timing,
            "session_vwap_ok": True,
            "relative_volume_ok": True,
            "execution_data_quality": "REALTIME_EXECUTION_READY",
        },
    )


def _action(ticker="009150.KS", name="삼성전기", **overrides) -> PortfolioAction:
    payload = {
        "canonical_ticker": ticker,
        "display_name": name,
        "priority": 1,
        "confidence": 0.82,
        "action_now": "WATCH",
        "delta_krw_now": 0,
        "target_weight_now": 0.0,
        "action_if_triggered": "NONE",
        "delta_krw_if_triggered": 0,
        "target_weight_if_triggered": 0.0,
        "trigger_conditions": ("1,100,000원 위 유지",),
        "rationale": "pilot ready",
        "data_health": {
            "execution_decision_state": "ACTIONABLE_NOW",
            "execution_timing_state": "PILOT_READY",
            "session_vwap_ok": True,
            "relative_volume_ok": True,
        },
        "portfolio_relative_action": "WATCH",
    }
    payload.update(overrides)
    return PortfolioAction(**payload)


def _recommendation(action: PortfolioAction) -> PortfolioRecommendation:
    return PortfolioRecommendation(
        snapshot_id="snap",
        report_date="2026-05-21",
        account_value_krw=5_000_000,
        recommended_cash_after_now_krw=5_000_000,
        recommended_cash_after_triggered_krw=5_000_000,
        market_regime="constructive_but_selective",
        actions=(action,),
        portfolio_risks=tuple(),
        data_health_summary={},
    )


def test_pilot_ready_bullish_watch_is_action_lift_failure_and_reported():
    snapshot = _snapshot()
    recommendation = attach_action_lift_audit(
        recommendation=_recommendation(_action()),
        candidates=[_candidate()],
        snapshot=snapshot,
        profile=_profile(snapshot),
    )

    entry = recommendation.action_lift_audit["entries"][0]
    markdown = render_portfolio_report_markdown(snapshot=snapshot, recommendation=recommendation, candidates=[_candidate()])

    assert entry["lift_status"] == "ACTION_LIFT_FAILURE"
    assert entry["pilot_allowed"] is True
    assert "놓친 기회 위험 / 액션 승격 점검" in markdown
    assert "액션 승격 실패" in markdown


def test_held_pilot_ready_take_profit_is_relabelled_buy_signal_warning():
    held = Position(
        broker_symbol="009150",
        canonical_ticker="009150.KS",
        display_name="삼성전기",
        sector="Semiconductors",
        quantity=1,
        available_qty=1,
        avg_cost_krw=1_000_000,
        market_price_krw=1_100_000,
        market_value_krw=1_100_000,
        unrealized_pnl_krw=100_000,
    )
    snapshot = _snapshot(positions=(held,))
    action = _action(
        action_now="TAKE_PROFIT_NOW",
        delta_krw_now=-200_000,
        portfolio_relative_action="TAKE_PROFIT",
        sell_intent="TAKE_PROFIT",
    )

    recommendation = attach_action_lift_audit(
        recommendation=_recommendation(action),
        candidates=[_candidate(held=True)],
        snapshot=snapshot,
        profile=_profile(snapshot),
    )

    assert recommendation.action_lift_audit["entries"][0]["lift_status"] == "BUY_SIGNAL_RELABELED_AS_SELL_SIDE"


def test_budget_blocked_pilot_records_min_trade_reason_when_sleeve_too_small():
    snapshot = _snapshot(cash=5_000_000)
    action = _action(action_now="STARTER_NOW", budget_blocked_actionable=True)
    recommendation = attach_action_lift_audit(
        recommendation=_recommendation(action),
        candidates=[_candidate()],
        snapshot=snapshot,
        profile=_profile(snapshot, opportunity=True),
    )

    entry = recommendation.action_lift_audit["entries"][0]
    assert entry["lift_status"] == "BUDGET_BLOCKED"
    assert "pilot_allowed_below_min_trade" in entry["block_reasons"]


def test_action_lift_artifact_is_saved_with_report_and_audit(tmp_path):
    snapshot = _snapshot()
    recommendation = attach_action_lift_audit(
        recommendation=_recommendation(_action()),
        candidates=[_candidate()],
        snapshot=snapshot,
        profile=_profile(snapshot),
    )
    artifacts = save_portfolio_outputs(
        private_dir=tmp_path / "portfolio-private",
        snapshot=snapshot,
        candidates=[_candidate()],
        recommendation=recommendation,
        portfolio_report_markdown="report",
        semantic_verdicts=[],
        action_judge_payload={},
        report_writer_payload={},
        batch_metrics={},
        warnings=[],
    )

    assert "action_lift_audit_json" in artifacts
    assert (tmp_path / "portfolio-private" / "action_lift_audit.json").exists()
    assert (tmp_path / "portfolio-private" / "decision_audit.json").read_text(encoding="utf-8").find("action_lift_audit") >= 0
