"""Deterministic, next-open research simulator; never sends broker orders.

Input OHLC is adjusted consistently for splits/distributions. Units therefore
represent total-return units, not an executable share ledger. Cash earns zero.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def targets(close: pd.DataFrame, strategy: str) -> pd.DataFrame:
    """Each row uses only information available at that day's completed close."""
    if close.empty or close.isna().any().any() or (close <= 0).any().any():
        raise ValueError("Complete, positive, aligned closes required")
    out = close * 0.0
    if strategy == "buy_hold":
        out.iloc[:, 0] = 1.0
    elif strategy == "trend_200":
        out.iloc[:, 0] = (
            close.iloc[:, 0] > close.iloc[:, 0].rolling(200).mean()
        ).astype(float)
    elif strategy == "momentum_126_top2":
        mom = close / close.shift(126) - 1
        eligible = (mom > 0) & (close > close.rolling(200).mean())
        ranks = mom.where(eligible).rank(axis=1, ascending=False, method="first")
        # Two 50% slots; leave an unfilled slot as cash, never lever up.
        out = (ranks <= 2).astype(float) * 0.5
    elif strategy != "cash":
        raise ValueError("Unknown strategy")
    return out


def simulate(
    open_: pd.DataFrame,
    close: pd.DataFrame,
    desired: pd.DataFrame,
    *,
    start: str,
    end: str,
    cost_bps: float = 10.0,
    rebalance: str = "monthly",
    initial: float = 100000.0,
):
    if not (
        open_.index.equals(close.index)
        and desired.index.equals(close.index)
        and open_.columns.equals(close.columns)
        and desired.columns.equals(close.columns)
    ):
        raise ValueError("Price and target axes must match")
    if not close.index.is_monotonic_increasing or close.index.has_duplicates:
        raise ValueError("Unique increasing dates required")
    arrays = [open_.to_numpy(), close.to_numpy(), desired.to_numpy()]
    if (
        any(not np.isfinite(x).all() for x in arrays)
        or (open_ <= 0).any().any()
        or (close <= 0).any().any()
    ):
        raise ValueError("Missing or invalid prices/weights")
    if (desired < 0).any().any() or (desired.sum(axis=1) > 1.00000001).any():
        raise ValueError("Only unlevered long-only targets supported")
    if (
        not np.isfinite(cost_bps)
        or not 0 <= cost_bps < 10000
        or not np.isfinite(initial)
        or initial <= 0
    ):
        raise ValueError("Invalid costs or capital")
    if rebalance not in {"monthly", "daily", "once"}:
        raise ValueError("Unknown rebalance frequency")
    ix = np.flatnonzero(
        (close.index >= pd.Timestamp(start)) & (close.index <= pd.Timestamp(end))
    )
    if not len(ix) or ix[0] == 0:
        raise ValueError("Evaluation requires at least one prior observation")
    cash, units, rows, orders = initial, np.zeros(len(close.columns)), [], []
    cost = cost_bps / 10000
    for n, i in enumerate(ix):
        date = close.index[i]
        op = open_.iloc[i].to_numpy()
        equity_open = cash + float(units @ op)
        due = (
            n == 0
            or rebalance == "daily"
            or (
                rebalance == "monthly"
                and date.to_period("M") != close.index[i - 1].to_period("M")
            )
        )
        if due:
            # Yesterday's close, including its date: no same-bar fill.
            weight = desired.iloc[i - 1].to_numpy()
            # Reserve a conservative bound on costs so cash cannot go negative.
            target_value = weight * equity_open / (1 + 2 * cost)
            delta = target_value / op - units
            # Sell first; buy with remaining settled simulated cash.
            for k in sorted(range(len(units)), key=lambda k: delta[k]):
                q = delta[k]
                if q > 0:
                    q = min(q, max(0.0, cash) / (op[k] * (1 + cost)))
                if abs(q * op[k]) < 1e-8:
                    continue
                fee = abs(q * op[k]) * cost
                cash -= q * op[k] + fee
                units[k] += q
                orders.append(
                    {
                        "date": date.date().isoformat(),
                        "ticker": close.columns[k],
                        "units": float(q),
                        "price": float(op[k]),
                        "cost": float(fee),
                        "notional": float(abs(q * op[k])),
                        "signal_date": close.index[i - 1].date().isoformat(),
                    }
                )
        nav = cash + float(units @ close.iloc[i].to_numpy())
        rows.append(
            {
                "date": date.date().isoformat(),
                "nav": nav,
                "cash": cash,
                "exposure": 1 - cash / nav,
            }
        )
    curve = pd.DataFrame(rows)
    navs = np.r_[initial, curve.nav.to_numpy()]
    returns = navs[1:] / navs[:-1] - 1
    years = (close.index[ix[-1]] - close.index[ix[0]]).days / 365.25
    sd = np.std(returns, ddof=1) if len(returns) > 1 else 0
    metrics = {
        "start": rows[0]["date"],
        "end": rows[-1]["date"],
        "sessions": len(rows),
        "total_return_pct": (navs[-1] / initial - 1) * 100,
        "cagr_pct": ((navs[-1] / initial) ** (1 / years) - 1) * 100
        if years > 0
        else None,
        "max_drawdown_pct": float(np.min(navs / np.maximum.accumulate(navs) - 1) * 100),
        "sharpe_rf_zero": float(np.mean(returns) / sd * np.sqrt(252))
        if sd > 0
        else None,
        "annualized_vol_pct": float(sd * np.sqrt(252) * 100),
        "mean_exposure_pct": float(curve.exposure.mean() * 100),
        "order_legs": len(orders),
        "cost_paid": sum(o["cost"] for o in orders),
        "cost_bps_per_side": cost_bps,
        "turnover_over_initial": sum(o["notional"] for o in orders) / initial,
    }
    return metrics, rows, orders
