"""Strict OHLCV contract. Provider clocks never become publication clocks."""
from __future__ import annotations

from collections import Counter
from datetime import date, datetime
import math
from typing import Any, Iterable, Mapping


def instant(value: Any) -> datetime | None:
    try:
        result = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return result if result.tzinfo is not None and result.utcoffset() is not None else None
    except (ValueError, TypeError):
        return None


def finite(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    try:
        number = float(value)
        return number if math.isfinite(number) else None
    except (ValueError, TypeError, OverflowError):
        return None


def validate_bars(records: Iterable[Mapping[str, Any]], *, analysis_as_of: str | datetime) -> dict:
    """Admit completed, observed bars only; conflicting duplicates remove both."""
    cutoff = instant(analysis_as_of)
    if cutoff is None:
        raise ValueError("analysis_as_of must include a timezone")
    admitted, rejected, conflicts = {}, Counter(), set()
    for row in records:
        if not isinstance(row, Mapping):
            rejected["invalid_record"] += 1
            continue
        times = {key: instant(row.get(key)) for key in ("timestamp", "available_at", "observed_at")}
        if any(value is None for value in times.values()):
            rejected["missing_or_invalid_clock"] += 1
            continue
        if any(value > cutoff for value in times.values()):
            rejected["future_or_unobserved"] += 1
            continue
        if not times["timestamp"] <= times["available_at"] <= times["observed_at"]:
            rejected["invalid_clock_order"] += 1
            continue
        amended_at = instant(row.get("corrected_at")) if row.get("corrected_at") is not None else None
        if row.get("corrected_at") is not None and (amended_at is None or not times["timestamp"] <= amended_at <= times["available_at"]):
            rejected["invalid_correction_clock"] += 1
            continue
        values = {key: finite(row.get(key)) for key in ("open", "high", "low", "close", "volume")}
        if (any(value is None for value in values.values())
                or min(values[key] for key in ("open", "high", "low", "close")) <= 0
                or values["volume"] < 0
                or values["low"] > min(values["open"], values["close"])
                or values["high"] < max(values["open"], values["close"])):
            rejected["invalid_ohlcv"] += 1
            continue
        try:
            session = row.get("session_id")
            valid_session = isinstance(session, str) and len(session) == 10 and date.fromisoformat(session).isoformat() == session
        except ValueError:
            valid_session = False
        interval = row.get("interval")
        if not valid_session or not isinstance(interval, str) or interval not in {"1d", "1m", "5m", "15m", "30m", "60m"}:
            rejected["missing_session_or_interval"] += 1
            continue
        normalized = {**values, **{key: value.isoformat() for key, value in times.items()},
                      "session_id": str(row["session_id"]), "interval": row["interval"],
                      "event_time": times["timestamp"].isoformat(),
                      "ingested_at": times["observed_at"].isoformat(), "evaluated_at": cutoff.isoformat(),
                      "is_amended": row.get("is_amended") is True or amended_at is not None}
        key = (times["timestamp"], row["interval"])
        if key in conflicts:
            rejected["conflicting_duplicate"] += 1
            continue
        previous = admitted.get(key)
        # Reobservation of the identical candle is idempotent, retaining its first clock.
        if previous and any(previous[name] != normalized[name] for name in (*values, "session_id")):
            admitted.pop(key)
            conflicts.add(key)
            rejected["conflicting_duplicate"] += 2
        elif not previous or instant(normalized["observed_at"]) < instant(previous["observed_at"]):
            admitted[key] = normalized
    return {"bars": [admitted[key] for key in sorted(admitted)], "rejected": dict(rejected),
            "analysis_as_of": cutoff.isoformat(), "schema": "tradingagents.chart-bars/v1"}
