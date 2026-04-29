from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from .models import ACTION_TRACKER_SCHEMA, ActionPerformanceSummary
from .price_history import BENCHMARK_KEY


def initialize_action_tracker(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        for statement in ACTION_TRACKER_SCHEMA:
            conn.execute(statement)
        _ensure_columns(conn, "action_recommendations", {
            "prism_agreement": "TEXT",
            "skip_reason": "TEXT",
        })
        _ensure_columns(conn, "action_outcomes", {
            "return_60d": "REAL",
            "benchmark_return_5d": "REAL",
        })
        conn.commit()


def record_run_recommendations(run_dir: Path, db_path: Path) -> None:
    initialize_action_tracker(db_path)
    run_dir = Path(run_dir)
    manifest = _load_json(run_dir / "run.json")
    run_id = str(manifest.get("run_id") or run_dir.name)
    created_at = str(manifest.get("finished_at") or manifest.get("started_at") or datetime.now().astimezone().isoformat())
    rows = _portfolio_action_rows(run_dir, manifest, run_id=run_id, created_at=created_at)
    rows.extend(_scanner_rows(run_dir, run_id=run_id, created_at=created_at))
    rows.extend(_prism_skipped_rows(run_dir, run_id=run_id, created_at=created_at, existing_tickers={row["ticker"] for row in rows}))
    with sqlite3.connect(db_path) as conn:
        for row in rows:
            if _recommendation_exists(conn, row):
                continue
            conn.execute(
                """
                INSERT INTO action_recommendations (
                  run_id, ticker, action, risk_action, recommended_price, confidence,
                  trigger_type, source, prism_agreement, was_executed, skip_reason, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row["run_id"],
                    row["ticker"],
                    row["action"],
                    row.get("risk_action"),
                    row.get("recommended_price"),
                    row.get("confidence"),
                    row.get("trigger_type"),
                    row.get("source"),
                    row.get("prism_agreement"),
                    int(bool(row.get("was_executed"))),
                    row.get("skip_reason"),
                    row["created_at"],
                ),
            )
        conn.commit()


def update_action_outcomes(
    db_path: Path,
    asof_date: str,
    horizons: Sequence[int] = (1, 3, 5, 10, 20, 60),
    *,
    price_history: Mapping[str, Any] | None = None,
    price_history_path: str | Path | None = None,
) -> None:
    initialize_action_tracker(db_path)
    prices = _normalize_price_history(price_history or (_load_json(Path(price_history_path)) if price_history_path else {}))
    benchmark_series = prices.get(BENCHMARK_KEY)
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        recommendations = list(conn.execute("SELECT * FROM action_recommendations"))
        for row in recommendations:
            ticker = str(row["ticker"])
            series = prices.get(ticker)
            if not series:
                continue
            returns = _compute_returns(row, series, horizons=horizons, benchmark_series=benchmark_series)
            if not returns:
                continue
            conn.execute("DELETE FROM action_outcomes WHERE recommendation_id = ?", (row["id"],))
            conn.execute(
                """
                INSERT INTO action_outcomes (
                  recommendation_id, return_1d, return_3d, return_5d, return_10d,
                  return_20d, return_60d, benchmark_return_5d, max_drawdown_20d,
                  max_favorable_excursion_20d, outcome_label, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row["id"],
                    returns.get("return_1d"),
                    returns.get("return_3d"),
                    returns.get("return_5d"),
                    returns.get("return_10d"),
                    returns.get("return_20d"),
                    returns.get("return_60d"),
                    returns.get("benchmark_return_5d"),
                    returns.get("max_drawdown_20d"),
                    returns.get("max_favorable_excursion_20d"),
                    returns.get("outcome_label"),
                    asof_date,
                ),
            )
        conn.commit()


def summarize_action_performance(db_path: Path) -> ActionPerformanceSummary:
    initialize_action_tracker(db_path)
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        recommendations = int(conn.execute("SELECT COUNT(*) FROM action_recommendations").fetchone()[0])
        outcomes = int(conn.execute("SELECT COUNT(*) FROM action_outcomes").fetchone()[0])
        closed_trades = int(_count_optional_table(conn, "trade_journal"))
        learned = int(_count_optional_table(conn, "learned_intuitions"))
        by_action = _aggregate(conn, "action")
        by_prism = _aggregate(conn, "prism_agreement")
    return ActionPerformanceSummary(
        recommendations=recommendations,
        outcomes=outcomes,
        closed_trades=closed_trades,
        learned_intuitions=learned,
        by_action=by_action,
        prism_agreement=by_prism,
    )


def _portfolio_action_rows(run_dir: Path, manifest: dict[str, Any], *, run_id: str, created_at: str) -> list[dict[str, Any]]:
    report_path = _resolve_artifact(run_dir, ((manifest.get("portfolio") or {}).get("artifacts") or {}).get("portfolio_report_json"))
    if report_path is None:
        candidate = run_dir / "portfolio-private" / "portfolio_report.json"
        report_path = candidate if candidate.exists() else None
    if report_path is None:
        return []
    payload = _load_json(report_path)
    rows: list[dict[str, Any]] = []
    for action in payload.get("actions") or []:
        if not isinstance(action, dict):
            continue
        ticker = str(action.get("canonical_ticker") or "").strip().upper()
        if not ticker:
            continue
        preferred_action = _preferred_action(action)
        rows.append(
            {
                "run_id": run_id,
                "ticker": ticker,
                "action": preferred_action,
                "risk_action": action.get("risk_action"),
                "recommended_price": _recommended_price(action),
                "confidence": action.get("confidence"),
                "trigger_type": action.get("trigger_type"),
                "source": "TradingAgents",
                "prism_agreement": action.get("prism_agreement") or (action.get("data_health") or {}).get("prism_agreement"),
                "was_executed": bool(int(action.get("delta_krw_now") or 0)),
                "skip_reason": None if int(action.get("delta_krw_now") or 0) else _skip_reason(action),
                "created_at": created_at,
            }
        )
    return rows


def _scanner_rows(run_dir: Path, *, run_id: str, created_at: str) -> list[dict[str, Any]]:
    path = run_dir / "scanner" / "scanner_candidates.json"
    payload = _load_json(path)
    rows: list[dict[str, Any]] = []
    for item in payload.get("candidates") or []:
        if not isinstance(item, dict):
            continue
        ticker = str(item.get("ticker") or "").strip().upper()
        if not ticker:
            continue
        rows.append(
            {
                "run_id": run_id,
                "ticker": ticker,
                "action": "scanner_candidate_skipped",
                "risk_action": None,
                "recommended_price": None,
                "confidence": item.get("final_score"),
                "trigger_type": item.get("trigger_type"),
                "source": "scanner",
                "prism_agreement": None,
                "was_executed": False,
                "skip_reason": "scanner_discovery_only",
                "created_at": created_at,
            }
        )
    return rows


def _prism_skipped_rows(run_dir: Path, *, run_id: str, created_at: str, existing_tickers: set[str]) -> list[dict[str, Any]]:
    payload = _load_json(run_dir / "external_signals" / "prism_signals.json")
    rows: list[dict[str, Any]] = []
    for signal in payload.get("signals") or []:
        if not isinstance(signal, dict):
            continue
        ticker = str(signal.get("canonical_ticker") or "").strip().upper()
        if not ticker or ticker in existing_tickers:
            continue
        rows.append(
            {
                "run_id": run_id,
                "ticker": ticker,
                "action": "prism_candidate_skipped",
                "risk_action": signal.get("signal_action"),
                "recommended_price": signal.get("current_price"),
                "confidence": signal.get("confidence"),
                "trigger_type": signal.get("trigger_type"),
                "source": "PRISM",
                "prism_agreement": "external_only",
                "was_executed": False,
                "skip_reason": "external_advisory_only",
                "created_at": created_at,
            }
        )
    return rows


def _compute_returns(
    row: sqlite3.Row,
    series: list[tuple[str, float]],
    *,
    horizons: Sequence[int],
    benchmark_series: list[tuple[str, float]] | None = None,
) -> dict[str, Any]:
    created_date = str(row["created_at"] or "")[:10]
    start_index = _start_index_for_date(series, created_date)
    base_price = _float_or_none(row["recommended_price"]) or series[start_index][1]
    if base_price <= 0:
        return {}
    values: dict[str, Any] = {}
    for horizon in horizons:
        target_index = min(start_index + int(horizon), len(series) - 1)
        ret = (series[target_index][1] - base_price) / base_price
        values[f"return_{int(horizon)}d"] = round(ret, 6)
    window = [price for _date, price in series[start_index : min(start_index + 21, len(series))]]
    if window:
        values["max_drawdown_20d"] = round((min(window) - base_price) / base_price, 6)
        values["max_favorable_excursion_20d"] = round((max(window) - base_price) / base_price, 6)
    return_5d = values.get("return_5d")
    values["benchmark_return_5d"] = _benchmark_return_5d(benchmark_series, created_date=created_date)
    values["outcome_label"] = _outcome_label(str(row["action"]), return_5d)
    return values


def _start_index_for_date(series: list[tuple[str, float]], created_date: str) -> int:
    for index, (date_text, _price) in enumerate(series):
        if date_text >= created_date:
            return index
    return max(len(series) - 1, 0)


def _benchmark_return_5d(series: list[tuple[str, float]] | None, *, created_date: str) -> float | None:
    if not series:
        return None
    start_index = _start_index_for_date(series, created_date)
    base = series[start_index][1]
    if base <= 0:
        return None
    target_index = min(start_index + 5, len(series) - 1)
    return round((series[target_index][1] - base) / base, 6)


def _normalize_price_history(payload: Mapping[str, Any]) -> dict[str, list[tuple[str, float]]]:
    result: dict[str, list[tuple[str, float]]] = {}
    if not isinstance(payload, Mapping):
        return result
    for ticker, raw_series in payload.items():
        series: list[tuple[str, float]] = []
        values = raw_series.get("prices") if isinstance(raw_series, Mapping) else raw_series
        if not isinstance(values, list):
            continue
        for item in values:
            if isinstance(item, Mapping):
                date_text = str(item.get("date") or item.get("asof") or item.get("timestamp") or "")[:10]
                price = _float_or_none(item.get("close") or item.get("price") or item.get("last"))
            elif isinstance(item, (list, tuple)) and len(item) >= 2:
                date_text = str(item[0])[:10]
                price = _float_or_none(item[1])
            else:
                continue
            if date_text and price is not None:
                series.append((date_text, price))
        if series:
            result[str(ticker).upper()] = sorted(series, key=lambda row: row[0])
    return result


def _aggregate(conn: sqlite3.Connection, column: str) -> dict[str, dict[str, Any]]:
    rows = conn.execute(
        f"""
        SELECT r.{column} AS bucket, COUNT(*) AS n, AVG(o.return_5d) AS avg_return_5d,
               AVG(o.return_20d) AS avg_return_20d
        FROM action_recommendations r
        LEFT JOIN action_outcomes o ON o.recommendation_id = r.id
        GROUP BY r.{column}
        """
    )
    result: dict[str, dict[str, Any]] = {}
    for row in rows:
        bucket = str(row["bucket"] or "UNKNOWN")
        result[bucket] = {
            "count": int(row["n"] or 0),
            "avg_return_5d": row["avg_return_5d"],
            "avg_return_20d": row["avg_return_20d"],
        }
    return result


def _ensure_columns(conn: sqlite3.Connection, table: str, columns: dict[str, str]) -> None:
    existing = {str(row[1]) for row in conn.execute(f"PRAGMA table_info({table})")}
    for name, sql_type in columns.items():
        if name not in existing:
            conn.execute(f"ALTER TABLE {table} ADD COLUMN {name} {sql_type}")


def _recommendation_exists(conn: sqlite3.Connection, row: dict[str, Any]) -> bool:
    existing = conn.execute(
        """
        SELECT 1 FROM action_recommendations
        WHERE run_id = ? AND ticker = ? AND action = ? AND source = ?
        LIMIT 1
        """,
        (row["run_id"], row["ticker"], row["action"], row.get("source")),
    ).fetchone()
    return existing is not None


def _preferred_action(action: Mapping[str, Any]) -> str:
    now = str(action.get("action_now") or "").upper()
    triggered = str(action.get("action_if_triggered") or "").upper()
    relative = str(action.get("portfolio_relative_action") or "").upper()
    if now and now not in {"HOLD", "WATCH", "NONE"}:
        return now
    if triggered and triggered != "NONE":
        return triggered
    return relative or now or "UNKNOWN"


def _recommended_price(action: Mapping[str, Any]) -> float | None:
    data = action.get("data_health") if isinstance(action.get("data_health"), Mapping) else {}
    for key in ("current_price", "last_price", "estimated_market_price_krw"):
        value = data.get(key)
        number = _float_or_none(value)
        if number is not None and number > 0:
            return number
    return None


def _skip_reason(action: Mapping[str, Any]) -> str | None:
    if action.get("budget_blocked_actionable"):
        return "budget_or_cash_buffer_blocked"
    gate_reasons = action.get("gate_reasons") or []
    if gate_reasons:
        return ",".join(str(item) for item in gate_reasons)
    return "not_executed"


def _outcome_label(action: str, return_5d: float | None) -> str:
    if return_5d is None:
        return "pending"
    buy_like = action in {"ADD_NOW", "ADD_IF_TRIGGERED", "STARTER_NOW", "STARTER_IF_TRIGGERED"}
    risk_like = action in {"STOP_LOSS", "STOP_LOSS_NOW", "REDUCE_RISK", "REDUCE_NOW", "EXIT", "EXIT_NOW"}
    if buy_like:
        return "positive_followthrough" if return_5d > 0 else "failed_followthrough"
    if risk_like:
        return "avoided_loss" if return_5d < 0 else "missed_upside"
    return "neutral_positive" if return_5d >= 0 else "neutral_negative"


def _resolve_artifact(run_dir: Path, path_value: Any) -> Path | None:
    if not path_value:
        return None
    path = Path(str(path_value))
    if not path.is_absolute():
        path = run_dir / path
    return path if path.exists() else None


def _load_json(path: Path) -> dict[str, Any]:
    try:
        if path and Path(path).exists():
            payload = json.loads(Path(path).read_text(encoding="utf-8"))
            return payload if isinstance(payload, dict) else {}
    except Exception:
        return {}
    return {}


def _float_or_none(value: Any) -> float | None:
    if value in (None, "") or isinstance(value, bool):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _count_optional_table(conn: sqlite3.Connection, table: str) -> int:
    exists = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
        (table,),
    ).fetchone()
    if not exists:
        return 0
    return int(conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])
