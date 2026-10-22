"""Read-only evaluation of proven strategy cash flows, never trading authority.

The caller supplies one latest cumulative observation per strategy intent and
may attach verified availability of its current consecutive economic state.
Sensitivity costs are explicit assumptions on observed turnover, not broker fees
or a claim that taxes, FX, financing and model costs have been measured.
"""
from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal, ROUND_CEILING
import math
from zoneinfo import ZoneInfo


SCHEMA = "tradingagents.strategy-evaluation/v1"
COST_SENSITIVITY_BPS = (10, 30, 50)
TERMINAL = {"FILLED", "CANCELLED", "REJECTED", "NOT_SENT", "BLOCKED"}


def _at(value):
    if not isinstance(value, str):
        raise ValueError("EVALUATION_TIMESTAMP_REQUIRED")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            raise ValueError()
        return parsed.astimezone(timezone.utc)
    except ValueError:
        raise ValueError("EVALUATION_TIMESTAMP_INVALID") from None


def _amount(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < 0:
        raise ValueError("EVALUATION_AMOUNT_INVALID")
    return Decimal(str(value))


def evaluate_strategy_orders(orders, *, market, as_of, gross_pnl, valuation_complete):
    """Evaluate verified cumulative observations without importing validation trades.

    Missing or invalid proof fails closed. A full liquidation establishes gross
    realized cash flow without inventing execution-level FIFO from daily reports.
    Open inventory never receives an inferred realized profit or exit cost.
    """
    if market not in {"KR", "US"} or type(valuation_complete) is not bool:
        raise ValueError("EVALUATION_CONTEXT_INVALID")
    now = _at(as_of)
    currency, zone = ("KRW", "Asia/Seoul") if market == "KR" else ("USD", "America/New_York")
    identities, validated, sessions = set(), [], set()
    availability, first_observations = {}, {}
    pending = False
    for order in orders:
        identity = order.get("id")
        if not isinstance(identity, str) or not identity or identity in identities:
            raise ValueError("EVALUATION_DUPLICATE_OR_MISSING_INTENT")
        identities.add(identity)
        prepared = _at(order.get("prepared_at"))
        if prepared > now or order.get("side") not in {"BUY", "SELL"}:
            raise ValueError("EVALUATION_ORDER_INVALID")
        quantity, requested = order.get("filled_quantity"), order.get("quantity")
        if type(quantity) is not int or type(requested) is not int or not 0 <= quantity <= requested or requested <= 0:
            raise ValueError("EVALUATION_QUANTITY_INVALID")
        pending |= order.get("status") not in TERMINAL
        if not quantity:
            continue
        observed, ingested = _at(order.get("observed_at")), _at(order.get("ingested_at"))
        if not prepared <= observed <= ingested <= now:
            raise ValueError("EVALUATION_OBSERVATION_CLOCK_INVALID")
        if (order.get("mode") != "demo" or order.get("source") != "KIS_DEMO_BROKER_REPORT"
                or order.get("strategy_performance") is not True):
            raise ValueError("EVALUATION_STRATEGY_PROOF_REQUIRED")
        ticker = order.get("ticker")
        if not isinstance(ticker, str) or not ticker:
            raise ValueError("EVALUATION_TICKER_REQUIRED")
        amount = None if order.get("fill_notional") is None else _amount(order["fill_notional"])
        if amount == 0:
            raise ValueError("EVALUATION_FILL_AMOUNT_INVALID")
        available, proof_observed = ingested, observed
        if "fill_availability" in order:
            proof = order["fill_availability"]
            if (not isinstance(proof, dict) or proof.get("source") != "KIS_DEMO_BROKER_REPORT"
                    or type(proof.get("filled_quantity")) is not int or proof["filled_quantity"] != quantity
                    or "fill_notional" not in proof
                    or (None if proof["fill_notional"] is None else _amount(proof["fill_notional"])) != amount):
                raise ValueError("EVALUATION_FILL_AVAILABILITY_INVALID")
            proof_observed, available = _at(proof.get("observed_at")), _at(proof.get("ingested_at"))
            if not (prepared <= proof_observed <= observed and proof_observed <= available <= ingested):
                raise ValueError("EVALUATION_FILL_AVAILABILITY_CLOCK_INVALID")
        first_observed = _at(order["first_fill_observed_at"]) if "first_fill_observed_at" in order else proof_observed
        if not prepared <= first_observed <= proof_observed:
            raise ValueError("EVALUATION_FIRST_FILL_CLOCK_INVALID")
        availability[identity], first_observations[identity] = available, first_observed
        validated.append((prepared, identity, order, amount))
        # This is the session in which the original order was submitted; exact
        # execution times are not available from the cumulative order report.
        sessions.add(prepared.astimezone(ZoneInfo(zone)).date().isoformat())
    validated.sort(key=lambda value: (value[0], value[1]))
    holdings, episodes, last_available = {}, {}, {}
    closed = 0
    buy = sell = Decimal(0)
    money_known, sequence_known = True, True
    for prepared, _, order, amount in validated:
        ticker, quantity, side = order["ticker"], order["filled_quantity"], order["side"]
        # Observing a broker response is not enough: the predecessor's fill
        # must have been ingested before the successor order was prepared.
        if ticker in last_available and prepared < last_available[ticker]:
            sequence_known = False
        last_available[ticker] = availability[order["id"]]
        holdings[ticker] = holdings.get(ticker, 0) + (quantity if side == "BUY" else -quantity)
        if holdings[ticker] < 0:
            raise ValueError("EVALUATION_UNOWNED_SELL")
        if amount is None:
            money_known = False
        elif side == "BUY":
            buy += amount
        else:
            sell += amount
        episodes[ticker] = episodes.get(ticker, False) or side == "BUY"
        if holdings[ticker] == 0 and episodes[ticker]:
            closed += 1
            episodes[ticker] = False
    has_fills = bool(validated)
    flat = not any(holdings.values())
    if gross_pnl is not None and (isinstance(gross_pnl, bool) or not isinstance(gross_pnl, (int, float)) or not math.isfinite(gross_pnl)):
        raise ValueError("EVALUATION_GROSS_PNL_INVALID")
    gross = Decimal(str(gross_pnl)) if has_fills and money_known and valuation_complete and gross_pnl is not None else None
    turnover = buy + sell if money_known else None
    if gross is not None and flat and abs(gross - (sell - buy)) > Decimal("0.0001"):
        raise ValueError("EVALUATION_GROSS_CASHFLOW_MISMATCH")
    # Unknown costs stay unknown even if a sensitivity scenario happens to equal
    # a future broker charge. Rounded-up assumptions are conservative per currency.
    scenarios = []
    quantum = Decimal("1") if currency == "KRW" else Decimal("0.01")
    for bps in COST_SENSITIVITY_BPS:
        cost = (turnover * Decimal(bps) / 10000).quantize(quantum, rounding=ROUND_CEILING) if has_fills and turnover is not None else None
        scenarios.append({"assumed_cost_bps_on_turnover": bps,
                          "estimated_cost": float(cost) if cost is not None else None,
                          "estimated_pnl_after_assumed_cost": round(float(gross - cost), 4) if gross is not None and cost is not None else None})
    missing = ["ACTUAL_FEES_TAXES_FX_UNVERIFIED", "SETTLEMENT_UNVERIFIED",
               "BROKER_CORRECTIONS_UNVERIFIED", "STATISTICAL_AND_OUT_OF_SAMPLE_VALIDATION_REQUIRED"]
    buys = [order for _, _, order, _ in validated if order["side"] == "BUY"]
    sells = [order for _, _, order, _ in validated if order["side"] == "SELL"]
    if not has_fills:
        missing.append("NO_STRATEGY_FILLS")
    if not buys:
        missing.append("STRATEGY_BUY_FILL_REQUIRED")
    if not sells:
        missing.append("STRATEGY_SELL_FILL_REQUIRED")
    if not closed or not sequence_known:
        missing.append("CLOSED_STRATEGY_ROUND_TRIP_UNVERIFIED")
    if not money_known:
        missing.append("FILL_NOTIONAL_UNVERIFIED")
    if has_fills and gross is None:
        missing.append("GROSS_VALUATION_INCOMPLETE")
    if not flat:
        missing.append("OPEN_STRATEGY_INVENTORY")
    if pending:
        missing.append("ORDER_PENDING_OR_UNRESOLVED")
    return {"schema": SCHEMA, "scope": "NORMAL_STRATEGY_ONLY", "market": market,
            "currency": currency, "analysis_as_of": as_of,
            "status": "NO_FILLS" if not has_fills else "AVAILABLE_GROSS_ONLY" if gross is not None else "INCOMPLETE",
            "sample": {"filled_order_count": len(validated), "buy_filled_orders": len(buys), "sell_filled_orders": len(sells),
                       "buy_filled_quantity": sum(o["filled_quantity"] for o in buys),
                       "sell_filled_quantity": sum(o["filled_quantity"] for o in sells),
                       "closed_inventory_episodes": closed if sequence_known else None,
                       "order_session_count": len(sessions), "order_sessions": sorted(sessions),
                       # First positive cumulative report, not exact execution
                       # time; legacy callers only supply their latest report.
                       "first_observed_at": min(first_observations.values()).isoformat() if first_observations else None,
                       "last_observed_at": max((o["observed_at"] for _, _, o, _ in validated), key=_at, default=None)},
            "open_positions": {ticker: quantity for ticker, quantity in holdings.items() if quantity},
            "turnover": round(float(turnover), 4) if turnover is not None else None,
            "gross_pnl": round(float(gross), 4) if gross is not None else None,
            "realized_gross_pnl": round(float(sell - buy), 4) if has_fills and flat and money_known and sequence_known else None,
            "realized_basis": "FULLY_CLOSED_STRATEGY_CASHFLOWS" if has_fills and flat and money_known and sequence_known else "UNAVAILABLE",
            "exact_fifo_available": False, "actual_cost": None, "net_pnl": None,
            "fees_known": False, "settlement_known": False,
            "cost_sensitivity": {"basis": "ASSUMPTION_ONLY_NOT_BROKER_COSTS", "applies_to": "OBSERVED_BUY_PLUS_SELL_NOTIONAL",
                                 "assumption": "10/30/50 bps of observed turnover; no measured fee, tax, FX or other cost coverage is claimed",
                                 "includes_future_exit_cost": False,
                                 "execution_prices_already_include_realized_price_slippage": True,
                                 "scenarios": scenarios},
            "readiness": "NOT_READY_FOR_REAL_INVESTMENT", "unmet_criteria": missing,
            "real_orders_enabled": False, "automatic_live_transition": False}
