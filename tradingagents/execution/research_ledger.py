"""Next-open integer-share ledger for the paired KRW research portfolios."""
from bisect import bisect_right
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, timedelta
import math

from .account_cost_replay import CostScenario, annual_tax

INITIAL_NAV = 100_000_000
CORE_WEIGHTS = {"US": .8, "KR": .2}
COMMISSION = {"KR": .001, "US": .001}
SLIPPAGE = {"KR": .001, "US": .001}
WITHHOLDING = {"KR": .154, "US": .15}
FX_SPREAD = .001
GAINS = CostScenario(commission_rate=0, capital_gains_rate=.22, annual_allowance_krw=2_500_000)
_KOSPI_LEVY = {2020: .0025, 2021: .0023, 2022: .0023, 2023: .002, 2024: .0018, 2025: .0015, 2026: .002}
BENCHMARKS = {"US": "SPY", "KR": "069500.KS"}


@dataclass
class Position:
    units: int = 0
    basis: float = 0.0
    close: float = 0.0


def actual_shares(rows):
    """Undo Yahoo split scaling for the executable share ledger."""
    scale = 1.0
    result = {}
    for day, row in sorted(rows.items(), reverse=True):
        prices = [row.get(field) for field in ("Open", "High", "Low", "Close")]
        actions = [row.get(field) for field in ("Dividends", "Stock Splits", "Capital Gains")]
        volume = row.get("Volume")
        if (any(type(x) not in (float, int) or not math.isfinite(x) or x <= 0 for x in prices)
                or any(type(x) not in (float, int) or not math.isfinite(x) or x < 0 for x in (*actions, volume))
                or prices[2] > min(prices[0], prices[3]) or prices[1] < max(prices[0], prices[3])):
            continue
        dividend, split, distribution = actions
        result[day] = {"open": prices[0] * scale, "close": prices[3] * scale,
                       "dividend": (dividend + distribution) * scale, "split": split or 1,
                       "turnover": prices[3] * volume}
        scale *= split or 1
    return result


class RateHistory:
    def __init__(self, raw):
        self.rows = sorted((date.fromisoformat(day) + timedelta(days=2), row["Close"])
                           for day, row in raw.items()
                           if type(row.get("Close")) in (float, int) and 0 < row["Close"] < 10000)
        self.days = [day for day, _ in self.rows]

    def at(self, instant):
        today = instant.date()  # UTC event clock
        pos = bisect_right(self.days, today) - 1
        if pos < 0 or (today - self.days[pos]).days > 6:
            raise ValueError(f"Unverified USD/KRW marking rate on {today}.")
        return self.rows[pos][1]


