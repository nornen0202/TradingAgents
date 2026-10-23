"""Collected current metadata candidates, isolated from trading and history policies."""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import re
from typing import Any

from .kis import KisClient, PortfolioConfigurationError, _SECURITY_INFO_MARKETS


def _clock(value: Any) -> datetime:
    if not isinstance(value, str):
        raise ValueError("Missing metadata availability clock.")
    try:
        result = datetime.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("Invalid metadata availability clock.") from exc
    if result.tzinfo is None or result.utcoffset() is None:
        raise ValueError("Metadata availability clock must be aware.")
    return result.astimezone(timezone.utc)


def collect_security_metadata(client: KisClient, symbol: str, *, exchange: str) -> dict[str, Any]:
    """Collect now using an explicitly configured real data reader; no demo fallback."""
    if client.environment != "real":
        raise PortfolioConfigurationError("Security metadata requires an explicit real data reader.")
    started = datetime.now(timezone.utc)
    payload = client.overseas_product_info_raw(symbol, exchange=exchange)
    finished = datetime.now(timezone.utc)
    return {
        "schema": "kis.current-security-metadata/v1", "provider": "KIS", "environment": "real",
        "symbol": symbol, "exchange": exchange, "product_type": _SECURITY_INFO_MARKETS[exchange],
        "collection_started_at": started.isoformat(), "available_at": finished.isoformat(),
        "payload": deepcopy(payload),
    }


def security_metadata_candidate(snapshot: dict[str, Any], *, analysis_as_of: datetime) -> dict[str, Any]:
    """Reject unavailable facts and project identity candidates, never live quote fields.

    This does not establish issuer binding, first regular listing, or historical
    validity before collection. No caller may use it to shorten price history.
    """
    if not isinstance(analysis_as_of, datetime) or analysis_as_of.tzinfo is None:
        raise ValueError("analysis_as_of must be an aware datetime.")
    cutoff = analysis_as_of.astimezone(timezone.utc)
    started = _clock(snapshot.get("collection_started_at"))
    available = _clock(snapshot.get("available_at"))
    exchange = snapshot.get("exchange")
    symbol = snapshot.get("symbol")
    if (
        snapshot.get("schema") != "kis.current-security-metadata/v1"
        or snapshot.get("provider") != "KIS" or snapshot.get("environment") != "real"
        or not isinstance(exchange, str) or exchange not in _SECURITY_INFO_MARKETS
        or snapshot.get("product_type") != _SECURITY_INFO_MARKETS[exchange]
        or not isinstance(symbol, str) or re.fullmatch(r"[A-Z][A-Z0-9.\-]{0,19}", symbol) is None
        or started > available or available > cutoff
    ):
        raise ValueError("Invalid or unavailable metadata envelope.")
    payload = snapshot.get("payload")
    if not isinstance(payload, dict) or payload.get("rt_cd") != "0":
        raise ValueError("Unsuccessful metadata response.")
    row = payload.get("output")
    if not isinstance(row, dict) or not row:
        raise ValueError("Missing or ambiguous metadata response.")
    isin = row.get("istt_usge_isin_cd")
    if not isinstance(isin, str) or re.fullmatch(r"[A-Z]{2}[A-Z0-9]{9}[0-9]", isin) is None:
        raise ValueError("Missing or invalid ISIN.")
    expanded = "".join(str(ord(ch) - 55) if ch.isalpha() else ch for ch in isin)
    digits = [int(ch) for ch in expanded[::-1]]
    if sum((value * 2 // 10 + value * 2 % 10) if index % 2 else value
           for index, value in enumerate(digits)) % 10:
        raise ValueError("Invalid ISIN checksum.")
    listing = row.get("lstg_dt")
    try:
        if not isinstance(listing, str) or re.fullmatch(r"[0-9]{8}", listing) is None:
            raise ValueError("Invalid listing date.")
        listing_date = datetime.strptime(listing, "%Y%m%d").date()
    except ValueError as exc:
        raise ValueError("Invalid listing date.") from exc
    if listing_date > started.date():
        raise ValueError("Future listing date.")
    # Provider venue/class code meanings require separate official validation.
    if row.get("tr_crcy_cd") != "USD":
        raise ValueError("Unsupported metadata currency.")
    if not isinstance(row.get("ovrs_excg_cd"), str) or not row["ovrs_excg_cd"].strip():
        raise ValueError("Missing metadata venue.")
    return {
        "symbol": symbol, "requested_exchange": exchange, "isin": isin,
        "provider_exchange_code": row["ovrs_excg_cd"], "currency": "USD",
        "provider_listing_date": listing_date.isoformat(), "available_at": available.isoformat(),
        "issuer_binding_verified": False, "first_regular_listing_verified": False,
        "historical_identity_verified": False, "price_history_shortening_authorized": False,
    }
