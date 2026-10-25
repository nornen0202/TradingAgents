"""Offline first-listing contracts never excuse an interior trading-day gap."""
from datetime import datetime, timedelta, timezone
from io import BytesIO
from types import SimpleNamespace
from unittest.mock import Mock
import hashlib
import json
import zipfile

import pandas as pd
import pytest

from tradingagents.dataflows import kr_daily_history as kr, kr_security_listing as listing
from tradingagents.dataflows import daily_history_evidence as evidence
from tradingagents.dataflows.config import run_config
from tradingagents.dataflows.daily_history_selection import (
    activate_daily_history_selection, reset_daily_history_selection, select_daily_history,
)
from tradingagents.dataflows.stockstats_utils import calculate_stockstats_indicator
from tradingagents.dataflows.vendor_exceptions import (
    InsufficientIndicatorHistoryError, VendorInputError, VendorMalformedResponseError,
)
from tradingagents.portfolio.kis import KisClient

NOW = datetime(2026, 10, 26, 1, tzinfo=timezone.utc)
ORIGINAL, END = "2021-10-23", "2026-10-23"
REVIEWED_CASES = [("278470.KS", "2024-02-27"), ("403870.KQ", "2022-07-15"),
                  ("064400.KS", "2025-02-05"), ("411080.KQ", "2023-02-15")]


@pytest.fixture(autouse=True)
def clock(monkeypatch):
    state = SimpleNamespace(now=NOW)

    class ClockType(type):
        def __instancecheck__(cls, instance):
            return isinstance(instance, datetime)

    class Clock(datetime, metaclass=ClockType):
        @classmethod
        def now(cls, tz=None):
            return state.now.astimezone(tz) if tz else state.now.replace(tzinfo=None)

    for module in (kr, listing, evidence):
        monkeypatch.setattr(module, "datetime", Clock)
    with run_config({"analysis_as_of": "2026-10-26"}):
        yield state


def metadata(symbol="278470.KS"):
    issue = listing._REVIEWED[symbol]
    now = listing.datetime.now(timezone.utc)
    return {"schema": listing.METADATA_SCHEMA, "provider": "KIS", "environment": "public",
            "symbol": symbol, "board": issue["board"], "url": listing.master_url(issue["board"]),
            "reader_source_sha256": listing._MASTER[issue["board"]][2],
            "collection_started_at": (now - timedelta(seconds=30)).isoformat(),
            "available_at": (now - timedelta(seconds=1)).isoformat(),
            "zip_sha256": "a" * 64, "master_sha256": "b" * 64,
            "identity": {"short_code_raw": issue["short_code"], "standard_code": issue["isin"],
                         "korean_name": issue["provider_name"], "security_group_token": "ST",
                         "listing_date_raw": issue["first_regular_session"].replace("-", ""),
                         "indirect_listing_raw": "N", "row_sha256": "c" * 64, "row_bytes": 289}}


def verify(snapshot=None, symbol="278470.KS", **changes):
    return listing.verify_listing_contract(symbol, metadata(symbol) if snapshot is None else snapshot,
        requested_start=changes.get("requested_start", ORIGINAL), end_date=changes.get("end_date", END),
        analysis_as_of=changes.get("analysis_as_of", NOW))


@pytest.mark.parametrize("symbol,first", REVIEWED_CASES)
def test_exact_original_event_and_current_master_keep_original_window(symbol, first):
    contract = verify(symbol=symbol)
    assert contract["required_start"] == first and contract["original_requested_start"] == ORIGINAL
    assert contract["reviewed_event"]["isin"] == metadata(symbol)["identity"]["standard_code"]
    assert contract["historical_vintage_verified"] is False
    assert listing.validate_listing_receipt(symbol, contract, requested_start=ORIGINAL,
        end_date=END, observed_at=NOW) == contract


