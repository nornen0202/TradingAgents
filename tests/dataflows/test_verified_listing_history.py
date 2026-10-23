"""Offline issuer binding, availability and complete post-listing history contracts."""
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import Mock

import pandas as pd
import pytest

from tradingagents.dataflows import security_listing as listing, us_daily_history as us
from tradingagents.dataflows.config import run_config
from tradingagents.dataflows.daily_history_evidence import _snapshot
from tradingagents.dataflows.stockstats_utils import calculate_stockstats_indicator
from tradingagents.dataflows.vendor_exceptions import InsufficientIndicatorHistoryError, VendorInputError, VendorMalformedResponseError
from tradingagents.portfolio.kis import KisClient


END = "2026-10-21"
ORIGINAL = "2021-10-21"
FIRST = "2024-04-02"
ASOF = datetime(2026, 10, 21, 23, 59, tzinfo=timezone.utc)


def metadata():
    return {
        "schema": "kis.current-security-metadata/v1", "provider": "KIS", "environment": "real",
        "symbol": "GEV", "exchange": "NYS", "product_type": "513",
        "collection_started_at": "2026-10-21T23:58:58+00:00",
        "available_at": "2026-10-21T23:58:59+00:00",
        "payload": {"rt_cd": "0", "output": {
            "std_pdno": "US36828A1016", "istt_usge_isin_cd": "US36828A1016",
            "prdt_eng_name": "GE VERNOVA INC", "ovrs_excg_cd": "NYSE", "tr_crcy_cd": "USD",
            "lstg_dt": "20240402", "lstg_yn": "Y", "lstg_abol_item_yn": "N",
            "lstg_abol_dt": "", "chng_bf_pdno": "", "ovrs_now_pric1": "untrusted-price",
        }},
    }


@pytest.fixture
def reviewed(monkeypatch):
    # Fixtures predate production review; this is an explicit mocked review clock.
    issue = deepcopy(listing._REVIEWED["GEV"])
    issue["evidence_available_at"] = "2026-10-20T00:00:00+00:00"
    monkeypatch.setattr(listing, "_REVIEWED", {"GEV": issue})
    return issue


def verify(data=None, *, cutoff=ASOF):
    return listing.verify_listing_contract("GEV", metadata() if data is None else data,
                                          requested_start=ORIGINAL, end_date=END, analysis_as_of=cutoff)


def test_current_binding_carries_original_window_issuer_and_availability(reviewed):
    result = verify()
    assert result["original_requested_start"] == ORIGINAL
    assert result["required_start"] == FIRST
    assert result["reviewed_event"]["cusip"] == "36828A101"
    assert result["metadata_identity"]["available_at"] == metadata()["available_at"]
    assert result["historical_vintage_verified"] is False
    assert len(result["contract_id"]) == 64
    assert "untrusted-price" not in str(result)
    assert listing.validate_listing_receipt("GEV", result, requested_start=ORIGINAL,
                                            end_date=END, observed_at=ASOF) == result


@pytest.mark.parametrize("field,value", [
    ("std_pdno", "US0378331005"), ("istt_usge_isin_cd", "US0378331005"),
    ("ovrs_excg_cd", "NAS"), ("tr_crcy_cd", "EUR"), ("prdt_eng_name", "OTHER COMPANY"),
    ("lstg_dt", "20240327"), ("lstg_dt", "20260230"), ("lstg_dt", None),
    ("lstg_yn", "N"), ("lstg_abol_item_yn", "Y"), ("lstg_abol_item_yn", None),
    ("lstg_abol_dt", "20261020"), ("chng_bf_pdno", "OLD"), ("chng_bf_pdno", None),
])
def test_conflicts_relisting_and_invalid_dates_never_bound_history(reviewed, field, value):
    data = metadata()
    data["payload"]["output"][field] = value
    with pytest.raises(ValueError):
        verify(data)


@pytest.mark.parametrize("key,value", [
    ("available_at", None), ("available_at", "bad"),
    ("available_at", "2026-10-21T23:58:59"),
    ("available_at", "2026-10-22T00:00:00+00:00"),
    ("available_at", "2026-10-21T23:50:00+00:00"),
    ("symbol", "OTHER"), ("exchange", "NAS"), ("environment", "demo"),
    ("payload", {}), ("payload", {"rt_cd": "0", "output": []}),
])
def test_missing_future_stale_and_wrong_request_evidence_rejected(reviewed, key, value):
    data = metadata()
    data[key] = value
    with pytest.raises((ValueError, KeyError)):
        verify(data)


