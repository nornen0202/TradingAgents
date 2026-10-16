from __future__ import annotations

import json
import math
import sqlite3
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from tradingagents.external.prism_normalize import normalize_market

from .models import ACTION_TRACKER_SCHEMA, OUTCOME_CALCULATION_VERSION, ActionPerformanceSummary
from .price_history import BENCHMARK_KEY
from .lifecycle import append_lifecycle_event, initialize_lifecycle, stable_signal_id, timestamp, validate_event


def initialize_action_tracker(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        initialize_lifecycle(conn)
        for statement in ACTION_TRACKER_SCHEMA:
            conn.execute(statement)
        _ensure_columns(conn, "action_recommendations", {
            "market": "TEXT",
            "prism_agreement": "TEXT",
            "skip_reason": "TEXT",
            "sell_intent": "TEXT",
            "sell_trigger_status": "TEXT",
            "sell_size_plan": "TEXT",
            "unrealized_return_pct": "REAL",
            "profit_protection_score": "REAL",
            "profit_plan_json": "TEXT",
            "lift_status": "TEXT",
            "source_cohort": "TEXT",
            "source_quality_score": "REAL",
            "thesis_status": "TEXT",
            "opportunity_cost_score": "REAL",
            "opportunity_capture_score": "REAL",
            "pilot_allowed": "INTEGER",
            "full_size_allowed": "INTEGER",
            "execution_evidence": "TEXT",
        })
        _ensure_columns(conn, "action_outcomes", {
            "return_60d": "REAL",
            "benchmark_return_5d": "REAL",
            "benchmark_excess_5d": "REAL",
            "benchmark_return_20d": "REAL",
            "benchmark_excess_20d": "REAL",
            "benchmark_return_60d": "REAL",
            "benchmark_excess_60d": "REAL",
            "benchmark_key": "TEXT",
            "avoided_drawdown_20d": "REAL",
            "missed_upside_20d": "REAL",
            "calculation_version": "INTEGER DEFAULT 1",
        })
        conn.commit()


def record_run_recommendations(run_dir: Path, db_path: Path, *, run_market: str | None = None, recorded_at: str | None = None) -> int:
    initialize_action_tracker(db_path)
    run_dir = Path(run_dir)
    manifest = _load_json(run_dir / "run.json")
    run_id = str(manifest.get("run_id") or run_dir.name)
    market = _normalize_target_market(run_market) or _manifest_run_market(manifest)
    created_at = str(manifest.get("finished_at") or manifest.get("started_at") or datetime.now().astimezone().isoformat())
    rows = _portfolio_action_rows(run_dir, manifest, run_id=run_id, created_at=created_at, run_market=market)
    rows.extend(_scanner_rows(run_dir, run_id=run_id, created_at=created_at, run_market=market))
    rows.extend(
        _prism_skipped_rows(
            run_dir,
            run_id=run_id,
            created_at=created_at,
            existing_tickers={row["ticker"] for row in rows},
            run_market=market,
        )
    )
    inserted = 0
    ingested_at = recorded_at or datetime.now(timezone.utc).isoformat()
    with sqlite3.connect(db_path) as conn:
        for row in rows:
            if _recommendation_exists(conn, row):
                receipt = row.get("execution_receipt")
                if isinstance(receipt, Mapping):
                    record_execution_receipt(conn, row=row, receipt=receipt, recorded_at=ingested_at)
                continue
            conn.execute(
                """
                INSERT INTO action_recommendations (
                  run_id, ticker, market, action, risk_action, recommended_price, confidence,
                  trigger_type, source, source_cohort, source_quality_score, thesis_status,
                  prism_agreement, sell_intent, sell_trigger_status,
                  sell_size_plan, unrealized_return_pct, profit_protection_score,
                  profit_plan_json, lift_status, opportunity_cost_score, opportunity_capture_score,
                  pilot_allowed, full_size_allowed, was_executed, execution_evidence, skip_reason, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    row["run_id"],
                    row["ticker"],
                    row.get("market") or _ticker_market(row["ticker"], None),
                    row["action"],
                    row.get("risk_action"),
                    row.get("recommended_price"),
                    row.get("confidence"),
                    row.get("trigger_type"),
                    row.get("source"),
                    row.get("source_cohort"),
                    row.get("source_quality_score"),
                    row.get("thesis_status"),
                    row.get("prism_agreement"),
                    row.get("sell_intent"),
                    row.get("sell_trigger_status"),
                    row.get("sell_size_plan"),
                    row.get("unrealized_return_pct"),
                    row.get("profit_protection_score"),
                    row.get("profit_plan_json"),
                    row.get("lift_status"),
                    row.get("opportunity_cost_score"),
                    row.get("opportunity_capture_score"),
                    _bool_to_int(row.get("pilot_allowed")),
                    _bool_to_int(row.get("full_size_allowed")),
                    int(bool(row.get("was_executed"))),
                    row.get("execution_evidence"),
                    row.get("skip_reason"),
                    row["created_at"],
                ),
            )
            inserted += 1
            record_recommendation_evidence(conn, row, ingested_at=ingested_at)
            receipt = row.get("execution_receipt")
            if isinstance(receipt, Mapping):
                record_execution_receipt(conn, row=row, receipt=receipt, recorded_at=ingested_at)
        conn.commit()
    return inserted


def update_action_outcomes(
    db_path: Path,
    asof_date: str,
    horizons: Sequence[int] = (1, 3, 5, 10, 20, 60),
    *,
    price_history: Mapping[str, Any] | None = None,
    price_history_path: str | Path | None = None,
    refresh_window_days: int = 120,
    recommendation_ids: Sequence[int] | None = None,
    recorded_at: str | None = None,
) -> None:
    initialize_action_tracker(db_path)
    # Validate locally even if the upstream adapter claims to apply end_date.
    cutoff = date.fromisoformat(str(asof_date)[:10])
    ingested_at = recorded_at or datetime.now(timezone.utc).isoformat()
    prices = _normalize_price_history(price_history or (_load_json(Path(price_history_path)) if price_history_path else {}), asof_date=str(asof_date))
    benchmark_series = prices.get(BENCHMARK_KEY)
    price_tickers = sorted(key for key in prices if key != BENCHMARK_KEY)
    if not price_tickers:
        return
    selected_ids = tuple(dict.fromkeys(int(item) for item in recommendation_ids or () if int(item) > 0))
    if recommendation_ids is not None and not selected_ids:
        return
    cutoff_date = _outcome_refresh_cutoff_date(asof_date, refresh_window_days)
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        placeholders = ",".join("?" for _ in price_tickers)
        if recommendation_ids is not None:
            id_placeholders = ",".join("?" for _ in selected_ids)
            recommendations = list(
                conn.execute(
                    f"""
                    SELECT *
                    FROM action_recommendations
                    WHERE id IN ({id_placeholders})
                      AND upper(ticker) IN ({placeholders})
                    """,
                    (*selected_ids, *price_tickers),
                )
            )
        elif cutoff_date:
            recommendations = list(
                conn.execute(
                    f"""
                    SELECT DISTINCT r.*
                    FROM action_recommendations r
                    LEFT JOIN action_outcomes o ON o.recommendation_id = r.id
                    WHERE substr(r.created_at, 1, 10) >= ?
                      AND upper(r.ticker) IN ({placeholders})
                      AND (
                        o.recommendation_id IS NULL
                        OR COALESCE(o.calculation_version, 1) < ?
                        OR (
                          o.return_60d IS NULL
                          AND substr(COALESCE(o.updated_at, ''), 1, 10) < ?
                        )
                      )
                    """,
                    (
                        cutoff_date,
                        *price_tickers,
                        OUTCOME_CALCULATION_VERSION,
                        str(asof_date)[:10],
                    ),
                )
            )
        else:
            recommendations = list(
                conn.execute(
                    f"SELECT * FROM action_recommendations WHERE upper(ticker) IN ({placeholders})",
                    price_tickers,
                )
            )
        for row in recommendations:
            try:
                decision_time = timestamp(row["created_at"])
                decision_cutoff = timestamp(str(asof_date) if "T" in str(asof_date) else cutoff.isoformat() + "T23:59:59.999999+00:00")
                if decision_time > decision_cutoff:
                    continue
            except ValueError:
                # Legacy date-only rows retain date-granularity metrics but are
                # deliberately excluded from the evidence replay below.
                try:
                    if date.fromisoformat(str(row["created_at"])) > cutoff:
                        continue
                except ValueError:
                    continue
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
                  return_20d, return_60d, benchmark_return_5d, benchmark_excess_5d,
                  benchmark_return_20d, benchmark_excess_20d, benchmark_return_60d,
                  benchmark_excess_60d, benchmark_key,
                  max_drawdown_20d, max_favorable_excursion_20d, avoided_drawdown_20d,
                  missed_upside_20d, outcome_label, calculation_version, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                    returns.get("benchmark_excess_5d"),
                    returns.get("benchmark_return_20d"),
                    returns.get("benchmark_excess_20d"),
                    returns.get("benchmark_return_60d"),
                    returns.get("benchmark_excess_60d"),
                    returns.get("benchmark_key"),
                    returns.get("max_drawdown_20d"),
                    returns.get("max_favorable_excursion_20d"),
                    returns.get("avoided_drawdown_20d"),
                    returns.get("missed_upside_20d"),
                    returns.get("outcome_label"),
                    OUTCOME_CALCULATION_VERSION,
                    asof_date,
                ),
            )
            try:
                decision_at = timestamp(row["created_at"]).isoformat()
            except ValueError:
                continue
            known_at = str(asof_date) if "T" in str(asof_date) else cutoff.isoformat() + "T23:59:59.999999+00:00"
            if timestamp(known_at) < timestamp(decision_at):
                continue
            signal_id = stable_signal_id(row["run_id"], row["ticker"], row["action"], row["source"] or "TradingAgents")
            append_lifecycle_event(conn, event_id=f"outcome:{signal_id}:{known_at}:v{OUTCOME_CALCULATION_VERSION}", signal_id=signal_id,
                kind="OUTCOME", occurred_at=decision_at, available_at=known_at, confirmed_at=known_at,
                ingested_at=ingested_at,
                payload={"ticker": row["ticker"], "measurement_scope": "counterfactual_recommendation_price_path", **returns})
        conn.commit()


def _outcome_refresh_cutoff_date(asof_date: str, refresh_window_days: int) -> str | None:
    text = str(asof_date or "").strip()[:10]
    if not text:
        return None
    try:
        parsed = date.fromisoformat(text)
    except ValueError:
        return None
    return (parsed - timedelta(days=max(1, int(refresh_window_days or 1)))).isoformat()


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
        source_cohorts = _aggregate(conn, "source_cohort")
        action_buckets = _aggregate_action_buckets(conn)
        profit_taking = _aggregate_profit_taking(conn)
        calibration = _aggregate_calibration(conn)
        data_quality = _performance_data_quality(conn, closed_trades=closed_trades)
    return ActionPerformanceSummary(
        recommendations=recommendations,
        outcomes=outcomes,
        closed_trades=closed_trades,
        learned_intuitions=learned,
        by_action=by_action,
        prism_agreement=by_prism,
        source_cohorts=source_cohorts,
        action_buckets=action_buckets,
        profit_taking=profit_taking,
        calibration=calibration,
        data_quality=data_quality,
    )


def _portfolio_action_rows(
    run_dir: Path,
    manifest: dict[str, Any],
    *,
    run_id: str,
    created_at: str,
    run_market: str | None = None,
) -> list[dict[str, Any]]:
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
        ticker_market = _ticker_market(ticker, None)
        if not _market_matches(ticker_market, run_market):
            continue
        preferred_action = _preferred_action(action)
        position_metrics = action.get("position_metrics") if isinstance(action.get("position_metrics"), Mapping) else {}
        profit_plan = action.get("profit_taking_plan") if isinstance(action.get("profit_taking_plan"), Mapping) else {}
        data_health = action.get("data_health") if isinstance(action.get("data_health"), Mapping) else {}
        lift = data_health.get("action_lift") if isinstance(data_health.get("action_lift"), Mapping) else {}
        execution_evidence = _execution_evidence(action)
        has_proposed_allocation = bool(int(action.get("delta_krw_now") or 0))
        rows.append(
            {
                "run_id": run_id,
                "ticker": ticker,
                "market": ticker_market,
                "action": preferred_action,
                "risk_action": action.get("risk_action"),
                "recommended_price": _recommended_price(action),
                "confidence": action.get("confidence"),
                "trigger_type": action.get("trigger_type"),
                "source": "TradingAgents",
                "source_cohort": data_health.get("source_cohort"),
                "source_quality_score": _float_or_none(data_health.get("source_quality_score")),
                "thesis_status": data_health.get("thesis_status"),
                "prism_agreement": action.get("prism_agreement") or (action.get("data_health") or {}).get("prism_agreement"),
                "sell_intent": action.get("sell_intent"),
                "sell_trigger_status": action.get("sell_trigger_status"),
                "sell_size_plan": action.get("sell_size_plan"),
                "unrealized_return_pct": _float_or_none(position_metrics.get("unrealized_return_pct")),
                "profit_protection_score": _float_or_none(position_metrics.get("profit_protection_score")),
                "profit_plan_json": json.dumps(profit_plan, ensure_ascii=False) if profit_plan else None,
                "lift_status": lift.get("lift_status") or data_health.get("lift_status"),
                "opportunity_cost_score": _float_or_none(lift.get("opportunity_cost_score") or data_health.get("opportunity_cost_score")),
                "opportunity_capture_score": _float_or_none(lift.get("opportunity_capture_score") or data_health.get("opportunity_capture_score")),
                "pilot_allowed": lift.get("pilot_allowed") if lift else data_health.get("pilot_allowed"),
                "full_size_allowed": lift.get("full_size_allowed") if lift else data_health.get("full_size_allowed"),
                "was_executed": execution_evidence == "broker_fill",
                "execution_evidence": execution_evidence,
                "execution_receipt": action.get("execution_receipt"),
                "skip_reason": (
                    None
                    if execution_evidence == "broker_fill"
                    else (
                        "proposed_allocation_without_execution_receipt"
                        if has_proposed_allocation
                        else _skip_reason(action)
                    )
                ),
                "created_at": created_at,
            }
        )
    return rows


def _scanner_rows(run_dir: Path, *, run_id: str, created_at: str, run_market: str | None = None) -> list[dict[str, Any]]:
    path = run_dir / "scanner" / "scanner_candidates.json"
    payload = _load_json(path)
    rows: list[dict[str, Any]] = []
    for item in payload.get("candidates") or []:
        if not isinstance(item, dict):
            continue
        ticker = str(item.get("ticker") or "").strip().upper()
        if not ticker:
            continue
        ticker_market = _ticker_market(ticker, item.get("market"))
        if not _market_matches(ticker_market, run_market):
            continue
        rows.append(
            {
                "run_id": run_id,
                "ticker": ticker,
                "market": ticker_market,
                "action": "scanner_candidate_skipped",
                "risk_action": None,
                "recommended_price": None,
                "confidence": item.get("final_score"),
                "trigger_type": item.get("trigger_type"),
                "source": "scanner",
                "prism_agreement": None,
                "was_executed": False,
                "execution_evidence": None,
                "skip_reason": "scanner_discovery_only",
                "created_at": created_at,
            }
        )
    return rows


def _prism_skipped_rows(
    run_dir: Path,
    *,
    run_id: str,
    created_at: str,
    existing_tickers: set[str],
    run_market: str | None = None,
) -> list[dict[str, Any]]:
    payload = _load_json(run_dir / "external_signals" / "prism_signals.json")
    rows: list[dict[str, Any]] = []
    for signal in payload.get("signals") or []:
        if not isinstance(signal, dict):
            continue
        ticker = str(signal.get("canonical_ticker") or "").strip().upper()
        if not ticker or ticker in existing_tickers:
            continue
        ticker_market = _ticker_market(ticker, signal.get("market"))
        if not _market_matches(ticker_market, run_market):
            continue
        rows.append(
            {
                "run_id": run_id,
                "ticker": ticker,
                "market": ticker_market,
                "action": "prism_candidate_skipped",
                "risk_action": signal.get("signal_action"),
                "recommended_price": signal.get("current_price"),
                "confidence": signal.get("confidence"),
                "trigger_type": signal.get("trigger_type"),
                "source": "PRISM",
                "prism_agreement": "external_only",
                "was_executed": False,
                "execution_evidence": None,
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
    if start_index is None:
        return {}
    base_price = _float_or_none(row["recommended_price"]) or series[start_index][1]
    if base_price <= 0:
        return {}
    values: dict[str, Any] = {}
    for horizon in horizons:
        target_index = start_index + int(horizon)
        if target_index >= len(series):
            values[f"return_{int(horizon)}d"] = None
            continue
        ret = (series[target_index][1] - base_price) / base_price
        values[f"return_{int(horizon)}d"] = round(ret, 6)
    window_end = start_index + 20
    window = [price for _date, price in series[start_index : window_end + 1]] if window_end < len(series) else []
    if window:
        values["max_drawdown_20d"] = round((min(window) - base_price) / base_price, 6)
        values["max_favorable_excursion_20d"] = round((max(window) - base_price) / base_price, 6)
        values["avoided_drawdown_20d"] = round(max(0.0, -float(values["max_drawdown_20d"])), 6)
        values["missed_upside_20d"] = round(max(0.0, float(values["max_favorable_excursion_20d"])), 6)
    return_5d = values.get("return_5d")
    values["benchmark_key"] = BENCHMARK_KEY if benchmark_series else None
    for horizon in (5, 20, 60):
        benchmark_return = _benchmark_return(benchmark_series, created_date=created_date, horizon=horizon)
        values[f"benchmark_return_{horizon}d"] = benchmark_return
        action_return = values.get(f"return_{horizon}d")
        if action_return is not None and benchmark_return is not None:
            values[f"benchmark_excess_{horizon}d"] = round(float(action_return) - float(benchmark_return), 6)
    values["outcome_label"] = _outcome_label(str(row["action"]), return_5d)
    return values


def _start_index_for_date(series: list[tuple[str, float]], created_date: str) -> int | None:
    if not series or not created_date or created_date > series[-1][0]:
        return None
    for index, (date_text, _price) in enumerate(series):
        if date_text >= created_date:
            return index
    return None


def _benchmark_return(series: list[tuple[str, float]] | None, *, created_date: str, horizon: int) -> float | None:
    if not series:
        return None
    start_index = _start_index_for_date(series, created_date)
    if start_index is None:
        return None
    base = series[start_index][1]
    if base <= 0:
        return None
    target_index = start_index + int(horizon)
    if target_index >= len(series):
        return None
    return round((series[target_index][1] - base) / base, 6)


def _normalize_price_history(payload: Mapping[str, Any], *, asof_date: str | None = None) -> dict[str, list[tuple[str, float]]]:
    result: dict[str, list[tuple[str, float]]] = {}
    if not isinstance(payload, Mapping):
        return result
    cutoff = (timestamp(asof_date) if asof_date and "T" in asof_date else
              timestamp(asof_date + "T23:59:59.999999+00:00") if asof_date else None)
    for ticker, raw_series in payload.items():
        series: list[tuple[str, float]] = []
        values = raw_series.get("prices") if isinstance(raw_series, Mapping) else raw_series
        if not isinstance(values, list):
            continue
        for item in values:
            if isinstance(item, Mapping):
                raw_date = str(item.get("date") or item.get("asof") or item.get("timestamp") or "")
                price = _float_or_none(item.get("close") or item.get("price") or item.get("last"))
            elif isinstance(item, (list, tuple)) and len(item) >= 2:
                raw_date = str(item[0])
                price = _float_or_none(item[1])
            else:
                continue
            date_text = raw_date[:10]
            try:
                date.fromisoformat(date_text)
                bar_available = timestamp(raw_date if "T" in raw_date else raw_date + "T23:59:59.999999+00:00")
            except ValueError:
                continue
            if cutoff and bar_available > cutoff:
                continue
            if isinstance(item, Mapping):
                unavailable = False
                for clock in ("available_at", "observed_at", "confirmed_at", "settled_at"):
                    if clock in item:
                        try:
                            if cutoff and timestamp(item[clock]) > cutoff:
                                unavailable = True
                        except ValueError:
                            unavailable = True
                if unavailable:
                    continue
            if date_text and price is not None and math.isfinite(price) and price > 0:
                series.append((date_text, price))
        if series:
            # A duplicate trading date cannot represent multiple future bars.
            grouped: dict[str, set[float]] = {}
            for day, value in series:
                grouped.setdefault(day, set()).add(value)
            result[str(ticker).upper()] = sorted((day, next(iter(values))) for day, values in grouped.items() if len(values) == 1)
    return result


def _aggregate(conn: sqlite3.Connection, column: str) -> dict[str, dict[str, Any]]:
    rows = conn.execute(
        f"""
        SELECT r.{column} AS bucket, COUNT(*) AS n,
               COUNT(o.return_5d) AS outcome_count_5d,
               COUNT(o.return_20d) AS outcome_count_20d,
               AVG(o.return_5d) AS avg_return_5d,
               AVG(o.return_20d) AS avg_return_20d,
               AVG(o.benchmark_excess_20d) AS avg_benchmark_excess_20d
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
            "outcome_count_5d": int(row["outcome_count_5d"] or 0),
            "outcome_count_20d": int(row["outcome_count_20d"] or 0),
            "avg_return_5d": row["avg_return_5d"],
            "avg_return_20d": row["avg_return_20d"],
            "avg_benchmark_excess_20d": row["avg_benchmark_excess_20d"],
        }
    return result


def _aggregate_action_buckets(conn: sqlite3.Connection) -> dict[str, dict[str, Any]]:
    rows = conn.execute(
        """
        SELECT r.source AS source, r.prism_agreement AS prism_agreement,
               COUNT(*) AS n,
               COUNT(o.return_5d) AS outcome_count_5d,
               COUNT(o.return_20d) AS outcome_count_20d,
               AVG(o.return_5d) AS avg_return_5d,
               AVG(o.return_20d) AS avg_return_20d,
               AVG(o.benchmark_excess_20d) AS avg_benchmark_excess_20d
        FROM action_recommendations r
        LEFT JOIN action_outcomes o ON o.recommendation_id = r.id
        GROUP BY r.source, r.prism_agreement
        """
    )
    result: dict[str, dict[str, Any]] = {}
    for row in rows:
        bucket = _action_bucket(str(row["source"] or ""), str(row["prism_agreement"] or ""))
        current = result.setdefault(
            bucket,
            {
                "count": 0,
                "avg_return_5d": None,
                "avg_return_20d": None,
                "avg_benchmark_excess_20d": None,
                "outcome_count_5d": 0,
                "outcome_count_20d": 0,
                "_sum_5d": 0.0,
                "_n_5d": 0,
                "_sum_20d": 0.0,
                "_n_20d": 0,
                "_sum_excess_20d": 0.0,
                "_n_excess_20d": 0,
            },
        )
        count = int(row["n"] or 0)
        current["count"] += count
        count_5d = int(row["outcome_count_5d"] or 0)
        count_20d = int(row["outcome_count_20d"] or 0)
        current["outcome_count_5d"] += count_5d
        current["outcome_count_20d"] += count_20d
        if row["avg_return_5d"] is not None:
            current["_sum_5d"] += float(row["avg_return_5d"]) * count_5d
            current["_n_5d"] += count_5d
        if row["avg_return_20d"] is not None:
            current["_sum_20d"] += float(row["avg_return_20d"]) * count_20d
            current["_n_20d"] += count_20d
        if row["avg_benchmark_excess_20d"] is not None:
            current["_sum_excess_20d"] += float(row["avg_benchmark_excess_20d"]) * count_20d
            current["_n_excess_20d"] += count_20d
    for metrics in result.values():
        if metrics["_n_5d"]:
            metrics["avg_return_5d"] = metrics["_sum_5d"] / metrics["_n_5d"]
        if metrics["_n_20d"]:
            metrics["avg_return_20d"] = metrics["_sum_20d"] / metrics["_n_20d"]
        if metrics["_n_excess_20d"]:
            metrics["avg_benchmark_excess_20d"] = metrics["_sum_excess_20d"] / metrics["_n_excess_20d"]
        for key in ("_sum_5d", "_n_5d", "_sum_20d", "_n_20d", "_sum_excess_20d", "_n_excess_20d"):
            metrics.pop(key, None)
    return result


def _aggregate_profit_taking(conn: sqlite3.Connection) -> dict[str, dict[str, Any]]:
    rows = conn.execute(
        """
        SELECT COALESCE(NULLIF(r.action, ''), 'TAKE_PROFIT') AS bucket,
               COUNT(*) AS n,
               COUNT(o.return_5d) AS outcome_count_5d,
               COUNT(o.return_20d) AS outcome_count_20d,
               AVG(o.return_5d) AS avg_return_5d,
               AVG(o.return_20d) AS avg_return_20d,
               AVG(o.avoided_drawdown_20d) AS avg_avoided_drawdown_20d,
               AVG(o.missed_upside_20d) AS avg_missed_upside_20d
        FROM action_recommendations r
        LEFT JOIN action_outcomes o ON o.recommendation_id = r.id
        WHERE UPPER(COALESCE(r.sell_intent, '')) = 'TAKE_PROFIT'
           OR UPPER(COALESCE(r.action, '')) IN ('TAKE_PROFIT', 'TAKE_PROFIT_NOW', 'TAKE_PROFIT_IF_TRIGGERED')
           OR UPPER(COALESCE(r.risk_action, '')) = 'TAKE_PROFIT'
        GROUP BY COALESCE(NULLIF(r.action, ''), 'TAKE_PROFIT')
        """
    )
    result: dict[str, dict[str, Any]] = {}
    for row in rows:
        bucket = str(row["bucket"] or "TAKE_PROFIT")
        result[bucket] = {
            "count": int(row["n"] or 0),
            "outcome_count_5d": int(row["outcome_count_5d"] or 0),
            "outcome_count_20d": int(row["outcome_count_20d"] or 0),
            "avg_return_5d": row["avg_return_5d"],
            "avg_return_20d": row["avg_return_20d"],
            "avg_avoided_drawdown_20d": row["avg_avoided_drawdown_20d"],
            "avg_missed_upside_20d": row["avg_missed_upside_20d"],
        }
    return result


def _aggregate_calibration(conn: sqlite3.Connection) -> dict[str, Any]:
    row = conn.execute(
        """
        WITH portfolio_lift_rows AS (
          SELECT *
          FROM action_recommendations
          WHERE source = 'TradingAgents'
            AND lift_status IS NOT NULL
            AND UPPER(COALESCE(action, '')) NOT IN ('SCANNER_CANDIDATE_SKIPPED', 'PRISM_CANDIDATE_SKIPPED')
        )
        SELECT
          COUNT(*) AS total,
          SUM(CASE WHEN UPPER(COALESCE(lift_status, '')) IN (
            'ACTION_LIFT_FAILURE', 'BUDGET_BLOCKED', 'PILOT_VISIBLE_NO_ORDER',
            'BUY_SIGNAL_RELABELED_AS_SELL_SIDE', 'PRISM_SOFT_BLOCK_PILOT_ALLOWED'
          ) THEN 1 ELSE 0 END) AS actionable_not_ordered,
          AVG(CASE WHEN UPPER(COALESCE(lift_status, '')) IN (
            'ACTION_LIFT_FAILURE', 'BUDGET_BLOCKED', 'PILOT_VISIBLE_NO_ORDER',
            'BUY_SIGNAL_RELABELED_AS_SELL_SIDE', 'PRISM_SOFT_BLOCK_PILOT_ALLOWED'
          ) THEN o.return_5d ELSE NULL END) AS missed_upside_5d,
          AVG(CASE WHEN UPPER(COALESCE(lift_status, '')) IN (
            'ACTION_LIFT_FAILURE', 'BUDGET_BLOCKED', 'PILOT_VISIBLE_NO_ORDER',
            'BUY_SIGNAL_RELABELED_AS_SELL_SIDE', 'PRISM_SOFT_BLOCK_PILOT_ALLOWED'
          ) THEN o.missed_upside_20d ELSE NULL END) AS missed_upside_20d,
          AVG(CASE WHEN COALESCE(prism_agreement, '') LIKE 'conflict_%'
            THEN CASE WHEN o.return_5d > 0 THEN 1.0 ELSE 0.0 END ELSE NULL END) AS prism_conflict_winner_rate
        FROM portfolio_lift_rows r
        LEFT JOIN action_outcomes o ON o.recommendation_id = r.id
        """
    ).fetchone()
    skipped = conn.execute(
        """
        SELECT
          SUM(CASE WHEN UPPER(COALESCE(action, '')) = 'SCANNER_CANDIDATE_SKIPPED'
                    OR LOWER(COALESCE(source, '')) = 'scanner'
              THEN 1 ELSE 0 END) AS scanner_skipped,
          SUM(CASE WHEN UPPER(COALESCE(action, '')) = 'PRISM_CANDIDATE_SKIPPED'
                    OR COALESCE(source, '') = 'PRISM'
              THEN 1 ELSE 0 END) AS prism_skipped
        FROM action_recommendations
        """
    ).fetchone()
    total = int(row["total"] or 0) if row else 0
    actionable_not_ordered = int(row["actionable_not_ordered"] or 0) if row else 0
    return {
        "action_lift_denominator_count": total,
        "actionable_not_ordered_count": actionable_not_ordered,
        "actionable_not_ordered_rate": (actionable_not_ordered / total if total else 0.0),
        "missed_upside_5d": row["missed_upside_5d"] if row else None,
        "missed_upside_20d": row["missed_upside_20d"] if row else None,
        "prism_conflict_winner_rate": row["prism_conflict_winner_rate"] if row else None,
        "scanner_candidate_skipped_count": int(skipped["scanner_skipped"] or 0) if skipped else 0,
        "prism_candidate_skipped_count": int(skipped["prism_skipped"] or 0) if skipped else 0,
    }


def _performance_data_quality(
    conn: sqlite3.Connection,
    *,
    closed_trades: int,
) -> dict[str, Any]:
    row = conn.execute(
        """
        SELECT
          COUNT(*) AS recommendation_rows,
          COUNT(DISTINCT run_id) AS distinct_runs,
          COUNT(DISTINCT ticker) AS distinct_tickers,
          SUM(CASE WHEN market IS NULL OR TRIM(market) = '' THEN 1 ELSE 0 END) AS missing_market_rows,
          SUM(CASE WHEN source = 'TradingAgents' THEN 1 ELSE 0 END) AS portfolio_recommendation_rows,
          SUM(CASE WHEN LOWER(COALESCE(source, '')) IN ('scanner', 'prism') THEN 1 ELSE 0 END) AS advisory_rows,
          SUM(CASE WHEN execution_evidence = 'broker_fill' THEN 1 ELSE 0 END) AS broker_fill_linked_rows,
          SUM(CASE WHEN COALESCE(was_executed, 0) = 1
                    AND COALESCE(execution_evidence, '') = '' THEN 1 ELSE 0 END) AS legacy_unverified_execution_rows,
          COUNT(o.return_5d) AS matured_5d_rows,
          COUNT(o.return_20d) AS matured_20d_rows,
          COUNT(o.return_60d) AS matured_60d_rows
        FROM action_recommendations r
        LEFT JOIN action_outcomes o ON o.recommendation_id = r.id
        """
    ).fetchone()
    market_rows = {
        str(item["market"] or "UNKNOWN"): int(item["n"] or 0)
        for item in conn.execute(
            """
            SELECT COALESCE(NULLIF(TRIM(market), ''), 'UNKNOWN') AS market, COUNT(*) AS n
            FROM action_recommendations
            GROUP BY COALESCE(NULLIF(TRIM(market), ''), 'UNKNOWN')
            """
        )
    }
    recommendations = int(row["recommendation_rows"] or 0) if row else 0
    matured_5d = int(row["matured_5d_rows"] or 0) if row else 0
    legacy_fill_claims = int(row["broker_fill_linked_rows"] or 0) if row else 0
    # An old receipt label or a paper journal row cannot prove actual trading
    # effectiveness. Require the immutable, confirmed and settled evidence chain.
    now = datetime.now(timezone.utc)
    actual_fills, paper_fills, actual_reviews = {}, {}, []
    for stored in conn.execute("SELECT * FROM lifecycle_events WHERE kind IN ('FILL','RETROSPECTIVE')"):
        event = dict(stored)
        try:
            event["payload"] = json.loads(event.pop("payload_json"))
            validate_event(event)
            if any(timestamp(event[key]) > now for key in ("occurred_at", "available_at", "confirmed_at", "settled_at", "ingested_at") if event.get(key)):
                continue
        except (ValueError, TypeError, KeyError):
            continue
        if event["kind"] == "FILL":
            if event["mode"] == "actual":
                actual_fills[event["event_id"]] = event
            elif event["mode"] == "paper":
                paper_fills[event["event_id"]] = event
        elif event["mode"] == "actual":
            actual_reviews.append(event["payload"])
    broker_fills = len({event["signal_id"] for event in actual_fills.values()})
    actual_closed = sum(review.get("entry_fill_id") in actual_fills and review.get("exit_fill_id") in actual_fills for review in actual_reviews)
    legacy_unverified = int(row["legacy_unverified_execution_rows"] or 0) if row else 0
    actual_feedback_available = broker_fills > 0 and actual_closed > 0
    warnings = []
    if not actual_feedback_available:
        warnings.append("actual_trade_effectiveness_unavailable:no_linked_broker_fills_or_closed_trades")
    if legacy_unverified:
        warnings.append(
            f"legacy_proposed_allocations_not_execution_receipts:{legacy_unverified}"
        )
    missing_market = int(row["missing_market_rows"] or 0) if row else 0
    if missing_market:
        warnings.append(f"recommendation_market_unclassified:{missing_market}")
    return {
        "measurement_scope": "counterfactual_recommendation_price_path",
        "actual_trade_effectiveness_available": actual_feedback_available,
        "feedback_loop_status": "ACTUAL_TRADE_LINKED" if actual_feedback_available else "COUNTERFACTUAL_ONLY",
        "recommendation_rows": recommendations,
        "distinct_runs": int(row["distinct_runs"] or 0) if row else 0,
        "distinct_tickers": int(row["distinct_tickers"] or 0) if row else 0,
        "portfolio_recommendation_rows": int(row["portfolio_recommendation_rows"] or 0) if row else 0,
        "advisory_rows": int(row["advisory_rows"] or 0) if row else 0,
        "market_rows": market_rows,
        "missing_market_rows": missing_market,
        "matured_5d_rows": matured_5d,
        "matured_20d_rows": int(row["matured_20d_rows"] or 0) if row else 0,
        "matured_60d_rows": int(row["matured_60d_rows"] or 0) if row else 0,
        "matured_5d_coverage": matured_5d / recommendations if recommendations else 0.0,
        "broker_fill_linked_rows": broker_fills,
        "legacy_broker_fill_claim_rows": legacy_fill_claims,
        "settled_actual_fill_events": len(actual_fills),
        "paper_fill_events": len(paper_fills),
        "actual_closed_trade_reviews": actual_closed,
        "closed_trade_journal_rows": int(closed_trades or 0),
        "legacy_unverified_execution_rows": legacy_unverified,
        "warnings": warnings,
    }


def _action_bucket(source: str, prism_agreement: str) -> str:
    source_text = source.strip().lower()
    agreement = prism_agreement.strip().lower()
    if source_text == "scanner":
        return "Scanner-discovered"
    if agreement in {"confirmed_buy", "confirmed_sell"}:
        return "PRISM-confirmed"
    if agreement.startswith("conflict_"):
        return "PRISM-conflicted"
    if agreement == "no_same_market_prism_coverage":
        return "PRISM-uncovered-current-market"
    return "TradingAgents-only"


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


def record_recommendation_evidence(conn: sqlite3.Connection, row: Mapping[str, Any], *, ingested_at: str) -> None:
    try:
        if timestamp(row.get("created_at")) > timestamp(ingested_at):
            return
    except ValueError:
        return  # Legacy date-only rows are not invented point-in-time evidence.
    signal_id = stable_signal_id(row["run_id"], row["ticker"], row["action"], row.get("source") or "TradingAgents")
    payload = {key: row.get(key) for key in ("run_id", "ticker", "action", "risk_action", "source",
                "recommended_price", "confidence", "skip_reason", "trigger_type")}
    payload["source"] = row.get("source") or "TradingAgents"
    append_lifecycle_event(conn, event_id=signal_id, signal_id=signal_id, kind="SIGNAL",
        occurred_at=row["created_at"], available_at=row["created_at"], ingested_at=ingested_at, payload=payload)


def record_execution_receipt(db: Path | sqlite3.Connection, *, row: Mapping[str, Any], receipt: Mapping[str, Any], recorded_at: str | None = None, strict: bool = False) -> bool:
    """Import explicit, settled broker evidence; never infer fills from allocation.

    One receipt represents one incremental fill, not cumulative order quantity.
    Unknown costs, fill IDs or timing make it ineligible for historical replay.
    Existing recommendation statistics remain backward compatible.
    """
    if _execution_evidence({"execution_receipt": receipt}) != "broker_fill":
        if strict:
            raise ValueError("Explicit supported broker fill status/source/quantity required")
        return False
    ingested_at = recorded_at or datetime.now(timezone.utc).isoformat()
    try:
        executed_at = receipt["executed_at"]
        intent_at = receipt["intent_at"]
        confirmed_at, settled_at = receipt["confirmed_at"], receipt["settled_at"]
        available_at = receipt.get("available_at") or confirmed_at
        for value in (executed_at, confirmed_at, settled_at, available_at, intent_at):
            timestamp(value)
        if timestamp(intent_at) > timestamp(executed_at):
            if strict:
                raise ValueError("Fill cannot precede intent")
            return False
        intent_id, fill_id = receipt["intent_id"], receipt["fill_id"]
        if any(not isinstance(value, str) or not value.strip() or len(value) > 200 for value in (intent_id, fill_id)):
            if strict:
                raise ValueError("Stable intent and incremental fill IDs required")
            return False
        quantity, requested = receipt["filled_quantity"], receipt["requested_quantity"]
        price, cost, side = receipt["fill_price"], receipt["cost"], receipt["side"]
        if (not isinstance(requested, (int, float)) or isinstance(requested, bool)
                or not math.isfinite(requested) or requested < quantity):
            if strict:
                raise ValueError("Requested quantity must cover incremental fill")
            return False
        signal_id = stable_signal_id(row["run_id"], row["ticker"], row["action"], row.get("source") or "TradingAgents")
        payload = {"ticker": row["ticker"], "side": side, "quantity": quantity,
                   "price": price, "cost": cost, "currency": receipt["currency"],
                   "reference_price": row.get("recommended_price"), "broker_fill_id": fill_id}
        # Validate before writing the intent so malformed fills cannot leave an
        # apparent order link without usable execution evidence.
        validate_event(dict(event_id="fill:actual:" + fill_id, signal_id=signal_id, intent_id=intent_id,
            kind="FILL", mode="actual", occurred_at=executed_at, available_at=available_at,
            confirmed_at=confirmed_at, settled_at=settled_at, ingested_at=ingested_at, payload=payload))
    except (KeyError, ValueError, TypeError):
        if strict:
            raise ValueError("Receipt is missing required fields or contains invalid execution evidence") from None
        return False
    if not isinstance(db, sqlite3.Connection):
        with sqlite3.connect(db) as conn:
            return record_execution_receipt(conn, row=row, receipt=receipt, recorded_at=ingested_at, strict=strict)
    append_lifecycle_event(db, event_id="intent:actual:" + intent_id, signal_id=signal_id,
        intent_id=intent_id, kind="INTENT", mode="actual", occurred_at=intent_at,
        available_at=receipt.get("intent_available_at") or intent_at, ingested_at=ingested_at, payload={"ticker": row["ticker"], "side": side,
            "quantity": requested, "status": "OBSERVED_BROKER_INTENT"})
    inserted = append_lifecycle_event(db, event_id="fill:actual:" + fill_id, signal_id=signal_id,
        intent_id=intent_id, kind="FILL", mode="actual", occurred_at=executed_at,
        available_at=available_at, confirmed_at=confirmed_at, settled_at=settled_at, ingested_at=ingested_at, payload=payload)
    from .journal import record_fill_retrospectives
    # Reimports also reconcile now-settled exits and out-of-order file imports.
    exits = db.execute("SELECT event_id,payload_json FROM lifecycle_events WHERE kind='FILL' AND mode='actual'").fetchall()
    for exit_id, encoded in exits:
        candidate = json.loads(encoded)
        if candidate.get("side") == "SELL" and candidate.get("ticker") == row["ticker"]:
            record_fill_retrospectives(db, exit_event_id=exit_id, evaluated_at=ingested_at)
    return inserted


def _manifest_run_market(manifest: Mapping[str, Any]) -> str | None:
    settings = manifest.get("settings") if isinstance(manifest.get("settings"), Mapping) else {}
    return _normalize_target_market(settings.get("market"))


def _normalize_target_market(value: Any) -> str | None:
    normalized = normalize_market(value)
    return normalized if normalized in {"KR", "US"} else None


def _ticker_market(ticker: Any, explicit_market: Any) -> str:
    return normalize_market(explicit_market, ticker=str(ticker or "").strip().upper())


def _market_matches(ticker_market: str, run_market: str | None) -> bool:
    target = _normalize_target_market(run_market)
    if not target:
        return True
    return _normalize_target_market(ticker_market) == target


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
    metrics = action.get("position_metrics") if isinstance(action.get("position_metrics"), Mapping) else {}
    for key in ("current_price", "market_price_krw"):
        number = _float_or_none(metrics.get(key))
        if number is not None and number > 0:
            return number
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


def _execution_evidence(action: Mapping[str, Any]) -> str | None:
    """Return broker-fill evidence only when the action carries a verified execution receipt."""

    receipt = action.get("execution_receipt")
    if not isinstance(receipt, Mapping):
        return None
    status = str(receipt.get("status") or "").strip().upper()
    source = str(receipt.get("source") or "").strip().lower()
    filled_quantity = _float_or_none(receipt.get("filled_quantity"))
    if status not in {"FILLED", "PARTIALLY_FILLED"}:
        return None
    if source not in {"broker", "kis", "broker_api"}:
        return None
    if filled_quantity is None or filled_quantity <= 0:
        return None
    return "broker_fill"


def _outcome_label(action: str, return_5d: float | None) -> str:
    if return_5d is None:
        return "pending"
    buy_like = action in {"ADD_NOW", "ADD_IF_TRIGGERED", "STARTER_NOW", "STARTER_IF_TRIGGERED"}
    profit_like = action in {"TAKE_PROFIT", "TAKE_PROFIT_NOW", "TAKE_PROFIT_IF_TRIGGERED"}
    risk_like = action in {"STOP_LOSS", "STOP_LOSS_NOW", "REDUCE_RISK", "REDUCE_NOW", "EXIT", "EXIT_NOW"}
    if buy_like:
        return "positive_followthrough" if return_5d > 0 else "failed_followthrough"
    if profit_like:
        if return_5d < 0:
            return "avoided_loss"
        if return_5d > 0:
            return "missed_upside"
        return "profit_protected_flat"
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


def _bool_to_int(value: Any) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return 1 if value else 0
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "on"}:
        return 1
    if text in {"0", "false", "no", "off"}:
        return 0
    return None


def _count_optional_table(conn: sqlite3.Connection, table: str) -> int:
    exists = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
        (table,),
    ).fetchone()
    if not exists:
        return 0
    return int(conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])
