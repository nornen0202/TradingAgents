"""Authoritative, fail-closed market-session checks for automations."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
import json
import os
from pathlib import Path
from typing import Callable, Mapping
import urllib.parse
import urllib.request
from zoneinfo import ZoneInfo


SEOUL = ZoneInfo("Asia/Seoul")
NEW_YORK = ZoneInfo("America/New_York")
CACHE_SCHEMA = "tradingagents.official-market-calendar/v1"
DEFAULT_KIS_BASE_URL = "https://openapi.koreainvestment.com:9443"


@dataclass(frozen=True)
class MarketSessionStatus:
    market: str
    session_date: date
    is_session: bool | None
    source: str
    detail: str = ""


def automated_market_session_status(
    market: str,
    now: datetime,
    *,
    cache_path: str | os.PathLike[str] | None = None,
    opener: Callable[..., object] | None = None,
) -> MarketSessionStatus:
    """Return the current market session state; None means callers must hold."""

    normalized = market.strip().lower()
    if normalized not in {"kr", "us"}:
        raise ValueError(f"unsupported market: {market}")
    if now.tzinfo is None:
        raise ValueError("now must be timezone-aware")
    local_date = now.astimezone(SEOUL if normalized == "kr" else NEW_YORK).date()

    if normalized == "kr" and _enabled():
        credentials = _credentials()
        if credentials is None:
            return MarketSessionStatus(
                normalized,
                local_date,
                None,
                "kis_official_unconfigured",
                "KIS calendar is enabled but credentials are missing",
            )
        try:
            return _cached_or_fetch_kis_status(
                local_date,
                cache_path=_cache_path(cache_path),
                credentials=credentials,
                opener=opener or urllib.request.urlopen,
            )
        except (OSError, TimeoutError, ValueError, KeyError, TypeError) as exc:
            return MarketSessionStatus(
                normalized,
                local_date,
                None,
                "kis_official_unavailable",
                f"KIS calendar unavailable: {type(exc).__name__}",
            )

    return _exchange_calendar_status(normalized, local_date)


def _enabled() -> bool:
    return os.getenv("TRADINGAGENTS_KIS_MARKET_CALENDAR_ENABLED", "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def _credentials() -> tuple[str, str] | None:
    app_key = (
        os.getenv("KIS_APP_KEY") or os.getenv("KIS_DEVELOPERS_APP_KEY") or ""
    ).strip()
    app_secret = (
        os.getenv("KIS_APP_SECRET")
        or os.getenv("KIS_DEVELOPERS_APP_SECRET")
        or ""
    ).strip()
    return (app_key, app_secret) if app_key and app_secret else None


def _cache_path(value: str | os.PathLike[str] | None) -> Path:
    configured = value or os.getenv("TRADINGAGENTS_KIS_MARKET_CALENDAR_CACHE")
    return Path(configured or ".runtime/market-calendar/kis-open-days.json")


def _cached_or_fetch_kis_status(
    session_date: date,
    *,
    cache_path: Path,
    credentials: tuple[str, str],
    opener: Callable[..., object],
) -> MarketSessionStatus:
    cached = _load_cache(cache_path)
    status = _status_from_cache(cached, session_date)

    # KIS can return future dates. Only a lookup made on this same KST day can
    # suppress a refresh, otherwise yesterday's forecast could mask a newly
    # announced one-off closure.
    if status is not None and _cache_was_fetched_on(cached, session_date):
        return status

    records = dict(cached.get("records", {}))
    records.update(_fetch_kis_calendar(session_date, credentials, opener))
    payload: dict[str, object] = {
        "schema": CACHE_SCHEMA,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "records": records,
    }
    _write_cache(cache_path, payload)
    status = _status_from_cache(payload, session_date)
    if status is None:
        raise ValueError(f"KIS response omitted {session_date.isoformat()}")
    return status


def _cache_was_fetched_on(payload: Mapping[str, object], session_date: date) -> bool:
    raw = payload.get("fetched_at")
    if not isinstance(raw, str):
        return False
    try:
        fetched_at = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        return False
    if fetched_at.tzinfo is None:
        fetched_at = fetched_at.replace(tzinfo=timezone.utc)
    return fetched_at.astimezone(SEOUL).date() == session_date


def _load_cache(path: Path) -> dict[str, object]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(payload, dict) or payload.get("schema") != CACHE_SCHEMA:
        return {}
    records = payload.get("records")
    if not isinstance(records, dict):
        return {}
    return payload


def _write_cache(path: Path, payload: Mapping[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def _status_from_cache(
    payload: Mapping[str, object], session_date: date
) -> MarketSessionStatus | None:
    records = payload.get("records")
    if not isinstance(records, dict):
        return None
    record = records.get(session_date.isoformat())
    if not isinstance(record, dict) or not isinstance(record.get("is_open"), bool):
        return None
    return MarketSessionStatus(
        "kr",
        session_date,
        bool(record["is_open"]),
        "kis_official_cache",
        str(record.get("detail", "")),
    )


def _fetch_kis_calendar(
    session_date: date,
    credentials: tuple[str, str],
    opener: Callable[..., object],
) -> dict[str, dict[str, object]]:
    app_key, app_secret = credentials
    base_url = os.getenv("KIS_BASE_URL", DEFAULT_KIS_BASE_URL).rstrip("/")
    timeout = float(
        os.getenv("TRADINGAGENTS_KIS_MARKET_CALENDAR_TIMEOUT_SECONDS", "15")
    )
    token_request = urllib.request.Request(
        f"{base_url}/oauth2/tokenP",
        data=json.dumps(
            {
                "grant_type": "client_credentials",
                "appkey": app_key,
                "appsecret": app_secret,
            }
        ).encode("utf-8"),
        headers={"content-type": "application/json; charset=utf-8"},
        method="POST",
    )
    token_payload = _read_json(opener(token_request, timeout=timeout))
    token = str(token_payload.get("access_token", "")).strip()
    if not token:
        raise ValueError("KIS token response omitted access_token")

    query = urllib.parse.urlencode(
        {
            "BASS_DT": session_date.strftime("%Y%m%d"),
            "CTX_AREA_FK": "",
            "CTX_AREA_NK": "",
        }
    )
    request = urllib.request.Request(
        f"{base_url}/uapi/domestic-stock/v1/quotations/chk-holiday?{query}",
        headers={
            "authorization": f"Bearer {token}",
            "appkey": app_key,
            "appsecret": app_secret,
            "tr_id": "CTCA0903R",
            "content-type": "application/json; charset=utf-8",
        },
        method="GET",
    )
    payload = _read_json(opener(request, timeout=timeout))
    if str(payload.get("rt_cd", "0")) != "0":
        raise ValueError(f"KIS holiday request failed: {payload.get('msg1', '')}")
    rows = payload.get("output")
    if not isinstance(rows, list):
        raise ValueError("KIS holiday response omitted output rows")

    parsed: dict[str, dict[str, object]] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        try:
            row_date = datetime.strptime(str(row.get("bass_dt", "")), "%Y%m%d").date()
        except ValueError:
            continue
        is_open = str(row.get("opnd_yn", "")).strip().upper()
        if is_open in {"Y", "N"}:
            parsed[row_date.isoformat()] = {
                "is_open": is_open == "Y",
                "detail": "KIS chk-holiday opnd_yn",
            }
    return parsed


def _read_json(response: object) -> dict[str, object]:
    read = getattr(response, "read", None)
    if not callable(read):
        raise TypeError("HTTP response has no read()")
    raw = read()
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8")
    payload = json.loads(raw)
    if not isinstance(payload, dict):
        raise ValueError("HTTP response is not a JSON object")
    return payload


def _exchange_calendar_status(
    market: str, session_date: date
) -> MarketSessionStatus:
    try:
        import exchange_calendars as xcals

        calendar_name = "XKRX" if market == "kr" else "XNYS"
        calendar = xcals.get_calendar(calendar_name)
        is_session = bool(calendar.is_session(session_date.isoformat()))
        if market == "kr":
            from tradingagents.scheduled.market_calendar import (
                is_supplemental_market_holiday,
            )

            if is_supplemental_market_holiday("kr", session_date):
                is_session = False
        return MarketSessionStatus(
            market,
            session_date,
            is_session,
            f"exchange_calendars:{calendar_name}",
        )
    except (ImportError, KeyError, TypeError, ValueError) as exc:
        return MarketSessionStatus(
            market,
            session_date,
            None,
            "exchange_calendar_unavailable",
            f"exchange calendar unavailable: {type(exc).__name__}",
        )
