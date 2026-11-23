"""Compare aligned, separately replayed net account series without hiding missing sessions."""

from __future__ import annotations

import argparse
from datetime import date
import hashlib
import json
import math
from pathlib import Path
import random
import re
from statistics import fmean, stdev

from tradingagents.calendar_access import get_exchange_calendar

from .experiments import _stamp

ARMS = ("quant_only", "llm_veto", "dca", "sixty_forty")
_CALENDAR = {"KR": "XKRX", "US": "XNYS"}
_METRICS = ("commission", "slippage", "fx_cost", "tax", "dividend_net", "exposure",
            "llm_cost", "llm_calls", "round_trips")


def _number(value, *, nonnegative=False, integral=False):
    if type(value) not in (int, float) or not math.isfinite(value) or (nonnegative and value < 0):
        raise ValueError("Invalid comparison observation")
    if integral and type(value) is not int:
        raise ValueError("Expected a count")
    return float(value)


def _calendar(market, start, end, cutoff):
    exchange = get_exchange_calendar(_CALENDAR[market])
    output = {}
    for session in exchange.sessions_in_range(start.isoformat(), end.isoformat()):
        closed = exchange.session_close(session).to_pydatetime()
        if closed <= cutoff:
            output[session.date().isoformat()] = closed
    return output


def _stats(values):
    compounded, peak, drawdown = 1.0, 1.0, 0.0
    for value in values:
        compounded *= 1 + value
        peak = max(peak, compounded)
        drawdown = min(drawdown, compounded / peak - 1)
    volatility = stdev(values) if len(values) > 1 else None
    return {"net_time_weighted_return": compounded - 1, "max_drawdown": drawdown,
            "sharpe_rf_zero": math.sqrt(252) * fmean(values) / volatility if volatility else None}


def _paired_interval(diffs, block, samples, seed):
    rng = random.Random(seed)
    means = []
    for _ in range(samples):
        selected = []
        while len(selected) < len(diffs):
            start = rng.randrange(len(diffs) - block + 1)
            selected.extend(diffs[start:start + block])
        means.append(fmean(selected[:len(diffs)]))
    means.sort()
    return [means[int(.025 * (samples - 1))], means[int(.975 * (samples - 1))]]


