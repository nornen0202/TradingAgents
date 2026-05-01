from types import SimpleNamespace

from tradingagents.external.prism_conflicts import reconcile_prism_with_actions, render_external_signal_section
from tradingagents.external.prism_models import PrismExternalSignal, PrismIngestionResult, PrismSignalAction


def _action(ticker):
    return SimpleNamespace(
        canonical_ticker=ticker,
        display_name=ticker,
        action_now="HOLD",
        action_if_triggered="NONE",
        portfolio_relative_action="HOLD",
        risk_action="NONE",
        data_health={},
    )


def test_prism_no_signal_label_same_market_only():
    reconciliation = reconcile_prism_with_actions(
        tradingagents_actions=[_action("AAPL")],
        ingestion=PrismIngestionResult(enabled=True, ok=True, signals=[]),
        run_market="US",
    )

    entry = reconciliation["entries"][0]
    assert entry["coverage_status"] == "NO_SIGNAL"
    assert entry["prism_agreement"] == "no_prism_signal"


def test_prism_cross_market_no_coverage_label():
    ingestion = PrismIngestionResult(
        enabled=True,
        ok=True,
        signals=[
            PrismExternalSignal(
                canonical_ticker="000660.KS",
                market="KR",
                signal_action=PrismSignalAction.BUY,
            )
        ],
    )
    reconciliation = reconcile_prism_with_actions(
        tradingagents_actions=[_action("AAPL")],
        ingestion=ingestion,
        run_market="US",
    )

    assert reconciliation["entries"][0]["coverage_status"] == "NO_SAME_MARKET_SIGNAL"


def test_portfolio_external_summary_shows_market_coverage():
    ingestion = PrismIngestionResult(
        enabled=True,
        ok=True,
        source_kind=None,
        signals=[
            PrismExternalSignal(canonical_ticker="000660.KS", market="KR", signal_action=PrismSignalAction.BUY),
            PrismExternalSignal(canonical_ticker="005930.KS", market="KR", signal_action=PrismSignalAction.SELL),
        ],
    )
    reconciliation = reconcile_prism_with_actions(
        tradingagents_actions=[_action("AAPL")],
        ingestion=ingestion,
        run_market="US",
    )

    section = render_external_signal_section(reconciliation)

    assert "현재 리포트 시장: US" in section
    assert "현재 시장에 매칭된 PRISM 신호: 0개" in section
    assert "교차시장 신호는 후보 생성/충돌 판단에서 제외됨" in section
