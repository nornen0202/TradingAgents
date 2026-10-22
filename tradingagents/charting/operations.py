"""Read-only local archive discovery and explicitly scoped operational receipts."""
from __future__ import annotations

from datetime import datetime, timezone
from functools import lru_cache
import json
from pathlib import Path
import re

from .bars import instant, validate_bars


def _json(path):
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except (OSError, ValueError):
        return {}


@lru_cache(maxsize=2048)
def _cached_manifest(path, modified_ns, size):
    # Filesystem metadata only invalidates parsed bytes; it never determines
    # data availability. Timestamp eligibility is checked afresh per request.
    return _json(path)


def _manifest(path):
    try:
        stat = path.stat()
        return _cached_manifest(str(path), stat.st_mtime_ns, stat.st_size)
    except OSError:
        return {}


def known_artifacts(directory, cutoff):
    """Coverage is based on known records, never mutable file existence."""
    from .report import _checkpoint_payloads, _snapshot_visible
    from tradingagents.dataflows.event_timeline import build_event_timeline
    from tradingagents.dataflows.market_policy import source_use_policy
    chart = False
    for payload in _checkpoint_payloads(directory, "chart_evidence"):
        if (_snapshot_visible(payload, cutoff)
                and (not payload.get("ticker") or str(payload["ticker"]).upper() == directory.name.upper())
                and source_use_policy(payload.get("provider") or "local_archive", entitlement=payload.get("entitlement"))["allowed"]
                and validate_bars(payload.get("bars") or [], analysis_as_of=cutoff)["bars"]):
            chart = True
            break
    board = _json(directory / "event_timeline.json")
    records = board.get("records") or [version for event in board.get("events", []) if isinstance(event, dict)
                                        for version in event.get("versions", [event])]
    events = bool(build_event_timeline(records, analysis_as_of=cutoff, ticker=directory.name)["events"])
    receipts = []
    for item in _checkpoint_payloads(directory, "chart_capture_status"):
        checked = instant(item.get("checked_at"))
        if (item.get("schema") == "tradingagents.chart-capture-status/v1" and checked is not None and checked <= cutoff
                and item.get("ticker") == directory.name and item.get("status") in {"REFRESHED", "UNAVAILABLE"}):
            error_type = item.get("error_type")
            count = item.get("completed_bar_count")
            receipts.append((checked, {"status": item["status"], "checked_at": checked.isoformat(),
                "error_type": error_type if isinstance(error_type, str) and re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{0,79}", error_type) else None,
                "completed_bar_count": count if type(count) is int and count >= 0 else None}))
    status = max(receipts, key=lambda pair: pair[0])[1] if receipts else None
    return {"chart_capture_available": chart, "event_board_available": events, "chart_capture_status": status}


