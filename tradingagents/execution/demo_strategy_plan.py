"""Allocate explicitly approved strategy signals against the demo account only.

The existing per-order broker caps remain unchanged. This mode allocates at most
one share per thesis/direction and never promotes a watch level into a buy. Real
account cash, positions and proposed orders are advisory artifacts, not VTS funds.
"""
from collections import Counter
from datetime import timedelta
import hashlib
import json

from .demo_validation import _at
from tradingagents.dataflows.research_evidence import assess_tool_evidence, evidence_review_reason
from tradingagents.schemas import parse_structured_decision

MODE = "DEMO_NATIVE_ONE_SHARE_V1"
BUY = {"STARTER_NOW", "ADD_NOW", "BUY_NOW"}
SELL = {"REDUCE_NOW", "EXIT_NOW", "STOP_LOSS_NOW"}
HARD_BUY_GATES = {"blocked_new_entries_no_tool_calls", "blocked_new_entries_company_news_zero",
                  "high_fallback_count", "required_research_evidence_missing", "prism_conflict_review_required", "BUY_MATRIX_FAIL"}


def _original_entry_research(read, ticker, contract, generated, candidate):
    """A derived portfolio row cannot grant or extend the original approval."""
    try:
        analysis = read(f"tickers/{ticker}/analysis.json")
        started, finished = _at(analysis.get("started_at")), _at(analysis.get("finished_at"))
        if (analysis.get("ticker") != ticker or analysis.get("status") != "success"
                or not started <= finished <= generated
                or finished != _at(contract.get("analysis_asof"))):
            raise ValueError("Unverified original research identity or clock")
        original = parse_structured_decision(analysis.get("decision")).to_dict()
    except (ValueError, TypeError, KeyError, OSError, AttributeError) as exc:
        raise ValueError("ENTRY_ORIGINAL_RESEARCH_UNVERIFIED") from exc
    try:
        derived = parse_structured_decision(candidate.get("structured_decision")).to_dict()
    except (ValueError, TypeError, KeyError, AttributeError) as exc:
        raise ValueError("ENTRY_RESEARCH_DECISION_MISMATCH") from exc
    if original != derived:
        raise ValueError("ENTRY_RESEARCH_DECISION_MISMATCH")
    conditional = original["conditional_entry_action"]
    authorized = conditional if conditional in {"STARTER", "ADD"} else original["entry_action"]
    if authorized not in {"STARTER", "ADD"}:
        raise ValueError("ENTRY_NOT_AUTHORIZED_BY_RESEARCH")
    if (contract.get("action_if_triggered") != authorized
            or contract.get("entry_action_base") != original["entry_action"]
            or contract.get("risk_action") != original["risk_action"]):
        raise ValueError("ENTRY_AUTHORIZATION_MISMATCH")
    return analysis, original