class Ledger:
    def __init__(self, asset_markets):
        self.cash = INITIAL_NAV
        self.receivables = defaultdict(float)
        self.asset_markets = asset_markets
        self.positions = {symbol: Position() for symbol in asset_markets}
        self.realized = defaultdict(float)
        self.costs = dict.fromkeys(("commission", "slippage", "sell_levy", "fx_cost", "dividend_tax"), 0.0)
        self.fills = []
        self.actions = []

    @property
    def reserve(self):
        return annual_tax(self.realized, GAINS)

    def nav(self, fx):
        invested = sum(p.units * p.close * (fx if self.asset_markets[symbol] == "US" else 1)
                       for symbol, p in self.positions.items())
        value = self.cash + self.receivables["KR"] + self.receivables["US"] * fx + invested - self.reserve
        return value, invested

    def corporate_action(self, symbol, bar, instant, fx):
        position = self.positions[symbol]
        if not position.units or bar["split"] == 1 and not bar["dividend"]:
            return
        market = self.asset_markets[symbol]
        rate = fx if market == "US" else 1
        result = position.units * bar["split"]
        units = math.floor(result + 1e-9)
        if not math.isclose(result, units, rel_tol=0, abs_tol=1e-8):
            raise ValueError(f"{symbol} split lacks a verified fractional cash settlement.")
        position.units = units
        gross = units * bar["dividend"]
        withheld = gross * WITHHOLDING[market]
        self.receivables[market] += gross - withheld
        self.costs["dividend_tax"] += withheld * rate
        self.actions.append({"time": instant.isoformat(), "symbol": symbol, "split": bar["split"],
                             "ex_date_dividend_local": gross, "withholding_local": withheld,
                             "units_after": units, "cash_available_from_dividend": False})

    def _fill(self, symbol, units, opening, instant, day, fx):
        market = self.asset_markets[symbol]
        rate, spread = (fx, FX_SPREAD) if market == "US" else (1.0, 0.0)
        commission, slippage = COMMISSION[market], SLIPPAGE[market]
        levy = _KOSPI_LEVY[day.year] if market == "KR" and symbol != BENCHMARKS["KR"] else 0.0
        position = self.positions[symbol]
        buying = units > 0
        execution = opening * (1 + slippage if buying else 1 - slippage)
        notional_local = execution * abs(units)
        fee_local = notional_local * commission
        levy_local = 0.0 if buying else notional_local * levy
        local_debit = notional_local + fee_local if buying else -(notional_local - fee_local - levy_local)
        fx_cost = abs(local_debit) * rate * spread
        debit = local_debit * rate + fx_cost
        if buying:
            position.basis += debit
        else:
            sold_basis = position.basis * (-units) / position.units
            position.basis -= sold_basis
            if market == "US":
                self.realized[day.year] -= debit + sold_basis
        position.units += units
        self.cash -= debit
        fees = {"commission": fee_local * rate, "slippage": abs(opening - execution) * abs(units) * rate,
                "fx_cost": fx_cost, "sell_levy": levy_local * rate}
        for name, value in fees.items():
            self.costs[name] += value
        self.fills.append({"time": instant.isoformat(), "market_session": day.isoformat(), "symbol": symbol,
                           "units": units, "opening_price_local": opening, "fill_price_local": execution,
                           "fx": rate, "debit_krw": debit, "cash_krw": self.cash, "reserve_krw": self.reserve,
                           **fees})

    def rebalance(self, market, opening_bars, weights, instant, day, fx):
        rate = fx if market == "US" else 1.0
        delta = {}
        nav = self.nav(fx)[0]
        for symbol, opening in opening_bars.items():
            position = self.positions[symbol]
            desired = math.floor(max(0, nav) * weights.get(symbol, 0) / (opening * rate))
            delta[symbol] = desired - position.units
        # Sell first. Orders on the other national exchange use its own open
        # and cannot finance purchases before that exchange opens.
        for symbol, units in sorted(delta.items(), key=lambda entry: (entry[1] >= 0, entry[0])):
            opening = opening_bars[symbol]
            if units > 0:
                spread = FX_SPREAD if market == "US" else 0
                unit_cost = opening * rate * (1 + COMMISSION[market]) * (1 + SLIPPAGE[market]) * (1 + spread)
                units = min(units, math.floor(max(0.0, self.cash - self.reserve) / unit_cost))
            if units:
                self._fill(symbol, units, opening, instant, day, fx)

    def observe(self, day, instant, fx):
        nav, invested = self.nav(fx)
        if not math.isfinite(nav) or nav <= 0:
            raise ValueError("Nonpositive account value.")
        return {"day": day, "time": instant.isoformat(), "nav": nav, "invested": invested,
                "cash": self.cash, "dividend_receivable": self.receivables["KR"] + self.receivables["US"] * fx,
                "capital_gains_reserve": self.reserve, "fx": fx, "external_cashflow": 0,
                "fill_count": len(self.fills), **self.costs}


def market_events(sessions, start, end):
    events = []
    for market, days in sessions.items():
        for day, (opening, close) in days.items():
            if start <= day <= end:
                events.extend(((opening, day, market, True), (close, day, market, False)))
    events.sort()
    last_marks = {day: instant for instant, day, _, opening in events if not opening}
    return events, last_marks


def replay(sessions, bars, fx, schedule, asset_markets, start, end):
    """Value all arms on the same union of local closing-session dates."""
    accounts = {arm: Ledger(mapping) for arm, mapping in asset_markets.items()}
    curves = {arm: [] for arm in accounts}
    events, last_marks = market_events(sessions, start, end)
    gaps = defaultdict(set)
    last_prices = {symbol: max(panel, default="") for symbol, panel in bars.items()}
    for instant, day, market, opening in events:
        exchange_rate = fx.at(instant)
        for arm, account in accounts.items():
            prices = {}
            for symbol, position in account.positions.items():
                if account.asset_markets[symbol] != market:
                    continue
                bar = bars[symbol].get(day)
                if bar is None:
                    if position.units:
                        if day > last_prices[symbol]:
                            raise ValueError(f"{symbol} has no verified terminal price or delisting settlement on {day}.")
                        gaps[arm].add(f"{symbol}:{day}")
                    continue
                if opening:
                    account.corporate_action(symbol, bar, instant, exchange_rate)
                current = bar["open" if opening else "close"]
                prices[symbol] = position.close = current
            targets = schedule.get(arm, {}).get((market, day))
            if opening and targets is not None:
                account.rebalance(market, prices, targets, instant, date.fromisoformat(day), exchange_rate)
            if not opening and instant == last_marks[day]:
                curves[arm].append(account.observe(day, instant, exchange_rate))
    return curves, accounts, {key: sorted(values) for key, values in gaps.items()}
