"""Integer paper sizing from explicit quantities/budgets, never natural language."""

from __future__ import annotations

from dataclasses import dataclass
import math

from .paper import PaperLimits, order_nav_limit, positive


@dataclass(frozen=True)
class SizeResult:
    quantity: int
    reason: str
    one_share_nav_pct: float | None = None


def size_paper_order(
    *,
    side: str,
    price_krw: float,
    nav_krw: float,
    quantity=None,
    budget_krw=None,
    available_qty=None,
    limits: PaperLimits | None = None,
) -> SizeResult:
    limits = limits or PaperLimits()
    if side not in {"BUY", "SELL"} or not positive(price_krw) or not positive(nav_krw):
        return SizeResult(0, "invalid_sizing_price_or_nav")
    share_pct = price_krw / nav_krw * 100
    if quantity is not None and (type(quantity) is not int or quantity <= 0):
        return SizeResult(0, "invalid_integer_quantity", share_pct)
    if budget_krw is not None and not positive(budget_krw):
        return SizeResult(0, "invalid_explicit_budget", share_pct)
    if quantity is None and budget_krw is None:
        return SizeResult(0, "missing_quantity_and_budget", share_pct)
    # Budget includes a conservative 30bp limit collar plus estimated fees/tax.
    unit_cost = price_krw * (1.003 if side == "BUY" else 1.0)
    budget_unit = unit_cost * (
        1 + (limits.fee_bps + (limits.sell_tax_bps if side == "SELL" else 0)) / 10000
    )
    requested = (
        quantity if quantity is not None else math.floor(budget_krw / budget_unit)
    )
    if budget_krw is not None:
        requested = min(requested, math.floor(budget_krw / budget_unit))
    if not requested:
        return SizeResult(0, "explicit_budget_below_one_share", share_pct)
    cap = math.floor(nav_krw * order_nav_limit(limits, side, requested) / unit_cost)
    sized = min(requested, cap)
    if side == "SELL":
        if (
            available_qty is None
            or not isinstance(available_qty, (int, float))
            or isinstance(available_qty, bool)
            or not math.isfinite(available_qty)
            or available_qty < 0
        ):
            return SizeResult(0, "missing_available_holdings", share_pct)
        sized = min(sized, math.floor(available_qty))
    if not sized:
        return SizeResult(0, "whole_share_nav_or_holdings_limit", share_pct)
    return SizeResult(
        sized,
        "explicit_integer_quantity"
        if quantity is not None
        else "explicit_budget_to_whole_shares",
        share_pct,
    )
