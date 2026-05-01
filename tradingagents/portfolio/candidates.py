from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from tradingagents.schemas import DecisionRating, RiskAction, parse_structured_decision

from .account_models import AccountSnapshot, PortfolioCandidate
from .instrument_identity import resolve_identity


_TRIGGER_ACTIONS = {
    "ADD_IF_TRIGGERED",
    "STARTER_IF_TRIGGERED",
    "REDUCE_IF_TRIGGERED",
    "TAKE_PROFIT_IF_TRIGGERED",
    "STOP_LOSS_IF_TRIGGERED",
    "EXIT_IF_TRIGGERED",
}


def build_portfolio_candidates(
    *,
    snapshot: AccountSnapshot,
    run_dir: Path,
    manifest: dict[str, Any],
    watch_tickers: tuple[str, ...],
) -> tuple[list[PortfolioCandidate], list[str]]:
    analysis_by_ticker = _load_analysis_by_ticker(run_dir, manifest)
    failed_by_ticker = _failed_tickers_by_canonical(manifest)
    target_tickers = set(watch_tickers)
    target_tickers.update(position.canonical_ticker for position in snapshot.positions)
    target_tickers.update(analysis_by_ticker.keys())
    target_tickers.update(failed_by_ticker.keys())

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
            failed_reason=failed_by_ticker.get(canonical_ticker),
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


def _failed_tickers_by_canonical(manifest: dict[str, Any]) -> dict[str, str]:
    failed: dict[str, str] = {}
    quality_gate = manifest.get("quality_gate") if isinstance(manifest.get("quality_gate"), dict) else {}
    sources = list(quality_gate.get("failed_tickers") or [])
    if not sources:
        sources = [
            item
            for item in (manifest.get("tickers") or [])
            if isinstance(item, dict) and item.get("status") != "success"
        ]
    for item in sources:
        if not isinstance(item, dict):
            continue
        raw_ticker = str(item.get("ticker") or "").strip()
        if not raw_ticker:
            continue
        try:
            identity = resolve_identity(raw_ticker, str(item.get("ticker_name") or "") or None)
        except Exception:
            continue
        reason = str(item.get("reason") or item.get("error") or "analysis failed").strip()
        failed[identity.canonical_ticker] = _short_failure_reason(reason)
    return failed


