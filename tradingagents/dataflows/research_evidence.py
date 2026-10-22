"""Assess completed tool requests, independently of provider failover counts.

Only newly recorded, correlated requests can use this policy. Old analyses keep
their original conservative gate. Optional context never supplies missing core
price, company news, financial statements, or disclosure evidence.
"""
from __future__ import annotations

from datetime import datetime
import re

SCHEMA = "tradingagents.research-tool-requests/v1"
REQUIRED_METHODS = frozenset({
    "get_stock_data", "get_indicators", "get_company_news", "get_fundamentals",
    "get_balance_sheet", "get_cashflow", "get_income_statement", "get_disclosures",
})


def _at(value):
    result = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if result.tzinfo is None:
        raise ValueError("Aware tool evidence time required")
    return result


def assess_tool_evidence(telemetry, *, started_at, finished_at):
    """Return None for legacy evidence; malformed new receipts remain blocked."""
    if "request_outcomes" not in telemetry and "request_schema" not in telemetry:
        return None
    invalid = {"schema": SCHEMA, "status": "UNVERIFIED", "missing_required_methods": sorted(REQUIRED_METHODS)}
    try:
        if telemetry.get("request_schema") != SCHEMA:
            return invalid
        started, finished = _at(started_at), _at(finished_at)
        if finished < started:
            return invalid
        outcomes, events = telemetry["request_outcomes"], telemetry["events"]
        if not isinstance(outcomes, list) or not outcomes or not isinstance(events, list):
            return invalid
        by_id, by_method = {}, {}
        for row in outcomes:
            identity, method, status = row["request_id"], row["method"], row["status"]
            if (not isinstance(identity, str) or not re.fullmatch(r"[a-f0-9]{32}", identity)
                    or identity in by_id or not isinstance(method, str) or not method.startswith("get_")
                    or status not in {"available", "unavailable", "input_error", "error"}
                    or not started <= _at(row["started_at"]) <= _at(row["completed_at"]) <= finished):
                return invalid
            if status == "available" and not re.fullmatch(r"[a-f0-9]{64}", str(row.get("result_sha256", ""))):
                return invalid
            by_id[identity] = row
            by_method.setdefault(method, []).append(row)
        recovered = set()
        for event in events:
            row = by_id.get(event.get("request_id"))
            if row is None or row["method"] != event.get("method"):
                return invalid
            if event.get("fallback") is True and row["status"] == "available":
                recovered.add(row["request_id"])
        unavailable = {method for method, rows in by_method.items()
                       if any(row["status"] != "available" for row in rows)}
        missing = sorted(REQUIRED_METHODS - by_method.keys() | REQUIRED_METHODS & unavailable)
        return {"schema": SCHEMA, "status": "COMPLETE" if not missing else "REQUIRED_EVIDENCE_MISSING",
                "missing_required_methods": missing,
                "optional_unavailable_methods": sorted(unavailable - REQUIRED_METHODS),
                "request_count": len(outcomes), "recovered_request_count": len(recovered)}
    except (KeyError, TypeError, ValueError, AttributeError):
        return invalid


def evidence_review_reason(vendor_health):
    """Keep all legacy failures blocked until genuinely new evidence exists."""
    evidence = vendor_health.get("request_evidence")
    if evidence is not None:
        if not isinstance(evidence, dict) or evidence.get("schema") != SCHEMA or evidence.get("status") != "COMPLETE":
            return "required_research_evidence_missing"
        return None
    return "high_fallback_count" if int(vendor_health.get("fallback_count", 0) or 0) >= 3 else None


def evidence_risk_count(vendor_health):
    """Retain optional gaps as uncertainty without counting recovered attempts."""
    evidence = vendor_health.get("request_evidence")
    if evidence is None:
        return int(vendor_health.get("fallback_count", 0) or 0)
    if not isinstance(evidence, dict) or evidence.get("schema") != SCHEMA:
        return len(REQUIRED_METHODS)
    return len(evidence.get("missing_required_methods", REQUIRED_METHODS)) + len(evidence.get("optional_unavailable_methods", []))
