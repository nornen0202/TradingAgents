"""Point-in-time evaluation of a decision's direction and new cash exposure."""
from __future__ import annotations

from collections import Counter
from datetime import date, datetime, time, timedelta
import math
from zoneinfo import ZoneInfo

import pandas as pd

from tradingagents.calendar_access import get_exchange_calendar
from tradingagents.dataflows.integrity import session_date
from tradingagents.scheduled.market_calendar import default_calendar_name, is_supplemental_market_holiday

DIRECTION = {"BUY": 1, "OVERWEIGHT": 1, "SELL": -1, "UNDERWEIGHT": -1}
EXPOSURE = {"BUY": 1.0, "OVERWEIGHT": .5, "HOLD": 0.0, "SELL": 0.0, "UNDERWEIGHT": 0.0, "NO_TRADE": 0.0}
SCHEMA = "tradingagents.dual-decision-scores/v1"
_ZONES = {"KR": "Asia/Seoul", "US": "America/New_York"}


def evaluation_sessions(market, day, count):
    start = date.fromisoformat(day) + timedelta(days=1)
    end = start + timedelta(days=max(14, count * 4))
    calendar = get_exchange_calendar(default_calendar_name(market))
    sessions = [
        (label.date().isoformat(), calendar.session_open(label).to_pydatetime(),
         calendar.session_close(label).to_pydatetime())
        for label in calendar.sessions_in_range(start.isoformat(), end.isoformat())
        if not is_supplemental_market_holiday(market=market, session_date=label.date())
    ]
    if len(sessions) < count:
        raise ValueError("Insufficient verified exchange sessions")
    return sessions[:count]


def yahoo_bars(symbol, first, last):
    import yfinance as yf
    end = (date.fromisoformat(last) + timedelta(days=1)).isoformat()
    return yf.Ticker(symbol).history(start=first, end=end, auto_adjust=True, raise_errors=True)


def daily_bar_available_at(market, last_session, exchange_close):
    """Yahoo's same-local-day record may still contain the live price."""
    next_date = date.fromisoformat(last_session) + timedelta(days=1)
    next_midnight = datetime.combine(next_date, time.min, tzinfo=ZoneInfo(_ZONES[market]))
    return max(exchange_close, next_midnight)


def _price(bars, label, column):
    if not isinstance(bars, pd.DataFrame) or column not in bars or bars.empty:
        return None
    indices = [i for i, stamp in enumerate(bars.index) if session_date(stamp) == pd.Timestamp(label)]
    if len(indices) != 1:
        return None
    try:
        value = float(bars[column].iloc[indices[0]])
    except (ValueError, TypeError, OverflowError):
        return None
    return value if math.isfinite(value) and value > 0 else None


def _asset_return(frame, first, last, column):
    initial, final = _price(frame, first, column), _price(frame, last, "Close")
    return None if initial is None or final is None else (final - initial) / initial