def compare_replays(policy, series, *, analysis_as_of):
    """Aggregate cost and paired risk evidence from complete aligned replay outputs."""
    keys = {"plan_sha256", "frozen_at", "market", "start", "end", "initial_nav", "minimum_sessions",
            "costs", "data_class", "block_length", "resamples", "seed"}
    if not isinstance(policy, dict) or set(policy) != keys or policy["market"] not in _CALENDAR:
        raise ValueError("Require a frozen comparison plan with explicit market")
    if policy["data_class"] not in {"synthetic", "caller_attested_replay"}:
        raise ValueError("Separate synthetic and retrospective replay evidence")
    if not isinstance(policy["plan_sha256"], str) or re.fullmatch(r"[a-f0-9]{64}", policy["plan_sha256"]) is None:
        raise ValueError("Expected preregistered research plan digest")
    cutoff = _stamp(analysis_as_of)
    start, end = (date.fromisoformat(policy[key]) for key in ("start", "end"))
    fixed = _stamp(policy["frozen_at"])
    if not fixed.date() < start <= end <= cutoff.date():
        raise ValueError("Comparison must follow its frozen plan and stay within the cutoff")
    counts = ("minimum_sessions", "block_length", "resamples", "seed")
    if any(type(policy[name]) is not int for name in counts):
        raise ValueError("Require fixed sample and bootstrap counts")
    minimum, block, n_samples = (policy[name] for name in counts[:3])
    if not 2 <= minimum <= 2000 or not 1 <= block <= minimum or not 200 <= n_samples <= 5000:
        raise ValueError("Invalid preregistered comparison sample policy")
    if (not isinstance(policy["costs"], dict) or not policy["costs"] or len(policy["costs"]) > 8
            or not all(isinstance(value, str) and re.fullmatch(r"[a-f0-9]{64}", value)
                       for value in policy["costs"].values())
            or not isinstance(series, dict) or set(series) != set(policy["costs"])):
        raise ValueError("Each frozen cost scenario needs its own paired replay results")
    nav = _number(policy["initial_nav"], nonnegative=True)
    if nav <= 0:
        raise ValueError("Positive and identical comparison capital required")
    sessions = _calendar(policy["market"], start, end, cutoff)
    if len(sessions) > 2000:
        raise ValueError("At most 2000 sessions per comparison")
    scenarios = {}
    for scenario, digest in policy["costs"].items():
        records = series[scenario]
        if not isinstance(records, dict) or set(records) != set(ARMS):
            raise ValueError("All four preregistered comparison arms are required")
        prepared = {arm: _prepare(records[arm], sessions, digest, cutoff, arm) for arm in ARMS}
        scenarios[scenario] = _paired(prepared, sessions, nav, minimum, block, n_samples, policy["seed"])
    signature = hashlib.sha256(json.dumps(policy, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return {"data_class": policy["data_class"], "analysis_as_of": cutoff.isoformat(),
            "comparison_policy_sha256": signature, "plan_sha256": policy["plan_sha256"],
            "expected_sessions": len(sessions), "results": scenarios,
            "interpretation": "Synthetic inputs validate the engine. Caller-attested inputs are retrospective evidence only.",
            "live_order_authority": False}


def _prepare(rows, sessions, digest, cutoff, arm):
    if not isinstance(rows, list):
        raise ValueError("Comparison observations must be ordered rows")
    output = {}
    seen = set()
    for row in rows:
        day = row.get("session") if isinstance(row, dict) else None
        if not isinstance(day, str) or day not in sessions or day in seen:
            raise ValueError("Invalid, duplicate, future, or non-session observation")
        seen.add(day)
        # Explicit failures remain in the expected denominator just like missing rows.
        if row.get("status") != "VERIFIED":
            continue
        try:
            known = _stamp(row.get("available_at"))
            if not sessions[day] <= known <= cutoff or row.get("cost_digest") != digest:
                continue
            value = _number(row.get("closing_nav"), nonnegative=True)
            flow = _number(row.get("external_cashflow"))
            stats = {key: _number(row.get(key), nonnegative=True, integral=key in {"llm_calls", "round_trips"})
                     for key in _METRICS}
            if value <= 0 or stats["exposure"] > 1 or (arm != "llm_veto" and (stats["llm_calls"] or stats["llm_cost"])):
                continue
            output[day] = (value, flow, stats, row.get("regime"))
        except ValueError:
            continue
    return output


def _paired(arms, sessions, initial_nav, minimum, block, samples, seed):
    missing = [day for day in sessions if any(day not in arms[arm] for arm in ARMS)]
    mismatch = [day for day in sessions if day not in missing and len({arms[arm][day][1] for arm in ARMS}) != 1]
    result = {"eligible_sessions": len(sessions) - len(missing) - len(mismatch),
              "missing_or_unverified_sessions": missing, "cashflow_mismatch_sessions": mismatch}
    if missing or mismatch or len(sessions) < minimum:
        return result | {"status": "INSUFFICIENT_COMPARABLE_SESSIONS"}
    returns, summaries = {}, {}
    for arm in ARMS:
        prior = initial_nav
        values = []
        totals = {key: 0.0 for key in _METRICS}
        regimes = {}
        for day in sessions:
            value, flow, entries, regime = arms[arm][day]
            denominator = prior + flow
            if denominator <= 0:
                return result | {"status": "UNFUNDED_EXTERNAL_CASHFLOW"}
            ret = value / denominator - 1
            if not math.isfinite(ret):
                return result | {"status": "INVALID_NET_ACCOUNT_RETURN"}
            values.append(ret)
            if isinstance(regime, str) and regime:
                regimes.setdefault(regime, []).append(ret)
            for key in totals:
                totals[key] += entries[key]
            prior = value
        totals["mean_exposure"] = totals.pop("exposure") / len(values)
        summaries[arm] = _stats(values) | {"cost_totals": totals,
                                          "regime_samples": {key: len(value) for key, value in regimes.items()}}
        returns[arm] = values

    pairs = {}
    for challenger, baseline in (("llm_veto", "quant_only"), ("quant_only", "dca"), ("quant_only", "sixty_forty")):
        differences = [left - right for left, right in zip(returns[challenger], returns[baseline])]
        pairs[f"{challenger}_vs_{baseline}"] = {
            "mean_paired_daily_excess": fmean(differences),
            "paired_block_bootstrap_95pct": _paired_interval(differences, block, samples, seed),
        }
    return result | {"status": "COMPARABLE", "arms": summaries, "paired": pairs}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--as-of", required=True)
    args = parser.parse_args(argv)
    data = json.loads(args.input.read_text(encoding="utf-8-sig"))
    print(json.dumps(compare_replays(data["policy"], data["series"], analysis_as_of=args.as_of), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
