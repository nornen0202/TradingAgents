import pandas as pd
import pytest

from tradingagents.execution.research_backtest import simulate, targets


def test_future_price_cannot_change_past_signals():
    idx = pd.bdate_range("2020-01-01", periods=260)
    close = pd.DataFrame({"A": range(100, 360)}, index=idx)
    original = targets(close, "trend_200")
    close.iloc[240:] *= 10
    pd.testing.assert_frame_equal(
        original.iloc[:240], targets(close, "trend_200").iloc[:240]
    )


def test_prior_close_target_fills_at_next_open_and_costs_apply():
    idx = pd.bdate_range("2020-01-01", periods=3)
    px = pd.DataFrame({"A": [10.0, 20.0, 40.0]}, index=idx)
    desired = pd.DataFrame({"A": [0.0, 1.0, 0.0]}, index=idx)
    m, rows, trades = simulate(
        px,
        px,
        desired,
        start=str(idx[1].date()),
        end=str(idx[-1].date()),
        cost_bps=10,
        rebalance="daily",
    )
    assert len(trades) == 1
    assert trades[0]["date"] == str(idx[2].date())
    assert trades[0]["price"] == 40
    assert m["total_return_pct"] < 0
    assert rows[0]["nav"] == 100000


def test_missing_prices_are_not_forward_filled():
    idx = pd.bdate_range("2020-01-01", periods=3)
    px = pd.DataFrame({"A": [10.0, float("nan"), 40.0]}, index=idx)
    with pytest.raises(ValueError):
        simulate(px, px, px * 0, start="2020-01-02", end="2020-01-03")


def test_buy_hold_flat_market_loses_exactly_entry_cost_on_bought_units():
    idx = pd.bdate_range("2020-01-01", periods=3)
    px = pd.DataFrame({"A": [100.0] * 3}, index=idx)
    m, rows, trades = simulate(
        px,
        px,
        targets(px, "buy_hold"),
        start="2020-01-02",
        end="2020-01-03",
        cost_bps=10,
        rebalance="once",
    )
    assert rows[-1]["nav"] == pytest.approx(100000 - trades[0]["cost"])
    assert m["order_legs"] == 1
