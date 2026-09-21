from tradingagents.execution.paper import PaperLimits
from tradingagents.execution.sizing import size_paper_order


def test_new_position_can_use_explicit_budget_and_quote():
    result = size_paper_order(side="BUY", price_krw=100, nav_krw=100000, budget_krw=600)
    assert result.quantity == 5  # Costs must fit too.


def test_insufficient_budget_never_rounds_up_to_one_share():
    result = size_paper_order(
        side="SELL",
        price_krw=800000,
        nav_krw=25000000,
        budget_krw=120000,
        available_qty=1,
    )
    assert result.quantity == 0 and result.reason == "explicit_budget_below_one_share"


def test_risk_sell_does_not_use_small_buy_pilot_cap():
    sell = size_paper_order(
        side="SELL", price_krw=800000, nav_krw=25000000, quantity=1, available_qty=1
    )
    buy = size_paper_order(side="BUY", price_krw=800000, nav_krw=25000000, quantity=1)
    assert sell.quantity == 1 and buy.quantity == 0


def test_one_share_exception_requires_separate_limit_and_explicit_quantity():
    limits = PaperLimits(one_share_nav_ceiling=0.05)
    result = size_paper_order(
        side="BUY", price_krw=800000, nav_krw=25000000, quantity=1, limits=limits
    )
    assert result.quantity == 1
    too_large = size_paper_order(
        side="BUY", price_krw=2000000, nav_krw=25000000, quantity=1, limits=limits
    )
    assert too_large.quantity == 0
    budget = size_paper_order(
        side="BUY", price_krw=800000, nav_krw=25000000, budget_krw=250000, limits=limits
    )
    assert budget.quantity == 0


def test_sellable_quantity_and_costs_bound_order():
    assert (
        size_paper_order(
            side="SELL", price_krw=100, nav_krw=100000, quantity=10, available_qty=2.5
        ).quantity
        == 2
    )
    assert (
        size_paper_order(
            side="SELL", price_krw=100, nav_krw=100000, quantity=10
        ).quantity
        == 0
    )
    assert (
        size_paper_order(
            side="BUY", price_krw=float("nan"), nav_krw=100000, quantity=10
        ).quantity
        == 0
    )
