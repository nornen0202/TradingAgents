from datetime import datetime
from unittest.mock import Mock

import pytest

from tradingagents.charting.capture import normalize_kis_bars
from tradingagents.dataflows.config import run_config
from tradingagents.dataflows.intraday import kis_quotes
from tradingagents.dataflows.intraday.microstructure import _native_bar_reference
from tradingagents.dataflows.vendor_exceptions import VendorUnavailableError
from tradingagents.performance.price_evidence import native_reference


NOW = datetime.fromisoformat("2026-11-25T11:00:00+09:00")
BAR = {"close": 70000.0, "available_at": "2026-11-25T10:45:00+09:00", "observed_at": NOW.isoformat()}


@pytest.mark.parametrize("changes", [
    None,
    {"available_at": None},
    {"available_at": "malformed"},
    {"observed_at": None},
    {"observed_at": "malformed"},
    {"observed_at": "2026-11-25T11:00:01+09:00"},
    {"available_at": "2026-11-25T11:00:01+09:00"},
    {"available_at": "2026-11-24T15:30:00+09:00"},
    {"available_at": "2026-11-25T10:44:59+09:00"},
    {"close": float("inf")},
])
def test_kis_bar_rejection_cannot_supply_a_native_recommendation_price(changes):
    bars = [] if changes is None else [BAR | changes]
    receipt = _native_bar_reference(bars, NOW, "KRW", "kis.chart.fixture")
    assert receipt is None
    assert native_reference(receipt, "KR", NOW.isoformat())[0] is None


def test_kis_completed_bar_at_maximum_age_supplies_native_reference():
    raw = {"stck_bsop_date": "20261125", "stck_cntg_hour": "104400", "stck_oprc": "70000",
           "stck_hgpr": "70500", "stck_lwpr": "69900", "stck_prpr": "70300", "cntg_vol": "50"}
    bars = normalize_kis_bars([raw], observed_at=NOW, timezone_name="Asia/Seoul")
    assert len(bars) == 1
    receipt = _native_bar_reference(bars, NOW, "KRW", "kis.domestic_time_itemchartprice")
    reference, state = native_reference(receipt, "KR", NOW.isoformat())
    assert state == "verified_native_reference" and reference.price == 70300 and reference.currency == "KRW"


@pytest.mark.parametrize("day,hour,accepted", [
    ("20261125", "104500", True),
    ("20261125", "104459", False),
    ("20261124", "153000", False),
    ("20261125", "110001", None),
    (None, None, None),
    ("20261125", None, None),
    ("20261125", "oops", None),
])
def test_kis_quote_snapshot_admits_only_verified_current_trades(monkeypatch, day, hour, accepted):
    class Clock(datetime):
        @classmethod
        def now(cls, tz=None):
            return NOW.astimezone(tz)

    monkeypatch.setattr(kis_quotes, "datetime", Clock)
    client = Mock()
    fields = {"stck_prpr": "70300", "stck_bsop_date": day, "stck_cntg_hour": hour}
    client.request_json.return_value = ({"output": fields if day is not None or hour is not None else {}}, {})
    monkeypatch.setattr(kis_quotes.KisClient, "from_api_keys", lambda **_: client)
    with run_config({}):
        if accepted is None:
            with pytest.raises(VendorUnavailableError):
                kis_quotes.KISQuoteProvider().fetch("005930.KS")
            return
        quote = kis_quotes.KISQuoteProvider().fetch("005930.KS")
    if accepted:
        reference, state = native_reference(quote.research_price_reference, "KR", NOW.isoformat())
        assert state == "verified_native_reference" and reference.price == 70300 and reference.currency == "KRW"
    else:
        assert quote.research_price_reference is None
        assert native_reference(quote.research_price_reference, "KR", NOW.isoformat())[0] is None



def test_kis_bar_rejects_prior_session_even_within_fifteen_minutes():
    next_day = datetime.fromisoformat("2026-11-25T00:01:00+09:00")
    recent_prior_day = BAR | {"available_at": "2026-11-24T23:59:00+09:00", "observed_at": next_day.isoformat()}
    assert _native_bar_reference([recent_prior_day], next_day, "KRW", "kis.chart.fixture") is None
