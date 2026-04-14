from __future__ import annotations

import json
from typing import Iterable
from typing import Any

from tradingagents.llm_clients.factory import create_llm_client
from tradingagents.schemas import ExecutionContract, ExecutionUpdate


def render_execution_update_markdown(
    contract: ExecutionContract,
    update: ExecutionUpdate,
    *,
    llm_settings: Any | None = None,
    llm_model: str | None = None,
    thesis_summary: str | None = None,
) -> str:
    lines = [
        f"# {update.ticker} Intraday Execution Update",
        "",
        f"- Analysis As-Of: `{contract.analysis_asof}`",
        f"- Market Data As-Of: `{update.market_data_asof}`",
        f"- Execution As-Of: `{update.execution_asof}`",
        f"- Decision State: **{update.decision_state.value}**",
        f"- Decision Now: **{update.decision_now.value}**",
        f"- Decision If Triggered: **{update.decision_if_triggered.value}**",
        f"- Staleness: `{update.staleness_seconds}s`",
        f"- Data Health: `{update.data_health}`",
        "",
        "## Reason Codes",
    ]
    for code in update.reason_codes:
        lines.append(f"- `{code}`")
    llm_summary = _generate_llm_summary(
        contract=contract,
        update=update,
        llm_settings=llm_settings,
        llm_model=llm_model,
        thesis_summary=thesis_summary,
    )
    if llm_summary:
        lines.extend(["", "## Explanation", "", llm_summary.strip()])
    return "\n".join(lines) + "\n"


def render_execution_summary_markdown(*, run_id: str, checkpoint: str, updates: Iterable[ExecutionUpdate]) -> str:
    updates = list(updates)
    actionable = [item.ticker for item in updates if item.decision_state.value == "ACTIONABLE_NOW"]
    pending_close = [item.ticker for item in updates if item.decision_state.value == "TRIGGERED_PENDING_CLOSE"]
    wait = [item.ticker for item in updates if item.decision_state.value == "WAIT"]
    degraded = [item.ticker for item in updates if item.decision_state.value == "DEGRADED"]

    return "\n".join(
        [
            f"# Execution Summary ({run_id})",
            "",
            f"- Refresh checkpoint: `{checkpoint}`",
            f"- Actionable now: {', '.join(actionable) if actionable else '-'}",
            f"- Triggered pending close: {', '.join(pending_close) if pending_close else '-'}",
            f"- Wait: {', '.join(wait) if wait else '-'}",
            f"- Degraded: {', '.join(degraded) if degraded else '-'}",
            "",
        ]
    )


def _generate_llm_summary(
    *,
    contract: ExecutionContract,
    update: ExecutionUpdate,
    llm_settings: Any | None,
    llm_model: str | None,
    thesis_summary: str | None,
) -> str | None:
    model = str(llm_model or "").strip()
    provider = str(getattr(llm_settings, "provider", "") or "").strip().lower()
    if not model or not provider:
        return _deterministic_summary(update)
    try:
        kwargs: dict[str, Any] = {}
        if provider == "codex":
            kwargs = {
                "codex_binary": getattr(llm_settings, "codex_binary", None),
                "codex_reasoning_effort": getattr(llm_settings, "codex_reasoning_effort", "medium"),
                "codex_summary": getattr(llm_settings, "codex_summary", "none"),
                "codex_personality": getattr(llm_settings, "codex_personality", "none"),
                "codex_workspace_dir": getattr(llm_settings, "codex_workspace_dir", None),
                "codex_request_timeout": getattr(llm_settings, "codex_request_timeout", 120.0),
                "codex_max_retries": getattr(llm_settings, "codex_max_retries", 2),
                "codex_cleanup_threads": getattr(llm_settings, "codex_cleanup_threads", True),
            }
        llm = create_llm_client(provider=provider, model=model, **kwargs).get_llm()
        payload = {
            "contract": contract.to_dict(),
            "update": update.to_dict(),
            "thesis_summary": thesis_summary or "",
        }
        prompt = (
            "Summarize this deterministic execution update in 3 concise bullets. "
            "Do not alter any numbers or enum values. "
            "Return plain markdown bullet list only.\n\n"
            + json.dumps(payload, ensure_ascii=False)
        )
        response = llm.invoke(prompt)
        content = getattr(response, "content", response)
        text = str(content or "").strip()
        return text or _deterministic_summary(update)
    except Exception:
        return _deterministic_summary(update)


def _deterministic_summary(update: ExecutionUpdate) -> str:
    reasons = ", ".join(update.reason_codes) if update.reason_codes else "none"
    return (
        f"- State: `{update.decision_state.value}` / Now: `{update.decision_now.value}`.\n"
        f"- Market: price `{update.last_price}`, rVOL `{update.relative_volume}`, staleness `{update.staleness_seconds}s`.\n"
        f"- Reasons: {reasons}."
    )
