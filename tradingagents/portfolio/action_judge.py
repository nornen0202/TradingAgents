from __future__ import annotations

import json
from json import JSONDecodeError
from typing import Any, Mapping

from tradingagents.llm_clients import create_llm_client
from tradingagents.llm_clients.role_config import codex_client_kwargs

from .account_models import AccountSnapshot, PortfolioAction, PortfolioCandidate, PortfolioRecommendation


def arbitrate_portfolio_actions(
    *,
    recommendation: PortfolioRecommendation,
    candidates: list[PortfolioCandidate],
    snapshot: AccountSnapshot,
    batch_metrics: dict[str, Any],
    warnings: list[str],
    llm_settings: Any | None,
    portfolio_settings: Any,
) -> tuple[PortfolioRecommendation, dict[str, Any], list[str]]:
    action_judge_enabled = bool(getattr(portfolio_settings, "action_judge_enabled", False))
    top_n = max(1, int(getattr(portfolio_settings, "action_judge_top_n", 5) or 5))
    payload: dict[str, Any] = {
        "status": "skipped",
        "provider": str(getattr(llm_settings, "provider", "") or ""),
        "model": str(
            getattr(llm_settings, "judge_model", "")
            or getattr(llm_settings, "deep_model", "")
            or getattr(llm_settings, "output_model", "")
            or ""
        ),
        "priority_order": [action.canonical_ticker for action in recommendation.actions],
        "portfolio_note": None,
        "reason_by_ticker": {},
    }
    judge_warnings: list[str] = []
    if not action_judge_enabled:
        return recommendation, payload, judge_warnings

    calibration_mode = _calibration_mode_for_warnings(warnings)
    if calibration_mode == "wait_heavy_constructive_batch":
        top_n = max(top_n, min(len(recommendation.actions), 10))
    payload["calibration_mode"] = calibration_mode
    candidate_by_ticker = {candidate.instrument.canonical_ticker: candidate for candidate in candidates}
    eligible = _eligible_actions(recommendation.actions, top_n=top_n)
    payload["eligible_tickers"] = [action.canonical_ticker for action in eligible]
    if len(eligible) < 2:
        payload["status"] = "not_needed"
        return recommendation, payload, judge_warnings

    try:
        llm = _create_action_llm(llm_settings)
    except Exception as exc:
        payload["status"] = "fallback"
        judge_warnings.append(f"action_judge_unavailable: {exc}")
        return recommendation, payload, judge_warnings

    if llm is None:
        payload["status"] = "fallback"
        return recommendation, payload, judge_warnings

    try:
        result = _invoke_action_llm(
            llm,
            _build_prompt(
                recommendation=recommendation,
                eligible=eligible,
                candidate_by_ticker=candidate_by_ticker,
                snapshot=snapshot,
                batch_metrics=batch_metrics,
                warnings=warnings,
            ),
        )
        priority_order = _normalize_priority_order(
            result.get("priority_order"),
            default=[action.canonical_ticker for action in eligible],
        )
        reason_by_ticker = _normalize_reason_by_ticker(result.get("reason_by_ticker"))
        portfolio_note = str(result.get("portfolio_note") or "").strip() or None
        payload.update(
            {
                "status": "success",
                "priority_order": priority_order,
                "portfolio_note": portfolio_note,
                "reason_by_ticker": reason_by_ticker,
            }
        )
        recommendation = _apply_arbiter_result(
            recommendation=recommendation,
            priority_order=priority_order,
            reason_by_ticker=reason_by_ticker,
            touched={action.canonical_ticker for action in eligible},
        )
        return recommendation, payload, judge_warnings
    except Exception as exc:
        payload["status"] = "fallback"
        judge_warnings.append(f"action_judge_failed: {exc}")
    return recommendation, payload, judge_warnings


def _calibration_mode_for_warnings(warnings: list[str]) -> str:
    joined = " ".join(str(item) for item in warnings).lower()
    if "bullish_wait_concentration" in joined or "wait-heavy constructive" in joined:
        return "wait_heavy_constructive_batch"
    return "standard"


def _eligible_actions(actions: tuple[PortfolioAction, ...], *, top_n: int) -> list[PortfolioAction]:
    ranked = sorted(
        actions,
        key=lambda action: (
            abs(action.delta_krw_now) > 0,
            abs(action.delta_krw_if_triggered) > 0,
            action.review_required,
            -action.priority,
        ),
        reverse=True,
    )
    return ranked[:top_n]


def _apply_arbiter_result(
    *,
    recommendation: PortfolioRecommendation,
    priority_order: list[str],
    reason_by_ticker: dict[str, dict[str, Any]],
    touched: set[str],
) -> PortfolioRecommendation:
    action_by_ticker = {action.canonical_ticker: action for action in recommendation.actions}
    known = [ticker for ticker in priority_order if ticker in action_by_ticker]
    ordered_actions: list[PortfolioAction] = []
    for ticker in known:
        action = action_by_ticker.pop(ticker)
        ordered_actions.append(_apply_reason_override(action, reason_by_ticker.get(ticker), touched=touched))
    for action in recommendation.actions:
        if action.canonical_ticker in action_by_ticker:
            ordered_actions.append(_apply_reason_override(action_by_ticker.pop(action.canonical_ticker), reason_by_ticker.get(action.canonical_ticker), touched=touched))

    reprioritized = tuple(
        PortfolioAction(
            **{
                **action.__dict__,
                "priority": index,
            }
        )
        for index, action in enumerate(ordered_actions, start=1)
    )
    return PortfolioRecommendation(
        **{
            **recommendation.__dict__,
            "actions": reprioritized,
        }
    )


