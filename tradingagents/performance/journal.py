from __future__ import annotations

import json
import hashlib
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Mapping

from .action_outcomes import initialize_action_tracker
from .lifecycle import append_lifecycle_event, timestamp
from .models import ACTION_TRACKER_SCHEMA


def create_closed_trade_journal_entry(
    *,
    buy_context: Mapping[str, Any],
    sell_context: Mapping[str, Any],
    outcome: Mapping[str, Any],
) -> dict[str, Any]:
    ticker = str(sell_context.get("ticker") or buy_context.get("ticker") or "").strip()
    return {
        "ticker": ticker,
        "buy_context": dict(buy_context),
        "sell_context": dict(sell_context),
        "outcome": dict(outcome),
        "created_at": datetime.now().astimezone().isoformat(),
        "status": "journal_created",
    }


def generate_closed_trade_review(
    *,
    entry_context: Mapping[str, Any],
    exit_context: Mapping[str, Any],
    realized_return_pct: float | None = None,
    holding_days: int | None = None,
    output_path: str | Path | None = None,
) -> dict[str, Any]:
    ticker = str(exit_context.get("ticker") or entry_context.get("ticker") or "").strip()
    entry_action = str(entry_context.get("action") or entry_context.get("entry_action") or "UNKNOWN")
    exit_action = str(exit_context.get("action") or exit_context.get("exit_action") or "UNKNOWN")
    realized = _float_or_none(realized_return_pct if realized_return_pct is not None else exit_context.get("realized_return_pct"))
    days = _int_or_none(holding_days if holding_days is not None else exit_context.get("holding_days"))
    lessons = _rule_based_lessons(realized_return_pct=realized, exit_action=exit_action)
    review = {
        "ticker": ticker,
        "entry_run_id": entry_context.get("run_id"),
        "exit_run_id": exit_context.get("run_id"),
        "entry_action": entry_action,
        "exit_action": exit_action,
        "realized_return_pct": realized,
        "holding_days": days,
        "judgment_evaluation": _judgment_evaluation(realized, exit_action),
        "missed_signals": [],
        "overreacted_signals": [],
        "lessons": lessons,
        "pattern_tags": _pattern_tags(realized, exit_action),
        "created_at": datetime.now().astimezone().isoformat(),
    }
    if output_path:
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(review, indent=2, ensure_ascii=False), encoding="utf-8")
    return review


def store_closed_trade_review(db_path: Path | sqlite3.Connection, review: Mapping[str, Any]) -> int:
    if not isinstance(db_path, sqlite3.Connection):
        initialize_action_tracker(db_path)
        with sqlite3.connect(db_path) as conn:
            return store_closed_trade_review(conn, review)
    conn = db_path
    _prepare_journal(conn)
    identity = {key: review.get(key) for key in ("ticker", "entry_fill_id", "exit_fill_id", "entry_run_id", "exit_run_id", "realized_return_pct", "holding_days")}
    review_id = review.get("review_id") or "review:" + hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()
    canonical = json.dumps({key: value for key, value in review.items() if key not in {"created_at", "ingested_at"}}, sort_keys=True, ensure_ascii=False, allow_nan=False)
    previous = conn.execute("SELECT id,review_json FROM trade_journal WHERE review_id=?", (review_id,)).fetchone()
    if previous:
        if previous[1] is not None and previous[1] != canonical:
            raise ValueError("Review ID reused with different outcome evidence")
        return previous[0]
    cursor = conn.execute(
            """
            INSERT INTO trade_journal (
              ticker, buy_run_id, sell_run_id, buy_context_json, sell_context_json,
              profit_rate, holding_days, missed_signals_json, overreacted_signals_json,
              lessons_json, pattern_tags_json, one_line_summary, confidence_score, created_at,
              review_id, signal_id, confirmed_at, settled_at, review_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                review.get("ticker"),
                review.get("entry_run_id"),
                review.get("exit_run_id"),
                json.dumps(review.get("entry_context") or {"entry_action": review.get("entry_action")}, ensure_ascii=False),
                json.dumps(review.get("exit_context") or {"exit_action": review.get("exit_action")}, ensure_ascii=False),
                review.get("realized_return_pct"),
                review.get("holding_days"),
                json.dumps(review.get("missed_signals") or [], ensure_ascii=False),
                json.dumps(review.get("overreacted_signals") or [], ensure_ascii=False),
                json.dumps(review.get("lessons") or [], ensure_ascii=False),
                json.dumps(review.get("pattern_tags") or [], ensure_ascii=False),
                review.get("judgment_evaluation"),
                0.60,
                review.get("created_at") or datetime.now().astimezone().isoformat(),
                review_id, review.get("signal_id"), review.get("confirmed_at"), review.get("settled_at"),
                canonical,
            ),
        )
    journal_id = cursor.lastrowid
    for lesson in review.get("lessons") or []:
            if not isinstance(lesson, Mapping):
                continue
            conn.execute(
                """
                INSERT INTO learned_intuitions (
                  category, condition, insight, confidence, supporting_trades,
                  success_rate, source_journal_ids_json, is_active, created_at, confirmed_at, settled_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "closed_trade_review",
                    lesson.get("condition") or "closed_trade",
                    lesson.get("reason") or lesson.get("action") or "",
                    0.50,
                    1,
                    None,
                    json.dumps([journal_id]),
                    1,
                    review.get("created_at") or datetime.now().astimezone().isoformat(),
                    review.get("confirmed_at"), review.get("settled_at"),
                ),
            )
    if review.get("signal_id") and review.get("confirmed_at") and review.get("settled_at"):
        append_lifecycle_event(conn, event_id=review_id, signal_id=review["signal_id"], kind="RETROSPECTIVE",
            mode=review.get("mode") or "actual", occurred_at=review.get("closed_at") or review["created_at"],
            available_at=review["created_at"], confirmed_at=review["confirmed_at"], settled_at=review["settled_at"],
            ingested_at=review.get("ingested_at") or review["created_at"], payload=dict(review))
    return journal_id