def test_actual_review_is_unavailable_before_collection_not_backdated(monkeypatch):
    client = Mock()
    collect = Mock(side_effect=AssertionError("historical metadata request forbidden"))
    monkeypatch.setattr(listing, "collect_security_metadata", collect)
    assert listing.collect_listing_contract("GEV", client, requested_start=ORIGINAL, end_date=END) is None
    collect.assert_not_called()
    with pytest.raises(ValueError, match="Unavailable"):
        verify()


@pytest.mark.parametrize("change", [
    {"event_kind": "EXCHANGE_TRANSFER"}, {"event_kind": "WHEN_ISSUED"},
    {"event_kind": "RELISTING"}, {"security_class": "ADR"},
    {"evidence_available_at": "2026-10-22T00:00:00+00:00"},
])
def test_only_reviewed_first_regular_common_stock_events_qualify(reviewed, monkeypatch, change):
    issue = {**reviewed, **change}
    monkeypatch.setattr(listing, "_REVIEWED", {"GEV": issue})
    with pytest.raises(ValueError):
        verify()


def test_mature_and_unknown_symbols_make_no_metadata_requests(reviewed, monkeypatch):
    collect = Mock(side_effect=AssertionError("no metadata lookup"))
    monkeypatch.setattr(listing, "collect_security_metadata", collect)
    assert listing.collect_listing_contract("AAPL", Mock(), requested_start=ORIGINAL, end_date=END) is None
    assert listing.collect_listing_contract("GEV", Mock(), requested_start=FIRST, end_date=END) is None
    collect.assert_not_called()


@pytest.mark.parametrize("field,value", [
    ("required_start", "2025-01-01"), ("original_requested_start", "2026-01-01"),
    ("contract_id", "f" * 64), ("reviewed_event_sha256", "f" * 64),
    ("metadata_payload_sha256", "not-a-hash"),
])
def test_cached_or_decorative_contract_tampering_is_not_accepted(reviewed, field, value):
    contract = verify()
    contract[field] = value
    with pytest.raises(ValueError):
        listing.validate_listing_receipt("GEV", contract, requested_start=ORIGINAL, end_date=END, observed_at=ASOF)


@pytest.fixture
def broker(reviewed, monkeypatch):
    us._CACHE.clear()
    monkeypatch.setenv("TRADINGAGENTS_KIS_RESEARCH_FALLBACK_ENABLED", "1")
    monkeypatch.setattr(us, "get_api_key", lambda _: "offline")
    monkeypatch.setattr(us, "time", SimpleNamespace(monotonic=lambda: 10., sleep=lambda _: None))
    monkeypatch.setattr(listing, "cutoff_for_day", lambda _: ASOF)
    monkeypatch.setattr(listing, "collect_security_metadata", Mock(return_value=metadata()))
    monkeypatch.setattr(us, "_sessions", lambda a, b: [d.date() for d in pd.bdate_range(a, b)])
    days = [d.date() for d in pd.bdate_range(FIRST, END)]
    rows = [{"xymd": d.strftime("%Y%m%d"), "open": "100", "high": "110",
             "low": "90", "clos": "105", "tvol": "200"} for d in reversed(days)]
    client = Mock()
    def reply(**kwargs):
        assert kwargs["params"]["EXCD"] == "NYS"
        cursor = kwargs["params"]["BYMD"]
        return {"output2": [deepcopy(r) for r in rows if r["xymd"] <= cursor][:100]}, {}
    client.request_json.side_effect = reply
    monkeypatch.setattr(KisClient, "from_api_keys", Mock(return_value=client))
    yield client, rows
    us._CACHE.clear()


