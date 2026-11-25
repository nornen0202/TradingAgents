"""Multi-year after-cost and after-tax Walk-Forward Backtest for Hybrid Core+Satellite Policy."""
from __future__ import annotations

import argparse
from datetime import date, datetime, timedelta, timezone
import json
import math
from pathlib import Path
from statistics import mean, stdev
import sys
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tradingagents.execution.quant_data_bridge import evaluate_hybrid_portfolio_proposal  # noqa: E402


def _observed_quote(row, field):
    price = row.get(field)
    volume = row.get("executable_volume", row.get("volume"))
    if all(type(x) in (int, float) and math.isfinite(x) and x > 0 for x in (price, volume)):
        return price
    return None


def simulate_after_tax_walk_forward(
    bars_by_ticker: Mapping[str, Sequence[Mapping[str, Any]]],
    *,
    market: str,
    core_tickers: list[str],
    satellite_tickers: list[str],
    benchmark_ticker: str,
    rebalance_every_days: int = 21,
    fee_bps: float = 10.0,
    kr_stock_sell_tax_bps: float = 20.0,
    us_cap_gains_tax_rate: float = 0.22,
    us_annual_deduction_usd: float = 1800.0,
    decisions_by_date: Mapping[str, Mapping[str, Mapping[str, Any]]] | None = None,
    fill_timing: str = "legacy_close",
    audit_traces: dict | None = None,
    entry_study=None,
) -> dict[str, Any]:
    if fill_timing not in {"legacy_close", "same_close", "next_open"}:
        raise ValueError("Unknown fill timing")
    if entry_study is not None and (fill_timing != "next_open" or audit_traces is None or decisions_by_date):
        raise ValueError("Entry comparison requires next-open traces with its own bound evidence")
    market = market.upper()
    currency = "KRW" if market == "KR" else "USD"
    initial_capital = 10_000_000.0 if market == "KR" else 10_000.0
    all_dates = sorted(
        {
            str(row["date"])[:10]
            for rows in bars_by_ticker.values()
            for row in rows
            if isinstance(row, Mapping) and row.get("date")
        }
    )
    if len(all_dates) < 90:
        raise ValueError("At least 90 trading sessions are required for walk-forward simulation")

    price_lookup: dict[str, dict[str, float]] = {}
    observed_prices = {}
    for ticker, rows in bars_by_ticker.items():
        series: dict[str, float] = {}
        # Preserve the original first observation on duplicate dates.
        observed = {str(r.get("date"))[:10]: r for r in reversed(rows)}
        observed_prices[ticker.upper()] = observed
        last = None
        for d in all_dates:
            match = observed.get(d)
            if match is not None and float(match["close"]) > 0:
                last = float(match["close"])
            if last is not None:
                series[d] = last
        price_lookup[ticker.upper()] = series

    warmup = 70
    eval_dates = all_dates[warmup:]
    policy_base = {
        "version": f"hybrid-{market.lower()}-v1",
        "frozen_at": "2020-01-01T00:00:00+00:00",
        "currency": currency,
        "core": [t.upper() for t in core_tickers],
        "satellite": [t.upper() for t in satellite_tickers],
        "budget_core": 0.65,
        "budget_satellite": 0.30,
        "cash_floor": 0.05,
        "asset_cap": 0.65,
        "trend_window": 60,
        "momentum_window": 40,
        "volatility_window": 20,
        "annual_volatility_target": 0.22,
        "maximum_stale_days": 14,
        "minimum_turnover": 1.0,
        "satellite_limit": min(3, len(satellite_tickers)),
        "factor_weights": {"quality": 0.35, "revision": 0.30, "strength": 0.35},
        "cost_version": "after-tax-v1",
    }

    def _run_variant(mode: str) -> dict[str, Any]:
        cash = initial_capital
        shares: dict[str, float] = {}
        avg_cost: dict[str, float] = {}
        annual_realized_gain = 0.0
        current_year = eval_dates[0][:4]
        nav_curve: list[float] = []
        total_fees_and_taxes = 0.0
        trades_count = 0
        daily_fills, fills, signals, unavailable = [], [], {}, []
        pending = {}
        order_signal_day = None
        superseded = 0
        account_marks, opportunities = [], []

        def queue_close_signal(index):
            nonlocal pending, order_signal_day, superseded
            if index % rebalance_every_days:
                return
            signal_day = eval_dates[index]
            if mode == "buy_and_hold":
                if index:
                    return
                targets = {benchmark_ticker.upper(): 0.99}
            elif mode == "static_80_20":
                targets = {benchmark_ticker.upper(): 0.80}
            else:
                policy = policy_base
                decisions = {}
                if mode == "core_taa_only":
                    policy = {**policy_base, "budget_core": 0.95, "budget_satellite": 0.0}
                else:
                    decisions = (decisions_by_date or {}).get(signal_day, {})
                proposal = evaluate_hybrid_portfolio_proposal(
                    policy, bars_by_ticker, analysis_as_of=f"{signal_day}T22:00:00+00:00", decisions=decisions)
                targets = proposal["after_veto"]["weights"]
                if mode in {"quant_breakout", "quant_breakout_veto"}:
                    targets = entry_study.targets(signal_day, targets)
            superseded += len(pending)
            pending = {sym: targets.get(sym, 0.0) for sym in set(shares) | set(targets)}
            order_signal_day = signal_day
            if audit_traces is not None:
                signals[signal_day] = dict(targets)

        for step_idx, day in enumerate(eval_dates):
            cost_before = total_fees_and_taxes
            traded_notional = 0.0
            turnover = 0.0
            year = day[:4]
            if year != current_year:
                if market == "US" and annual_realized_gain > us_annual_deduction_usd:
                    tax = (annual_realized_gain - us_annual_deduction_usd) * us_cap_gains_tax_rate
                    cash -= tax
                    total_fees_and_taxes += tax
                annual_realized_gain = 0.0
                current_year = year

            if fill_timing != "next_open":
                queue_close_signal(step_idx)
            if pending:
                all_syms = sorted(pending)
                prices = {}
                for sym in set(pending) | set(shares):
                    if fill_timing == "legacy_close":
                        prices[sym] = price_lookup.get(sym, {}).get(day)
                    else:
                        row = observed_prices.get(sym, {}).get(day, {})
                        field = "open" if fill_timing == "next_open" else "close"
                        prices[sym] = _observed_quote(row, field)
                # A missing auction may carry a prior mark for sizing. It
                # cannot generate a fill or borrow the close of that day.
                previous = all_dates[warmup + step_idx - 1]
                nav = cash + sum(shares[t] * (prices[t] or price_lookup[t][previous]) for t in shares)
                targets = pending.copy()
                pending = {}
                for sym in all_syms:
                    if prices[sym] is None:
                        unavailable.append((day, sym))
                        if fill_timing == "next_open":
                            pending[sym] = targets[sym]
                # Execute sells first
                for sym in all_syms:
                    px = prices[sym]
                    if not px or px <= 0:
                        continue
                    cur_val = shares.get(sym, 0.0) * px
                    tgt_val = nav * float(targets.get(sym, 0.0))
                    diff = tgt_val - cur_val
                    if diff < -nav * 0.01 and shares.get(sym, 0.0) > 0:
                        sell_qty = min(shares[sym], abs(diff) / px)
                        gross = sell_qty * px
                        traded_notional += gross
                        is_kr_stock = market == "KR" and sym in {s.upper() for s in satellite_tickers}
                        sell_bps = fee_bps + (kr_stock_sell_tax_bps if is_kr_stock else 0.0)
                        cost = gross * (sell_bps / 10_000.0)
                        realized = (px - avg_cost.get(sym, px)) * sell_qty - cost
                        annual_realized_gain += realized
                        shares[sym] -= sell_qty
                        if shares[sym] <= 1e-9:
                            shares.pop(sym, None)
                            avg_cost.pop(sym, None)
                        cash += gross - cost
                        total_fees_and_taxes += cost
                        trades_count += 1
                        if audit_traces is not None:
                            fills.append((order_signal_day, day, sym, "sell", px))
                # Execute buys second
                for sym in all_syms:
                    px = prices[sym]
                    if not px or px <= 0:
                        continue
                    cur_val = shares.get(sym, 0.0) * px
                    tgt_val = nav * float(targets.get(sym, 0.0))
                    diff = tgt_val - cur_val
                    if diff > nav * 0.01 and cash > 0:
                        if entry_study is not None:
                            observation = entry_study.risk_at(order_signal_day, sym)
                            blocked = mode == "quant_breakout_veto" and observation in {"STOP_LOSS", "EXIT"}
                            opportunities.append((order_signal_day, day, sym, observation, blocked))
                            if blocked:
                                continue
                        spend = min(cash * 0.995, diff)
                        cost = spend * (fee_bps / 10_000.0)
                        buy_qty = max(0.0, (spend - cost) / px)
                        if buy_qty > 0:
                            prev_qty = shares.get(sym, 0.0)
                            prev_cost = avg_cost.get(sym, px)
                            shares[sym] = prev_qty + buy_qty
                            avg_cost[sym] = (prev_qty * prev_cost + buy_qty * px) / shares[sym]
                            cash -= spend
                            traded_notional += buy_qty * px
                            total_fees_and_taxes += cost
                            trades_count += 1
                            if audit_traces is not None:
                                fills.append((order_signal_day, day, sym, "buy", px))
                if entry_study is not None:
                    turnover = traded_notional / nav

            nav_eod = cash + sum(shares.get(t, 0.0) * price_lookup[t][day] for t in shares if day in price_lookup.get(t, {}))
            nav_curve.append(nav_eod)
            if fill_timing == "next_open":
                queue_close_signal(step_idx)
            if audit_traces is not None:
                daily_fills.append(trades_count)
            if entry_study is not None:
                etfs = sum(shares.get(t, 0.0) * price_lookup[t][day] for t in policy_base["core"] if t in shares)
                account_marks.append({"cash": cash, "etfs": etfs, "stocks": nav_eod - cash - etfs,
                                      "turnover": turnover, "notional": traded_notional,
                                      "cost": total_fees_and_taxes - cost_before})

        if market == "US" and annual_realized_gain > us_annual_deduction_usd:
            tax = (annual_realized_gain - us_annual_deduction_usd) * us_cap_gains_tax_rate
            nav_curve[-1] -= tax
            total_fees_and_taxes += tax
            if entry_study is not None:
                account_marks[-1]["cash"] -= tax
                account_marks[-1]["cost"] += tax

        if audit_traces is not None:
            audit_traces[mode] = {"days": eval_dates, "nav": nav_curve, "cumulative_fills": daily_fills,
                                  "signals": signals, "fills": fills, "initial_nav": initial_capital,
                                  "missing_quotes": unavailable, "superseded": superseded,
                                  "pending_at_end": sorted(pending)}
            if entry_study is not None:
                audit_traces[mode].update(account_marks=account_marks, opportunities=opportunities)
        daily_rets = [right / left - 1.0 for left, right in zip(nav_curve[:-1], nav_curve[1:]) if left > 0]
        total_ret = (nav_curve[-1] / initial_capital - 1.0) * 100.0
        years = max(len(eval_dates) / 252.0, 1e-6)
        cagr = ((nav_curve[-1] / initial_capital) ** (1.0 / years) - 1.0) * 100.0 if nav_curve[-1] > 0 else -100.0
        vol = stdev(daily_rets) * math.sqrt(252) * 100.0 if len(daily_rets) > 1 else 0.0
        sharpe = (mean(daily_rets) / stdev(daily_rets) * math.sqrt(252)) if len(daily_rets) > 1 and stdev(daily_rets) > 0 else 0.0
        peak = initial_capital
        mdd = 0.0
        for v in nav_curve:
            peak = max(peak, v)
            mdd = min(mdd, (v - peak) / peak * 100.0)
        return {
            "final_nav": round(nav_curve[-1], 2),
            "cumulative_return_pct": round(total_ret, 2),
            "cagr_pct": round(cagr, 2),
            "annual_volatility_pct": round(vol, 2),
            "sharpe": round(sharpe, 3),
            "max_drawdown_pct": round(mdd, 2),
            "trades_count": trades_count,
            "total_fees_and_taxes": round(total_fees_and_taxes, 2),
        }

    return {
        "market": market,
        "currency": currency,
        "period_start": eval_dates[0],
        "period_end": eval_dates[-1],
        "sessions": len(eval_dates),
        "strategies": {
            name: _run_variant(name)
            for name in (("buy_and_hold", "static_80_20", "hybrid_core_satellite", "quant_breakout", "quant_breakout_veto")
                         if entry_study is not None else
                         ("buy_and_hold", "static_80_20", "core_taa_only", "hybrid_core_satellite"))
        },
    }


