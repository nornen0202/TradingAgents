from tradingagents.external.prism_conflicts import build_prism_coverage_summary, filter_prism_signals_for_market
from tradingagents.external.prism_models import PrismExternalSignal, PrismIngestionResult, PrismSignalAction


def _signal(ticker, market, action=PrismSignalAction.BUY):
    return PrismExternalSignal(canonical_ticker=ticker, market=market, signal_action=action)


def test_prism_coverage_summary_counts_markets():
    ingestion = PrismIngestionResult(
        enabled=True,
        ok=True,
        signals=[_signal("000660.KS", "KR"), _signal("AAPL", "US"), _signal("005930.KS", "KR")],
    )

    summary = build_prism_coverage_summary(ingestion, run_market="US")

    assert summary.source_markets == {"KR": 2, "US": 1}
    assert summary.total_signals == 3
    assert summary.matching_market_signals == 1
    assert summary.cross_market_signals == 2


def test_prism_coverage_summary_counts_overlap():
    ingestion = PrismIngestionResult(
        enabled=True,
        ok=True,
        signals=[_signal("AAPL", "US"), _signal("MSFT", "US")],
    )

    summary = build_prism_coverage_summary(ingestion, run_market="US", run_tickers=["AAPL", "NVDA"])

    assert summary.overlapping_tickers == 1


def test_filter_prism_signals_defaults_to_current_market():
    signals = [_signal("000660.KS", "KR"), _signal("AAPL", "US")]

    filtered = filter_prism_signals_for_market(signals, run_market="US")

    assert [signal.canonical_ticker for signal in filtered] == ["AAPL"]
