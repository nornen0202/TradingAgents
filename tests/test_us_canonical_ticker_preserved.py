from tradingagents.portfolio.instrument_identity import _looks_like_symbol


def test_symbol_detection_keeps_exchange_ticker_shape():
    assert _looks_like_symbol("AAPL") is True
    assert _looks_like_symbol("000660.KS") is True
    assert _looks_like_symbol("APPLE INC") is False
