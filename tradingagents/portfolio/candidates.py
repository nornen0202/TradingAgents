from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from tradingagents.schemas import DecisionRating, parse_structured_decision

from .account_models import AccountSnapshot, PortfolioCandidate
from .instrument_identity import resolve_identity


def build_portfolio_candidates(
    *,
    snapshot: AccountSnapshot,
    run_dir: Path,
    manifest: dict[str, Any],
    watch_tickers: tuple[str, ...],
) -> tuple[list[PortfolioCandidate], list[str]]:
    analysis_by_ticker = _load_analysis_by_ticker(run_dir, manifest)
    target_tickers = set(watch_tickers)
    target_tickers.update(position.canonical_ticker for position in snapshot.positions)
    target_tickers.update(analysis_by_ticker.keys())

    candidates: list[PortfolioCandidate] = []
    warnings: list[str] = []
    for canonical_ticker in sorted(target_tickers):
        analysis = analysis_by_ticker.get(canonical_ticker)
        position = snapshot.find_position(canonical_ticker)
        if analysis is None and position is None:
            continue
        candidate, candidate_warnings = _build_single_candidate(
            snapshot=snapshot,
            canonical_ticker=canonical_ticker,
            analysis=analysis,
            position=position,
        )
        candidates.append(candidate)
        warnings.extend(candidate_warnings)
    return candidates, warnings


def _load_analysis_by_ticker(run_dir: Path, manifest: dict[str, Any]) -> dict[str, dict[str, Any]]:
    loaded: dict[str, dict[str, Any]] = {}
    for ticker_summary in manifest.get("tickers", []):
        if ticker_summary.get("status") != "success":
            continue
        artifacts = ticker_summary.get("artifacts") or {}
        analysis_json = artifacts.get("analysis_json")
        if not analysis_json:
            continue
        analysis_path = run_dir / analysis_json
        if not analysis_path.exists():
            continue
        payload = json.loads(analysis_path.read_text(encoding="utf-8"))
        execution_update_path = artifacts.get("execution_update_json")
        if execution_update_path:
            execution_path = run_dir / execution_update_path
            if execution_path.exists():
                payload["execution_update"] = json.loads(execution_path.read_text(encoding="utf-8"))
        try:
            identity = resolve_identity(
                str(payload.get("ticker") or ticker_summary.get("ticker") or ""),
                str(payload.get("ticker_name") or ticker_summary.get("ticker_name") or "") or None,
            )
        except Exception:
            continue
        loaded[identity.canonical_ticker] = payload
    return loaded