def archive_catalog(archive_dir, *, analysis_as_of, only_ticker=None, include_coverage=True):
    """Discover the latest completed producer per ticker, at the requested cutoff.

    Directory names and the global latest pointer are never data clocks. Return
    paths only to the server caller; ``public_context`` is safe for localhost UI.
    Re-scan on demand so a long-running viewer sees new KR/US runs without restart.
    """
    cutoff = instant(analysis_as_of)
    if cutoff is None:
        raise ValueError("Archive cutoff requires a timezone")
    root = (Path(archive_dir) / "runs").resolve()
    selected = {}
    for manifest_path in root.glob("*/*/run.json"):
        run_dir = manifest_path.parent.resolve()
        if not run_dir.is_relative_to(root):
            continue
        manifest = _manifest(manifest_path)
        started, finished = instant(manifest.get("started_at")), instant(manifest.get("finished_at"))
        run_id = str(manifest.get("run_id") or "")
        if (started is None or finished is None or not started <= finished <= cutoff
                or run_id != run_dir.name or manifest.get("status") == "running"):
            continue
        summaries = manifest.get("tickers")
        for summary in summaries if isinstance(summaries, list) else []:
            if not isinstance(summary, dict) or summary.get("status") != "success":
                continue
            ticker = str(summary.get("ticker") or "")
            if only_ticker is not None and ticker != only_ticker:
                continue
            ticker_dir = (run_dir / "tickers" / ticker).resolve()
            ticker_root = (run_dir / "tickers").resolve()
            if not ticker or not ticker_dir.is_relative_to(ticker_root) or not ticker_dir.is_dir():
                continue
            key = (started, run_id)
            if ticker in selected and selected[ticker]["key"] >= key:
                continue
            selected[ticker] = {"key": key, "ticker_dir": ticker_dir, "_manifest": manifest, "_summary": summary}
    # Inspect candle/event vintages only for the selected sources, rather than
    # every historical candidate encountered while finding the newest run.
    for entry in selected.values():
        manifest, summary = entry.pop("_manifest"), entry.pop("_summary")
        ticker_dir = entry["ticker_dir"]
        research_finished = instant(_json(ticker_dir / "analysis.json").get("finished_at"))
        settings = manifest.get("settings") if isinstance(manifest.get("settings"), dict) else {}
        entry["public_context"] = {"run_id": manifest["run_id"], "run_started_at": instant(manifest["started_at"]).isoformat(),
                   "run_finished_at": instant(manifest["finished_at"]).isoformat(),
                   "research_finished_at": research_finished.isoformat() if research_finished is not None and research_finished <= cutoff else None,
                   "market": settings.get("market"), "run_mode": settings.get("run_mode"),
                   "source_analysis_run_id": manifest.get("overlay_source_run_id"),
                   "quality_flags": [item for item in (summary.get("quality_flags") or []) if isinstance(item, str) and _CODE.fullmatch(item)],
                   **(known_artifacts(ticker_dir, cutoff) if include_coverage else {})}
    return selected


_CODE = re.compile(r"^[A-Za-z0-9_.:-]{1,160}$")


def _source_health(raw):
    if not isinstance(raw, dict):
        return {}
    statuses = {"NO_SOURCE", "BLOCKED", "NO_ALLOCATED_ORDERS", "PROPOSALS_AVAILABLE"}
    result = {"status": raw.get("status") if raw.get("status") in statuses else "BLOCKED"}
    for key in ("strategy_rows", "fresh_rows", "execution_ready_rows", "allocated_orders"):
        value = raw.get(key)
        if type(value) is int and value >= 0:
            result[key] = value
    counts = raw.get("reason_counts")
    result["reason_counts"] = {k: v for k, v in (counts.items() if isinstance(counts, dict) else [])
                               if isinstance(k, str) and re.fullmatch(r"[A-Za-z0-9_:.-]{1,100}", k)
                               and type(v) is int and v >= 0}
    return result


