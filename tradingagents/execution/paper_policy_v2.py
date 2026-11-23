"""Size versioned, isolated paper candidates in one verified market currency."""

from __future__ import annotations

import argparse
from datetime import timedelta
from decimal import Decimal, InvalidOperation, ROUND_DOWN
from hashlib import sha256
import json
from pathlib import Path
import re
import sqlite3

from .experiments import _stamp


SCHEMA = "tradingagents.paper-policy/v2"
_CURRENCY = {"KR": "KRW", "US": "USD"}
_BUY = frozenset({"STARTER_NOW", "ADD_NOW", "BUY_NOW"})
_REDUCTION = frozenset({"REDUCE_NOW", "EXIT_NOW", "TAKE_PROFIT_NOW", "TRIM_NOW", "STOP_LOSS_NOW"})


def _decimal(value):
    if isinstance(value, bool):
        raise ValueError("Price or quantity must be numeric")
    try:
        number = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError("Invalid native amount") from exc
    if not number.is_finite() or number < 0:
        raise ValueError("Expected a finite nonnegative native amount")
    return number


def _hash(payload):
    return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def _fresh(value, *, now, seconds):
    try:
        return timedelta() <= now - _stamp(value) <= timedelta(seconds=seconds)
    except (TypeError, ValueError):
        return False


def _policy_terms(policy, watchlist, now):
    keys = {"schema", "version", "scope", "broker", "market", "currency", "frozen_at", "cash_reserve_fraction",
            "max_order_fraction", "max_position_fraction", "max_sale_fraction", "fee_bps", "drift_band_fraction",
            "max_quote_age_seconds"}
    if not isinstance(policy, dict) or set(policy) != keys or policy["schema"] != SCHEMA:
        raise ValueError("Versioned V2 paper policy required")
    market = policy["market"]
    if (not isinstance(market, str) or market not in _CURRENCY or _CURRENCY[market] != policy["currency"]
            or any(not isinstance(policy[key], str) or not policy[key].strip() for key in ("version", "scope"))
            or policy["broker"] not in {"local", "kis_vts", "alpaca_paper"}
            or (policy["broker"] == "alpaca_paper" and market != "US")
            or not _stamp(policy["frozen_at"]) <= now
            or type(policy["max_quote_age_seconds"]) is not int or not 1 <= policy["max_quote_age_seconds"] <= 120):
        raise ValueError("Policy must bind an isolated broker, market, currency and clock")
    fraction_keys = ("cash_reserve_fraction", "max_order_fraction", "max_position_fraction",
                     "max_sale_fraction", "drift_band_fraction")
    fractions = {key: _decimal(policy[key]) for key in fraction_keys}
    if (any(value > 1 for value in fractions.values()) or not fractions["max_position_fraction"]
            or not fractions["max_order_fraction"] or not fractions["max_sale_fraction"]
            or _decimal(policy["fee_bps"]) >= 10000):
        raise ValueError("Policy has invalid concentration or cost bounds")
    if (not isinstance(watchlist, dict) or set(watchlist) != {"version", "market", "known_at", "tickers"}
            or not isinstance(watchlist["version"], str) or not watchlist["version"]
            or watchlist["market"] != market or _stamp(watchlist["known_at"]) > now
            or not isinstance(watchlist["tickers"], list)
            or not all(isinstance(key, str) and re.fullmatch(r"[A-Z0-9.-]{1,16}", key) for key in watchlist["tickers"])
            or len(watchlist["tickers"]) != len(set(watchlist["tickers"]))):
        raise ValueError("Watchlist version or scope is invalid")
    return fractions


