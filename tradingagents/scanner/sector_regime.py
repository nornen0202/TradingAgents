from __future__ import annotations

from typing import Any, Iterable

from .models import BuyMatrix


REGIME_SLOT_POLICY: dict[str, tuple[int, int]] = {
    "strong_bull": (2, 1),
    "moderate_bull": (1, 2),
    "sideways": (1, 2),
    "moderate_bear": (1, 2),
    "strong_bear": (0, 3),
    "unknown": (1, 2),
}
MACRO_ADJUSTMENT = {
    "strong_bull": 0.15,
    "constructive": 0.10,
    "moderate_bull": 0.05,
    "constructive_but_selective": 0.05,
    "sideways": 0.0,
    "mixed": 0.0,
    "moderate_bear": -0.10,
    "defensive": -0.10,
    "strong_bear": -0.20,
}


def evaluate_buy_matrix(
    candidate: Any,
    *,
    market_regime: str | None = None,
    min_score_required: float = 0.60,
    risk_reward_floor: float = 1.30,
) -> BuyMatrix:
    data = _mapping(candidate)
    structured = data.get("structured_decision") if isinstance(data.get("structured_decision"), dict) else {}
    data_health = data.get("data_health") if isinstance(data.get("data_health"), dict) else {}
    trigger_profile = data.get("trigger_profile") if isinstance(data.get("trigger_profile"), dict) else {}
    buy_matrix_raw = structured.get("buy_matrix") if isinstance(structured, dict) else {}

    profitability = _optional_bool(_first_present(buy_matrix_raw, data_health, "profitability_gate", "profitability"))
    balance_sheet = _optional_bool(_first_present(buy_matrix_raw, data_health, "balance_sheet_gate", "balance_sheet"))
    growth = _optional_bool(_first_present(buy_matrix_raw, data_health, "growth_gate", "growth"))
    clarity = _optional_bool(_first_present(buy_matrix_raw, data_health, "business_clarity_gate", "business_clarity"))
    rr = _optional_float(
        _first_present(buy_matrix_raw, data_health, "risk_reward_ratio", "risk_reward", "external_risk_reward_ratio")
    )
    if rr is None:
        for signal in data.get("external_signals") or []:
            if isinstance(signal, dict) and signal.get("risk_reward_ratio") not in (None, ""):
                rr = _optional_float(signal.get("risk_reward_ratio"))
                break
    sector_score = _optional_float(_first_present(buy_matrix_raw, data_health, "sector_leadership_score"))
    momentum_count = _momentum_signal_count(data, data_health, trigger_profile)
    regime = str(market_regime or data_health.get("market_regime") or "unknown").strip().lower() or "unknown"
    macro_adjustment = MACRO_ADJUSTMENT.get(regime, 0.0)

    hard_fails: list[str] = []
    for label, value in (
        ("profitability_gate", profitability),
        ("balance_sheet_gate", balance_sheet),
        ("growth_gate", growth),
        ("business_clarity_gate", clarity),
    ):
        if value is False:
            hard_fails.append(label)
    rr_passed = None if rr is None else rr >= risk_reward_floor
    if rr_passed is False:
        hard_fails.append("risk_reward_floor")

    gate_values = [profitability, balance_sheet, growth, clarity]
    known_gate_values = [value for value in gate_values if value is not None]
    gate_score = (
        sum(1.0 for value in known_gate_values if value) / len(known_gate_values)
        if known_gate_values
        else 0.55
    )
    momentum_score = min(momentum_count / 4.0, 1.0)
    rr_score = 0.55 if rr is None else min(max((rr - 0.8) / 1.2, 0.0), 1.0)
    sector_component = 0.50 if sector_score is None else max(min(sector_score, 1.0), 0.0)
    effective_score = max(
        0.0,
        min(
            1.0,
            gate_score * 0.30
            + momentum_score * 0.35
            + rr_score * 0.20
            + sector_component * 0.10
            + 0.05
            + macro_adjustment,
        ),
    )
    passed = effective_score >= min_score_required and not hard_fails
    warnings = []
    if not known_gate_values:
        warnings.append("fundamental_gates_unavailable")
    if rr is None:
        warnings.append("risk_reward_unavailable")
    return BuyMatrix(
        profitability_gate=profitability,
        balance_sheet_gate=balance_sheet,
        growth_gate=growth,
        business_clarity_gate=clarity,
        momentum_signal_count=momentum_count,
        macro_adjustment=macro_adjustment,
        risk_reward_ratio=rr,
        risk_reward_floor_passed=rr_passed,
        sector_leadership_score=sector_score,
        market_regime=regime,
        effective_score=round(effective_score, 4),
        min_score_required=min_score_required,
        passed=passed,
        fail_reasons=tuple(dict.fromkeys(hard_fails)),
        warnings=warnings,
    )


