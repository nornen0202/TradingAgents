from __future__ import annotations

from datetime import datetime
from typing import Any

from tradingagents.portfolio.account_models import AccountSnapshot, PortfolioCandidate, PortfolioRecommendation
from tradingagents.presentation import present_account_action, present_market_regime, present_snapshot_mode


def build_portfolio_summary_image_spec(
    *,
    snapshot: AccountSnapshot,
    recommendation: PortfolioRecommendation,
    candidates: list[PortfolioCandidate],
    manifest: dict[str, Any],
    live_sell_side_delta: list[dict[str, Any]] | None = None,
    report_writer_payload: dict[str, Any] | None = None,
    redact_account_values: bool = False,
) -> dict[str, Any]:
    """Build a compact, deterministic data contract for the web summary image."""
    settings = manifest.get("settings") or {}
    market = str(settings.get("market") or settings.get("run_market") or "").strip().upper()
    if not market or market == "AUTO":
        market = _infer_market(manifest)
    report_kind = "계좌 운용" if snapshot.snapshot_health != "WATCHLIST_ONLY" else "종목 분석"
    title = f"TradingAgents {market or 'Market'} {report_kind} 리포트 요약"
    summary = manifest.get("summary") or {}
    counts = _candidate_counts(recommendation)
    sell_side = recommendation.data_health_summary.get("sell_side_distribution") or {}
    top_priority = _top_priority_actions(recommendation)
    next_checkpoints = _next_checkpoints(recommendation)
    position_guide = _position_guide(recommendation)
    writer_summary = _writer_summary(report_writer_payload)

    return {
        "artifact_type": "portfolio_summary_image",
        "version": 1,
        "generated_at": datetime.now().astimezone().isoformat(),
        "title": title,
        "run": {
            "run_id": str(manifest.get("run_id") or ""),
            "date": str(manifest.get("daily_thesis_trade_date") or manifest.get("started_at") or "")[:10],
            "status": str(manifest.get("status") or "unknown"),
            "total_tickers": int(summary.get("total_tickers") or len(manifest.get("tickers") or [])),
            "successful_tickers": int(summary.get("successful_tickers") or 0),
            "failed_tickers": int(summary.get("failed_tickers") or 0),
            "category": str(manifest.get("market_session_phase") or ""),
        },
        "badges": {
            "snapshot_mode": present_snapshot_mode(snapshot.snapshot_health, language="Korean"),
            "market_regime": present_market_regime(recommendation.market_regime, language="Korean"),
            "status": _status_label(str(manifest.get("status") or "unknown")),
        },
        "account": {
            "account_value": _money_or_redacted(snapshot.account_value_krw, redact=redact_account_values),
            "available_cash": _money_or_redacted(snapshot.available_cash_krw, redact=redact_account_values),
            "min_cash_buffer": _money_or_redacted(snapshot.constraints.min_cash_buffer_krw, redact=redact_account_values),
            "mode": present_snapshot_mode(snapshot.snapshot_health, language="Korean"),
            "redacted": bool(redact_account_values),
        },
        "summary_text": {
            "headline": writer_summary.get("headline_action") or _default_headline(counts),
            "one_sentence": writer_summary.get("one_sentence_summary") or _default_sentence(counts),
            "why": writer_summary.get("why_now") or _default_why(recommendation),
        },
        "counts": {
            "add_now": counts.get("immediate_budgeted_count", 0),
            "pilot_ready": counts.get("pilot_ready_count", 0),
            "close_confirm": counts.get("close_confirm_count", 0),
            "trim_to_fund": counts.get("trim_to_fund_count", 0),
            "reduce_risk": counts.get("reduce_risk_count", 0),
            "take_profit": counts.get("take_profit_count", 0),
            "stop_loss": counts.get("stop_loss_count", 0),
            "exit": counts.get("exit_count", 0),
            "sell_side_total": sum(int(sell_side.get(key) or 0) for key in ("TRIM_TO_FUND", "REDUCE_RISK", "TAKE_PROFIT", "STOP_LOSS", "EXIT")),
        },
        "top_priority": top_priority,
        "next_checkpoints": next_checkpoints,
        "position_guide": position_guide,
        "risks": _risk_lines(recommendation, live_sell_side_delta),
        "candidate_universe": {
            "held": [candidate.instrument.display_name for candidate in candidates if candidate.is_held][:8],
            "watch": [candidate.instrument.display_name for candidate in candidates if not candidate.is_held][:8],
        },
        "footer": "리포트 기준: TradingAgents 계좌 운용 리포트 요약 · 실시간 실행 신호가 아닌 조건 확인용 요약 이미지",
    }


def _candidate_counts(recommendation: PortfolioRecommendation) -> dict[str, int]:
    counts = dict(recommendation.candidate_counts or {})
    actions = recommendation.actions
    counts.setdefault("immediate_budgeted_count", sum(1 for action in actions if action.delta_krw_now > 0))
    counts.setdefault("pilot_ready_count", sum(1 for action in actions if action.action_now == "STARTER_NOW" or action.action_if_triggered == "STARTER_IF_TRIGGERED"))
    counts.setdefault("close_confirm_count", sum(1 for action in actions if str(action.action_if_triggered or "").endswith("_IF_TRIGGERED")))
    counts.setdefault("trim_to_fund_count", sum(1 for action in actions if action.portfolio_relative_action == "TRIM_TO_FUND"))
    counts.setdefault("reduce_risk_count", sum(1 for action in actions if action.portfolio_relative_action == "REDUCE_RISK"))
    counts.setdefault("take_profit_count", sum(1 for action in actions if action.portfolio_relative_action == "TAKE_PROFIT"))
    counts.setdefault("stop_loss_count", sum(1 for action in actions if action.portfolio_relative_action == "STOP_LOSS"))
    counts.setdefault("exit_count", sum(1 for action in actions if action.portfolio_relative_action == "EXIT"))
    return {key: int(value or 0) for key, value in counts.items()}


