"""Offline identity, corporate-action and complete ADS-successor history checks."""
from copy import deepcopy
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import Mock

import pandas as pd
import pytest

from tradingagents.dataflows import security_listing as listing, us_daily_history as us
from tradingagents.dataflows.daily_history_evidence import _snapshot
from tradingagents.dataflows.stockstats_utils import calculate_stockstats_indicator
from tradingagents.dataflows.vendor_exceptions import InsufficientIndicatorHistoryError, VendorMalformedResponseError
from tradingagents.portfolio.kis import KisClient


FIRST = "2022-02-01"
END = "2026-10-23"
ORIGINAL = "2021-10-23"
ASOF = datetime(2026, 10, 24, 12, tzinfo=timezone.utc)


def metadata():
    return {
        "schema": "kis.current-security-metadata/v1", "provider": "KIS", "environment": "real",
        "symbol": "SHEL", "exchange": "NYS", "product_type": "513",
        "collection_started_at": "2026-10-24T11:59:58+00:00",
        "available_at": "2026-10-24T11:59:59+00:00",
        "payload": {"rt_cd": "0", "output": {
            "std_pdno": "US7802593050", "istt_usge_isin_cd": "US7802593050",
            "prdt_eng_name": "SHELL PLC SPON ADS EA REP 2 ORD SHS", "ovrs_excg_cd": "NYSE",
            "tr_crcy_cd": "USD", "lstg_dt": "20220201", "sedol_no": "BPK3CG3",
            "lstg_yn": "Y", "lstg_abol_item_yn": "N", "lstg_abol_dt": "", "chng_bf_pdno": "",
            "ovrs_now_pric1": "not-research-evidence", "tax_levy_yn": "not-cost-evidence",
        }},
    }


@pytest.fixture
def reviewed(monkeypatch):
    # Counterfactual offline fixtures explicitly override the review clock.
    # Production evidence remains unavailable before its actual October 25 read.
    issue = deepcopy(listing._REVIEWED["SHEL"])
    issue["evidence_available_at"] = "2026-10-23T00:00:00+00:00"
    monkeypatch.setattr(listing, "_REVIEWED", {**listing._REVIEWED, "SHEL": issue})
    return issue


def verify(data=None, *, cutoff=ASOF):
    return listing.verify_listing_contract("SHEL", metadata() if data is None else data,
        requested_start=ORIGINAL, end_date=END, analysis_as_of=cutoff)


def test_successor_is_distinct_from_spinoff_and_preserves_the_five_year_request(reviewed):
    receipt = verify()
    event = receipt["reviewed_event"]
    assert event["security_class"] == "SPONSORED_ADS"
    assert event["event_kind"] == "ADS_CLASS_UNIFICATION_SUCCESSOR"
    assert event["ordinary_shares_per_ads"] == 2
    assert event["when_issued_session"] == "2022-01-31"
    assert event["first_regular_session"] == FIRST
    assert receipt["original_requested_start"] == ORIGINAL
    assert receipt["scope"] == "ALL_REGULAR_SESSIONS_OF_VERIFIED_ADS_SUCCESSOR_WITHIN_ORIGINAL_WINDOW"
    assert receipt["metadata_identity"]["payload"]["output"]["sedol_no"] == "BPK3CG3"
    assert "not-research-evidence" not in str(receipt)
    assert "not-cost-evidence" not in str(receipt)
    assert receipt["historical_vintage_verified"] is False
    assert listing.validate_listing_receipt("SHEL", receipt, requested_start=ORIGINAL,
                                           end_date=END, observed_at=ASOF) == receipt


