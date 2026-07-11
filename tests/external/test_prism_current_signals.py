from datetime import datetime, timedelta, timezone

from tradingagents.external.prism_conflicts import build_current_prism_signals_payload
from tradingagents.external.prism_models import (
    PrismExternalSignal,
    PrismIngestionResult,
    PrismSignalAction,
    PrismSourceKind,
)


def test_current_prism_signals_filters_market_age_missing_asof_and_duplicates():
    now = datetime(2026, 7, 10, 12, 0, tzinfo=timezone.utc)
    ingestion = PrismIngestionResult(
        enabled=True,
        ok=True,
        source_kind=PrismSourceKind.DASHBOARD_JSON,
        ingested_at=now,
        signals=[
            PrismExternalSignal(
                canonical_ticker="NVDA",
                market="US",
                signal_action=PrismSignalAction.HOLD,
                source_asof=(now - timedelta(hours=2)).replace(tzinfo=None),
                confidence=0.7,
            ),
            PrismExternalSignal(
                canonical_ticker="NVDA",
                market="US",
                signal_action=PrismSignalAction.BUY,
                source_asof=now - timedelta(hours=1),
                confidence=0.9,
            ),
            PrismExternalSignal(
                canonical_ticker="AAPL",
                market="US",
                signal_action=PrismSignalAction.SELL,
                source_asof=now - timedelta(days=8),
            ),
            PrismExternalSignal(
                canonical_ticker="MSFT",
                market="US",
                signal_action=PrismSignalAction.WATCH,
                source_asof=None,
            ),
            PrismExternalSignal(
                canonical_ticker="005930.KS",
                market="KR",
                signal_action=PrismSignalAction.BUY,
                source_asof=now,
            ),
        ],
    )

    payload = build_current_prism_signals_payload(
        ingestion=ingestion,
        run_market="US",
        max_signal_age_hours=72,
    )

    assert [signal["canonical_ticker"] for signal in payload["signals"]] == ["NVDA"]
    assert payload["signals"][0]["signal_action"] == "BUY"
    assert payload["quality"] == {
        "raw_signal_count": 5,
        "cross_market_excluded_count": 1,
        "missing_source_asof_count": 1,
        "expired_signal_count": 1,
        "duplicate_ticker_count": 1,
        "current_signal_count": 1,
    }
