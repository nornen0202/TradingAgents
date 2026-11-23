"""Explicit session-level entry evidence for isolated research and paper planning."""

from __future__ import annotations

import argparse
from datetime import date, timedelta
import json
import math
from pathlib import Path

from tradingagents.calendar_access import get_exchange_calendar
from tradingagents.scheduled.market_calendar import default_calendar_name, is_supplemental_market_holiday

from .experiments import _stamp


def _positive(value):
    try:
        return type(value) in (float, int) and math.isfinite(value) and value > 0
    except OverflowError:
        return False


def _schedule(market, origin):
    start = date.fromisoformat(origin)
    calendar = get_exchange_calendar(default_calendar_name(market))
    for day in calendar.sessions_in_range(start.isoformat(), (start + timedelta(days=30)).isoformat()):
        label = day.date()
        if not is_supplemental_market_holiday(market=market, session_date=label):
            yield label.isoformat(), _stamp(calendar.session_open(day)), _stamp(calendar.session_close(day))


def _read_market_record(record, plan, session, *, purpose, earliest, latest, now):
    if (not isinstance(record, dict) or not _positive(record.get("price"))
            or any(record.get(key) != plan[key] for key in ("ticker", "market", "currency"))
            or record.get("session") != session or record.get("kind") != purpose
            or not isinstance(record.get("source"), str) or not record["source"].strip()):
        return None
    try:
        event, observed = _stamp(record["event_at"]), _stamp(record["observed_at"])
        if not earliest <= event <= latest or not event <= observed <= now:
            return None
    except (KeyError, TypeError, ValueError):
        return None
    return record["price"], observed


def _validate_plan(plan):
    required = {"ticker", "market", "currency", "origin_session", "created_at", "valid_sessions",
                "quote_max_age_seconds", "max_open_delay_seconds", "execution_window_seconds", "max_gap_bps", "alternatives"}
    if not isinstance(plan, dict) or set(plan) != required or plan.get("market") not in ("KR", "US"):
        raise ValueError("Incomplete paper confirmation plan")
    if any(not isinstance(plan[key], str) or not plan[key].strip() for key in ("ticker", "currency")):
        raise ValueError("Instrument and price currency must be explicit")
    for key, upper in (("valid_sessions", 5), ("quote_max_age_seconds", 120), ("max_open_delay_seconds", 1800),
                       ("execution_window_seconds", 1800), ("max_gap_bps", 1000)):
        if type(plan[key]) is not int or not 1 <= plan[key] <= upper:
            raise ValueError(f"Invalid independent gate: {key}")
    groups = plan["alternatives"]
    if not isinstance(groups, list) or not groups or len(groups) > 16:
        raise ValueError("Explicit alternatives must be provided")
    identities = set()
    for group in groups:
        if not isinstance(group, list) or not group or len(group) > 16:
            raise ValueError("Each alternative requires all of its stated conditions")
        for rule in group:
            if (not isinstance(rule, dict) or set(rule) != {"id", "stage", "direction", "level"}
                    or not isinstance(rule["id"], str) or not rule["id"] or rule["id"] in identities
                    or rule["stage"] not in ("intraday", "close", "next_day")
                    or rule["direction"] not in ("above", "below") or not _positive(rule["level"])):
                raise ValueError("Invalid condition")
            identities.add(rule["id"])


def evaluate_plan(plan, *, analysis_as_of, regular_close=None, official_open=None, live_quote=None, calendar=None):
    _validate_plan(plan)
    now, created = _stamp(analysis_as_of), _stamp(plan["created_at"])
    sessions = list((calendar or _schedule)(plan["market"], plan["origin_session"]))
    if not sessions or sessions[0][0] != plan["origin_session"] or created > now:
        raise ValueError("Origin must be a trading session with a visible plan")
    origin, _, origin_close = sessions[0]
    position = next((i for i, (_, opening, closing) in enumerate(sessions) if opening <= now < closing), None)
    allowed = position is not None and position < plan["valid_sessions"] + 1
    quote = None
    if allowed:
        day, market_open, _ = sessions[position]
        quote = _read_market_record(live_quote, plan, day, purpose="quote", earliest=max(market_open, created), latest=now, now=now)
        if quote and (now - _stamp(live_quote["event_at"])).total_seconds() >= plan["quote_max_age_seconds"]:
            quote = None
    close = None
    if now >= origin_close and created <= origin_close:
        close = _read_market_record(regular_close, plan, origin, purpose="final_regular_close",
                                    earliest=origin_close, latest=origin_close, now=now)
    opening = None
    next_window = allowed and position == 1 and now < market_open + timedelta(seconds=plan["execution_window_seconds"])
    if next_window:
        opening = _read_market_record(official_open, plan, day, purpose="official_regular_open",
                                      earliest=market_open, latest=min(now, market_open + timedelta(seconds=plan["max_open_delay_seconds"])),
                                      now=now)
    gap_ok = bool(close and opening and abs(opening[0] / close[0] - 1) * 10000 <= plan["max_gap_bps"] + 1e-9)
    results = {}
    ready_groups = []
    deadlines = []
    for index, group in enumerate(plan["alternatives"]):
        joined = bool(quote) and allowed
        for rule in group:
            stage = rule["stage"]
            measured = {"intraday": quote, "close": close, "next_day": opening}[stage]
            value = measured[0] if measured else None
            crossed = value is not None and (value >= rule["level"] if rule["direction"] == "above" else value <= rule["level"])
            next_session_ready = next_window and gap_ok
            ready = crossed and (stage == "intraday" or next_session_ready)
            joined = joined and ready
            results[rule["id"]] = {"stage": stage, "crossed": crossed, "ready": ready,
                                   "observation_as_of": measured[1].isoformat() if measured else None}
        if joined:
            ready_groups.append(index)
            session_deadline = sessions[position][2]
            if any(rule["stage"] != "intraday" for rule in group):
                session_deadline = min(session_deadline, market_open + timedelta(seconds=plan["execution_window_seconds"]))
            deadlines.append(session_deadline)
    quote_deadline = (_stamp(live_quote["event_at"]) + timedelta(seconds=plan["quote_max_age_seconds"])) if quote else None
    return {
        "paper_candidate_ready": bool(ready_groups), "execution_authority": False,
        "matched_alternatives": ready_groups, "conditions": results,
        "origin_session": origin, "current_session": sessions[position][0] if position is not None else None,
        "quote_fresh": bool(quote), "within_session_ttl": allowed, "verified_next_open": bool(opening),
        "opening_gap_allowed": gap_ok,
        "quote_expires_at": quote_deadline.isoformat() if quote_deadline else None,
        "candidate_valid_until": min(max(deadlines), quote_deadline).isoformat() if deadlines else None,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    args = parser.parse_args(argv)
    print(json.dumps(evaluate_plan(**json.loads(args.input.read_text(encoding="utf-8"))), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
