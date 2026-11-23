"""Versioned, forward-only paper promotion evidence. This ledger cannot authorize orders."""

from __future__ import annotations

import argparse
from datetime import date, datetime, timedelta, timezone
import hashlib
import json
import math
from pathlib import Path
import sqlite3
from statistics import mean, stdev
from zoneinfo import ZoneInfo

from tradingagents.calendar_access import get_exchange_calendar
from tradingagents.scheduled.market_calendar import default_calendar_name, is_supplemental_market_holiday

from .experiments import _stamp


def _encode(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _policy(spec):
    required = {"version", "market", "sample_kind", "minimum_sessions", "cost_version", "benchmark"}
    if not isinstance(spec, dict) or set(spec) != required:
        raise ValueError("Promotion policy requires version, market, sample kind, session floor, costs and benchmark")
    if (spec["market"] not in ("KR", "US") or spec["sample_kind"] not in ("round_trip", "rebalance")
            or type(spec["minimum_sessions"]) is not int or not 60 <= spec["minimum_sessions"] <= 120
            or any(not isinstance(spec[key], str) or not spec[key].strip()
                   for key in ("version", "cost_version", "benchmark"))):
        raise ValueError("Invalid promotion policy")
    return {
        **spec,
        "minimum_samples": 30 if spec["sample_kind"] == "round_trip" else 6,
        "minimum_regimes": 2,
        "minimum_sharpe_delta": 0.20,
        "minimum_drawdown_relief": 0.25,
        "minimum_session_availability": 0.99,
    }


def _sessions(market, start, as_of):
    zone = ZoneInfo("Asia/Seoul" if market == "KR" else "America/New_York")
    calendar = get_exchange_calendar(default_calendar_name(market))
    low, high = start.astimezone(zone).date(), as_of.astimezone(zone).date()
    for session in calendar.sessions_in_range(low.isoformat(), high.isoformat()):
        day = session.date()
        if is_supplemental_market_holiday(market=market, session_date=day):
            continue
        opening, closing = _stamp(calendar.session_open(session)), _stamp(calendar.session_close(session))
        if start < opening and closing <= as_of:
            yield day.isoformat(), opening, closing


def _finite_return(value):
    return type(value) in (int, float) and math.isfinite(value) and -1 < value


def _observation(value, *, policy, opening, closing):
    keys = {"cost_version", "benchmark", "regime", "net_return", "benchmark_net_return",
            "samples", "order_ids", "mismatches", "monitored_seconds", "kill_switch_drill_id", "source_id"}
    if not isinstance(value, dict) or set(value) != keys:
        raise ValueError("Incomplete paper observation")
    if (value["cost_version"] != policy["cost_version"] or value["benchmark"] != policy["benchmark"]
            or value["regime"] not in ("risk_on", "neutral", "risk_off")
            or not all(_finite_return(value[key]) for key in ("net_return", "benchmark_net_return"))
            or type(value["mismatches"]) is not int or value["mismatches"] < 0
            or type(value["monitored_seconds"]) is not int
            or not 0 <= value["monitored_seconds"] <= (closing - opening).total_seconds()
            or not isinstance(value["source_id"], str) or not value["source_id"].strip()
            or (value["kill_switch_drill_id"] is not None
                and (not isinstance(value["kill_switch_drill_id"], str) or not value["kill_switch_drill_id"].strip()))):
        raise ValueError("Observation does not match the frozen policy or session")
    for key in ("samples", "order_ids"):
        ids = value[key]
        if not isinstance(ids, list) or any(not isinstance(item, str) or not item.strip() for item in ids):
            raise ValueError("Evidence IDs must be explicit")
    return {**value, "samples": sorted(value["samples"]), "order_ids": sorted(value["order_ids"])}


def _statistics(returns):
    if not returns:
        return None, None
    log_wealth = peak = 0.0
    drawdown = 0.0
    for value in returns:
        log_wealth += math.log1p(value)
        peak = max(peak, log_wealth)
        drawdown = max(drawdown, -math.expm1(log_wealth - peak))
    volatility = stdev(returns) if len(returns) > 1 else 0
    sharpe = mean(returns) / volatility * math.sqrt(252) if volatility else None
    return sharpe if sharpe is None or math.isfinite(sharpe) else None, drawdown


class PromotionLedger:
    def __init__(self, path: Path, *, clock=None, sessions=None):
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._sessions = sessions or _sessions
        self._fixture_only = clock is not None or sessions is not None
        path.parent.mkdir(parents=True, exist_ok=True)
        self._db = sqlite3.connect(path, timeout=20)
        self._db.executescript("""
            CREATE TABLE IF NOT EXISTS promotion_starts(
                version TEXT PRIMARY KEY, policy TEXT NOT NULL, policy_hash TEXT NOT NULL,
                started_at TEXT NOT NULL, fixture_only INTEGER NOT NULL
            );
            CREATE TABLE IF NOT EXISTS promotion_days(
                version TEXT NOT NULL, session TEXT NOT NULL, observed_at TEXT NOT NULL,
                evidence TEXT NOT NULL, PRIMARY KEY(version, session)
            );
            CREATE TRIGGER IF NOT EXISTS promotion_start_no_update BEFORE UPDATE ON promotion_starts
                BEGIN SELECT RAISE(ABORT, 'Promotion policy is frozen'); END;
            CREATE TRIGGER IF NOT EXISTS promotion_start_no_delete BEFORE DELETE ON promotion_starts
                BEGIN SELECT RAISE(ABORT, 'Promotion policy is frozen'); END;
            CREATE TRIGGER IF NOT EXISTS promotion_day_no_update BEFORE UPDATE ON promotion_days
                BEGIN SELECT RAISE(ABORT, 'Promotion evidence is append-only'); END;
            CREATE TRIGGER IF NOT EXISTS promotion_day_no_delete BEFORE DELETE ON promotion_days
                BEGIN SELECT RAISE(ABORT, 'Promotion evidence is append-only'); END;
        """)

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self._db.close()

    def start(self, spec):
        policy = _policy(spec)
        encoded = _encode(policy)
        digest = hashlib.sha256(encoded.encode()).hexdigest()
        with self._db:
            self._db.execute("BEGIN IMMEDIATE")
            row = self._db.execute("SELECT policy_hash, fixture_only FROM promotion_starts WHERE version=?",
                                   (policy["version"],)).fetchone()
            if row is not None and row != (digest, int(self._fixture_only)):
                raise ValueError("A policy version cannot be repurposed")
            self._db.execute("INSERT OR IGNORE INTO promotion_starts VALUES (?,?,?,?,?)",
                             (policy["version"], encoded, digest, _stamp(self._clock()).isoformat(), int(self._fixture_only)))
        return digest

    def _started(self, version):
        row = self._db.execute("SELECT policy, policy_hash, started_at, fixture_only FROM promotion_starts WHERE version=?",
                               (version,)).fetchone()
        if row is None:
            raise ValueError("Unknown promotion policy version")
        return json.loads(row[0]), row[1], _stamp(row[2]), bool(row[3])

    def record(self, version, session, observation):
        if not isinstance(session, str) or date.fromisoformat(session).isoformat() != session:
            raise ValueError("Require an ISO exchange session date")
        policy, _, start, fixture = self._started(version)
        if fixture != self._fixture_only:
            raise ValueError("Fixture and forward ledgers require separate evidence")
        now = _stamp(self._clock())
        with self._db:
            self._db.execute("BEGIN IMMEDIATE")
            row = self._db.execute("SELECT evidence FROM promotion_days WHERE version=? AND session=?",
                                   (version, session)).fetchone()
            session_bounds = {day: (opening, closing) for day, opening, closing in self._sessions(policy["market"], start, now)}
            if session not in session_bounds:
                raise ValueError("Session must close after preregistration and before observation")
            opening, closing = session_bounds[session]
            encoded = _encode(_observation(observation, policy=policy, opening=opening, closing=closing))
            if row is not None:
                if row[0] != encoded:
                    raise ValueError("Conflicting evidence for an existing session")
                return False
            if now > closing + timedelta(hours=12):
                raise ValueError("The forward observation window has expired")
            self._db.execute("INSERT INTO promotion_days VALUES (?,?,?,?)", (version, session, now.isoformat(), encoded))
        return True

    def status(self, version):
        policy, digest, start, fixture = self._started(version)
        now = _stamp(self._clock())
        expected = list(self._sessions(policy["market"], start, now))
        stored = {day: json.loads(evidence) for day, evidence in self._db.execute(
            "SELECT session, evidence FROM promotion_days WHERE version=? AND observed_at<=?", (version, now.isoformat()))}
        observations = [stored[day] for day, _, _ in expected if day in stored]
        missed = sum(day not in stored for day, _, _ in expected)
        seconds = sum((end - begin).total_seconds() for _, begin, end in expected)
        uptime = sum(row["monitored_seconds"] for row in observations) / seconds if seconds else 0.0
        orders = [order for row in observations for order in row["order_ids"]]
        samples = {item for row in observations for item in row["samples"]}
        regimes = {row["regime"] for row in observations}
        mismatches = sum(row["mismatches"] for row in observations)
        duplicates = len(orders) - len(set(orders))
        sharpe, mdd = _statistics([row["net_return"] for row in observations])
        benchmark_sharpe, benchmark_mdd = _statistics([row["benchmark_net_return"] for row in observations])
        qualifying_risk = (
            (sharpe is not None and benchmark_sharpe is not None
             and sharpe >= benchmark_sharpe + policy["minimum_sharpe_delta"])
            or (mdd is not None and benchmark_mdd is not None and benchmark_mdd > 0
                and mdd <= benchmark_mdd * (1 - policy["minimum_drawdown_relief"]))
        )
        checks = {
            "session_window": len(expected) >= policy["minimum_sessions"] and missed == 0,
            "regimes": len(regimes) >= policy["minimum_regimes"],
            "sample": len(samples) >= policy["minimum_samples"],
            "relative_risk": qualifying_risk,
            "reconciliation": mismatches == 0 and duplicates == 0,
            "availability": uptime >= policy["minimum_session_availability"],
            "kill_switch": any(row["kill_switch_drill_id"] for row in observations),
            "forward_observation": not fixture and not self._fixture_only,
        }
        return {
            "policy": policy, "policy_hash": digest, "started_at": start.isoformat(), "as_of": now.isoformat(),
            "expected_sessions": len(expected), "observed_sessions": len(observations), "missing_sessions": missed,
            "regimes": sorted(regimes), "unique_samples": len(samples), "duplicate_orders": duplicates,
            "reconciliation_mismatches": mismatches, "availability": uptime,
            "sharpe": sharpe, "benchmark_sharpe": benchmark_sharpe, "mdd": mdd, "benchmark_mdd": benchmark_mdd,
            "checks": checks, "eligible_for_review": all(checks.values()), "live_order_authority": False,
        }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ledger", type=Path)
    actions = parser.add_subparsers(dest="command", required=True)
    actions.add_parser("start").add_argument("policy", type=Path)
    record = actions.add_parser("record")
    record.add_argument("version")
    record.add_argument("session")
    record.add_argument("evidence", type=Path)
    actions.add_parser("status").add_argument("version")
    args = parser.parse_args(argv)
    with PromotionLedger(args.ledger) as ledger:
        if args.command == "start":
            result = {"policy_hash": ledger.start(json.loads(args.policy.read_text(encoding="utf-8")))}
        elif args.command == "record":
            result = {"added": ledger.record(args.version, args.session, json.loads(args.evidence.read_text(encoding="utf-8")))}
        else:
            result = ledger.status(args.version)
    print(_encode(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