def test_full_post_listing_series_retains_original_request_receipt_and_minimums(broker):
    client, rows = broker
    result = us.load_us_daily_bars("GEV", "2026-10-20", END)
    assert result.attrs["requested_start"] == ORIGINAL
    assert result.attrs["required_start"] == FIRST
    assert result.iloc[0]["Date"] == pd.Timestamp(FIRST)
    assert len(result) == len(rows)
    assert len(rows) > 200
    assert all(call.kwargs["params"]["MODP"] == "1" for call in client.request_json.call_args_list)
    receipt = _snapshot("GEV", END, us.SOURCE, result)
    assert receipt["status"] == "VERIFIED_RETRIEVED_SERIES"
    assert receipt["requested_start"] == ORIGINAL
    assert receipt["listing_contract"]["required_start"] == FIRST
    assert "untrusted-price" not in str(receipt)
    assert "verified first regular session" in us.source_note(result)
    before = client.request_json.call_count
    pd.testing.assert_frame_equal(us.load_us_daily_bars("GEV", "2026-10-20", END), result)
    assert client.request_json.call_count == before
    short = result.tail(5).copy()
    with pytest.raises(InsufficientIndicatorHistoryError):
        calculate_stockstats_indicator(short, "GEV", "close_200_sma", END)


@pytest.mark.parametrize("bad_day", [FIRST, "2024-04-03", END])
def test_missing_regular_session_cannot_hide_behind_listing_contract(broker, bad_day):
    _, rows = broker
    rows[:] = [r for r in rows if r["xymd"] != bad_day.replace("-", "")]
    with pytest.raises(VendorMalformedResponseError):
        us.load_us_daily_bars("GEV", "2026-10-20", END)
    assert not us._CACHE


def test_invalid_regular_bar_is_never_discarded(broker):
    _, rows = broker
    rows[-2]["high"] = "99"
    with pytest.raises(VendorMalformedResponseError, match="OHLCV"):
        us.load_us_daily_bars("GEV", "2026-10-20", END)


def test_only_verified_pre_regular_period_is_excluded_explicitly(broker):
    _, rows = broker
    rows.append({"xymd": "20240327", "open": "bad", "high": "bad"})
    result = us.load_us_daily_bars("GEV", "2026-10-20", END)
    assert result.attrs["excluded_before_verified_regular_listing"] == ["2024-03-27"]
    assert result.iloc[0]["Date"] == pd.Timestamp(FIRST)


def test_receipt_rejects_changed_binding_and_listing_bounds(broker):
    result = us.load_us_daily_bars("GEV", "2026-10-20", END)
    result.attrs["listing_contract"]["metadata_identity"]["payload"]["output"]["std_pdno"] = "OTHER"
    assert _snapshot("GEV", END, us.SOURCE, result)["status"] == "UNVERIFIED"


def test_metadata_time_consumes_original_history_deadline(broker, monkeypatch):
    client, _ = broker
    ticks = iter([0., 121.])
    monkeypatch.setattr(us, "time", SimpleNamespace(monotonic=lambda: next(ticks), sleep=lambda _: None))
    with pytest.raises(VendorMalformedResponseError, match="time limit"):
        us.load_us_daily_bars("GEV", "2026-10-20", END)
    client.request_json.assert_not_called()


def test_analysis_day_can_follow_last_price_day_without_backdating(reviewed, monkeypatch):
    data = metadata()
    data['collection_started_at'] = '2026-10-22T01:00:00+00:00'
    data['available_at'] = '2026-10-22T01:00:01+00:00'
    cutoff = datetime(2026, 10, 22, 1, 0, 2, tzinfo=timezone.utc)
    # NY Oct 21 evening is already Oct 22 UTC, and remains within analysis day Oct 21.
    contract = listing.verify_listing_contract('GEV', data, requested_start=ORIGINAL,
                                               end_date=END, analysis_as_of=cutoff)
    assert contract['requested_end'] == END
    assert contract['metadata_identity']['available_at'] == data['available_at']
    with pytest.raises(ValueError):
        listing.verify_listing_contract('GEV', data, requested_start=ORIGINAL, end_date=END,
                                        analysis_as_of=datetime(2026, 10, 21, 23, 59, tzinfo=timezone.utc))


def test_scoped_analysis_day_and_new_york_boundary_are_used():
    with run_config({'analysis_as_of': '2026-10-21'}):
        cutoff = listing.cutoff_for_day('2026-10-20')
        assert cutoff == datetime(2026, 10, 22, 3, 59, 59, 999999, tzinfo=timezone.utc)
        with pytest.raises(VendorInputError):
            listing.cutoff_for_day('2026-10-22')