def paper_health(path, *, analysis_as_of):
    """Expose status/counters only: never ledger paths, account IDs or balances."""
    cutoff = instant(analysis_as_of)
    if cutoff is None:
        raise ValueError("Paper status cutoff requires a timezone")
    result = {"status": "UNAVAILABLE", "mode": "LOCAL_PAPER_ONLY", "real_orders_enabled": False,
              "broker_orders_sent": 0, "markets": {}, "checked_at": None}
    raw = _json(path) if path is not None else {}
    checked = instant(raw.get("checked_at"))
    markets = raw.get("markets")
    if (raw.get("schema") != "tradingagents.paper-runtime/v1" or checked is None or checked > cutoff
            or raw.get("mode") != "LOCAL_PAPER_ONLY" or raw.get("real_orders_enabled") is not False
            or type(raw.get("broker_orders_sent")) is not int or raw["broker_orders_sent"] != 0 or not isinstance(markets, dict)):
        return result
    result.update(status="AVAILABLE", checked_at=checked.isoformat(), enabled=raw.get("enabled") is True,
                  stale=(cutoff - checked).total_seconds() > 600)
    allowed_states = {"MARKET_CLOSED", "WAITING_SOURCE", "ACTIVE", "VALUATION_ONLY", "BLOCKED", "ERROR"}
    for key in ("kr", "us"):
        source = markets.get(key)
        if not isinstance(source, dict):
            continue
        market_checked = instant(source.get("checked_at"))
        if market_checked is None or market_checked > checked:
            continue
        view = {"status": source.get("status") if source.get("status") in allowed_states else "ERROR",
                "checked_at": market_checked.isoformat(), "stale": (cutoff - market_checked).total_seconds() > 600,
                "order_counts": {}, "blockers": []}
        for clock in ("last_observation_at", "last_fill_at", "last_quote_at", "last_success_at"):
            value = instant(source.get(clock))
            view[clock] = value.isoformat() if value is not None and value <= market_checked else None
        for field in ("source_run_id", "source_revision"):
            value = source.get(field)
            view[field] = value if isinstance(value, str) and _CODE.fullmatch(value) else None
        blockers = source.get("blockers")
        view["source_diagnostics"] = _source_health(source.get("source_diagnostics"))
        view["blockers"] = [value for value in blockers if isinstance(value, str) and _CODE.fullmatch(value)] if isinstance(blockers, list) else []
        counts = source.get("order_counts")
        counts = counts if isinstance(counts, dict) else {}
        for state in ("PENDING", "FILLED", "REJECTED", "CANCELLED"):
            value = counts.get(state)
            view["order_counts"][state] = value if type(value) is int and value >= 0 else 0
        result["markets"][key] = view
    return result


def kis_demo_health(archive_dir, *, analysis_as_of):
    """Project fixed KIS read-probe receipts without account or order access.

    Receipt freshness is not a claim that an order path has been tested. A
    successful read remains distinct from unverified submission/cancellation.
    Unknown, undated and future receipts expose no data at this cutoff.
    """
    cutoff = instant(analysis_as_of)
    if cutoff is None:
        raise ValueError("KIS read status cutoff requires a timezone")
    result = {"as_of": cutoff.isoformat(), "read_only": True, "markets": {}}
    states = {"READ_CONNECTION_VERIFIED", "READY_TO_PROBE", "MISSING_DEMO_SETTINGS",
              "CONFIGURATION_UNREADABLE", "CONNECTION_UNVERIFIED"}
    root = (Path(archive_dir) / "paper").resolve() if archive_dir is not None else None
    for market, filename in (("KR", "kis-readiness.json"), ("US", "kis-us-readiness.json")):
        view = {"status": "UNAVAILABLE", "checked_at": None, "market": market, "mode": "KIS_DEMO",
                "orders_submitted": 0, "live_orders_enabled": False, "paper_order_connection_verified": False}
        path = (root / filename).resolve() if root is not None else None
        raw = _json(path) if path is not None and path.is_relative_to(root) else {}
        checked = instant(raw.get("checked_at"))
        if (raw.get("mode") == "KIS_DEMO" and raw.get("market") == market
                and raw.get("status") in states and checked is not None and checked <= cutoff
                and type(raw.get("orders_submitted")) is int and raw["orders_submitted"] == 0
                and raw.get("live_orders_enabled") is False and raw.get("real_account_access") is False
                and raw.get("paper_order_connection_verified") is False):
            view.update(status=raw["status"], checked_at=checked.isoformat())
        result["markets"][market] = view
    return result


