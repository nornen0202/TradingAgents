from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone
from typing import Any
from zoneinfo import ZoneInfo

import pandas as pd


def default_calendar_name(market: str) -> str:
    normalized = str(market or "").strip().upper()
    if normalized == "KR":
        return "XKRX"
    if normalized == "US":
        return "XNYS"
    return normalized or "XNYS"


def is_supplemental_market_holiday(*, market: str, session_date: date) -> bool:
    """Return whether a recently enacted market holiday is missing upstream.

    ``exchange_calendars`` 4.13.2 still treats Constitution Day 2026 as an
    XKRX session even though the holiday was restored effective May 11, 2026.
    Keep this small overlay until the upstream calendar includes the new
    recurring holiday and its substitute day.
    """

    if str(market or "").strip().upper() != "KR" or session_date.year < 2026:
        return False

    constitution_day = date(session_date.year, 7, 17)
    holidays = {constitution_day}
    if constitution_day.weekday() >= 5:
        substitute_day = constitution_day + timedelta(days=1)
        while substitute_day.weekday() >= 5:
            substitute_day += timedelta(days=1)
        holidays.add(substitute_day)
    return session_date in holidays


def market_session_state(
    *,
    market: str,
    now_local: datetime,
    calendar_name: str | None = None,
) -> dict[str, Any]:
    calendar_name = calendar_name or default_calendar_name(market)
    normalized_market = str(market or "").strip().upper()
    if now_local.tzinfo is None:
        raise ValueError("now_local must be timezone-aware")

    market_date = now_local.astimezone(ZoneInfo("Asia/Seoul")).date()
    if is_supplemental_market_holiday(market=normalized_market, session_date=market_date):
        return {
            "market": normalized_market,
            "calendar": calendar_name,
            "source": "supplemental_market_holiday",
            "is_open": False,
            "phase": "closed",
            "now_local": now_local.isoformat(),
            "holiday_date": market_date.isoformat(),
        }

    exchange_state = _exchange_calendar_state(calendar_name=calendar_name, now_local=now_local)
    if exchange_state is not None:
        return {
            "market": normalized_market,
            "calendar": calendar_name,
            "source": "exchange_calendars",
            **exchange_state,
        }

    is_open = _fallback_is_open(normalized_market, now_local)
    return {
        "market": normalized_market,
        "calendar": calendar_name,
        "source": "weekday_clock_fallback",
        "is_open": is_open,
        "phase": "regular" if is_open else _fallback_phase(normalized_market, now_local),
        "now_local": now_local.isoformat(),
    }


def _exchange_calendar_state(*, calendar_name: str, now_local: datetime) -> dict[str, Any] | None:
    try:
        import exchange_calendars as xcals
    except Exception:
        return None

    try:
        calendar = xcals.get_calendar(calendar_name)
        minute = pd.Timestamp(now_local.astimezone(timezone.utc))
        is_open = bool(calendar.is_open_on_minute(minute))
        session_label = calendar.minute_to_session_label(minute, direction="previous")
        schedule = calendar.schedule
        open_at = None
        close_at = None
        if session_label in schedule.index:
            row = schedule.loc[session_label]
            open_at = pd.Timestamp(row["open"]).tz_localize("UTC").tz_convert(now_local.tzinfo).isoformat()
            close_at = pd.Timestamp(row["close"]).tz_localize("UTC").tz_convert(now_local.tzinfo).isoformat()
        return {
            "is_open": is_open,
            "phase": "regular" if is_open else "closed",
            "now_local": now_local.isoformat(),
            "session_label": str(session_label.date() if hasattr(session_label, "date") else session_label),
            "session_open": open_at,
            "session_close": close_at,
        }
    except Exception:
        return None


def _fallback_is_open(market: str, now_local: datetime) -> bool:
    if now_local.weekday() >= 5:
        return False
    current = now_local.time()
    if market == "KR":
        return time(hour=9) <= current <= time(hour=15, minute=30)
    return time(hour=9, minute=30) <= current <= time(hour=16)


def _fallback_phase(market: str, now_local: datetime) -> str:
    if now_local.weekday() >= 5:
        return "closed"
    current = now_local.time()
    if market == "KR":
        if current < time(hour=9):
            return "pre_open"
        if current <= time(hour=15, minute=30):
            return "regular"
        return "post_close"
    if current < time(hour=9, minute=30):
        return "pre_open"
    if current <= time(hour=16):
        return "regular"
    return "post_close"
