"""Explicit session-level entry evidence for isolated research and paper planning."""

from __future__ import annotations

import argparse
from datetime import date, timedelta
import json
import math
from pathlib import Path
import re
from zoneinfo import ZoneInfo

from tradingagents.calendar_access import get_exchange_calendar
from tradingagents.scheduled.market_calendar import default_calendar_name, is_supplemental_market_holiday

from .experiments import _stamp

RECEIPT_SCHEMA = "tradingagents.regular-session-observations/v1"
_PROVIDERS = {"KR": {"KIS_DOMESTIC_REGULAR_SESSION"}, "US": {"KIS_US_REGULAR_SESSION", "ALPACA_SIP_REGULAR_SESSION"}}
_OBSERVATION_FIELDS = ("kind", "event_at", "observed_at", "price", "ticker", "source", "market", "currency", "session",
                       "venue", "session_id", "price_basis", "scheduled_event_at", "revised_at")
_ENTRY_GROUP = re.compile(r"[A-Za-z0-9_-]{1,32}")
ENTRY_CONFIRMATION_STAGES = {"intraday", "close", "next_open", "next_session_quote"}
EXPLICIT_NEXT_SESSION_STAGES = {"next_open", "next_session_quote"}


def entry_research_deadline(analysis_at, explicit_expiry=None):
    """Use the existing active research window when no conditional override exists."""
    return _stamp(explicit_expiry) if explicit_expiry is not None else _stamp(analysis_at) + timedelta(hours=24)


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
        if record.get("session_id") is not None:
            venue = record.get("venue")
            if (not isinstance(venue, str) or record["session_id"] != f"{plan['market']}:{venue}:regular:{session}"
                    or record.get("price_basis") != "unadjusted"):
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
                    or rule["stage"] not in ENTRY_CONFIRMATION_STAGES | {"next_day"}
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
    next_session_ready = bool(next_window and gap_ok and quote and quote[1] >= max(close[1], opening[1]))
    results = {}
    ready_groups = []
    deadlines = []
    for index, group in enumerate(plan["alternatives"]):
        joined = bool(quote) and allowed
        for rule in group:
            stage = rule["stage"]
            measured = {"intraday": quote, "close": close, "next_day": opening,
                        "next_open": opening, "next_session_quote": quote if next_window else None}[stage]
            value = measured[0] if measured else None
            crossed = value is not None and (value >= rule["level"] if rule["direction"] == "above" else value <= rule["level"])
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
        "next_session_evidence_available_at": max(close[1], opening[1]).isoformat() if close and opening else None,
        "quote_expires_at": quote_deadline.isoformat() if quote_deadline else None,
        "candidate_valid_until": min(max(deadlines), quote_deadline).isoformat() if deadlines else None,
    }


def load_session_observations(root, ticker, market):
    """Read independently captured regular-session prices from a private directory."""
    if root is None or market not in _PROVIDERS or not re.fullmatch(r"[A-Z0-9][A-Z0-9.\-]{0,31}", ticker):
        return {}
    try:
        root = root.resolve()
        path = (root / f"{ticker}.json").resolve()
        if path.parent != root or path.stat().st_size > 128_000:
            return {}
        receipt = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError):
        return {}
    if (not isinstance(receipt, dict) or receipt.get("schema") != RECEIPT_SCHEMA
            or receipt.get("ticker") != ticker or receipt.get("market") != market
            or receipt.get("price_basis") != "unadjusted"):
        return {}
    return _official_observations(receipt, market)


def _official_observations(records, market):
    if not isinstance(records, dict):
        return {}
    clean = {}
    for name in ("regular_close", "official_open"):
        row = records.get(name)
        if (isinstance(row, dict) and isinstance(row.get("source"), str) and row["source"] in _PROVIDERS[market]
                and (name != "official_open" or row["source"] != "KIS_US_REGULAR_SESSION")):
            clean[name] = {field: row.get(field) for field in _OBSERVATION_FIELDS}
    return clean


def uses_entry_groups(levels):
    return has_explicit_entry_plan(levels) or (
        len(levels) == 1 and _entry_field(levels[0], "confirmation") in {"close", "next_day", "next_open", "next_session_quote"}
    )


def has_explicit_entry_plan(levels):
    return any(_entry_field(level, "confirmation_group") is not None
               or _entry_field(level, "entry_condition_role") is not None
               or _entry_field(level, "confirmation") in EXPLICIT_NEXT_SESSION_STAGES for level in levels)


def _entry_field(level, name):
    return level.get(name) if isinstance(level, dict) else getattr(level, name, None)


