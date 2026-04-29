from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Mapping

from .action_outcomes import initialize_action_tracker


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


def store_closed_trade_review(db_path: Path, review: Mapping[str, Any]) -> None:
    initialize_action_tracker(db_path)
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO trade_journal (
              ticker, buy_run_id, sell_run_id, buy_context_json, sell_context_json,
              profit_rate, holding_days, missed_signals_json, overreacted_signals_json,
              lessons_json, pattern_tags_json, one_line_summary, confidence_score, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                review.get("ticker"),
                review.get("entry_run_id"),
                review.get("exit_run_id"),
                json.dumps({"entry_action": review.get("entry_action")}, ensure_ascii=False),
                json.dumps({"exit_action": review.get("exit_action")}, ensure_ascii=False),
                review.get("realized_return_pct"),
                review.get("holding_days"),
                json.dumps(review.get("missed_signals") or [], ensure_ascii=False),
                json.dumps(review.get("overreacted_signals") or [], ensure_ascii=False),
                json.dumps(review.get("lessons") or [], ensure_ascii=False),
                json.dumps(review.get("pattern_tags") or [], ensure_ascii=False),
                review.get("judgment_evaluation"),
                0.60,
                review.get("created_at") or datetime.now().astimezone().isoformat(),
            ),
        )
        for lesson in review.get("lessons") or []:
            if not isinstance(lesson, Mapping):
                continue
            conn.execute(
                """
                INSERT INTO learned_intuitions (
                  category, condition, insight, confidence, supporting_trades,
                  success_rate, source_journal_ids_json, is_active, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    "closed_trade_review",
                    lesson.get("condition") or "closed_trade",
                    lesson.get("reason") or lesson.get("action") or "",
                    0.50,
                    1,
                    None,
                    "[]",
                    1,
                    datetime.now().astimezone().isoformat(),
                ),
            )
        conn.commit()


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
