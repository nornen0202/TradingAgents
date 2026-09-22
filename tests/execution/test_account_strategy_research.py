import numpy as np
import pandas as pd
import pytest

from tools.review_live_account_strategies import extract_market_prices
from tradingagents.execution.account_strategy_research import (
    STRATEGIES,
    open_signals,
    pareto_strategies,
    price_hash,
    simulate,
    specification_hash,
)


def prices(values, dates=None, opens=None):
    index = (
        pd.to_datetime(dates)
        if dates is not None
        else pd.bdate_range("2019-01-01", periods=len(values))
    )
    return pd.DataFrame(
        {"Open": values if opens is None else opens, "Close": values}, index=index
    )


@pytest.fixture
def history():
    t = np.arange(1100)
    return prices(100 * np.exp(0.0008 * t + 0.13 * np.sin(t / 30)))


@pytest.mark.parametrize("strategy", STRATEGIES)
def test_prefix_invariance_of_signals_and_simulation(history, strategy):
    prefix = history.iloc[:830]
    pd.testing.assert_frame_equal(
        open_signals(history, strategy).loc[prefix.index],
        open_signals(prefix, strategy),
    )
    _, long_curve, long_orders = simulate(
        history,
        strategy,
        start="2021-01-01",
        end="2023-12-31",
        execution_delay_sessions=1,
    )
    _, short_curve, short_orders = simulate(
        prefix,
        strategy,
        start="2021-01-01",
        end=str(prefix.index[-1].date()),
        execution_delay_sessions=1,
    )
    assert long_curve[: len(short_curve)] == short_curve
    assert [
        row for row in long_orders if row["date"] <= short_curve[-1]["date"]
    ] == short_orders


def test_incomplete_month_is_never_a_trend_signal(history):
    altered = history.copy()
    in_month = altered.index.to_period("M") == pd.Period("2021-06")
    altered.loc[in_month, "Close"] *= 100
    original_signals = open_signals(history, "monthly_trend")
    altered_signals = open_signals(altered, "monthly_trend")
    pd.testing.assert_frame_equal(
        original_signals.loc[in_month], altered_signals.loc[in_month]
    )
    month_rows = original_signals.loc[in_month]
    assert all(pd.Timestamp(date).month == 5 for date in month_rows.signal_date)


def test_completed_month_signal_executes_first_next_month_open(history):
    _, _, orders = simulate(
        history, "monthly_trend", start="2021-01-01", end="2021-12-31", cost_bps=0
    )
    assert orders
    for order in orders:
        when, signal = pd.Timestamp(order["date"]), pd.Timestamp(order["signal_date"])
        assert signal < when
        same_month = history.index[history.index.to_period("M") == when.to_period("M")]
        assert when == same_month[0]
        assert signal.to_period("M") < when.to_period("M")


def test_delay_means_one_additional_session_not_same_bar():
    data = prices(
        [10, 10, 20, 30], ["2020-01-01", "2020-01-02", "2020-01-03", "2020-01-06"]
    )
    fast, _, fast_orders = simulate(
        data,
        "broad_hold",
        start="2020-01-02",
        end="2020-01-06",
        initial=100,
        cost_bps=0,
    )
    slow, _, slow_orders = simulate(
        data,
        "broad_hold",
        start="2020-01-02",
        end="2020-01-06",
        initial=100,
        cost_bps=0,
        execution_delay_sessions=1,
    )
    assert fast["final_nav"] == 300
    assert slow["final_nav"] == 150
    assert fast_orders[0]["date"] == "2020-01-02"
    assert slow_orders[0]["date"] == "2020-01-03"
    assert slow_orders[0]["signal_date"] == "2020-01-01"


def test_quarterly_band_uses_prior_close_and_skips_small_drift():
    data = prices(
        [100, 100, 120, 200, 200, 200],
        [
            "2020-01-01",
            "2020-01-02",
            "2020-03-31",
            "2020-04-01",
            "2020-06-30",
            "2020-07-01",
        ],
    )
    _, curve, orders = simulate(
        data,
        "balanced_80_20",
        start="2020-01-02",
        end="2020-07-01",
        initial=100,
        cost_bps=0,
    )
    assert [row["date"] for row in orders] == ["2020-01-02", "2020-07-01"]
    assert orders[1]["side"] == "SELL"
    assert curve[-1]["exposure"] == pytest.approx(0.8)


@pytest.mark.parametrize(
    "strategy,target", [("broad_hold", 1.0), ("balanced_80_20", 0.8)]
)
def test_transaction_cost_and_post_cost_weight_conserve_cash(strategy, target):
    data = prices([100] * 5)
    metrics, curve, orders = simulate(
        data, strategy, start="2019-01-02", end="2019-01-07", initial=100, cost_bps=100
    )
    notional = target * 100 / (1 + target * 0.01)
    assert orders[0]["notional"] == pytest.approx(notional)
    assert metrics["cost_paid"] == pytest.approx(notional * 0.01)
    assert metrics["final_nav"] + metrics["cost_paid"] == pytest.approx(100)
    assert all(row["cash"] >= 0 for row in curve)
    assert curve[-1]["exposure"] == pytest.approx(target)
    assert len(orders) == 1


