from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

from .prism_models import PrismCoverageSummary, PrismExternalSignal, PrismIngestionResult, PrismSignalAction
from .prism_normalize import normalize_market


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
    run_market: str | None = None,
) -> list[Any]:
    signals = list((ingestion.signals if ingestion else []) or [])
    same_market_signals = _same_market_signals(signals, run_market=run_market)
    signal_by_ticker = best_prism_signal_by_ticker(same_market_signals)
    coverage_status = _candidate_coverage_status(ingestion, same_market_signals, run_market=run_market)
    enriched: list[Any] = []
    cap = abs(float(confidence_cap if confidence_cap is not None else 0.25))
    for candidate in candidates:
        ticker = str(_get(candidate, "instrument").canonical_ticker if _get(candidate, "instrument") else _get(candidate, "canonical_ticker") or "").upper()
        signal = signal_by_ticker.get(ticker)
        patch = _candidate_prism_patch(candidate, signal, cap=cap, coverage_status=coverage_status)
        enriched.append(candidate.__class__(**{**candidate.__dict__, **patch}))
    return enriched


def reconcile_prism_with_actions(
    *,
    tradingagents_actions: Iterable[Any],
    ingestion: PrismIngestionResult | None,
    confidence_cap: float = 0.25,
    asof: str | None = None,
    run_market: str | None = None,
) -> dict[str, Any]:
    action_by_ticker = {_action_ticker(action): action for action in tradingagents_actions if _action_ticker(action)}
    signals = list((ingestion.signals if ingestion else []) or [])
    same_market_signals = _same_market_signals(signals, run_market=run_market)
    signal_by_ticker = best_prism_signal_by_ticker(same_market_signals)
    coverage_status = _candidate_coverage_status(ingestion, same_market_signals, run_market=run_market)
    tickers = sorted(set(action_by_ticker) | set(signal_by_ticker))
    entries = [
        _reconcile_one(
            ticker,
            action_by_ticker.get(ticker),
            signal_by_ticker.get(ticker),
            confidence_cap=confidence_cap,
            run_market=run_market,
            coverage_status=coverage_status,
        )
        for ticker in tickers
    ]
    coverage = build_prism_coverage_summary(
        ingestion,
        run_market=run_market,
        run_tickers=action_by_ticker.keys(),
    )
    summary = _summary(entries, ingestion, coverage=coverage)
    return {
        "source": "prism",
        "status": "ok" if ingestion and ingestion.ok else ("disabled" if ingestion and not ingestion.enabled else "unavailable"),
        "asof": asof or datetime.now().astimezone().isoformat(),
        "run_market": _normalize_run_market(run_market),
        "summary": summary,
        "coverage_summary": coverage.to_dict(),
        "ingestion_status": ingestion.status_dict() if ingestion is not None else None,
        "entries": entries,
    }


