from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage

from tradingagents.schemas import StructuredDecisionValidationError, ensure_structured_decision_json


def invoke_structured_decision_with_retry(
    llm: Any,
    prompt: str | Sequence[BaseMessage | Mapping[str, Any]],
    *,
    context: str,
    max_retries: int = 3,
) -> tuple[Any, str]:
    """Invoke an LLM and repair structured-decision validation failures."""
    response = llm.invoke(prompt)
    last_content = str(getattr(response, "content", "") or "")
    last_error: StructuredDecisionValidationError | None = None

    for _attempt in range(max(0, max_retries) + 1):
        try:
            return response, ensure_structured_decision_json(last_content)
        except StructuredDecisionValidationError as exc:
            last_error = exc
            if _attempt >= max(0, max_retries):
                raise
            repair_prompt = _build_repair_prompt(
                context=context,
                validation_error=str(exc),
                invalid_response=last_content,
            )
            response = llm.invoke(_append_repair_request(prompt, last_content, repair_prompt))
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