@pytest.mark.parametrize("field,value", [
    ("std_pdno", "US7802592060"), ("istt_usge_isin_cd", "US7802591070"),
    ("ovrs_excg_cd", "LSE"), ("tr_crcy_cd", "GBP"),
    ("prdt_eng_name", "SHELL PLC ORDINARY SHARES"),
    ("prdt_eng_name", "SHELL PLC SPON ADS EA REP 1 ORD SHS"),
    ("sedol_no", None), ("sedol_no", "B03MM62"),
    ("lstg_dt", "20220131"), ("lstg_dt", "20220230"), ("lstg_dt", None),
    ("lstg_yn", "N"), ("lstg_abol_item_yn", "Y"), ("chng_bf_pdno", "RDS.A"),
    ("chng_bf_pdno", None), ("lstg_abol_dt", "20261020"),
])
def test_conflicting_identity_ratio_class_predecessor_and_dates_are_rejected(reviewed, field, value):
    data = metadata()
    data["payload"]["output"][field] = value
    with pytest.raises(ValueError):
        verify(data)


@pytest.mark.parametrize("key,value", [
    ("available_at", None), ("available_at", "bad"),
    ("available_at", "2026-10-24T11:59:59"),
    ("available_at", "2026-10-24T12:00:01+00:00"),
    ("available_at", "2026-10-24T11:50:00+00:00"),
    ("symbol", "SHELL"), ("exchange", "NAS"), ("environment", "demo"),
    ("payload", {}), ("payload", {"rt_cd": "0", "output": {}}),
])
def test_empty_missing_future_naive_and_wrong_context_fail_closed(reviewed, key, value):
    data = metadata()
    data[key] = value
    with pytest.raises((ValueError, KeyError)):
        verify(data)


@pytest.mark.parametrize("change", [
    {"ordinary_shares_per_ads": 1}, {"ordinary_shares_per_ads": True},
    {"security_class": "COMMON_STOCK"}, {"event_kind": "SPIN_OFF_FIRST_REGULAR_COMMON_STOCK"},
    {"underlying_isin": "US7802592060"}, {"predecessors": []},
    {"history_policy": "MIX_PREDECESSOR_BARS"}, {"when_issued_session": FIRST},
])
def test_ads_event_cannot_be_reclassified_or_used_to_splice_predecessors(reviewed, monkeypatch, change):
    monkeypatch.setattr(listing, "_REVIEWED", {"SHEL": {**reviewed, **change}})
    with pytest.raises(ValueError):
        verify()


def test_real_review_cannot_be_applied_to_old_analyses(monkeypatch):
    collect = Mock(side_effect=AssertionError("No current collection for past analysis"))
    monkeypatch.setattr(listing, "collect_security_metadata", collect)
    with pytest.raises(ValueError, match="Unavailable"):
        verify()
    monkeypatch.setattr(listing, "cutoff_for_day", lambda _: ASOF)
    assert listing.collect_listing_contract("SHEL", Mock(), requested_start=ORIGINAL, end_date=END) is None
    collect.assert_not_called()


@pytest.mark.parametrize("field,value", [
    ("required_start", "2022-01-31"), ("contract_id", "f" * 64),
    ("reviewed_event_sha256", "f" * 64), ("metadata_payload_sha256", "bad"),
])
def test_replayed_receipt_is_rebuilt_and_tampering_is_rejected(reviewed, field, value):
    receipt = verify()
    receipt[field] = value
    with pytest.raises(ValueError):
        listing.validate_listing_receipt("SHEL", receipt, requested_start=ORIGINAL, end_date=END, observed_at=ASOF)


@pytest.fixture
def broker(reviewed, monkeypatch):
    us._CACHE.clear()
    monkeypatch.setenv("TRADINGAGENTS_KIS_RESEARCH_FALLBACK_ENABLED", "1")
    monkeypatch.setattr(us, "get_api_key", lambda _: "offline")
    monkeypatch.setattr(us, "time", SimpleNamespace(monotonic=lambda: 10., sleep=lambda _: None))
    monkeypatch.setattr(listing, "cutoff_for_day", lambda _: ASOF)
    monkeypatch.setattr(listing, "collect_security_metadata", Mock(return_value=metadata()))
    monkeypatch.setattr(us, "_sessions", lambda a, b: [d.date() for d in pd.bdate_range(a, b)])
    rows = [{"xymd": d.strftime("%Y%m%d"), "open": "100", "high": "110", "low": "90",
             "clos": "105", "tvol": "200"} for d in reversed(pd.bdate_range(FIRST, END))]
    client = Mock()
    def reply(**kwargs):
        assert kwargs["params"]["EXCD"] == "NYS"
        assert kwargs["params"]["SYMB"] == "SHEL"
        cursor = kwargs["params"]["BYMD"]
        return {"output2": [deepcopy(r) for r in rows
                            if not str(r.get("xymd", "")).isdigit() or r["xymd"] <= cursor][:100]}, {}
    client.request_json.side_effect = reply
    monkeypatch.setattr(KisClient, "from_api_keys", Mock(return_value=client))
    yield client, rows
    us._CACHE.clear()


