from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

from .models import (
    ExternalReconciliationEntry,
    ExternalSignal,
    ExternalSignalAction,
    ExternalSignalIngestion,
    ReconciliationAgreement,
)


_TA_BUY_NOW = {"ADD_NOW", "STARTER_NOW"}
_TA_BUY_TRIGGER = {"ADD_IF_TRIGGERED", "STARTER_IF_TRIGGERED"}
_TA_WAIT = {"HOLD", "WATCH", "NONE", ""}
_TA_RISK = {"REDUCE_RISK", "STOP_LOSS", "EXIT", "TAKE_PROFIT"}
_EXTERNAL_BUY = {ExternalSignalAction.BUY, ExternalSignalAction.ADD}
_EXTERNAL_SELL_OR_RISK = {
    ExternalSignalAction.TRIM_TO_FUND,
    ExternalSignalAction.REDUCE_RISK,
    ExternalSignalAction.TAKE_PROFIT,
    ExternalSignalAction.STOP_LOSS,
    ExternalSignalAction.EXIT,
}
_EXTERNAL_WAIT = {ExternalSignalAction.WATCH, ExternalSignalAction.HOLD, ExternalSignalAction.NO_ENTRY}


def build_external_reconciliation(
    *,
    tradingagents_actions: Iterable[Any],
    external_signals: Iterable[ExternalSignal],
    ingestion: ExternalSignalIngestion | None = None,
    asof: str | None = None,
) -> dict[str, Any]:
    action_by_ticker = {_action_ticker(action): action for action in tradingagents_actions if _action_ticker(action)}
    signal_by_ticker = _best_external_signal_by_ticker(external_signals)
    tickers = sorted(set(action_by_ticker) | set(signal_by_ticker))
    status = "ok" if signal_by_ticker else "unavailable"
    if ingestion is not None:
        status = ingestion.status
    entries = [
        _reconcile_one(ticker, action_by_ticker.get(ticker), signal_by_ticker.get(ticker))
        for ticker in tickers
    ]
    summary = _summary(entries)
    return {
        "source": "prism",
        "status": status,
        "asof": asof or datetime.now().astimezone().isoformat(),
        "summary": summary,
        "ingestion_status": ingestion.status_dict() if ingestion is not None else None,
        "entries": [entry.to_dict() for entry in entries],
    }