def test_new_collection_can_only_support_explicit_later_analysis(reviewed, monkeypatch):
    from zoneinfo import ZoneInfo
    now = datetime.now(timezone.utc)
    analysis_day = now.astimezone(ZoneInfo('America/New_York')).date().isoformat()
    data = metadata()
    data['collection_started_at'] = (now - timedelta(seconds=2)).isoformat()
    data['available_at'] = (now - timedelta(seconds=1)).isoformat()
    monkeypatch.setattr(listing, 'collect_security_metadata', Mock(return_value=data))
    with run_config({'analysis_as_of': analysis_day}):
        contract = listing.collect_listing_contract('GEV', Mock(), requested_start=ORIGINAL, end_date=END)
        assert contract is not None
        assert contract['requested_end'] == END
        assert datetime.fromisoformat(contract['analysis_as_of']) >= datetime.fromisoformat(data['available_at'])
    with run_config({'analysis_as_of': END}):
        with pytest.raises(VendorMalformedResponseError):
            listing.collect_listing_contract('GEV', Mock(), requested_start=ORIGINAL, end_date=END)


def test_failed_binding_stops_before_price_calls_or_cache(broker, monkeypatch):
    client, _ = broker
    monkeypatch.setattr(listing, 'collect_security_metadata', Mock(side_effect=RuntimeError('offline failed read')))
    with pytest.raises(VendorMalformedResponseError, match='listing evidence unavailable'):
        us.load_us_daily_bars('GEV', '2026-10-20', END)
    client.request_json.assert_not_called()
    assert not us._CACHE


def test_expired_metadata_requires_new_binding_even_with_price_cache(broker, monkeypatch):
    client, _ = broker
    first = us.load_us_daily_bars('GEV', '2026-10-20', END)
    previous_calls = client.request_json.call_count
    later = ASOF + timedelta(seconds=300)
    fresh = metadata()
    fresh['collection_started_at'] = (later - timedelta(seconds=2)).isoformat()
    fresh['available_at'] = (later - timedelta(seconds=1)).isoformat()
    monkeypatch.setattr(listing, 'cutoff_for_day', lambda _: later)
    monkeypatch.setattr(listing, 'collect_security_metadata', Mock(return_value=fresh))
    second = us.load_us_daily_bars('GEV', '2026-10-20', END)
    assert client.request_json.call_count > previous_calls
    assert first.attrs['listing_contract']['contract_id'] != second.attrs['listing_contract']['contract_id']
    pd.testing.assert_frame_equal(first, second)


def test_price_and_indicator_selection_pin_the_full_regular_series(broker):
    from tradingagents.dataflows.daily_history_selection import select_daily_history
    with run_config({}):
        full = us.load_us_daily_bars('GEV', '2026-10-20', END)
        select_daily_history('GEV', END, us.SOURCE, full)
        pinned = us.selected_history('GEV', ORIGINAL, END)
        assert pinned.iloc[0]['Date'] == pd.Timestamp(FIRST)
        assert pinned.attrs['series_sha256'] == full.attrs['series_sha256']
        assert pinned.attrs['listing_contract'] == full.attrs['listing_contract']
        with pytest.raises(VendorMalformedResponseError, match='pinned'):
            us.selected_history('GEV', '2020-01-01', END)


def test_original_finished_research_cannot_adopt_later_review_but_new_analysis_can():
    data = metadata()
    data['collection_started_at'] = '2026-10-23T01:20:11+00:00'
    data['available_at'] = '2026-10-23T01:20:12+00:00'
    old_finished = datetime(2026, 10, 22, 13, 12, 10, tzinfo=timezone.utc)
    with pytest.raises(ValueError, match='Unavailable'):
        listing.verify_listing_contract('GEV', data, requested_start='2021-10-22',
                                        end_date='2026-10-22', analysis_as_of=old_finished)
    current = datetime(2026, 10, 23, 1, 20, 13, tzinfo=timezone.utc)
    result = listing.verify_listing_contract('GEV', data, requested_start='2021-10-22',
                                             end_date='2026-10-22', analysis_as_of=current)
    assert result['analysis_as_of'] == current.isoformat()
    assert result['requested_end'] == '2026-10-22'
    assert result['required_start'] == FIRST


def test_non_session_reviewed_first_date_is_rejected_before_prices(broker, monkeypatch):
    client, _ = broker
    original_sessions = us._sessions
    monkeypatch.setattr(us, '_sessions', lambda a, b: [day for day in original_sessions(a, b)
                                                    if day.isoformat() != FIRST])
    with pytest.raises(VendorMalformedResponseError, match='first regular listing'):
        us.load_us_daily_bars('GEV', '2026-10-20', END)
    client.request_json.assert_not_called()
