"""Public-safe market progress, derived from sealed inputs; never order authority.

No account, journal, network, latest-pointer or scheduling dependency belongs here.
Original research is read only for the selected manifest's explicit artifacts.
"""
from __future__ import annotations

import copy
import hashlib
import json
import re
import stat
from datetime import date, datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from tradingagents.dataflows.research_evidence import REQUIRED_METHODS, assess_tool_evidence
from tradingagents.schemas.decision import parse_structured_decision

SCHEMA = "tradingagents.market-report-context/v1"
RESEARCH_SCHEMA = "tradingagents.work-research-readiness/v1"
_HASH = re.compile(r"[a-f0-9]{64}")
_TICKER = re.compile(r"(?:[0-9]{6}\.(?:KS|KQ)|[A-Z][A-Z0-9.\-]{0,19})")
_REASONS = {"VERIFIED", "NO_PRIOR_ACK", "ACK_UNVERIFIED", "CONTRACT_CHANGED"}
_PARSE = {"VALIDATED", "FALLBACK", "UNVERIFIED"}
_RESEARCH = {"COMPLETE", "REQUIRED_EVIDENCE_MISSING", "UNVERIFIED"}
_RESEARCH_REASONS = {"VERIFIED", "ORIGINAL_EVIDENCE_UNVERIFIED", "ORIGINAL_DECISION_MISMATCH",
                     "DECISION_FALLBACK", "DECISION_VALIDATION_UNVERIFIED", "REQUIRED_TOOLS_MISSING",
                     "TOOL_EVIDENCE_UNVERIFIED", "LEGACY_TOOL_EVIDENCE_UNVERIFIED", "FUTURE_SOURCE_CLOCK"}
_READINESS = {"READY_NOW", "WAIT_FOR_TRIGGER", "NEEDS_LIVE_RECHECK", "DATA_OUTAGE", "MARKET_CLOSED", "RESEARCH_ONLY"}
_ENTRY = {"STARTER", "ADD", "WAIT", "NONE"}
_RISK = {"HOLD", "NONE", "REDUCE_RISK", "TAKE_PROFIT", "EXIT", "STOP_LOSS"}
_STAGES = {
    "DATA": ("DATA_PRODUCER", "VERIFIED_CURRENT_MARKET_INPUTS"),
    "RESEARCH": ("RESEARCH_ENGINE", "VALIDATED_ORIGINAL_RESEARCH_AND_REQUIRED_TOOLS"),
    "DECISION": ("DECISION_ENGINE", "ORIGINAL_ENGINE_ACTION_AND_VALIDITY"),
    "PRIVATE_OPERATIONS": ("PRIVATE_OPERATIONS_REVIEW", "SEPARATE_PRIVATE_EXECUTION_AND_COST_PROOF"),
}


def instant(value: Any) -> datetime:
    if not isinstance(value, str):
        raise ValueError("Aware context clock required")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.utcoffset() is None:
        raise ValueError("Aware context clock required")
    return parsed


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                    separators=(",", ":")).encode()).hexdigest()


def bounded_file(root: Path, candidate: Path) -> Path:
    """Allow a configured root alias, reject any reparse/escape below it."""
    base = root.resolve(strict=True)
    # Check lexical components as well as the resolved destination: a junction
    # can point back inside the allowed root and must still be rejected.
    lexical = Path(candidate.absolute())
    lexical_base = Path(root.absolute())
    try:
        relative = lexical.relative_to(lexical_base)
    except ValueError as exc:
        raise ValueError("Context artifact outside its fixed root") from exc
    current = lexical_base
    for part in relative.parts:
        current = current / part
        item = current.lstat()
        if stat.S_ISLNK(item.st_mode) or getattr(item, "st_file_attributes", 0) & 0x400:
            raise ValueError("Context artifact reparse point")
    resolved = lexical.resolve(strict=True)
    resolved.relative_to(base)
    if not resolved.is_file():
        raise ValueError("Context artifact is not a regular file")
    return resolved


def _json_object(raw: bytes) -> dict:
    result = json.loads(raw)
    if not isinstance(result, dict):
        raise ValueError("Context object required")
    return result


def _decision(value: Any) -> dict:
    result = json.loads(value) if isinstance(value, str) else value
    if not isinstance(result, dict):
        raise ValueError("Original decision required")
    return result


