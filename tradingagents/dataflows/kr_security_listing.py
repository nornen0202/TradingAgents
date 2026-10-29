"""Reviewed KR first-regular listings, bound to a current public KIS master.

The public master is identity evidence, not a historical quote or listing event.
Only a separately reviewed, exact security event may change a history boundary.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import date, datetime, time, timezone
from io import BytesIO
import hashlib
import json
import re
import urllib.error
import urllib.request
import zipfile
from zoneinfo import ZoneInfo

from .vendor_exceptions import VendorInputError, VendorMalformedResponseError

SCHEMA = "tradingagents.verified-kr-first-regular-listing/v1"
METADATA_SCHEMA = "kis.public-kr-master-identity/v1"
_MASTER = {
    "kospi": ("KS", 228, "135ed22451832935f3d962d1997a05726aaec84cc9d1472ff40ea24685edd0d4"),
    "kosdaq": ("KQ", 222, "fcacb0f401c745bf1810c731a1c533d16ff6af83729ca0771faab876cd0e56bc"),
}
_TAIL_FIELDS = {"kospi": (105, 113, 67), "kosdaq": (100, 108, 62)}
_REVIEWED = {
    "278470.KS": {
        "symbol": "278470.KS", "short_code": "278470", "board": "kospi",
        "exchange": "KRX", "currency": "KRW", "isin": "KR7278470000",
        "issuer": "에이피알보통주", "provider_name": "에이피알",
        "security_class": "COMMON_STOCK", "event_kind": "IPO_FIRST_REGULAR_COMMON_STOCK",
        "first_regular_session": "2024-02-27",
        # Actual collection, not the event's 2024 date. Never backdate this review.
        "evidence_available_at": "2026-10-25T21:12:42.095309+00:00",
        "sources": [
            {"url": "https://kind.krx.co.kr/external/2024/02/23/001109/20240223002474/68152.htm",
             "sha256": "57d6550d8a5fc1f5744f8229bf1464e9540fc821c2043c3cd12fafbb47b68686",
             "role": "EXCHANGE_NEW_COMMON_LISTING_DATE_AND_ISIN"},
            {"url": "https://new.real.download.dws.co.kr/common/master/kospi_code.mst.zip",
             "sha256": "98c8ec803662ed69ce0247ea2887a602a145b5ed39fd27cf4f55ecaf11dc64b2",
             "role": "REVIEWED_CURRENT_MASTER_IDENTITY_NOT_HISTORICAL_LISTING"},
        ],
    },
    "403870.KQ": {
        "symbol": "403870.KQ", "short_code": "403870", "board": "kosdaq",
        "exchange": "KRX", "currency": "KRW", "isin": "KR7403870009",
        "issuer": "주식회사 에이치피에스피 보통주", "provider_name": "HPSP",
        "security_class": "COMMON_STOCK", "event_kind": "IPO_FIRST_REGULAR_COMMON_STOCK",
        "first_regular_session": "2022-07-15",
        "evidence_available_at": "2026-10-25T21:17:25.414010+00:00",
        "sources": [
            {"url": "https://kind.krx.co.kr/external/2022/07/13/000206/20220713000595/70760.htm",
             "sha256": "600f495b516a6b3bd5390da7b3b8e583f69c70e2c07a2ee7c1f98ec316e84465",
             "role": "EXCHANGE_NEW_COMMON_LISTING_DATE_AND_ISIN"},
            {"url": "https://new.real.download.dws.co.kr/common/master/kosdaq_code.mst.zip",
             "sha256": "9e2db1f0bea2b3f7f74b71f3bdfcc3058466db50bd7d3764229bd9a4609a534e",
             "role": "REVIEWED_CURRENT_MASTER_IDENTITY_NOT_HISTORICAL_LISTING"},
        ],
    },
    "064400.KS": {
        "symbol": "064400.KS", "short_code": "064400", "board": "kospi",
        "exchange": "KRX", "currency": "KRW", "isin": "KR7064400005",
        "issuer": "엘지씨엔에스보통주", "provider_name": "LG씨엔에스",
        "security_class": "COMMON_STOCK", "event_kind": "IPO_FIRST_REGULAR_COMMON_STOCK",
        "first_regular_session": "2025-02-05",
        "evidence_available_at": "2026-10-25T21:29:20.316312+00:00",
        "date_evidence": "NEW_LISTING_DATE_AND_SEPARATE_LISTING_DAY_TRADING_REFERENCE_NOTICE",
        "sources": [
            {"url": "https://kind.krx.co.kr/external/2025/02/03/001315/20250203003368/68152.htm",
             "sha256": "88f6401b812effc816af5fe82a8be334312f1f04d4b91bc07a15ca1883e344cb",
             "role": "EXCHANGE_NEW_COMMON_LISTING_DATE_AND_ISIN"},
            {"url": "https://kind.krx.co.kr/external/2025/02/04/000728/20250204001896/99364.htm",
             "sha256": "68d83cd8a81d07a8cec9359423088846a2611e1774195128002c198cf72b5c46",
             "role": "EXCHANGE_LISTING_DAY_TRADING_REFERENCE_CORROBORATION"},
            {"url": "https://new.real.download.dws.co.kr/common/master/kospi_code.mst.zip",
             "sha256": "98c8ec803662ed69ce0247ea2887a602a145b5ed39fd27cf4f55ecaf11dc64b2",
             "role": "REVIEWED_CURRENT_MASTER_IDENTITY_NOT_HISTORICAL_LISTING"},
        ],
    },
    "411080.KQ": {
        "symbol": "411080.KQ", "short_code": "411080", "board": "kosdaq",
        "exchange": "KRX", "currency": "KRW", "isin": "KR7411080005",
        "issuer": "주식회사 샌즈랩 보통주", "provider_name": "샌즈랩",
        "security_class": "COMMON_STOCK", "event_kind": "IPO_FIRST_REGULAR_COMMON_STOCK",
        "first_regular_session": "2023-02-15",
        "evidence_available_at": "2026-10-25T21:28:46.994820+00:00",
        "sources": [
            {"url": "https://kind.krx.co.kr/external/2023/02/13/001336/20230213003382/70760.htm",
             "sha256": "1d09c5fec42ffe671e84218ed18be94c278209c41230885bba82f1c84b65b901",
             "role": "EXCHANGE_NEW_COMMON_FIRST_TRADING_DATE_AND_ISIN"},
            {"url": "https://new.real.download.dws.co.kr/common/master/kosdaq_code.mst.zip",
             "sha256": "9e2db1f0bea2b3f7f74b71f3bdfcc3058466db50bd7d3764229bd9a4609a534e",
             "role": "REVIEWED_CURRENT_MASTER_IDENTITY_NOT_HISTORICAL_LISTING"},
        ],
    },
    "396300.KQ": {
        "symbol": "396300.KQ", "short_code": "396300", "board": "kosdaq",
        "exchange": "KRX", "currency": "KRW", "isin": "KR7396300006",
        # Original IPO issuer and current master name are separate evidence fields.
        "issuer": "(주)세아메카닉스 보통주", "provider_name": "HT로보틱스",
        "security_class": "COMMON_STOCK", "event_kind": "IPO_FIRST_REGULAR_COMMON_STOCK",
        "first_regular_session": "2022-03-24",
        "evidence_available_at": "2026-10-25T22:29:04.545082+00:00",
        "sources": [
            {"url": "https://kind.krx.co.kr/external/2022/03/22/001510/20220322005961/70760.htm",
             "sha256": "a49cfc42142b5c71e5a1272d0262cb88e5e472458801dbc3d7237533f5ceb2a6",
             "role": "EXCHANGE_NEW_COMMON_FIRST_TRADING_DATE_AND_ISIN"},
            {"url": "https://new.real.download.dws.co.kr/common/master/kosdaq_code.mst.zip",
             "sha256": "9e2db1f0bea2b3f7f74b71f3bdfcc3058466db50bd7d3764229bd9a4609a534e",
             "role": "REVIEWED_CURRENT_MASTER_IDENTITY_NOT_HISTORICAL_LISTING"},
        ],
    },
    "179880.KQ": {
        "symbol": "179880.KQ", "short_code": "179880", "board": "kosdaq",
        "exchange": "KRX", "currency": "KRW", "isin": "KR7179880000",
        "issuer": "멜콘 주식회사", "provider_name": "멜콘",
        "security_class": "COMMON_STOCK", "event_kind": "IPO_FIRST_REGULAR_COMMON_STOCK",
        "first_regular_session": "2026-10-15",
        "evidence_available_at": "2026-10-29T08:34:21.037673+00:00",
        "sources": [
            {"url": "https://kind.krx.co.kr/external/2026/10/13/000679/20261013001545/70760.htm",
             "sha256": "beb8b355cf67375f69ef5c4ffda36e1598439033921edb60e605e8c6ae597ffe",
             "role": "EXCHANGE_NEW_COMMON_FIRST_TRADING_DATE_AND_ISIN"},
            {"url": "https://kind.krx.co.kr/external/2026/10/14/000511/20261014000808/72100.htm",
             "sha256": "1bded0ebc902b5e17897b182634aa1a93f6573d42561942be42f658eb4d5b263",
             "role": "EXCHANGE_LISTING_DAY_TRADING_REFERENCE_CORROBORATION"},
            {"url": "https://new.real.download.dws.co.kr/common/master/kosdaq_code.mst.zip",
             "sha256": "a87fa3d6d1ebe76f7bdf32efef9bcdce2679aa06e8d8e3590aafdd74710b0d44",
             "role": "REVIEWED_CURRENT_MASTER_IDENTITY_NOT_HISTORICAL_LISTING"},
        ],
    },
    "443670.KQ": {
        "symbol": "443670.KQ", "short_code": "443670", "board": "kosdaq",
        "exchange": "KRX", "currency": "KRW", "isin": "KR7443670005",
        "issuer": "주식회사 에스피소프트", "provider_name": "에스피소프트",
        "security_class": "COMMON_STOCK", "event_kind": "SPAC_DISSOLUTION_NEW_COMMON_ISSUE",
        "first_regular_session": "2024-02-15",
        "predecessor_name": "IBKS제19호스팩", "predecessor_history_allowed": False,
        "new_security": True,
        "evidence_available_at": "2026-10-29T08:34:21.515152+00:00",
        "sources": [
            {"url": "https://kind.krx.co.kr/external/2024/02/13/001310/20240213003429/70980.htm",
             "sha256": "be2102a8b23870df11954e5feaeac12817b7ea392ec4ff2e36e83eeed92f6002",
             "role": "EXCHANGE_SPAC_DISSOLUTION_NEW_COMMON_DATE_AND_ISIN"},
            {"url": "https://kind.krx.co.kr/external/2024/02/14/001266/20240214003127/70718.htm",
             "sha256": "454be58a405add58fe3e1a47d00fb9e4945d17cae5f319e6735639cdbbaa002e",
             "role": "EXCHANGE_SPAC_DISSOLUTION_TRADING_REFERENCE_CORROBORATION"},
            {"url": "https://new.real.download.dws.co.kr/common/master/kosdaq_code.mst.zip",
             "sha256": "a87fa3d6d1ebe76f7bdf32efef9bcdce2679aa06e8d8e3590aafdd74710b0d44",
             "role": "REVIEWED_CURRENT_MASTER_IDENTITY_NOT_HISTORICAL_LISTING"},
        ],
    },
}
_SHA = re.compile(r"[a-f0-9]{64}")


def _digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     allow_nan=False).encode()).hexdigest()


def _day(value):
    if not isinstance(value, str) or re.fullmatch(r"\d{4}-\d{2}-\d{2}", value) is None:
        raise ValueError("KR listing dates require ISO calendar dates")
    return date.fromisoformat(value)


def _instant(value):
    value = datetime.fromisoformat(value) if isinstance(value, str) else value
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("KR listing evidence requires an aware clock")
    return value.astimezone(timezone.utc)


def cutoff_for_day(end_date):
    """Keep the KR analysis day separate from the completed price-reference day."""
    from .config import get_config
    end = _day(end_date)
    configured = get_config().get("analysis_as_of")
    analysis = _day(configured) if configured else end
    if analysis < end:
        raise VendorInputError("Price window exceeds the explicit KR analysis date")
    boundary = datetime.combine(analysis, time.max, ZoneInfo("Asia/Seoul")).astimezone(timezone.utc)
    return min(boundary, datetime.now(timezone.utc))


def master_url(board):
    if board not in _MASTER:
        raise ValueError("Unsupported KR master board")
    return f"https://new.real.download.dws.co.kr/common/master/{board}_code.mst.zip"


def reviewed_issue(symbol):
    issue = _REVIEWED.get(symbol)
    if issue is None and any(row["short_code"] == symbol.split(".")[0] for row in _REVIEWED.values()):
        raise VendorInputError("Reviewed KR symbol has a conflicting exchange suffix")
    return issue


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise urllib.error.HTTPError(req.full_url, code, "KR master redirects refused", headers, fp)


def _parse_master(raw, *, board, short_code):
    """The fixed public reader schema: 9-char short code, 12-char ISIN, name, ASCII tail."""
    suffix = _MASTER[board][1]
    matches = []
    for line in raw.splitlines(keepends=True):
        text = line.decode("cp949")
        if len(text) <= suffix + 21:
            continue
        prefix = text[:-suffix]
        tail = text[-suffix:]
        code = prefix[:9].rstrip()
        if code in {short_code, "A" + short_code}:
            lower, upper, indirect = _TAIL_FIELDS[board]
            matches.append({"short_code_raw": code, "standard_code": prefix[9:21].rstrip(),
                            "korean_name": prefix[21:].strip(), "security_group_token": tail[:2],
                            "listing_date_raw": tail[lower:upper], "indirect_listing_raw": tail[indirect:indirect + 1],
                            "row_sha256": hashlib.sha256(line).hexdigest(), "row_bytes": len(line)})
    if len(matches) != 1:
        raise ValueError("Exactly one KR master identity row is required")
    return matches[0]


def collect_master_identity(symbol, *, board, short_code):
    """One bounded public ZIP GET; no credentials, broker API, extraction or disk cache."""
    url = master_url(board)
    started = datetime.now(timezone.utc)
    request = urllib.request.Request(url, headers={"User-Agent": "TradingAgents-KR-identity/1"})
    with urllib.request.build_opener(_NoRedirect()).open(request, timeout=20) as response:
        if response.geturl() != url or response.status != 200:
            raise ValueError("Unexpected KR public master response")
        zipped = response.read(2 * 1024 * 1024 + 1)
    if len(zipped) > 2 * 1024 * 1024:
        raise ValueError("KR public master ZIP exceeds its bound")
    with zipfile.ZipFile(BytesIO(zipped)) as archive:
        name = board + "_code.mst"
        if archive.namelist().count(name) != 1:
            raise ValueError("Exactly one fixed KR master member required")
        member = archive.getinfo(name)
        if member.file_size > 10 * 1024 * 1024:
            raise ValueError("KR public master member exceeds its bound")
        raw = archive.read(member)
    identity = _parse_master(raw, board=board, short_code=short_code)
    finished = datetime.now(timezone.utc)
    return {"schema": METADATA_SCHEMA, "provider": "KIS", "environment": "public",
            "symbol": symbol, "board": board, "url": url,
            "reader_source_sha256": _MASTER[board][2],
            "collection_started_at": started.isoformat(), "available_at": finished.isoformat(),
            "zip_sha256": hashlib.sha256(zipped).hexdigest(), "master_sha256": hashlib.sha256(raw).hexdigest(),
            "identity": identity}


def verify_listing_contract(symbol, snapshot, *, requested_start, end_date, analysis_as_of):
    issue = _REVIEWED.get(symbol)
    if issue is None:
        raise ValueError("No reviewed KR first regular listing event")
    cutoff, start, end = _instant(analysis_as_of), _day(requested_start), _day(end_date)
    first = _day(issue["first_regular_session"])
    # The reviewed dissolution lists a new operating-company security. This
    # never admits the dissolved SPAC's prices or an ordinary reverse merger.
    event = issue["event_kind"]
    spac_new_issue = (event == "SPAC_DISSOLUTION_NEW_COMMON_ISSUE"
        and issue.get("new_security") is True and issue.get("predecessor_history_allowed") is False
        and bool(issue.get("predecessor_name"))
        and {"EXCHANGE_SPAC_DISSOLUTION_NEW_COMMON_DATE_AND_ISIN",
             "EXCHANGE_SPAC_DISSOLUTION_TRADING_REFERENCE_CORROBORATION"}
            <= {row.get("role") for row in issue.get("sources", [])})
    if (issue["security_class"] != "COMMON_STOCK"
            or not (event == "IPO_FIRST_REGULAR_COMMON_STOCK" or spac_new_issue)
            or issue["exchange"] != "KRX" or issue["currency"] != "KRW"
            or cutoff > datetime.now(timezone.utc) or _instant(issue["evidence_available_at"]) > cutoff
            or not start < first <= end or end > cutoff.astimezone(ZoneInfo("Asia/Seoul")).date()):
        raise ValueError("Unavailable or inapplicable KR first regular event")
    board = issue["board"]
    if issue["symbol"] != symbol or symbol != issue["short_code"] + "." + _MASTER[board][0]:
        raise ValueError("KR reviewed event board/identity mismatch")
    if set(snapshot) != {"schema", "provider", "environment", "symbol", "board", "url",
                         "reader_source_sha256", "collection_started_at", "available_at",
                         "zip_sha256", "master_sha256", "identity"}:
        raise ValueError("Unexpected KR identity-envelope fields")
    began, available = _instant(snapshot["collection_started_at"]), _instant(snapshot["available_at"])
    if (snapshot["schema"] != METADATA_SCHEMA or snapshot["provider"] != "KIS"
            or snapshot["environment"] != "public" or snapshot["symbol"] != symbol
            or snapshot["board"] != board or snapshot["url"] != master_url(board)
            or snapshot["reader_source_sha256"] != _MASTER[board][2]
            or not began <= available <= cutoff or (cutoff - available).total_seconds() > 300):
        raise ValueError("Unavailable or mismatched current KR master identity")
    identity = snapshot["identity"]
    if (set(identity) != {"short_code_raw", "standard_code", "korean_name", "security_group_token",
                         "listing_date_raw", "indirect_listing_raw", "row_sha256", "row_bytes"}
            or identity["short_code_raw"] not in {issue["short_code"], "A" + issue["short_code"]}
            or identity["standard_code"] != issue["isin"]
            or identity["korean_name"] != issue["provider_name"]
            or identity["security_group_token"] != "ST"
            or identity["listing_date_raw"] != first.strftime("%Y%m%d")
            or identity["indirect_listing_raw"] != "N"
            or type(identity["row_bytes"]) is not int or identity["row_bytes"] <= 21
            or any(not isinstance(value, str) or _SHA.fullmatch(value) is None for value in (
                identity["row_sha256"], snapshot["zip_sha256"], snapshot["master_sha256"]))):
        raise ValueError("Current KR master does not bind the reviewed common stock")
    receipt = {"schema": SCHEMA, "symbol": symbol, "original_requested_start": start.isoformat(),
               "requested_end": end.isoformat(), "required_start": first.isoformat(),
               "analysis_as_of": cutoff.isoformat(), "reviewed_event": deepcopy(issue),
               "reviewed_event_sha256": _digest(issue), "metadata_identity": deepcopy(snapshot),
               "scope": "ALL_KR_REGULAR_SESSIONS_SINCE_VERIFIED_FIRST_LISTING_WITHIN_ORIGINAL_WINDOW",
               "historical_vintage_verified": False}
    receipt["contract_id"] = _digest(receipt)
    return receipt


def validate_listing_receipt(symbol, contract, *, requested_start, end_date, observed_at):
    cutoff = _instant(contract["analysis_as_of"])
    if cutoff > _instant(observed_at) or cutoff > datetime.now(timezone.utc):
        raise ValueError("Future KR listing-contract analysis clock")
    rebuilt = verify_listing_contract(symbol, contract["metadata_identity"], requested_start=requested_start,
                                      end_date=end_date, analysis_as_of=cutoff)
    if contract != rebuilt:
        raise ValueError("KR listing receipt changed or no longer matches the reviewed event")
    return deepcopy(rebuilt)


def collect_listing_contract(symbol, *, requested_start, end_date):
    issue = reviewed_issue(symbol)
    if issue is None or _day(requested_start) >= _day(issue["first_regular_session"]):
        return None
    if _instant(issue["evidence_available_at"]) > cutoff_for_day(end_date):
        return None
    if _day(end_date) < _day(issue["first_regular_session"]):
        raise VendorMalformedResponseError("Requested price range precedes the reviewed KR listing")
    try:
        snapshot = collect_master_identity(symbol, board=issue["board"], short_code=issue["short_code"])
        return verify_listing_contract(symbol, snapshot, requested_start=requested_start, end_date=end_date,
                                       analysis_as_of=cutoff_for_day(end_date))
    except Exception as exc:
        raise VendorMalformedResponseError("Verified KR first regular listing evidence unavailable") from exc
