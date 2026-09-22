"""Fixed-rule, single-asset retrospective research; no broker dependencies.

Adjusted OHLC represents fractional total-return units, never executable shares.
Signals only use completed observations. Cash has zero yield; tax, FX, settlement
and conversion of existing holdings into a strategy are intentionally unmodeled.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

import numpy as np
import pandas as pd

STRATEGIES = ("broad_hold", "balanced_80_20", "monthly_trend", "trend_vol_cap")
SPECIFICATION = {
    "version": "account-strategy-research-v1",
    "strategies": list(STRATEGIES),
    "balanced_weight": 0.8,
    "balanced_review": "calendar_quarter_first_session",
    "balanced_drift_percentage_points": 5.0,
    "trend_completed_months": 10,
    "trend_comparison": "last_completed_month_close > mean_last_10_completed_month_closes",
    "trend_review": "calendar_month_first_session",
    "trend_risk_on_weight": 0.8,
    "volatility_daily_returns": 60,
    "volatility_estimator": "sample_std_simple_returns * sqrt(252)",
    "volatility_target": 0.1,
    "volatility_weight_cap": 0.8,
    "volatility_observation": "last_completed_month_last_session",
    "cap_applies_at": "rebalance_target_only; weights_can_drift_between_reviews",
    "price_units": "fractional_adjusted_total_return_units",
    "cash_yield": 0.0,
    "tax_modeled": False,
    "fx_modeled": False,
    "initial_holdings_conversion_cost_modeled": False,
    "entry_transaction_cost_modeled": True,
    "terminal_liquidation": False,
    "evaluation": "retrospective_sensitivity_not_out_of_sample",
    "initial_state": "all_cash_independent_reset_each_period",
    "execution": "next_available_open_after_information; optional_extra_session_delay",
    "warmup": "historical_prices_before_evaluation_start",
}


def specification_hash() -> str:
    return hashlib.sha256(
        json.dumps(SPECIFICATION, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def validate_prices(prices: pd.DataFrame) -> None:
    if not isinstance(prices.index, pd.DatetimeIndex):
        raise ValueError("DatetimeIndex required")
    if (
        prices.empty
        or not prices.index.is_monotonic_increasing
        or prices.index.has_duplicates
        or prices.index.hasnans
        or prices.index.tz is not None
        or not prices.index.equals(prices.index.normalize())
    ):
        raise ValueError("Unique increasing naive session dates required")
    if not {"Open", "Close"}.issubset(prices.columns):
        raise ValueError("Open and Close required")
    values = prices[["Open", "Close"]].to_numpy(dtype=float)
    if not np.isfinite(values).all() or (values <= 0).any():
        raise ValueError("Complete positive finite prices required")


def price_hash(prices: pd.DataFrame) -> str:
    validate_prices(prices)
    canonical = prices[["Open", "Close"]].to_csv(
        date_format="%Y-%m-%d", float_format="%.17g", lineterminator="\n"
    )
    return hashlib.sha256(canonical.encode()).hexdigest()


def open_signals(prices: pd.DataFrame, strategy: str) -> pd.DataFrame:
    """Target available at each open, excluding the current incomplete month."""
    validate_prices(prices)
    if strategy not in STRATEGIES:
        raise ValueError("Unknown strategy")
    close = prices.Close
    periods = close.index.to_period("M")
    monthly = close.groupby(periods).last()
    monthly_dates = pd.Series(close.index, index=close.index).groupby(periods).last()
    # Shift the completed-month statistic onto the following month. Mapping by
    # month also works when a calendar month has no observations.
    monthly_mean = monthly.rolling(10, min_periods=10).mean()
    vol = close.pct_change(fill_method=None).rolling(60, min_periods=60).std(ddof=1)
    monthly_vol = (vol * np.sqrt(252)).groupby(periods).last()
    rows = []
    for i, date in enumerate(close.index):
        previous_date = close.index[i - 1] if i else pd.NaT
        target, ready, signal_date = 0.0, True, previous_date
        if strategy == "broad_hold":
            target = 1.0
        elif strategy == "balanced_80_20":
            target = 0.8
        else:
            completed = monthly.index[monthly.index < date.to_period("M")]
            ready = len(completed) >= 10
            if len(completed):
                last = completed[-1]
                signal_date = monthly_dates.loc[last]
                if ready and monthly.loc[last] > monthly_mean.loc[last]:
                    target = 0.8
                    if strategy == "trend_vol_cap":
                        sigma = monthly_vol.loc[last]
                        ready = bool(np.isfinite(sigma))
                        target = min(0.8, 0.1 / sigma) if ready and sigma > 0 else 0.8
                        if not ready:
                            target = 0.0
        rows.append({"weight": target, "signal_date": signal_date, "ready": ready})
    return pd.DataFrame(rows, index=close.index)


def _rebalance(cash: float, units: float, price: float, weight: float, cost: float):
    """Solve target weight against NAV *after* proportional transaction costs."""
    value = units * price
    equity = cash + value
    gap = weight * equity - value
    delta = gap / (1 + weight * cost) if gap >= 0 else gap / (1 - weight * cost)
    if abs(delta) <= max(equity, 1.0) * 1e-12:
        return cash, units, 0.0, 0.0
    fee = abs(delta) * cost
    next_cash = cash - delta - fee
    next_units = units + delta / price
    tolerance = max(equity, 1.0) * 1e-10
    if next_cash < -tolerance or next_units < -tolerance:
        raise AssertionError("Research ledger cannot borrow cash or short")
    return max(0.0, next_cash), max(0.0, next_units), delta, fee


def simulate(
    prices: pd.DataFrame,
    strategy: str,
    *,
    start: str,
    end: str,
    cost_bps: float = 10.0,
    execution_delay_sessions: int = 0,
    initial: float = 100000.0,
    signals: pd.DataFrame | None = None,
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    """Independently initialize an all-cash research account for this period.

    delay=0 is the first eligible next open, not same-close execution. delay=1
    holds the target fixed for one additional observed market session.
    """
    validate_prices(prices)
    if strategy not in STRATEGIES:
        raise ValueError("Unknown strategy")
    if (
        isinstance(execution_delay_sessions, bool)
        or execution_delay_sessions not in (0, 1)
        or not np.isfinite(cost_bps)
        or not 0 <= cost_bps < 10000
        or not np.isfinite(initial)
        or initial <= 0
    ):
        raise ValueError("Invalid delay, costs or capital")
    if signals is None:
        signals = open_signals(prices, strategy)
    if not signals.index.equals(prices.index):
        raise ValueError("Signals must match the price session index")
    weights = signals.weight.to_numpy(dtype=float)
    if not np.isfinite(weights).all() or (weights < 0).any() or (weights > 1).any():
        raise ValueError("Invalid signal weights")
    ix = np.flatnonzero(
        (prices.index >= pd.Timestamp(start)) & (prices.index <= pd.Timestamp(end))
    )
    if not len(ix) or ix[0] == 0:
        raise ValueError("Evaluation needs at least one prior session")
    cash, units, cost = float(initial), 0.0, cost_bps / 10000
    rows, orders, pending = [], [], []
    decisions = 0
    for n, i in enumerate(ix):
        date, previous = prices.index[i], prices.index[i - 1]
        due = n == 0
        if strategy == "balanced_80_20":
            due |= date.to_period("Q") != previous.to_period("Q")
        elif strategy in {"monthly_trend", "trend_vol_cap"}:
            due |= date.to_period("M") != previous.to_period("M")
        if due:
            row = signals.iloc[i]
            signal_date = pd.Timestamp(row.signal_date)
            if pd.isna(signal_date) or signal_date >= date:
                raise ValueError("Signal must predate eligible execution session")
            if not bool(row.ready):
                raise ValueError("Insufficient historical warmup")
            previous_value = units * float(prices.Close.iloc[i - 1])
            previous_weight = previous_value / (cash + previous_value)
            band_breached = abs(previous_weight - 0.8) >= 0.05 - 1e-12
            if strategy != "balanced_80_20" or n == 0 or band_breached:
                pending.append(
                    (i + execution_delay_sessions, float(row.weight), signal_date, date)
                )
                decisions += 1
        op = float(prices.Open.iloc[i])
        for execution_index, weight, signal_date, eligible_date in pending:
            if execution_index != i:
                continue
            cash, units, delta, fee = _rebalance(cash, units, op, weight, cost)
            if delta:
                orders.append(
                    {
                        "date": date.date().isoformat(),
                        "signal_date": signal_date.date().isoformat(),
                        "eligible_date": eligible_date.date().isoformat(),
                        "target_weight": weight,
                        "side": "BUY" if delta > 0 else "SELL",
                        "adjusted_units": delta / op,
                        "adjusted_price": op,
                        "notional": abs(delta),
                        "cost": fee,
                    }
                )
        pending = [item for item in pending if item[0] > i]
        nav = cash + units * float(prices.Close.iloc[i])
        rows.append(
            {
                "date": date.date().isoformat(),
                "nav": nav,
                "cash": cash,
                "adjusted_units": units,
                "exposure": 1 - cash / nav,
            }
        )
    navs = np.r_[initial, [row["nav"] for row in rows]]
    drawdowns = navs / np.maximum.accumulate(navs) - 1
    # Calendar-day duration, including an unrecovered drawdown at sample end.
    peak_value, peak_date = initial, prices.index[ix[0] - 1]
    max_underwater_days, underwater = 0, False
    for row in rows:
        date = pd.Timestamp(row["date"])
        if row["nav"] >= peak_value:
            if underwater:
                max_underwater_days = max(max_underwater_days, (date - peak_date).days)
            peak_value, peak_date = row["nav"], date
            underwater = False
        else:
            underwater = True
            max_underwater_days = max(max_underwater_days, (date - peak_date).days)
    elapsed_years = (prices.index[ix[-1]] - prices.index[ix[0]]).days / 365.25
    metrics = {
        "strategy": strategy,
        "start": rows[0]["date"],
        "end": rows[-1]["date"],
        "sessions": len(rows),
        "cost_bps_per_side": cost_bps,
        "execution_delay_sessions": execution_delay_sessions,
        "initial_nav": initial,
        "final_nav": float(navs[-1]),
        "total_return_pct": float((navs[-1] / initial - 1) * 100),
        "cagr_pct": float(((navs[-1] / initial) ** (1 / elapsed_years) - 1) * 100)
        if elapsed_years >= 1
        else None,
        "max_drawdown_pct": float(np.min(drawdowns) * 100),
        "max_underwater_calendar_days": max_underwater_days,
        "underwater_at_end": bool(drawdowns[-1] < -1e-12),
        "turnover_over_initial": float(sum(o["notional"] for o in orders) / initial),
        "cost_paid": float(sum(o["cost"] for o in orders)),
        "cost_pct_initial": float(sum(o["cost"] for o in orders) / initial * 100),
        "mean_exposure_pct": float(np.mean([row["exposure"] for row in rows]) * 100),
        "order_legs": len(orders),
        "decisions": decisions,
        "pending_decisions_at_end": len(pending),
    }
    return metrics, rows, orders


def pareto_strategies(results: list[dict[str, Any]]) -> list[str]:
    """Non-dominated return/drawdown set within ONE identical scenario."""
    scenario_fields = (
        "start",
        "end",
        "cost_bps_per_side",
        "execution_delay_sessions",
        "ticker",
    )
    if results and any(
        any(row.get(field) != results[0].get(field) for field in scenario_fields)
        for row in results
    ):
        raise ValueError("Pareto comparison requires identical scenarios")
    frontier = []
    for candidate in results:
        dominated = any(
            other["total_return_pct"] >= candidate["total_return_pct"]
            and other["max_drawdown_pct"] >= candidate["max_drawdown_pct"]
            and (
                other["total_return_pct"] > candidate["total_return_pct"]
                or other["max_drawdown_pct"] > candidate["max_drawdown_pct"]
            )
            for other in results
        )
        if not dominated:
            frontier.append(candidate["strategy"])
    return frontier