def _apply_reason_override(
    action: PortfolioAction,
    reason_payload: dict[str, Any] | None,
    *,
    touched: set[str],
) -> PortfolioAction:
    if action.canonical_ticker not in touched:
        return action
    merged_reason_codes = list(action.reason_codes)
    merged_review_required = action.review_required
    merged_rationale = action.rationale
    decision_source = action.decision_source
    if reason_payload:
        merged_reason_codes = list(
            dict.fromkeys([*merged_reason_codes, *[str(item) for item in reason_payload.get("reason_codes", [])]])
        )
        if reason_payload.get("summary"):
            merged_rationale = str(reason_payload["summary"])
        merged_review_required = bool(reason_payload.get("review_required", merged_review_required))
    if "RULE+DEEP" in decision_source or decision_source == "RULE_ONLY":
        decision_source = "RULE+DEEP+CODEX"
    return PortfolioAction(
        **{
            **action.__dict__,
            "decision_source": decision_source,
            "reason_codes": tuple(merged_reason_codes),
            "review_required": merged_review_required,
            "rationale": merged_rationale,
        }
    )


def _build_prompt(
    *,
    recommendation: PortfolioRecommendation,
    eligible: list[PortfolioAction],
    candidate_by_ticker: dict[str, PortfolioCandidate],
    snapshot: AccountSnapshot,
    batch_metrics: dict[str, Any],
    warnings: list[str],
) -> str:
    compact_payload = {
        "snapshot": {
            "snapshot_id": snapshot.snapshot_id,
            "account_value_krw": snapshot.account_value_krw,
            "available_cash_krw": snapshot.available_cash_krw,
            "constraints": snapshot.constraints.to_dict(),
        },
        "market_regime": recommendation.market_regime,
        "batch_metrics": batch_metrics,
        "warnings": list(warnings),
        "calibration_mode": _calibration_mode_for_warnings(warnings),
        "eligible_actions": [
            {
                **action.to_dict(),
                "candidate": (
                    candidate_by_ticker[action.canonical_ticker].to_dict()
                    if action.canonical_ticker in candidate_by_ticker
                    else None
                ),
            }
            for action in eligible
        ],
    }
    return (
        "You are the portfolio arbitration judge for TradingAgents.\n"
        "Return exactly one JSON object and nothing else.\n"
        "Re-rank only the provided tickers. Do not invent new tickers.\n"
        "Be conservative when sector concentration, low data quality, or wait-heavy batches are present.\n"
        "When calibration_mode is wait_heavy_constructive_batch, review every eligible WATCH/HOLD action for missed "
        "pilot-sized opportunities while preserving hard account, stale-data, stop-distance, event, and concentration gates.\n"
        "For stock-level ACTIONABLE_NOW/Pilot ready candidates that remain account WATCH/HOLD, explicitly classify the gap as one of: "
        "legitimate hard block, full-size blocked but pilot allowed, or action lift failure.\n"
        "Always distinguish full-size permission from pilot permission; a full-size block does not automatically block a small pilot.\n"
        "Use snake_case reason codes when applicable: action_lift_failure, full_size_blocked_pilot_allowed, "
        "pilot_blocked_by_hard_risk, pilot_blocked_by_stop_distance, pilot_blocked_by_account_concentration, "
        "prism_conflict_full_size_blocked.\n"
        "Schema: "
        '{"priority_order":["ticker"],"reason_by_ticker":{"ticker":{"summary":"...","reason_codes":["snake_case"],"review_required":false}},"portfolio_note":"..."}.\n'
        f"Portfolio context JSON:\n{json.dumps(compact_payload, ensure_ascii=False)}"
    )


def _create_action_llm(llm_settings: Any | None) -> Any | None:
    if llm_settings is None:
        return None
    provider = str(getattr(llm_settings, "provider", "") or "").strip().lower()
    model = str(
        getattr(llm_settings, "judge_model", "")
        or getattr(llm_settings, "deep_model", "")
        or getattr(llm_settings, "output_model", "")
        or ""
    ).strip()
    if provider == "codex" and not model:
        model = "gpt-5.6-sol"
    if not provider or not model:
        return None

    kwargs: dict[str, Any] = {}
    if provider == "codex":
        kwargs = codex_client_kwargs(llm_settings, role="judge")
    return create_llm_client(provider=provider, model=model, **kwargs).get_llm()


def _invoke_action_llm(llm: Any, prompt: str) -> Mapping[str, Any]:
    response = llm.invoke(prompt)
    content = getattr(response, "content", response)
    return _extract_json_object(content)


def _normalize_priority_order(value: Any, *, default: list[str]) -> list[str]:
    if not isinstance(value, list):
        return list(default)
    normalized = [str(item).strip() for item in value if str(item).strip()]
    return normalized or list(default)


def _normalize_reason_by_ticker(value: Any) -> dict[str, dict[str, Any]]:
    if not isinstance(value, Mapping):
        return {}
    normalized: dict[str, dict[str, Any]] = {}
    for ticker, payload in value.items():
        if not isinstance(payload, Mapping):
            continue
        ticker_text = str(ticker).strip()
        if not ticker_text:
            continue
        normalized[ticker_text] = {
            "summary": str(payload.get("summary") or "").strip() or None,
            "reason_codes": [str(item).strip() for item in (payload.get("reason_codes") or []) if str(item).strip()],
            "review_required": bool(payload.get("review_required", False)),
        }
    return normalized


def _extract_json_object(payload: Any) -> Mapping[str, Any]:
    if isinstance(payload, Mapping):
        return payload
    if not isinstance(payload, str) or not payload.strip():
        raise ValueError("action judge payload must be a non-empty JSON string")

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
    raise ValueError("action judge did not return a JSON object")