def write_external_signal_artifacts(
    *,
    run_dir: Path,
    ingestion: ExternalSignalIngestion,
    reconciliation: dict[str, Any],
) -> dict[str, str]:
    output_dir = run_dir / "external_signals"
    output_dir.mkdir(parents=True, exist_ok=True)
    signals_path = output_dir / "prism_signals.json"
    status_path = output_dir / "prism_ingestion_status.json"
    reconciliation_path = output_dir / "external_reconciliation.json"
    signals_path.write_text(json.dumps(ingestion.signals_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    status_path.write_text(json.dumps(ingestion.status_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    reconciliation_path.write_text(json.dumps(reconciliation, indent=2, ensure_ascii=False), encoding="utf-8")
    return {
        "external_prism_signals_json": signals_path.as_posix(),
        "external_prism_ingestion_status_json": status_path.as_posix(),
        "external_reconciliation_json": reconciliation_path.as_posix(),
    }


def _best_external_signal_by_ticker(signals: Iterable[ExternalSignal]) -> dict[str, ExternalSignal]:
    result: dict[str, ExternalSignal] = {}
    for signal in signals:
        ticker = str(signal.ticker or "").strip().upper()
        if not ticker:
            continue
        current = result.get(ticker)
        if current is None or _signal_rank(signal) > _signal_rank(current):
            result[ticker] = signal
    return result


def _signal_rank(signal: ExternalSignal) -> tuple[int, float, float]:
    action_priority = {
        ExternalSignalAction.STOP_LOSS: 90,
        ExternalSignalAction.EXIT: 85,
        ExternalSignalAction.REDUCE_RISK: 80,
        ExternalSignalAction.TAKE_PROFIT: 75,
        ExternalSignalAction.BUY: 70,
        ExternalSignalAction.ADD: 68,
        ExternalSignalAction.NO_ENTRY: 55,
        ExternalSignalAction.WATCH: 45,
        ExternalSignalAction.HOLD: 40,
        ExternalSignalAction.TRIM_TO_FUND: 35,
        ExternalSignalAction.UNKNOWN: 0,
    }
    return (
        action_priority.get(signal.action, 0),
        float(signal.confidence or 0.0),
        float(signal.score or 0.0),
    )


def _reconcile_one(ticker: str, action: Any | None, signal: ExternalSignal | None) -> ExternalReconciliationEntry:
    ta_action = _preferred_action(action) if action is not None else None
    ta_risk_action = _risk_action(action) if action is not None else None
    display_name = _display_name(action, signal)
    prism_action = signal.action if signal is not None else None

    if action is None and signal is not None:
        return ExternalReconciliationEntry(
            ticker=ticker,
            display_name=display_name,
            tradingagents_action=None,
            tradingagents_risk_action=None,
            prism_action=signal.action.value,
            prism_confidence=signal.confidence,
            agreement=ReconciliationAgreement.EXTERNAL_ONLY,
            recommendation="EXTERNAL_WATCHLIST_ONLY",
            reason="PRISM has a ticker-level signal, but TradingAgents did not analyze this ticker in the current run.",
        )
    if action is not None and signal is None:
        return ExternalReconciliationEntry(
            ticker=ticker,
            display_name=display_name,
            tradingagents_action=ta_action,
            tradingagents_risk_action=ta_risk_action,
            prism_action=None,
            prism_confidence=None,
            agreement=ReconciliationAgreement.TRADINGAGENTS_ONLY,
            recommendation="USE_TRADINGAGENTS_RISK_GATES",
            reason="No overlapping PRISM ticker-level signal was available.",
        )

    assert action is not None and signal is not None
    ta_buy = _is_ta_buy(action)
    ta_wait = _is_ta_wait(action)
    ta_risk = _is_ta_risk(action)
    ta_trim_to_fund = str(_get(action, "portfolio_relative_action") or "").upper() == "TRIM_TO_FUND"

    if ta_risk and signal.action in _EXTERNAL_BUY:
        return ExternalReconciliationEntry(
            ticker=ticker,
            display_name=display_name,
            tradingagents_action=ta_action,
            tradingagents_risk_action=ta_risk_action,
            prism_action=signal.action.value,
            prism_confidence=signal.confidence,
            agreement=ReconciliationAgreement.HARD_CONFLICT,
            recommendation="HUMAN_REVIEW_REQUIRED",
            reason="TradingAgents is reducing risk while PRISM is constructive; immediate execution should be blocked pending review.",
            execution_blocked=True,
        )
    if ta_trim_to_fund and signal.action in _EXTERNAL_BUY:
        return ExternalReconciliationEntry(
            ticker=ticker,
            display_name=display_name,
            tradingagents_action=ta_action,
            tradingagents_risk_action=ta_risk_action,
            prism_action=signal.action.value,
            prism_confidence=signal.confidence,
            agreement=ReconciliationAgreement.HARD_CONFLICT,
            recommendation="DO_NOT_USE_AS_FUNDING_SOURCE_WITHOUT_REVIEW",
            reason="TradingAgents marked this as a funding source, but PRISM has a buy-side signal.",
            execution_blocked=True,
        )
    if ta_buy and signal.action in _EXTERNAL_SELL_OR_RISK:
        return ExternalReconciliationEntry(
            ticker=ticker,
            display_name=display_name,
            tradingagents_action=ta_action,
            tradingagents_risk_action=ta_risk_action,
            prism_action=signal.action.value,
            prism_confidence=signal.confidence,
            agreement=ReconciliationAgreement.HARD_CONFLICT,
            recommendation="BLOCK_IMMEDIATE_EXECUTION",
            reason="TradingAgents is constructive while PRISM is risk-off; require confirmation before acting.",
            execution_blocked=True,
        )
    if ta_buy and signal.action in _EXTERNAL_BUY:
        return ExternalReconciliationEntry(
            ticker=ticker,
            display_name=display_name,
            tradingagents_action=ta_action,
            tradingagents_risk_action=ta_risk_action,
            prism_action=signal.action.value,
            prism_confidence=signal.confidence,
            agreement=ReconciliationAgreement.CONSENSUS,
            recommendation="HIGH_CONVICTION_CONSENSUS_CANDIDATE",
            reason="Both TradingAgents and PRISM are constructive; confidence may improve, but risk gates still apply.",
            confidence_modifier=0.05,
        )
    if ta_buy and signal.action in _EXTERNAL_WAIT:
        return ExternalReconciliationEntry(
            ticker=ticker,
            display_name=display_name,
            tradingagents_action=ta_action,
            tradingagents_risk_action=ta_risk_action,
            prism_action=signal.action.value,
            prism_confidence=signal.confidence,
            agreement=ReconciliationAgreement.PARTIAL_AGREEMENT,
            recommendation="TRADINGAGENTS_ONLY_SIZE_DOWN_OR_CONFIRM",
            reason="TradingAgents is constructive, but PRISM is neutral or no-entry.",
        )
    if ta_wait and signal.action in _EXTERNAL_BUY:
        return ExternalReconciliationEntry(
            ticker=ticker,
            display_name=display_name,
            tradingagents_action=ta_action,
            tradingagents_risk_action=ta_risk_action,
            prism_action=signal.action.value,
            prism_confidence=signal.confidence,
            agreement=ReconciliationAgreement.PARTIAL_AGREEMENT,
            recommendation="WATCH_FOR_PILOT",
            reason="PRISM has a buy-side momentum signal while TradingAgents is waiting for confirmation.",
            confidence_modifier=0.02,
        )

    return ExternalReconciliationEntry(
        ticker=ticker,
        display_name=display_name,
        tradingagents_action=ta_action,
        tradingagents_risk_action=ta_risk_action,
        prism_action=signal.action.value,
        prism_confidence=signal.confidence,
        agreement=ReconciliationAgreement.PARTIAL_AGREEMENT,
        recommendation="COMPARE_AS_EXTERNAL_CONTEXT",
        reason="Signals are not directly contradictory, but they are not a full consensus.",
    )


def _summary(entries: list[ExternalReconciliationEntry]) -> dict[str, Any]:
    counts: dict[str, int] = {}
    for entry in entries:
        key = entry.agreement.value
        counts[key] = counts.get(key, 0) + 1
    return {
        "total_entries": len(entries),
        "agreement_counts": counts,
        "hard_conflict_count": sum(1 for entry in entries if entry.agreement == ReconciliationAgreement.HARD_CONFLICT),
        "execution_blocked_count": sum(1 for entry in entries if entry.execution_blocked),
        "consensus_count": sum(1 for entry in entries if entry.agreement == ReconciliationAgreement.CONSENSUS),
    }


def _action_ticker(action: Any) -> str | None:
    value = _get(action, "canonical_ticker")
    text = str(value or "").strip().upper()
    return text or None


def _preferred_action(action: Any) -> str:
    now = str(_get(action, "action_now") or "").upper()
    triggered = str(_get(action, "action_if_triggered") or "").upper()
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
    if relative in _TA_RISK or relative == "TRIM_TO_FUND":
        return relative
    return None


def _is_ta_buy(action: Any) -> bool:
    now = str(_get(action, "action_now") or "").upper()
    triggered = str(_get(action, "action_if_triggered") or "").upper()
    return now in _TA_BUY_NOW or triggered in _TA_BUY_TRIGGER


def _is_ta_wait(action: Any) -> bool:
    now = str(_get(action, "action_now") or "").upper()
    triggered = str(_get(action, "action_if_triggered") or "").upper()
    relative = str(_get(action, "portfolio_relative_action") or "").upper()
    return now in _TA_WAIT and triggered not in _TA_BUY_TRIGGER and relative in {"", "WATCH", "HOLD", "NONE"}


def _is_ta_risk(action: Any) -> bool:
    now = str(_get(action, "action_now") or "").upper()
    triggered = str(_get(action, "action_if_triggered") or "").upper()
    risk = str(_get(action, "risk_action") or "").upper()
    relative = str(_get(action, "portfolio_relative_action") or "").upper()
    return (
        risk in _TA_RISK
        or relative in _TA_RISK
        or now in {"REDUCE_NOW", "TAKE_PROFIT_NOW", "STOP_LOSS_NOW", "EXIT_NOW"}
        or triggered in {"REDUCE_IF_TRIGGERED", "TAKE_PROFIT_IF_TRIGGERED", "STOP_LOSS_IF_TRIGGERED", "EXIT_IF_TRIGGERED"}
    )


def _display_name(action: Any | None, signal: ExternalSignal | None) -> str | None:
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