def write_prism_signal_artifacts(
    *,
    run_dir: Path,
    ingestion: PrismIngestionResult,
    reconciliation: dict[str, Any],
    allow_cross_market_candidates: bool = False,
) -> dict[str, str]:
    output_dir = run_dir / "external_signals"
    output_dir.mkdir(parents=True, exist_ok=True)
    signals_path = output_dir / "prism_signals.json"
    status_path = output_dir / "prism_ingestion_status.json"
    reconciliation_path = output_dir / "prism_reconciliation.json"
    signals_path.write_text(json.dumps(ingestion.signals_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    status_payload = ingestion.status_dict()
    coverage = reconciliation.get("coverage_summary") if isinstance(reconciliation, dict) else None
    if isinstance(coverage, dict):
        status_payload["coverage_summary"] = coverage
        status_payload["prism_market_coverage"] = {
            "run_market": coverage.get("run_market"),
            "total_signals": coverage.get("total_signals"),
            "matching_market_signals": coverage.get("matching_market_signals"),
            "excluded_cross_market_signals": coverage.get("cross_market_signals"),
            "allow_cross_market_candidates": bool(allow_cross_market_candidates),
        }
    status_path.write_text(json.dumps(status_payload, indent=2, ensure_ascii=False), encoding="utf-8")
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


def build_prism_coverage_summary(
    ingestion: PrismIngestionResult | None,
    *,
    run_market: str | None,
    run_tickers: Iterable[str] | None = None,
) -> PrismCoverageSummary:
    signals = list((ingestion.signals if ingestion else []) or [])
    normalized_run_market = _normalize_run_market(run_market)
    source_markets: dict[str, int] = {}
    for signal in signals:
        market = _signal_market(signal)
        source_markets[market] = source_markets.get(market, 0) + 1

    same_market = _same_market_signals(signals, run_market=normalized_run_market)
    run_ticker_set = {str(ticker or "").strip().upper() for ticker in (run_tickers or []) if str(ticker or "").strip()}
    same_market_tickers = {str(signal.canonical_ticker or "").strip().upper() for signal in same_market}
    actions = [signal.signal_action for signal in signals]
    buy_actions = {PrismSignalAction.BUY, PrismSignalAction.ADD}
    sell_actions = PRISM_SELL_OR_RISK
    hold_actions = {PrismSignalAction.HOLD, PrismSignalAction.WATCH, PrismSignalAction.NO_ENTRY}
    warnings = list((ingestion.warnings if ingestion else []) or [])
    if signals and normalized_run_market != "UNKNOWN" and not same_market:
        warnings.append("prism_no_current_market_coverage")
    return PrismCoverageSummary(
        source_kind=ingestion.source_kind.value if ingestion and ingestion.source_kind else "",
        source=ingestion.source if ingestion else None,
        source_markets=dict(sorted(source_markets.items())),
        run_market=normalized_run_market,
        total_signals=len(signals),
        matching_market_signals=len(same_market),
        overlapping_tickers=len(run_ticker_set & same_market_tickers) if run_ticker_set else 0,
        cross_market_signals=max(len(signals) - len(same_market), 0),
        buy_count=sum(1 for action in actions if action in buy_actions),
        sell_count=sum(1 for action in actions if action in sell_actions),
        hold_count=sum(1 for action in actions if action in hold_actions),
        unknown_count=sum(1 for action in actions if action == PrismSignalAction.UNKNOWN),
        confidence_available_count=sum(1 for signal in signals if signal.confidence is not None),
        performance_available=bool(ingestion and ingestion.performance_summary),
        warnings=list(dict.fromkeys(warnings)),
    )


def filter_prism_signals_for_market(
    signals: Iterable[PrismExternalSignal],
    *,
    run_market: str | None,
    allow_cross_market_candidates: bool = False,
    allowed_markets: Iterable[str] | None = None,
) -> list[PrismExternalSignal]:
    run = _normalize_run_market(run_market)
    allowed = {_normalize_run_market(value) for value in (allowed_markets or []) if str(value or "").strip()}
    allowed.discard("UNKNOWN")
    if run == "UNKNOWN" and not allowed:
        return list(signals)
    allowed.add(run)
    if not allow_cross_market_candidates:
        allowed = {run}
    return [signal for signal in signals if _signal_market(signal) in allowed]


def prism_market_coverage_dict(
    ingestion: PrismIngestionResult | None,
    *,
    run_market: str | None,
    allow_cross_market_candidates: bool = False,
) -> dict[str, Any]:
    coverage = build_prism_coverage_summary(ingestion, run_market=run_market)
    return {
        "run_market": coverage.run_market,
        "total_signals": coverage.total_signals,
        "matching_market_signals": coverage.matching_market_signals,
        "excluded_cross_market_signals": coverage.cross_market_signals,
        "allow_cross_market_candidates": bool(allow_cross_market_candidates),
    }


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
    coverage = reconciliation.get("coverage_summary") or summary.get("coverage_summary") or {}
    entries = [entry for entry in reconciliation.get("entries") or [] if isinstance(entry, dict)]
    action_counts = summary.get("prism_action_distribution") or {}
    consensus = [entry for entry in entries if str(entry.get("prism_agreement")) in {"confirmed_buy", "confirmed_sell"}]
    conflicts = [entry for entry in entries if str(entry.get("prism_agreement")).startswith("conflict_")]
    source_markets = coverage.get("source_markets") if isinstance(coverage, dict) else {}
    market_summary = _format_source_market_summary(source_markets)
    run_market = str((coverage or {}).get("run_market") or reconciliation.get("run_market") or "UNKNOWN")
    matching_market = int((coverage or {}).get("matching_market_signals") or 0)
    cross_market = int((coverage or {}).get("cross_market_signals") or 0)
    status = str(reconciliation.get("status") or "").lower()
    if status == "disabled" or ingestion.get("enabled") is False:
        collection_status = "PRISM 미사용"
    elif status == "unavailable" or ingestion.get("ok") is False:
        collection_status = "PRISM 수집 실패"
    else:
        collection_status = str(ingestion.get("source_kind") or ingestion.get("source") or reconciliation.get("status") or "unavailable")
    coverage_label = ""
    if collection_status == "PRISM 미사용":
        coverage_label = "PRISM 미사용"
    elif collection_status == "PRISM 수집 실패":
        coverage_label = "PRISM 수집 실패"
    elif matching_market <= 0 and cross_market > 0:
        coverage_label = "PRISM 현재 시장 커버리지 없음"
    elif matching_market > 0:
        coverage_label = "PRISM 같은 시장 커버리지 있음"
    lines = [
        "## 외부 PRISM 신호 요약",
        "",
        "- PRISM 신호는 외부 비교/검증용입니다. TradingAgents의 계좌 리스크 게이트를 우회하지 않습니다.",
        f"- 수집 상태: {collection_status}",
        f"- 총 신호 수: {int(ingestion.get('signals_count') or summary.get('signals_count') or 0)}",
        f"- 수집 시장: {market_summary}",
        f"- 현재 리포트 시장: {run_market}",
        f"- 커버리지 상태: {coverage_label or 'UNKNOWN'}",
        f"- 현재 시장에 매칭된 PRISM 신호: {matching_market}개",
        f"- 교차시장 신호는 후보 생성/충돌 판단에서 {'제외됨' if cross_market else '해당 없음'}",
        f"- BUY / SELL / HOLD 분포: BUY {int(action_counts.get('BUY') or 0) + int(action_counts.get('ADD') or 0)} / SELL {int(action_counts.get('SELL') or 0) + int(action_counts.get('REDUCE_RISK') or 0) + int(action_counts.get('STOP_LOSS') or 0) + int(action_counts.get('EXIT') or 0)} / HOLD {int(action_counts.get('HOLD') or 0) + int(action_counts.get('WATCH') or 0)}",
        f"- TradingAgents와 일치한 수: {len(consensus)}",
        f"- 충돌한 수: {len(conflicts)}",
        f"- 성과 기반 신뢰도: {'사용 가능' if summary.get('performance_available') else 'PRISM 성과 데이터 없음'}",
        "",
        "### PRISM과 TradingAgents가 모두 동의한 후보",
        *_entry_lines(consensus, empty="- 없음"),
        "",
        "### PRISM과 TradingAgents가 충돌한 후보",
        *_entry_lines(conflicts, empty="- 없음"),
    ]
    return "\n".join(lines)


def _candidate_prism_patch(
    candidate: Any,
    signal: PrismExternalSignal | None,
    *,
    cap: float,
    coverage_status: str = "NO_SIGNAL",
) -> dict[str, Any]:
    data_health = dict(_get(candidate, "data_health") or {})
    notes: list[str] = list(_get(candidate, "external_signal_notes") or [])
    risk_codes = list(_get(candidate, "risk_action_reason_codes") or [])
    gate_reasons = list(_get(candidate, "gate_reasons") or [])
    signal_payload = [signal.to_dict()] if signal is not None else []
    if signal is None:
        agreement = _agreement_for_coverage_status(coverage_status)
        note = _note_for_coverage_status(coverage_status)
        return {
            "external_signals": tuple(),
            "prism_agreement": agreement,
            "external_signal_score_delta": 0.0,
            "external_signal_notes": tuple(notes or [note]),
            "data_health": {
                **data_health,
                "prism_agreement": agreement,
                "prism_coverage_status": coverage_status,
                "external_signal_score_delta": 0.0,
            },
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
            "prism_coverage_status": "MATCHED",
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


def _reconcile_one(
    ticker: str,
    action: Any | None,
    signal: PrismExternalSignal | None,
    *,
    confidence_cap: float,
    run_market: str | None = None,
    coverage_status: str = "NO_SIGNAL",
) -> dict[str, Any]:
    if action is None and signal is not None:
        return {
            "ticker": ticker,
            "run_market": _normalize_run_market(run_market),
            "display_name": signal.display_name,
            "tradingagents_action": None,
            "tradingagents_risk_action": None,
            "ta_action_now": None,
            "ta_action_if_triggered": None,
            "ta_risk_action": None,
            "prism_action": signal.signal_action.value,
            "prism_signal": signal.to_dict(),
            "prism_confidence": signal.confidence,
            "prism_agreement": "external_only",
            "coverage_status": "MATCHED",
            "agreement": "EXTERNAL_ONLY",
            "recommendation": "EXTERNAL_WATCHLIST_ONLY",
            "reason": "PRISM has a ticker-level signal, but TradingAgents did not analyze this ticker in the current run.",
            "execution_blocked": False,
            "external_signal_score_delta": 0.0,
            "risk_gate_bypass_allowed": False,
        }
    if action is not None and signal is None:
        agreement = _agreement_for_coverage_status(coverage_status)
        return {
            "ticker": ticker,
            "run_market": _normalize_run_market(run_market),
            "display_name": _display_name(action, None),
            "tradingagents_action": _preferred_action(action),
            "tradingagents_risk_action": _risk_action(action),
            "ta_action_now": _get(action, "action_now") or _get(action, "suggested_action_now"),
            "ta_action_if_triggered": _get(action, "action_if_triggered") or _get(action, "suggested_action_if_triggered"),
            "ta_risk_action": _risk_action(action),
            "prism_action": None,
            "prism_signal": None,
            "prism_confidence": None,
            "prism_agreement": agreement,
            "coverage_status": coverage_status,
            "agreement": "no_prism_signal" if coverage_status in {"NO_SIGNAL", "NO_SAME_MARKET_SIGNAL"} else agreement,
            "recommendation": "use_ta_only",
            "reason": _reason_for_coverage_status(coverage_status),
            "execution_blocked": False,
            "external_signal_score_delta": 0.0,
            "risk_gate_bypass_allowed": False,
        }
    assert action is not None and signal is not None
    agreement, delta, note, blocked = _classify_candidate(_ActionShim(action), signal, cap=abs(float(confidence_cap)))
    return {
        "ticker": ticker,
        "run_market": _normalize_run_market(run_market),
        "display_name": _display_name(action, signal),
        "tradingagents_action": _preferred_action(action),
        "tradingagents_risk_action": _risk_action(action),
        "ta_action_now": _get(action, "action_now") or _get(action, "suggested_action_now"),
        "ta_action_if_triggered": _get(action, "action_if_triggered") or _get(action, "suggested_action_if_triggered"),
        "ta_risk_action": _risk_action(action),
        "prism_action": signal.signal_action.value,
        "prism_signal": signal.to_dict(),
        "prism_confidence": signal.confidence,
        "prism_agreement": agreement,
        "coverage_status": "MATCHED",
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


def _summary(
    entries: list[dict[str, Any]],
    ingestion: PrismIngestionResult | None,
    *,
    coverage: PrismCoverageSummary | None = None,
) -> dict[str, Any]:
    agreements: dict[str, int] = {}
    actions: dict[str, int] = {}
    for entry in entries:
        key = str(entry.get("agreement") or "UNKNOWN")
        agreements[key] = agreements.get(key, 0) + 1
        action = str(entry.get("prism_action") or "")
        if action:
            actions[action] = actions.get(action, 0) + 1
    result = {
        "total_entries": len(entries),
        "signals_count": len(ingestion.signals) if ingestion else 0,
        "agreement_counts": agreements,
        "prism_action_distribution": actions,
        "hard_conflict_count": sum(1 for entry in entries if str(entry.get("agreement")) == "HARD_CONFLICT"),
        "execution_blocked_count": sum(1 for entry in entries if bool(entry.get("execution_blocked"))),
        "consensus_count": sum(1 for entry in entries if str(entry.get("agreement")) == "CONSENSUS"),
        "performance_available": bool(ingestion and ingestion.performance_summary),
    }
    if coverage is not None:
        result["coverage_summary"] = coverage.to_dict()
        result["prism_market_coverage"] = {
            "run_market": coverage.run_market,
            "total_signals": coverage.total_signals,
            "matching_market_signals": coverage.matching_market_signals,
            "excluded_cross_market_signals": coverage.cross_market_signals,
        }
    return result


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
    if value in {"no_prism_signal", "no_same_market_prism_coverage", "prism_disabled", "prism_ingestion_failed"}:
        return "TRADINGAGENTS_ONLY"
    return "PARTIAL_AGREEMENT"


def _recommendation(agreement: str, blocked: bool) -> str:
    if blocked:
        return "block_buy_review_required"
    mapping = {
        "confirmed_buy": "high_conviction_consensus_candidate",
        "confirmed_sell": "risk_reduction_confirmed",
        "prism_watch_only": "watch_for_pilot",
        "prism_sell_warning": "risk_review",
    }
    return mapping.get(agreement, "compare_as_external_context")


def _same_market_signals(
    signals: Iterable[PrismExternalSignal],
    *,
    run_market: str | None,
) -> list[PrismExternalSignal]:
    normalized = _normalize_run_market(run_market)
    if normalized == "UNKNOWN":
        return list(signals)
    return [signal for signal in signals if _signal_market(signal) == normalized]


def _signal_market(signal: PrismExternalSignal) -> str:
    return normalize_market(getattr(signal, "market", None), ticker=getattr(signal, "canonical_ticker", None))


def _normalize_run_market(value: Any) -> str:
    text = str(value or "").strip().upper()
    if text in {"KR", "KOREA", "KRX", "KQ", "KS"}:
        return "KR"
    if text in {"US", "USA", "NASDAQ", "NYSE", "AMEX"}:
        return "US"
    return "UNKNOWN"


def _candidate_coverage_status(
    ingestion: PrismIngestionResult | None,
    same_market_signals: list[PrismExternalSignal],
    *,
    run_market: str | None,
) -> str:
    if ingestion is None or not ingestion.enabled:
        return "DISABLED"
    if not ingestion.ok:
        return "INGESTION_FAILED"
    if _normalize_run_market(run_market) != "UNKNOWN" and ingestion.signals and not same_market_signals:
        return "NO_SAME_MARKET_SIGNAL"
    return "NO_SIGNAL"


def _agreement_for_coverage_status(status: str) -> str:
    normalized = str(status or "").strip().upper()
    if normalized == "DISABLED":
        return "prism_disabled"
    if normalized == "INGESTION_FAILED":
        return "prism_ingestion_failed"
    if normalized == "NO_SAME_MARKET_SIGNAL":
        return "no_same_market_prism_coverage"
    return "no_prism_signal"


def _note_for_coverage_status(status: str) -> str:
    normalized = str(status or "").strip().upper()
    if normalized == "DISABLED":
        return "PRISM integration is disabled."
    if normalized == "INGESTION_FAILED":
        return "PRISM ingestion failed for this run."
    if normalized == "NO_SAME_MARKET_SIGNAL":
        return "PRISM source contains signals for another market."
    return "No same-market PRISM ticker-level signal was available."


def _reason_for_coverage_status(status: str) -> str:
    normalized = str(status or "").strip().upper()
    if normalized == "NO_SAME_MARKET_SIGNAL":
        return "PRISM source contains signals for another market for this run."
    if normalized == "DISABLED":
        return "PRISM integration is disabled for this run."
    if normalized == "INGESTION_FAILED":
        return "PRISM was enabled but ingestion failed."
    return "No overlapping same-market PRISM ticker-level signal was available."


def _format_source_market_summary(source_markets: Any) -> str:
    if not isinstance(source_markets, dict) or not source_markets:
        return "UNKNOWN"
    total = sum(int(value or 0) for value in source_markets.values())
    parts = [f"{market} {int(count or 0)}개" for market, count in sorted(source_markets.items())]
    if len(source_markets) == 1:
        market, count = next(iter(source_markets.items()))
        return f"{market} inferred from {int(count or 0)}/{total} signals"
    return ", ".join(parts)


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