def _build_single_candidate(
    *,
    snapshot: AccountSnapshot,
    canonical_ticker: str,
    analysis: dict[str, Any] | None,
    position,
) -> tuple[PortfolioCandidate, list[str]]:
    warnings: list[str] = []
    if position is not None:
        identity = resolve_identity(position.broker_symbol, position.display_name)
    else:
        identity = resolve_identity(canonical_ticker)

    quality_flags = tuple(str(item) for item in ((analysis or {}).get("quality_flags") or []))
    tool_telemetry = (analysis or {}).get("tool_telemetry") or {}
    vendor_health = {
        "vendor_calls": tool_telemetry.get("vendor_calls") or {},
        "fallback_count": int(tool_telemetry.get("fallback_count", 0) or 0),
    }

    structured = None
    decision_payload = (analysis or {}).get("decision")
    if isinstance(decision_payload, str) and decision_payload.strip().startswith("{"):
        try:
            structured = parse_structured_decision(decision_payload)
        except Exception as exc:
            warnings.append(f"{canonical_ticker}: structured decision parse failed ({exc}).")

    rating_value = "UNKNOWN"
    if structured is None and isinstance(decision_payload, str) and decision_payload.strip():
        normalized = decision_payload.strip().upper()
        rating_value = normalized
        stance = "BULLISH" if normalized in {"BUY", "OVERWEIGHT"} else "BEARISH" if normalized in {"SELL", "UNDERWEIGHT"} else "NEUTRAL"
        entry_action = "ADD" if normalized in {"BUY", "OVERWEIGHT"} else "EXIT" if normalized in {"SELL", "UNDERWEIGHT"} else "WAIT"
        setup_quality = "COMPELLING" if normalized in {"BUY", "SELL"} else "DEVELOPING"
        confidence = 0.55
        data_coverage = {
            "company_news_count": 0,
            "disclosures_count": 0,
            "social_source": "unavailable",
            "macro_items_count": 0,
        }
        structured_dict = {
            "rating": normalized,
            "portfolio_stance": stance,
            "entry_action": entry_action,
            "setup_quality": setup_quality,
            "confidence": confidence,
            "watchlist_triggers": [],
            "catalysts": [],
            "invalidators": [],
            "data_coverage": data_coverage,
        }
        trigger_conditions = tuple()
    elif structured is not None:
        structured_dict = structured.to_dict()
        rating_value = structured.rating.value
        confidence = structured.confidence
        stance = structured.portfolio_stance.value
        entry_action = structured.entry_action.value
        setup_quality = structured.setup_quality.value
        data_coverage = structured.data_coverage.to_dict()
        trigger_conditions = tuple(
            dict.fromkeys([*structured.watchlist_triggers, *structured.catalysts, *structured.invalidators])
        )
    else:
        structured_dict = None
        rating_value = "UNKNOWN"
        confidence = 0.30
        stance = "NEUTRAL"
        entry_action = "WAIT"
        setup_quality = "WEAK"
        data_coverage = {
            "company_news_count": 0,
            "disclosures_count": 0,
            "social_source": "unavailable",
            "macro_items_count": 0,
        }
        trigger_conditions = tuple()
        warnings.append(f"{canonical_ticker}: missing analysis; defaulting to NEUTRAL/WAIT before portfolio action translation.")

    is_held = position is not None
    action_now, action_if_triggered = _translate_actions(
        is_held=is_held,
        stance=stance,
        entry_action=entry_action,
        rating=rating_value,
    )
    execution_update = (analysis or {}).get("execution_update") if analysis else None
    if isinstance(execution_update, dict):
        action_now, action_if_triggered = _apply_execution_overlay_actions(
            action_now=action_now,
            action_if_triggered=action_if_triggered,
            execution_update=execution_update,
            is_held=is_held,
        )
    rationale = _build_rationale(
        stance=stance,
        entry_action=entry_action,
        is_held=is_held,
        analysis_present=analysis is not None,
    )

    if analysis is None and is_held:
        quality_flags = (*quality_flags, "missing_analysis_for_held_position")

    return (
        PortfolioCandidate(
            snapshot_id=snapshot.snapshot_id,
            instrument=identity,
            is_held=is_held,
            market_value_krw=int(position.market_value_krw if position else 0),
            quantity=float(position.quantity if position else 0),
            available_qty=float(position.available_qty if position else 0),
            sector=position.sector if position else None,
            structured_decision=structured_dict,
            data_coverage=data_coverage,
            quality_flags=quality_flags,
            vendor_health=vendor_health,
            suggested_action_now=action_now,
            suggested_action_if_triggered=action_if_triggered,
            trigger_conditions=trigger_conditions,
            confidence=float(confidence),
            stance=stance,
            entry_action=entry_action,
            setup_quality=setup_quality,
            rationale=rationale,
            data_health={
                "coverage_score": 0.0,
                "vendor_calls": vendor_health["vendor_calls"],
                "fallback_count": vendor_health["fallback_count"],
                "quality_flags": list(quality_flags),
                "legacy_rating": rating_value,
            },
        ),
        warnings,
    )


