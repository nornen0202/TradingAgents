from tradingagents.external.prism_models import PrismExternalSignal, PrismSignalAction
from tradingagents.scheduled.runner import _augment_with_prism_candidates


def _signal(ticker, market):
    return PrismExternalSignal(
        canonical_ticker=ticker,
        market=market,
        signal_action=PrismSignalAction.BUY,
        confidence=0.9,
    )


def test_us_run_does_not_add_kr_prism_candidates_by_default():
    tickers = _augment_with_prism_candidates(
        ["AAPL"],
        [_signal("000660.KS", "KR")],
        max_new=3,
        run_market="US",
    )

    assert tickers == ["AAPL"]


def test_kr_run_does_not_add_us_prism_candidates_by_default():
    tickers = _augment_with_prism_candidates(
        ["000660.KS"],
        [_signal("AAPL", "US")],
        max_new=3,
        run_market="KR",
    )

    assert tickers == ["000660.KS"]


def test_cross_market_candidates_can_be_enabled_explicitly():
    tickers = _augment_with_prism_candidates(
        ["AAPL"],
        [_signal("000660.KS", "KR")],
        max_new=3,
        run_market="US",
        allow_cross_market_candidates=True,
        allowed_markets=("KR",),
    )

    assert tickers == ["AAPL", "000660.KS"]
