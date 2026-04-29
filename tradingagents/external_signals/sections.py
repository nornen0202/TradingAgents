from __future__ import annotations

from typing import Any


def render_external_signal_section(reconciliation: dict[str, Any] | None) -> str:
    if not reconciliation:
        return "\n".join(
            [
                "## 외부 신호 비교",
                "",
                "- 외부 데이터 미사용/불가: 이번 run에는 PRISM 비교 신호가 연결되지 않았습니다.",
            ]
        )

    status = str(reconciliation.get("status") or "unavailable").lower()
    ingestion = reconciliation.get("ingestion_status") or {}
    entries = [entry for entry in reconciliation.get("entries") or [] if isinstance(entry, dict)]
    if status != "ok" and not entries:
        warning_text = "; ".join(str(item) for item in (ingestion.get("warnings") or [])[:2]) or "신호 없음"
        return "\n".join(
            [
                "## 외부 신호 비교",
                "",
                "- 외부 데이터 미사용/불가: PRISM dashboard/local data를 읽지 못했습니다.",
                f"- 상태: `{status}` / 사유: {warning_text}",
            ]
        )

    consensus = _filter(entries, agreements={"CONSENSUS"})
    external_buy_wait = _filter(entries, recommendations={"WATCH_FOR_PILOT"})
    conflicts = [
        entry
        for entry in entries
        if str(entry.get("agreement") or "").upper() == "HARD_CONFLICT" or bool(entry.get("execution_blocked"))
    ]
    external_only = _filter(entries, agreements={"EXTERNAL_ONLY"})
    summary = reconciliation.get("summary") or {}
    chunks = [
        "## 외부 신호 비교",
        "",
        "- PRISM 신호는 외부 비교/검증용입니다. TradingAgents의 계좌 리스크 게이트를 우회하지 않습니다.",
        f"- 비교 종목: {int(summary.get('total_entries') or len(entries))}개 / 강한 충돌: {int(summary.get('hard_conflict_count') or 0)}개",
        "",
        "### PRISM과 일치",
        *_entry_lines(consensus, empty="- 없음"),
        "",
        "### PRISM은 매수, TradingAgents는 대기",
        *_entry_lines(external_buy_wait, empty="- 없음"),
        "",
        "### TradingAgents는 축소, PRISM은 매수 - 검토 필요",
        *_entry_lines(conflicts, empty="- 없음"),
    ]
    if external_only:
        chunks.extend(["", "### PRISM 외부 관찰 종목", *_entry_lines(external_only[:5], empty="- 없음")])
    return "\n".join(chunks)


def _filter(
    entries: list[dict[str, Any]],
    *,
    agreements: set[str] | None = None,
    recommendations: set[str] | None = None,
) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for entry in entries:
        agreement = str(entry.get("agreement") or "").upper()
        recommendation = str(entry.get("recommendation") or "").upper()
        if agreements is not None and agreement not in agreements:
            continue
        if recommendations is not None and recommendation not in recommendations:
            continue
        result.append(entry)
    return result


def _entry_lines(entries: list[dict[str, Any]], *, empty: str) -> list[str]:
    if not entries:
        return [empty]
    lines: list[str] = []
    for entry in entries[:6]:
        name = str(entry.get("display_name") or entry.get("ticker") or "-")
        ticker = str(entry.get("ticker") or "-")
        ta_action = str(entry.get("tradingagents_action") or "-")
        prism_action = str(entry.get("prism_action") or "-")
        recommendation = _recommendation_label(str(entry.get("recommendation") or ""))
        blocked = " / 실행 보류" if bool(entry.get("execution_blocked")) else ""
        lines.append(f"- {name} ({ticker}): TradingAgents `{ta_action}` / PRISM `{prism_action}` - {recommendation}{blocked}")
    return lines


def _recommendation_label(value: str) -> str:
    normalized = value.upper()
    mapping = {
        "HIGH_CONVICTION_CONSENSUS_CANDIDATE": "강한 일치 후보",
        "WATCH_FOR_PILOT": "외부 모멘텀 관찰 후보",
        "HUMAN_REVIEW_REQUIRED": "수동 검토 필요",
        "BLOCK_IMMEDIATE_EXECUTION": "즉시 실행 차단",
        "DO_NOT_USE_AS_FUNDING_SOURCE_WITHOUT_REVIEW": "자금 조달원 사용 전 검토",
        "TRADINGAGENTS_ONLY_SIZE_DOWN_OR_CONFIRM": "TradingAgents 단독 아이디어",
        "EXTERNAL_WATCHLIST_ONLY": "외부 관찰 종목",
        "USE_TRADINGAGENTS_RISK_GATES": "TradingAgents 기준 유지",
    }
    return mapping.get(normalized, normalized.replace("_", " ").lower() or "비교 참고")
