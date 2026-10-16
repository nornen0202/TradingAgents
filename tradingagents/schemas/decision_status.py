"""Shared safety status for schema-valid placeholders without a validated decision."""

from __future__ import annotations

from .decision import StructuredDecision


UNVALIDATED_DECISION_REASON_CODES = frozenset({
    "CODEX_PROVIDER_UNAVAILABLE",
    "STRUCTURED_DECISION_INVALID",
})


def is_unvalidated_decision(decision: StructuredDecision) -> bool:
    """Keep provider failures and exhausted output repairs out of actionable results."""
    return bool(UNVALIDATED_DECISION_REASON_CODES.intersection(decision.risk_action_reason_codes))