def kis_validation_health(archive_dir, *, analysis_as_of):
    """Read only bounded VTS validation proofs; never infer fills from ACKs.

    The fixed receipt is written by the session-validation worker. Each stage
    needs its own broker source and post-response observation clock. This view
    is not a broker query and never returns accounts, orders, prices or paths.
    """
    cutoff = instant(analysis_as_of)
    if cutoff is None:
        raise ValueError("KIS validation cutoff requires a timezone")
    sources = {"submitted": "KIS_DEMO_BROKER_ACK", "filled": "KIS_DEMO_BROKER_REPORT",
               "cancelled": "KIS_DEMO_BROKER_REPORT"}
    empty_stages = lambda: {stage: {"verified": False, "observed_at": None} for stage in sources}
    result = {"as_of": cutoff.isoformat(), "read_only": True, "live_orders_enabled": False,
              "markets": {market: {"market": market, "mode": "KIS_DEMO", "status": "UNAVAILABLE",
                "checked_at": None, "stages": empty_stages(), "blocker": None} for market in ("KR", "US")}}
    root = (Path(archive_dir) / "paper").resolve() if archive_dir is not None else None
    path = (root / "kis-session-validation.json").resolve() if root is not None else None
    raw = _json(path) if path is not None and path.is_relative_to(root) else {}
    checked = instant(raw.get("checked_at"))
    if (raw.get("schema") != "tradingagents.kis-session-validation/v1" or raw.get("mode") != "KIS_DEMO"
            or raw.get("live_orders_enabled") is not False or checked is None or checked > cutoff
            or not isinstance(raw.get("markets"), dict)):
        return result
    states = {"WAITING_SESSION", "RUNNING", "VERIFIED", "BLOCKED", "ATTENTION"}
    blockers = {"MARKET_CLOSED", "CALENDAR_UNVERIFIED", "SESSION_EDGE", "HALTED", "EVIDENCE_UNAVAILABLE",
                "AMBIGUOUS_ORDER", "AMBIGUOUS_CANCELLATION", "ORDER_REJECTED", "ORDER_NOT_SENT",
                "CAMPAIGN_BUDGET_EXHAUSTED", "CANCELLATION_RACE", "FILL_NOT_OBSERVED", "STATE_INVALID",
                "JOURNAL_RECOVERY_REQUIRED", "DAY_ORDER_REQUIRES_REVIEW", "CANCELLATION_REJECTED",
                "ORDER_REPORT_UNVERIFIED", "CANCELLATION_NOT_CONFIRMED"}
    for market, view in result["markets"].items():
        row = raw["markets"].get(market)
        if not isinstance(row, dict):
            continue
        observed = instant(row.get("checked_at"))
        if row.get("status") not in states or observed is None or observed > checked:
            continue
        stages = row.get("stages")
        if not isinstance(stages, dict):
            continue
        proofs = empty_stages()
        for stage, source in sources.items():
            proof = stages.get(stage)
            if not isinstance(proof, dict):
                continue
            at = instant(proof.get("observed_at"))
            if proof.get("verified") is True and proof.get("source") == source and at is not None and at <= observed:
                proofs[stage] = {"verified": True, "observed_at": at.isoformat()}
        # A claimed completion without every genuine stage stays unverified.
        status = row["status"]
        if status == "VERIFIED" and not all(proof["verified"] for proof in proofs.values()):
            status = "ATTENTION"
        view.update(status=status, checked_at=observed.isoformat(), stages=proofs)
        # Raw errors can include broker payloads or secrets; only known codes
        # cross this boundary, and new codes require an explicit UI contract.
        blocker = row.get("blocker")
        if blocker:
            view["blocker"] = blocker if isinstance(blocker, str) and blocker in blockers else "OPERATOR_REVIEW_REQUIRED"
    return result


def now_utc():
    return datetime.now(timezone.utc)


