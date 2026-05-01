from types import SimpleNamespace

from tradingagents.external.prism_conflicts import reconcile_prism_with_actions
from tradingagents.external.prism_models import PrismExternalSignal, PrismIngestionResult, PrismSignalAction


def _action(ticker, *, now="HOLD", triggered="NONE", risk="NONE"):
    return SimpleNamespace(
        canonical_ticker=ticker,
        display_name=ticker,
        action_now=now,
        action_if_triggered=triggered,
        risk_action=risk,
        portfolio_relative_action=risk if risk != "NONE" else "HOLD",
        confidence=0.7,
    )


def _signal(ticker, market, action):
    return PrismExternalSignal(canonical_ticker=ticker, market=market, signal_action=action, confidence=0.8)


def test_prism_conflict_ignores_cross_market_signal():
    ingestion = PrismIngestionResult(
        enabled=True,
        ok=True,
        signals=[_signal("000660.KS", "KR", PrismSignalAction.BUY)],
    )

    reconciliation = reconcile_prism_with_actions(
        tradingagents_actions=[_action("AAPL", risk="REDUCE_RISK")],
        ingestion=ingestion,
        run_market="US",
    )

    assert [entry["ticker"] for entry in reconciliation["entries"]] == ["AAPL"]
    assert reconciliation["entries"][0]["coverage_status"] == "NO_SAME_MARKET_SIGNAL"
    assert reconciliation["entries"][0]["reason"] == "PRISM source contains signals for another market for this run."


def test_reconciliation_artifact_contains_no_same_market_signal_reason():
    ingestion = PrismIngestionResult(
        enabled=True,
        ok=True,
        signals=[_signal("000660.KS", "KR", PrismSignalAction.BUY)],
    )

    entry = reconcile_prism_with_actions(
        tradingagents_actions=[_action("NVDA")],
        ingestion=ingestion,
        run_market="US",
    )["entries"][0]

    assert entry["coverage_status"] == "NO_SAME_MARKET_SIGNAL"
    assert entry["agreement"] == "no_prism_signal"
    assert entry["recommendation"] == "use_ta_only"


def test_reconciliation_artifact_blocks_same_market_conflict():
    ingestion = PrismIngestionResult(
        enabled=True,
        ok=True,
        signals=[_signal("006340.KS", "KR", PrismSignalAction.BUY)],
    )

    entry = reconcile_prism_with_actions(
        tradingagents_actions=[_action("006340.KS", risk="REDUCE_RISK")],
        ingestion=ingestion,
        run_market="KR",
    )["entries"][0]

    assert entry["coverage_status"] == "MATCHED"
    assert entry["prism_agreement"] == "conflict_prism_buy_ta_reduce"
    assert entry["recommendation"] == "block_buy_review_required"
