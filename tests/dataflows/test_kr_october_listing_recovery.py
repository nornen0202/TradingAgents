from copy import deepcopy
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import Mock

import pandas as pd
import pytest

from tradingagents.dataflows import kr_daily_history as kr, kr_security_listing as listing
from tradingagents.dataflows.config import run_config
from tradingagents.dataflows.daily_history_selection import activate_daily_history_selection, reset_daily_history_selection
from tradingagents.dataflows.vendor_exceptions import VendorInputError, VendorMalformedResponseError


NOW = datetime(2026, 10, 29, 8, 35, tzinfo=timezone.utc)
START, END = "2021-10-28", "2026-10-28"
CASES = [("179880.KQ", "2026-10-15", "KR7179880000"),
         ("443670.KQ", "2024-02-15", "KR7443670005")]


def metadata(symbol, now=NOW):
    issue = listing._REVIEWED[symbol]
    return {"schema": listing.METADATA_SCHEMA, "provider": "KIS", "environment": "public",
            "symbol": symbol, "board": "kosdaq", "url": listing.master_url("kosdaq"),
            "reader_source_sha256": listing._MASTER["kosdaq"][2],
            "collection_started_at": (now-timedelta(seconds=2)).isoformat(),
            "available_at": (now-timedelta(seconds=1)).isoformat(),
            "zip_sha256": "a"*64, "master_sha256": "b"*64,
            "identity": {"short_code_raw": issue["short_code"], "standard_code": issue["isin"],
                         "korean_name": issue["provider_name"], "security_group_token": "ST",
                         "listing_date_raw": issue["first_regular_session"].replace("-", ""),
                         "indirect_listing_raw": "N", "row_sha256": "c"*64, "row_bytes": 283}}


@pytest.fixture(autouse=True)
def clock(monkeypatch):
    class ClockType(type):
        def __instancecheck__(cls, instance):
            return isinstance(instance, datetime)
    class Clock(datetime, metaclass=ClockType):
        @classmethod
        def now(cls, tz=None):
            return NOW.astimezone(tz) if tz else NOW.replace(tzinfo=None)
    for module in (listing, kr):
        monkeypatch.setattr(module, "datetime", Clock)
    kr._CACHE.clear()
    token = activate_daily_history_selection()
    with run_config({"analysis_as_of": "2026-10-29"}):
        yield
    reset_daily_history_selection(token)
    kr._CACHE.clear()


@pytest.mark.parametrize("symbol,first,isin", CASES)
def test_exact_new_security_and_actual_review_clock(symbol, first, isin):
    issue = listing._REVIEWED[symbol]
    assert issue["isin"] == isin and issue["first_regular_session"] == first
    contract = listing.verify_listing_contract(symbol, metadata(symbol), requested_start=START,
                                                end_date=END, analysis_as_of=NOW)
    assert contract["original_requested_start"] == START
    assert contract["required_start"] == first and not contract["historical_vintage_verified"]
    before = datetime.fromisoformat(issue["evidence_available_at"])-timedelta(microseconds=1)
    with pytest.raises(ValueError, match="Unavailable"):
        listing.verify_listing_contract(symbol, metadata(symbol, before), requested_start=START,
                                        end_date=END, analysis_as_of=before)


@pytest.mark.parametrize("change", [
    {"event_kind": "SPAC_MERGER"}, {"new_security": False}, {"predecessor_history_allowed": True},
    {"predecessor_name": ""}, {"sources": []},
])
def test_spac_dissolution_is_not_a_general_predecessor_history_exception(monkeypatch, change):
    issue = {**deepcopy(listing._REVIEWED["443670.KQ"]), **change}
    monkeypatch.setitem(listing._REVIEWED, "443670.KQ", issue)
    with pytest.raises(ValueError, match="Unavailable"):
        listing.verify_listing_contract("443670.KQ", metadata("443670.KQ"), requested_start=START,
                                        end_date=END, analysis_as_of=NOW)


@pytest.mark.parametrize("symbol,first,isin", CASES)
@pytest.mark.parametrize("field,value", [("standard_code", "KR7000000000"),
    ("security_group_token", "SC"), ("indirect_listing_raw", "Y"), ("listing_date_raw", "20200101")])
def test_foreign_or_predecessor_master_cannot_bind(symbol, first, isin, field, value):
    snapshot = metadata(symbol)
    snapshot["identity"][field] = value
    with pytest.raises(ValueError, match="master"):
        listing.verify_listing_contract(symbol, snapshot, requested_start=START,
                                        end_date=END, analysis_as_of=NOW)


