from types import SimpleNamespace

from tradingagents.portfolio.instrument_identity import _looks_like_symbol, resolve_identity


def test_symbol_detection_keeps_exchange_ticker_shape():
    assert _looks_like_symbol("AAPL") is True
    assert _looks_like_symbol("000660.KS") is True
    assert _looks_like_symbol("APPLE INC") is False


def test_resolve_identity_prefers_symbol_over_display_name(monkeypatch):
    def _fake_resolve(value: str):
        normalized = str(value).upper()
        if normalized == "AAPL":
            return SimpleNamespace(
                primary_symbol="AAPL",
                yahoo_symbol="AAPL",
                krx_code=None,
                dart_corp_code=None,
                display_name="Apple",
                exchange="NASDAQ",
                country="US",
                currency="USD",
            )
        return SimpleNamespace(
            primary_symbol="APPLE",
            yahoo_symbol="APPLE",
            krx_code=None,
            dart_corp_code=None,
            display_name="Apple Inc",
            exchange="NASDAQ",
            country="US",
            currency="USD",
        )

    monkeypatch.setattr("tradingagents.portfolio.instrument_identity.resolve_instrument", _fake_resolve)
    identity = resolve_identity("AAPL", "Apple")
    assert identity.canonical_ticker == "AAPL"