def apply_buy_matrix_overlay(
    candidates: Iterable[Any],
    *,
    market_regime: str | None = None,
    min_score_required: float = 0.60,
    score_delta_cap: float = 0.05,
) -> list[Any]:
    result: list[Any] = []
    for candidate in candidates:
        matrix = evaluate_buy_matrix(
            candidate,
            market_regime=market_regime,
            min_score_required=min_score_required,
        )
        data_health = dict(getattr(candidate, "data_health", {}) or {})
        gate_reasons = list(getattr(candidate, "gate_reasons", ()) or ())
        notes = list(getattr(candidate, "external_signal_notes", ()) or ())
        action_now = str(getattr(candidate, "suggested_action_now", "") or "")
        action_if_triggered = str(getattr(candidate, "suggested_action_if_triggered", "") or "")
        confidence = float(getattr(candidate, "confidence", 0.0) or 0.0)
        delta = min(score_delta_cap, max(score_delta_cap * (matrix.effective_score - min_score_required), -score_delta_cap))
        if not matrix.passed and not matrix.fail_reasons:
            delta = 0.0

        if matrix.passed:
            gate_reasons.append("BUY_MATRIX_PASS")
            notes.append(f"BuyMatrix passed at {matrix.effective_score:.2f}.")
            if (
                action_now in {"WATCH", "HOLD"}
                and action_if_triggered in {"NONE", "WATCH_TRIGGER"}
                and str(getattr(candidate, "stance", "")).upper() == "BULLISH"
                and str(getattr(candidate, "risk_action", "NONE")).upper() in {"NONE", "HOLD"}
            ):
                action_if_triggered = "ADD_IF_TRIGGERED" if bool(getattr(candidate, "is_held", False)) else "STARTER_IF_TRIGGERED"
        else:
            gate_reasons.append("BUY_MATRIX_FAIL" if matrix.fail_reasons else "BUY_MATRIX_REVIEW")
            notes.append(f"BuyMatrix did not pass: {', '.join(matrix.fail_reasons) or 'review required'}.")
            if matrix.fail_reasons and action_now in {"ADD_NOW", "STARTER_NOW"}:
                action_now = "HOLD" if bool(getattr(candidate, "is_held", False)) else "WATCH"
                if action_if_triggered == "NONE":
                    action_if_triggered = "ADD_IF_TRIGGERED" if bool(getattr(candidate, "is_held", False)) else "STARTER_IF_TRIGGERED"

        result.append(
            candidate.__class__(
                **{
                    **candidate.__dict__,
                    "suggested_action_now": action_now,
                    "suggested_action_if_triggered": action_if_triggered,
                    "confidence": max(0.0, min(1.0, confidence + delta)),
                    "buy_matrix": matrix.to_dict(),
                    "gate_reasons": tuple(dict.fromkeys(gate_reasons)),
                    "external_signal_notes": tuple(dict.fromkeys(notes)),
                    "data_health": {
                        **data_health,
                        "buy_matrix": matrix.to_dict(),
                    },
                }
            )
        )
    return result


def regime_slots(regime: str | None) -> tuple[int, int]:
    return REGIME_SLOT_POLICY.get(str(regime or "unknown").strip().lower(), REGIME_SLOT_POLICY["unknown"])


def _mapping(candidate: Any) -> dict[str, Any]:
    if isinstance(candidate, dict):
        return candidate
    payload = dict(getattr(candidate, "__dict__", {}) or {})
    instrument = payload.get("instrument")
    if instrument is not None:
        payload["canonical_ticker"] = getattr(instrument, "canonical_ticker", None)
        payload["display_name"] = getattr(instrument, "display_name", None)
    return payload


def _first_present(*mappings_and_keys: Any) -> Any:
    mappings = [item for item in mappings_and_keys if isinstance(item, dict)]
    keys = [item for item in mappings_and_keys if isinstance(item, str)]
    for mapping in mappings:
        for key in keys:
            if key in mapping and mapping[key] not in (None, ""):
                return mapping[key]
    return None


def _optional_bool(value: Any) -> bool | None:
    if value in (None, ""):
        return None
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "y", "pass", "passed"}:
        return True
    if text in {"0", "false", "no", "n", "fail", "failed"}:
        return False
    return None


def _optional_float(value: Any) -> float | None:
    if value in (None, "") or isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if 1.0 < number <= 100.0 and "score" in str(value).lower():
        return number / 100.0
    return number


def _momentum_signal_count(data: dict[str, Any], data_health: dict[str, Any], trigger_profile: dict[str, Any]) -> int:
    tokens: set[str] = set()
    for value in data.get("trigger_conditions") or []:
        tokens.add(str(value).strip().lower())
    for value in (
        trigger_profile.get("primary_trigger_type"),
        trigger_profile.get("trigger_quality"),
        data_health.get("execution_timing_state"),
        data_health.get("prism_agreement"),
    ):
        if str(value or "").strip():
            tokens.add(str(value).strip().lower())
    if data_health.get("session_vwap_ok") is True:
        tokens.add("vwap")
    if data_health.get("relative_volume_ok") is True:
        tokens.add("volume_surge")
    count = 0
    haystack = " ".join(tokens)
    for token in (
        "volume",
        "foreign",
        "52w",
        "sector",
        "breakout",
        "close",
        "pilot_ready",
        "confirmed_buy",
    ):
        if token in haystack:
            count += 1
    return count
