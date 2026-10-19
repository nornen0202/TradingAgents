"""Versioned cash and integer sizing policy; never authorizes broker orders."""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
import json
from math import ceil, floor, isfinite
from pathlib import Path

POLICY_PATH = (
    Path(__file__).resolve().parents[2] / "config" / "strategy_capital_policy.json"
)


def load_policy(*, now: datetime, path: Path = POLICY_PATH) -> dict:
    policy = json.loads(path.read_text(encoding="utf-8"))
    effective = datetime.fromisoformat(policy["effective_at"])
    if now.tzinfo is None or effective.tzinfo is None:
        raise ValueError("Policy requires timezone-aware timestamps")
    if effective > now or not policy.get("enabled"):
        return {}
    cash_reserve(1_000_000, policy)  # Validate configuration before using it.
    return policy


def cash_reserve(nav: float, policy: dict) -> int:
    ratio, minimum = policy["cash_reserve_nav_ratio"], policy["cash_reserve_floor_krw"]
    if any(
        isinstance(v, bool) or not isinstance(v, (float, int)) or not isfinite(v)
        for v in (nav, ratio, minimum)
    ):
        raise ValueError("Invalid cash-policy input")
    if nav <= 0 or not 0 <= ratio <= 1 or minimum < 0:
        raise ValueError("Invalid cash-policy bounds")
    return ceil(max(nav * ratio, minimum))


def buy_budget(cash: float, buying_power: float, reserve: float) -> float:
    """Reserve is deducted from cash once; broker buying power is a separate cap."""
    return max(0.0, min(cash - reserve, buying_power))


def reduction_quantity(
    target: float,
    available: float,
    *,
    risk_reduction: bool,
    held: float,
    keep_core: float = 0,
) -> int:
    values = (target, available, held, keep_core)
    if any(
        isinstance(v, bool)
        or not isinstance(v, (int, float))
        or not isfinite(v)
        or v < 0
        for v in values
    ):
        raise ValueError("Invalid reduction input")
    if available > held or keep_core > 1:
        raise ValueError("Invalid available/core bounds")
    # A reduction is a minimum risk removal: floor the retained position, not
    # the shares to sell. Soft rebalancing uses nearest shares and preserves core.
    quantity = ceil(target - 1e-10) if risk_reduction else floor(target + 0.5)
    cap = floor(available)
    if not risk_reduction:
        cap = min(cap, max(0, floor(held - ceil(held * keep_core))))
    return max(0, min(quantity, cap))


def is_risk_reduction(action: dict, action_code: str = "") -> bool:
    intent = str(action.get("sell_intent") or "").upper()
    if intent not in {"", "NONE"}:
        return intent in {"REDUCE_RISK", "STOP_LOSS", "EXIT"}
    return str(action_code).upper() in {
        "REDUCE_NOW",
        "REDUCE_IF_TRIGGERED",
        "STOP_LOSS_NOW",
        "STOP_LOSS_IF_TRIGGERED",
        "EXIT_NOW",
        "EXIT_IF_TRIGGERED",
    }


def apply_snapshot_policy(snapshot, *, now: datetime | None = None):
    policy = load_policy(now=now or datetime.now(timezone.utc))
    if not policy:
        return snapshot
    reserve = cash_reserve(snapshot.account_value_krw, policy)
    return replace(
        snapshot,
        constraints=replace(snapshot.constraints, min_cash_buffer_krw=reserve),
        cash_diagnostics={
            **snapshot.cash_diagnostics,
            "capital_policy": {**policy, "resolved_reserve_krw": reserve},
        },
    )
