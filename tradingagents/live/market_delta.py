from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from tradingagents.dataflows.intraday_market import (
    DELAYED_ANALYSIS_ONLY,
    REALTIME_EXECUTION_READY,
    STALE_INVALID_FOR_EXECUTION,
)
from tradingagents.schemas import parse_structured_decision


def build_market_delta(
    *,
    run_dir: Path,
    ticker_summary: dict[str, Any],
) -> dict[str, Any] | None:
    execution_update = ticker_summary.get("execution_update")
    if not isinstance(execution_update, dict):
        return None

    contract_payload = _load_contract_payload(run_dir=run_dir, ticker_summary=ticker_summary)
    base_action = _base_action(ticker_summary)
    timing_state = _normalized_timing_state(execution_update.get("execution_timing_state"))
    live_action = _live_action_from_execution(execution_update=execution_update, timing_state=timing_state)

    reason_codes: list[str] = []
    for code in execution_update.get("reason_codes") or []:
        normalized = str(code).strip().upper()
        if normalized and normalized not in reason_codes:
            reason_codes.append(normalized)

    reason_codes.extend(
        _price_and_volume_reason_codes(
            execution_update=execution_update,
            contract_payload=contract_payload,
        )
    )
    reason_codes = _dedupe_strings(reason_codes)

    return {
        "ticker": str(ticker_summary.get("ticker") or ""),
        "base_action": base_action,
        "live_action": live_action,
        "reason_codes": reason_codes,
        "execution_timing_state": timing_state,
        "live_price": execution_update.get("last_price"),
        "day_high": execution_update.get("day_high"),
        "day_low": execution_update.get("day_low"),
        "vwap": execution_update.get("session_vwap"),
        "relative_volume": execution_update.get("relative_volume"),
        "execution_data_quality": _execution_quality(execution_update),
    }


def is_live_action_change(delta: dict[str, Any]) -> bool:
    if not delta:
        return False
    if str(delta.get("base_action") or "").upper() != str(delta.get("live_action") or "").upper():
        return True
    return bool(delta.get("reason_codes"))


def top_add_candidates(deltas: list[dict[str, Any]]) -> list[str]:
    preferred_states = {
        "PILOT_CANDIDATE",
        "PILOT_BLOCKED_VOLUME",
        "CLOSE_CONFIRM_PENDING",
        "CLOSE_CONFIRMED",
        "NEXT_DAY_FOLLOWTHROUGH_PENDING",
    }
    ordered = [
        item["ticker"]
        for item in deltas
        if str(item.get("live_action") or "").upper() in preferred_states
    ]
    return ordered[:5]


def top_trim_candidates(deltas: list[dict[str, Any]]) -> list[str]:
    preferred_states = {"FAILED_BREAKOUT", "SUPPORT_FAIL"}
    ordered = [
        item["ticker"]
        for item in deltas
        if str(item.get("live_action") or "").upper() in preferred_states
    ]
    return ordered[:5]


def _load_contract_payload(*, run_dir: Path, ticker_summary: dict[str, Any]) -> dict[str, Any]:
    artifacts = ticker_summary.get("artifacts") or {}
    rel_path = artifacts.get("execution_contract_json")
    if not rel_path:
        return {}
    path = run_dir / str(rel_path)
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _base_action(ticker_summary: dict[str, Any]) -> str:
    decision = ticker_summary.get("decision")
    try:
        parsed = parse_structured_decision(decision)
    except Exception:
        return "WAIT"
    return str(getattr(parsed, "entry_action", "WAIT") or "WAIT").upper()