def research_receipts(archive: Path, manifest: dict, rows: list, *, market: str, now: datetime) -> list[dict]:
    """Bind the existing canonical assessor to raw original analysis hash/clocks.

    A summary's status/COMPLETE assertion alone cannot pass this contract.
    Unverifiable legacy input stays unknown; a real model WAIT remains WAIT.
    """
    result = []
    summaries = {str(row.get("ticker")): row for row in manifest.get("tickers", []) if isinstance(row, dict)}
    manifest_hash = None
    run_dir = None
    try:
        run_id = str(manifest["run_id"])
        if not re.fullmatch(r"[A-Za-z0-9_\-]+", run_id):
            raise ValueError("Invalid original run identity")
        matches = list((archive / "runs").glob(f"*/{run_id}/run.json"))
        if len(matches) != 1 or str(manifest["settings"]["market"]).lower() != market:
            raise ValueError("Unverified original manifest")
        manifest_path = bounded_file(archive, matches[0])
        raw = manifest_path.read_bytes()
        if _json_object(raw) != manifest or not instant(manifest["started_at"]) <= instant(manifest["finished_at"]) <= now:
            raise ValueError("Original manifest clock or content mismatch")
        manifest_hash = hashlib.sha256(raw).hexdigest()
        run_dir = matches[0].parent
    except (OSError, ValueError, KeyError, TypeError):
        pass
    for row in rows:
        ticker = str(row.get("ticker") or "")
        item = {"ticker": ticker, "status": "UNVERIFIED", "decision_parse": "UNVERIFIED",
                "reason": "ORIGINAL_EVIDENCE_UNVERIFIED", "analysis_sha256": None,
                "manifest_sha256": manifest_hash, "started_at": None, "finished_at": None,
                "decision_sha256": None, "entry_action": None, "risk_action": None,
                "missing_required_methods": sorted(REQUIRED_METHODS)}
        result.append(item)
        try:
            summary = summaries[ticker]
            if run_dir is None or summary.get("status") != "success":
                raise ValueError("Original successful analysis unavailable")
            relative = summary["artifacts"]["analysis_json"]
            if not isinstance(relative, str) or Path(relative).is_absolute():
                raise ValueError("Invalid original analysis path")
            path = bounded_file(archive, run_dir / relative)
            path.relative_to(run_dir.resolve())
            raw = path.read_bytes()
            analysis = _json_object(raw)
            digest = hashlib.sha256(raw).hexdigest()
            reuse = summary.get("research_reuse") or {}
            expected_hash = (reuse.get("artifact_sha256") or {}).get("analysis_json")
            if expected_hash is not None and expected_hash != digest:
                raise ValueError("Reused original hash mismatch")
            started, finished = instant(analysis["started_at"]), instant(analysis["finished_at"])
            if (analysis.get("status") != "success" or analysis.get("ticker") != ticker
                    or analysis.get("decision") != summary.get("decision")
                    or analysis.get("started_at") != summary.get("started_at")
                    or analysis.get("finished_at") != summary.get("finished_at")
                    or not started <= finished <= instant(manifest["finished_at"]) <= now):
                raise ValueError("Original analysis identity or clock mismatch")
            for field in ("trade_date", "analysis_date"):
                if (not isinstance(analysis[field], str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", analysis[field])
                        or analysis[field] != summary.get(field)):
                    raise ValueError("Original analysis date mismatch")
            market_date = started.astimezone(ZoneInfo("Asia/Seoul" if market == "kr" else "America/New_York")).date()
            if (date.fromisoformat(analysis["analysis_date"]) != market_date
                    or date.fromisoformat(analysis["trade_date"]) > market_date):
                raise ValueError("Original research market-date contract mismatch")
            decision = _decision(analysis["decision"])
            parsed = parse_structured_decision(decision)
            flags = analysis.get("quality_flags")
            metrics = analysis.get("metrics")
            if not isinstance(flags, list) or not isinstance(metrics, dict):
                raise ValueError("Original decision validation evidence missing")
            parse_status = "FALLBACK" if (
                "decision_unvalidated" in flags or decision.get("fallback_reason")
                or set(parsed.risk_action_reason_codes) & {"STRUCTURED_DECISION_INVALID", "CODEX_PROVIDER_UNAVAILABLE"}
                or "TRADINGAGENTS_CODEX_FALLBACK_RESPONSE" in json.dumps(decision)
                or metrics.get("llm_fallback_calls") not in (0, None)
            ) else "VALIDATED" if metrics.get("llm_fallback_calls") == 0 else "UNVERIFIED"
            assessed = assess_tool_evidence(analysis.get("tool_telemetry") or {},
                started_at=analysis["started_at"], finished_at=analysis["finished_at"])
            item.update(analysis_sha256=digest, started_at=analysis["started_at"], finished_at=analysis["finished_at"],
                        decision_sha256=_digest(decision), decision_parse=parse_status,
                        entry_action=parsed.entry_action.value, risk_action=parsed.risk_action.value)
            if parse_status != "VALIDATED":
                item["reason"] = "DECISION_FALLBACK" if parse_status == "FALLBACK" else "DECISION_VALIDATION_UNVERIFIED"
            elif assessed is not None and assessed.get("status") in _RESEARCH:
                item.update(status=assessed["status"], missing_required_methods=assessed["missing_required_methods"],
                            reason="VERIFIED" if assessed["status"] == "COMPLETE" else
                            "REQUIRED_TOOLS_MISSING" if assessed["status"] == "REQUIRED_EVIDENCE_MISSING" else
                            "TOOL_EVIDENCE_UNVERIFIED")
            else:
                item["reason"] = "LEGACY_TOOL_EVIDENCE_UNVERIFIED"
            if path.read_bytes() != raw:
                raise ValueError("Original analysis changed during receipt")
        except (OSError, ValueError, KeyError, TypeError, AttributeError):
            item.update(status="UNVERIFIED", decision_parse="UNVERIFIED", reason="ORIGINAL_EVIDENCE_UNVERIFIED")
    if run_dir is not None:
        raw_manifest_bytes(manifest_path, manifest_hash)
    return result


def raw_manifest_bytes(path: Path, expected_hash: str) -> bytes:
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected_hash:
        raise ValueError("Original manifest changed during receipt")
    return raw


def _enum(value: Any, allowed: set[str]) -> str | None:
    return value if isinstance(value, str) and value in allowed else None


def project_market(body: dict, *, market: str) -> list[dict]:
    if body.get("kind") != "market" or body.get("market") != market.upper():
        raise ValueError("Report context market mismatch")
    current = body.get("current") or {}
    receipts = {row["ticker"]: row for row in current.get("research_readiness", [])}
    result = []
    seen = set()
    for row in (current.get("bundle") or {}).get("strategy_table", []):
        ticker = row.get("ticker")
        if (not isinstance(ticker, str) or not _TICKER.fullmatch(ticker) or ticker in seen
                or (market == "kr") != bool(re.fullmatch(r"[0-9]{6}\.(?:KS|KQ)", ticker))):
            raise ValueError("Report context ticker market mismatch or duplicate")
        seen.add(ticker)
        thesis, execution = row.get("thesis") or {}, row.get("execution") or {}
        proof = receipts.get(ticker) or {}
        bound = (bool(proof.get("decision_sha256")) and proof.get("decision_sha256") == thesis.get("decision_sha256")
                 and proof.get("finished_at") is not None and proof.get("finished_at") == thesis.get("analysis_asof"))
        result.append({"ticker": ticker,
            "decision_sha256": thesis.get("decision_sha256") if _HASH.fullmatch(str(thesis.get("decision_sha256"))) else None,
            "analysis_asof": _safe_clock(thesis.get("analysis_asof")) if _HASH.fullmatch(str(thesis.get("decision_sha256"))) else None,
            "market_data_asof": _safe_clock(row.get("market_data_asof")),
            "stance": _enum(thesis.get("stance"), {"BUY", "HOLD", "REDUCE", "SELL", "AVOID", "RESEARCH"}),
            "entry_action": _enum(proof.get("entry_action"), _ENTRY) if bound else None,
            "risk_action": _enum(proof.get("risk_action"), _RISK) if bound else None,
            "execution_readiness": _enum(execution.get("readiness"), _READINESS),
            "research_status": (_enum(proof.get("status"), _RESEARCH) or "UNVERIFIED") if bound else "UNVERIFIED",
            "decision_parse": (_enum(proof.get("decision_parse"), _PARSE) or "UNVERIFIED") if bound else "UNVERIFIED",
            "research_reason": (_enum(proof.get("reason"), _RESEARCH_REASONS) or "ORIGINAL_EVIDENCE_UNVERIFIED") if bound else
                               "ORIGINAL_DECISION_MISMATCH" if proof.get("decision_sha256") else "ORIGINAL_EVIDENCE_UNVERIFIED",
            "analysis_sha256": proof.get("analysis_sha256") if bound and _HASH.fullmatch(str(proof.get("analysis_sha256"))) else None,
            "manifest_sha256": proof.get("manifest_sha256") if bound and _HASH.fullmatch(str(proof.get("manifest_sha256"))) else None,
            "missing_required_methods": sorted(set(proof.get("missing_required_methods", REQUIRED_METHODS)) & REQUIRED_METHODS)})
    return sorted(result, key=lambda row: row["ticker"])


def _safe_clock(value: Any) -> str | None:
    try:
        instant(value)
        return value
    except (ValueError, TypeError):
        return None


def make_context(body: dict, *, market: str, cutoff: datetime, baseline: dict,
                 prior_body: dict | None, comparable: bool) -> dict:
    if cutoff.utcoffset() is None:
        raise ValueError("Aware report comparison cutoff required")
    rows = project_market(body, market=market)
    # Future source receipts cannot become a historical comparison or claim.
    for row in rows:
        if any(instant(row[key]) > cutoff for key in ("analysis_asof", "market_data_asof") if row[key]):
            row.update(research_status="UNVERIFIED", decision_parse="UNVERIFIED", research_reason="FUTURE_SOURCE_CLOCK")
    current = body.get("current") or {}
    freshness = current.get("freshness_receipt") or {}
    data_status = freshness.get("market_data_status")
    if any(row["market_data_asof"] is None for row in rows):
        data_status = "UNVERIFIED"
    elif any(instant(row["market_data_asof"]) > cutoff for row in rows):
        data_status = "INVALID"
    stage = "DATA" if data_status != "FRESH" or not rows else "RESEARCH" if any(
        row["research_status"] != "COMPLETE" or row["decision_parse"] != "VALIDATED" for row in rows
    ) else "DECISION" if not any(row["execution_readiness"] in {"READY_NOW", "WAIT_FOR_TRIGGER"} for row in rows) else "PRIVATE_OPERATIONS"
    role, condition = _STAGES[stage]
    changes = []
    comparison = "VERIFIED" if comparable and prior_body is not None else "NOT_COMPARABLE"
    if comparison == "VERIFIED":
        prior = {row["ticker"]: row for row in project_market(prior_body, market=market)}
        current_rows = {row["ticker"]: row for row in rows}
        for ticker in sorted(prior.keys() | current_rows.keys()):
            old, new = prior.get(ticker), current_rows.get(ticker)
            fields = sorted(key for key in old if key != "ticker" and old[key] != new[key]) if old and new else []
            if old is None or new is None or fields:
                changes.append({"ticker": ticker, "kind": "ADDED_RESEARCH" if old is None else "REMOVED_RESEARCH" if new is None else "MARKET_INPUT_CHANGED",
                                "fields": fields, "before": old, "after": new,
                                "before_sha256": _digest(old), "after_sha256": _digest(new)})
    result = {"schema": SCHEMA, "scope": "PUBLIC_MARKET_INPUTS_ONLY", "market": market.upper(),
              "comparison_cutoff": cutoff.isoformat(), "prior_ack": copy.deepcopy(baseline),
              "comparison_status": comparison, "market_inputs": rows, "changes": changes,
              "first_unmet": {"stage": stage, "responsible_role": role, "next_condition": condition},
              "data_status": data_status if data_status in {"FRESH", "STALE", "MISSING", "INVALID"} else "UNVERIFIED",
              "private_execution_cost_status": "NOT_PROVIDED", "ack_is_investment_approval": False,
              "automatic_live_transition": False}
    validate_context(result)
    return result


def validate_context(value: Any) -> None:
    """Closed public schema: arbitrary LLM fields cannot carry private receipts."""
    if not isinstance(value, dict) or set(value) != {"schema", "scope", "market", "comparison_cutoff", "prior_ack", "comparison_status", "market_inputs", "changes", "first_unmet", "data_status", "private_execution_cost_status", "ack_is_investment_approval", "automatic_live_transition"}:
        raise ValueError("Invalid public report context keys")
    if (value["schema"] != SCHEMA or value["scope"] != "PUBLIC_MARKET_INPUTS_ONLY" or value["market"] not in {"KR", "US"}
            or value["private_execution_cost_status"] != "NOT_PROVIDED" or value["ack_is_investment_approval"] is not False
            or value["automatic_live_transition"] is not False or value["data_status"] not in {"FRESH", "STALE", "MISSING", "INVALID", "UNVERIFIED"}):
        raise ValueError("Invalid public report context constants")
    cutoff = instant(value["comparison_cutoff"])
    prior = value["prior_ack"]
    if not isinstance(prior, dict) or set(prior) != {"status", "reason", "event_id", "source_sha256", "report_sha256", "workflow_contract_sha256", "acknowledged_at", "ledger_revision"}:
        raise ValueError("Invalid prior ACK receipt keys")
    if prior["status"] not in {"VERIFIED", "NO_PRIOR_ACK", "UNVERIFIED"} or prior["reason"] not in _REASONS:
        raise ValueError("Invalid prior ACK status")
    if prior["status"] == "VERIFIED":
        if (prior["reason"] != "VERIFIED" or instant(prior["acknowledged_at"]) > cutoff
                or not re.fullmatch(value["market"].lower() + r":[a-f0-9]{32}", str(prior["event_id"]))
                or type(prior["ledger_revision"]) is not int or prior["ledger_revision"] < 1
                or any(not _HASH.fullmatch(str(prior[key])) for key in ("source_sha256", "report_sha256", "workflow_contract_sha256"))):
            raise ValueError("Invalid prior ACK binding")
    elif any(prior[key] is not None for key in prior if key not in {"status", "reason"}):
        raise ValueError("Unverified prior ACK must not expose unverified metadata")
    if value["comparison_status"] not in {"VERIFIED", "NOT_COMPARABLE"} or (value["comparison_status"] == "VERIFIED" and prior["status"] != "VERIFIED"):
        raise ValueError("Invalid comparison status")
    stage = value["first_unmet"]
    if not isinstance(stage, dict) or set(stage) != {"stage", "responsible_role", "next_condition"} or stage.get("stage") not in _STAGES or (stage["responsible_role"], stage["next_condition"]) != _STAGES[stage["stage"]]:
        raise ValueError("Invalid report progress contract")
    rows = value["market_inputs"]
    if not isinstance(rows, list) or len(rows) > 250:
        raise ValueError("Invalid report market inputs")
    seen = set()
    for row in rows:
        _validate_row(row, market=value["market"])
        if row["ticker"] in seen:
            raise ValueError("Repeated context ticker")
        seen.add(row["ticker"])
    if not isinstance(value["changes"], list) or len(value["changes"]) > 500 or (value["comparison_status"] != "VERIFIED" and value["changes"]):
        raise ValueError("Invalid report change list")
    for change in value["changes"]:
        if not isinstance(change, dict) or set(change) != {"ticker", "kind", "fields", "before", "after", "before_sha256", "after_sha256"}:
            raise ValueError("Invalid report change keys")
        old, new = change["before"], change["after"]
        if old is None and new is None:
            raise ValueError("Empty report change")
        for row in (old, new):
            if row is not None:
                _validate_row(row, market=value["market"])
                if row["ticker"] != change["ticker"]:
                    raise ValueError("Change ticker mismatch")
        expected_kind = "ADDED_RESEARCH" if old is None else "REMOVED_RESEARCH" if new is None else "MARKET_INPUT_CHANGED"
        expected_fields = sorted(key for key in old if key != "ticker" and old[key] != new[key]) if old and new else []
        if (change["kind"] != expected_kind or change["fields"] != expected_fields
                or (old == new) or change["before_sha256"] != _digest(old) or change["after_sha256"] != _digest(new)):
            raise ValueError("Invalid report change proof")


def _validate_row(row: Any, *, market: str) -> None:
    keys = {"ticker", "decision_sha256", "analysis_asof", "market_data_asof", "stance", "entry_action", "risk_action", "execution_readiness", "research_status", "decision_parse", "research_reason", "analysis_sha256", "manifest_sha256", "missing_required_methods"}
    if not isinstance(row, dict) or set(row) != keys:
        raise ValueError("Invalid public market input keys")
    ticker = row["ticker"]
    if not isinstance(ticker, str) or not _TICKER.fullmatch(ticker) or (market == "KR") != bool(re.fullmatch(r"[0-9]{6}\.(?:KS|KQ)", ticker)):
        raise ValueError("Invalid context ticker market")
    for key in ("decision_sha256", "analysis_sha256", "manifest_sha256"):
        if row[key] is not None and not _HASH.fullmatch(str(row[key])):
            raise ValueError("Invalid original research hash")
    for key in ("analysis_asof", "market_data_asof"):
        if row[key] is not None:
            instant(row[key])
    for key, allowed in (("stance", {"BUY", "HOLD", "REDUCE", "SELL", "AVOID", "RESEARCH"}), ("entry_action", _ENTRY), ("risk_action", _RISK), ("execution_readiness", _READINESS)):
        if row[key] is not None and row[key] not in allowed:
            raise ValueError("Invalid public market enum")
    if row["research_status"] not in _RESEARCH or row["decision_parse"] not in _PARSE or row["research_reason"] not in _RESEARCH_REASONS or not isinstance(row["missing_required_methods"], list) or row["missing_required_methods"] != sorted(set(row["missing_required_methods"]) & REQUIRED_METHODS):
        raise ValueError("Invalid original research receipt")
    if row["research_status"] == "COMPLETE" and (row["decision_parse"] != "VALIDATED" or row["research_reason"] != "VERIFIED"
            or row["missing_required_methods"] or any(row[key] is None for key in ("decision_sha256", "analysis_sha256", "manifest_sha256", "analysis_asof"))):
        raise ValueError("Incomplete original research proof")


def empty_baseline(status: str = "NO_PRIOR_ACK") -> dict:
    return {"status": status, "reason": "NO_PRIOR_ACK" if status == "NO_PRIOR_ACK" else "ACK_UNVERIFIED",
            "event_id": None, "source_sha256": None, "report_sha256": None, "workflow_contract_sha256": None,
            "acknowledged_at": None, "ledger_revision": None}


def validate_public_report_envelope(draft: dict) -> None:
    """The new contract cannot move private receipts outside the closed context.

    Existing exact-copy coverage/freshness/model receipts retain their historical
    public shape. No silent redaction or byte rewriting is performed here.
    """
    allowed = {"binding", "title", "generated_at", "as_of", "source_health", "report_mode", "summary",
               "top_actions", "strategies", "coverage_receipt", "model_receipt", "source_summary", "next_checkpoint"}
    if set(draft) - allowed:
        raise ValueError("Unsupported new public report field")
    source_keys = {"analysis_receipt", "policy", "freshness_receipt", "external_evidence_receipt", "report_context_receipt"}
    if set(draft.get("source_summary") or {}) - source_keys:
        raise ValueError("Unsupported new public source summary field")
    strategy_keys = {"ticker", "display_name", "rank", "portfolio_role", "thesis", "execution",
                     "source_contributions", "no_relevant_evidence_reason"}
    thesis_keys = {"stance", "horizon", "confidence", "rationale", "entry_conditions", "invalidation_conditions",
                   "invalidation_action", "position_sizing", "research_priority", "data_needed_reason",
                   "major_news_issues", "bullish_drivers", "bearish_drivers", "risk_limits", "execution_levels",
                   "profit_taking_plan", "risk_action", "risk_action_reason", "risk_action_level",
                   "conditional_entry_action", "conditional_entry_valid_until", "rating", "portfolio_stance",
                   "setup_quality", "risk_action_reason_codes", "risk_action_confidence"}
    thesis_keys.add("stance_change")
    execution_keys = {"readiness", "as_of", "valid_until", "action_now", "action_if_triggered", "required_rechecks", "blockers"}
    for row in draft.get("strategies") or []:
        if (not isinstance(row, dict) or set(row) - strategy_keys or set(row.get("thesis") or {}) - thesis_keys
                or set(row.get("execution") or {}) - execution_keys):
            raise ValueError("Unsupported new public strategy field")
    for action in draft.get("top_actions") or []:
        if not isinstance(action, dict) or set(action) - {"ticker", "readiness", "action"}:
            raise ValueError("Unsupported new public action field")
    blocked = {"actualcost", "actualfee", "actualtax", "actualfxcost", "netpnl", "grosspnl", "realizedpnl",
               "settlementreceipt", "privatecostreceipt", "owner", "ownerid", "accountid", "accountnumber",
               "accountno", "brokerorderid", "positionquantity", "filledquantity", "cashbalance", "ledgerpath",
               "pid", "localpath"}

    def inspect(value):
        if isinstance(value, dict):
            for key, item in value.items():
                if re.sub(r"[^a-z0-9]", "", str(key).lower()) in blocked:
                    raise ValueError("Private operational receipt in public report")
                inspect(item)
        elif isinstance(value, list):
            for item in value:
                inspect(item)

    inspect(draft)