@pytest.mark.parametrize("field,value", [
    ("short_code_raw", "403870"), ("standard_code", "KR7403870009"),
    ("korean_name", "OTHER"), ("security_group_token", "EF"),
    ("listing_date_raw", "20240228"), ("listing_date_raw", "20260230"),
    ("indirect_listing_raw", "Y"), ("row_sha256", "bad"), ("row_bytes", True),
])
def test_identity_board_class_or_date_conflicts_never_authorize(field, value):
    snapshot = metadata()
    snapshot["identity"][field] = value
    with pytest.raises((ValueError, KeyError, TypeError)):
        verify(snapshot)


@pytest.mark.parametrize("field,value", [
    ("board", "kosdaq"), ("symbol", "403870.KQ"), ("environment", "demo"),
    ("url", "http://new.real.download.dws.co.kr/other"), ("reader_source_sha256", "f" * 64),
    ("available_at", None), ("available_at", "bad"), ("available_at", "2026-10-26T01:00:01Z"),
    ("available_at", "2026-10-26T00:54:00Z"), ("collection_started_at", "2026-10-26T01:00:01Z"),
])
def test_metadata_missing_future_stale_or_wrong_request_rejected(field, value):
    snapshot = metadata()
    snapshot[field] = value
    with pytest.raises((ValueError, KeyError, TypeError)):
        verify(snapshot)


@pytest.mark.parametrize("change", [{"event_kind": "RELISTING"}, {"security_class": "ADR"},
                                   {"currency": "USD"}, {"exchange": "NYS"}])
def test_only_reviewed_new_common_share_event_is_applicable(monkeypatch, change):
    monkeypatch.setitem(listing._REVIEWED, "278470.KS", {**listing._REVIEWED["278470.KS"], **change})
    with pytest.raises(ValueError):
        verify()


def test_explicit_old_0445_and_hpsp_before_0617_cannot_gain_later_proof(monkeypatch, clock):
    collect = Mock(side_effect=AssertionError("old analysis cannot collect new metadata"))
    monkeypatch.setattr(listing, "collect_master_identity", collect)
    clock.now = datetime.fromisoformat("2026-10-25T19:45:00+00:00")
    assert listing.collect_listing_contract("278470.KS", requested_start=ORIGINAL, end_date=END) is None
    assert listing.collect_listing_contract("403870.KQ", requested_start=ORIGINAL, end_date=END) is None
    with pytest.raises(ValueError, match="Unavailable"):
        verify(analysis_as_of=clock.now)
    clock.now = datetime.fromisoformat("2026-10-25T21:15:00+00:00")
    assert listing.collect_listing_contract("403870.KQ", requested_start=ORIGINAL, end_date=END) is None
    collect.assert_not_called()


def test_kr_cutoff_uses_analysis_day_not_price_day_and_never_future():
    with run_config({"analysis_as_of": "2026-10-25"}):
        assert listing.cutoff_for_day(END) == datetime(2026, 10, 25, 14, 59, 59, 999999, tzinfo=timezone.utc)
    with run_config({"analysis_as_of": "2026-10-26"}):
        assert listing.cutoff_for_day(END) == NOW
    with run_config({"analysis_as_of": "2026-10-22"}), pytest.raises(VendorInputError):
        listing.cutoff_for_day(END)


@pytest.mark.parametrize("day", ["2026-02-30", "20261023", "bad", None])
def test_invalid_requested_dates_never_form_receipts(day):
    with pytest.raises((ValueError, TypeError)):
        verify(end_date=day)


def test_unreviewed_or_mature_and_pre_listing_end_never_collect(monkeypatch):
    collect = Mock(side_effect=AssertionError("unexpected public master lookup"))
    monkeypatch.setattr(listing, "collect_master_identity", collect)
    assert listing.collect_listing_contract("000660.KS", requested_start=ORIGINAL, end_date=END) is None
    assert listing.collect_listing_contract("278470.KS", requested_start="2024-02-27", end_date=END) is None
    with pytest.raises(VendorMalformedResponseError, match="precedes"):
        listing.collect_listing_contract("278470.KS", requested_start=ORIGINAL, end_date="2024-02-26")
    collect.assert_not_called()


