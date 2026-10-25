"""Reviewed first-regular-listing events with fresh, point-in-time KIS binding.

An API listing date or a first bar alone never establishes an event. Changes to
the reviewed event table require source review, just like changes to this code.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import date, datetime, time, timezone
import hashlib
import json
import re
from zoneinfo import ZoneInfo

from tradingagents.portfolio.security_metadata import collect_security_metadata, security_metadata_candidate

from .vendor_exceptions import VendorInputError, VendorMalformedResponseError


_REVIEWED = {
    "GEV": {
        "symbol": "GEV", "exchange": "NYS", "provider_exchange": "NYSE", "currency": "USD",
        "isin": "US36828A1016", "cusip": "36828A101", "issuer": "GE VERNOVA INC",
        "security_class": "COMMON_STOCK", "event_kind": "SPIN_OFF_FIRST_REGULAR_COMMON_STOCK",
        "first_regular_session": "2024-04-02",
        # Collection, rather than the event's 2024 date, bounds this review's availability.
        "evidence_available_at": "2026-10-23T01:20:11.116019+00:00",
        "sources": [
            {"url": "https://www.gevernova.com/investors/faq",
             "sha256": "c495efad884370fc591fba42276150c7472435521a807011c8c67e999f2e84db"},
            {"url": "https://www.gevernova.com/news/press-releases/ge-vernova-completes-spin-off-begins-trading-new-york-stock-exchange",
             "sha256": "65f8cb3d178b8a8620c21a1d4bdb43dc3279150d80ec3ddfdd2f26421d362f61"},
            {"url": "https://www.cusip.com/identifiers.html?section=ISIN",
             "sha256": "8c1d8fc75acbcf3c630edf2eb6008952c9686ed2b57f909062231d612fb65d2e"},
        ],
    },
    "SHEL": {
        "symbol": "SHEL", "exchange": "NYS", "provider_exchange": "NYSE", "currency": "USD",
        "isin": "US7802593050", "cusip": "780259305", "sedol": "BPK3CG3",
        "issuer": "SHELL PLC SPON ADS EA REP 2 ORD SHS",
        "security_class": "SPONSORED_ADS", "event_kind": "ADS_CLASS_UNIFICATION_SUCCESSOR",
        "underlying_isin": "GB00BP6MXD84", "ordinary_shares_per_ads": 2,
        "assimilation_effective_date": "2022-01-29", "when_issued_session": "2022-01-31",
        "first_regular_session": "2022-02-01",
        "predecessors": [
            {"symbol": "RDS.A", "isin": "US7802592060", "successor_ads_per_predecessor_ads": 1},
            {"symbol": "RDS.B", "isin": "US7802591070", "successor_ads_per_predecessor_ads": 1},
        ],
        "history_policy": "CURRENT_SUCCESSOR_ONLY_NO_PREDECESSOR_SPLICING",
        # These sources were reviewed now, not at the 2022 corporate-action date.
        "evidence_available_at": "2026-10-25T14:19:03.925670+00:00",
        "date_evidence": "ISSUER_TIMETABLE_IMPLEMENTATION_CONFIRMATION_AND_CURRENT_KIS_IDENTITY",
        "sources": [
            {"url": "https://www.shell.com/news-and-insights/newsroom/news-and-media-releases/_jcr_content/root/main/section/simple_1285915735/call_to_action_copy__162139957/links/item0.stream/1742566965484/55dda471d98bce808e2b5d62df100a503d9b1ca8/2021-press-releases.pdf",
             "sha256": "67b4db48fb4bdb3ccef5dab3ef3662b7bb76ef35bee17f9065e1d04adbe268ee",
             "pages_1_based": [175, 176, 177], "role": "EXPECTED_REGULAR_WAY_TIMETABLE_AND_IDENTIFIERS"},
            {"url": "https://www.shell.com/news-and-insights/newsroom/news-and-media-releases/_jcr_content/root/main/section/simple_1285915735/call_to_action_copy__876059154/links/item0.stream/1742566955507/e7fdc6470f3fac2d5279ce45b136e5d54038947e/2022-press-releases.pdf",
             "sha256": "afe021804e2ced43263b557215ea132b6979f9ba1b6d718ca2546e3c40744f42",
             "pages_1_based": [19], "role": "JANUARY_29_ASSIMILATION_IMPLEMENTED_CONFIRMATION"},
            {"url": "https://www.shell.com/investors/information-for-shareholders/share-information.html",
             "sha256": "1489b770469db50570b805b29bf8f50d43f32507604aa3898ea43511daa59966",
             "role": "POST_EVENT_ADS_RATIO_AND_ONE_FOR_ONE_ASSIMILATION"},
        ],
    },
}
_IDENTITY_FIELDS = (
    "std_pdno", "istt_usge_isin_cd", "prdt_eng_name", "ovrs_excg_cd", "tr_crcy_cd",
    "lstg_dt", "lstg_yn", "lstg_abol_item_yn", "lstg_abol_dt", "chng_bf_pdno",
)


def _digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def _instant(value):
    result = datetime.fromisoformat(value) if isinstance(value, str) else value
    if not isinstance(result, datetime) or result.tzinfo is None or result.utcoffset() is None:
        raise ValueError("Listing evidence requires an aware clock.")
    return result.astimezone(timezone.utc)


def cutoff_for_day(end_date: str) -> datetime:
    """Keep the explicit analysis day distinct from the last completed price bar.

    US analysis dates are NY market dates. Midnight UTC is not their end.
    Without a scoped analysis date, the requested price day remains the cutoff.
    """
    from .config import get_config
    end = date.fromisoformat(end_date)
    configured = get_config().get("analysis_as_of")
    analysis_day = date.fromisoformat(configured) if configured else end
    if analysis_day < end:
        raise VendorInputError("Price window exceeds the explicit analysis date.")
    boundary = datetime.combine(analysis_day, time.max, ZoneInfo("America/New_York")).astimezone(timezone.utc)
    return min(boundary, datetime.now(timezone.utc))


def _reviewed_event_kind(issue):
    if (issue["security_class"] == "COMMON_STOCK"
            and issue["event_kind"] == "SPIN_OFF_FIRST_REGULAR_COMMON_STOCK"):
        return "COMMON_STOCK"
    if (issue["security_class"] == "SPONSORED_ADS"
            and issue["event_kind"] == "ADS_CLASS_UNIFICATION_SUCCESSOR"
            and type(issue.get("ordinary_shares_per_ads")) is int
            and issue["ordinary_shares_per_ads"] == 2
            and issue.get("history_policy") == "CURRENT_SUCCESSOR_ONLY_NO_PREDECESSOR_SPLICING"
            and issue.get("underlying_isin") == "GB00BP6MXD84"
            and issue.get("predecessors") == [
                {"symbol": "RDS.A", "isin": "US7802592060", "successor_ads_per_predecessor_ads": 1},
                {"symbol": "RDS.B", "isin": "US7802591070", "successor_ads_per_predecessor_ads": 1},
            ]
            and date.fromisoformat(issue["assimilation_effective_date"])
                < date.fromisoformat(issue["when_issued_session"])
                < date.fromisoformat(issue["first_regular_session"])):
        return "ADS_SUCCESSOR"
    raise ValueError("Unsupported reviewed first regular security event.")


def verify_listing_contract(symbol, snapshot, *, requested_start: str, end_date: str,
                            analysis_as_of: datetime, payload_sha256: str | None = None):
    """Validate a current identity snapshot against a separately reviewed issuer event."""
    issue = _REVIEWED.get(symbol)
    if issue is None:
        raise ValueError("No reviewed first regular listing event.")
    event_kind = _reviewed_event_kind(issue)
    cutoff = _instant(analysis_as_of)
    first = date.fromisoformat(issue["first_regular_session"])
    original, end = date.fromisoformat(requested_start), date.fromisoformat(end_date)
    if (_instant(issue["evidence_available_at"]) > cutoff
            or not original < first <= end or end > cutoff.astimezone(ZoneInfo("America/New_York")).date()):
        raise ValueError("Unavailable or inapplicable first regular listing event.")
    candidate = security_metadata_candidate(snapshot, analysis_as_of=cutoff)
    row = snapshot["payload"]["output"]
    if (
        candidate["symbol"] != symbol or candidate["requested_exchange"] != issue["exchange"]
        or candidate["provider_exchange_code"] != issue["provider_exchange"]
        or candidate["currency"] != issue["currency"] or candidate["isin"] != issue["isin"]
        or row.get("std_pdno") != issue["isin"] or candidate["isin"][2:11] != issue["cusip"]
        or row.get("prdt_eng_name") != issue["issuer"]
        or candidate["provider_listing_date"] != issue["first_regular_session"]
        or row.get("lstg_yn") != "Y" or row.get("lstg_abol_item_yn") != "N"
        or row.get("chng_bf_pdno") != "" or row.get("lstg_abol_dt") not in (None, "", "00000000")
        or (event_kind == "ADS_SUCCESSOR" and row.get("sedol_no") != issue["sedol"])
        or (cutoff - _instant(snapshot["available_at"])).total_seconds() > 300
    ):
        raise ValueError("Current metadata does not bind the reviewed security event.")
    # Keep identity-only replay inputs; live price/tax fields never enter research evidence.
    identity = {k: deepcopy(snapshot[k]) for k in (
        "schema", "provider", "environment", "symbol", "exchange", "product_type",
        "collection_started_at", "available_at")}
    fields = _IDENTITY_FIELDS + (("sedol_no",) if event_kind == "ADS_SUCCESSOR" else ())
    identity["payload"] = {"rt_cd": "0", "output": {k: row[k] for k in fields if k in row}}
    payload_digest = payload_sha256 or _digest(snapshot["payload"])
    if not isinstance(payload_digest, str) or re.fullmatch(r"[0-9a-f]{64}", payload_digest) is None:
        raise ValueError("Invalid metadata payload digest.")
    result = {
        "schema": "tradingagents.verified-first-regular-listing/v1",
        "symbol": symbol, "original_requested_start": original.isoformat(), "requested_end": end.isoformat(),
        "required_start": first.isoformat(), "analysis_as_of": cutoff.isoformat(),
        "reviewed_event": deepcopy(issue), "reviewed_event_sha256": _digest(issue),
        "metadata_identity": identity, "metadata_payload_sha256": payload_digest,
        "scope": ("ALL_REGULAR_SESSIONS_OF_VERIFIED_ADS_SUCCESSOR_WITHIN_ORIGINAL_WINDOW"
                  if event_kind == "ADS_SUCCESSOR" else
                  "ALL_REGULAR_SESSIONS_SINCE_VERIFIED_FIRST_LISTING_WITHIN_ORIGINAL_WINDOW"),
        "historical_vintage_verified": False,
    }
    result["contract_id"] = _digest(result)
    return result


def validate_listing_receipt(symbol, contract, *, requested_start, end_date, observed_at):
    """Rebuild a receipt rather than trusting a frame's decorative attributes."""
    cutoff = _instant(contract["analysis_as_of"])
    if cutoff > _instant(observed_at) or cutoff > datetime.now(timezone.utc):
        raise ValueError("Future listing-contract analysis clock.")
    rebuilt = verify_listing_contract(
        symbol, contract["metadata_identity"], requested_start=requested_start,
        end_date=end_date, analysis_as_of=cutoff, payload_sha256=contract["metadata_payload_sha256"])
    if contract != rebuilt:
        raise ValueError("Listing receipt changed or no longer matches the reviewed event.")
    return deepcopy(rebuilt)


def collect_listing_contract(symbol, client, *, requested_start, end_date):
    """Only known, applicable events permit one additional public metadata read.

    Past analyses cannot acquire a current snapshot and backdate its availability.
    Mature and unreviewed symbols retain the original complete five-year contract.
    """
    issue = _REVIEWED.get(symbol)
    if issue is None or date.fromisoformat(requested_start) >= date.fromisoformat(issue["first_regular_session"]):
        return None
    cutoff = cutoff_for_day(end_date)
    if _instant(issue["evidence_available_at"]) > cutoff:
        return None
    try:
        snapshot = collect_security_metadata(client, symbol, exchange=issue["exchange"])
        # Availability is checked at the actual completion clock, within the explicit daily cutoff.
        return verify_listing_contract(symbol, snapshot, requested_start=requested_start,
                                       end_date=end_date, analysis_as_of=cutoff_for_day(end_date))
    except Exception as exc:
        raise VendorMalformedResponseError("Verified first regular listing evidence unavailable") from exc