def _strategy_evaluation_view(raw, market, observed):
    """Expose a bounded, dated evaluation; assumptions cannot become actual costs."""
    import math
    from decimal import Decimal, ROUND_CEILING
    if not isinstance(raw, dict):
        return None
    known = instant(raw.get("analysis_as_of"))
    currency = "KRW" if market == "KR" else "USD"
    if (raw.get("schema") != "tradingagents.strategy-evaluation/v1"
            or raw.get("scope") != "NORMAL_STRATEGY_ONLY" or raw.get("market") != market
            or raw.get("currency") != currency or known is None or known > observed
            or raw.get("status") not in {"NO_FILLS", "AVAILABLE_GROSS_ONLY", "INCOMPLETE"}
            or raw.get("real_orders_enabled") is not False or raw.get("automatic_live_transition") is not False):
        return None
    sample = raw.get("sample")
    if not isinstance(sample, dict):
        return None
    counts = {key: sample.get(key) for key in ("filled_order_count", "buy_filled_orders", "sell_filled_orders",
              "buy_filled_quantity", "sell_filled_quantity", "order_session_count")}
    if any(type(value) is not int or value < 0 for value in counts.values()):
        return None
    if counts["filled_order_count"] != counts["buy_filled_orders"] + counts["sell_filled_orders"]:
        return None
    if (counts["buy_filled_quantity"] < counts["buy_filled_orders"]
            or counts["sell_filled_quantity"] < counts["sell_filled_orders"]
            or counts["sell_filled_quantity"] > counts["buy_filled_quantity"]
            or not 0 <= counts["order_session_count"] <= counts["filled_order_count"]
            or any(counts[f"{side}_filled_quantity"] and not counts[f"{side}_filled_orders"] for side in ("buy", "sell"))):
        return None
    closed = sample.get("closed_inventory_episodes")
    if closed is not None and (type(closed) is not int or not 0 <= closed <= min(counts["buy_filled_orders"], counts["sell_filled_orders"])):
        return None
    first, last = instant(sample.get("first_observed_at")), instant(sample.get("last_observed_at"))
    if counts["filled_order_count"]:
        if first is None or last is None or not first <= last <= known or raw["status"] == "NO_FILLS":
            return None
    elif sample.get("first_observed_at") is not None or sample.get("last_observed_at") is not None or raw["status"] != "NO_FILLS":
        return None
    def number(value):
        return value if not isinstance(value, bool) and isinstance(value, (int, float)) and math.isfinite(value) else None
    turnover, gross, realized = (number(raw.get(key)) for key in ("turnover", "gross_pnl", "realized_gross_pnl"))
    if turnover is not None and turnover < 0:
        return None
    if (counts["filled_order_count"] and turnover == 0
            or not counts["filled_order_count"] and (gross is not None or realized is not None or turnover not in {None, 0})):
        return None
    if raw["status"] != "AVAILABLE_GROSS_ONLY":
        gross = None
    elif gross is None:
        return None
    if (raw.get("realized_basis") != "FULLY_CLOSED_STRATEGY_CASHFLOWS" or not closed
            or counts["buy_filled_quantity"] != counts["sell_filled_quantity"]):
        realized = None
    sensitivity = raw.get("cost_sensitivity")
    if (not isinstance(sensitivity, dict) or sensitivity.get("basis") != "ASSUMPTION_ONLY_NOT_BROKER_COSTS"
            or sensitivity.get("applies_to") != "OBSERVED_BUY_PLUS_SELL_NOTIONAL"
            or sensitivity.get("includes_future_exit_cost") is not False):
        return None
    scenarios = sensitivity.get("scenarios")
    if not isinstance(scenarios, list) or len(scenarios) != 3:
        return None
    projected = []
    for bps, scenario in zip((10, 30, 50), scenarios):
        if not isinstance(scenario, dict) or scenario.get("assumed_cost_bps_on_turnover") != bps:
            return None
        cost = number(scenario.get("estimated_cost"))
        pnl = number(scenario.get("estimated_pnl_after_assumed_cost"))
        expected = float((Decimal(str(turnover)) * bps / 10000).quantize(
            Decimal("1") if market == "KR" else Decimal("0.01"), rounding=ROUND_CEILING)) if turnover is not None and counts["filled_order_count"] else None
        if cost != expected or (pnl is None) != (gross is None or cost is None):
            return None
        if pnl is not None and abs(pnl - (gross - cost)) > .00011:
            return None
        projected.append({"assumed_cost_bps_on_turnover": bps, "estimated_cost": cost,
                          "estimated_pnl_after_assumed_cost": pnl})
    allowed = {"ACTUAL_FEES_TAXES_FX_UNVERIFIED", "SETTLEMENT_UNVERIFIED", "BROKER_CORRECTIONS_UNVERIFIED",
               "STATISTICAL_AND_OUT_OF_SAMPLE_VALIDATION_REQUIRED", "NO_STRATEGY_FILLS", "STRATEGY_BUY_FILL_REQUIRED",
               "STRATEGY_SELL_FILL_REQUIRED", "CLOSED_STRATEGY_ROUND_TRIP_UNVERIFIED", "FILL_NOTIONAL_UNVERIFIED",
               "GROSS_VALUATION_INCOMPLETE", "OPEN_STRATEGY_INVENTORY", "ORDER_PENDING_OR_UNRESOLVED"}
    unmet = raw.get("unmet_criteria")
    if not isinstance(unmet, list) or not all(isinstance(value, str) and value in allowed for value in unmet):
        return None
    required = {"ACTUAL_FEES_TAXES_FX_UNVERIFIED", "SETTLEMENT_UNVERIFIED", "BROKER_CORRECTIONS_UNVERIFIED",
                "STATISTICAL_AND_OUT_OF_SAMPLE_VALIDATION_REQUIRED"}
    if not counts["filled_order_count"]:
        required.add("NO_STRATEGY_FILLS")
    for side in ("buy", "sell"):
        if not counts[f"{side}_filled_orders"]:
            required.add(f"STRATEGY_{side.upper()}_FILL_REQUIRED")
    if not closed:
        required.add("CLOSED_STRATEGY_ROUND_TRIP_UNVERIFIED")
    if counts["buy_filled_quantity"] > counts["sell_filled_quantity"]:
        required.add("OPEN_STRATEGY_INVENTORY")
    if not required <= set(unmet):
        return None
    return {"status": raw["status"], "currency": currency, "analysis_as_of": known.isoformat(),
            "sample": {**counts, "closed_inventory_episodes": closed}, "turnover": turnover,
            "gross_pnl": gross, "realized_gross_pnl": realized,
            "net_pnl": None, "actual_cost": None, "fees_known": False, "settlement_known": False,
            "cost_sensitivity": {"basis": "ASSUMPTION_ONLY_NOT_BROKER_COSTS", "scenarios": projected,
                                 "includes_future_exit_cost": False},
            "unmet_criteria": list(dict.fromkeys(unmet)), "readiness": "NOT_READY_FOR_REAL_INVESTMENT",
            "real_orders_enabled": False, "automatic_live_transition": False}