def plan(source, market, now, tickers, owned):
    def read(name):
        return json.loads((source / name).read_text(encoding="utf-8-sig"))

    manifest, bundle = read("run.json"), read("decision_bundle_v2.json")
    generated = _at(bundle["generated_at"])
    if (manifest.get("status") != "success" or str(bundle.get("market")).upper() != market
            or str((manifest.get("settings") or {}).get("market")).upper() != market
            or not generated <= _at(manifest["finished_at"]) <= now):
        raise ValueError("STRATEGY_SOURCE_UNVERIFIED")
    research = read("portfolio-private/portfolio_candidates.json")["candidates"]
    by_ticker = {}
    for candidate in research:
        ticker = candidate["instrument"]["canonical_ticker"]
        if ticker in by_ticker:
            raise ValueError("AMBIGUOUS_STRATEGY_RESEARCH")
        by_ticker[ticker] = candidate
    counts, rejected, result, seen = Counter(), {}, [], set()
    for row in bundle["strategy_table"]:
        ticker = row["ticker"]
        if ticker in seen:
            raise ValueError("AMBIGUOUS_STRATEGY_ROW")
        seen.add(ticker)
        decision = (row.get("raw_codes") or {}).get("decision_now")
        side = "BUY" if decision in BUY else "SELL" if decision in SELL else None
        reason = None
        if side is None:
            reason = "NO_AUTHORIZED_EXECUTION_ACTION"
        elif ticker not in tickers:
            reason = "OUTSIDE_APPROVED_UNIVERSE"
        elif side == "SELL" and owned.get(ticker, 0) <= 0:
            reason = "NO_STRATEGY_OWNED_POSITION"
        elif side == "BUY" and owned.get(ticker, 0) > 0:
            reason = "STRATEGY_POSITION_ALREADY_OPEN"
        if reason is None:
            try:
                observed = _at(row.get("market_data_asof"))
                quality = row.get("quality") or {}
                if not (observed <= generated <= now < observed + timedelta(seconds=120)
                        and quality.get("execution_ready") is True
                        and quality.get("generated_in_current_run") is True
                        and row.get("market_session") == "regular"):
                    raise ValueError("STRATEGY_OBSERVATION_NOT_EXECUTABLE")
                contract = read(f"tickers/{ticker}/execution_contract.json")
                update = read(f"tickers/{ticker}/execution_update.json")
                if (contract.get("ticker") != ticker or update.get("ticker") != ticker
                        or update.get("decision_now") != decision
                        or update.get("analysis_asof") != contract.get("analysis_asof")
                        or _at(contract.get("analysis_asof")) > generated
                        or _at(update.get("execution_asof")) > generated
                        or _at(update.get("market_data_asof")) != observed):
                    raise ValueError("STRATEGY_LINEAGE_MISMATCH")
                expiry = observed + timedelta(seconds=120)
                if side == "SELL" and decision == "REDUCE_NOW" and contract.get("risk_action") not in {"REDUCE_RISK", "STOP_LOSS", "EXIT"}:
                    # A one-share account cannot infer a discretionary trim or
                    # profit-taking fraction/core-retention policy.
                    raise ValueError("SELL_SIZE_REQUIRES_EXPLICIT_ALLOCATION")
                if side == "BUY":
                    research_row = by_ticker.get(ticker) or {}
                    analysis, structured = _original_entry_research(read, ticker, contract, generated, research_row)
                    conditional = structured["conditional_entry_action"]
                    if conditional in {"STARTER", "ADD"}:
                        research_expiry = _at(structured.get("conditional_entry_valid_until"))
                        if _at(contract.get("entry_valid_until")) != research_expiry:
                            raise ValueError("ENTRY_AUTHORIZATION_MISMATCH")
                        expiry = min(expiry, research_expiry)
                    elif now - _at(contract["analysis_asof"]) >= timedelta(hours=24):
                        raise ValueError("ENTRY_RESEARCH_EXPIRED")
                    health = research_row.get("data_health") or {}
                    if (research_row.get("review_required") is True or health.get("reanalysis_required") is True
                            or set(research_row.get("gate_reasons") or []) & HARD_BUY_GATES
                            or (research_row.get("buy_matrix") or {}).get("fail_reasons")):
                        raise ValueError("ENTRY_RESEARCH_REVIEW_REQUIRED")
                    # New demo positions must satisfy new-entry evidence even
                    # if the reporting account already owns this instrument.
                    coverage, vendor = research_row.get("data_coverage") or {}, research_row.get("vendor_health") or {}
                    original_telemetry = analysis.get("tool_telemetry") or {}
                    original_evidence = assess_tool_evidence(original_telemetry,
                        started_at=analysis.get("started_at"), finished_at=analysis.get("finished_at"))
                    original_health = {"fallback_count": original_telemetry.get("fallback_count", 0)}
                    if original_evidence is not None or "request_evidence" in vendor:
                        if original_evidence is None or original_evidence != vendor.get("request_evidence"):
                            raise ValueError("ENTRY_RESEARCH_EVIDENCE_INCOMPLETE")
                        original_health["request_evidence"] = original_evidence
                    if (coverage.get("company_news_count", 0) < 1 or evidence_review_reason(vendor)
                            or structured["data_coverage"]["company_news_count"] < 1
                            or evidence_review_reason(original_health)
                            or "no_tool_calls_detected" in (analysis.get("quality_flags") or [])
                            or "no_tool_calls_detected" in (research_row.get("quality_flags") or [])):
                        raise ValueError("ENTRY_RESEARCH_EVIDENCE_INCOMPLETE")
                if now >= expiry:
                    raise ValueError("STRATEGY_AUTHORIZATION_EXPIRED")
                thesis = {key: value for key, value in contract.items()
                          if key not in {"event_time", "ingested_at", "evaluated_at"}}
                digest = hashlib.sha256(json.dumps(thesis, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
                identity = f"strategy-native-v1:{market}:{ticker}:{side}:{digest}"
                signal = {"signal_id": identity, "ticker": ticker[:6] if market == "KR" else ticker,
                          "decision_now": "STARTER_NOW" if side == "BUY" else "EXIT_NOW" if decision in {"EXIT_NOW", "STOP_LOSS_NOW"} else "REDUCE_NOW",
                          "execution_ready": True, "available_at": generated.isoformat(), "valid_until": expiry.isoformat()}
                result.append({"id": identity, "ticker": ticker, "side": side, "signal": signal,
                               "run_id": source.name, "allocation_mode": MODE,
                               "evidence": {"source_run_id": source.name, "contract_sha256": digest,
                                   "decision_now": decision, "market_data_asof": observed.isoformat(),
                                   "generated_at": generated.isoformat(), "allocation_mode": MODE,
                                   "maximum_shares": 1, "real_account_allocation_used": False}})
            except (ValueError, TypeError, KeyError, OSError) as exc:
                reason = str(exc) if str(exc) in {
                    "STRATEGY_OBSERVATION_NOT_EXECUTABLE", "STRATEGY_LINEAGE_MISMATCH",
                    "ENTRY_ORIGINAL_RESEARCH_UNVERIFIED", "ENTRY_RESEARCH_DECISION_MISMATCH",
                    "ENTRY_NOT_AUTHORIZED_BY_RESEARCH", "ENTRY_AUTHORIZATION_MISMATCH", "ENTRY_RESEARCH_EXPIRED",
                    "ENTRY_RESEARCH_REVIEW_REQUIRED", "ENTRY_RESEARCH_EVIDENCE_INCOMPLETE",
                    "STRATEGY_AUTHORIZATION_EXPIRED", "SELL_SIZE_REQUIRES_EXPLICIT_ALLOCATION"} else "STRATEGY_EVIDENCE_UNVERIFIED"
        if reason:
            counts[reason] += 1
            rejected[ticker] = reason
    diagnostic = {"allocation_mode": MODE, "eligible_candidates": len(result),
                  "reason_counts": dict(counts), "ticker_blockers": rejected,
                  "research_entry_actions": dict(Counter((row.get("structured_decision") or {}).get("entry_action", "MISSING") for row in research)),
                  "research_conditional_entries": dict(Counter((row.get("structured_decision") or {}).get("conditional_entry_action", "MISSING") for row in research)),
                  "strategy_owned_positions": sum(qty > 0 for qty in owned.values()),
                  "real_account_allocation_used": False}
    return sorted(result, key=lambda item: (item["side"] == "BUY", item["ticker"])), diagnostic