def _build_single_candidate(
    *,
    snapshot: AccountSnapshot,
    canonical_ticker: str,
    analysis: dict[str, Any] | None,
    position,
    failed_reason: str | None = None,
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
    structured_parse_error: str | None = None
    decision_payload = (analysis or {}).get("decision")
    if isinstance(decision_payload, str) and decision_payload.strip().startswith("{"):
        try:
            structured = parse_structured_decision(decision_payload)
        except Exception as exc:
            structured_parse_error = str(exc)
            warnings.append(f"{canonical_ticker}: structured decision parse failed ({exc}).")

    rating_value = "UNKNOWN"
    if (
        structured is None
        and structured_parse_error is None
        and isinstance(decision_payload, str)
        and decision_payload.strip()
    ):
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
            "risk_action": "EXIT" if normalized == "SELL" else "REDUCE_RISK" if normalized == "UNDERWEIGHT" else "NONE",
            "setup_quality": setup_quality,
            "confidence": confidence,
            "watchlist_triggers": [],
            "catalysts": [],
            "invalidators": [],
            "data_coverage": data_coverage,
        }
        risk_action = str(structured_dict["risk_action"])
        risk_action_reason_codes = ("LEGACY_SELL_EXIT",) if risk_action == "EXIT" else ("LEGACY_UNDERWEIGHT",) if risk_action == "REDUCE_RISK" else tuple()
        risk_action_level = None
        trigger_conditions = tuple()
    elif structured is not None:
        structured_dict = structured.to_dict()
        rating_value = structured.rating.value
        confidence = structured.confidence
        stance = structured.portfolio_stance.value
        entry_action = structured.entry_action.value
        risk_action = structured.risk_action.value
        risk_action_reason_codes = structured.risk_action_reason_codes
        risk_action_level = structured.risk_action_level.to_dict() if structured.risk_action_level else None
        setup_quality = structured.setup_quality.value
        data_coverage = structured.data_coverage.to_dict()
        trigger_conditions = tuple(
            dict.fromkeys([*structured.watchlist_triggers, *structured.catalysts, *structured.invalidators])
        )
        execution_levels = structured.execution_levels.to_dict()
        level_conditions = [
            execution_levels.get("intraday_pilot_rule"),
            execution_levels.get("close_confirm_rule"),
            execution_levels.get("next_day_followthrough_rule"),
            execution_levels.get("failed_breakout_rule"),
        ]
        trigger_conditions = tuple(
            dict.fromkeys([*trigger_conditions, *(str(item).strip() for item in level_conditions if str(item or "").strip())])
        )
    else:
        structured_dict = None
        rating_value = "UNKNOWN"
        confidence = 0.30
        stance = "NEUTRAL"
        entry_action = "WAIT"
        setup_quality = "WEAK"
        risk_action = "NONE"
        risk_action_reason_codes = tuple()
        risk_action_level = None
        data_coverage = {
            "company_news_count": 0,
            "disclosures_count": 0,
            "social_source": "unavailable",
            "macro_items_count": 0,
        }
        trigger_conditions = tuple()
        if structured_parse_error:
            quality_flags = (*quality_flags, "invalid_structured_decision", "run_failed_reanalysis_required")
            warnings.append(f"{canonical_ticker}: invalid structured decision; reanalysis required.")
        elif failed_reason:
            quality_flags = (*quality_flags, "run_failed_reanalysis_required")
            warnings.append(f"{canonical_ticker}: run failed; reanalysis required ({failed_reason}).")
        else:
            warnings.append(f"{canonical_ticker}: missing analysis; defaulting to NEUTRAL/WAIT before portfolio action translation.")
    execution_levels_dict = (
        (structured_dict or {}).get("execution_levels")
        if isinstance((structured_dict or {}).get("execution_levels"), dict)
        else {}
    )

    is_held = position is not None
    action_now, action_if_triggered = _translate_actions(
        is_held=is_held,
        stance=stance,
        entry_action=entry_action,
        rating=rating_value,
    )
    reanalysis_reason = _reanalysis_reason(failed_reason, structured_parse_error)
    if reanalysis_reason:
        action_now = "HOLD" if is_held else "WATCH"
        action_if_triggered = "NONE"
        risk_action = "NONE"
        risk_action_reason_codes = tuple()
        risk_action_level = None
    execution_update = (analysis or {}).get("execution_update") if analysis else None
    execution_update_payload = execution_update if isinstance(execution_update, dict) else None
    current_price_for_risk = _current_price_for_risk_mapping(execution_update_payload, position)
    risk_action, risk_action_reason_codes = _apply_execution_overlay_risk_action(
        risk_action=risk_action,
        risk_action_reason_codes=risk_action_reason_codes,
        execution_update=execution_update_payload,
        is_held=is_held,
    )
    action_now, action_if_triggered = _apply_risk_action_mapping(
        action_now=action_now,
        action_if_triggered=action_if_triggered,
        risk_action=risk_action,
        risk_action_reason_codes=risk_action_reason_codes,
        risk_action_level=risk_action_level,
        execution_update=execution_update_payload,
        current_price=current_price_for_risk,
        is_held=is_held,
    )
    if isinstance(execution_update, dict):
        action_now, action_if_triggered = _apply_execution_overlay_actions(
            action_now=action_now,
            action_if_triggered=action_if_triggered,
            execution_update=execution_update,
            is_held=is_held,
        )
        action_now, action_if_triggered = _apply_risk_action_mapping(
            action_now=action_now,
            action_if_triggered=action_if_triggered,
            risk_action=risk_action,
            risk_action_reason_codes=risk_action_reason_codes,
            risk_action_level=risk_action_level,
            execution_update=execution_update_payload,
            current_price=current_price_for_risk,
            is_held=is_held,
        )
    if reanalysis_reason:
        action_now = "HOLD" if is_held else "WATCH"
        action_if_triggered = "NONE"
        risk_action = "NONE"
        risk_action_reason_codes = tuple()
        risk_action_level = None
    execution_feasibility_now = _execution_feasibility_now(
        action_now=action_now,
        execution_update=execution_update if isinstance(execution_update, dict) else None,
        quality_flags=quality_flags,
    )
    execution_health = _execution_health(
        execution_update=execution_update if isinstance(execution_update, dict) else None,
        execution_levels=execution_levels_dict,
    )
    strategy_state = _strategy_state(
        action_now=action_now,
        action_if_triggered=action_if_triggered,
        is_held=is_held,
        stance=stance,
    )
    stale_but_triggerable = (
        execution_feasibility_now == "blocked_stale_or_degraded_data"
        and action_if_triggered in _TRIGGER_ACTIONS
    )
    rationale = _build_rationale(
        stance=stance,
        entry_action=entry_action,
        is_held=is_held,
        analysis_present=analysis is not None,
    )

    if analysis is None and is_held:
        quality_flags = (*quality_flags, "missing_analysis_for_held_position")
    portfolio_relative_action = _initial_portfolio_relative_action(
        is_held=is_held,
        action_now=action_now,
        action_if_triggered=action_if_triggered,
        stance=stance,
        entry_action=entry_action,
        analysis_present=analysis is not None,
        risk_action=risk_action,
    )
    relative_reason_codes = _initial_relative_reason_codes(
        is_held=is_held,
        action_now=action_now,
        action_if_triggered=action_if_triggered,
        stance=stance,
        entry_action=entry_action,
        analysis_present=analysis is not None,
        risk_action=risk_action,
        risk_action_reason_codes=risk_action_reason_codes,
    )
    if reanalysis_reason:
        portfolio_relative_action = "HOLD" if is_held else "WATCH"
        relative_reason_codes = ("REANALYSIS_REQUIRED",)
    sell_side_category = _sell_side_category(risk_action, portfolio_relative_action)

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
            strategy_state=strategy_state,
            execution_feasibility_now=execution_feasibility_now,
            portfolio_relative_action=portfolio_relative_action,
            relative_action_reason=_relative_reason_text(relative_reason_codes),
            relative_action_reason_codes=relative_reason_codes,
            risk_action=risk_action,
            risk_action_reason_codes=risk_action_reason_codes,
            risk_action_level=risk_action_level,
            sell_side_category=sell_side_category,
            stale_but_triggerable=stale_but_triggerable,
            review_required=bool(reanalysis_reason),
            trigger_profile={
                "intraday_pilot_rule": execution_levels_dict.get("intraday_pilot_rule"),
                "close_confirm_rule": execution_levels_dict.get("close_confirm_rule"),
                "next_day_followthrough_rule": execution_levels_dict.get("next_day_followthrough_rule"),
                "failed_breakout_rule": execution_levels_dict.get("failed_breakout_rule"),
                "trim_rule": execution_levels_dict.get("trim_rule"),
                "funding_priority": execution_levels_dict.get("funding_priority"),
                "entry_window": execution_levels_dict.get("entry_window"),
                "trigger_quality": execution_levels_dict.get("trigger_quality"),
                "primary_trigger_type": _primary_trigger_type(execution_update if isinstance(execution_update, dict) else None),
            },
            data_health={
                "coverage_score": 0.0,
                "vendor_calls": vendor_health["vendor_calls"],
                "fallback_count": vendor_health["fallback_count"],
                "quality_flags": list(quality_flags),
                "legacy_rating": rating_value,
                "strategy_state": strategy_state,
                "execution_feasibility_now": execution_feasibility_now,
                "portfolio_relative_action": portfolio_relative_action,
                "relative_action_reason_codes": list(relative_reason_codes),
                "risk_action": risk_action,
                "risk_action_reason_codes": list(risk_action_reason_codes),
                "risk_action_level": risk_action_level,
                "sell_side_category": sell_side_category,
                "stale_but_triggerable": stale_but_triggerable,
                "reanalysis_required": bool(reanalysis_reason),
                "reanalysis_reason": reanalysis_reason,
                **execution_health,
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


def _reanalysis_reason(failed_reason: str | None, parse_error: str | None) -> str | None:
    if parse_error:
        return _short_failure_reason(parse_error)
    if failed_reason:
        return _short_failure_reason(failed_reason)
    return None


def _short_failure_reason(reason: str) -> str:
    text = " ".join(str(reason or "").split())
    lower = text.lower()
    if "missing required fields" in lower:
        return "decision payload missing required fields"
    if not text:
        return "analysis failed"
    return text[:180]


def _apply_execution_overlay_risk_action(
    *,
    risk_action: str,
    risk_action_reason_codes: tuple[str, ...],
    execution_update: dict[str, Any] | None,
    is_held: bool,
) -> tuple[str, tuple[str, ...]]:
    if not execution_update or not is_held:
        return risk_action, risk_action_reason_codes
    current = str(risk_action or "NONE").upper()
    codes = list(risk_action_reason_codes)
    decision_state = str(execution_update.get("decision_state") or "").upper()
    timing_state = _normalize_timing_state(str(execution_update.get("execution_timing_state") or "").upper())
    trigger_status = execution_update.get("trigger_status") if isinstance(execution_update.get("trigger_status"), dict) else {}
    if decision_state == "INVALIDATED" or timing_state == "INVALIDATED" or trigger_status.get("invalidated"):
        codes.append("INVALIDATION_BROKEN")
        return _stronger_risk_action(current, RiskAction.STOP_LOSS.value), tuple(dict.fromkeys(codes))
    if timing_state == "SUPPORT_FAIL" or trigger_status.get("support_fail"):
        codes.append("SUPPORT_BROKEN")
        return _stronger_risk_action(current, RiskAction.REDUCE_RISK.value), tuple(dict.fromkeys(codes))
    if timing_state in {"FAILED_BREAKOUT", "PILOT_BLOCKED_FAILED_BREAKOUT"} or trigger_status.get("failed_breakout"):
        codes.append("FAILED_BREAKOUT")
        return _stronger_risk_action(current, RiskAction.REDUCE_RISK.value), tuple(dict.fromkeys(codes))
    return current or RiskAction.NONE.value, tuple(dict.fromkeys(codes))


def _stronger_risk_action(current: str, candidate: str) -> str:
    order = {
        RiskAction.NONE.value: 0,
        RiskAction.HOLD.value: 0,
        RiskAction.TRIM_TO_FUND.value: 1,
        RiskAction.TAKE_PROFIT.value: 2,
        RiskAction.REDUCE_RISK.value: 3,
        RiskAction.STOP_LOSS.value: 4,
        RiskAction.EXIT.value: 5,
    }
    current_key = str(current or RiskAction.NONE.value).upper()
    candidate_key = str(candidate or RiskAction.NONE.value).upper()
    return candidate_key if order.get(candidate_key, 0) > order.get(current_key, 0) else current_key


def _apply_risk_action_mapping(
    *,
    action_now: str,
    action_if_triggered: str,
    risk_action: str,
    risk_action_reason_codes: tuple[str, ...],
    risk_action_level: dict[str, Any] | None,
    execution_update: dict[str, Any] | None,
    current_price: float | None,
    is_held: bool,
) -> tuple[str, str]:
    normalized = str(risk_action or RiskAction.NONE.value).upper()
    if normalized in {RiskAction.NONE.value, RiskAction.HOLD.value}:
        return action_now, action_if_triggered
    if not is_held:
        if normalized in {RiskAction.REDUCE_RISK.value, RiskAction.STOP_LOSS.value, RiskAction.EXIT.value}:
            return "WATCH", "NONE"
        return action_now, action_if_triggered
    if normalized == RiskAction.TRIM_TO_FUND.value:
        return action_now, action_if_triggered

    triggered_now = _risk_action_triggered_now(
        risk_action=normalized,
        reason_codes=risk_action_reason_codes,
        risk_action_level=risk_action_level,
        execution_update=execution_update,
        current_price=current_price,
    )
    if normalized == RiskAction.EXIT.value:
        return ("EXIT_NOW", "NONE") if triggered_now else ("HOLD", "EXIT_IF_TRIGGERED")
    if normalized == RiskAction.STOP_LOSS.value:
        return ("STOP_LOSS_NOW", "NONE") if triggered_now else ("HOLD", "STOP_LOSS_IF_TRIGGERED")
    if normalized == RiskAction.REDUCE_RISK.value:
        return ("REDUCE_NOW", "NONE") if triggered_now else ("HOLD", "REDUCE_IF_TRIGGERED")
    if normalized == RiskAction.TAKE_PROFIT.value:
        return ("TAKE_PROFIT_NOW", "NONE") if triggered_now else ("HOLD", "TAKE_PROFIT_IF_TRIGGERED")
    return action_now, action_if_triggered


def _risk_action_triggered_now(
    *,
    risk_action: str,
    reason_codes: tuple[str, ...],
    risk_action_level: dict[str, Any] | None,
    execution_update: dict[str, Any] | None,
    current_price: float | None,
) -> bool:
    if risk_action_level is not None:
        return _risk_action_level_triggered_now(
            risk_action=risk_action,
            risk_action_level=risk_action_level,
            execution_update=execution_update,
            current_price=current_price,
        )
    if _execution_update_has_risk_trigger(execution_update):
        return True
    code_blob = " ".join(str(code).upper() for code in reason_codes)
    if str(risk_action or "").upper() == RiskAction.EXIT.value and any(
        token in code_blob for token in ("LEGACY_SELL_EXIT", "MANUAL_EXIT_NOW", "EXPLICIT_EXIT_NOW")
    ):
        return True
    return False


def _current_price_for_risk_mapping(execution_update: dict[str, Any] | None, position: Any) -> float | None:
    for value in (
        (execution_update or {}).get("last_price"),
        (execution_update or {}).get("current_price"),
        (execution_update or {}).get("estimated_market_price_krw"),
        getattr(position, "market_price_krw", None),
    ):
        try:
            if value is not None and float(value) > 0:
                return float(value)
        except (TypeError, ValueError):
            continue
    return None


def _execution_update_has_risk_trigger(execution_update: dict[str, Any] | None) -> bool:
    if not execution_update:
        return False
    decision_state = str(execution_update.get("decision_state") or "").upper()
    timing_state = _normalize_timing_state(str(execution_update.get("execution_timing_state") or "").upper())
    trigger_status = execution_update.get("trigger_status") if isinstance(execution_update.get("trigger_status"), dict) else {}
    if decision_state == "INVALIDATED" or timing_state in {"INVALIDATED", "SUPPORT_FAIL", "FAILED_BREAKOUT"}:
        return True
    return bool(trigger_status.get("invalidated") or trigger_status.get("support_fail") or trigger_status.get("failed_breakout"))


def _risk_action_level_triggered_now(
    *,
    risk_action: str,
    risk_action_level: dict[str, Any],
    execution_update: dict[str, Any] | None,
    current_price: float | None,
) -> bool:
    if current_price is None or current_price <= 0:
        return False
    confirmation = str(risk_action_level.get("confirmation") or "").strip().lower()
    if confirmation in {"two_bar", "next_day"}:
        return False
    if confirmation == "close" and not _is_close_confirmed_execution(execution_update):
        return False

    direction = _risk_action_level_direction(risk_action=risk_action, risk_action_level=risk_action_level)
    trigger_level = _risk_action_trigger_price(risk_action_level, direction=direction)
    if trigger_level is None or trigger_level <= 0:
        return False
    if direction == "upside":
        return float(current_price) >= float(trigger_level)
    return float(current_price) <= float(trigger_level)


def _is_close_confirmed_execution(execution_update: dict[str, Any] | None) -> bool:
    if not execution_update:
        return False
    source = execution_update.get("source") if isinstance(execution_update.get("source"), dict) else {}
    market_session = str(source.get("market_session") or "").strip().lower()
    timing_state = _normalize_timing_state(str(execution_update.get("execution_timing_state") or "").upper())
    return market_session in {"post_close", "closed", "after_hours"} or timing_state in {"CLOSE_CONFIRMED", "CLOSE_CONFIRM"}


def _risk_action_trigger_price(risk_action_level: dict[str, Any], *, direction: str) -> float | None:
    values = {
        "price": risk_action_level.get("price"),
        "low": risk_action_level.get("low"),
        "high": risk_action_level.get("high"),
    }
    if values["price"] not in (None, ""):
        try:
            return float(values["price"])
        except (TypeError, ValueError):
            return None
    ordered_keys = ("high", "low") if direction == "upside" else ("low", "high")
    for key in ordered_keys:
        try:
            value = values[key]
            if value not in (None, ""):
                return float(value)
        except (TypeError, ValueError):
            continue
    return None


def _risk_action_level_direction(*, risk_action: str, risk_action_level: dict[str, Any]) -> str:
    normalized_action = str(risk_action or "").upper()
    level_type = str(risk_action_level.get("level_type") or "").upper().replace(" ", "_")
    text = " ".join(
        str(risk_action_level.get(key) or "")
        for key in ("label", "source_text", "reason_code", "level_type")
    ).lower()
    if normalized_action == RiskAction.TAKE_PROFIT.value:
        return "upside"
    if normalized_action in {RiskAction.STOP_LOSS.value, RiskAction.EXIT.value}:
        return "downside"
    if level_type in {"TAKE_PROFIT", "RESISTANCE"}:
        return "upside"
    if level_type in {"SUPPORT", "INVALIDATION", "STOP_LOSS"}:
        return "downside"
    if any(token in text for token in ("profit", "target", "resistance", "ceiling", "이익", "익절", "저항", "고점")):
        return "upside"
    return "downside"


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
    timing_state = _normalize_timing_state(str(execution_update.get("execution_timing_state") or "").upper())

    if timing_state == "FAILED_BREAKOUT":
        if is_held:
            return ("HOLD", "REDUCE_IF_TRIGGERED")
        return ("WATCH", "WATCH_TRIGGER")
    if timing_state == "PILOT_BLOCKED_FAILED_BREAKOUT":
        if is_held:
            preserved_trigger = "ADD_IF_TRIGGERED" if action_if_triggered == "STARTER_IF_TRIGGERED" else action_if_triggered
            return ("HOLD", preserved_trigger or "ADD_IF_TRIGGERED")
        preserved_trigger = action_if_triggered if action_if_triggered in {"STARTER_IF_TRIGGERED", "ADD_IF_TRIGGERED"} else "STARTER_IF_TRIGGERED"
        return ("WATCH", preserved_trigger)
    if timing_state == "SUPPORT_FAIL":
        return ("REDUCE_NOW" if is_held else "WATCH", "EXIT_IF_TRIGGERED" if is_held else "NONE")
    if timing_state in {"NO_LIVE_DATA", "PRE_OPEN_THESIS_ONLY"}:
        if is_held:
            preserved_trigger = action_if_triggered
            if preserved_trigger == "STARTER_IF_TRIGGERED":
                preserved_trigger = "ADD_IF_TRIGGERED"
            return ("HOLD", preserved_trigger)
        preserved_trigger = action_if_triggered if action_if_triggered in {"STARTER_IF_TRIGGERED", "ADD_IF_TRIGGERED", "WATCH_TRIGGER"} else "NONE"
        return ("WATCH", preserved_trigger)
    if decision_state == "DEGRADED" or timing_state == "STALE_TRIGGERABLE":
        if is_held:
            preserved_trigger = action_if_triggered
            if action_if_triggered == "STARTER_IF_TRIGGERED":
                preserved_trigger = "ADD_IF_TRIGGERED"
            return ("HOLD", preserved_trigger)
        preserved_trigger = action_if_triggered if action_if_triggered in {"STARTER_IF_TRIGGERED", "ADD_IF_TRIGGERED", "WATCH_TRIGGER"} else "NONE"
        return ("WATCH", preserved_trigger)
    if decision_state == "INVALIDATED":
        return ("REDUCE_NOW" if is_held else "WATCH", "EXIT_IF_TRIGGERED" if is_held else "NONE")
    if decision_state == "TRIGGERED_PENDING_CLOSE" or timing_state in {
        "CLOSE_CONFIRM_PENDING",
        "CLOSE_CONFIRMED",
        "NEXT_DAY_FOLLOWTHROUGH_PENDING",
        "LATE_SESSION_CONFIRM",
        "CLOSE_CONFIRM",
    }:
        if is_held:
            return ("HOLD", "ADD_IF_TRIGGERED")
        return ("WATCH", "STARTER_IF_TRIGGERED")
    if decision_state == "ACTIONABLE_NOW" and decision_now in {"REDUCE_NOW", "EXIT_NOW"}:
        return (decision_now, "NONE") if is_held else ("WATCH", "NONE")
    if timing_state == "PILOT_READY":
        if is_held:
            return ("ADD_NOW", "NONE")
        return ("STARTER_NOW", "NONE")
    if timing_state == "PILOT_BLOCKED_VOLUME":
        if is_held:
            preserved_trigger = "ADD_IF_TRIGGERED" if action_if_triggered == "STARTER_IF_TRIGGERED" else action_if_triggered
            return ("HOLD", preserved_trigger or "ADD_IF_TRIGGERED")
        preserved_trigger = action_if_triggered if action_if_triggered in {"STARTER_IF_TRIGGERED", "ADD_IF_TRIGGERED"} else "STARTER_IF_TRIGGERED"
        return ("WATCH", preserved_trigger)
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


def _execution_feasibility_now(
    *,
    action_now: str,
    execution_update: dict[str, Any] | None,
    quality_flags: tuple[str, ...],
) -> str:
    quality_flag_set = {str(flag).strip().lower() for flag in quality_flags}
    if "stale_market_data" in quality_flag_set:
        return "blocked_stale_or_degraded_data"
    if execution_update:
        decision_state = str(execution_update.get("decision_state") or "").upper()
        data_health = str(execution_update.get("data_health") or "").upper()
        reason_codes = {str(item).strip().lower() for item in (execution_update.get("reason_codes") or [])}
        timing_state = _normalize_timing_state(str(execution_update.get("execution_timing_state") or "").upper())
        if (
            decision_state == "DEGRADED"
            or data_health in {"STALE", "DELAYED", "UNAVAILABLE"}
            or "stale_market_data" in reason_codes
            or timing_state in {"STALE_TRIGGERABLE", "NO_LIVE_DATA"}
        ):
            return "blocked_stale_or_degraded_data"
        if decision_state == "INVALIDATED":
            return "risk_exit_review"
        if timing_state == "PILOT_READY":
            return "executable_now"
    if action_now in {"ADD_NOW", "STARTER_NOW", "REDUCE_NOW", "TRIM_NOW", "EXIT_NOW", "STOP_LOSS_NOW", "TAKE_PROFIT_NOW"}:
        return "executable_now"
    return "not_actionable_now"


def _execution_health(
    *,
    execution_update: dict[str, Any] | None,
    execution_levels: dict[str, Any],
) -> dict[str, Any]:
    quality_map = {"weak": 0.33, "medium": 0.66, "strong": 1.0}
    trigger_quality = str(execution_levels.get("trigger_quality") or "").strip().lower()
    payload: dict[str, Any] = {
        "execution_timing_state": "",
        "session_vwap_ok": None,
        "relative_volume_ok": None,
        "trigger_quality": quality_map.get(trigger_quality, 0.0),
        "entry_window": execution_levels.get("entry_window"),
    }
    if not execution_update:
        return payload
    timing_state = _normalize_timing_state(str(execution_update.get("execution_timing_state") or "").upper())
    source = execution_update.get("source") if isinstance(execution_update.get("source"), dict) else {}
    payload["execution_timing_state"] = timing_state
    payload["market_session"] = source.get("market_session")
    payload["quote_delay_seconds"] = source.get("quote_delay_seconds")
    payload["provider_realtime_capable"] = source.get("provider_realtime_capable")
    payload["execution_data_quality"] = source.get("execution_data_quality")
    last_price = _safe_float(execution_update.get("last_price"))
    session_vwap = _safe_float(execution_update.get("session_vwap"))
    relative_volume = _safe_float(execution_update.get("relative_volume"))
    payload["session_vwap_ok"] = None if last_price is None or session_vwap is None else last_price >= session_vwap
    payload["relative_volume_ok"] = None if relative_volume is None else relative_volume >= 1.0
    return payload


def _primary_trigger_type(execution_update: dict[str, Any] | None) -> str:
    if not execution_update:
        return ""
    timing_state = _normalize_timing_state(str(execution_update.get("execution_timing_state") or "").upper())
    if timing_state in {
        "LIVE_BREAKOUT",
        "FAILED_BREAKOUT",
        "LATE_SESSION_CONFIRM",
        "PILOT_READY",
        "PILOT_BLOCKED_VOLUME",
        "PILOT_BLOCKED_FAILED_BREAKOUT",
        "CLOSE_CONFIRM_PENDING",
        "CLOSE_CONFIRMED",
        "CLOSE_CONFIRM",
    }:
        return "breakout"
    if timing_state in {"SUPPORT_HOLD", "SUPPORT_FAIL"}:
        return "support"
    return timing_state.lower()


def _normalize_timing_state(value: str) -> str:
    mapping = {
        "LIVE_BREAKOUT": "PILOT_READY",
        "LATE_SESSION_CONFIRM": "CLOSE_CONFIRM_PENDING",
        "CLOSE_CONFIRM": "CLOSE_CONFIRM_PENDING",
        "ACTIONABLE_LIVE": "PILOT_READY",
    }
    normalized = str(value or "").strip().upper()
    return mapping.get(normalized, normalized)


def _safe_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _initial_portfolio_relative_action(
    *,
    is_held: bool,
    action_now: str,
    action_if_triggered: str,
    stance: str,
    entry_action: str,
    analysis_present: bool,
    risk_action: str,
) -> str:
    normalized_risk = str(risk_action or RiskAction.NONE.value).upper()
    if is_held and normalized_risk in {
        RiskAction.TRIM_TO_FUND.value,
        RiskAction.REDUCE_RISK.value,
        RiskAction.TAKE_PROFIT.value,
        RiskAction.STOP_LOSS.value,
        RiskAction.EXIT.value,
    }:
        return normalized_risk
    if not is_held and normalized_risk in {RiskAction.REDUCE_RISK.value, RiskAction.STOP_LOSS.value, RiskAction.EXIT.value}:
        return "AVOID"
    if not is_held and normalized_risk == RiskAction.TAKE_PROFIT.value:
        return "WATCH_RISK"
    if is_held and action_now in {"REDUCE_NOW", "TRIM_NOW"}:
        return "REDUCE_RISK"
    if is_held and action_now == "EXIT_NOW":
        return "EXIT"
    if is_held and action_if_triggered in {"REDUCE_IF_TRIGGERED", "EXIT_IF_TRIGGERED"}:
        return "REDUCE_RISK"
    if is_held:
        return "HOLD" if analysis_present or stance == "BULLISH" else "TRIM_TO_FUND"
    if action_now in {"ADD_NOW", "STARTER_NOW"} or action_if_triggered in {"ADD_IF_TRIGGERED", "STARTER_IF_TRIGGERED"}:
        return "ADD"
    return "WATCH"


def _initial_relative_reason_codes(
    *,
    is_held: bool,
    action_now: str,
    action_if_triggered: str,
    stance: str,
    entry_action: str,
    analysis_present: bool,
    risk_action: str,
    risk_action_reason_codes: tuple[str, ...],
) -> tuple[str, ...]:
    codes: list[str] = list(risk_action_reason_codes)
    normalized_risk = str(risk_action or RiskAction.NONE.value).upper()
    if is_held and not analysis_present:
        codes.append("NO_COVERAGE")
    if is_held and normalized_risk in {RiskAction.REDUCE_RISK.value, RiskAction.STOP_LOSS.value, RiskAction.EXIT.value}:
        codes.append("THESIS_WEAKENING")
    if is_held and normalized_risk == RiskAction.TAKE_PROFIT.value:
        codes.append("PROFIT_TAKING")
    if is_held and normalized_risk == RiskAction.TRIM_TO_FUND.value:
        codes.append("OPPORTUNITY_COST")
    if is_held and (
        stance == "BEARISH"
        or entry_action == "EXIT"
        or action_now in {"REDUCE_NOW", "TRIM_NOW", "EXIT_NOW", "STOP_LOSS_NOW", "TAKE_PROFIT_NOW"}
    ):
        codes.append("THESIS_WEAKENING")
    if is_held and action_if_triggered in {
        "REDUCE_IF_TRIGGERED",
        "EXIT_IF_TRIGGERED",
        "STOP_LOSS_IF_TRIGGERED",
        "TAKE_PROFIT_IF_TRIGGERED",
    }:
        codes.append("THESIS_WEAKENING")
    return tuple(dict.fromkeys(codes))


def _relative_reason_text(reason_codes: tuple[str, ...]) -> str:
    if "REANALYSIS_REQUIRED" in reason_codes:
        return "Reanalysis required before using this ticker as an actionable candidate."
    if "INVALIDATION_BROKEN" in reason_codes:
        return "Invalidation or stop-loss level was breached; prioritize loss control."
    if "SUPPORT_BROKEN" in reason_codes:
        return "Named support broke; reduce downside risk before adding exposure."
    if "FAILED_BREAKOUT" in reason_codes:
        return "Breakout failed; avoid fresh buying and reduce risk if weakness persists."
    if "PROFIT_TAKING" in reason_codes:
        return "Take partial profit because reward/risk no longer favors full size."
    if "NO_COVERAGE" in reason_codes:
        return "No current thesis coverage; size should be reviewed before funding stronger candidates."
    if "THESIS_WEAKENING" in reason_codes:
        return "Thesis or execution state weakened; reduce risk before adding exposure."
    return ""


def _sell_side_category(risk_action: str, portfolio_relative_action: str) -> str:
    normalized = str(risk_action or portfolio_relative_action or "").upper()
    if normalized == RiskAction.TRIM_TO_FUND.value:
        return "funding"
    if normalized == RiskAction.REDUCE_RISK.value:
        return "risk"
    if normalized == RiskAction.TAKE_PROFIT.value:
        return "profit"
    if normalized == RiskAction.STOP_LOSS.value:
        return "stop"
    if normalized == RiskAction.EXIT.value:
        return "exit"
    return "none"


def _strategy_state(*, action_now: str, action_if_triggered: str, is_held: bool, stance: str) -> str:
    if action_now in {"REDUCE_NOW", "TRIM_NOW", "EXIT_NOW", "STOP_LOSS_NOW", "TAKE_PROFIT_NOW"} or action_if_triggered in {
        "REDUCE_IF_TRIGGERED",
        "EXIT_IF_TRIGGERED",
        "STOP_LOSS_IF_TRIGGERED",
        "TAKE_PROFIT_IF_TRIGGERED",
    }:
        return "reduce_or_exit"
    if action_now in {"ADD_NOW", "STARTER_NOW"}:
        return "add_now"
    if action_if_triggered in {"ADD_IF_TRIGGERED", "STARTER_IF_TRIGGERED"}:
        return "add_if_triggered"
    if action_if_triggered == "WATCH_TRIGGER":
        return "watch_if_triggered"
    if is_held and stance == "NEUTRAL":
        return "hold_or_watch"
    return "hold_or_watch"