def master_row(symbol):
    issue = listing._REVIEWED[symbol]
    suffix = listing._MASTER[issue["board"]][1]
    tail = list(" " * (suffix - 1) + "\n")
    tail[:2] = "ST"
    lo, hi, indirect = listing._TAIL_FIELDS[issue["board"]]
    tail[lo:hi] = issue["first_regular_session"].replace("-", "")
    tail[indirect] = "N"
    return (f"{issue['short_code']:<9}{issue['isin']}{issue['provider_name']}" + "".join(tail)).encode("cp949")


@pytest.mark.parametrize("symbol", [row[0] for row in REVIEWED_CASES])
def test_public_master_one_exact_read_no_extract_credentials_or_broker(monkeypatch, symbol):
    issue = listing._REVIEWED[symbol]
    content = BytesIO()
    with zipfile.ZipFile(content, "w") as archive:
        archive.writestr(issue["board"] + "_code.mst", master_row(symbol))
    body = content.getvalue()

    class Response:
        status = 200
        def __enter__(self):
            return self
        def __exit__(self, *args):
            return False
        def geturl(self):
            return listing.master_url(issue["board"])
        def read(self, bound):
            assert bound == 2 * 1024 * 1024 + 1
            return body

    opened = Mock(return_value=Response())
    monkeypatch.setattr(listing.urllib.request, "build_opener", Mock(return_value=SimpleNamespace(open=opened)))
    result = listing.collect_master_identity(symbol, board=issue["board"], short_code=issue["short_code"])
    assert result["identity"]["standard_code"] == issue["isin"]
    assert result["identity"]["listing_date_raw"] == issue["first_regular_session"].replace("-", "")
    assert verify(result, symbol=symbol)["required_start"] == issue["first_regular_session"]
    assert opened.call_count == 1


@pytest.mark.parametrize("raw", [b"", master_row("278470.KS") * 2, b"\xff" * 300])
def test_empty_duplicate_or_invalid_master_never_binds(raw):
    with pytest.raises((ValueError, UnicodeDecodeError)):
        listing._parse_master(raw, board="kospi", short_code="278470")


@pytest.fixture
def broker(monkeypatch):
    kr._CACHE.clear()
    monkeypatch.setenv("TRADINGAGENTS_KIS_RESEARCH_FALLBACK_ENABLED", "1")
    monkeypatch.setattr(kr, "get_api_key", lambda _: "offline")
    monkeypatch.setattr(kr, "time", SimpleNamespace(monotonic=lambda: 10., sleep=lambda _: None))
    collect = Mock(side_effect=lambda symbol, **kwargs: metadata(symbol))
    monkeypatch.setattr(listing, "collect_master_identity", collect)
    monkeypatch.setattr("tradingagents.calendar_access.get_exchange_calendar",
                        lambda name, *, start, end: SimpleNamespace(sessions=pd.bdate_range(start, end)))
    monkeypatch.setattr("tradingagents.scheduled.market_calendar.is_supplemental_market_holiday", lambda **_: False)
    client = Mock()
    state = SimpleNamespace(symbol="278470.KS", missing=set(), bad=None)

    def reply(symbol, *, start_date, end_date, **kwargs):
        assert symbol == state.symbol[:6] and kwargs["adjusted_price"] == "0"
        first = listing._REVIEWED[state.symbol]["first_regular_session"]
        days = pd.bdate_range(first, END)
        rows = [{"stck_bsop_date": day.strftime("%Y%m%d"), "stck_oprc": "100", "stck_hgpr": "110",
                 "stck_lwpr": "90", "stck_clpr": "105", "acml_vol": "200"}
                for day in reversed(days) if start_date <= day.date() <= end_date
                and day.date().isoformat() not in state.missing]
        if state.bad:
            rows[-1].update(state.bad)
        return {"output2": rows[:100]}

    client.domestic_daily_itemchartprice.side_effect = reply
    monkeypatch.setattr(KisClient, "from_api_keys", Mock(return_value=client))
    yield client, collect, state
    kr._CACHE.clear()