def _level_rules(level, identifier):
    stage = _entry_field(level, "confirmation")
    if stage not in ENTRY_CONFIRMATION_STAGES:
        raise ValueError("Unverified entry confirmation stage")
    role = _entry_field(level, "level_type")
    role = str(getattr(role, "value", role)).upper()
    if role in {"BREAKOUT", "RESISTANCE"}:
        price = _entry_field(level, "price")
        if price is None:
            price = _entry_field(level, "high")
        if not _positive(price):
            raise ValueError("Missing breakout threshold")
        return [{"id": identifier, "stage": stage, "direction": "above", "level": price}]
    low, high = _entry_field(level, "low"), _entry_field(level, "high")
    if role == "SUPPORT" and low is None and high is None and _positive(price := _entry_field(level, "price")):
        return [{"id": identifier, "stage": stage, "direction": "above", "level": price}]
    if not _positive(low) or not _positive(high) or low > high:
        raise ValueError("A grouped pullback needs an explicit price range")
    return [
        {"id": f"{identifier}-low", "stage": stage, "direction": "above", "level": low},
        {"id": f"{identifier}-high", "stage": stage, "direction": "below", "level": high},
    ]


def _entry_alternatives(levels, currency, pilot_open):
    levels = [level for level in levels if not (
        _entry_field(level, "entry_condition_role") == "reference"
        and _entry_field(level, "confirmation_group") is None
    )]
    grouped = {}
    required = []
    for level in levels:
        name = _entry_field(level, "confirmation_group")
        role = _entry_field(level, "entry_condition_role")
        if role is not None:
            if name is not None or role != "required":
                return []
            required.append(level)
            continue
        if name is None and len(levels) == 1:
            name = "entry"
        if not isinstance(name, str) or _ENTRY_GROUP.fullmatch(name) is None:
            return []  # A legacy unclassified level may be a required condition.
        grouped.setdefault(name, []).append(level)
    alternatives = []
    if required and not grouped:
        grouped["entry"] = []
    for name, alternative in grouped.items():
        conditions = [*alternative, *required]
        if (not pilot_open and any(_entry_field(level, "confirmation") == "intraday" for level in conditions)
                or any(_entry_field(level, "currency") not in (None, currency) for level in conditions)):
            continue
        try:
            rules = [rule for index, level in enumerate(conditions) for rule in _level_rules(level, f"{name}-{index}")]
        except ValueError:
            continue  # Evidence for a different explicit alternative can still qualify.
        alternatives.append(rules)
    return alternatives


def is_archived_entry_plan(proof, levels, analysis_at):
    try:
        plan = proof["plan"]
        _validate_plan(plan)
        created = _stamp(analysis_at)
        zone = ZoneInfo("Asia/Seoul" if plan["market"] == "KR" else "America/New_York")
        allowed = _entry_alternatives(levels, plan["currency"], pilot_open=True)
        alternatives = plan["alternatives"]
        return (
            _stamp(plan["created_at"]) == created
            and plan["origin_session"] == created.astimezone(zone).date().isoformat()
            and (plan["valid_sessions"], plan["max_open_delay_seconds"], plan["execution_window_seconds"],
                 plan["max_gap_bps"]) == (1, 60, 1800, 200)
            and all(alternative in allowed for alternative in alternatives)
        )
    except (ValueError, TypeError, KeyError, AttributeError):
        return False


def evaluate_entry_groups(contract, market, levels, *, now, max_age_seconds, pilot_open, observations):
    """Compile archived alternatives and evaluate their dated market evidence."""
    if (market.market not in _PROVIDERS or market.ticker != contract.ticker or market.market_session != "regular"
            or not _positive(market.last_price) or not isinstance(market.provider, str) or not market.provider.strip()):
        return None
    currency = "KRW" if market.market == "KR" else "USD"
    alternatives = _entry_alternatives(levels, currency, pilot_open)
    if not alternatives:
        return None
    local_zone = ZoneInfo("Asia/Seoul" if market.market == "KR" else "America/New_York")
    try:
        created, event = _stamp(contract.analysis_asof), _stamp(market.asof)
        plan = {"ticker": market.ticker, "market": market.market, "currency": currency,
                "origin_session": created.astimezone(local_zone).date().isoformat(), "created_at": created.isoformat(),
                "valid_sessions": 1, "quote_max_age_seconds": min(max_age_seconds, 120),
                "max_open_delay_seconds": 60, "execution_window_seconds": 1800, "max_gap_bps": 200,
                "alternatives": alternatives}
        proof = {"plan": plan, **_official_observations(observations, market.market),
                 "live_quote": {"kind": "quote", "source": market.provider, "price": market.last_price,
                                "ticker": market.ticker, "market": market.market, "currency": currency,
                                "session": event.astimezone(local_zone).date().isoformat(),
                                "event_at": event.isoformat(), "observed_at": _stamp(now).isoformat()}}
        evaluated = evaluate_plan(analysis_as_of=now.isoformat(), **proof)
    except (ValueError, TypeError, KeyError):
        return None
    return {**proof, "evaluation": evaluated}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    args = parser.parse_args(argv)
    print(json.dumps(evaluate_plan(**json.loads(args.input.read_text(encoding="utf-8"))), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
