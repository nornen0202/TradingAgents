"""Explicit clock context for deliberation, without changing research cutoffs."""

from datetime import datetime, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


def build_decision_clock_context(state: dict, *, now: datetime | None = None) -> str:
    instant = now if now is not None else datetime.now(timezone.utc)
    if instant.tzinfo is None or instant.utcoffset() is None:
        raise ValueError("Decision runtime clock must be timezone-aware")
    instant = instant.astimezone(timezone.utc)
    profile = state.get("instrument_profile") or {}
    zone_name = profile.get("timezone") if isinstance(profile, dict) else None
    try:
        local = instant.astimezone(ZoneInfo(zone_name)) if zone_name else None
    except (ZoneInfoNotFoundError, TypeError, ValueError):
        local = None
    analysis_date = str(state.get("analysis_date") or state.get("trade_date") or "unknown")
    price_date = str(state.get("trade_date") or "unknown")
    same_date = local is not None and analysis_date == local.date().isoformat()
    return (
        "Decision clock context:\n"
        f"- Runtime UTC instant: {instant.isoformat()}\n"
        f"- Exchange-local runtime instant: {local.isoformat() if local else 'UNVERIFIED'} "
        f"({zone_name or 'unknown timezone'})\n"
        f"- Research as-of date (date only): {analysis_date}\n"
        f"- Daily price reference date (date only): {price_date}\n"
        f"- Research date matches exchange runtime date: {same_date}\n"
        "Compare timezone-aware expiry timestamps as instants, never bare hour numbers across UTC, KST, or exchange time. "
        "Date-only labels and unverified statements in the debate do not establish that an intraday deadline has passed. "
        "Do not roll a deadline to the next session merely because another agent said it expired. "
        "If research and exchange runtime dates differ, the runtime clock is NOT the historical as-of instant: "
        "preserve the research cutoff and mark as-of intraday timing unverified unless a dated source establishes it. "
        "Even on the same date this clock does not establish the actual exchange session, holiday/early-close calendar, "
        "quote freshness, or fulfilled entry conditions. Verify those separately; never invent a session or expiry. "
        "Distinguish when a plan may first activate from when it expires, and flag conflicting timing for recheck."
    )