def score_decision(*, ticker, market, decision_date, rating, benchmark, holding, fee_bps, as_of,
                   provider=yahoo_bars, sessions=evaluation_sessions):
    if rating == "REVIEW" or rating not in EXPOSURE:
        return {"direction": {"status": "REVIEW"}, "new_exposure": {"status": "REVIEW"}}
    if as_of.tzinfo is None or as_of.utcoffset() is None:
        raise ValueError("Settlement cutoff must be timezone-aware")
    slots = sessions(market, decision_date, holding + 1)
    entry, entry_open, entry_close = slots[0]
    fork_exit, _, fork_close = slots[holding - 1]
    original_exit, _, original_close = slots[holding]

    original_available = daily_bar_available_at(market, original_exit, original_close)
    fork_available = daily_bar_available_at(market, fork_exit, fork_close)
    direction = {"status": "PENDING", "entry_session": entry, "exit_session": original_exit,
                 "entry_at": entry_close.isoformat(), "exit_close_at": original_close.isoformat(),
                 "matures_at": original_available.isoformat()}
    exposure = EXPOSURE[rating]
    fork = {"status": "PENDING", "entry_session": entry, "exit_session": fork_exit,
            "entry_at": entry_open.isoformat(), "exit_close_at": fork_close.isoformat(),
            "matures_at": fork_available.isoformat(), "weight": exposure}
    if not DIRECTION.get(rating):
        direction["status"] = "NO_DIRECTION"
    if not exposure:
        fork["status"] = "NO_NEW_EXPOSURE"

    settle_direction = direction["status"] == "PENDING" and as_of >= original_available
    settle_fork = fork["status"] == "PENDING" and as_of >= fork_available
    if not (settle_direction or settle_fork):
        return {"direction": direction, "new_exposure": fork}
    end = original_exit if settle_direction else fork_exit

    try:
        asset = provider(ticker, entry, end)
    except (OSError, RuntimeError, ValueError, TypeError, KeyError) as exc:
        for active, result in ((settle_direction, direction), (settle_fork, fork)):
            if active:
                result.update(status="ASSET_PROVIDER_FAILURE", error_type=type(exc).__name__)
        return {"direction": direction, "new_exposure": fork}

    if settle_fork:
        raw = _asset_return(asset, entry, fork_exit, "Open")
        if raw is None:
            fork["status"] = "ASSET_PRICE_MISSING"
        else:
            # Preserve the existing fork's one independent, costed cash episode.
            cost = 2 * exposure * fee_bps / 10_000
            net = exposure * raw - cost
            fork.update(status="SCORED", asset_return=raw, strategy_return=net,
                        transaction_cost=cost, hit=net > 0, benchmark_status="PENDING")
            try:
                base = _asset_return(provider(benchmark, entry, fork_exit), entry, fork_exit, "Open")
            except (OSError, RuntimeError, ValueError, TypeError, KeyError) as exc:
                fork.update(benchmark_status="BENCHMARK_PROVIDER_FAILURE", benchmark_error_type=type(exc).__name__)
            else:
                if base is None:
                    fork["benchmark_status"] = "BENCHMARK_PRICE_MISSING"
                else:
                    benchmark_net = base - 2 * fee_bps / 10_000
                    fork.update(benchmark_status="AVAILABLE", benchmark_return=benchmark_net,
                                excess_return=net - benchmark_net)

    if settle_direction:
        raw = _asset_return(asset, entry, original_exit, "Close")
        if raw is None:
            direction["status"] = "ASSET_PRICE_MISSING"
        else:
            try:
                base = _asset_return(provider(benchmark, entry, original_exit), entry, original_exit, "Close")
            except (OSError, RuntimeError, ValueError, TypeError, KeyError) as exc:
                direction.update(status="BENCHMARK_PROVIDER_FAILURE", error_type=type(exc).__name__)
            else:
                if base is None:
                    direction["status"] = "BENCHMARK_PRICE_MISSING"
                else:
                    # Tauric memory persists one decimal percentage before scoring.
                    logged = f"{raw-base:+.1%}"
                    alpha = float(logged.rstrip("%")) / 100
                    direction.update(status="SCORED", asset_return=raw, benchmark_return=base,
                                     alpha=alpha, alpha_logged=logged, hit=alpha * DIRECTION[rating] > 0)
    return {"direction": direction, "new_exposure": fork}


def aggregate(rows, key):
    statuses = Counter(row[key]["status"] for row in rows)
    scored = [row for row in rows if row[key]["status"] == "SCORED"]
    hits = sum(row[key]["hit"] for row in scored)
    miss_benchmark = Counter(row[key]["benchmark_status"] for row in scored if "benchmark_status" in row[key])
    return {"target": len(rows), "hits": hits, "scored": len(scored),
            "hit_rate": hits / len(scored) if scored else None, "statuses": dict(statuses),
            "benchmark_statuses_for_scored": dict(miss_benchmark)}