def _prepare_journal(conn: sqlite3.Connection) -> None:
    for statement in ACTION_TRACKER_SCHEMA:
        conn.execute(statement)
    for table, columns in {
        "trade_journal": {"review_id": "TEXT", "signal_id": "TEXT", "confirmed_at": "TEXT", "settled_at": "TEXT", "review_json": "TEXT"},
        "learned_intuitions": {"confirmed_at": "TEXT", "settled_at": "TEXT"},
    }.items():
        existing = {row[1] for row in conn.execute(f"PRAGMA table_info({table})")}
        for name, sql_type in columns.items():
            if name not in existing:
                conn.execute(f"ALTER TABLE {table} ADD COLUMN {name} {sql_type}")
    conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_trade_journal_review_id ON trade_journal(review_id)")


def record_fill_retrospectives(conn: sqlite3.Connection, *, exit_event_id: str, evaluated_at: str | None = None) -> list[int]:
    """FIFO reviews from known incremental fills, including both sides' costs.

    Seed holdings have unknown acquisition basis and consume sells without a
    fabricated realized return. Partial exits close only the matching lot slice.
    """
    rows = conn.execute("SELECT * FROM lifecycle_events WHERE kind IN ('ACCOUNT_SEED','FILL')").fetchall()
    columns = [row[1] for row in conn.execute("PRAGMA table_info(lifecycle_events)")]
    events = [{**dict(zip(columns, row)), "payload": json.loads(dict(zip(columns, row))["payload_json"])} for row in rows]
    target = next((event for event in events if event["event_id"] == exit_event_id), None)
    if not target or target["payload"].get("side") != "SELL":
        return []
    target_known = max(timestamp(target[k]) for k in ("occurred_at", "available_at", "confirmed_at", "settled_at", "ingested_at"))
    cutoff = timestamp(evaluated_at) if evaluated_at is not None else target_known
    if target_known > cutoff:
        return []
    symbol, currency = target["payload"]["ticker"], target["payload"].get("currency", "KRW")
    lots, ids = [], []
    for event in sorted(events, key=lambda item: (timestamp(item["occurred_at"]), item["event_id"])):
        if event["mode"] != target["mode"] or any(timestamp(event[k]) > cutoff for k in ("occurred_at", "available_at", "confirmed_at", "settled_at", "ingested_at") if event.get(k)):
            continue
        payload = event["payload"]
        if payload.get("currency", "KRW") != currency:
            continue
        if event["kind"] == "ACCOUNT_SEED":
            quantity = (payload.get("positions") or {}).get(symbol, 0)
            if quantity:
                lots.append({"remaining": quantity, "event": None})
            continue
        if payload.get("ticker") != symbol:
            continue
        if payload["side"] == "BUY":
            lots.append({"remaining": payload["quantity"], "event": event})
            continue
        remaining = payload["quantity"]
        while remaining > 1e-9 and lots:
            lot = lots[0]
            closed = min(lot["remaining"], remaining)
            entry = lot["event"]
            if event["event_id"] == exit_event_id and entry:
                buy = entry["payload"]
                costs = buy["cost"] * closed / buy["quantity"] + payload["cost"] * closed / payload["quantity"]
                profit = (payload["price"] - buy["price"]) * closed - costs
                review = generate_closed_trade_review(entry_context={"ticker": symbol, "action": "BUY"},
                    exit_context={"ticker": symbol, "action": "SELL"}, realized_return_pct=100 * profit / (buy["price"] * closed),
                    holding_days=(timestamp(event["occurred_at"]) - timestamp(entry["occurred_at"])).days)
                review.update(review_id=f"review:{entry['event_id']}:{exit_event_id}", entry_fill_id=entry["event_id"],
                    exit_fill_id=exit_event_id, signal_id=event["signal_id"], entry_signal_id=entry["signal_id"],
                    closed_quantity=closed, net_profit=profit, total_cost=costs, currency=currency, mode=event["mode"],
                    measurement_scope="realized_fill_return_after_costs", created_at=cutoff.isoformat(),
                    ingested_at=cutoff.isoformat(),
                    closed_at=event["occurred_at"], confirmed_at=event["confirmed_at"], settled_at=event["settled_at"],
                    entry_context=buy, exit_context=payload)
                review["judgment_evaluation"] = "profitable_fill" if profit >= 0 else "unprofitable_fill"
                ids.append(store_closed_trade_review(conn, review))
            lot["remaining"] -= closed
            remaining -= closed
            if lot["remaining"] <= 1e-9:
                lots.pop(0)
        if event["event_id"] == exit_event_id:
            break
    return ids


