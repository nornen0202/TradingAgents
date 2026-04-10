from __future__ import annotations

import json
from json import JSONDecodeError
from pathlib import Path
from typing import Any, Mapping

from tradingagents.llm_clients import create_llm_client

from .account_models import PortfolioCandidate
from .instrument_identity import resolve_identity


def build_semantic_verdicts(
    *,
    candidates: list[PortfolioCandidate],
    run_dir: Path,
    manifest: dict[str, Any],
    llm_settings: Any | None,
    portfolio_settings: Any,
) -> tuple[list[PortfolioCandidate], list[dict[str, Any]], list[str]]:
    contexts = _load_context_by_ticker(run_dir, manifest)
    warnings: list[str] = []

    llm = None
    semantic_llm_enabled = bool(getattr(portfolio_settings, "semantic_judge_enabled", False))
    if semantic_llm_enabled:
        try:
            llm = _create_semantic_llm(llm_settings)
        except Exception as exc:
            warnings.append(f"semantic_judge_unavailable: {exc}")

    judged: list[PortfolioCandidate] = []
    verdicts: list[dict[str, Any]] = []
    for candidate in candidates:
        context = contexts.get(candidate.instrument.canonical_ticker) or {}
        base_verdict = _heuristic_verdict(candidate)
        verdict = dict(base_verdict)
        decision_source = "RULE_ONLY"

        should_call_llm = semantic_llm_enabled and llm is not None and _should_call_semantic_llm(candidate)
        if should_call_llm:
            try:
                payload = _invoke_semantic_llm(llm, _build_prompt(candidate, context))
                verdict = _normalize_verdict(base_verdict, payload)
                decision_source = "RULE+DEEP"
            except Exception as exc:
                decision_source = "RULE_ONLY_FALLBACK"
                verdict["review_required"] = True
                verdict["reason_codes"] = list(
                    dict.fromkeys([*verdict.get("reason_codes", []), "semantic_judge_fallback"])
                )
                warnings.append(f"{candidate.instrument.canonical_ticker}: semantic_judge_failed ({exc})")
        elif semantic_llm_enabled and _should_call_semantic_llm(candidate):
            decision_source = "RULE_ONLY_FALLBACK"
            verdict["review_required"] = True
            verdict["reason_codes"] = list(
                dict.fromkeys([*verdict.get("reason_codes", []), "semantic_judge_skipped"])
            )

        trigger_profile = {
            "primary_trigger_type": verdict["trigger_type"],
            "trigger_horizon": verdict["trigger_horizon"],
            "trigger_quality": verdict["trigger_quality"],
            "entry_readiness": verdict["timing_readiness"],
            "thesis_state": verdict["thesis_state"],
            "semantic_summary": verdict["semantic_summary"],
        }
        reason_codes = tuple(str(item) for item in verdict.get("reason_codes", []))

        judged.append(
            PortfolioCandidate(
                **{
                    **candidate.__dict__,
                    "trigger_profile": trigger_profile,
                    "decision_source": decision_source,
                    "thesis_strength": float(verdict["thesis_strength"]),
                    "timing_readiness": float(verdict["timing_readiness"]),
                    "reason_codes": reason_codes,
                    "review_required": bool(verdict["review_required"]),
                    "rationale": str(verdict["semantic_summary"] or candidate.rationale),
                    "data_health": {
                        **candidate.data_health,
                        "trigger_quality": float(verdict["trigger_quality"]),
                        "decision_source": decision_source,
                        "timing_readiness": float(verdict["timing_readiness"]),
                    },
                }
            )
        )
        verdicts.append(
            {
                "canonical_ticker": candidate.instrument.canonical_ticker,
                "display_name": candidate.instrument.display_name,
                "decision_source": decision_source,
                **verdict,
            }
        )

    return judged, verdicts, warnings


