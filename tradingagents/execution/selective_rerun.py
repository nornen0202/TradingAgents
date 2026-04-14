from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from tradingagents.schemas import ExecutionContract, ExecutionUpdate


def find_selective_rerun_targets(
    *,
    contracts: dict[str, ExecutionContract],
    updates: dict[str, ExecutionUpdate],
    event_signals: dict[str, list[str]] | None = None,
) -> dict[str, list[str]]:
    targets: dict[str, list[str]] = {}
    event_signals = event_signals or {}

    for ticker, update in updates.items():
        reasons: list[str] = []
        if update.decision_state.value == "INVALIDATED":
            reasons.append("overlay_invalidated")
        for event_type in event_signals.get(ticker, []):
            reasons.append(f"event:{event_type}")
        contract = contracts.get(ticker)
        event_guard = getattr(contract, "event_guard", None) if contract is not None else None
        requires_post_event_rerun = False
        if isinstance(event_guard, dict):
            requires_post_event_rerun = bool(event_guard.get("requires_post_event_rerun", False))
        elif event_guard is not None:
            requires_post_event_rerun = bool(getattr(event_guard, "requires_post_event_rerun", False))
        if requires_post_event_rerun:
            if event_signals.get(ticker):
                reasons.append("post_event_guard_rerun")
        if reasons:
            targets[ticker] = sorted(set(reasons))
    return targets


def collect_event_signals(
    *,
    run_dir: Path,
    ticker_summaries: list[dict[str, Any]],
) -> dict[str, list[str]]:
    keyword_map = {
        "earnings": "earnings",
        "guidance": "guidance",
        "acquisition": "mna",
        "merger": "mna",
        "regulatory": "regulatory",
        "lawsuit": "litigation",
        "litigation": "litigation",
        "ceo": "management_change",
    }
    signals: dict[str, list[str]] = {}
    for summary in ticker_summaries:
        if summary.get("status") != "success":
            continue
        ticker = str(summary.get("ticker") or "").strip().upper()
        artifacts = summary.get("artifacts") or {}
        analysis_rel = artifacts.get("analysis_json")
        if not ticker or not analysis_rel:
            continue
        analysis_path = run_dir / str(analysis_rel)
        if not analysis_path.exists():
            continue
        try:
            payload = json.loads(analysis_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        text_fields = [
            str(payload.get("decision") or ""),
            json.dumps((payload.get("tool_telemetry") or {}).get("events") or [], ensure_ascii=False),
        ]
        joined = " ".join(text_fields).lower()
        detected: set[str] = set()
        for keyword, event_type in keyword_map.items():
            if keyword in joined:
                detected.add(event_type)
        if detected:
            signals[ticker] = sorted(detected)
    return signals
