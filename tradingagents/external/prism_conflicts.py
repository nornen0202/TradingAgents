from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

from .prism_models import PrismExternalSignal, PrismIngestionResult, PrismSignalAction


TA_BUY_NOW = {"ADD_NOW", "STARTER_NOW"}
TA_BUY_TRIGGER = {"ADD_IF_TRIGGERED", "STARTER_IF_TRIGGERED"}
TA_WAIT = {"HOLD", "WATCH", "NONE", ""}
TA_RISK = {"REDUCE_RISK", "STOP_LOSS", "EXIT", "TAKE_PROFIT"}
PRISM_BUY = {PrismSignalAction.BUY, PrismSignalAction.ADD}
PRISM_SELL_OR_RISK = {
    PrismSignalAction.SELL,
    PrismSignalAction.TRIM_TO_FUND,
    PrismSignalAction.REDUCE_RISK,
    PrismSignalAction.TAKE_PROFIT,
    PrismSignalAction.STOP_LOSS,
    PrismSignalAction.EXIT,
}
PRISM_HARD_SELL = {
    PrismSignalAction.SELL,
    PrismSignalAction.REDUCE_RISK,
    PrismSignalAction.STOP_LOSS,
    PrismSignalAction.EXIT,
}
PRISM_WAIT = {PrismSignalAction.WATCH, PrismSignalAction.HOLD, PrismSignalAction.NO_ENTRY}


def enrich_candidates_with_prism(
    candidates: Iterable[Any],
    ingestion: PrismIngestionResult | None,
    *,
    confidence_cap: float = 0.25,
) -> list[Any]:
    signal_by_ticker = best_prism_signal_by_ticker((ingestion.signals if ingestion else []) or [])
    enriched: list[Any] = []
    cap = abs(float(confidence_cap if confidence_cap is not None else 0.25))
    for candidate in candidates:
        ticker = str(_get(candidate, "instrument").canonical_ticker if _get(candidate, "instrument") else _get(candidate, "canonical_ticker") or "").upper()
        signal = signal_by_ticker.get(ticker)
        patch = _candidate_prism_patch(candidate, signal, cap=cap)
        enriched.append(candidate.__class__(**{**candidate.__dict__, **patch}))
    return enriched


def reconcile_prism_with_actions(
    *,
    tradingagents_actions: Iterable[Any],
    ingestion: PrismIngestionResult | None,
    confidence_cap: float = 0.25,
    asof: str | None = None,
) -> dict[str, Any]:
    action_by_ticker = {_action_ticker(action): action for action in tradingagents_actions if _action_ticker(action)}
    signal_by_ticker = best_prism_signal_by_ticker((ingestion.signals if ingestion else []) or [])
    tickers = sorted(set(action_by_ticker) | set(signal_by_ticker))
    entries = [
        _reconcile_one(ticker, action_by_ticker.get(ticker), signal_by_ticker.get(ticker), confidence_cap=confidence_cap)
        for ticker in tickers
    ]
    summary = _summary(entries, ingestion)
    return {
        "source": "prism",
        "status": "ok" if ingestion and ingestion.ok else ("disabled" if ingestion and not ingestion.enabled else "unavailable"),
        "asof": asof or datetime.now().astimezone().isoformat(),
        "summary": summary,
        "ingestion_status": ingestion.status_dict() if ingestion is not None else None,
        "entries": entries,
    }