def size_v2_candidate(policy, watchlist, account, signal, quote, *, as_of):
    """Return a reducing or adding paper candidate, with no order authority."""
    now = _stamp(as_of)
    fractions = _policy_terms(policy, watchlist, now)
    identity = {"policy_sha256": _hash(policy), "watchlist_sha256": _hash(watchlist),
                "policy_version": policy["version"], "watchlist_version": watchlist["version"],
                "mode": "isolated_paper", "live_order_authority": False}
    code = signal.get("action_now") if isinstance(signal, dict) else None
    if not isinstance(code, str) or (code not in _BUY and code not in _REDUCTION):
        return identity | {"status": "NO_CURRENT_STRATEGY_ACTION"}
    side = "BUY" if code in _BUY else "SELL"
    outputs = identity | {"side": side}
    try:
        ticker = signal["ticker"]
        if not isinstance(ticker, str) or not re.fullmatch(r"[A-Z0-9.-]{1,16}", ticker):
            return outputs | {"status": "UNVERIFIED_CANDIDATE_TICKER"}
        for payload in (account, signal, quote):
            if any(payload.get(field) != policy[field] for field in ("scope", "currency", "market")):
                return outputs | {"status": "SCOPE_MISMATCH"}
        seconds = policy["max_quote_age_seconds"]
        if (account.get("mode") != "isolated_paper" or account.get("reconciled") is not True
                or account.get("settlement_verified") is not True
                or not _fresh(account.get("observed_at"), now=now, seconds=seconds)
                or signal.get("execution_ready") is not True or not _fresh(signal.get("observed_at"), now=now, seconds=seconds)
                or quote.get("ticker") != ticker or not _fresh(quote.get("observed_at"), now=now, seconds=seconds)
                or quote.get("regular_executable") is not True):
            return outputs | {"status": "STALE_OR_UNRECONCILED_EVIDENCE"}
        if side == "BUY" and (ticker not in watchlist["tickers"] or account.get("portfolio_complete") is not True
                               or account.get("benchmark_fresh") is not True):
            return outputs | {"status": "BUY_COVERAGE_OR_WATCHLIST_BLOCKED"}
        if side == "SELL" and signal.get("verified_risk_reduction") is not True:
            return outputs | {"status": "SELL_RISK_REDUCTION_UNVERIFIED"}
        nav, target, requested = (_decimal(account["nav"]), _decimal(signal["target_weight"]), _decimal(signal["quantity"]))
        price = _decimal(quote["ask"] if side == "BUY" else quote["bid"])
        if not nav or not price or not requested or target > 1:
            return outputs | {"status": "INVALID_NATIVE_INPUT"}
        holding = account["positions"].get(ticker, {"owned": 0, "sellable": 0, "pending_sell": 0})
        owned, sellable, pending_sell = (_decimal(holding[key]) for key in ("owned", "sellable", "pending_sell"))
        if pending_sell > sellable or sellable > owned:
            return outputs | {"status": "INCONSISTENT_INVENTORY"}
        current_notional = owned * price
        if side == "BUY":
            settled, reserved = (_decimal(account[key]) for key in ("settled_cash", "pending_buy_notional"))
            symbol_reserve = _decimal(account["pending_buys_by_ticker"].get(ticker, 0))
            if symbol_reserve > reserved:
                return outputs | {"status": "INCONSISTENT_CASH_RESERVATIONS"}
            current_weight = (current_notional + symbol_reserve) / nav
            if target - current_weight <= fractions["drift_band_fraction"]:
                return outputs | {"status": "WITHIN_DRIFT_BAND"}
            budget = min(nav * fractions["max_order_fraction"],
                         settled - reserved - nav * fractions["cash_reserve_fraction"],
                         nav * min(target, fractions["max_position_fraction"]) - current_notional - symbol_reserve)
            per_unit = price * (1 + _decimal(policy["fee_bps"]) / 10000)
            allowed = min(requested, max(Decimal(0), budget) / per_unit)
        else:
            allowed = min(requested, sellable - pending_sell, nav * fractions["max_sale_fraction"] / price)
        if policy["broker"] == "alpaca_paper" and quote.get("fractionable") is True:
            if not _fresh(quote.get("asset_observed_at"), now=now, seconds=seconds):
                return outputs | {"status": "UNVERIFIED_FRACTIONAL_ASSET"}
            step = _decimal(quote["fractional_quantity_step"])
            if not Decimal("0.000000001") <= step <= 1:
                return outputs | {"status": "INVALID_BROKER_QUANTITY_STEP"}
        else:
            step = Decimal(1)
        quantity = (allowed / step).to_integral_value(rounding=ROUND_DOWN) * step
        if quantity <= 0:
            return outputs | {"status": "NO_ELIGIBLE_LOT"}
        return outputs | {"status": "PAPER_CANDIDATE", "quantity": str(quantity), "currency": policy["currency"],
                          "ticker": ticker, "maximum_price": str(price) if side == "BUY" else None}
    except (AttributeError, KeyError, TypeError, ValueError, InvalidOperation, OverflowError):
        return outputs | {"status": "INVALID_NATIVE_INPUT"}


def bind_v2_journal(state_root, policy, watchlist, *, as_of):
    """Keep one V2 account lane and reject ambiguous concurrent policy changes."""
    now = _stamp(as_of)
    _policy_terms(policy, watchlist, now)
    key = _hash({"scope": policy["scope"], "market": policy["market"], "broker": policy["broker"]})
    journal = Path(state_root) / "paper-v2" / key / "policy.sqlite"
    journal.parent.mkdir(parents=True, exist_ok=True)
    record = (_hash(policy), _hash(watchlist))
    with sqlite3.connect(journal, timeout=20) as connection:
        connection.execute("BEGIN IMMEDIATE")
        connection.execute("CREATE TABLE IF NOT EXISTS paper_v2_binding (id INTEGER PRIMARY KEY CHECK(id=1), "
                           "policy_digest TEXT NOT NULL, watchlist_digest TEXT NOT NULL)")
        connection.execute("INSERT OR IGNORE INTO paper_v2_binding VALUES (1,?,?)", record)
        if connection.execute("SELECT policy_digest,watchlist_digest FROM paper_v2_binding").fetchone() != record:
            raise ValueError("A different policy or watchlist already owns the isolated V2 lane")
    return journal


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--as-of", required=True)
    parser.add_argument("--journal-root", type=Path)
    args = parser.parse_args(argv)
    data = json.loads(args.input.read_text(encoding="utf-8-sig"))
    result = size_v2_candidate(**data, as_of=args.as_of)
    if args.journal_root is not None:
        bind_v2_journal(args.journal_root, data["policy"], data["watchlist"], as_of=args.as_of)
        result["v2_journal_bound"] = True
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
