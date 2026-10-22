from __future__ import annotations

import json
import hashlib
import sqlite3
from datetime import datetime, timezone
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


def record_fill_retrospectives(conn: sqlite3.Connection, *, exit_event_id: str,
                               evaluated_at: str | None = None, clock=None) -> list[int]:
    """Atomically publish one complete FIFO allocation for a known SELL.

    Older allocations and their lessons remain immutable historical evidence.
    An empty allocation explicitly withdraws an earlier known-cost allocation.
    ``evaluated_at`` limits input evidence; it never backdates publication.
    Publication uses the current UTC clock by default. Offline fixtures and
    producers with an explicit execution clock must inject that clock themselves.
    Historical queries use select_retrospectives, not this writer.
    """
    publication = clock() if clock is not None else datetime.now(timezone.utc)
    publication = timestamp(publication.isoformat() if isinstance(publication, datetime) else publication)
    cutoff = timestamp(evaluated_at) if evaluated_at is not None else publication
    if cutoff > publication:
        raise ValueError("Evaluation cutoff cannot follow publication time")
    conn.execute("SAVEPOINT fifo_allocation")
    try:
        result = _record_fill_allocation(conn, exit_event_id, cutoff, publication)
        conn.execute("RELEASE SAVEPOINT fifo_allocation")
        return result
    except Exception:
        conn.execute("ROLLBACK TO SAVEPOINT fifo_allocation")
        conn.execute("RELEASE SAVEPOINT fifo_allocation")
        raise


def _record_fill_allocation(conn, exit_event_id, cutoff, publication):
    from .outcome_revisions import (ALGORITHM, REVISION_KIND, allocation_hash, content_hash,
                                    event_order, known_at, read_events, revision_heads,
                                    validate_opening_seeds, visible_events)
    all_events = read_events(conn)
    target = next((event for event in all_events if event["event_id"] == exit_event_id), None)
    if not target or target["kind"] != "FILL" or target["payload"].get("side") != "SELL":
        return []
    visible = visible_events(all_events, cutoff.isoformat())
    validate_opening_seeds(visible)
    _, heads = revision_heads(all_events, publication.isoformat())
    target = visible.get(exit_event_id)
    if target is None:
        return []
    symbol, currency = target["payload"]["ticker"], target["payload"]["currency"]
    key = target["mode"], currency, symbol, exit_event_id
    head = heads.get(key)
    if head and timestamp(head["payload"]["input_as_of"]) > cutoff:
        raise ValueError("Cannot publish a backdated FIFO allocation")
    # Historical reads never rewrite the allocation chain. A writer cannot
    # append a fork behind an already published revision, even with old clocks.
    for event in all_events:
        if (event["kind"] == REVISION_KIND and event["mode"] == key[0]
                and event["payload"].get("exit_fill_id") == exit_event_id and known_at(event) > publication):
            raise ValueError("Cannot publish a backdated FIFO allocation")
    lots, reviews, inputs = [], [], []
    for event in sorted(visible.values(), key=event_order):
        if event["kind"] not in {"ACCOUNT_SEED", "FILL"} or event["mode"] != target["mode"]:
            continue
        payload = event["payload"]
        if payload.get("currency", "KRW") != currency:
            continue
        if event["kind"] == "ACCOUNT_SEED":
            quantity = (payload.get("positions") or {}).get(symbol, 0)
            if quantity:
                lots.append({"remaining": quantity, "event": None})
                inputs.append(event)
            continue
        if payload.get("ticker") != symbol:
            continue
        inputs.append(event)
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
                review.update(entry_fill_id=entry["event_id"], exit_fill_id=exit_event_id,
                    signal_id=event["signal_id"], entry_signal_id=entry["signal_id"],
                    closed_quantity=closed, net_profit=profit, total_cost=costs, currency=currency, mode=event["mode"],
                    measurement_scope="realized_fill_return_after_costs", created_at=publication.isoformat(),
                    ingested_at=publication.isoformat(), closed_at=event["occurred_at"],
                    entry_context=buy, exit_context=payload)
                review["judgment_evaluation"] = "profitable_fill" if profit >= 0 else "unprofitable_fill"
                reviews.append(review)
            lot["remaining"] -= closed
            remaining -= closed
            if lot["remaining"] <= 1e-9:
                lots.pop(0)
        if event["event_id"] == exit_event_id:
            break
    input_ids = sorted(event["event_id"] for event in inputs)
    digest = allocation_hash(reviews, input_ids)
    if head and head["payload"]["content_hash"] == digest:
        rows = [conn.execute("SELECT id FROM trade_journal WHERE review_id=?", (identity,)).fetchone()
                for identity in head["payload"]["review_ids"]]
        if any(row is None for row in rows):
            raise ValueError("Committed FIFO allocation is missing its journal reviews")
        return [row[0] for row in rows]
    previous = head["event_id"] if head else None
    revision_id = "allocation:" + content_hash({"scope": key, "previous": previous, "content": digest})
    confirmed = max(timestamp(event["confirmed_at"]) for event in inputs if event.get("confirmed_at"))
    settled = max(timestamp(event["settled_at"]) for event in inputs if event.get("settled_at"))
    ids, review_ids = [], []
    for review in reviews:
        review_id = "review:" + content_hash({"revision": revision_id, "entry": review["entry_fill_id"]})
        review.update(review_id=review_id, allocation_revision_id=revision_id,
                      confirmed_at=confirmed.isoformat(), settled_at=settled.isoformat())
        ids.append(store_closed_trade_review(conn, review))
        review_ids.append(review_id)
    append_lifecycle_event(conn, event_id=revision_id, signal_id=target["signal_id"],
        kind=REVISION_KIND, mode=target["mode"], occurred_at=target["occurred_at"],
        available_at=publication.isoformat(), ingested_at=publication.isoformat(),
        confirmed_at=confirmed.isoformat(), settled_at=settled.isoformat(),
        payload={"schema": "tradingagents.fifo-allocation/v1", "algorithm": ALGORITHM,
                 "ticker": symbol, "currency": currency, "exit_fill_id": exit_event_id,
                 "input_as_of": cutoff.isoformat(),
                 "previous_revision_id": previous, "content_hash": digest,
                 "input_event_ids": input_ids, "review_ids": review_ids})
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
