"""Read-only, point-in-time Core/Satellite weight proposal and veto ablation."""

from __future__ import annotations

import argparse
from datetime import timedelta
import json
import math
from pathlib import Path
from statistics import mean, stdev

from .experiments import _digest, _stamp


def _number(value):
    if type(value) not in (int, float):
        raise ValueError("Numeric evidence required")
    try:
        if math.isfinite(value):
            return value
    except OverflowError:
        pass
    raise ValueError("Finite evidence required")


def _known(record, cutoff):
    if not isinstance(record, dict) or not isinstance(record.get("source"), str) or not record["source"].strip():
        raise ValueError("Evidence source required")
    event, known = _stamp(record.get("effective_at")), _stamp(record.get("known_at"))
    if event > known or known > cutoff:
        raise ValueError("Evidence outside the decision cutoff")
    return event


def _policy(value, cutoff):
    required = {"version", "frozen_at", "currency", "core", "satellite", "budget_core", "budget_satellite",
                "cash_floor", "asset_cap", "trend_window", "momentum_window", "volatility_window",
                "annual_volatility_target", "maximum_stale_days", "minimum_turnover", "satellite_limit",
                "factor_weights", "cost_version"}
    if not isinstance(value, dict) or set(value) != required or _stamp(value["frozen_at"]) >= cutoff:
        raise ValueError("Preregistered policy must be frozen before the decision")
    for key in ("version", "cost_version", "currency"):
        if not isinstance(value[key], str) or not value[key].strip():
            raise ValueError("Explicit version, cost model, and portfolio currency required")
    if (any(not isinstance(value[key], list) or not value[key] for key in ("core", "satellite"))
            or any(not isinstance(symbol, str) or not symbol.strip() for symbol in (*value["core"], *value["satellite"]))):
        raise ValueError("Preregistered Core and Satellite membership required")
    tickers = (*value["core"], *value["satellite"])
    if len(set(tickers)) != len(tickers):
        raise ValueError("Universe membership must not overlap or duplicate")
    budgets = [_number(value[key]) for key in ("budget_core", "budget_satellite", "cash_floor")]
    if min(budgets) < 0 or sum(budgets) > 1 + 1e-12 or not 0 < _number(value["asset_cap"]) <= 1:
        raise ValueError("Invalid portfolio budgets")
    for key in ("trend_window", "momentum_window", "volatility_window", "maximum_stale_days", "satellite_limit"):
        if type(value[key]) is not int or not 1 <= value[key] <= 1000:
            raise ValueError("Invalid preregistered window")
    if value["volatility_window"] < 2 or min(_number(value["minimum_turnover"]), _number(value["annual_volatility_target"])) <= 0:
        raise ValueError("Liquidity and volatility constraints must be positive")
    factors = value["factor_weights"]
    if (not isinstance(factors, dict) or not factors or any(key not in ("quality", "revision", "strength") for key in factors)
            or any(not 0 <= _number(weight) <= 1 for weight in factors.values())
            or not math.isclose(sum(factors.values()), 1.0)):
        raise ValueError("Preregistered factor weights must sum to one")


def _security(values, policy, cutoff, *, satellite):
    if not isinstance(values, dict):
        raise ValueError("Invalid asset evidence")
    security = values.get("security")
    _known(security, cutoff)
    if security.get("eligible") is not True or security.get("currency") != policy["currency"]:
        raise ValueError("Missing eligible listing or comparable currency")
    liquidity = values.get("liquidity")
    if cutoff - _known(liquidity, cutoff) > timedelta(days=policy["maximum_stale_days"]):
        raise ValueError("Stale turnover")
    if _number(liquidity.get("turnover")) < policy["minimum_turnover"]:
        raise ValueError("Turnover below constraint")
    panel = {}
    for bar in values.get("closes", []):
        try:
            stamp = _known(bar, cutoff)
        except (TypeError, ValueError):
            continue
        price = _number(bar.get("price"))
        if price <= 0 or bar.get("basis") != "total_return" or bar.get("currency") != policy["currency"]:
            raise ValueError("Incompatible price basis")
        if stamp in panel and panel[stamp] != price:
            raise ValueError("Conflicting closing prices")
        panel[stamp] = price
    minimum = max(policy["trend_window"], policy["momentum_window"] + 1, policy["volatility_window"] + 1)
    if len(panel) < minimum or cutoff - max(panel) > timedelta(days=policy["maximum_stale_days"]):
        raise ValueError("Insufficient completed price evidence")
    prices = [panel[stamp] for stamp in sorted(panel)]
    recent = prices[-policy["volatility_window"] - 1:]
    vol = stdev([right / left - 1 for left, right in zip(recent, recent[1:])]) * math.sqrt(252)
    momentum = prices[-1] / prices[-policy["momentum_window"] - 1] - 1
    trend = prices[-1] > mean(prices[-policy["trend_window"]:])
    if not satellite:
        return momentum, vol, momentum > 0 and trend
    factors = values.get("factors")
    if not isinstance(factors, dict):
        raise ValueError("Missing dated factors")
    score = 0.0
    for key, weight in policy["factor_weights"].items():
        factor = factors.get(key)
        _known(factor, cutoff)
        normalised = _number(factor.get("value"))
        if not -1 <= normalised <= 1:
            raise ValueError("Invalid normalised factor")
        score += normalised * weight
    return score, vol, True


