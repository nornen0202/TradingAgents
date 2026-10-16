from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile
from zipfile import BadZipFile
import io

import requests

from .api_keys import get_api_key
from .config import get_config
from .news_models import DisclosureItem, format_disclosure_items_report
from .vendor_exceptions import VendorConfigurationError, VendorInputError, VendorMalformedResponseError, VendorTransientError


_OPENDART_API_BASE = "https://opendart.fss.or.kr/api"


def _get_opendart_key() -> str:
    api_key = get_api_key("OPENDART_API_KEY")
    if not api_key:
        raise VendorConfigurationError("OpenDART API key is not configured.")
    return api_key


def validate_opendart_credentials() -> None:
    _download_corp_code_map()


def _corp_code_cache_path() -> Path:
    data_cache_dir = Path(get_config().get("data_cache_dir", Path(__file__).resolve().parent / "data_cache"))
    data_cache_dir.mkdir(parents=True, exist_ok=True)
    return data_cache_dir / "opendart_corp_codes.json"


def _download_corp_code_map() -> dict[str, str]:
    try:
        response = requests.get(
            f"{_OPENDART_API_BASE}/corpCode.xml",
            params={"crtfc_key": _get_opendart_key()},
            timeout=float(get_config().get("vendor_timeout", 15)),
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise VendorTransientError(f"OpenDART corpCode download failed: {exc}") from exc

    try:
        with ZipFile(io.BytesIO(response.content)) as zipped:
            xml_name = zipped.namelist()[0]
            xml_bytes = zipped.read(xml_name)
    except (BadZipFile, ET.ParseError, IndexError) as exc:
        raise VendorConfigurationError(
            "OpenDART credentials were rejected or returned an invalid corpCode payload."
        ) from exc

    root = ET.fromstring(xml_bytes)
    corp_codes: dict[str, str] = {}
    for item in root.findall("list"):
        stock_code = (item.findtext("stock_code") or "").strip()
        corp_code = (item.findtext("corp_code") or "").strip()
        if stock_code and corp_code:
            corp_codes[stock_code] = corp_code

    _corp_code_cache_path().write_text(json.dumps(corp_codes, ensure_ascii=False), encoding="utf-8")
    return corp_codes


def _load_corp_code_map() -> dict[str, str]:
    cache_path = _corp_code_cache_path()
    if cache_path.exists():
        try:
            return json.loads(cache_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return _download_corp_code_map()


def _resolve_corp_code(symbol: str) -> tuple[str | None, str | None]:
    from tradingagents.agents.utils.instrument_resolver import is_krx_symbol, resolve_instrument

    profile = resolve_instrument(symbol)
    if profile.country != "KR" and not is_krx_symbol(profile.primary_symbol):
        return None, None
    stock_code = profile.krx_code or profile.primary_symbol.split(".", 1)[0]
    corp_code = _load_corp_code_map().get(stock_code)
    return corp_code, stock_code


def fetch_disclosures_opendart(symbol: str, start_date: str, end_date: str, *, page_count: int = 10) -> list[DisclosureItem]:
    try:
        lower = datetime.strptime(start_date, "%Y-%m-%d").date()
        upper = datetime.strptime(end_date, "%Y-%m-%d").date()
        if lower.isoformat() != start_date or upper.isoformat() != end_date:
            raise ValueError("Noncanonical disclosure date")
    except (TypeError, ValueError) as exc:
        raise VendorInputError("Disclosure dates must be YYYY-MM-DD") from exc
    if lower > upper:
        raise VendorInputError("start_date must not be later than end_date")
    corp_code, stock_code = _resolve_corp_code(symbol)
    if not corp_code or not stock_code:
        return []

    params = {
        "crtfc_key": _get_opendart_key(),
        "corp_code": corp_code,
        "bgn_de": start_date.replace("-", ""),
        "end_de": end_date.replace("-", ""),
        "page_count": str(page_count),
    }
    try:
        response = requests.get(
            f"{_OPENDART_API_BASE}/list.json",
            params=params,
            timeout=float(get_config().get("vendor_timeout", 15)),
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise VendorTransientError(f"OpenDART disclosure request failed: {exc}") from exc

    try:
        payload = response.json()
    except ValueError as exc:
        raise VendorMalformedResponseError("OpenDART returned invalid disclosure JSON.") from exc
    if not isinstance(payload, dict):
        raise VendorMalformedResponseError("OpenDART disclosure payload must be an object.")
    status = payload.get("status")
    if status == "013":
        return []
    if status == "020":
        raise VendorTransientError("OpenDART disclosure request limit exceeded (status 020).")
    if status != "000":
        message = payload.get("message", "Unknown OpenDART error")
        raise VendorMalformedResponseError(f"OpenDART returned status {status}: {message}")

    disclosure_items = payload.get("list")
    if not isinstance(disclosure_items, list):
        raise VendorMalformedResponseError("OpenDART list.json payload did not include a disclosure list.")

    result: list[DisclosureItem] = []
    for item in disclosure_items:
        if not isinstance(item, dict):
            continue
        receipt_no = str(item.get("rcept_no", ""))
        receipt_dt = item.get("rcept_dt")
        if not isinstance(receipt_dt, str) or len(receipt_dt) != 8 or not receipt_dt.isdigit():
            continue
        try:
            published_at = datetime.strptime(receipt_dt, "%Y%m%d")
        except (TypeError, ValueError):
            continue
        # Treat the server's search arguments as a request, not proof that every
        # returned row is eligible. Unknown and out-of-window filings are withheld.
        if not lower <= published_at.date() <= upper:
            continue
        published_at = published_at.replace(tzinfo=timezone(timedelta(hours=9)))
        report_name = str(item.get("report_nm", "Disclosure"))
        corp_name = str(item.get("corp_name", stock_code))
        result.append(
            DisclosureItem(
                title=f"{corp_name}: {report_name}",
                source="OpenDART",
                published_at=published_at,
                url=f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={receipt_no}" if receipt_no else "",
                summary=f"Filer: {item.get('flr_nm', '')} | Receipt no: {receipt_no}",
                symbol=symbol,
                raw_vendor="opendart",
            )
        )
    return result


def get_disclosures_opendart(symbol: str, start_date: str, end_date: str) -> str:
    items = fetch_disclosures_opendart(symbol, start_date, end_date)
    if not items:
        return f"No disclosures found for {symbol} between {start_date} and {end_date}"
    return format_disclosure_items_report(
        f"{symbol} Disclosures, from {start_date} to {end_date}",
        items,
        max_items=10,
    )