@pytest.mark.parametrize("symbol", [row[0] for row in REVIEWED_CASES])
def test_complete_post_listing_series_pins_original_window_receipt_and_200_minimum(broker, symbol):
    client, collect, state = broker
    state.symbol = symbol
    frame = kr.load_kr_daily_bars(symbol, ORIGINAL, END, require_complete=True)
    first = listing._REVIEWED[symbol]["first_regular_session"]
    assert frame.attrs["requested_start"] == ORIGINAL and frame.attrs["required_start"] == first
    assert frame.iloc[0]["Date"] == pd.Timestamp(first)
    receipt = evidence._snapshot(symbol, END, kr.SOURCE, frame)
    assert receipt["status"] == "VERIFIED_RETRIEVED_SERIES"
    assert receipt["listing_contract"]["schema"] == listing.SCHEMA
    assert receipt["historical_vintage_verified"] is False
    assert "Original request start=" in kr.source_note(frame)
    before = client.domestic_daily_itemchartprice.call_count
    pd.testing.assert_frame_equal(kr.load_kr_daily_bars(symbol, ORIGINAL, END, require_complete=True), frame)
    assert client.domestic_daily_itemchartprice.call_count == before and collect.call_count == 1
    with pytest.raises(InsufficientIndicatorHistoryError, match="requires 200"):
        calculate_stockstats_indicator(frame.tail(199), symbol, "close_200_sma", END)


@pytest.mark.parametrize("missing", ["2025-09-19", "2024-02-27", END])
def test_listing_never_excuses_missing_regular_session(broker, missing):
    client, _, state = broker
    state.missing = {missing}
    with pytest.raises(VendorMalformedResponseError):
        kr.load_kr_daily_bars(state.symbol, ORIGINAL, END, require_complete=True)
    assert not kr._CACHE


def test_expired_current_metadata_rebinds_but_original_selected_proof_does_not_move(broker, clock):
    _, collect, state = broker
    frame = kr.load_kr_daily_bars(state.symbol, ORIGINAL, END, require_complete=True)
    token = activate_daily_history_selection()
    try:
        select_daily_history(state.symbol, END, kr.SOURCE, frame)
        clock.now += timedelta(seconds=301)
        selected = kr.selected_history(state.symbol, ORIGINAL, END)
        assert selected.attrs["listing_contract"] == frame.attrs["listing_contract"]
        renewed = kr.load_kr_daily_bars(state.symbol, ORIGINAL, END, require_complete=True)
        assert collect.call_count == 2
        assert renewed.attrs["listing_contract"]["metadata_identity"]["available_at"] != frame.attrs["listing_contract"]["metadata_identity"]["available_at"]
    finally:
        reset_daily_history_selection(token)


@pytest.mark.parametrize("field", ["required_start", "series_sha256", "listing_contract"])
def test_cached_or_selected_tampering_never_becomes_a_new_provider(broker, field):
    _, _, state = broker
    kr.load_kr_daily_bars(state.symbol, ORIGINAL, END, require_complete=True)
    key = (state.symbol, ORIGINAL, END)
    if field == "listing_contract":
        kr._CACHE[key][1].attrs[field]["metadata_identity"]["identity"]["standard_code"] = "KR7403870009"
    else:
        kr._CACHE[key][1].attrs[field] = "tampered"
    with pytest.raises(VendorInputError):
        kr.load_kr_daily_bars(state.symbol, ORIGINAL, END, require_complete=True)
    assert evidence._snapshot(state.symbol, END, kr.SOURCE, kr._CACHE[key][1])["status"] == "UNVERIFIED"


def test_bad_master_stops_before_price_or_cache_and_us_contract_cannot_be_relabelled(broker):
    client, collect, state = broker
    snapshot = metadata()
    snapshot["identity"]["security_group_token"] = "EF"
    collect.side_effect = None
    collect.return_value = snapshot
    with pytest.raises(VendorMalformedResponseError, match="listing evidence"):
        kr.load_kr_daily_bars(state.symbol, ORIGINAL, END, require_complete=True)
    client.domestic_daily_itemchartprice.assert_not_called()
    assert not kr._CACHE
    contract = verify()
    contract["schema"] = "tradingagents.verified-first-regular-listing/v1"
    with pytest.raises(ValueError, match="changed"):
        listing.validate_listing_receipt(state.symbol, contract, requested_start=ORIGINAL,
                                         end_date=END, observed_at=NOW)


