from datetime import datetime, timezone
import json
import pytest
from tradingagents.portfolio.capital_policy import (
    cash_reserve,
    buy_budget,
    reduction_quantity,
    is_risk_reduction,
    load_policy,
)

POLICY = {"cash_reserve_nav_ratio": 0.2, "cash_reserve_floor_krw": 100000}


def test_scale_and_orderable_cap_are_independent():
    assert cash_reserve(9676532, POLICY) == 1935307
    assert cash_reserve(24752712, POLICY) == 4950543
    assert cash_reserve(200000, POLICY) == 100000
    assert buy_budget(3000000, 107553, 2500000) == 107553
    assert buy_budget(976652, 107553, 2500000) == 0
    assert buy_budget(3000000, 0, 100000) == 0


@pytest.mark.parametrize("nav", [0, -1, True, float("nan"), float("inf")])
def test_invalid_nav_is_not_policy_evidence(nav):
    with pytest.raises(ValueError):
        cash_reserve(nav, POLICY)


@pytest.mark.parametrize(
    "held,target,available,expected",
    [
        (1, 0.159, 1, 1),
        (2, 0.302, 2, 1),
        (10, 1.3, 10, 2),
        (3, 0.44, 3, 1),
        (1, 0.4, 0, 0),
        (0.436, 0.2, 0.436, 0),
        (2, 3, 2, 2),
    ],
)
def test_risk_reduction_uses_whole_shares_without_shorting(
    held, target, available, expected
):
    assert (
        reduction_quantity(target, available, held=held, risk_reduction=True)
        == expected
    )


def test_profit_taking_never_silently_exits_core_or_uses_risk_rounding():
    assert not is_risk_reduction({"sell_intent": "TAKE_PROFIT"}, "REDUCE_IF_TRIGGERED")
    assert reduction_quantity(0.2, 1, held=1, risk_reduction=False) == 0
    assert reduction_quantity(0.8, 1, held=1, risk_reduction=False, keep_core=0.45) == 0
    assert (
        reduction_quantity(2.6, 10, held=10, risk_reduction=False, keep_core=0.8) == 2
    )


@pytest.mark.parametrize(
    "effective", ["2030-01-01T00:00:00+00:00", "bad", "2020-01-01"]
)
def test_policy_cannot_be_backdated_or_undated(tmp_path, effective):
    p = tmp_path / "policy.json"
    p.write_text(json.dumps({**POLICY, "enabled": True, "effective_at": effective}))
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    if effective.startswith("2030"):
        assert load_policy(now=now, path=p) == {}
    else:
        with pytest.raises(ValueError):
            load_policy(now=now, path=p)
