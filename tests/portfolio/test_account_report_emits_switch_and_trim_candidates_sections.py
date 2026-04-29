from tradingagents.portfolio.account_models import (
    AccountConstraints,
    AccountSnapshot,
    InstrumentIdentity,
    PortfolioCandidate,
    PortfolioProfile,
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


def test_account_report_emits_switch_and_trim_candidates_sections():
    snapshot = _snapshot()
    candidates = [
        PortfolioCandidate(
            snapshot_id=snapshot.snapshot_id,
            instrument=_identity("005930.KS", "삼성전자"),
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
            trigger_conditions=("종가 75,000원 상회",),
            confidence=0.7,
            stance="BULLISH",
            entry_action="WAIT",
            setup_quality="DEVELOPING",
            rationale="조건 확인 전까지 대기",
            strategy_state="add_if_triggered",
        )
    ]

    recommendation, scored = build_recommendation(
        candidates=candidates,
        snapshot=snapshot,
        batch_metrics={"entry_action_distribution": {"WAIT": 1}, "stance_distribution": {"BULLISH": 1}},
        warnings=[],
        profile=_profile(snapshot),
        report_date="2026-04-16",
    )
    markdown = render_portfolio_report_markdown(snapshot=snapshot, recommendation=recommendation, candidates=scored)

    assert "## 자금이 생기면 살 후보" in markdown
    assert "## 자금 조달 시 먼저 줄일 후보" in markdown
    assert "## 줄여서 살 조합" in markdown
    assert "would-buy-if-funded" not in markdown
