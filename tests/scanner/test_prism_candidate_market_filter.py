from tradingagents.external.prism_models import PrismExternalSignal, PrismSignalAction
from tradingagents.scanner.prism_like_scanner import run_prism_like_scanner


def _signal(ticker, market):
    return PrismExternalSignal(
        canonical_ticker=ticker,
        market=market,
        signal_action=PrismSignalAction.BUY,
        confidence=0.8,
    )


def test_scanner_prism_candidate_same_market_filter_default():
    result = run_prism_like_scanner(
        ohlcv_rows=[],
        market="US",
        external_signals=[_signal("000660.KS", "KR")],
    )

    assert result.source_counts["prism_imported_same_market"] == 0
    assert result.source_counts["prism_excluded_cross_market"] == 1


def test_scanner_artifact_records_excluded_cross_market_count(tmp_path):
    output_path = tmp_path / "scanner_candidates.json"

    run_prism_like_scanner(
        ohlcv_rows=[],
        market="US",
        external_signals=[_signal("000660.KS", "KR"), _signal("AAPL", "US")],
        output_path=output_path,
    )

    text = output_path.read_text(encoding="utf-8")
    assert '"prism_excluded_cross_market": 1' in text
    assert "PRISM 후보 2개 중 현재 시장 US와 일치하지 않아 1개 제외" in text