def write_prism_signal_artifacts(
    *,
    run_dir: Path,
    ingestion: PrismIngestionResult,
    reconciliation: dict[str, Any],
) -> dict[str, str]:
    output_dir = run_dir / "external_signals"
    output_dir.mkdir(parents=True, exist_ok=True)
    signals_path = output_dir / "prism_signals.json"
    status_path = output_dir / "prism_ingestion_status.json"
    reconciliation_path = output_dir / "prism_reconciliation.json"
    signals_path.write_text(json.dumps(ingestion.signals_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    status_path.write_text(json.dumps(ingestion.status_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    reconciliation_path.write_text(json.dumps(reconciliation, indent=2, ensure_ascii=False), encoding="utf-8")
    return {
        "external_prism_signals_json": signals_path.as_posix(),
        "external_prism_ingestion_status_json": status_path.as_posix(),
        "external_prism_reconciliation_json": reconciliation_path.as_posix(),
    }


def best_prism_signal_by_ticker(signals: Iterable[PrismExternalSignal]) -> dict[str, PrismExternalSignal]:
    result: dict[str, PrismExternalSignal] = {}
    for signal in signals:
        ticker = str(signal.canonical_ticker or "").strip().upper()
        if not ticker:
            continue
        current = result.get(ticker)
        if current is None or _signal_rank(signal) > _signal_rank(current):
            result[ticker] = signal
    return result


def render_external_signal_section(reconciliation: dict[str, Any] | None) -> str:
    if not reconciliation:
        return "\n".join(
            [
                "## 외부 PRISM 신호 요약",
                "",
                "- 수집 상태: unavailable",
                "- PRISM 신호는 외부 참고 자료이며 TradingAgents 리스크 게이트를 우회하지 않습니다.",
            ]
        )
    ingestion = reconciliation.get("ingestion_status") or {}
    summary = reconciliation.get("summary") or {}
    entries = [entry for entry in reconciliation.get("entries") or [] if isinstance(entry, dict)]
    action_counts = summary.get("prism_action_distribution") or {}
    consensus = [entry for entry in entries if str(entry.get("prism_agreement")) in {"confirmed_buy", "confirmed_sell"}]
    conflicts = [entry for entry in entries if str(entry.get("prism_agreement")).startswith("conflict_")]
    lines = [
        "## 외부 PRISM 신호 요약",
        "",
        "- PRISM 신호는 외부 비교/검증용입니다. TradingAgents의 계좌 리스크 게이트를 우회하지 않습니다.",
        f"- 수집 상태: {ingestion.get('source_kind') or ingestion.get('source') or reconciliation.get('status') or 'unavailable'}",
        f"- 총 신호 수: {int(ingestion.get('signals_count') or summary.get('signals_count') or 0)}",
        f"- BUY / SELL / HOLD 분포: BUY {int(action_counts.get('BUY') or 0) + int(action_counts.get('ADD') or 0)} / SELL {int(action_counts.get('SELL') or 0) + int(action_counts.get('REDUCE_RISK') or 0) + int(action_counts.get('STOP_LOSS') or 0) + int(action_counts.get('EXIT') or 0)} / HOLD {int(action_counts.get('HOLD') or 0) + int(action_counts.get('WATCH') or 0)}",
        f"- TradingAgents와 일치한 수: {len(consensus)}",
        f"- 충돌한 수: {len(conflicts)}",
        f"- 성과 기반 신뢰도: {'available' if summary.get('performance_available') else 'unavailable'}",
        "",
        "### PRISM과 TradingAgents가 모두 동의한 후보",
        *_entry_lines(consensus, empty="- 없음"),
        "",
        "### PRISM과 TradingAgents가 충돌한 후보",
        *_entry_lines(conflicts, empty="- 없음"),
    ]
    return "\n".join(lines)


def _candidate_prism_patch(candidate: Any, signal: PrismExternalSignal | None, *, cap: float) -> dict[str, Any]:
    data_health = dict(_get(candidate, "data_health") or {})
    notes: list[str] = list(_get(candidate, "external_signal_notes") or [])
    risk_codes = list(_get(candidate, "risk_action_reason_codes") or [])
    gate_reasons = list(_get(candidate, "gate_reasons") or [])
    signal_payload = [signal.to_dict()] if signal is not None else []
    if signal is None:
        return {
            "external_signals": tuple(),
            "prism_agreement": "no_prism_signal",
            "external_signal_score_delta": 0.0,
            "external_signal_notes": tuple(notes or ["No overlapping PRISM signal."]),
            "data_health": {**data_health, "prism_agreement": "no_prism_signal", "external_signal_score_delta": 0.0},
        }

    agreement, delta, note, block_buy = _classify_candidate(candidate, signal, cap=cap)
    notes.append(note)
    action_now = str(_get(candidate, "suggested_action_now") or "")
    action_if_triggered = str(_get(candidate, "suggested_action_if_triggered") or "")
    review_required = bool(_get(candidate, "review_required"))
    if block_buy:
        review_required = True
        gate_reasons.append("prism_conflict_review_required")
        risk_codes.append("PRISM_CONFLICT_REVIEW")
        if action_now in TA_BUY_NOW:
            action_now = "HOLD" if bool(_get(candidate, "is_held")) else "WATCH"
        if action_if_triggered in TA_BUY_TRIGGER:
            action_if_triggered = "NONE" if bool(_get(candidate, "is_held")) else "WATCH_TRIGGER"

    confidence = float(_get(candidate, "confidence") or 0.0)
    adjusted_confidence = max(0.0, min(1.0, confidence + delta))
    return {
        "external_signals": tuple(signal_payload),
        "prism_agreement": agreement,
        "external_signal_score_delta": round(delta, 4),
        "external_signal_notes": tuple(dict.fromkeys(notes)),
        "suggested_action_now": action_now,
        "suggested_action_if_triggered": action_if_triggered,
        "confidence": adjusted_confidence,
        "review_required": review_required,
        "risk_action_reason_codes": tuple(dict.fromkeys(risk_codes)),
        "gate_reasons": tuple(dict.fromkeys(gate_reasons)),
        "data_health": {
            **data_health,
            "external_signals": signal_payload,
            "prism_agreement": agreement,
            "external_signal_score_delta": round(delta, 4),
            "external_signal_notes": list(dict.fromkeys(notes)),
        },
    }


def _classify_candidate(candidate: Any, signal: PrismExternalSignal, *, cap: float) -> tuple[str, float, str, bool]:
    action = signal.signal_action
    confidence = max(min(float(signal.confidence if signal.confidence is not None else signal.composite_score or 0.5), 1.0), 0.0)
    delta = min(cap, confidence * cap)
    if _is_ta_risk(candidate) and action in PRISM_BUY:
        return (
            "conflict_prism_buy_ta_reduce",
            0.0,
            f"PRISM {action.value} conflicts with TradingAgents risk reduction; no buy permission is granted.",
            True,
        )
    if _is_ta_buy(candidate) and action in PRISM_SELL_OR_RISK:
        return (
            "conflict_prism_sell_ta_buy",
            -delta,
            f"PRISM {action.value} conflicts with TradingAgents buy-side action; immediate buy requires review.",
            True,
        )
    if _is_ta_buy(candidate) and action in PRISM_BUY:
        return (
            "confirmed_buy",
            delta,
            f"PRISM {action.value} confirms the TradingAgents buy-side setup within the advisory cap.",
            False,
        )
    if _is_ta_risk(candidate) and action in PRISM_SELL_OR_RISK:
        return (
            "confirmed_sell",
            min(delta, cap * 0.5),
            f"PRISM {action.value} agrees with TradingAgents sell-side or risk-reduction posture.",
            False,
        )
    if _is_ta_wait(candidate) and action in PRISM_BUY:
        strong = max(float(signal.trigger_score or 0.0), confidence) >= 0.75
        return (
            "prism_watch_only",
            min(delta, cap * (0.4 if strong else 0.25)),
            "PRISM has a constructive trigger while TradingAgents is waiting; raise watchlist priority only.",
            False,
        )
    if action in PRISM_SELL_OR_RISK:
        return (
            "prism_sell_warning",
            -min(delta, cap * 0.5),
            f"PRISM {action.value} is a risk warning; TradingAgents risk gates remain final.",
            False,
        )
    if action in PRISM_WAIT:
        return (
            "prism_watch_only",
            0.0,
            f"PRISM is {action.value}; external confirmation is limited.",
            False,
        )
    return ("no_prism_signal", 0.0, "PRISM signal is unknown or not action-bearing.", False)


def _reconcile_one(ticker: str, action: Any | None, signal: PrismExternalSignal | None, *, confidence_cap: float) -> dict[str, Any]:
    if action is None and signal is not None:
        return {
            "ticker": ticker,
            "display_name": signal.display_name,
            "tradingagents_action": None,
            "tradingagents_risk_action": None,
            "prism_action": signal.signal_action.value,
            "prism_confidence": signal.confidence,
            "prism_agreement": "external_only",
            "agreement": "EXTERNAL_ONLY",
            "recommendation": "EXTERNAL_WATCHLIST_ONLY",
            "reason": "PRISM has a ticker-level signal, but TradingAgents did not analyze this ticker in the current run.",
            "execution_blocked": False,
            "external_signal_score_delta": 0.0,
            "risk_gate_bypass_allowed": False,
        }
    if action is not None and signal is None:
        return {
            "ticker": ticker,
            "display_name": _display_name(action, None),
            "tradingagents_action": _preferred_action(action),
            "tradingagents_risk_action": _risk_action(action),
            "prism_action": None,
            "prism_confidence": None,
            "prism_agreement": "no_prism_signal",
            "agreement": "TRADINGAGENTS_ONLY",
            "recommendation": "USE_TRADINGAGENTS_RISK_GATES",
            "reason": "No overlapping PRISM ticker-level signal was available.",
            "execution_blocked": False,
            "external_signal_score_delta": 0.0,
            "risk_gate_bypass_allowed": False,
        }
    assert action is not None and signal is not None
    agreement, delta, note, blocked = _classify_candidate(_ActionShim(action), signal, cap=abs(float(confidence_cap)))
    return {
        "ticker": ticker,
        "display_name": _display_name(action, signal),
        "tradingagents_action": _preferred_action(action),
        "tradingagents_risk_action": _risk_action(action),
        "prism_action": signal.signal_action.value,
        "prism_confidence": signal.confidence,
        "prism_agreement": agreement,
        "agreement": _legacy_agreement(agreement),
        "recommendation": _recommendation(agreement, blocked),
        "reason": note,
        "execution_blocked": blocked,
        "external_signal_score_delta": round(delta, 4),
        "risk_gate_bypass_allowed": False,
        "trigger_type": signal.trigger_type,
    }


class _ActionShim:
    def __init__(self, action: Any):
        self.instrument = None
        self.canonical_ticker = _get(action, "canonical_ticker")
        self.suggested_action_now = _get(action, "action_now")
        self.suggested_action_if_triggered = _get(action, "action_if_triggered")
        self.action_now = _get(action, "action_now")
        self.action_if_triggered = _get(action, "action_if_triggered")
        self.portfolio_relative_action = _get(action, "portfolio_relative_action")
        self.risk_action = _get(action, "risk_action")
        self.is_held = True
        self.confidence = _get(action, "confidence")


def _signal_rank(signal: PrismExternalSignal) -> tuple[int, float, float]:
    action_priority = {
        PrismSignalAction.STOP_LOSS: 95,
        PrismSignalAction.EXIT: 90,
        PrismSignalAction.SELL: 85,
        PrismSignalAction.REDUCE_RISK: 80,
        PrismSignalAction.TAKE_PROFIT: 75,
        PrismSignalAction.BUY: 70,
        PrismSignalAction.ADD: 68,
        PrismSignalAction.NO_ENTRY: 55,
        PrismSignalAction.WATCH: 45,
        PrismSignalAction.HOLD: 40,
        PrismSignalAction.TRIM_TO_FUND: 35,
        PrismSignalAction.UNKNOWN: 0,
    }
    return (
        action_priority.get(signal.signal_action, 0),
        float(signal.confidence or 0.0),
        float(signal.composite_score or signal.trigger_score or 0.0),
    )


def _summary(entries: list[dict[str, Any]], ingestion: PrismIngestionResult | None) -> dict[str, Any]:
    agreements: dict[str, int] = {}
    actions: dict[str, int] = {}
    for entry in entries:
        key = str(entry.get("agreement") or "UNKNOWN")
        agreements[key] = agreements.get(key, 0) + 1
        action = str(entry.get("prism_action") or "")
        if action:
            actions[action] = actions.get(action, 0) + 1
    return {
        "total_entries": len(entries),
        "signals_count": len(ingestion.signals) if ingestion else 0,
        "agreement_counts": agreements,
        "prism_action_distribution": actions,
        "hard_conflict_count": sum(1 for entry in entries if str(entry.get("agreement")) == "HARD_CONFLICT"),
        "execution_blocked_count": sum(1 for entry in entries if bool(entry.get("execution_blocked"))),
        "consensus_count": sum(1 for entry in entries if str(entry.get("agreement")) == "CONSENSUS"),
        "performance_available": bool(ingestion and ingestion.performance_summary),
    }


def _entry_lines(entries: list[dict[str, Any]], *, empty: str) -> list[str]:
    if not entries:
        return [empty]
    lines: list[str] = []
    for entry in entries[:8]:
        name = str(entry.get("display_name") or entry.get("ticker") or "-")
        ticker = str(entry.get("ticker") or "-")
        ta_action = str(entry.get("tradingagents_action") or "-")
        prism_action = str(entry.get("prism_action") or "-")
        blocked = " / 실행 보류" if bool(entry.get("execution_blocked")) else ""
        lines.append(f"- {name} ({ticker}): TradingAgents `{ta_action}` / PRISM `{prism_action}`{blocked}")
    return lines


def _legacy_agreement(value: str) -> str:
    if value in {"confirmed_buy", "confirmed_sell"}:
        return "CONSENSUS"
    if value.startswith("conflict_"):
        return "HARD_CONFLICT"
    if value == "no_prism_signal":
        return "TRADINGAGENTS_ONLY"
    return "PARTIAL_AGREEMENT"


def _recommendation(agreement: str, blocked: bool) -> str:
    if blocked:
        return "HUMAN_REVIEW_REQUIRED"
    mapping = {
        "confirmed_buy": "HIGH_CONVICTION_CONSENSUS_CANDIDATE",
        "confirmed_sell": "RISK_REDUCTION_CONFIRMED",
        "prism_watch_only": "WATCH_FOR_PILOT",
        "prism_sell_warning": "RISK_REVIEW",
    }
    return mapping.get(agreement, "COMPARE_AS_EXTERNAL_CONTEXT")


def _action_ticker(action: Any) -> str | None:
    value = _get(action, "canonical_ticker")
    text = str(value or "").strip().upper()
    return text or None


def _preferred_action(action: Any) -> str:
    now = str(_get(action, "action_now") or _get(action, "suggested_action_now") or "").upper()
    triggered = str(_get(action, "action_if_triggered") or _get(action, "suggested_action_if_triggered") or "").upper()
    relative = str(_get(action, "portfolio_relative_action") or "").upper()
    if now and now not in {"NONE", "HOLD", "WATCH"}:
        return now
    if triggered and triggered != "NONE":
        return triggered
    return relative or now or "UNKNOWN"


def _risk_action(action: Any) -> str | None:
    risk = str(_get(action, "risk_action") or "").upper()
    relative = str(_get(action, "portfolio_relative_action") or "").upper()
    if risk and risk != "NONE":
        return risk
    if relative in TA_RISK or relative == "TRIM_TO_FUND":
        return relative
    return None


def _is_ta_buy(action: Any) -> bool:
    now = str(_get(action, "action_now") or _get(action, "suggested_action_now") or "").upper()
    triggered = str(_get(action, "action_if_triggered") or _get(action, "suggested_action_if_triggered") or "").upper()
    return now in TA_BUY_NOW or triggered in TA_BUY_TRIGGER


def _is_ta_wait(action: Any) -> bool:
    now = str(_get(action, "action_now") or _get(action, "suggested_action_now") or "").upper()
    triggered = str(_get(action, "action_if_triggered") or _get(action, "suggested_action_if_triggered") or "").upper()
    relative = str(_get(action, "portfolio_relative_action") or "").upper()
    return now in TA_WAIT and triggered not in TA_BUY_TRIGGER and relative in {"", "WATCH", "HOLD", "NONE"}


def _is_ta_risk(action: Any) -> bool:
    now = str(_get(action, "action_now") or _get(action, "suggested_action_now") or "").upper()
    triggered = str(_get(action, "action_if_triggered") or _get(action, "suggested_action_if_triggered") or "").upper()
    risk = str(_get(action, "risk_action") or "").upper()
    relative = str(_get(action, "portfolio_relative_action") or "").upper()
    return (
        risk in TA_RISK
        or relative in TA_RISK
        or now in {"REDUCE_NOW", "TAKE_PROFIT_NOW", "STOP_LOSS_NOW", "EXIT_NOW"}
        or triggered in {"REDUCE_IF_TRIGGERED", "TAKE_PROFIT_IF_TRIGGERED", "STOP_LOSS_IF_TRIGGERED", "EXIT_IF_TRIGGERED"}
    )


def _display_name(action: Any | None, signal: PrismExternalSignal | None) -> str | None:
    if action is not None:
        value = _get(action, "display_name")
        if value:
            return str(value)
    if signal is not None and signal.display_name:
        return signal.display_name
    return None


def _get(value: Any, key: str) -> Any:
    if isinstance(value, dict):
        return value.get(key)
    return getattr(value, key, None)