def _fetch_yfinance_bars(tickers: list[str], start: str, end: str) -> dict[str, list[dict[str, Any]]]:
    import yfinance as yf

    out: dict[str, list[dict[str, Any]]] = {}
    end_dt = date.fromisoformat(end)
    for sym in tickers:
        df = yf.download(sym, start=start, end=(end_dt + timedelta(days=1)).isoformat(), progress=False, auto_adjust=True, threads=False)
        if df is None or df.empty:
            continue
        close = df["Close"]
        if hasattr(close, "columns"):
            close = close.iloc[:, 0]
        vol = df["Volume"] if "Volume" in df else None
        if vol is not None and hasattr(vol, "columns"):
            vol = vol.iloc[:, 0]
        rows = []
        for idx, c_val in close.dropna().items():
            d_str = str(idx)[:10]
            if d_str > end:
                continue
            v_val = float(vol.loc[idx]) if vol is not None and idx in vol.index else 1_000_000.0
            rows.append({"date": d_str, "close": float(c_val), "volume": max(1.0, v_val)})
        if rows:
            out[sym.upper()] = rows
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", default="2022-01-03")
    parser.add_argument("--end", default="2026-11-24")
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    us_syms = ["SPY", "QQQ", "AAPL", "MSFT", "NVDA", "AMZN", "META", "LLY"]
    kr_syms = ["069500.KS", "229200.KS", "005930.KS", "000660.KS", "035420.KS", "012450.KS"]
    us_bars = _fetch_yfinance_bars(us_syms, args.start, args.end)
    kr_bars = _fetch_yfinance_bars(kr_syms, args.start, args.end)

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "US": simulate_after_tax_walk_forward(
            us_bars,
            market="US",
            core_tickers=["SPY", "QQQ"],
            satellite_tickers=["AAPL", "MSFT", "NVDA", "AMZN", "META", "LLY"],
            benchmark_ticker="SPY",
        ),
        "KR": simulate_after_tax_walk_forward(
            kr_bars,
            market="KR",
            core_tickers=["069500.KS", "229200.KS"],
            satellite_tickers=["005930.KS", "000660.KS", "035420.KS", "012450.KS"],
            benchmark_ticker="069500.KS",
        ),
    }
    encoded = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
    print(encoded)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