def test_new_receipt_cannot_be_used_under_earlier_analysis_or_edited_series(broker):
    _, _, state = broker
    frame = kr.load_kr_daily_bars(state.symbol, ORIGINAL, END, require_complete=True)
    token = activate_daily_history_selection()
    try:
        select_daily_history(state.symbol, END, kr.SOURCE, frame)
        with run_config({"analysis_as_of": "2026-10-23"}), pytest.raises(VendorInputError):
            kr.load_kr_daily_bars(state.symbol, ORIGINAL, END, require_complete=True)
    finally:
        reset_daily_history_selection(token)
    frame.loc[0, "Close"] = 104
    assert evidence._snapshot(state.symbol, END, kr.SOURCE, frame)["status"] == "UNVERIFIED"


def test_raw_metadata_or_contract_extra_fields_never_leak_as_identity():
    snapshot = metadata()
    snapshot["private_or_price_field"] = "not identity"
    with pytest.raises(ValueError, match="fields"):
        verify(snapshot)
    receipt = verify()
    receipt["required_start"] = "2025-09-22"
    with pytest.raises(ValueError):
        listing.validate_listing_receipt("278470.KS", receipt, requested_start=ORIGINAL,
                                         end_date=END, observed_at=NOW)


def yahoo_series(symbol="278470.KS"):
    return pd.DataFrame({"Date": pd.bdate_range(listing._REVIEWED[symbol]["first_regular_session"], END),
                         "Open": 100., "High": 110., "Low": 90., "Close": 104., "Volume": 200.})


def known_yahoo_basis(frame, symbol="278470.KS"):
    # Explicit offline source-fetch hook with the same download(auto_adjust=True)
    # request used by the original getter. A cache read never invokes this hook.
    frame.attrs["observed_at"] = (NOW - timedelta(seconds=50)).isoformat()
    frame.attrs["adjustment"] = kr.YAHOO_ADJUSTMENT
    frame.attrs["yahoo_price_basis"] = kr._capture_yahoo_price_basis(frame, symbol, ORIGINAL, END,
        frame.attrs["observed_at"], method="download", auto_adjust=True)
    return frame


@pytest.mark.parametrize("symbol", [row[0] for row in REVIEWED_CASES])
def test_reviewed_primary_has_same_first_session_contract_but_yahoo_price_identity(broker, symbol):
    client, collect, _ = broker
    data = known_yahoo_basis(yahoo_series(symbol), symbol)
    result = kr.validate_with_kr_fallback(data, symbol, ORIGINAL, END)
    assert result.attrs["provider"] == "yfinance" and result.attrs["source"] == "yfinance"
    assert result.attrs["adjustment"] == kr.YAHOO_ADJUSTMENT
    assert result.attrs["observed_at"] == data.attrs["observed_at"]
    receipt = evidence._snapshot(symbol, END, "yfinance", result)
    assert receipt["status"] == "VERIFIED_RETRIEVED_SERIES"
    assert receipt["provider"] == "yfinance" and receipt["identity_provider"] == "KIS"
    assert receipt["listing_contract"]["required_start"] == listing._REVIEWED[symbol]["first_regular_session"]
    assert receipt["identity_verified_at"] == NOW.isoformat()
    assert receipt["price_request_basis"]["auto_adjust"] is True
    assert receipt["price_request_basis"]["method"] == "download"
    assert "OHLCV source: yfinance" in kr.source_note(result)
    client.domestic_daily_itemchartprice.assert_not_called()
    assert collect.call_count == 1


@pytest.mark.parametrize("missing", ["first", "2025-09-19"])
def test_primary_cannot_hide_first_or_interior_gap_and_replacement_reuses_identity(broker, missing):
    client, collect, state = broker
    data = yahoo_series()
    day = data.iloc[0]["Date"] if missing == "first" else pd.Timestamp(missing)
    data = data[data.Date != day]
    result = kr.validate_with_kr_fallback(data, state.symbol, ORIGINAL, END)
    assert result.attrs["source"] == kr.SOURCE and result.iloc[0]["Date"] == pd.Timestamp("2024-02-27")
    assert result.loc[result.Date == pd.Timestamp("2025-09-19"), "Close"].tolist() == [105.]
    assert client.domestic_daily_itemchartprice.call_count > 0 and collect.call_count == 1


