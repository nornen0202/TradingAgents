"""Preregistered, forward-only paper comparisons using a local append-only ledger.

This module never places orders or fetches prices. Baseline and AI decisions are
recorded together *before* a session opens, then share the same price panel,
capital, costs and next-open fills. Injecting a clock is for offline replay/tests;
such replay cannot establish that historical source data were point-in-time.
"""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sqlite3
from datetime import datetime, timezone
from typing import Any, Callable, Mapping


def _stamp(value: Any) -> datetime:
    try:
        result = value if isinstance(value, datetime) else datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (ValueError, TypeError) as exc:
        raise ValueError("A valid timezone-aware timestamp is required") from exc
    if result.tzinfo is None or result.utcoffset() is None:
        raise ValueError("A timezone-aware timestamp is required")
    return result.astimezone(timezone.utc)


def _json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def _digest(value: Any) -> str:
    return hashlib.sha256(_json(value).encode("utf-8")).hexdigest()


def _number(value: Any, *, positive: bool = False) -> float:
    if type(value) not in (int, float) or not math.isfinite(value) or value < 0 or (positive and value == 0):
        raise ValueError("A finite positive number is required" if positive else "A finite nonnegative number is required")
    return float(value)


def validate_spec(spec: Mapping[str, Any]) -> dict[str, Any]:
    """Copy and validate the complete preregistration, including research cutoff."""
    required = {"id", "hypothesis", "universe", "capital", "currency", "costs", "benchmark",
                "baseline_rules", "ai_rules", "training_end", "forward_start", "forward_end"}
    if not isinstance(spec, Mapping) or set(spec) != required:
        raise ValueError("Experiment spec must contain exactly: " + ", ".join(sorted(required)))
    result = json.loads(_json(dict(spec)))
    for key in ("id", "hypothesis", "currency", "benchmark"):
        if not isinstance(result[key], str) or not result[key].strip():
            raise ValueError(f"{key} must be nonempty text")
    universe = result["universe"]
    if (not isinstance(universe, list) or not universe or len(universe) > 1000
            or any(not isinstance(ticker, str) or not ticker.strip() for ticker in universe)
            or len(set(universe)) != len(universe)):
        raise ValueError("Universe must contain unique, nonempty ticker strings")
    result["capital"] = _number(result["capital"], positive=True)
    if not isinstance(result["costs"], dict) or set(result["costs"]) != {"fee_bps", "slippage_bps"}:
        raise ValueError("Costs require fee_bps and slippage_bps per side")
    for key in ("fee_bps", "slippage_bps"):
        result["costs"][key] = _number(result["costs"][key])
        if result["costs"][key] >= 10000:
            raise ValueError("Per-side costs must be below 10000 bps")
    for key in ("baseline_rules", "ai_rules"):
        rules = result[key]
        if not isinstance(rules, dict) or not rules or not isinstance(rules.get("strategy"), str) or not rules["strategy"].strip():
            raise ValueError("Each frozen rule set requires a strategy identifier")
    start, end, training_end = (_stamp(result[key]) for key in ("forward_start", "forward_end", "training_end"))
    if not training_end < start < end:
        raise ValueError("Require training_end < forward_start < forward_end")
    for key in ("forward_start", "forward_end", "training_end"):
        result[key] = _stamp(result[key]).isoformat()
    return result