def _rule_based_lessons(*, realized_return_pct: float | None, exit_action: str) -> list[dict[str, Any]]:
    action = str(exit_action or "").upper()
    if realized_return_pct is None:
        return [{"condition": "closed_trade", "action": "review_data", "reason": "Realized outcome was unavailable.", "priority": "low"}]
    if action in {"TAKE_PROFIT", "TAKE_PROFIT_NOW"} and realized_return_pct > 0:
        return [{"condition": "profitable_extension", "action": "keep_scaled_take_profit", "reason": "Partial profit-taking followed the plan.", "priority": "medium"}]
    if action in {"STOP_LOSS", "STOP_LOSS_NOW", "EXIT", "EXIT_NOW"} and realized_return_pct < 0:
        return [{"condition": "loss_control", "action": "respect_invalidations", "reason": "Risk control limited the loss.", "priority": "high"}]
    if realized_return_pct > 0:
        return [{"condition": "positive_close", "action": "catalog_winning_setup", "reason": "The closed trade produced a positive return.", "priority": "medium"}]
    return [{"condition": "negative_close", "action": "tighten_entry_filter", "reason": "The closed trade lost money; review entry timing and risk/reward.", "priority": "medium"}]


def _judgment_evaluation(realized_return_pct: float | None, exit_action: str) -> str:
    action = str(exit_action or "").upper()
    if action in {"TAKE_PROFIT", "TAKE_PROFIT_NOW"} and (realized_return_pct or 0) >= 0:
        return "principle_followed"
    if action in {"STOP_LOSS", "STOP_LOSS_NOW", "EXIT", "EXIT_NOW"}:
        return "risk_control_followed"
    if realized_return_pct is None:
        return "needs_manual_review"
    return "principle_followed" if realized_return_pct >= 0 else "needs_manual_review"


def _pattern_tags(realized_return_pct: float | None, exit_action: str) -> list[str]:
    tags: list[str] = []
    action = str(exit_action or "").upper()
    if action in {"TAKE_PROFIT", "TAKE_PROFIT_NOW"}:
        tags.append("분할익절")
    if action in {"STOP_LOSS", "STOP_LOSS_NOW"}:
        tags.append("손절준수")
    if realized_return_pct is not None and realized_return_pct >= 0:
        tags.append("원칙준수")
    return tags or ["검토필요"]


def _float_or_none(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _int_or_none(value: Any) -> int | None:
    number = _float_or_none(value)
    return None if number is None else int(number)