def test_primary_and_replacement_both_missing_0919_still_fail(broker):
    _, _, state = broker
    state.missing = {"2025-09-19"}
    data = yahoo_series()
    with pytest.raises(VendorMalformedResponseError, match="missing required"):
        kr.validate_with_kr_fallback(data[data.Date != pd.Timestamp("2025-09-19")], state.symbol, ORIGINAL, END)
    assert not kr._CACHE


def test_mature_original_start_needs_no_identity_lookup_and_unknown_is_not_registered(broker):
    client, collect, _ = broker
    data = yahoo_series()
    result = kr.validate_with_kr_fallback(data.tail(3), "278470.KS", "2026-10-21", END)
    assert "listing_contract" not in result.attrs
    collect.assert_not_called()
    client.domestic_daily_itemchartprice.assert_not_called()
    assert "000999.KS" not in listing._REVIEWED
    with pytest.raises(ValueError, match="No reviewed"):
        verify(symbol="000999.KS", snapshot=metadata())


def test_reviewed_symbol_cannot_pass_primary_using_future_review(clock, broker):
    client, collect, _ = broker
    clock.now = datetime.fromisoformat("2026-10-25T19:45:00+00:00")
    with pytest.raises(VendorInputError, match="unavailable"):
        kr.validate_with_kr_fallback(yahoo_series(), "278470.KS", ORIGINAL, END)
    collect.assert_not_called()
    client.domestic_daily_itemchartprice.assert_not_called()


@pytest.mark.parametrize("target", ["http://new.real.download.dws.co.kr/common/master/kospi_code.mst.zip",
                                    "https://example.invalid/master"])
def test_runtime_master_redirect_refused_before_another_request(target):
    import urllib.error
    request = listing.urllib.request.Request(listing.master_url("kospi"))
    with pytest.raises(urllib.error.HTTPError):
        listing._NoRedirect().redirect_request(request, None, 302, "Moved", {}, target)


@pytest.mark.parametrize("bad", ["oversize_zip", "wrong_final", "duplicate_member", "oversize_member", "bad_zip"])
def test_runtime_public_master_bounds_and_ambiguity_fail_closed(monkeypatch, bad):
    body = b"not a zip"
    if bad == "oversize_zip":
        body = b"x" * (2 * 1024 * 1024 + 1)
    elif bad in {"duplicate_member", "oversize_member"}:
        stream = BytesIO()
        with zipfile.ZipFile(stream, "w") as archive:
            archive.writestr("kospi_code.mst", master_row("278470.KS"))
        body = stream.getvalue()

    class Response:
        status = 200
        def __enter__(self):
            return self
        def __exit__(self, *args):
            return False
        def geturl(self):
            return "http://invalid" if bad == "wrong_final" else listing.master_url("kospi")
        def read(self, bound):
            return body

    monkeypatch.setattr(listing.urllib.request, "build_opener", Mock(return_value=SimpleNamespace(open=lambda *a, **kw: Response())))
    if bad in {"duplicate_member", "oversize_member"}:
        fake = Mock()
        fake.__enter__ = Mock(return_value=fake)
        fake.__exit__ = Mock(return_value=False)
        fake.namelist.return_value = ["kospi_code.mst"] * (2 if bad == "duplicate_member" else 1)
        fake.getinfo.return_value = SimpleNamespace(file_size=10 * 1024 * 1024 + 1)
        monkeypatch.setattr(listing.zipfile, "ZipFile", Mock(return_value=fake))
    with pytest.raises((ValueError, zipfile.BadZipFile)):
        listing.collect_master_identity("278470.KS", board="kospi", short_code="278470")