def test_all_successor_sessions_are_required_and_when_issued_is_excluded(broker):
    client, rows = broker
    rows.append({"xymd": "20220131", "open": "bad-when-issued-not-regular"})
    result = us.load_us_daily_bars("SHEL", "2026-10-22", END)
    assert result.iloc[0]["Date"] == pd.Timestamp(FIRST)
    assert result.attrs["requested_start"] == ORIGINAL
    assert result.attrs["required_start"] == FIRST
    assert result.attrs["excluded_before_verified_regular_listing"] == ["2022-01-31"]
    assert len(result) == len(rows) - 1 > 200
    assert all(c.kwargs["params"]["MODP"] == "1" for c in client.request_json.call_args_list)
    assert _snapshot("SHEL", END, us.SOURCE, result)["listing_contract"]["required_start"] == FIRST
    with pytest.raises(InsufficientIndicatorHistoryError):
        calculate_stockstats_indicator(result.tail(5).copy(), "SHEL", "close_200_sma", END)


@pytest.mark.parametrize("bad_day", [FIRST, "2022-02-02", END])
def test_missing_any_required_regular_bar_still_fails(broker, bad_day):
    _, rows = broker
    rows[:] = [row for row in rows if row["xymd"] != bad_day.replace("-", "")]
    with pytest.raises(VendorMalformedResponseError):
        us.load_us_daily_bars("SHEL", "2026-10-22", END)
    assert not us._CACHE


@pytest.mark.parametrize("bad", [{"xymd": "bad"}, {"xymd": "20260230"}, {"open": "100"}])
def test_bad_dates_cannot_hide_behind_ads_contract(broker, bad):
    _, rows = broker
    rows.insert(0, bad)
    with pytest.raises(VendorMalformedResponseError):
        us.load_us_daily_bars("SHEL", "2026-10-22", END)


def test_empty_history_is_not_covered_by_an_identity_receipt(broker):
    client, _ = broker
    client.request_json.side_effect = None
    client.request_json.return_value = {"output2": []}, {}
    with pytest.raises(VendorMalformedResponseError, match="ended before the required range"):
        us.load_us_daily_bars("SHEL", "2026-10-22", END)
    assert not us._CACHE


def test_future_invalid_price_rows_are_excluded_without_affecting_regular_series(broker):
    _, rows = broker
    rows.insert(0, {"xymd": "20261024", "open": "invalid-future-value"})
    result = us.load_us_daily_bars("SHEL", "2026-10-22", END)
    assert result["Date"].max() == pd.Timestamp(END)
    assert len(result) == len(rows) - 1


def test_invalid_regular_ohlcv_still_fails_with_a_verified_ads_event(broker):
    _, rows = broker
    rows[-1]["high"] = "99"
    with pytest.raises(VendorMalformedResponseError, match="OHLCV"):
        us.load_us_daily_bars("SHEL", "2026-10-22", END)
    assert not us._CACHE


def test_mature_successor_request_has_no_listing_override_or_metadata_lookup(reviewed, monkeypatch):
    collect = Mock(side_effect=AssertionError("No identity read for mature window"))
    monkeypatch.setattr(listing, "collect_security_metadata", collect)
    assert listing.collect_listing_contract("SHEL", Mock(), requested_start=FIRST, end_date=END) is None
    assert listing.collect_listing_contract("AAPL", Mock(), requested_start=ORIGINAL, end_date=END) is None
    collect.assert_not_called()
