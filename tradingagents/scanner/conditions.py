"""Small, typed scanner condition language. No executable expressions are accepted.

Missing or invalid data propagates as unknown, including through ``not``. Only a
definite True selects a candidate. Dates are checked by the scanner before this
module sees a row.
"""

from __future__ import annotations

import math
from typing import Any, Mapping


NUMERIC_FIELDS = frozenset({
    "open", "high", "low", "close", "prev_close", "volume", "prev_volume",
    "trading_value", "market_cap", "volume_ratio_to_market_avg", "volume_ratio",
    "daily_change_pct", "gap_pct", "close_strength", "high_52w", "sector_rank",
    "sector_leadership_score", "risk_reward_ratio", "stop_loss_pct",
    "trigger_score", "agent_fit_score", "final_score",
})
TEXT_FIELDS = frozenset({"ticker", "market", "sector", "trigger_type"})
BOOL_FIELDS = frozenset({"halted"})
FIELDS = NUMERIC_FIELDS | TEXT_FIELDS | BOOL_FIELDS
EXAMPLE_CONDITION = {"all": [
    {"field": "volume_ratio", "op": "gte", "value": 1.5},
    {"field": "trading_value", "op": "gte", "value": 10_000_000_000},
    {"not": {"field": "halted", "op": "eq", "value": True}},
]}


def _finite(value: Any) -> bool:
    return type(value) in (int, float) and math.isfinite(value)


def validate_condition(condition: Mapping[str, Any]) -> dict[str, Any]:
    """Validate and copy a JSON tree, with bounded depth and work."""
    remaining = 100

    def visit(node: Any, depth: int) -> dict[str, Any]:
        nonlocal remaining
        remaining -= 1
        if remaining < 0 or depth > 8 or not isinstance(node, dict):
            raise ValueError("Condition must be a JSON object of at most 100 nodes and 8 levels")
        if set(node) in ({"all"}, {"any"}):
            key = next(iter(node))
            if not isinstance(node[key], list) or not node[key]:
                raise ValueError("Compound conditions require a nonempty list")
            return {key: [visit(child, depth + 1) for child in node[key]]}
        if set(node) == {"not"}:
            return {"not": visit(node["not"], depth + 1)}
        if set(node) != {"field", "op", "value"}:
            raise ValueError("Expected all/any/not or field/op/value")
        field, op, value = node["field"], node["op"], node["value"]
        if not isinstance(field, str) or field not in FIELDS:
            raise ValueError("Unknown scanner field")
        operators = {"eq", "ne", "gt", "gte", "lt", "lte"} if field in NUMERIC_FIELDS else {"eq", "ne", "in"}
        if not isinstance(op, str) or op not in operators:
            raise ValueError("Unsupported operator for field")
        values = value if op == "in" else [value]
        if not isinstance(values, list) or not values or len(values) > 100:
            raise ValueError("in requires between 1 and 100 values")
        for item in values:
            valid = _finite(item) if field in NUMERIC_FIELDS else (
                isinstance(item, str) and bool(item.strip()) if field in TEXT_FIELDS else type(item) is bool
            )
            if not valid:
                raise ValueError("Condition value has the wrong type or is nonfinite")
        return {"field": field, "op": op, "value": list(value) if op == "in" else value}

    return visit(condition, 0)


def evaluate_condition(condition: Mapping[str, Any], row: Mapping[str, Any]) -> bool:
    """Return True only when a validated condition is known to pass."""
    tree = validate_condition(condition)

    def evaluate(node: dict[str, Any]) -> bool | None:
        if "not" in node:
            result = evaluate(node["not"])
            return None if result is None else not result
        for key in ("all", "any"):
            if key in node:
                results = [evaluate(child) for child in node[key]]
                if key == "all":
                    return False if False in results else (None if None in results else True)
                return True if True in results else (None if None in results else False)
        field, op, expected = node["field"], node["op"], node["value"]
        actual = row.get(field)
        valid = _finite(actual) if field in NUMERIC_FIELDS else (
            isinstance(actual, str) and bool(actual.strip()) if field in TEXT_FIELDS else type(actual) is bool
        )
        if not valid:
            return None
        if op == "eq":
            return actual == expected
        if op == "ne":
            return actual != expected
        if op == "in":
            return actual in expected
        if op == "gt":
            return actual > expected
        if op == "gte":
            return actual >= expected
        if op == "lt":
            return actual < expected
        return actual <= expected

    return evaluate(tree) is True
