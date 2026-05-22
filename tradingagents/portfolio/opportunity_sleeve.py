from __future__ import annotations

from typing import Any


def compute_opportunity_pilot_budget(
    *,
    nav_krw: int,
    available_cash_krw: int,
    min_cash_buffer_krw: int,
    stop_distance_pct: float | None,
    profile: Any,
) -> dict[str, Any]:
    """Return read-only pilot sizing diagnostics for the opportunity sleeve."""

    nav = max(int(nav_krw or 0), 0)
    available_after_buffer = max(int(available_cash_krw or 0) - max(int(min_cash_buffer_krw or 0), 0), 0)
    sleeve_pct = _pct(profile, "opportunity_capture_sleeve_nav_pct", 7.5)
    per_pilot_pct = _pct(profile, "opportunity_capture_per_pilot_nav_pct", 1.0)
    max_loss_pct = _pct(profile, "opportunity_capture_max_loss_nav_pct", 0.3)
    max_stop_pct = _pct(profile, "max_pilot_stop_distance_pct", 12.0)
    enabled = bool(getattr(profile, "opportunity_capture_enabled", False))

    sleeve_total = int(nav * sleeve_pct / 100.0)
    per_pilot_cap = int(nav * per_pilot_pct / 100.0)
    max_loss = int(nav * max_loss_pct / 100.0)
    stop_pct = _float_or_none(stop_distance_pct)
    block_reasons: list[str] = []
    sizing_blocked = False
    budget_reason = "ok"

    if not enabled:
        return {
            "pilot_budget_krw": 0,
            "max_loss_krw": max_loss,
            "sleeve_total_krw": sleeve_total,
            "sizing_blocked": False,
            "block_reasons": ["opportunity_capture_disabled"],
            "budget_reason": "opportunity_capture_disabled",
        }

    if stop_pct is not None and max_stop_pct > 0 and stop_pct > max_stop_pct:
        sizing_blocked = True
        budget_reason = "stop_distance_block"
        block_reasons.append("stop_distance_block")

    loss_based_cap = per_pilot_cap
    if stop_pct is not None and stop_pct > 0 and max_loss > 0:
        loss_based_cap = int(max_loss / (stop_pct / 100.0))

    budget = min(sleeve_total, per_pilot_cap, available_after_buffer, loss_based_cap)
    budget = max(int(budget), 0)

    if available_after_buffer <= 0:
        sizing_blocked = True
        budget_reason = "cash_buffer_block"
        block_reasons.append("cash_buffer_block")
    if sleeve_total <= 0:
        sizing_blocked = True
        budget_reason = "opportunity_capture_sleeve_cap"
        block_reasons.append("opportunity_capture_sleeve_cap")
    if per_pilot_cap <= 0:
        sizing_blocked = True
        budget_reason = "opportunity_capture_per_pilot_cap"
        block_reasons.append("opportunity_capture_per_pilot_cap")
    if budget <= 0:
        sizing_blocked = True
        if budget_reason == "ok":
            budget_reason = "pilot_budget_zero"
        block_reasons.append(budget_reason)

    min_trade = int(getattr(getattr(profile, "constraints", None), "min_trade_krw", 0) or 0)
    if 0 < budget < min_trade:
        sizing_blocked = True
        budget_reason = "pilot_allowed_below_min_trade"
        block_reasons.append("pilot_allowed_below_min_trade")

    return {
        "pilot_budget_krw": budget if not sizing_blocked else max(budget, 0),
        "max_loss_krw": max_loss,
        "sleeve_total_krw": sleeve_total,
        "sizing_blocked": bool(sizing_blocked),
        "block_reasons": list(dict.fromkeys(block_reasons)),
        "budget_reason": budget_reason,
    }


def _pct(profile: Any, name: str, default: float) -> float:
    value = _float_or_none(getattr(profile, name, default))
    return max(value if value is not None else default, 0.0)


def _float_or_none(value: Any) -> float | None:
    if value in (None, "") or isinstance(value, bool):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
