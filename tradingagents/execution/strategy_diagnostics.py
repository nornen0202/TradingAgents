"""Read-only explanations; never schedule work or grant an execution approval."""
from datetime import date
from zoneinfo import ZoneInfo

from tradingagents.charting.bars import instant
from .refresh_policy import MAX_CONSECUTIVE_FAILURES

PLAN_REASONS = frozenset({
    "NO_AUTHORIZED_EXECUTION_ACTION", "OUTSIDE_APPROVED_UNIVERSE", "NO_STRATEGY_OWNED_POSITION",
    "STRATEGY_POSITION_ALREADY_OPEN", "STRATEGY_OBSERVATION_NOT_EXECUTABLE", "STRATEGY_LINEAGE_MISMATCH",
    "ENTRY_ORIGINAL_RESEARCH_UNVERIFIED", "ENTRY_RESEARCH_DECISION_MISMATCH",
    "ENTRY_NOT_AUTHORIZED_BY_RESEARCH", "ENTRY_AUTHORIZATION_MISMATCH", "ENTRY_RESEARCH_EXPIRED",
    "ENTRY_RESEARCH_REVIEW_REQUIRED", "ENTRY_RESEARCH_EVIDENCE_INCOMPLETE",
    "STRATEGY_AUTHORIZATION_EXPIRED", "SELL_SIZE_REQUIRES_EXPLICIT_ALLOCATION", "STRATEGY_EVIDENCE_UNVERIFIED",
})
REFRESH_FIELDS = ("market", "session_date", "started_at", "finished_at", "status",
                  "consecutive_failures", "real_orders_enabled", "error_type")


def allocation_view(raw):
    """Forward only known codes/counts, never ticker paths or arbitrary errors."""
    if not isinstance(raw, dict) or raw.get("allocation_mode") != "DEMO_NATIVE_ONE_SHARE_V1":
        return None
    count = lambda value: type(value) is int and value >= 0
    eligible, owned = raw.get("eligible_candidates"), raw.get("strategy_owned_positions")
    reasons = raw.get("reason_counts")
    if (not count(eligible) or not count(owned) or not isinstance(reasons, dict)
            or raw.get("real_account_allocation_used") is not False
            or any(key not in PLAN_REASONS or not count(value) for key, value in reasons.items())):
        return None
    result = {"eligible_candidates": eligible, "strategy_owned_positions": owned,
              "reason_counts": dict(reasons), "real_account_allocation_used": False}
    for field, allowed in (("research_entry_actions", {"NONE", "WAIT", "STARTER", "ADD", "EXIT", "MISSING"}),
                           ("research_conditional_entries", {"NONE", "STARTER", "ADD", "MISSING"})):
        values = raw.get(field)
        if not isinstance(values, dict) or any(k not in allowed or not count(v) for k, v in values.items()):
            return None
        result[field] = dict(values)
    return result


def refresh_attempt_health(raw, *, market, now):
    """Interpret the original receipt against its exchange date, not KST midnight.

    A completed attempt is not proof of continuous freshness. Prior-day failures
    remain historical evidence and never claim today's retry budget is exhausted.
    """
    now = instant(now)
    if now is None or market not in {"KR", "US"}:
        raise ValueError("Aware market diagnostic clock required")
    if raw is None:
        return {"status": "UNAVAILABLE"}
    invalid = {"status": "UNVERIFIED"}
    if not isinstance(raw, dict):
        return invalid
    start, end = instant(raw.get("started_at")), instant(raw.get("finished_at"))
    failures, status = raw.get("consecutive_failures"), raw.get("status")
    zone = ZoneInfo("Asia/Seoul" if market == "KR" else "America/New_York")
    try:
        session = date.fromisoformat(raw["session_date"])
    except (KeyError, TypeError, ValueError):
        return invalid
    if (raw.get("market") != market.lower() or raw.get("real_orders_enabled") is not False
            or not isinstance(status, str) or status not in {"STARTED", "COMPLETED", "FAILED"}
            or start is None or not start <= now or start.astimezone(zone).date() != session
            or type(failures) is not int or failures < 0
            or (status == "COMPLETED" and failures != 0)
            or (status in {"STARTED", "FAILED"} and failures < 1)
            or (status != "STARTED" and (end is None or not start <= end <= now))
            or (status == "STARTED" and raw.get("finished_at") is not None)):
        return invalid
    current = session == now.astimezone(zone).date()
    # A durable STARTED record is not proof that its process is still alive.
    state = ("PREVIOUS_SESSION" if not current else "COMPLETION_UNVERIFIED" if status == "STARTED"
             else "RETRY_LIMIT_REACHED" if failures >= MAX_CONSECUTIVE_FAILURES
             else "LAST_ATTEMPT_FAILED" if status == "FAILED" else "LAST_ATTEMPT_COMPLETED")
    error = raw.get("error_type")
    return {"status": state, "attempt_status": status, "session_date": session.isoformat(),
            "started_at": start.isoformat(), "finished_at": end.isoformat() if end else None,
            "consecutive_failures": failures, "max_consecutive_failures": MAX_CONSECUTIVE_FAILURES,
            "current_session": current,
            "error_type": error if error is None or (isinstance(error, str)
                and error in {"LocalStorageHeadroomError", "TimeoutError", "ValueError"}) else "OTHER"}