def _targets(rows, *, budget, cap, volatility_target, limit):
    eligible = sorted(((-score, ticker, vol) for ticker, (score, vol, admitted) in rows.items() if admitted))[:limit]
    if not eligible:
        return {}
    target = budget / len(eligible)
    return {ticker: min(target, cap, volatility_target / vol if vol > 0 else cap)
            for _, ticker, vol in eligible}


def propose_weights(policy, market_evidence, *, analysis_as_of, vetoes=None, settled_cash=None, unsettled_cash=None):
    cutoff = _stamp(analysis_as_of)
    _policy(policy, cutoff)
    if not isinstance(market_evidence, dict) or (vetoes is not None and not isinstance(vetoes, dict)):
        raise ValueError("Expected instrument-keyed evidence")
    vetoes = vetoes or {}
    rejected = {}
    arms = {}
    for sleeve in ("core", "satellite"):
        arms[sleeve] = {}
        for ticker in policy[sleeve]:
            try:
                arms[sleeve][ticker] = _security(market_evidence.get(ticker) or {}, policy, cutoff,
                                                 satellite=sleeve == "satellite")
            except (TypeError, ValueError, OverflowError) as exc:
                rejected[ticker] = str(exc)
    weights = {}
    for sleeve, limit in (("core", 1), ("satellite", policy["satellite_limit"])):
        weights.update(_targets(arms[sleeve], budget=policy[f"budget_{sleeve}"], cap=policy["asset_cap"],
                                volatility_target=policy["annual_volatility_target"], limit=limit))
    after_veto = weights.copy()
    evidence = {}
    for ticker, veto in vetoes.items():
        if ticker not in after_veto:
            continue
        try:
            _known(veto, cutoff)
            if veto.get("decision") not in ("VETO", "DEFER") or not isinstance(veto.get("reason"), str) or not veto["reason"].strip():
                continue
        except (TypeError, ValueError):
            continue
        after_veto.pop(ticker)
        evidence[ticker] = {"decision": veto["decision"], "known_at": veto["known_at"], "source": veto["source"]}
    cash = {}
    for name, value in (("settled", settled_cash), ("unsettled", unsettled_cash)):
        try:
            _known(value, cutoff)
            amount = _number(value.get("amount"))
            if amount >= 0 and value["currency"] == policy["currency"]:
                cash[name] = amount
        except (KeyError, TypeError, ValueError):
            continue
    return {
        "policy_hash": _digest(policy), "analysis_as_of": cutoff.isoformat(), "currency": policy["currency"],
        "quant_only": {"weights": weights, "cash_weight": 1 - sum(weights.values())},
        "after_veto": {"weights": after_veto, "cash_weight": 1 - sum(after_veto.values())},
        "veto_evidence": evidence, "cash_evidence": cash, "universe_count": len(policy["core"]) + len(policy["satellite"]),
        "rejected_evidence": rejected, "execution_authority": False,
    }


def purged_folds(labels, folds, *, frozen_at, holdout_start, analysis_as_of):
    """Separate a final untouched holdout and remove labels reaching each fold's embargo."""
    frozen, holdout, cutoff = map(_stamp, (frozen_at, holdout_start, analysis_as_of))
    if not frozen < holdout <= cutoff or not isinstance(labels, list) or not isinstance(folds, list) or not folds:
        raise ValueError("An untouched final holdout and preregistered folds are required")
    rows = {}
    for row in labels:
        if not isinstance(row, dict) or not isinstance(row.get("id"), str) or not row["id"] or row["id"] in rows:
            raise ValueError("Unique observation IDs required")
        decision, outcome, known = (_stamp(row.get(key)) for key in ("decision_at", "outcome_end", "outcome_known_at"))
        if not decision < outcome <= known <= cutoff:
            raise ValueError("Outcome chronology is not verified")
        rows[row["id"]] = (decision, outcome, known)
    windows = []
    last_end = frozen
    for fold in folds:
        embargo, start, end = (_stamp(fold.get(key)) for key in ("train_before", "test_start", "test_end"))
        if not embargo < start <= end < holdout or start <= last_end:
            raise ValueError("Fold overlaps another evaluation, its embargo, or the holdout")
        training = sorted(key for key, (decision, outcome, known) in rows.items() if decision < embargo and known < embargo)
        purged = sorted(key for key, (decision, outcome, known) in rows.items() if decision < embargo <= known)
        testing = sorted(key for key, (decision, outcome, known) in rows.items() if start <= decision <= end)
        if not training or not testing:
            raise ValueError("Empty training or evaluation fold")
        windows.append({"training": training, "evaluation": testing, "purged": purged, "test_start": start.isoformat()})
        last_end = end
    return {
        "folds": windows,
        "holdout": sorted(key for key, (decision, _, _) in rows.items() if decision >= holdout),
        "evidence_count": len(rows),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--purged-folds", action="store_true")
    args = parser.parse_args(argv)
    record = json.loads(args.input.read_text(encoding="utf-8"))
    result = purged_folds(**record) if args.purged_folds else propose_weights(**record)
    print(json.dumps(result, ensure_ascii=False, allow_nan=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
