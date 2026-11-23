"""Deterministic limits for an isolated micro-paper sleeve."""

from datetime import timedelta
from decimal import Decimal, InvalidOperation

from .experiments import _stamp


def _decimal(value, *, zero=True):
    try:
        number = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError("Explicit finite risk quantity required") from exc
    if not number.is_finite() or number < 0 or (not zero and not number):
        raise ValueError("Invalid risk quantity")
    return number


def evaluate_micro_paper(policy, account, intent, api_events, *, as_of):
    now = _stamp(as_of)
    keys = {"version", "scope", "currency", "capital_ceiling", "order_ceiling",
            "day_loss_fraction", "drawdown_fraction", "max_api_failures", "max_account_age_seconds"}
    if (not isinstance(policy, dict) or set(policy) != keys
            or any(not isinstance(policy[key], str) or not policy[key].strip() for key in ("version", "scope", "currency"))):
        raise ValueError("A versioned isolated risk policy is required")
    if not all(type(policy[key]) is int and policy[key] > 0 for key in ("max_api_failures", "max_account_age_seconds")):
        raise ValueError("Invalid freshness or API limit")
    day_limit = _decimal(policy["day_loss_fraction"], zero=False)
    drawdown_limit = _decimal(policy["drawdown_fraction"], zero=False)
    capital_limit = _decimal(policy["capital_ceiling"], zero=False)
    order_limit = _decimal(policy["order_ceiling"], zero=False)
    if max(day_limit, drawdown_limit) >= 1 or order_limit > capital_limit or policy["max_account_age_seconds"] > 120:
        raise ValueError("Invalid exposure or loss threshold")
    blockers = []
    reduce_only = []
    failure_count = 0
    if not isinstance(api_events, list) or not api_events:
        blockers.append("api_observation_missing")
    else:
        previous = None
        seen = set()
        try:
            for event in api_events:
                stamp = _stamp(event.get("observed_at"))
                identity = event.get("id")
                if (event.get("scope") != policy["scope"] or not isinstance(identity, str) or not identity
                        or identity in seen or stamp > now or (previous is not None and stamp <= previous)
                        or type(event.get("success")) is not bool):
                    raise ValueError("Unverified API result sequence")
                seen.add(identity)
                previous = stamp
                failure_count = 0 if event["success"] else failure_count + 1
            if now - previous > timedelta(seconds=policy["max_account_age_seconds"]):
                blockers.append("api_observation_stale")
        except (AttributeError, TypeError, ValueError):
            blockers.append("invalid_api_observation")
    if failure_count >= policy["max_api_failures"]:
        blockers.append("consecutive_api_errors")

    try:
        for item in (account, intent):
            if (item.get("mode") != "isolated_paper" or item.get("scope") != policy["scope"]
                    or item.get("currency") != policy["currency"]):
                raise ValueError("Scope mismatch")
        if account.get("kill_switch") is not False or account.get("reconciled") is not True:
            blockers.append("account_halted_or_unreconciled")
        observed = _stamp(account.get("observed_at"))
        if not timedelta(0) <= now - observed <= timedelta(seconds=policy["max_account_age_seconds"]):
            blockers.append("account_observation_stale")
        nav, opening, peak = (_decimal(account[key], zero=False) for key in ("nav", "day_open_nav", "peak_nav"))
        exposure, settled, pending = (_decimal(account[key]) for key in ("gross_exposure", "settled_cash", "pending_buy_notional"))
        notional = _decimal(intent.get("notional"), zero=False)
        if peak < max(nav, opening) or intent.get("side") not in ("BUY", "SELL"):
            raise ValueError("Inconsistent account or action")
        if 1 - nav / opening >= day_limit:
            reduce_only.append("daily_loss_limit")
        if 1 - nav / peak >= drawdown_limit:
            reduce_only.append("drawdown_limit")
        if notional > order_limit:
            blockers.append("order_ceiling")
        if intent["side"] == "BUY":
            if exposure + pending + notional > capital_limit or pending + notional > settled:
                blockers.append("capital_or_settled_cash_limit")
            blockers.extend(reduce_only)
        elif intent.get("verified_risk_reduction") is not True:
            blockers.append("risk_reduction_unverified")
    except (AttributeError, KeyError, TypeError, ValueError):
        blockers.append("invalid_account_or_intent")

    return {"policy_version": policy["version"], "projected_paper_candidate": not blockers,
            "blocking_reasons": blockers, "reduce_only_reasons": reduce_only,
            "consecutive_api_failures": failure_count, "live_order_authority": False}
