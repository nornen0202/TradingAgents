from tradingagents.scheduled.config import _normalize_tickers


def test_kr_suffix_variants_deduped_by_identity():
    values = ["095340.KQ", "095340.KS", "000660.KS"]
    normalized = _normalize_tickers(values)
    assert normalized == ["095340.KQ", "000660.KS"]


def test_kr_bare_and_exchange_qualified_symbols_are_collapsed():
    values = ["005930", "005930.KS", "005930.KQ"]
    normalized = _normalize_tickers(values)
    assert normalized == ["005930"]


def test_non_kr_suffix_variants_not_collapsed():
    values = ["AAPL", "AAPL.US", "AAPL"]
    normalized = _normalize_tickers(values)
    assert normalized == ["AAPL", "AAPL.US"]