def test_yahoo_missing_original_price_clock_uses_complete_kis_replacement_without_renewing_cache_clock(broker):
    client, collect, state = broker
    data = yahoo_series()
    assert "observed_at" not in data.attrs
    result = kr.validate_with_kr_fallback(data, state.symbol, ORIGINAL, END)
    assert result.attrs["source"] == kr.SOURCE and result.attrs["provider"] == "kis"
    assert "observed_at" not in data.attrs
    assert collect.call_count == 1 and client.domestic_daily_itemchartprice.call_count > 0
    assert evidence._snapshot(state.symbol, END, kr.SOURCE, result)["status"] == "VERIFIED_RETRIEVED_SERIES"


def test_unknown_yahoo_clock_stays_unverified_when_no_replacement_exists(broker):
    client, _, state = broker
    client.domestic_daily_itemchartprice.return_value = {"output2": []}
    client.domestic_daily_itemchartprice.side_effect = None
    with pytest.raises(VendorMalformedResponseError, match="no requested bars"):
        kr.validate_with_kr_fallback(yahoo_series(), state.symbol, ORIGINAL, END)
    assert not kr._CACHE


def test_local_identity_clock_does_not_become_vendor_price_observation(broker):
    _, _, state = broker
    data = known_yahoo_basis(yahoo_series())
    frame = kr.validate_with_kr_fallback(data, state.symbol, ORIGINAL, END)
    del frame.attrs["observed_at"]
    receipt = evidence._snapshot(state.symbol, END, "yfinance", frame)
    assert receipt["status"] == "UNVERIFIED"
    assert "observed_at" not in receipt


@pytest.mark.parametrize("symbol", ["064400.KS", "411080.KQ"])
def test_later_extraction_of_old_master_does_not_renew_300_second_availability(symbol):
    snapshot = metadata(symbol)
    snapshot["collection_started_at"] = "2026-10-25T21:12:40+00:00"
    snapshot["available_at"] = "2026-10-25T21:12:42.022291+00:00"
    with pytest.raises(ValueError, match="current KR master"):
        verify(snapshot, symbol=symbol, analysis_as_of="2026-10-25T21:30:00+00:00")


@pytest.mark.parametrize("age,accepted", [(300, True), (300.000001, False)])
def test_metadata_300_second_boundary_is_not_extended(age, accepted):
    snapshot = metadata()
    available = NOW - timedelta(seconds=age)
    snapshot["available_at"] = available.isoformat()
    snapshot["collection_started_at"] = (available - timedelta(seconds=1)).isoformat()
    if accepted:
        assert verify(snapshot)["required_start"] == "2024-02-27"
    else:
        with pytest.raises(ValueError, match="current KR master"):
            verify(snapshot)


def test_future_analysis_cutoff_is_rejected_even_if_current_metadata_is_fresh():
    with pytest.raises(ValueError, match="Unavailable"):
        verify(analysis_as_of=NOW + timedelta(seconds=1))


@pytest.mark.parametrize("symbol", ["278470.KQ", "403870.KS", "064400.KQ", "411080.KS"])
def test_reviewed_wrong_board_cannot_be_treated_as_unreviewed_legacy(broker, symbol):
    client, collect, _ = broker
    with pytest.raises(VendorInputError, match="suffix"):
        kr.validate_with_kr_fallback(yahoo_series(), symbol, ORIGINAL, END)
    collect.assert_not_called()
    client.domestic_daily_itemchartprice.assert_not_called()


@pytest.mark.parametrize("basis", [None, "UNVERIFIED_PROVIDER_ADJUSTMENT_BASIS", "ARBITRARY_UNKNOWN_BASIS",
                                  "FID_ORG_ADJ_PRC=0", "YFINANCE_AUTO_ADJUST_FALSE"])
def test_unknown_adjustment_even_with_price_clock_uses_entire_kis_replacement(broker, basis):
    client, collect, state = broker
    data = known_yahoo_basis(yahoo_series())
    if basis is None:
        data.attrs.pop("adjustment")
    else:
        data.attrs["adjustment"] = basis
    original = data.copy()
    result = kr.validate_with_kr_fallback(data, state.symbol, ORIGINAL, END)
    pd.testing.assert_frame_equal(data, original)
    assert result.attrs["source"] == kr.SOURCE and result["Close"].eq(105).all()
    assert collect.call_count == 1 and client.domestic_daily_itemchartprice.call_count > 0