class ExperimentRegistry:
    """Local research ledger. Use a separate path from production paper accounts."""

    def __init__(self, path: str | Path, *, clock: Callable[[], datetime] | None = None):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path, timeout=20)
        self.db.row_factory = sqlite3.Row
        self.clock = clock or (lambda: datetime.now(timezone.utc))
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS experiments(
                id TEXT PRIMARY KEY, spec TEXT NOT NULL, spec_hash TEXT NOT NULL,
                registered_at TEXT NOT NULL, frozen_at TEXT);
            CREATE TABLE IF NOT EXISTS experiment_decisions(
                experiment_id TEXT NOT NULL, session_id TEXT NOT NULL,
                recorded_at TEXT NOT NULL, open_at TEXT NOT NULL,
                payload TEXT NOT NULL, payload_hash TEXT NOT NULL,
                PRIMARY KEY(experiment_id, session_id));
            CREATE TABLE IF NOT EXISTS experiment_sessions(
                experiment_id TEXT NOT NULL, session_id TEXT NOT NULL,
                recorded_at TEXT NOT NULL, close_at TEXT NOT NULL,
                payload TEXT NOT NULL, payload_hash TEXT NOT NULL,
                PRIMARY KEY(experiment_id, session_id));
            CREATE TRIGGER IF NOT EXISTS experiment_spec_immutable
                BEFORE UPDATE OF spec, spec_hash, registered_at ON experiments
                BEGIN SELECT RAISE(ABORT, 'Experiment spec is immutable'); END;
            CREATE TRIGGER IF NOT EXISTS experiment_freeze_immutable
                BEFORE UPDATE OF frozen_at ON experiments WHEN OLD.frozen_at IS NOT NULL
                BEGIN SELECT RAISE(ABORT, 'Experiment freeze is immutable'); END;
            CREATE TRIGGER IF NOT EXISTS experiment_no_delete
                BEFORE DELETE ON experiments BEGIN SELECT RAISE(ABORT, 'Experiment is immutable'); END;
            CREATE TRIGGER IF NOT EXISTS decision_no_update
                BEFORE UPDATE ON experiment_decisions BEGIN SELECT RAISE(ABORT, 'Decision is immutable'); END;
            CREATE TRIGGER IF NOT EXISTS decision_no_delete
                BEFORE DELETE ON experiment_decisions BEGIN SELECT RAISE(ABORT, 'Decision is immutable'); END;
            CREATE TRIGGER IF NOT EXISTS session_no_update
                BEFORE UPDATE ON experiment_sessions BEGIN SELECT RAISE(ABORT, 'Session is immutable'); END;
            CREATE TRIGGER IF NOT EXISTS session_no_delete
                BEFORE DELETE ON experiment_sessions BEGIN SELECT RAISE(ABORT, 'Session is immutable'); END;
        """)

    def close(self) -> None:
        self.db.close()

    def _now(self) -> datetime:
        return _stamp(self.clock())

    def _load(self, experiment_id: str) -> tuple[dict[str, Any], sqlite3.Row]:
        row = self.db.execute("SELECT * FROM experiments WHERE id=?", (experiment_id,)).fetchone()
        if row is None:
            raise ValueError("Unknown experiment")
        spec = json.loads(row["spec"])
        if _digest(spec) != row["spec_hash"]:
            raise ValueError("Experiment integrity check failed")
        return spec, row

    def register(self, spec: Mapping[str, Any]) -> dict[str, Any]:
        checked, now = validate_spec(spec), self._now()
        if not _stamp(checked["training_end"]) < now < _stamp(checked["forward_start"]):
            raise ValueError("Register after the research cutoff and before the forward start")
        with self.db:
            self.db.execute("INSERT INTO experiments VALUES (?,?,?,?,NULL)",
                            (checked["id"], _json(checked), _digest(checked), now.isoformat()))
        return {"id": checked["id"], "spec_hash": _digest(checked), "registered_at": now.isoformat()}

    def freeze(self, experiment_id: str) -> dict[str, Any]:
        with self.db:
            spec, row = self._load(experiment_id)
            now = self._now()
            if row["frozen_at"] is not None:
                raise ValueError("Experiment is already frozen")
            if not _stamp(row["registered_at"]) <= now < _stamp(spec["forward_start"]):
                raise ValueError("Freeze must occur after registration and before the forward start")
            self.db.execute("UPDATE experiments SET frozen_at=? WHERE id=? AND frozen_at IS NULL", (now.isoformat(), experiment_id))
        return {"id": experiment_id, "spec_hash": row["spec_hash"], "frozen_at": now.isoformat()}

    def record_decision(self, experiment_id: str, decision: Mapping[str, Any]) -> dict[str, Any]:
        """Lock paired targets before the stated session opens; no backdated targets.

        Model costs are denominated in the spec's valuation currency. Validation
        seconds are measured operator/review time, separately from model cost.
        """
        fields = {"session_id", "open_at", "data_as_of", "dataset_version", "baseline_weights",
                  "ai_weights", "model_cost", "validation_seconds"}
        if not isinstance(decision, Mapping) or set(decision) != fields:
            raise ValueError("Decision must contain exactly: " + ", ".join(sorted(fields)))
        payload = json.loads(_json(dict(decision)))
        with self.db:
            spec, row = self._load(experiment_id)
            now = self._now()
            open_at = _stamp(payload["open_at"])
            if row["frozen_at"] is None or not _stamp(row["frozen_at"]) <= now < open_at:
                raise ValueError("Freeze first and record paired decisions before session open")
            if not _stamp(spec["forward_start"]) <= open_at < _stamp(spec["forward_end"]):
                raise ValueError("Session open is outside the frozen forward window")
            if not _stamp(payload["data_as_of"]) <= now:
                raise ValueError("Decision inputs contain future information")
            for key in ("session_id", "dataset_version"):
                if not isinstance(payload[key], str) or not payload[key].strip():
                    raise ValueError(f"{key} must be nonempty text")
            previous = self.db.execute("SELECT open_at, recorded_at FROM experiment_decisions WHERE experiment_id=? ORDER BY open_at DESC LIMIT 1", (experiment_id,)).fetchone()
            if previous and (open_at <= _stamp(previous["open_at"]) or now < _stamp(previous["recorded_at"])):
                raise ValueError("Decisions must be recorded chronologically with unique session opens")
            observed_after = self.db.execute("SELECT recorded_at FROM experiment_sessions WHERE experiment_id=? ORDER BY recorded_at DESC LIMIT 1", (experiment_id,)).fetchone()
            if observed_after and now < _stamp(observed_after["recorded_at"]):
                raise ValueError("Clock cannot regress behind an existing outcome observation")
            for arm in ("baseline_weights", "ai_weights"):
                weights = payload[arm]
                if not isinstance(weights, dict) or set(weights) - set(spec["universe"]):
                    raise ValueError("Targets must use the frozen universe")
                payload[arm] = {ticker: _number(weights.get(ticker, 0)) for ticker in spec["universe"]}
                if sum(payload[arm].values()) > 1 + 1e-12:
                    raise ValueError("Only unlevered long-only weights are supported")
            for key in ("model_cost", "validation_seconds"):
                payload[key] = _number(payload[key])
            payload["open_at"] = open_at.isoformat()
            payload["data_as_of"] = _stamp(payload["data_as_of"]).isoformat()
            payload["spec_hash"] = row["spec_hash"]
            self.db.execute("INSERT INTO experiment_decisions VALUES (?,?,?,?,?,?)", (experiment_id,
                            payload["session_id"], now.isoformat(), open_at.isoformat(), _json(payload), _digest(payload)))
        return {"session_id": payload["session_id"], "decision_hash": _digest(payload), "recorded_at": now.isoformat()}

    def record_session(self, experiment_id: str, session: Mapping[str, Any]) -> dict[str, Any]:
        """Append completed, available OHLC observations for one locked decision."""
        fields = {"session_id", "close_at", "available_at", "opens", "closes", "benchmark_open", "benchmark_close"}
        if not isinstance(session, Mapping) or set(session) != fields:
            raise ValueError("Session must contain exactly: " + ", ".join(sorted(fields)))
        payload = json.loads(_json(dict(session)))
        with self.db:
            spec, row = self._load(experiment_id)
            now = self._now()
            decision = self.db.execute("SELECT * FROM experiment_decisions WHERE experiment_id=? AND session_id=?", (experiment_id, payload["session_id"])).fetchone()
            if decision is None:
                raise ValueError("A preregistered paired decision is required")
            close_at, available_at = _stamp(payload["close_at"]), _stamp(payload["available_at"])
            if not _stamp(decision["open_at"]) < close_at <= available_at <= now:
                raise ValueError("Require session open < close <= available_at <= observation time")
            if close_at > _stamp(spec["forward_end"]):
                raise ValueError("Session closes after the frozen forward window")
            previous = self.db.execute("SELECT close_at, recorded_at FROM experiment_sessions WHERE experiment_id=? ORDER BY close_at DESC LIMIT 1", (experiment_id,)).fetchone()
            if previous and (_stamp(decision["open_at"]) <= _stamp(previous["close_at"]) or now < _stamp(previous["recorded_at"])):
                raise ValueError("Sessions must be nonoverlapping and ingested chronologically")
            # An earlier outstanding decision must not silently disappear from performance.
            missing = self.db.execute("SELECT d.session_id FROM experiment_decisions d LEFT JOIN experiment_sessions s ON d.experiment_id=s.experiment_id AND d.session_id=s.session_id WHERE d.experiment_id=? AND d.open_at<? AND s.session_id IS NULL LIMIT 1", (experiment_id, decision["open_at"])).fetchone()
            if missing:
                raise ValueError("Record all earlier sessions before this observation")
            for key in ("opens", "closes"):
                if not isinstance(payload[key], dict) or set(payload[key]) != set(spec["universe"]):
                    raise ValueError("Complete shared price panel required for the frozen universe")
                payload[key] = {ticker: _number(value, positive=True) for ticker, value in payload[key].items()}
            for key in ("benchmark_open", "benchmark_close"):
                payload[key] = _number(payload[key], positive=True)
            for key in ("close_at", "available_at"):
                payload[key] = _stamp(payload[key]).isoformat()
            payload["spec_hash"] = row["spec_hash"]
            self.db.execute("INSERT INTO experiment_sessions VALUES (?,?,?,?,?,?)", (experiment_id,
                            payload["session_id"], now.isoformat(), close_at.isoformat(), _json(payload), _digest(payload)))
        return {"session_id": payload["session_id"], "observation_hash": _digest(payload), "recorded_at": now.isoformat()}

    def report(self, experiment_id: str, *, analysis_as_of: str | datetime) -> dict[str, Any]:
        """Read only information already recorded by the explicit report cutoff."""
        cutoff = _stamp(analysis_as_of)
        if cutoff > self._now():
            raise ValueError("Report cutoff cannot be in the future")
        spec, row = self._load(experiment_id)
        if _stamp(row["registered_at"]) > cutoff:
            raise ValueError("Experiment was not registered at the report cutoff")
        decisions = self.db.execute("SELECT * FROM experiment_decisions WHERE experiment_id=? ORDER BY open_at", (experiment_id,)).fetchall()
        sessions = self.db.execute("SELECT * FROM experiment_sessions WHERE experiment_id=? ORDER BY close_at", (experiment_id,)).fetchall()
        observed = []
        by_id = {}
        for decision in decisions:
            if _stamp(decision["recorded_at"]) <= cutoff:
                payload = self._verified_payload(decision, row["spec_hash"])
                by_id[decision["session_id"]] = payload
        for session in sessions:
            if _stamp(session["recorded_at"]) <= cutoff and _stamp(session["close_at"]) <= cutoff:
                payload = self._verified_payload(session, row["spec_hash"])
                if _stamp(payload["available_at"]) <= cutoff:
                    if session["session_id"] not in by_id:
                        raise ValueError("Observation has no contemporaneous decision")
                    observed.append((by_id[session["session_id"]], payload))
        arms = {arm: _simulate_forward(spec, observed, arm) for arm in ("baseline", "ai", "benchmark")}
        model_cost = sum(item["model_cost"] for item in by_id.values())
        ai_net = arms["ai"]["ending_nav"] - model_cost
        arms["ai"]["net_after_model_cost_pct"] = (ai_net / spec["capital"] - 1) * 100
        return {"id": experiment_id, "spec": spec, "spec_hash": row["spec_hash"],
                "as_of": cutoff.isoformat(), "registered_at": row["registered_at"],
                "frozen_at": row["frozen_at"] if row["frozen_at"] and _stamp(row["frozen_at"]) <= cutoff else None,
                "sessions": len(observed), "pending_sessions": len(by_id) - len(observed),
                "model_cost": model_cost, "validation_seconds": sum(item["validation_seconds"] for item in by_id.values()),
                "currency": spec["currency"], "arms": arms,
                "limitations": ["Forward paper evidence is not proof of profitability, including a 4–8 week trial.",
                                "Fractional long-only units, zero cash interest, no partial fills, liquidity or settlement simulation.",
                                "Rule descriptions are preregistered; recorded decisions require independent rule-compliance review.",
                                "Historical clock replay does not certify point-in-time data or prevent source revisions."]}

    @staticmethod
    def _verified_payload(row: sqlite3.Row, spec_hash: str) -> dict[str, Any]:
        payload = json.loads(row["payload"])
        if _digest(payload) != row["payload_hash"] or payload["spec_hash"] != spec_hash:
            raise ValueError("Experiment observation integrity check failed")
        return payload


def _simulate_forward(spec: dict[str, Any], observations: list, arm: str) -> dict[str, Any]:
    """Shared cash-constrained next-open simulation; sells precede buys."""
    capital = spec["capital"]
    cash, units, navs, orders, notional, total_cost = capital, {}, [capital], 0, 0.0, 0.0
    fee = spec["costs"]["fee_bps"] / 10000
    slippage = spec["costs"]["slippage_bps"] / 10000
    curve = []
    for n, (decision, session) in enumerate(observations):
        if arm == "benchmark":
            opens, closes = {"benchmark": session["benchmark_open"]}, {"benchmark": session["benchmark_close"]}
            weights = {"benchmark": 1.0}
        else:
            opens, closes, weights = session["opens"], session["closes"], decision[f"{arm}_weights"]
        equity_open = cash + sum(units.get(ticker, 0) * price for ticker, price in opens.items())
        # The benchmark is a single purchase, whereas each strategy may rebalance.
        if arm != "benchmark" or n == 0:
            reserve = (1 + slippage) * (1 + fee)
            deltas = {ticker: weights.get(ticker, 0) * equity_open / reserve / price - units.get(ticker, 0)
                      for ticker, price in opens.items()}
            for ticker in sorted(deltas, key=lambda value: deltas[value]):
                quantity = deltas[ticker]
                raw_price = opens[ticker]
                fill_price = raw_price * (1 + slippage if quantity > 0 else 1 - slippage)
                if quantity > 0:
                    quantity = min(quantity, max(cash, 0) / (fill_price * (1 + fee)))
                if abs(quantity * fill_price) < 1e-8:
                    continue
                commission = abs(quantity * fill_price) * fee
                cash -= quantity * fill_price + commission
                units[ticker] = units.get(ticker, 0) + quantity
                total_cost += commission + abs(quantity) * abs(fill_price - raw_price)
                notional += abs(quantity * raw_price)
                orders += 1
        nav = cash + sum(quantity * closes[ticker] for ticker, quantity in units.items())
        navs.append(nav)
        curve.append({"session_id": session["session_id"], "at": session["close_at"], "nav": nav, "cash": cash})
    peak, drawdown = capital, 0.0
    for nav in navs:
        peak = max(peak, nav)
        drawdown = min(drawdown, nav / peak - 1)
    return {"ending_nav": navs[-1], "net_return_pct": (navs[-1] / capital - 1) * 100,
            "max_drawdown_pct": drawdown * 100, "turnover_over_initial": notional / capital,
            "trade_count": orders, "execution_cost": total_cost, "curve": curve}


def validate_chronological_research(
    open_prices, close_prices, baseline_function, ai_function, *,
    training_end: str, evaluation_start: str, evaluation_end: str,
    analysis_as_of: str, initial: float, cost_bps: float,
) -> dict[str, Any]:
    """Offline holdout comparison with identical capital, prices and next-open costs.

    Indices must be timezone-aware *completed bar times*. All future rows are
    removed before either target function runs. Every historical prefix is
    checked (up to 2,000 bars), not merely a sample. These checks cannot establish
    original publication times or detect every kind of model training leakage.
    """
    import pandas as pd

    from .research_backtest import simulate
    from .research_validation import prefix_invariance

    train, start, end, cutoff = map(_stamp, (training_end, evaluation_start, evaluation_end, analysis_as_of))
    if not train < start <= end <= cutoff:
        raise ValueError("Require research cutoff < holdout start <= end <= analysis_as_of")
    if not open_prices.index.equals(close_prices.index) or not open_prices.columns.equals(close_prices.columns):
        raise ValueError("Shared OHLC axes must match")
    if (not isinstance(close_prices.index, pd.DatetimeIndex) or close_prices.index.tz is None
            or not close_prices.index.is_monotonic_increasing or close_prices.index.has_duplicates):
        raise ValueError("Unique, chronological, timezone-aware completed bar times required")
    panel = close_prices.loc[close_prices.index <= end].copy()
    opens = open_prices.loc[panel.index].copy()
    if len(panel) < 3 or len(panel) > 2000 or not (panel.index <= train).any():
        raise ValueError("Require 3–2000 bars with at least one research observation before the holdout")
    arms = {}
    for name, function in (("baseline", baseline_function), ("ai", ai_function)):
        invariance = prefix_invariance(panel, function, checkpoints=len(panel))
        if not invariance["passed"]:
            raise ValueError(f"{name} target function changes past decisions when future bars are added")
        desired = function(panel.copy())
        metrics, curve, orders = simulate(opens, panel, desired, start=start.isoformat(), end=end.isoformat(),
                                          initial=initial, cost_bps=cost_bps, rebalance="daily")
        arms[name] = {"metrics": metrics, "curve": curve, "orders": orders, "prefix_validation": invariance}
    return {"training_end": train.isoformat(), "evaluation_start": start.isoformat(), "evaluation_end": end.isoformat(),
            "analysis_as_of": cutoff.isoformat(), "initial": initial, "cost_bps_per_side": cost_bps,
            "arms": arms, "limitations": ["Chronological consistency does not certify historical publication times or model-training independence.",
                                           "Retrospective holdout results are not live forward evidence or proof of profitability."]}


def main(argv: list[str] | None = None) -> int:
    """Explicit offline-only CLI; never changes live execution configuration."""
    import argparse

    parser = argparse.ArgumentParser(description="Preregister and review forward paper experiments")
    parser.add_argument("--registry", required=True, type=Path)
    sub = parser.add_subparsers(dest="command", required=True)
    register = sub.add_parser("register")
    register.add_argument("--input", required=True, type=Path)
    for name in ("freeze", "decision", "session", "report"):
        command = sub.add_parser(name)
        command.add_argument("--id", required=True)
        if name in {"decision", "session"}:
            command.add_argument("--input", required=True, type=Path)
        if name == "report":
            command.add_argument("--as-of", required=True)
    args = parser.parse_args(argv)
    registry = ExperimentRegistry(args.registry)
    try:
        if args.command == "register":
            result = registry.register(json.loads(args.input.read_text(encoding="utf-8")))
        elif args.command == "freeze":
            result = registry.freeze(args.id)
        elif args.command == "decision":
            result = registry.record_decision(args.id, json.loads(args.input.read_text(encoding="utf-8")))
        elif args.command == "session":
            result = registry.record_session(args.id, json.loads(args.input.read_text(encoding="utf-8")))
        else:
            result = registry.report(args.id, analysis_as_of=args.as_of)
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
        return 0
    except (ValueError, TypeError, OSError, sqlite3.IntegrityError) as exc:
        parser.error(str(exc))
    finally:
        registry.close()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