@pytest.fixture
def broker(monkeypatch):
    monkeypatch.setenv("TRADINGAGENTS_KIS_RESEARCH_FALLBACK_ENABLED", "1")
    monkeypatch.setattr(kr, "get_api_key", lambda _: "offline")
    monkeypatch.setattr(kr, "time", SimpleNamespace(monotonic=lambda: 10., sleep=lambda _: None))
    monkeypatch.setattr(listing, "collect_master_identity", lambda symbol, **_: metadata(symbol))
    monkeypatch.setattr("tradingagents.calendar_access.get_exchange_calendar",
                        lambda name, *, start, end: SimpleNamespace(sessions=pd.bdate_range(start, end)))
    monkeypatch.setattr("tradingagents.scheduled.market_calendar.is_supplemental_market_holiday", lambda **_: False)
    state = SimpleNamespace(symbol="179880.KQ", missing=set(), bad=None, future=False)
    client = Mock()
    def reply(symbol, *, start_date, end_date, **kwargs):
        assert symbol == state.symbol[:6] and kwargs["adjusted_price"] == "0"
        days = pd.bdate_range(listing._REVIEWED[state.symbol]["first_regular_session"], END)
        rows = [{"stck_bsop_date": day.strftime("%Y%m%d"), "stck_oprc": "100", "stck_hgpr": "110",
                 "stck_lwpr": "90", "stck_clpr": "105", "acml_vol": "200"}
                for day in reversed(days) if start_date <= day.date() <= end_date
                and day.date().isoformat() not in state.missing][:100]
        if state.bad == "empty":
            rows = []
        elif state.bad == "missing_date":
            rows[0].pop("stck_bsop_date")
        elif state.bad == "bad_date":
            rows[0]["stck_bsop_date"] = "invalid"
        elif state.bad == "predecessor":
            rows.append({**rows[0], "stck_bsop_date": "20240214"})
        if state.future:
            rows.insert(0, {"stck_bsop_date": "20990101", "stck_clpr": "bad future price"})
        return {"output2": rows}
    client.domestic_daily_itemchartprice.side_effect = reply
    monkeypatch.setattr("tradingagents.portfolio.kis.KisClient.from_api_keys", lambda **_: client)
    return state, client


@pytest.mark.parametrize("symbol,first,isin", CASES)
def test_full_single_provider_replacement_preserves_all_real_sessions(broker, symbol, first, isin):
    state, client = broker
    state.symbol = symbol
    # Reproduce Yahoo's missing first Melcon session / interior SPSoft session.
    days = pd.bdate_range(first, END)
    missing = first if symbol == "179880.KQ" else "2025-09-19"
    yahoo = pd.DataFrame({"Date": days, "Open": 10., "High": 11., "Low": 9., "Close": 10., "Volume": 20.})
    yahoo = yahoo[yahoo.Date != pd.Timestamp(missing)]
    original = yahoo.copy(deep=True)
    result = kr.validate_with_kr_fallback(yahoo, symbol, START, END)
    assert result.attrs["source"] == kr.SOURCE and result.attrs["complete"] is True
    assert result.Date.tolist() == days.tolist() and set(result.Close) == {105.}
    assert result.attrs["listing_contract"]["reviewed_event"]["isin"] == isin
    assert result.attrs["requested_start"] == START
    pd.testing.assert_frame_equal(yahoo, original)
    assert client.domestic_daily_itemchartprice.call_count <= 20


@pytest.mark.parametrize("bad", ["empty", "missing_date", "bad_date", "predecessor"])
def test_bad_or_predecessor_bars_never_become_analysis_evidence(broker, bad):
    state, _ = broker
    state.symbol, state.bad = "443670.KQ", bad
    with pytest.raises((VendorInputError, VendorMalformedResponseError)):
        kr.load_kr_daily_bars(state.symbol, START, END, require_complete=True)


def test_missing_regular_day_is_still_rejected_and_future_rows_are_excluded(broker):
    state, _ = broker
    state.symbol, state.future = "443670.KQ", True
    valid = kr.load_kr_daily_bars(state.symbol, START, END, require_complete=True)
    assert valid.Date.max() == pd.Timestamp(END)
    kr._CACHE.clear()
    state.missing = {"2025-09-19"}
    with pytest.raises(VendorMalformedResponseError, match="missing required sessions"):
        kr.load_kr_daily_bars(state.symbol, START, END, require_complete=True)
