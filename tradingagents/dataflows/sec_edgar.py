"""SEC submissions index. Filing dates and acceptance times are not fiscal dates.

API contract: https://www.sec.gov/search-filings/edgar-application-programming-interfaces
Only filing metadata is returned; this never claims to have read filing content.
"""
from __future__ import annotations

import os
import threading
import time
from datetime import datetime, timezone
from functools import lru_cache

import requests

from .news_models import DisclosureItem, format_disclosure_items_report
from .vendor_exceptions import VendorMalformedResponseError, VendorTransientError

_LOCK = threading.Lock()
_LAST_REQUEST = 0.0
_UNAVAILABLE_UNTIL = 0.0
_UNAVAILABLE_STATUS = None


def _get_json(url: str) -> dict:
    global _LAST_REQUEST, _UNAVAILABLE_UNTIL, _UNAVAILABLE_STATUS
    with _LOCK:
        if time.monotonic() < _UNAVAILABLE_UNTIL:
            raise VendorTransientError(f"SEC access cooldown after HTTP {_UNAVAILABLE_STATUS}; filing coverage unavailable")
        time.sleep(max(0, 0.5 - (time.monotonic() - _LAST_REQUEST)))
        _LAST_REQUEST = time.monotonic()
    try:
        response = requests.get(url, timeout=25, headers={
            "User-Agent": os.getenv("SEC_EDGAR_USER_AGENT") or os.getenv("SEC_USER_AGENT") or "TradingAgents research contact https://github.com/nornen0202/TradingAgents/issues",
            "Accept-Encoding": "gzip, deflate", "Accept": "application/json",
        })
        response.raise_for_status()
        payload = response.json()
    except (requests.RequestException, ValueError) as exc:
        # Never include response headers, authentication values or body in logs.
        status = getattr(getattr(exc, "response", None), "status_code", None)
        if status in {403, 429}:
            _UNAVAILABLE_UNTIL = time.monotonic() + 600
            _UNAVAILABLE_STATUS = status
        raise VendorTransientError(f"SEC submissions unavailable ({type(exc).__name__}, HTTP {status or 'unknown'})") from exc
    if not isinstance(payload, dict):
        raise VendorMalformedResponseError("SEC returned a non-object response")
    return payload


@lru_cache(maxsize=8)
def _ticker_map(day: str) -> dict:
    payload = _get_json("https://www.sec.gov/files/company_tickers.json")
    return {str(row.get("ticker") or "").upper().replace(".", "-"): str(row["cik_str"]).zfill(10)
            for row in payload.values() if isinstance(row, dict) and row.get("cik_str")}


@lru_cache(maxsize=8)
def _fund_map(day: str) -> dict:
    payload = _get_json("https://www.sec.gov/files/company_tickers_mf.json")
    fields = payload.get("fields") or []
    rows = [dict(zip(fields, row)) for row in payload.get("data", [])]
    return {str(row.get("symbol") or "").upper(): str(row["cik"]).zfill(10) for row in rows if row.get("cik")}


@lru_cache(maxsize=256)
def _submissions(cik: str, hour: str) -> dict:
    return _get_json(f"https://data.sec.gov/submissions/CIK{cik}.json")


def get_disclosures_sec_edgar(symbol: str, start_date: str, end_date: str) -> str:
    now = datetime.now(timezone.utc)
    ticker = symbol.strip().upper().replace(".", "-")
    cik = _ticker_map(now.date().isoformat()).get(ticker)
    fund = False
    if not cik:
        cik = _fund_map(now.date().isoformat()).get(ticker)
        fund = bool(cik)
    if not cik:
        return f"SEC disclosure coverage: UNMAPPED_INSTRUMENT for {symbol}; corporate filing applicability unverified, not a verified zero. Retrieved {now.isoformat()}"
    payload = _submissions(cik, now.strftime("%Y-%m-%dT%H"))
    fund = fund or payload.get("entityType") == "investment"
    filings = payload.get("filings") or {}
    recent = filings.get("recent")
    if not isinstance(recent, dict) or not isinstance(recent.get("accessionNumber"), list):
        raise VendorMalformedResponseError("SEC filings.recent is missing")
    items = []
    dates = recent.get("filingDate") or []
    for index, accession in enumerate(recent["accessionNumber"]):
        filing_date = dates[index] if index < len(dates) else ""
        if not start_date <= filing_date <= end_date:
            continue
        def value(key):
            rows = recent.get(key) or []
            return rows[index] if index < len(rows) else ""
        acceptance = str(value("acceptanceDateTime") or "")
        try:
            published = datetime.fromisoformat(acceptance.replace("Z", "+00:00"))
            if published.tzinfo is None:
                published = published.replace(tzinfo=timezone.utc)
            if published > now or published.date().isoformat() > end_date:
                continue
        except ValueError:
            published = None
        accession_path = str(accession).replace("-", "")
        # Build a canonical SEC index link, not an arbitrary vendor URL.
        url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession_path}/{accession}-index.html"
        items.append(DisclosureItem(
            title=f"{symbol} {value('form')} — {value('primaryDocDescription') or 'filing index'}",
            source="SEC EDGAR", published_at=published, url=url, symbol=symbol, raw_vendor="sec_edgar",
            summary=f"Filed {filing_date}; accepted {acceptance or 'UNVERIFIED'}; retrieved {now.isoformat()}. Filing metadata only; document content not retrieved.",
        ))
    oldest = min(dates) if dates else None
    complete_window = bool(oldest and (oldest <= start_date or not filings.get("files")))
    coverage = "OBSERVED" if items else "VERIFIED_ZERO" if complete_window else "PARTIAL_WINDOW"
    header = f"SEC disclosure coverage: {coverage}; applicability={'FUND_FILINGS' if fund else 'CORPORATE_FILINGS'}; observed={len(items)}, rendered={min(20, len(items))}; recent index window complete={complete_window}. Retrieved {now.isoformat()}"
    if not items:
        return header
    return header + "\n\n" + format_disclosure_items_report(f"{symbol} SEC filing index {start_date} to {end_date}", items, max_items=20)