def _top_priority_actions(recommendation: PortfolioRecommendation) -> list[dict[str, Any]]:
    ranked = sorted(recommendation.actions, key=lambda action: (action.priority, -abs(action.delta_krw_now or action.delta_krw_if_triggered)))
    result: list[dict[str, Any]] = []
    for action in ranked:
        if len(result) >= 4:
            break
        label = present_account_action(action.action_now if action.delta_krw_now else action.action_if_triggered, language="Korean")
        condition = "; ".join(action.trigger_conditions[:2]) if action.trigger_conditions else action.rationale
        result.append(
            {
                "ticker": action.display_name,
                "action": label,
                "condition": _shorten(condition, 70),
                "priority": action.priority,
            }
        )
    return result


def _next_checkpoints(recommendation: PortfolioRecommendation) -> list[dict[str, str]]:
    checkpoints: list[dict[str, str]] = []
    for action in sorted(recommendation.actions, key=lambda item: item.priority):
        if len(checkpoints) >= 3:
            break
        if not action.trigger_conditions:
            continue
        checkpoints.append(
            {
                "ticker": action.display_name,
                "condition": _shorten("; ".join(action.trigger_conditions[:2]), 68),
                "action": present_account_action(action.action_if_triggered, language="Korean"),
            }
        )
    return checkpoints


def _position_guide(recommendation: PortfolioRecommendation) -> dict[str, list[str]]:
    keep: list[str] = []
    trim: list[str] = []
    risk: list[str] = []
    for action in sorted(recommendation.actions, key=lambda item: item.priority):
        relative = str(action.portfolio_relative_action or "").upper()
        if relative in {"HOLD", "ADD", "WATCH"} and len(keep) < 6:
            keep.append(action.display_name)
        elif relative == "TRIM_TO_FUND" and len(trim) < 6:
            trim.append(action.display_name)
        elif relative in {"REDUCE_RISK", "TAKE_PROFIT", "STOP_LOSS", "EXIT"} and len(risk) < 6:
            risk.append(action.display_name)
    return {"hold_or_add": keep, "trim_to_fund": trim, "risk_reduce": risk}


def _risk_lines(
    recommendation: PortfolioRecommendation,
    live_sell_side_delta: list[dict[str, Any]] | None,
) -> list[str]:
    lines = [_shorten(str(item), 72) for item in (recommendation.portfolio_risks or ()) if str(item).strip()]
    for delta in live_sell_side_delta or []:
        if len(lines) >= 4:
            break
        ticker = str(delta.get("ticker") or "").strip()
        delta_type = str(delta.get("delta_type") or "").strip()
        if ticker or delta_type:
            lines.append(_shorten(f"{ticker} {delta_type} 확인 필요".strip(), 72))
    return lines[:4] or ["조건 미충족 상태의 추격 매수는 피하고, 지지선·거래량 확인 우선"]


def _writer_summary(payload: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return {}
    normalized = payload.get("payload") if isinstance(payload.get("payload"), dict) else payload
    return normalized if isinstance(normalized, dict) else {}


def _default_headline(counts: dict[str, int]) -> str:
    if counts.get("immediate_budgeted_count", 0) > 0:
        return "조건을 충족한 후보만 제한적으로 실행"
    if counts.get("reduce_risk_count", 0) or counts.get("stop_loss_count", 0) or counts.get("exit_count", 0):
        return "신규 매수보다 위험 축소 우선"
    return "지금은 확인 우선, 조건 충족 종목만 선별"


def _default_sentence(counts: dict[str, int]) -> str:
    return (
        f"오늘 바로 실행 후보 {counts.get('immediate_budgeted_count', 0)}개, "
        f"조건부 후보 {counts.get('close_confirm_count', 0)}개, "
        f"리스크 축소 후보 {counts.get('reduce_risk_count', 0)}개입니다."
    )


def _default_why(recommendation: PortfolioRecommendation) -> list[str]:
    actions = list(recommendation.actions)
    if not actions:
        return ["분석 가능한 후보가 부족해 관찰이 우선입니다."]
    return [
        "신규 매수와 매도·축소 판단을 분리해 계좌 리스크를 관리합니다.",
        "가격 조건, 종가 확인, 거래량 확인이 맞을 때만 실행 후보로 봅니다.",
    ]


def _infer_market(manifest: dict[str, Any]) -> str:
    tickers = [str(item.get("ticker") or "").upper() for item in manifest.get("tickers") or [] if isinstance(item, dict)]
    if any(ticker.endswith(".KS") or ticker.endswith(".KQ") for ticker in tickers):
        return "KR"
    if tickers:
        return "US"
    return ""


def _status_label(status: str) -> str:
    normalized = status.strip().lower()
    if normalized == "success":
        return "정상 완료"
    if normalized == "partial_failure":
        return "일부 실패"
    if normalized == "failed":
        return "실패"
    return normalized or "unknown"


def _money_or_redacted(value: int | float | None, *, redact: bool) -> str:
    if redact:
        return "비공개"
    try:
        return f"{int(value or 0):,} KRW"
    except (TypeError, ValueError):
        return "-"


def _shorten(value: str, max_chars: int) -> str:
    text = " ".join(str(value or "").split())
    if len(text) <= max_chars:
        return text
    return text[: max(0, max_chars - 1)].rstrip() + "…"