def test_sell_cost_also_matches_post_cost_target():
    data = prices(
        [100, 100, 200, 200], ["2020-01-01", "2020-01-02", "2020-03-31", "2020-04-01"]
    )
    _, curve, orders = simulate(
        data,
        "balanced_80_20",
        start="2020-01-02",
        end="2020-04-01",
        initial=100,
        cost_bps=100,
    )
    assert orders[-1]["side"] == "SELL"
    assert curve[-1]["exposure"] == pytest.approx(0.8)
    assert curve[-1]["cash"] >= 0


def test_volatility_cap_is_lagged_and_never_levered():
    t = np.arange(700)
    data = prices(100 * np.exp(t * 0.002 + 0.15 * np.sin(t)))
    signals = open_signals(data, "trend_vol_cap")
    assert signals.weight.max() <= 0.8
    eligible = signals[(signals.weight > 0) & (signals.weight < 0.8)]
    assert not eligible.empty
    row = eligible.iloc[-1]
    historical = data.Close.loc[: row.signal_date]
    sigma = historical.pct_change(fill_method=None).iloc[-60:].std(ddof=1) * np.sqrt(
        252
    )
    assert row.weight == pytest.approx(0.1 / sigma)


def test_unrecovered_underwater_calendar_days():
    data = prices(
        [100, 100, 90, 95], ["2020-01-01", "2020-01-02", "2020-01-03", "2020-01-06"]
    )
    metrics, _, _ = simulate(
        data, "broad_hold", start="2020-01-02", end="2020-01-06", cost_bps=0
    )
    assert metrics["max_drawdown_pct"] == pytest.approx(-10)
    assert metrics["max_underwater_calendar_days"] == 4
    assert metrics["underwater_at_end"]


def test_new_highs_alone_have_no_underwater_days():
    data = prices([100, 110, 120, 130])
    metrics, _, _ = simulate(
        data, "broad_hold", start="2019-01-02", end="2019-01-07", cost_bps=0
    )
    assert metrics["max_underwater_calendar_days"] == 0


def test_mismatched_scenario_pareto_is_rejected():
    rows = [
        {"strategy": "a", "total_return_pct": 10, "max_drawdown_pct": -10},
        {"strategy": "b", "total_return_pct": 20, "max_drawdown_pct": -20},
        {"strategy": "c", "total_return_pct": 9, "max_drawdown_pct": -20},
    ]
    assert pareto_strategies(rows) == ["a", "b"]
    rows[0]["cost_bps_per_side"] = 10
    with pytest.raises(ValueError, match="identical"):
        pareto_strategies(rows)


def test_hashes_stable_and_price_edits_detected(history):
    assert len(specification_hash()) == 64
    assert price_hash(history) == price_hash(history.copy())
    changed = history.copy()
    changed.iloc[-1, 0] += 1
    assert price_hash(history) != price_hash(changed)


def test_joint_calendar_missing_days_not_filled():
    cache = pd.DataFrame(
        {("Open", "X"): [100, np.nan, 102], ("Close", "X"): [101, np.nan, 103]},
        index=pd.bdate_range("2020-01-01", periods=3),
    )
    data, info = extract_market_prices(cache, "X")
    assert len(data) == 2
    assert info["joint_calendar_rows_without_any_quote"] == 1
    cache.loc[cache.index[1], ("Close", "X")] = 100
    with pytest.raises(ValueError, match="partial"):
        extract_market_prices(cache, "X")


def test_large_moves_are_flagged_without_silently_editing_history():
    cache = pd.DataFrame(
        {("Open", "X"): [100, 100], ("Close", "X"): [100, 125]},
        index=pd.bdate_range("2020-01-01", periods=2),
    )
    data, info = extract_market_prices(cache, "X")
    assert data.Close.iloc[-1] == 125
    assert info["large_moves_requiring_source_review"][0]["return_pct"] == 25
    assert not info["independent_source_verified"]


def test_warmup_and_same_session_signal_fail_closed():
    data = prices([100] * 10)
    with pytest.raises(ValueError, match="warmup"):
        simulate(data, "monthly_trend", start="2019-01-02", end="2019-01-10")
    signals = open_signals(data, "broad_hold")
    signals.loc[data.index[1], "signal_date"] = data.index[1]
    with pytest.raises(ValueError, match="predate"):
        simulate(
            data, "broad_hold", start="2019-01-02", end="2019-01-10", signals=signals
        )


@pytest.mark.parametrize("bad", [np.nan, np.inf, -1, 0])
def test_bad_prices_rejected(bad):
    data = prices([100, bad, 100])
    with pytest.raises(ValueError, match="finite"):
        open_signals(data, "broad_hold")
