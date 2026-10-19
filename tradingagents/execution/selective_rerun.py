from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import yfinance as yf

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
    analysis_as_of: datetime,
    news_context: dict[str, str] | None = None,
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
            (news_context.get(ticker, "") if news_context is not None
             else _fetch_fresh_headlines(ticker, analysis_as_of=analysis_as_of)),
        ]
        joined = " ".join(text_fields).lower()
        detected: set[str] = set()
        for keyword, event_type in keyword_map.items():
            if keyword in joined:
                detected.add(event_type)
        if detected:
            signals[ticker] = sorted(detected)
    return signals


def collect_event_news(*, ticker_summaries: list[dict[str, Any]], analysis_as_of: datetime) -> dict[str, str]:
    """Collect once before price acquisition, never on the execution delivery path."""
    return {ticker: _fetch_fresh_headlines(ticker, analysis_as_of=analysis_as_of)
            for ticker in dict.fromkeys(str(row.get("ticker") or "").strip().upper()
                                       for row in ticker_summaries
                                       if row.get("status") == "success" and (row.get("artifacts") or {}).get("analysis_json"))
            if ticker}


def _fetch_fresh_headlines(ticker: str, *, analysis_as_of: datetime) -> str:
    if analysis_as_of.tzinfo is None:
        raise ValueError("Aware analysis_as_of required")
    try:
        news_items = yf.Ticker(ticker).news or []
    except Exception:
        return ""
    headlines: list[str] = []
    for item in news_items[:10]:
        if not isinstance(item, dict):
            continue
        content = item.get("content") if isinstance(item.get("content"), dict) else item
        value = content.get("pubDate", item.get("providerPublishTime"))
        try:
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                published = datetime.fromtimestamp(value, timezone.utc)
            else:
                published = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
            if published.tzinfo is None or not analysis_as_of - timedelta(days=3) <= published <= analysis_as_of:
                continue
        except (ValueError, TypeError, OverflowError, OSError):
            continue
        title = str(content.get("title") or "").strip()
        if title:
            headlines.append(title)
    return " | ".join(headlines)
