"""Trading-day admission for scheduled briefings, independent of order gates."""
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from tradingagents.scheduled.automation_calendar import automated_market_session_status


def scheduled_report_session(market, *, now=None, resolver=None):
    if market not in {"kr", "us"}:
        raise ValueError("Scheduled market admission supports KR/US only")
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        raise ValueError("Schedule time must include its timezone")
    session = now.astimezone(ZoneInfo("Asia/Seoul" if market == "kr" else "America/New_York")).date()
    result = {"surface": market, "session_date": session.isoformat(), "checked_at": now.isoformat()}
    if session.weekday() >= 5:
        return {**result, "status": "SKIP_NON_TRADING_DAY", "calendar_source": "market_local_weekend"}
    resolver = resolver or automated_market_session_status
    try:
        status = resolver(market=market, now=now)
        # Reject a calendar receipt for another day, rather than silently using
        # yesterday's holiday result. Unknown calendars do not block research.
        known = status is not None and status.session_date == session
        if known and status.is_session is False:
            return {**result, "status": "SKIP_NON_TRADING_DAY", "calendar_source": status.source}
        if known and status.is_session is True:
            return {**result, "status": "TRADING_DAY", "calendar_source": status.source}
    except (OSError, ValueError, TypeError, KeyError, RuntimeError):
        pass
    return {**result, "status": "CALENDAR_UNVERIFIED_REPORT_ALLOWED", "calendar_source": "unavailable",
            "detail": "Calendar unavailable; dated investor research may proceed. This does not authorize orders."}
