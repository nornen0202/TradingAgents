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


def test_kr_scanner_excludes_us_ohlcv_rows_even_when_fixture_is_mixed():
    result = run_prism_like_scanner(
        market="KR",
        ohlcv_rows=[
            {
                "ticker": "AAPL",
                "display_name": "Apple",
                "market": "US",
                "open": 190,
                "high": 200,
                "low": 188,
                "close": 198,
                "prev_close": 187,
                "volume": 80_000_000,
                "prev_volume": 40_000_000,
                "trading_value": 15_000_000_000,
                "market_cap": 3_000_000_000_000,
            },
            {
                "ticker": "000660",
                "display_name": "SK하이닉스",
                "market": "KR",
                "open": 196000,
                "high": 205000,
                "low": 194000,
                "close": 203000,
                "prev_close": 194000,
                "volume": 3_000_000,
                "prev_volume": 1_500_000,
                "trading_value": 610_000_000_000,
                "market_cap": 140_000_000_000_000,
            },
        ],
    )

    assert [candidate.ticker for candidate in result.candidates] == ["000660.KS"]
    assert result.source_counts["scanner_excluded_cross_market_rows"] == 1