def test_unknown_adjustment_and_unavailable_replacement_cannot_return_verified_primary(broker):
    client, _, state = broker
    client.domestic_daily_itemchartprice.side_effect = None
    client.domestic_daily_itemchartprice.return_value = {"output2": []}
    data = yahoo_series()
    data.attrs["observed_at"] = NOW.isoformat()
    with pytest.raises(VendorMalformedResponseError):
        kr.validate_with_kr_fallback(data, state.symbol, ORIGINAL, END)
    assert not kr._CACHE


@pytest.mark.parametrize("kind", ["unknown_label", "missing_proof", "future_clock", "changed_auto_adjust_rehashed",
                                 "plain_dict_rehashed", "changed_series_rehashed"])
def test_manual_or_rehashed_basis_claims_are_not_verified_price_evidence(broker, kind):
    _, _, state = broker
    frame = kr.validate_with_kr_fallback(known_yahoo_basis(yahoo_series()), state.symbol, ORIGINAL, END)
    if kind == "unknown_label":
        frame.attrs["adjustment"] = "UNKNOWN"
    elif kind == "missing_proof":
        frame.attrs.pop("yahoo_price_basis")
    elif kind == "future_clock":
        frame.attrs["observed_at"] = (NOW + timedelta(seconds=1)).isoformat()
    else:
        claim = kr.verified_yahoo_basis(frame, state.symbol, ORIGINAL, END)
        claim.pop("basis_id")
        if kind == "changed_auto_adjust_rehashed":
            claim["auto_adjust"] = False
        elif kind == "changed_series_rehashed":
            frame.loc[0, "Close"] = 103.
            claim["series_sha256"] = hashlib.sha256(frame.to_csv(index=False).encode()).hexdigest()
            frame.attrs["series_sha256"] = claim["series_sha256"]
        claim["basis_id"] = hashlib.sha256(json.dumps(claim, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        frame.attrs["yahoo_price_basis"] = claim
    assert evidence._snapshot(state.symbol, END, "yfinance", frame)["status"] == "UNVERIFIED"
    with pytest.raises(VendorInputError):
        kr._listing_start(frame, state.symbol, END)


@pytest.mark.parametrize("method,auto", [("download", False), ("download", 1), ("history", True), ("csv_cache", True)])
def test_source_basis_factory_cannot_claim_unrequested_or_default_adjustments(method, auto):
    with pytest.raises(ValueError):
        kr._capture_yahoo_price_basis(yahoo_series(), "278470.KS", ORIGINAL, END,
                                      NOW.isoformat(), method=method, auto_adjust=auto)


@pytest.mark.parametrize("claims", [
    {"source": kr.SOURCE, "provider": "yfinance", "adjustment": "ARBITRARY_UNKNOWN_BASIS"},
    {"source": kr.SOURCE, "provider": "kis", "adjustment": "FID_ORG_ADJ_PRC=0"},
    {"source": "yfinance", "provider": "kis", "adjustment": kr.YAHOO_ADJUSTMENT},
])
def test_unselected_provider_strings_never_relabel_yahoo_values_as_kis(broker, claims):
    client, collect, state = broker
    data = known_yahoo_basis(yahoo_series())
    data.attrs.update(claims)
    original = data.copy()
    result = kr.validate_with_kr_fallback(data, state.symbol, ORIGINAL, END)
    assert data["Close"].eq(104).all() and result["Close"].eq(105).all()
    pd.testing.assert_frame_equal(data, original)
    assert result.attrs["provider"] == "kis" and collect.call_count == 1
    assert client.domestic_daily_itemchartprice.call_count > 0


@pytest.mark.parametrize("end", ["2026-10-27", "2026-02-30", "20261023"])
def test_source_basis_factory_rejects_future_or_unverified_window(end):
    with pytest.raises(ValueError):
        kr._capture_yahoo_price_basis(yahoo_series(), "278470.KS", ORIGINAL, end,
                                      NOW.isoformat(), method="download", auto_adjust=True)
