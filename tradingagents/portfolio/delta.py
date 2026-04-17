from __future__ import annotations

from typing import Any


def compute_portfolio_delta(
    *,
    previous_manifest: dict[str, Any] | None,
    current_manifest: dict[str, Any],
) -> dict[str, Any]:
    current_run_id = str(current_manifest.get("run_id") or "")
    if not previous_manifest:
        return {
            "from_run": None,
            "to_run": current_run_id,
            "priority_changes": [],
            "state_changes": [],
            "relative_action_changes": [],
            "newly_actionable": [],
            "newly_invalidated": [],
            "newly_degraded": [],
            "summary": "이전 비교 대상 run이 없어 delta를 계산하지 않았습니다.",
        }

    previous_run_id = str(previous_manifest.get("run_id") or "")
    prev_rank = _priority_by_ticker(previous_manifest)
    curr_rank = _priority_by_ticker(current_manifest)
    priority_changes: list[dict[str, Any]] = []
    for ticker in sorted(set(prev_rank) & set(curr_rank)):
        if prev_rank[ticker] == curr_rank[ticker]:
            continue
        priority_changes.append({"ticker": ticker, "from": prev_rank[ticker], "to": curr_rank[ticker]})

    prev_state = _state_by_ticker(previous_manifest)
    curr_state = _state_by_ticker(current_manifest)
    state_changes: list[dict[str, Any]] = []
    for ticker in sorted(set(prev_state) & set(curr_state)):
        if prev_state[ticker] == curr_state[ticker]:
            continue
        state_changes.append({"ticker": ticker, "from": prev_state[ticker], "to": curr_state[ticker]})

    prev_relative_action = _relative_action_by_ticker(previous_manifest)
    curr_relative_action = _relative_action_by_ticker(current_manifest)
    relative_action_changes: list[dict[str, Any]] = []
    for ticker in sorted(set(prev_relative_action) & set(curr_relative_action)):
        if prev_relative_action[ticker] == curr_relative_action[ticker]:
            continue
        relative_action_changes.append({"ticker": ticker, "from": prev_relative_action[ticker], "to": curr_relative_action[ticker]})

    newly_actionable = sorted(ticker for ticker, state in curr_state.items() if state == "ACTIONABLE_NOW" and prev_state.get(ticker) != "ACTIONABLE_NOW")
    newly_invalidated = sorted(ticker for ticker, state in curr_state.items() if state == "INVALIDATED" and prev_state.get(ticker) != "INVALIDATED")
    newly_degraded = sorted(ticker for ticker, state in curr_state.items() if state == "DEGRADED" and prev_state.get(ticker) != "DEGRADED")

    return {
        "from_run": previous_run_id or None,
        "to_run": current_run_id,
        "priority_changes": priority_changes,
        "state_changes": state_changes,
        "relative_action_changes": relative_action_changes,
        "newly_actionable": newly_actionable,
        "newly_invalidated": newly_invalidated,
        "newly_degraded": newly_degraded,
        "summary": _summary_line(priority_changes, newly_actionable, newly_invalidated, newly_degraded, relative_action_changes),
    }


def render_portfolio_delta_markdown(delta: dict[str, Any]) -> str:
    lines = [
        "# Portfolio run delta",
        "",
        f"- from_run: `{delta.get('from_run') or '-'}`",
        f"- to_run: `{delta.get('to_run') or '-'}`",
        f"- summary: {delta.get('summary') or '-'}",
        "",
        "## priority_changes",
    ]
    priority_changes = delta.get("priority_changes") or []
    if priority_changes:
        for item in priority_changes:
            lines.append(f"- {item.get('ticker')}: {item.get('from')} -> {item.get('to')}")
    else:
        lines.append("- none")

    lines.extend([
        "",
        "## state_changes",
    ])
    state_changes = delta.get("state_changes") or []
    if state_changes:
        for item in state_changes:
            lines.append(f"- {item.get('ticker')}: {item.get('from')} -> {item.get('to')}")
    else:
        lines.append("- none")

    lines.extend([
        "",
        "## relative_action_changes",
    ])
    relative_action_changes = delta.get("relative_action_changes") or []
    if relative_action_changes:
        for item in relative_action_changes:
            lines.append(f"- {item.get('ticker')}: {item.get('from')} -> {item.get('to')}")
    else:
        lines.append("- none")

    for key in ("newly_actionable", "newly_invalidated", "newly_degraded"):
        values = ", ".join(delta.get(key) or []) or "none"
        lines.extend(["", f"## {key}", f"- {values}"])
    lines.append("")
    return "\n".join(lines)


