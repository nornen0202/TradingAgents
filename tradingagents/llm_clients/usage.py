from __future__ import annotations

import threading
from copy import deepcopy
from typing import Any, Iterable, Mapping


_LOCK = threading.Lock()
_EVENTS: list[dict[str, Any]] = []


def reset_llm_usage() -> None:
    with _LOCK:
        _EVENTS.clear()


def record_llm_usage(
    *, provider: str, model: str, usage: Mapping[str, Any], role: str = "unspecified"
) -> None:
    normalized = _normalize_usage(usage)
    if normalized is None:
        return
    with _LOCK:
        _EVENTS.append(
            {
                "provider": str(provider or "unknown"),
                "model": str(model or "unknown"),
                "role": str(role or "unspecified"),
                **normalized,
            }
        )


def snapshot_llm_usage() -> dict[str, Any]:
    with _LOCK:
        return _summarize_events(tuple(_EVENTS))


def aggregate_llm_usage(snapshots: Iterable[Mapping[str, Any] | None]) -> dict[str, Any]:
    events: list[dict[str, Any]] = []
    calls = 0
    input_tokens = 0
    output_tokens = 0
    by_model: dict[str, dict[str, int]] = {}
    by_role: dict[str, dict[str, int]] = {}

    for snapshot in snapshots:
        if not isinstance(snapshot, Mapping):
            continue
        calls += int(snapshot.get("calls") or 0)
        input_tokens += int(snapshot.get("input_tokens") or 0)
        output_tokens += int(snapshot.get("output_tokens") or 0)
        for model, payload in (snapshot.get("by_model") or {}).items():
            if not isinstance(payload, Mapping):
                continue
            target = by_model.setdefault(
                str(model),
                {"calls": 0, "input_tokens": 0, "output_tokens": 0, "total_tokens": 0},
            )
            target["calls"] += int(payload.get("calls") or 0)
            target["input_tokens"] += int(payload.get("input_tokens") or 0)
            target["output_tokens"] += int(payload.get("output_tokens") or 0)
            target["total_tokens"] += int(payload.get("total_tokens") or 0)
        for role, payload in (snapshot.get("by_role") or {}).items():
            if not isinstance(payload, Mapping):
                continue
            target = by_role.setdefault(
                str(role),
                {"calls": 0, "input_tokens": 0, "output_tokens": 0, "total_tokens": 0},
            )
            target["calls"] += int(payload.get("calls") or 0)
            target["input_tokens"] += int(payload.get("input_tokens") or 0)
            target["output_tokens"] += int(payload.get("output_tokens") or 0)
            target["total_tokens"] += int(payload.get("total_tokens") or 0)
        for event in snapshot.get("events") or ():
            if isinstance(event, Mapping):
                events.append(dict(event))

    total_tokens = input_tokens + output_tokens
    return {
        "available": calls > 0,
        "calls": calls,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens,
        "by_model": by_model,
        "by_role": by_role,
        "events": events,
    }


def _summarize_events(events: tuple[Mapping[str, Any], ...]) -> dict[str, Any]:
    calls = len(events)
    input_tokens = sum(int(event.get("input_tokens") or 0) for event in events)
    output_tokens = sum(int(event.get("output_tokens") or 0) for event in events)
    by_model: dict[str, dict[str, int]] = {}
    by_role: dict[str, dict[str, int]] = {}
    for event in events:
        model = str(event.get("model") or "unknown")
        target = by_model.setdefault(
            model,
            {"calls": 0, "input_tokens": 0, "output_tokens": 0, "total_tokens": 0},
        )
        target["calls"] += 1
        target["input_tokens"] += int(event.get("input_tokens") or 0)
        target["output_tokens"] += int(event.get("output_tokens") or 0)
        target["total_tokens"] += int(event.get("total_tokens") or 0)
        role = str(event.get("role") or "unspecified")
        role_target = by_role.setdefault(
            role,
            {"calls": 0, "input_tokens": 0, "output_tokens": 0, "total_tokens": 0},
        )
        role_target["calls"] += 1
        role_target["input_tokens"] += int(event.get("input_tokens") or 0)
        role_target["output_tokens"] += int(event.get("output_tokens") or 0)
        role_target["total_tokens"] += int(event.get("total_tokens") or 0)

    return {
        "available": calls > 0,
        "calls": calls,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
        "by_model": by_model,
        "by_role": by_role,
        "events": deepcopy(list(events)),
    }


def _normalize_usage(usage: Mapping[str, Any]) -> dict[str, int] | None:
    input_tokens = usage.get("input_tokens") or usage.get("inputTokens")
    output_tokens = usage.get("output_tokens") or usage.get("outputTokens")
    if not isinstance(input_tokens, int) or not isinstance(output_tokens, int):
        return None
    input_tokens = max(0, input_tokens)
    output_tokens = max(0, output_tokens)
    return {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": max(0, int(usage.get("total_tokens") or usage.get("totalTokens") or 0))
        or input_tokens + output_tokens,
    }
