"""Fail-closed market-session checks for unattended automations.

The Korean market check can use KIS' official ``chk-holiday`` endpoint. Its
result is cached for the current KST day only: responses can contain future
dates, but those forecasts must not survive into a later day because an
ad-hoc closure may have been declared in the meantime.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
import json
import os
import math
from pathlib import Path
import tempfile
from typing import Callable, Mapping
import urllib.parse
import urllib.request
from zoneinfo import ZoneInfo


SEOUL = ZoneInfo("Asia/Seoul")
NEW_YORK = ZoneInfo("America/New_York")
DEFAULT_KIS_BASE_URL = "https://openapi.koreainvestment.com:9443"
CACHE_SCHEMA = "tradingagents.official-market-calendar/v1"


@dataclass(frozen=True)
class MarketSessionStatus:
    market: str
    session_date: date
    is_session: bool | None
    source: str
    detail: str = ""

    @property
    def reason(self) -> str:
        state = "open" if self.is_session is True else "closed" if self.is_session is False else "unavailable"
        return f"{self.market.upper()} {self.session_date.isoformat()}: market {state}. {self.detail}".strip()


def automated_market_session_status(
    market: str,
    now: datetime,
    *,
    cache_path: str | os.PathLike[str] | None = None,
    opener: Callable[..., object] | None = None,
) -> MarketSessionStatus:
    """Return whether automation may run for ``market`` at ``now``.

    ``None`` means the authoritative check could not be completed. Schedule
    callers treat that as closed so an outage never launches trading work.
    """

    normalized = market.strip().lower()
    if normalized not in {"kr", "us"}:
        raise ValueError(f"unsupported market: {market}")
    if now.tzinfo is None:
        raise ValueError("now must be timezone-aware")

    market_tz = SEOUL if normalized == "kr" else NEW_YORK
    session_date = now.astimezone(market_tz).date()

    if normalized == "kr" and _env_enabled(
        "TRADINGAGENTS_KIS_MARKET_CALENDAR_ENABLED"
    ):
        credentials = _kis_credentials()
        if credentials is None:
            return MarketSessionStatus(
                normalized,
                session_date,
                None,
                "kis_official_unconfigured",
                "official KIS market calendar is enabled but credentials are missing",
            )
        try:
            return _cached_or_fetch_kis_status(
                session_date,
                cache_path=_resolve_cache_path(cache_path),
                credentials=credentials,
                opener=opener or urllib.request.urlopen,
                fetched_at=now,
            )
        except (OSError, TimeoutError, ValueError, KeyError, TypeError) as exc:
            return MarketSessionStatus(
                normalized,
                session_date,
                None,
                "kis_official_unavailable",
                f"official KIS market calendar unavailable: {type(exc).__name__}",
            )

    return _exchange_calendar_status(normalized, session_date)


def _env_enabled(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "on"}


def _resolve_cache_path(cache_path: str | os.PathLike[str] | None) -> Path:
    configured = (cache_path or os.getenv("TRADINGAGENTS_MARKET_CALENDAR_CACHE_PATH")
                  or os.getenv("TRADINGAGENTS_KIS_MARKET_CALENDAR_CACHE"))
    return Path(configured or ".runtime/market-calendar/kis-open-days.json")


def _kis_credentials() -> tuple[str, str] | None:
    app_key = (
        os.getenv("KIS_APP_KEY")
        or os.getenv("KIS_Developers_APP_KEY")
        or os.getenv("KIS_DEVELOPERS_APP_KEY")
        or ""
    ).strip()
    app_secret = (
        os.getenv("KIS_APP_SECRET")
        or os.getenv("KIS_Developers_APP_SECRET")
        or os.getenv("KIS_DEVELOPERS_APP_SECRET")
        or ""
    ).strip()
    if not app_key or not app_secret:
        return None
    return app_key, app_secret


def _cached_or_fetch_kis_status(
    session_date: date,
    *,
    cache_path: Path,
    credentials: tuple[str, str],
    opener: Callable[..., object],
    fetched_at: datetime,
) -> MarketSessionStatus:
    cached = _load_cache(cache_path)
    cached_status = _status_from_cache(cached, session_date)

    # KIS may return future dates. Only a cache fetched on this same KST day may
    # suppress a live lookup; otherwise a newly announced closure could be
    # masked by yesterday's forecast.
    if cached_status is not None and _cache_was_fetched_on(cached, session_date):
        return cached_status

    fetched = _fetch_kis_calendar(session_date, credentials, opener)
    # Never relabel yesterday's forecast as today's confirmed response.
    if session_date.isoformat() not in fetched:
        raise ValueError("KIS response did not include the requested session date")
    payload: dict[str, object] = {
        "schema": CACHE_SCHEMA,
        "fetched_at": fetched_at.astimezone(timezone.utc).isoformat(),
        "records": fetched,
    }
    _write_cache(cache_path, payload)
    status = _status_from_cache(payload, session_date)
    if status is None:
        raise ValueError(f"KIS response did not include {session_date.isoformat()}")
    return status


def _cache_was_fetched_on(payload: Mapping[str, object], session_date: date) -> bool:
    raw = payload.get("fetched_at")
    if not isinstance(raw, str) or not raw.strip():
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
    return payload


def _write_cache(path: Path, payload: Mapping[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False) as stream:
        temporary = Path(stream.name)
        json.dump(payload, stream, ensure_ascii=False, indent=2, sort_keys=True)
        stream.write("\n")
    try:
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


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
        os.getenv("TRADINGAGENTS_KIS_MARKET_CALENDAR_TIMEOUT_SECONDS")
        or os.getenv("KIS_HTTP_TIMEOUT_SECONDS", "8")
    )
    if not math.isfinite(timeout) or not 0 < timeout <= 60:
        raise ValueError("KIS calendar timeout must be between 0 and 60 seconds")
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
    token_payload = _read_json_response(opener(token_request, timeout=timeout))
    access_token = str(token_payload.get("access_token", "")).strip()
    if not access_token:
        raise ValueError("KIS token response did not include access_token")

    query = urllib.parse.urlencode(
        {
            "BASS_DT": session_date.strftime("%Y%m%d"),
            "CTX_AREA_FK": "",
            "CTX_AREA_NK": "",
        }
    )
    holiday_request = urllib.request.Request(
        f"{base_url}/uapi/domestic-stock/v1/quotations/chk-holiday?{query}",
        headers={
            "authorization": f"Bearer {access_token}",
            "appkey": app_key,
            "appsecret": app_secret,
            "tr_id": "CTCA0903R",
            "custtype": "P",
            "content-type": "application/json; charset=utf-8",
        },
        method="GET",
    )
    payload = _read_json_response(opener(holiday_request, timeout=timeout))
    if str(payload.get("rt_cd", "0")) != "0":
        raise ValueError(f"KIS holiday API rejected request: {payload.get('msg1', '')}")
    rows = payload.get("output")
    if not isinstance(rows, list):
        raise ValueError("KIS holiday API response did not include output rows")

    parsed: dict[str, dict[str, object]] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        raw_date = str(row.get("bass_dt", "")).strip()
        try:
            row_date = datetime.strptime(raw_date, "%Y%m%d").date()
        except ValueError:
            continue
        open_flag = str(row.get("opnd_yn", "")).strip().upper()
        if open_flag not in {"Y", "N"}:
            continue
        parsed[row_date.isoformat()] = {
            "is_open": open_flag == "Y",
            "detail": "KIS chk-holiday opnd_yn",
        }
    return parsed


def _read_json_response(response: object) -> dict[str, object]:
    read = getattr(response, "read", None)
    if not callable(read):
        raise TypeError("HTTP response does not expose read()")
    try:
        raw = read()
    finally:
        close = getattr(response, "close", None)
        if callable(close):
            close()
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8")
    payload = json.loads(raw)
    if not isinstance(payload, dict):
        raise ValueError("HTTP response is not a JSON object")
    return payload


def _exchange_calendar_status(market: str, session_date: date) -> MarketSessionStatus:
    try:
        import exchange_calendars as xcals

        calendar_name = "XKRX" if market == "kr" else "XNYS"
        calendar = xcals.get_calendar(calendar_name)
        is_session = bool(calendar.is_session(session_date.isoformat()))
        if market == "kr":
            from tradingagents.scheduled.market_calendar import (
                is_supplemental_market_holiday,
            )

            if is_supplemental_market_holiday(market="kr", session_date=session_date):
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
