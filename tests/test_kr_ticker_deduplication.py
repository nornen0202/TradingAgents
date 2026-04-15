from tradingagents.scheduled.config import _normalize_tickers


def test_kr_suffix_variants_deduped_by_identity():
    values = ["095340.KQ", "095340.KS", "000660.KS"]
    normalized = _normalize_tickers(values)
    assert normalized == ["095340.KQ", "000660.KS"]


def test_non_kr_suffix_variants_not_collapsed():
    values = ["AAPL", "AAPL.US", "AAPL"]
    normalized = _normalize_tickers(values)
    assert normalized == ["AAPL", "AAPL.US"]
