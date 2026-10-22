"""Shared, deterministic clocks and source-use rules for market consumers.

An observation's timestamp, a provider's publication, and our publication are
different clocks. Repackaging never renews an observation. These functions do
not fetch data or assume that a subscription permits unattended collection.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

MAX_EXECUTION_AGE = timedelta(minutes=10)
POLICY_SCHEMA = "tradingagents.market-policy/v1"


@dataclass(frozen=True)
class TimestampEnvelope:
    """Source event, local ingestion and evaluation are independent clocks."""
    event_time: str | None
    ingested_at: str | None
    evaluated_at: str
    is_amended: bool = False

    @classmethod
    def from_mapping(cls, row: dict[str, Any], *, evaluated_at: Any = None) -> "TimestampEnvelope":
        return cls(event_time=row.get("event_time", row.get("published_at")),
                   ingested_at=row.get("ingested_at", row.get("observed_at")),
                   evaluated_at=str(evaluated_at or row.get("evaluated_at") or row.get("analysis_as_of") or ""),
                   is_amended=bool(row.get("is_amended", row.get("status") == "corrected")))

    def to_dict(self) -> dict[str, Any]:
        evaluated = aware_datetime(self.evaluated_at)
        if evaluated is None:
            raise ValueError("evaluated_at must be a timezone-aware timestamp")
        event = aware_datetime(self.event_time)
        ingested = aware_datetime(self.ingested_at)
        eligible = ingested is not None and ingested <= evaluated
        if self.event_time is not None:
            eligible = eligible and event is not None and event <= ingested
        return {"event_time": event.isoformat() if event else None,
                "ingested_at": ingested.isoformat() if ingested else None,
                "evaluated_at": evaluated.isoformat(), "is_amended": self.is_amended,
                "exact_event_time_known": event is not None, "available_as_of": eligible,
                "published_at": event.isoformat() if event else None,
                "observed_at": ingested.isoformat() if ingested else None}


def aware_datetime(value: Any) -> datetime | None:
    try:
        parsed = value if isinstance(value, datetime) else datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return parsed if parsed.tzinfo is not None and parsed.utcoffset() is not None else None
    except (TypeError, ValueError, OverflowError):
        return None


def observation_status(observed_at: Any, *, as_of: Any, published_at: Any = None,
                       max_age: timedelta = MAX_EXECUTION_AGE) -> dict[str, Any]:
    """Classify a source clock; the exact age limit is already stale."""
    now = aware_datetime(as_of)
    if now is None:
        raise ValueError("analysis_as_of must be a timezone-aware timestamp")
    observed = aware_datetime(observed_at)
    published = aware_datetime(published_at) if published_at is not None else None
    status = "FRESH"
    if observed is None:
        status = "MISSING" if observed_at in (None, "") else "INVALID"
    elif observed > now:
        status = "FUTURE"
    elif max_age <= timedelta(0) or now - observed >= min(max_age, MAX_EXECUTION_AGE):
        status = "STALE"
    if published_at is not None and (published is None or published > now):
        status = "INVALID_PUBLICATION" if published is None else "FUTURE_PUBLICATION"
    return {"schema": POLICY_SCHEMA, "status": status, "eligible": status == "FRESH",
            "observed_at": observed.isoformat() if observed else None,
            "published_at": published.isoformat() if published else None,
            "as_of": now.isoformat(),
            "age_seconds": (now - observed).total_seconds() if observed else None,
            "max_age_seconds": min(max_age, MAX_EXECUTION_AGE).total_seconds(),
            "publication_does_not_refresh_inputs": True}


def source_use_policy(provider: Any, *, use: str = "automated_analysis",
                      entitlement: dict[str, Any] | None = None) -> dict[str, Any]:
    """Only explicitly configured provider rights permit automated use.

    Built-in adapters represent the repository's existing configured data
    routes. A new provider must declare rights; an opaque subscription flag is
    insufficient. TradingView MCP remains a manual comparison source.
    """
    name = str(provider or "").strip().lower().replace("-", "_").replace(" ", "_")
    manual = use == "manual_comparison"
    automated = use in {"automated_analysis", "execution", "alerts", "backtest"}
    builtins = {"kis", "kis_quote", "kis_microstructure", "kis_us_microstructure", "opendart", "dart", "sec", "sec_edgar",
                "fred", "yfinance", "yfinance_intraday", "massive", "alpaca", "fixture", "test", "local", "local_archive"}
    reason = None
    if "tradingview" in name or "trading_view" in name or name in {"tv_mcp", "tradingview_mcp"}:
        allowed = manual
        reason = None if allowed else "INTERACTIVE_SOURCE_NOT_AUTOMATION_ENTITLED"
    elif not name:
        allowed, reason = False, "SOURCE_UNVERIFIED"
    elif entitlement is not None:
        permitted = entitlement.get("permitted_uses", []) if isinstance(entitlement, dict) else []
        allowed = isinstance(entitlement, dict) and isinstance(permitted, (list, tuple)) and use in permitted and entitlement.get("verified") is True
        reason = None if allowed else "SOURCE_USE_NOT_ENTITLED"
    else:
        allowed = manual or (automated and name in builtins)
        reason = None if allowed else "SOURCE_USE_NOT_ENTITLED"
    return {"schema": POLICY_SCHEMA, "provider": name, "use": use,
            "allowed": bool(allowed), "reason": reason,
            "execution_requires_fresh_regular_session": True}


def session_policy(session: Any, *, require_regular: bool = True) -> dict[str, Any]:
    """Consume calendar/provider evidence without inventing holiday calendars."""
    if isinstance(session, dict):
        phase = str(session.get("phase") or session.get("market_session") or "unknown").lower()
        opened = session.get("is_open") is True
        verified = session.get("verified", True) is True and phase not in {"unknown", "unverified", "error"}
    else:
        phase = str(session or "unknown").lower()
        opened = phase in {"regular", "regular_session", "in_session"}
        verified = phase in {"regular", "regular_session", "in_session", "pre_open", "post_close", "closed", "pre_market", "after_hours"}
    allowed = verified and (opened if require_regular else True)
    return {"phase": phase, "verified": verified, "eligible": allowed,
            "reason": None if allowed else "SESSION_UNVERIFIED" if not verified else "SESSION_NOT_REGULAR"}


def market_observation_policy(observed_at: Any, *, as_of: Any, published_at: Any = None,
                              session: Any = None, provider: Any = None,
                              entitlement: dict[str, Any] | None = None) -> dict[str, Any]:
    clock = observation_status(observed_at, as_of=as_of, published_at=published_at)
    market_session = session_policy(session)
    source = source_use_policy(provider, use="execution", entitlement=entitlement)
    blockers = (["OBSERVATION_" + clock["status"]] if not clock["eligible"] else [])
    blockers += [part["reason"] for part in (market_session, source) if part.get("reason")]
    return {"schema": POLICY_SCHEMA, "eligible": not blockers, "blockers": blockers,
            "clock": clock, "session": market_session, "source": source}


def research_observation_policy(observed_at: Any, *, as_of: Any, session: Any,
                                interval: str = "1d", latest_regular_close_at: Any = None,
                                verified_session: bool = False) -> dict[str, Any]:
    """Permit verified last-session closes for closed-market research only.

    The caller supplies a calendar-verified latest regular close (including
    holidays and early closes). This function cannot invent that timestamp.
    Extended-session quotes retain their distinct research category.
    """
    clock = observation_status(observed_at, as_of=as_of)
    phase = session_policy(session)
    close = aware_datetime(latest_regular_close_at)
    observed = aware_datetime(observed_at)
    now = aware_datetime(as_of)
    category = "UNVERIFIED_RESEARCH_INPUT"
    research_valid = False
    if clock["eligible"] and phase["eligible"]:
        research_valid, category = True, "FRESH_REGULAR_SESSION"
    elif clock["eligible"] and phase["verified"]:
        research_valid, category = True, "EXTENDED_SESSION_RESEARCH_ONLY"
    elif (phase["verified"] and not phase["eligible"] and verified_session is True
          and interval.lower() in {"1d", "daily", "day"} and close is not None
          and observed == close and close <= now):
        research_valid, category = True, "LATEST_REGULAR_CLOSE_RESEARCH_ONLY"
    return {"schema": POLICY_SCHEMA, "research_valid": research_valid,
            "execution_eligible": clock["eligible"] and phase["eligible"],
            "category": category, "clock": clock, "session": phase,
            "latest_regular_close_at": close.isoformat() if close else None,
            "calendar_verified": verified_session is True}


def latest_regular_session_context(market: str, *, as_of: Any) -> dict[str, Any]:
    """Resolve the last completed regular session from the existing calendar.

    This uses bundled exchange calendars and the repository's supplemental
    holiday overlay. No weekday-only guess can verify a closing timestamp.
    """
    now = aware_datetime(as_of)
    if now is None:
        raise ValueError("as_of must be a timezone-aware timestamp")
    from tradingagents.scheduled.market_calendar import (
        default_calendar_name, is_supplemental_market_holiday, market_session_state,
    )
    normalized = str(market or "").upper()
    if normalized not in {"KR", "US"}:
        return {"session": "unknown", "verified_session": False, "latest_regular_close_at": None}
    session = market_session_state(market=normalized, now_local=now)
    result = {"session": session, "verified_session": False, "latest_regular_close_at": None}
    if session.get("phase") == "unknown" or session.get("source") not in {"exchange_calendars", "supplemental_market_holiday"}:
        return result
    try:
        from tradingagents.calendar_access import get_exchange_calendar
        import pandas as pd
        calendar = get_exchange_calendar(default_calendar_name(normalized))
        schedule = calendar.schedule
        closes = pd.to_datetime(schedule["close"], utc=True)
        completed = schedule.loc[closes <= pd.Timestamp(now)]
        for label, row in completed.tail(10).iloc[::-1].iterrows():
            session_date = label.date()
            if is_supplemental_market_holiday(market=normalized, session_date=session_date):
                continue
            close = pd.Timestamp(row["close"])
            close = close.tz_localize("UTC") if close.tzinfo is None else close.tz_convert("UTC")
            result.update(verified_session=True, latest_regular_close_at=close.isoformat())
            if session.get("is_open") is not True and session.get("session_label") != session_date.isoformat():
                corrected_session = {**session, "session_label": session_date.isoformat(),
                                     "session_close": close.isoformat(), "calendar_overlay_applied": True}
                if "open" in row:
                    opened = pd.Timestamp(row["open"])
                    opened = opened.tz_localize("UTC") if opened.tzinfo is None else opened.tz_convert("UTC")
                    corrected_session["session_open"] = opened.isoformat()
                result["session"] = corrected_session
            break
    except Exception:
        pass  # A missing/invalid calendar remains diagnostic-only.
    return result