def _priority_by_ticker(manifest: dict[str, Any]) -> dict[str, int]:
    execution = manifest.get("execution") or {}
    explicit = execution.get("top_priority_order") or []
    explicit_rank = {
        str(ticker).strip().upper(): index
        for index, ticker in enumerate(explicit, start=1)
        if str(ticker).strip()
    }
    if explicit_rank:
        return explicit_rank

    ranking = sorted(
        (item for item in (manifest.get("tickers") or []) if str(item.get("ticker") or "").strip()),
        key=lambda item: _priority_key(item),
    )
    return {str(item.get("ticker") or "").strip().upper(): idx for idx, item in enumerate(ranking, start=1)}


def _priority_key(ticker_summary: dict[str, Any]) -> tuple[int, str]:
    payload = ticker_summary.get("execution_update") or {}
    state = str(payload.get("decision_state") or "WAIT").upper()
    order = {
        "ACTIONABLE_NOW": 0,
        "TRIGGERED_PENDING_CLOSE": 1,
        "WAIT": 2,
        "DEGRADED": 3,
        "INVALIDATED": 4,
    }
    return (order.get(state, 5), str(ticker_summary.get("ticker") or ""))


def _state_by_ticker(manifest: dict[str, Any]) -> dict[str, str]:
    states: dict[str, str] = {}
    for ticker_summary in manifest.get("tickers") or []:
        ticker = str(ticker_summary.get("ticker") or "").strip().upper()
        if not ticker:
            continue
        payload = ticker_summary.get("execution_update") or {}
        states[ticker] = str(payload.get("decision_state") or "WAIT").upper()
    return states


def _relative_action_by_ticker(manifest: dict[str, Any]) -> dict[str, str]:
    portfolio = manifest.get("portfolio") if isinstance(manifest.get("portfolio"), dict) else {}
    action_summary = portfolio.get("action_summary") if isinstance(portfolio.get("action_summary"), dict) else {}
    relative_actions = action_summary.get("relative_actions") if isinstance(action_summary.get("relative_actions"), dict) else {}
    normalized = {
        str(ticker).strip().upper(): str(action).strip().upper()
        for ticker, action in relative_actions.items()
        if str(ticker).strip()
    }
    if normalized:
        return normalized
    values: dict[str, str] = {}
    for ticker_summary in manifest.get("tickers") or []:
        ticker = str(ticker_summary.get("ticker") or "").strip().upper()
        action = str(ticker_summary.get("portfolio_relative_action") or "").strip().upper()
        if ticker and action:
            values[ticker] = action
    return values


def _summary_line(
    priority_changes: list[dict[str, Any]],
    newly_actionable: list[str],
    newly_invalidated: list[str],
    newly_degraded: list[str],
    relative_action_changes: list[dict[str, Any]] | None = None,
) -> str:
    parts: list[str] = []
    if priority_changes:
        top = sorted(priority_changes, key=lambda item: int(item.get("to") or 999))[0]
        parts.append(f"{top.get('ticker')} 우선순위 변동")
    if newly_actionable:
        parts.append(f"신규 즉시 실행 {', '.join(newly_actionable[:2])}")
    if newly_invalidated:
        parts.append(f"무효화 {', '.join(newly_invalidated[:2])}")
    if newly_degraded:
        parts.append(f"자료 저하 {', '.join(newly_degraded[:2])}")
    if relative_action_changes:
        top = relative_action_changes[0]
        parts.append(f"{top.get('ticker')} 계좌 액션 {top.get('from')}->{top.get('to')}")
    return "; ".join(parts) if parts else "직전 run 대비 핵심 변화 없음"