def _live_action_from_execution(*, execution_update: dict[str, Any], timing_state: str) -> str:
    quality = _execution_quality(execution_update)
    if quality in {DELAYED_ANALYSIS_ONLY, STALE_INVALID_FOR_EXECUTION}:
        return "STALE_TRIGGERABLE" if timing_state not in {"FAILED_BREAKOUT", "SUPPORT_FAIL"} else timing_state

    mapping = {
        "PILOT_READY": "PILOT_CANDIDATE",
        "PILOT_BLOCKED_VOLUME": "PILOT_BLOCKED_VOLUME",
        "PILOT_BLOCKED_FAILED_BREAKOUT": "FAILED_BREAKOUT",
        "CLOSE_CONFIRM_PENDING": "CLOSE_CONFIRM_PENDING",
        "CLOSE_CONFIRMED": "CLOSE_CONFIRMED",
        "NEXT_DAY_FOLLOWTHROUGH_PENDING": "NEXT_DAY_FOLLOWTHROUGH_PENDING",
        "FAILED_BREAKOUT": "FAILED_BREAKOUT",
        "SUPPORT_HOLD": "SUPPORT_HOLD",
        "SUPPORT_FAIL": "SUPPORT_FAIL",
        "STALE_TRIGGERABLE": "STALE_TRIGGERABLE",
        "NO_LIVE_DATA": "NO_LIVE_DATA",
        "PRE_OPEN_THESIS_ONLY": "PRE_OPEN_THESIS_ONLY",
        "INVALIDATED": "INVALIDATED",
    }
    if timing_state in mapping:
        return mapping[timing_state]

    decision_state = str(execution_update.get("decision_state") or "").upper()
    if decision_state == "ACTIONABLE_NOW":
        return "PILOT_CANDIDATE"
    if decision_state == "TRIGGERED_PENDING_CLOSE":
        return "CLOSE_CONFIRM_PENDING"
    if decision_state == "INVALIDATED":
        return "INVALIDATED"
    if decision_state == "DEGRADED":
        return "STALE_TRIGGERABLE"
    return "WAIT"


def _price_and_volume_reason_codes(
    *,
    execution_update: dict[str, Any],
    contract_payload: dict[str, Any],
) -> list[str]:
    codes: list[str] = []
    last_price = _optional_float(execution_update.get("last_price"))
    breakout_level = _optional_float(contract_payload.get("breakout_level"))
    if last_price is not None and breakout_level is not None:
        if last_price >= breakout_level:
            codes.append("PRICE_ABOVE_TRIGGER")
        else:
            codes.append("PRICE_BELOW_TRIGGER")

    session_vwap = _optional_float(execution_update.get("session_vwap"))
    if last_price is not None and session_vwap is not None:
        codes.append("VWAP_OK" if last_price >= session_vwap else "VWAP_FAIL")

    relative_volume = _optional_float(execution_update.get("relative_volume"))
    min_relative_volume = _optional_float(
        contract_payload.get("min_relative_volume")
        or ((contract_payload.get("execution_levels") or {}).get("min_relative_volume"))
    )
    if relative_volume is not None and min_relative_volume is not None:
        codes.append("VOLUME_OK" if relative_volume >= min_relative_volume else "VOLUME_PENDING")
    elif relative_volume is None and min_relative_volume is not None:
        codes.append("VOLUME_PENDING")

    return codes


def _execution_quality(execution_update: dict[str, Any]) -> str:
    source = execution_update.get("source") if isinstance(execution_update.get("source"), dict) else {}
    return str(
        source.get("execution_data_quality")
        or execution_update.get("execution_data_quality")
        or ""
    ).strip().upper()


def _normalized_timing_state(value: Any) -> str:
    state = str(value or "").strip().upper()
    return {
        "LIVE_BREAKOUT": "PILOT_READY",
        "ACTIONABLE_LIVE": "PILOT_READY",
        "LATE_SESSION_CONFIRM": "CLOSE_CONFIRM_PENDING",
        "CLOSE_CONFIRM": "CLOSE_CONFIRM_PENDING",
    }.get(state, state or "WAITING")


def _optional_float(value: Any) -> float | None:
    try:
        if value in (None, ""):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _dedupe_strings(values: list[str]) -> list[str]:
    seen: list[str] = []
    for value in values:
        normalized = str(value).strip().upper()
        if normalized and normalized not in seen:
            seen.append(normalized)
    return seen
