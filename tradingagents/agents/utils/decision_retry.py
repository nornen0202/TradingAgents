from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from typing import Any

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage

from tradingagents.schemas import StructuredDecisionValidationError, ensure_structured_decision_json

_CODEX_FALLBACK_MARKER = "TRADINGAGENTS_CODEX_FALLBACK_RESPONSE"


def invoke_structured_decision_with_retry(
    llm: Any,
    prompt: str | Sequence[BaseMessage | Mapping[str, Any]],
    *,
    context: str,
    max_retries: int = 3,
) -> tuple[Any, str]:
    """Invoke an LLM and repair structured-decision validation failures."""
    try:
        response = llm.invoke(prompt)
    except Exception as exc:
        if not _is_recoverable_codex_provider_error(exc):
            raise
        decision_json = _fallback_structured_decision_json(context=context, reason=str(exc))
        return AIMessage(content=decision_json), decision_json
    last_content = str(getattr(response, "content", "") or "")
    last_error: StructuredDecisionValidationError | None = None

    for _attempt in range(max(0, max_retries) + 1):
        if _is_codex_fallback_response(last_content):
            return response, _fallback_structured_decision_json(context=context, reason=last_content)
        try:
            return response, ensure_structured_decision_json(last_content)
        except StructuredDecisionValidationError as exc:
            last_error = exc
            if _attempt >= max(0, max_retries):
                decision_json = _fallback_structured_decision_json(context=context, reason=str(exc))
                return AIMessage(content=decision_json), decision_json
            repair_prompt = _build_repair_prompt(
                context=context,
                validation_error=str(exc),
                invalid_response=last_content,
            )
            try:
                response = llm.invoke(_append_repair_request(prompt, last_content, repair_prompt))
            except Exception as repair_exc:
                if not _is_recoverable_codex_provider_error(repair_exc):
                    raise
                decision_json = _fallback_structured_decision_json(context=context, reason=str(repair_exc))
                return AIMessage(content=decision_json), decision_json
            last_content = str(getattr(response, "content", "") or "")

    raise last_error or StructuredDecisionValidationError("Structured decision validation failed.")


def _build_repair_prompt(*, context: str, validation_error: str, invalid_response: str) -> str:
    skeleton = _required_decision_skeleton()
    return (
        f"The previous {context} response failed TradingAgents structured-decision validation: "
        f"{validation_error}\n\n"
        "Repair the response now. Preserve the investment conclusion when possible, but return "
        "one complete JSON object that includes every required field from the decision schema. "
        "Return only JSON, with no markdown fences or prose. Use this top-level JSON shape and "
        "fill every placeholder with specific, evidence-grounded content:\n"
        f"{skeleton}\n\n"
        f"Previous invalid response:\n{invalid_response}"
    )


def _required_decision_skeleton() -> str:
    return (
        "{\n"
        '  "rating": "HOLD",\n'
        '  "portfolio_stance": "NEUTRAL",\n'
        '  "entry_action": "WAIT",\n'
        '  "setup_quality": "DEVELOPING",\n'
        '  "confidence": 0.50,\n'
        '  "time_horizon": "medium",\n'
        '  "entry_logic": "State the entry condition.",\n'
        '  "exit_logic": "State the exit or stop condition.",\n'
        '  "position_sizing": "State the sizing rule.",\n'
        '  "risk_limits": "State the risk limit.",\n'
        '  "catalysts": ["List concrete bullish or neutral catalysts."],\n'
        '  "invalidators": ["List concrete invalidation conditions."],\n'
        '  "watchlist_triggers": ["List concrete trigger conditions."],\n'
        '  "data_coverage": {\n'
        '    "company_news_count": 0,\n'
        '    "disclosures_count": 0,\n'
        '    "social_source": "unavailable",\n'
        '    "macro_items_count": 0\n'
        "  }\n"
        "}"
    )


def _append_repair_request(
    prompt: str | Sequence[BaseMessage | Mapping[str, Any]],
    invalid_response: str,
    repair_prompt: str,
) -> str | list[BaseMessage | Mapping[str, Any]]:
    if isinstance(prompt, str):
        return f"{prompt}\n\n{repair_prompt}"

    repaired: list[BaseMessage | Mapping[str, Any]] = list(prompt)
    if repaired and isinstance(repaired[0], BaseMessage):
        repaired.append(AIMessage(content=invalid_response))
        repaired.append(HumanMessage(content=repair_prompt))
    else:
        repaired.append({"role": "assistant", "content": invalid_response})
        repaired.append({"role": "user", "content": repair_prompt})
    return repaired


def _is_codex_fallback_response(content: str) -> bool:
    return _CODEX_FALLBACK_MARKER in str(content or "")


def _is_recoverable_codex_provider_error(exc: Exception) -> bool:
    text = str(exc).lower()
    return (
        "timed out waiting for codex app-server" in text
        or "codex app-server closed unexpectedly" in text
        or "codex returned malformed structured output" in text
    )


def _fallback_structured_decision_json(*, context: str, reason: str) -> str:
    payload = {
        "rating": "NO_TRADE",
        "portfolio_stance": "NEUTRAL",
        "entry_action": "WAIT",
        "risk_action": "NONE",
        "risk_action_reason": "No validated LLM decision was available for this step.",
        "risk_action_reason_codes": ["CODEX_PROVIDER_UNAVAILABLE"],
        "risk_action_confidence": 0.1,
        "risk_action_level": None,
        "profit_taking_plan": {"enabled": False, "reason_codes": ["CODEX_PROVIDER_UNAVAILABLE"]},
        "setup_quality": "WEAK",
        "confidence": 0.1,
        "time_horizon": "short",
        "entry_logic": (
            f"Do not initiate a new trade from the {context}; Codex provider fallback was used "
            "because no validated LLM synthesis was available."
        ),
        "exit_logic": "Keep existing risk controls unchanged and rerun the analysis before making a new decision.",
        "position_sizing": "Use 0% new capital until a validated analysis succeeds.",
        "risk_limits": "Treat this as a watchlist-only placeholder; require a successful rerun before execution.",
        "catalysts": ["Successful rerun with validated analyst and decision output."],
        "invalidators": ["Codex provider timeout or malformed structured output prevented validated analysis."],
        "watchlist_triggers": ["Rerun the scheduled analysis after Codex provider health recovers."],
        "data_coverage": {
            "company_news_count": 0,
            "disclosures_count": 0,
            "social_source": "unavailable",
            "macro_items_count": 0,
        },
        "execution_levels": {
            "intraday_pilot_rule": "No pilot entry while the decision is provider-fallback only.",
            "close_confirm_rule": "Require a successful rerun before any close-confirmed entry.",
            "next_day_followthrough_rule": "Reassess on the next run with validated data and LLM synthesis.",
            "failed_breakout_rule": "Block new buying until a validated decision is available.",
            "trim_rule": "Use existing portfolio risk rules; this fallback does not create a new trim signal.",
            "levels": [],
            "min_relative_volume": None,
            "vwap_required": False,
            "earliest_pilot_time_local": "10:30",
            "funding_priority": "low",
            "entry_window": "mid",
            "trigger_quality": "weak",
        },
        "fallback_reason": str(reason or "")[:500],
    }
    return ensure_structured_decision_json(json.dumps(payload, ensure_ascii=False))