def _load_context_by_ticker(run_dir: Path, manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    loaded: dict[str, dict[str, Any]] = {}
    for ticker_summary in manifest.get("tickers", []):
        if ticker_summary.get("status") != "success":
            continue
        artifacts = ticker_summary.get("artifacts") or {}
        analysis_json = artifacts.get("analysis_json")
        final_state_json = artifacts.get("final_state_json")
        if not analysis_json:
            continue

        analysis_path = run_dir / analysis_json
        final_state_path = (run_dir / final_state_json) if final_state_json else None
        if not analysis_path.exists():
            continue

        analysis_payload = json.loads(analysis_path.read_text(encoding="utf-8"))
        final_state_payload = (
            json.loads(final_state_path.read_text(encoding="utf-8"))
            if final_state_path and final_state_path.exists()
            else {}
        )
        try:
            identity = resolve_identity(
                str(analysis_payload.get("ticker") or ticker_summary.get("ticker") or ""),
                str(analysis_payload.get("ticker_name") or ticker_summary.get("ticker_name") or "") or None,
            )
        except Exception:
            continue
        loaded[identity.canonical_ticker] = {
            "analysis": analysis_payload,
            "final_state": final_state_payload,
        }
    return loaded


def _should_call_semantic_llm(candidate: PortfolioCandidate) -> bool:
    if candidate.suggested_action_now not in {"HOLD", "WATCH"}:
        return True
    if candidate.suggested_action_if_triggered not in {"NONE", "WATCH_TRIGGER"}:
        return True
    if candidate.entry_action in {"WAIT", "EXIT"}:
        return True
    if int(candidate.vendor_health.get("fallback_count", 0) or 0) >= 2:
        return True
    quality_flags = set(candidate.quality_flags)
    return bool({"no_tool_calls_detected", "missing_analysis_for_held_position"} & quality_flags)


def _heuristic_verdict(candidate: PortfolioCandidate) -> dict[str, Any]:
    stance_score = {"BULLISH": 0.86, "NEUTRAL": 0.56, "BEARISH": 0.34}.get(candidate.stance, 0.50)
    setup_score = {"COMPELLING": 0.92, "DEVELOPING": 0.72, "WEAK": 0.42}.get(candidate.setup_quality, 0.55)
    thesis_strength = _clamp((stance_score * 0.42) + (setup_score * 0.28) + (candidate.confidence * 0.30))

    trigger_type = _infer_trigger_type(candidate)
    trigger_horizon = _infer_trigger_horizon(candidate)
    timing_readiness = _infer_timing_readiness(candidate, trigger_type)
    trigger_quality = _infer_trigger_quality(candidate)
    thesis_state = _infer_thesis_state(candidate, timing_readiness)
    reason_codes = _reason_codes(candidate, thesis_state)
    review_required = _review_required(candidate)
    semantic_summary = _semantic_summary(candidate, thesis_state, timing_readiness)

    return {
        "thesis_strength": round(thesis_strength, 4),
        "timing_readiness": round(timing_readiness, 4),
        "trigger_type": trigger_type,
        "trigger_horizon": trigger_horizon,
        "trigger_quality": round(trigger_quality, 4),
        "thesis_state": thesis_state,
        "semantic_summary": semantic_summary,
        "counter_evidence": _counter_evidence(candidate),
        "reason_codes": reason_codes,
        "review_required": review_required,
    }


def _infer_trigger_type(candidate: PortfolioCandidate) -> str:
    joined = " ".join(candidate.trigger_conditions).lower()
    if candidate.entry_action == "EXIT":
        return "exit_execution"
    if any(token in joined for token in ("breakout", "돌파", "추세", "trend")):
        return "breakout_confirmation"
    if any(token in joined for token in ("earnings", "실적", "revision", "guidance", "event")):
        return "event_confirmation"
    if any(token in joined for token in ("support", "invalid", "risk", "리스크", "지지")):
        return "risk_invalidation"
    if candidate.is_held and candidate.stance == "NEUTRAL":
        return "allocation_rebalance"
    return "watch_only"


def _infer_trigger_horizon(candidate: PortfolioCandidate) -> str:
    if candidate.entry_action == "EXIT":
        return "immediate"
    if candidate.entry_action in {"ADD", "STARTER"}:
        return "intraday_to_days"
    if candidate.entry_action == "WAIT":
        return "days_to_weeks"
    return "weeks_to_months"


def _infer_timing_readiness(candidate: PortfolioCandidate, trigger_type: str) -> float:
    base = {
        "ADD": 0.86,
        "STARTER": 0.74,
        "WAIT": 0.38,
        "EXIT": 0.92,
        "NONE": 0.14,
    }.get(candidate.entry_action, 0.25)
    if trigger_type == "breakout_confirmation":
        base += 0.04
    if trigger_type == "watch_only":
        base -= 0.06
    if candidate.is_held and candidate.entry_action == "WAIT":
        base += 0.03
    if int(candidate.vendor_health.get("fallback_count", 0) or 0) >= 2:
        base -= 0.08
    if "no_tool_calls_detected" in set(candidate.quality_flags):
        base -= 0.15
    return _clamp(base)


def _infer_trigger_quality(candidate: PortfolioCandidate) -> float:
    quality = 0.45
    quality += min(len(candidate.trigger_conditions), 3) * 0.08
    if int(candidate.data_coverage.get("company_news_count", 0) or 0) > 0:
        quality += 0.12
    if int(candidate.data_coverage.get("disclosures_count", 0) or 0) > 0:
        quality += 0.05
    if int(candidate.vendor_health.get("fallback_count", 0) or 0) >= 2:
        quality -= 0.10
    if "no_tool_calls_detected" in set(candidate.quality_flags):
        quality -= 0.20
    return _clamp(quality)


def _infer_thesis_state(candidate: PortfolioCandidate, timing_readiness: float) -> str:
    if candidate.stance == "BEARISH" and candidate.entry_action == "EXIT":
        return "defensive_exit"
    if candidate.stance == "BULLISH" and candidate.entry_action in {"ADD", "STARTER"} and timing_readiness >= 0.65:
        return "constructive_and_actionable"
    if candidate.stance == "BULLISH":
        return "constructive_but_not_confirmed"
    if candidate.stance == "NEUTRAL":
        return "neutral_watch"
    return "low_quality"


def _reason_codes(candidate: PortfolioCandidate, thesis_state: str) -> list[str]:
    codes: list[str] = []
    if candidate.stance == "BULLISH":
        codes.append("bullish_thesis_intact")
    if candidate.stance == "BEARISH":
        codes.append("bearish_risk_active")
    if candidate.entry_action == "WAIT":
        codes.append("timing_not_confirmed")
    if candidate.is_held:
        codes.append("held_position_context")
    if int(candidate.vendor_health.get("fallback_count", 0) or 0) >= 2:
        codes.append("high_fallback_count")
    if "no_tool_calls_detected" in set(candidate.quality_flags):
        codes.append("tool_coverage_insufficient")
    if thesis_state == "constructive_but_not_confirmed":
        codes.append("conditional_trigger_preferred")
    return list(dict.fromkeys(codes))


def _review_required(candidate: PortfolioCandidate) -> bool:
    quality_flags = set(candidate.quality_flags)
    if "no_tool_calls_detected" in quality_flags:
        return True
    if "missing_analysis_for_held_position" in quality_flags:
        return True
    return int(candidate.vendor_health.get("fallback_count", 0) or 0) >= 3


def _counter_evidence(candidate: PortfolioCandidate) -> list[str]:
    evidence: list[str] = []
    if int(candidate.vendor_health.get("fallback_count", 0) or 0) >= 2:
        evidence.append("벤더 fallback 비중이 높음")
    if int(candidate.data_coverage.get("company_news_count", 0) or 0) == 0:
        evidence.append("company news coverage 부족")
    if "no_tool_calls_detected" in set(candidate.quality_flags):
        evidence.append("tool call telemetry 부족")
    return evidence


def _semantic_summary(candidate: PortfolioCandidate, thesis_state: str, timing_readiness: float) -> str:
    if thesis_state == "constructive_and_actionable":
        return "논지와 타이밍이 모두 우호적이라 즉시 실행 후보로 볼 수 있습니다."
    if thesis_state == "constructive_but_not_confirmed":
        return "논지는 우호적이지만 아직 실행 타이밍 확인이 부족해 조건부 후보로 두는 편이 안전합니다."
    if thesis_state == "defensive_exit":
        return "약세 리스크와 청산 논리가 동시에 강해 비중 축소 또는 청산 우선순위가 높습니다."
    if thesis_state == "neutral_watch" and timing_readiness < 0.3:
        return "방향성과 타이밍 모두 강하지 않아 관찰 중심이 적절합니다."
    return candidate.rationale


def _build_prompt(candidate: PortfolioCandidate, context: dict[str, Any]) -> str:
    compact_context = {
        "candidate": candidate.to_dict(),
        "analysis": {
            "decision": ((context.get("analysis") or {}).get("decision")),
            "quality_flags": ((context.get("analysis") or {}).get("quality_flags")),
            "tool_telemetry": ((context.get("analysis") or {}).get("tool_telemetry")),
        },
        "final_state_excerpt": {
            "investment_plan": ((context.get("final_state") or {}).get("investment_plan")),
            "trader_investment_plan": ((context.get("final_state") or {}).get("trader_investment_plan")),
            "portfolio_manager_decision": (
                ((context.get("final_state") or {}).get("risk_debate_state") or {}).get("judge_decision")
            ),
        },
    }
    return (
        "You are the semantic timing judge for a portfolio action table.\n"
        "Return exactly one JSON object and nothing else.\n"
        "Be conservative. If thesis is constructive but timing is incomplete, keep timing_readiness below 0.50.\n"
        "Schema: "
        '{"thesis_strength":0.0,"timing_readiness":0.0,"trigger_type":"breakout_confirmation | event_confirmation | risk_invalidation | allocation_rebalance | watch_only | exit_execution",'
        '"trigger_horizon":"intraday_to_days | days_to_weeks | weeks_to_months | immediate | unknown",'
        '"trigger_quality":0.0,"thesis_state":"constructive_and_actionable | constructive_but_not_confirmed | neutral_watch | defensive_exit | low_quality",'
        '"semantic_summary":"...","counter_evidence":["..."],"reason_codes":["snake_case"],"review_required":false}.\n'
        f"Candidate context JSON:\n{json.dumps(compact_context, ensure_ascii=False)}"
    )


def _create_semantic_llm(llm_settings: Any | None) -> Any | None:
    if llm_settings is None:
        return None
    provider = str(getattr(llm_settings, "provider", "") or "").strip().lower()
    model = str(getattr(llm_settings, "deep_model", "") or "").strip()
    if not provider or not model:
        return None

    kwargs: dict[str, Any] = {}
    if provider == "codex":
        kwargs = {
            "codex_binary": getattr(llm_settings, "codex_binary", None),
            "codex_reasoning_effort": getattr(llm_settings, "codex_reasoning_effort", "medium"),
            "codex_summary": getattr(llm_settings, "codex_summary", "none"),
            "codex_personality": getattr(llm_settings, "codex_personality", "none"),
            "codex_workspace_dir": getattr(llm_settings, "codex_workspace_dir", None),
            "codex_request_timeout": getattr(llm_settings, "codex_request_timeout", 120.0),
            "codex_max_retries": getattr(llm_settings, "codex_max_retries", 2),
            "codex_cleanup_threads": getattr(llm_settings, "codex_cleanup_threads", True),
        }
    return create_llm_client(provider=provider, model=model, **kwargs).get_llm()


def _invoke_semantic_llm(llm: Any, prompt: str) -> Mapping[str, Any]:
    response = llm.invoke(prompt)
    content = getattr(response, "content", response)
    return _extract_json_object(content)


def _normalize_verdict(base: dict[str, Any], payload: Mapping[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    merged["thesis_strength"] = _clamp(_to_float(payload.get("thesis_strength"), base["thesis_strength"]))
    merged["timing_readiness"] = _clamp(_to_float(payload.get("timing_readiness"), base["timing_readiness"]))
    merged["trigger_type"] = _enum_or_default(
        payload.get("trigger_type"),
        {
            "breakout_confirmation",
            "event_confirmation",
            "risk_invalidation",
            "allocation_rebalance",
            "watch_only",
            "exit_execution",
        },
        base["trigger_type"],
    )
    merged["trigger_horizon"] = _enum_or_default(
        payload.get("trigger_horizon"),
        {"intraday_to_days", "days_to_weeks", "weeks_to_months", "immediate", "unknown"},
        base["trigger_horizon"],
    )
    merged["trigger_quality"] = _clamp(_to_float(payload.get("trigger_quality"), base["trigger_quality"]))
    merged["thesis_state"] = _enum_or_default(
        payload.get("thesis_state"),
        {
            "constructive_and_actionable",
            "constructive_but_not_confirmed",
            "neutral_watch",
            "defensive_exit",
            "low_quality",
        },
        base["thesis_state"],
    )
    merged["semantic_summary"] = str(payload.get("semantic_summary") or base["semantic_summary"]).strip()
    merged["counter_evidence"] = _normalize_string_list(payload.get("counter_evidence"), base["counter_evidence"])
    merged["reason_codes"] = _normalize_string_list(payload.get("reason_codes"), base["reason_codes"])
    merged["review_required"] = bool(payload.get("review_required", base["review_required"]))
    return merged


def _extract_json_object(payload: Any) -> Mapping[str, Any]:
    if isinstance(payload, Mapping):
        return payload
    if not isinstance(payload, str) or not payload.strip():
        raise ValueError("semantic judge payload must be a non-empty JSON string")

    text = payload.strip()
    try:
        parsed = json.loads(text)
        if isinstance(parsed, Mapping):
            return parsed
    except JSONDecodeError:
        pass

    decoder = json.JSONDecoder()
    for index, char in enumerate(text):
        if char != "{":
            continue
        try:
            parsed, _ = decoder.raw_decode(text[index:])
        except JSONDecodeError:
            continue
        if isinstance(parsed, Mapping):
            return parsed
    raise ValueError("semantic judge did not return a JSON object")


def _normalize_string_list(value: Any, default: list[str]) -> list[str]:
    if not isinstance(value, list):
        return list(default)
    normalized = [str(item).strip() for item in value if str(item).strip()]
    return normalized or list(default)


def _enum_or_default(value: Any, allowed: set[str], default: str) -> str:
    text = str(value or "").strip()
    return text if text in allowed else default


def _to_float(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def _clamp(value: float) -> float:
    return max(0.0, min(float(value), 1.0))
