"""Offline integer-share cost scenarios, never an execution or tax-filing engine.

Current rates are deliberately replayed over past prices as a sensitivity study.
Dividends accrue on ex-date but remain unspendable; payment dates are unavailable.
Capital-gains tax is a KRW liability reserved from buying power, not a tax payment.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import math

import numpy as np
import pandas as pd

from .account_strategy_research import STRATEGIES, open_signals, validate_prices


@dataclass(frozen=True)
class CostScenario:
    commission_rate: float
    sell_levy_rate: float = 0.0
    fx_base_spread: float = 0.0
    fx_discount: float = 0.0
    slippage_rate: float = 0.0
    dividend_withholding: float = 0.0
    capital_gains_rate: float = 0.0
    annual_allowance_krw: float = 0.0

    def __post_init__(self):
        for name, value in asdict(self).items():
            if not math.isfinite(value) or value < 0:
                raise ValueError(f"Invalid {name}")
            if name != "annual_allowance_krw" and value >= 1:
                # A 100% discount is a valid zero-spread scenario.
                if name != "fx_discount" or value != 1:
                    raise ValueError(f"Invalid {name}")
        if self.commission_rate + self.sell_levy_rate >= 1:
            raise ValueError("Total sell costs must be below proceeds")

    @property
    def fx_spread(self):
        return self.fx_base_spread * (1 - self.fx_discount)

    def fees(self, notional: float, side: str) -> tuple[float, float]:
        if side not in {"BUY", "SELL"} or not math.isfinite(notional) or notional < 0:
            raise ValueError("Invalid trade")
        return (
            notional * self.commission_rate,
            notional * self.sell_levy_rate if side == "SELL" else 0.0,
        )


def round_trip_loss(scenario: CostScenario, *, convert_currency: bool) -> float:
    """Flat-price proportional loss, excluding capital gains and rounding."""
    remaining = (1 - scenario.commission_rate - scenario.sell_levy_rate) / (
        1 + scenario.commission_rate
    )
    remaining *= (1 - scenario.slippage_rate) / (1 + scenario.slippage_rate)
    if convert_currency:
        remaining *= (1 - scenario.fx_spread) / (1 + scenario.fx_spread)
    return 1 - remaining


def annual_tax(realized: dict[int, float], scenario: CostScenario) -> float:
    return sum(
        max(0.0, amount - scenario.annual_allowance_krw) * scenario.capital_gains_rate
        for amount in realized.values()
    )


def _fx_series(fx: pd.Series, dates: pd.DatetimeIndex, *, prior: bool):
    if (
        not isinstance(fx.index, pd.DatetimeIndex)
        or fx.index.tz is not None
        or not fx.index.is_monotonic_increasing
        or fx.index.has_duplicates
        or fx.index.hasnans
        or not fx.index.equals(fx.index.normalize())
        or not np.isfinite(fx.to_numpy(dtype=float)).all()
        or (fx <= 0).any()
    ):
        raise ValueError("Invalid FX observations")
    lookup = dates - pd.Timedelta(days=1) if prior else dates
    locs = fx.index.get_indexer(lookup, method="pad")
    if (locs < 0).any():
        raise ValueError("FX history missing; future observations cannot fill it")
    if ((dates - fx.index[locs]) > pd.Timedelta(days=5)).any():
        raise ValueError("FX observations older than five calendar days")
    return fx.iloc[locs].to_numpy(dtype=float)


def simulate_account(
    prices: pd.DataFrame,
    strategy: str,
    *,
    start: str,
    end: str,
    initial_krw: float,
    scenario: CostScenario,
    fx_krw_per_unit: pd.Series,
    price_basis: str,
    execution_delay_sessions: int = 0,
    liquidate_at_end: bool = True,
):
    """All-cash, account-sized scenario; no reconstruction of existing tax lots.

    Raw prices must have no splits in the supplied interval. Adj Close is used
    only for signals. Tax lots use FIFO and prior-day FX as a research proxy.
    Liability is recomputed within a year (loss offsets), never across years.
    Real tax settlement FX, other accounts, personal exemptions and rounding
    are not inferred. All remaining shares are sold at final close if requested.
    """
    validate_prices(prices)
    if price_basis != "unadjusted_no_splits":
        raise ValueError("Integer shares require declared unadjusted prices")
    if not {"Adj Close", "Dividends", "Stock Splits"}.issubset(prices.columns):
        raise ValueError("Adjusted signal close, dividends and split data required")
    values = prices[["Adj Close", "Dividends", "Stock Splits"]].to_numpy(dtype=float)
    if not np.isfinite(values).all() or (prices["Adj Close"] <= 0).any():
        raise ValueError("Invalid adjusted prices or corporate actions")
    if (prices["Dividends"] < 0).any() or prices["Stock Splits"].ne(0).any():
        raise ValueError("Negative dividends or stock splits require another ledger")
    if "Capital Gains" in prices and prices["Capital Gains"].ne(0).any():
        raise ValueError("Capital-gain distributions are unsupported")
    if strategy not in STRATEGIES or not math.isfinite(initial_krw) or initial_krw <= 0:
        raise ValueError("Invalid strategy or initial capital")
    if isinstance(execution_delay_sessions, bool) or execution_delay_sessions not in (
        0,
        1,
    ):
        raise ValueError("Invalid execution delay")
    ix = np.flatnonzero(
        (prices.index >= pd.Timestamp(start)) & (prices.index <= pd.Timestamp(end))
    )
    if not len(ix) or ix[0] == 0:
        raise ValueError("Evaluation requires a preceding observation")
    dates = prices.index[ix]
    fx_open = _fx_series(fx_krw_per_unit, dates, prior=True)
    fx_close = _fx_series(fx_krw_per_unit, dates, prior=False)
    signal_prices = prices[["Open", "Close"]].copy()
    signal_prices["Close"] = prices["Adj Close"]
    signals = open_signals(signal_prices, strategy)
    cash = initial_krw / (fx_open[0] * (1 + scenario.fx_spread))
    initial_local = cash
    entry_fx_cost = initial_krw - cash * fx_open[0]
    shares, dividend_receivable = 0, 0.0
    lots, trades, curve, pending = [], [], [], []
    realized: dict[int, float] = {}

    def transact(delta, price, fx_rate, date, signal_date, reason):
        nonlocal cash, shares
        if not delta:
            return
        side = "BUY" if delta > 0 else "SELL"
        execution_price = price * (
            1 + scenario.slippage_rate * (1 if delta > 0 else -1)
        )
        notional = abs(delta) * execution_price
        commission, levy = scenario.fees(notional, side)
        if delta > 0:
            cash -= notional + commission
            lots.append([delta, (notional + commission) * fx_rate / delta])
        else:
            remaining, basis = -delta, 0.0
            while remaining:
                take = min(remaining, lots[0][0])
                basis += take * lots[0][1]
                lots[0][0] -= take
                remaining -= take
                if not lots[0][0]:
                    lots.pop(0)
            proceeds = notional - commission - levy
            cash += proceeds
            realized[date.year] = (
                realized.get(date.year, 0.0) + proceeds * fx_rate - basis
            )
        shares += delta
        if cash < -1e-7 or shares < 0:
            raise AssertionError("Cash borrowing and shorting are forbidden")
        cash = max(0.0, cash)
        trades.append(
            {
                "date": str(date.date()),
                "signal_date": signal_date,
                "reason": reason,
                "side": side,
                "quantity": abs(delta),
                "price": execution_price,
                "notional": notional,
                "commission": commission,
                "sell_levy": levy,
                "slippage_cost_krw": abs(delta)
                * price
                * scenario.slippage_rate
                * fx_rate,
                "cost_krw": (commission + levy) * fx_rate,
            }
        )

    for n, i in enumerate(ix):
        date, previous = prices.index[i], prices.index[i - 1]
        # Entitlement belongs to shares held before the ex-date open.
        dividend_receivable += (
            shares
            * float(prices.Dividends.iloc[i])
            * (1 - scenario.dividend_withholding)
        )
        due = n == 0
        if strategy == "balanced_80_20":
            due |= date.to_period("Q") != previous.to_period("Q")
        elif strategy in {"monthly_trend", "trend_vol_cap"}:
            due |= date.to_period("M") != previous.to_period("M")
        if due:
            signal = signals.iloc[i]
            if (
                not signal.ready
                or pd.isna(signal.signal_date)
                or signal.signal_date >= date
            ):
                raise ValueError("Signal warmup or timing invalid")
            previous_value = shares * float(prices.Close.iloc[i - 1])
            # Use information available before this open to decide the band.
            previous_nav = (
                cash
                + previous_value
                + dividend_receivable
                - annual_tax(realized, scenario) / fx_open[n]
            )
            previous_weight = previous_value / previous_nav if previous_nav > 0 else 0.0
            if (
                strategy != "balanced_80_20"
                or n == 0
                or abs(previous_weight - 0.8) >= 0.05
            ):
                pending.append(
                    (
                        i + execution_delay_sessions,
                        float(signal.weight),
                        str(signal.signal_date.date()),
                    )
                )
        op = float(prices.Open.iloc[i])
        for execution_index, weight, signal_date in pending:
            if execution_index != i:
                continue
            reserve = annual_tax(realized, scenario) / fx_open[n]
            equity = cash + shares * op + dividend_receivable - reserve
            target = max(0, math.floor(weight * equity / op))
            delta = target - shares
            if delta > 0:
                per_share = (
                    op * (1 + scenario.slippage_rate) * (1 + scenario.commission_rate)
                )
                delta = min(delta, max(0, math.floor((cash - reserve) / per_share)))
            transact(delta, op, fx_open[n], date, signal_date, "scheduled_rebalance")
        pending = [p for p in pending if p[0] > i]
        cl = float(prices.Close.iloc[i])
        if n == len(ix) - 1 and liquidate_at_end:
            transact(
                -shares,
                cl,
                fx_close[n],
                date,
                None,
                "hypothetical_terminal_liquidation",
            )
        tax = annual_tax(realized, scenario)
        gross_nav = (cash + shares * cl + dividend_receivable) * fx_close[n]
        net_nav = gross_nav - tax
        exit_fx_cost = 0.0
        if n == len(ix) - 1 and liquidate_at_end:
            exit_fx_cost = gross_nav * scenario.fx_spread
            net_nav -= exit_fx_cost
        curve.append(
            {
                "date": str(date.date()),
                "nav_krw": net_nav,
                "cash_local": cash,
                "shares": shares,
                "dividend_receivable_local": dividend_receivable,
                "tax_reserve_krw": tax,
                "fx": fx_close[n],
                "exit_fx_cost_krw": exit_fx_cost,
                "tax_cash_shortfall_krw": max(0.0, tax - cash * fx_close[n]),
            }
        )
    navs = np.r_[initial_krw, [r["nav_krw"] for r in curve]]
    metrics = {
        "strategy": strategy,
        "initial_krw": initial_krw,
        "final_krw": float(navs[-1]),
        "total_return_pct": float((navs[-1] / initial_krw - 1) * 100),
        "max_drawdown_pct": float((navs / np.maximum.accumulate(navs) - 1).min() * 100),
        "trades": len(trades),
        "trading_cost_krw": sum(t["cost_krw"] for t in trades),
        "entry_fx_cost_krw": entry_fx_cost,
        "exit_fx_cost_krw": curve[-1]["exit_fx_cost_krw"],
        "slippage_cost_krw": sum(t["slippage_cost_krw"] for t in trades),
        "local_return_before_capital_gains_tax_pct": (
            (cash + shares * float(prices.Close.iloc[ix[-1]]) + dividend_receivable)
            / initial_local
            - 1
        )
        * 100,
        "fx_change_pct": (fx_close[-1] / fx_open[0] - 1) * 100,
        "tax_reserve_krw": curve[-1]["tax_reserve_krw"],
        "realized_by_year_krw": realized,
        "dividends_net_local": dividend_receivable,
        "max_tax_cash_shortfall_krw": max(r["tax_cash_shortfall_krw"] for r in curve),
        "start": str(dates[0].date()),
        "end": str(dates[-1].date()),
        "execution_delay_sessions": execution_delay_sessions,
        "scenario": asdict(scenario),
        "terminal_liquidation": liquidate_at_end,
    }
    return metrics, curve, trades
