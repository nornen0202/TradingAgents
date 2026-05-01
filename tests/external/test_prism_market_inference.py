from tradingagents.external.prism_dashboard import parse_dashboard_payload
from tradingagents.external.prism_models import PrismSourceKind


def _parse(record, *, market="US"):
    result = parse_dashboard_payload(
        {"signals": [record]},
        source_kind=PrismSourceKind.DASHBOARD_JSON,
        source="fixture",
        market=market,
    )
    assert result.ok is True
    assert len(result.signals) == 1
    return result.signals[0]


def test_prism_kr_suffix_overrides_us_default_market():
    signal = _parse({"ticker": "000660.KS", "action": "BUY"}, market="US")

    assert signal.market == "KR"
    assert "market_inferred_from_ticker" in signal.warnings


def test_prism_plain_us_symbol_infers_us():
    signal = _parse({"ticker": "AAPL", "action": "BUY"}, market="KR")

    assert signal.canonical_ticker == "AAPL"
    assert signal.market == "US"
    assert "market_inferred_from_ticker" in signal.warnings


def test_prism_numeric_kr_code_infers_kr():
    signal = _parse({"ticker": "042660", "action": "HOLD"}, market="US")

    assert signal.canonical_ticker == "042660.KS"
    assert signal.market == "KR"


def test_prism_market_conflict_warning():
    signal = _parse({"ticker": "000660.KS", "market": "US", "action": "BUY"}, market="US")

    assert signal.market == "KR"
    assert "market_conflict_overridden" in signal.warnings
