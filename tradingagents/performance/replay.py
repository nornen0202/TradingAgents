"""Deterministic, offline replay of evidence known by an explicit instant."""
from __future__ import annotations

import json
import math
from pathlib import Path
import sqlite3
from typing import Any, Mapping, Sequence

from .lifecycle import timestamp, validate_event


def replay_action_history(
    db_path: str | Path | Sequence[str | Path], *, analysis_as_of: str,
    ticker: str | None = None, initial_cash: float | None = None,
    initial_positions: Mapping[str, float] | None = None,
) -> dict[str, Any]:
    """Read tracker plus a single account's journal without writes or networking.

    Unknown confirmation/settlement clocks exclude legacy evidence. Cash is per
    currency/mode, and recommendation returns never count as execution returns.
    """
    cutoff = timestamp(analysis_as_of)
    if initial_cash is not None and (isinstance(initial_cash, bool) or not isinstance(initial_cash, (int, float)) or not math.isfinite(initial_cash) or initial_cash < 0):
        raise ValueError("Initial cash must be finite and nonnegative")
    if initial_positions is not None and any(isinstance(qty, bool) or not isinstance(qty, (int, float)) or not math.isfinite(qty) or qty < 0 for qty in initial_positions.values()):
        raise ValueError("Initial positions must have finite nonnegative quantities")
    paths = [db_path] if isinstance(db_path, (str, Path)) else list(db_path)
    visible: dict[str, dict] = {}
    for path in paths:
        path = Path(path)
        if not path.is_file():
            continue
        with sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True) as conn:
            conn.row_factory = sqlite3.Row
            if not conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='lifecycle_events'").fetchone():
                continue
            for row in conn.execute("SELECT * FROM lifecycle_events"):
                event = dict(row)
                try:
                    event["payload"] = json.loads(event.pop("payload_json"))
                    validate_event(event)
                    clocks = [event[key] for key in ("occurred_at", "available_at", "confirmed_at", "settled_at", "ingested_at") if event.get(key)]
                    if any(timestamp(value) > cutoff for value in clocks):
                        continue
                except (ValueError, TypeError, KeyError):
                    continue
                if ticker and str(event["payload"].get("ticker", "")).upper() != ticker.upper():
                    continue
                previous = visible.get(event["event_id"])
                if previous and previous != event:
                    raise ValueError("Conflicting lifecycle evidence across journals")
                visible[event["event_id"]] = event
    known_intents = {(event["mode"], event["intent_id"], event["signal_id"]) for event in visible.values() if event["kind"] == "INTENT"}
    visible = {key: event for key, event in visible.items() if event["kind"] != "FILL" or
               (event["mode"], event["intent_id"], event["signal_id"]) in known_intents}
    events = sorted(visible.values(), key=lambda e: (
        max(timestamp(e[k]) for k in ("occurred_at", "available_at", "confirmed_at", "settled_at", "ingested_at") if e.get(k)),
        {"ACCOUNT_SEED": 0, "SIGNAL": 1, "INTENT": 2, "FILL": 3}.get(e["kind"], 4), e["event_id"]))
    signals: dict[str, dict] = {}
    intents: dict[str, dict] = {}
    fills, retrospectives = [], []
    accounts: dict[str, dict] = {}
    for event in events:
        event["event_time"] = event["occurred_at"]
        event["evaluated_at"] = max(timestamp(event[k]) for k in ("available_at", "confirmed_at", "ingested_at") if event.get(k)).isoformat()
        event["is_amended"] = event["payload"].get("is_amended") is True
        payload, kind, mode = event["payload"], event["kind"], event["mode"]
        signal = signals.setdefault(event["signal_id"], {"signal_id": event["signal_id"], "recommendation": None,
                    "recommendation_outcome": None, "intent_ids": [], "fill_event_ids": [], "retrospectives": []})
        if kind == "SIGNAL":
            signal["recommendation"] = payload
        elif kind == "OUTCOME":
            signal["recommendation_outcome"] = payload
        elif kind == "INTENT":
            intents[event["intent_id"]] = {**payload, "intent_id": event["intent_id"], "signal_id": event["signal_id"], "mode": mode}
            if event["intent_id"] not in signal["intent_ids"]:
                signal["intent_ids"].append(event["intent_id"])
        elif kind == "CANCEL":
            if event["intent_id"] in intents:
                intents[event["intent_id"]]["status"] = "CANCELLED"
                intents[event["intent_id"]]["cancelled"] = True
        elif kind == "ACCOUNT_SEED":
            key = f"{mode}:{payload.get('currency', 'KRW')}"
            if key in accounts:
                raise ValueError("Combine journals for one account only; duplicate account seed")
            accounts[key] = {"cash": payload["cash"], "positions": dict(payload.get("positions") or {}), "costs": 0.0,
                             "cash_known": True, "positions_known": True, "position_changes": {}}
        elif kind == "FILL":
            key = f"{mode}:{payload.get('currency', 'KRW')}"
            account = accounts.setdefault(key, {"cash": initial_cash, "positions": dict(initial_positions or {}), "costs": 0.0,
                                                "cash_known": initial_cash is not None, "positions_known": initial_positions is not None, "position_changes": {}})
            quantity, price, cost = payload["quantity"], payload["price"], payload["cost"]
            sign = 1 if payload["side"] == "BUY" else -1
            symbol = payload["ticker"]
            account["positions"][symbol] = account["positions"].get(symbol, 0) + sign * quantity
            account["position_changes"][symbol] = account["position_changes"].get(symbol, 0) + sign * quantity
            if account["cash_known"]:
                account["cash"] -= sign * quantity * price + cost
            account["costs"] += cost
            fill = {**payload, "event_id": event["event_id"], "signal_id": event["signal_id"],
                    "intent_id": event["intent_id"], "mode": mode, "confirmed_at": event["confirmed_at"], "settled_at": event["settled_at"]}
            fill.update(event_time=event["event_time"], ingested_at=event["ingested_at"], evaluated_at=event["evaluated_at"], is_amended=event["is_amended"])
            reference = payload.get("reference_price")
            fill["adverse_slippage_bps"] = sign * (price / reference - 1) * 10000 if isinstance(reference, (int, float)) and reference > 0 else None
            fills.append(fill)
            signal["fill_event_ids"].append(event["event_id"])
            if event["intent_id"] in intents:
                intent = intents[event["intent_id"]]
                intent["filled_quantity"] = intent.get("filled_quantity", 0) + quantity
                requested = intent.get("quantity")
                if not intent.get("cancelled"):
                    intent["status"] = "FILLED" if isinstance(requested, (int, float)) and intent["filled_quantity"] >= requested else "PARTIAL"
        elif kind == "RETROSPECTIVE":
            retrospectives.append(payload)
            signal["retrospectives"].append(payload)
    # A symbol-filtered projection omits other trades, so cannot report cash.
    if ticker:
        accounts = {}
    for account in accounts.values():
        if not account["positions_known"]:
            account["positions"] = None
    return {"status": "replayed", "analysis_as_of": analysis_as_of, "read_only": True,
            "broker_orders_sent": 0, "events": events, "signals": list(signals.values()),
            "intents": list(intents.values()), "fills": fills, "retrospectives": retrospectives,
            "accounts": accounts, "recommendation_outcomes_are_fills": False}


def get_replay_snapshot(ticker, as_of_ts, **kwargs):
    """Canonical chart/replay entry point; lazy import avoids a module cycle."""
    from tradingagents.charting.snapshot import get_replay_snapshot as snapshot
    return snapshot(ticker, as_of_ts, **kwargs)