def kis_strategy_health(archive_dir, *, analysis_as_of):
    """Fixed local projection; no account balances, secrets or broker IDs."""
    import math
    cutoff = instant(analysis_as_of)
    if cutoff is None:
        raise ValueError("Aware cutoff required")
    result = {"status": "UNAVAILABLE", "read_only": True, "real_orders_enabled": False, "markets": {}}
    raw = _json(Path(archive_dir) / "paper/kis-strategy-runtime.json") if archive_dir else {}
    checked = instant(raw.get("checked_at"))
    if (raw.get("schema") != "tradingagents.kis-strategy-runtime/v1" or raw.get("mode") != "KIS_DEMO_STRATEGY"
            or raw.get("real_orders_enabled") is not False or checked is None or checked > cutoff
            or not isinstance(raw.get("markets"), dict)):
        return result
    result.update(status="AVAILABLE", checked_at=checked.isoformat(), stale=(cutoff-checked).total_seconds() > 180, enabled=raw.get("enabled") is True)
    def number(value):
        return value if not isinstance(value, bool) and isinstance(value, (int, float)) and math.isfinite(value) else None
    statuses = {"DISABLED", "WAITING_VALIDATION", "WAITING_SIGNAL", "MARKET_CLOSED", "BLOCKED", "ACTIVE"}
    order_states = {"ACKNOWLEDGED", "OPEN", "PARTIAL", "FILLED", "CANCELLED", "REJECTED", "NOT_SENT", "BLOCKED", "UNKNOWN", "UNRESOLVED"}
    for market in ("KR", "US"):
        row = raw["markets"].get(market)
        if not isinstance(row, dict):
            continue
        observed = instant(row.get("checked_at"))
        if row.get("status") not in statuses or observed is None or observed > checked:
            continue
        view = {"status": row["status"], "checked_at": observed.isoformat(), "gate_passed": row.get("gate_passed") is True,
                "blockers": [b for b in (row.get("blockers") if isinstance(row.get("blockers"), list) else []) if isinstance(b, str) and re.fullmatch(r"[A-Z_]{1,80}", b)],
                "order_counts": {}, "orders": [], "performance": None, "performance_history": []}
        view["source_diagnostics"] = _source_health(row.get("source_diagnostics"))
        for key, value in (row.get("order_counts") if isinstance(row.get("order_counts"), dict) else {}).items():
            if key in order_states and type(value) is int and value >= 0:
                view["order_counts"][key] = value
        for order in (row.get("orders") if isinstance(row.get("orders"), list) else [])[-100:]:
            if not isinstance(order, dict):
                continue
            prepared, known = instant(order.get("prepared_at")), instant(order.get("observed_at"))
            if prepared is None or prepared > observed or (order.get("observed_at") is not None and (known is None or not prepared <= known <= observed)):
                continue
            if (order.get("status") not in order_states or order.get("side") not in {"BUY", "SELL"}
                    or not isinstance(order.get("ticker"), str) or not re.fullmatch(r"[A-Z0-9.]{1,16}", order["ticker"])
                    or not isinstance(order.get("run_id"), str) or not _CODE.fullmatch(order["run_id"])):
                continue
            values = {key: number(order.get(key)) for key in ("quantity", "limit_price", "filled_quantity", "average_fill_price")}
            if type(values["quantity"]) is not int or type(values["filled_quantity"]) is not int or not 0 <= values["filled_quantity"] <= values["quantity"] or values["quantity"] <= 0:
                continue
            if values["filled_quantity"] and known is None:
                continue
            if order["status"] == "FILLED" and values["filled_quantity"] != values["quantity"]:
                continue
            view["orders"].append({**values, **{key: order[key] for key in ("ticker", "run_id", "side", "status")},
                "prepared_at": prepared.isoformat(), "observed_at": known.isoformat() if known else None,
                "cancel_status": order.get("cancel_status") if order.get("cancel_status") in {"CONFIRMED", "ACKNOWLEDGED", "UNKNOWN", "REJECTED", "NOT_SENT"} else None})
        def performance_view(perf):
            if not isinstance(perf, dict):
                return None
            known = instant(perf.get("observed_at"))
            marks = perf.get("mark_times", [])
            if (known is not None and known <= observed and perf.get("status") in {"AVAILABLE", "INCOMPLETE", "NO_FILLS"}
                    and perf.get("currency") == ("KRW" if market == "KR" else "USD")
                    and perf.get("basis") == "STRATEGY_GROSS_CASHFLOWS_PLUS_MARKED_HOLDINGS"
                    and isinstance(marks, list) and all(instant(value) is not None and 0 <= (known-instant(value)).total_seconds() <= 120 for value in marks)):
                return {"status": perf["status"], "currency": perf["currency"], "observed_at": known.isoformat(),
                    "gross_pnl": number(perf.get("gross_pnl")) if perf["status"] == "AVAILABLE" else None,
                    "net_pnl": None, "fees_known": False, "settlement_known": False}
            return None
        view["performance"] = performance_view(row.get("performance"))
        view["evaluation"] = _strategy_evaluation_view(row.get("evaluation"), market, observed)
        for perf in (row.get("performance_history") if isinstance(row.get("performance_history"), list) else [])[-60:]:
            projected = performance_view(perf)
            if projected is not None and projected["status"] == "AVAILABLE":
                view["performance_history"].append(projected)
        result["markets"][market] = view
    return result