def _translate_actions(*, is_held: bool, stance: str, entry_action: str, rating: str) -> tuple[str, str]:
    normalized_rating = str(rating or "").strip().upper()
    if normalized_rating == DecisionRating.NO_TRADE.value:
        if stance == "BEARISH" or entry_action == "EXIT":
            return ("HOLD" if is_held else "WATCH", "NONE")
        if is_held:
            return "HOLD", "ADD_IF_TRIGGERED" if stance == "BULLISH" else "NONE"
        if stance == "BULLISH":
            return "WATCH", "STARTER_IF_TRIGGERED"
        return "WATCH", "WATCH_TRIGGER"

    if is_held and stance == "BEARISH" and entry_action == "EXIT":
        return "REDUCE_NOW", "EXIT_IF_TRIGGERED"
    if not is_held and stance == "BEARISH":
        return "WATCH", "NONE"
    if is_held and stance == "BULLISH" and entry_action == "ADD":
        return "ADD_NOW", "NONE"
    if not is_held and stance == "BULLISH" and entry_action == "STARTER":
        return "STARTER_NOW", "NONE"
    if is_held and stance == "BULLISH" and entry_action == "WAIT":
        return "HOLD", "ADD_IF_TRIGGERED"
    if not is_held and stance == "BULLISH" and entry_action == "WAIT":
        return "WATCH", "STARTER_IF_TRIGGERED"
    if is_held and stance == "NEUTRAL":
        return "HOLD", "NONE"
    if not is_held and stance == "NEUTRAL":
        return "WATCH", "WATCH_TRIGGER"
    if is_held:
        return "HOLD", "NONE"
    return "WATCH", "NONE"


def _build_rationale(*, stance: str, entry_action: str, is_held: bool, analysis_present: bool) -> str:
    if not analysis_present and is_held:
        return "보유 종목이지만 이번 런에서 종목 분석이 없어 현 상태 유지 중심으로 해석했습니다."
    if stance == "BULLISH" and entry_action == "WAIT":
        return "방향성은 긍정적이지만 즉시 진입/증액 근거보다 조건 확인 필요성이 더 큽니다."
    if stance == "BULLISH" and entry_action in {"ADD", "STARTER"}:
        return "방향성과 타이밍이 모두 비교적 우호적이라 즉시 진입 후보로 해석했습니다."
    if stance == "BEARISH" and entry_action == "EXIT":
        return "약세 판단과 청산 액션이 동시에 강해 비중 축소 또는 청산 우선순위가 높습니다."
    return "즉시 강한 액션보다 관찰 또는 유지 중심으로 해석했습니다."


def _apply_execution_overlay_actions(
    *,
    action_now: str,
    action_if_triggered: str,
    execution_update: dict[str, Any],
    is_held: bool,
) -> tuple[str, str]:
    decision_state = str(execution_update.get("decision_state") or "").upper()
    decision_now = str(execution_update.get("decision_now") or "").upper()

    if decision_state == "DEGRADED":
        if is_held:
            return ("HOLD", "ADD_IF_TRIGGERED" if action_if_triggered in {"ADD_IF_TRIGGERED", "STARTER_IF_TRIGGERED"} else action_if_triggered)
        preserved_trigger = action_if_triggered if action_if_triggered in {"STARTER_IF_TRIGGERED", "ADD_IF_TRIGGERED", "WATCH_TRIGGER"} else "WATCH_TRIGGER"
        return ("WATCH", preserved_trigger)
    if decision_state == "INVALIDATED":
        return ("REDUCE_NOW" if is_held else "WATCH", "EXIT_IF_TRIGGERED" if is_held else "NONE")
    if decision_state == "TRIGGERED_PENDING_CLOSE":
        if is_held:
            return ("HOLD", "ADD_IF_TRIGGERED")
        return ("WATCH", "STARTER_IF_TRIGGERED")
    if decision_state == "ACTIONABLE_NOW":
        mapping = {
            "STARTER_NOW": "STARTER_NOW",
            "ADD_NOW": "ADD_NOW",
            "REDUCE_NOW": "REDUCE_NOW",
            "EXIT_NOW": "EXIT_NOW",
        }
        promoted = mapping.get(decision_now)
        if promoted:
            return (promoted, "NONE")
    return action_now, action_if_triggered
