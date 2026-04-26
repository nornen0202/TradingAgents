from __future__ import annotations

from typing import Any

from tradingagents.presentation import (
    present_account_action,
    present_market_regime,
    present_review_required,
    present_snapshot_mode,
    sanitize_investor_text,
)
from tradingagents.reporting_consistency import render_consistency_section

from .account_models import AccountSnapshot, PortfolioCandidate, PortfolioRecommendation


_TRIGGER_ACTIONS = {
    "ADD_IF_TRIGGERED",
    "STARTER_IF_TRIGGERED",
    "REDUCE_IF_TRIGGERED",
    "TAKE_PROFIT_IF_TRIGGERED",
    "STOP_LOSS_IF_TRIGGERED",
    "EXIT_IF_TRIGGERED",
}


def render_portfolio_report_markdown(
    *,
    snapshot: AccountSnapshot,
    recommendation: PortfolioRecommendation,
    candidates: list[PortfolioCandidate],
    live_context_delta: dict[str, Any] | None = None,
    live_sell_side_delta: list[dict[str, Any]] | None = None,
) -> str:
    mode_label = present_snapshot_mode(snapshot.snapshot_health, language="Korean")
    market_label = present_market_regime(recommendation.market_regime, language="Korean")
    counts = _candidate_counts(recommendation)
    immediate_count = counts["immediate_candidates_count"]
    immediate_actionable_count = counts["immediate_actionable_count"]
    immediate_budgeted_count = counts["immediate_budgeted_count"]
    budget_blocked_actionable_count = counts["budget_blocked_actionable_count"]
    immediate_budget_blocked_count = counts["immediate_budget_blocked_count"]
    pilot_ready_count = counts["pilot_ready_count"]
    close_confirm_count = counts["close_confirm_count"]
    trim_to_fund_count = counts["trim_to_fund_count"]
    reduce_risk_count = counts["reduce_risk_count"]
    take_profit_count = counts["take_profit_count"]
    stop_loss_count = counts["stop_loss_count"]
    exit_count = counts["exit_count"]
    strategic_trigger_count = counts["strategic_trigger_candidates_count"]
    budgeted_trigger_count = counts["budgeted_trigger_candidates_count"]
    funding_count = counts["funding_candidates_count"]
    held_add_count = counts["held_add_if_triggered_count"]
    watch_if_triggered_count = counts["watch_if_triggered_count"]
    review_required_count = sum(1 for action in recommendation.actions if action.review_required)
    rule_only_fallback_count = sum(
        1 for action in recommendation.actions if str(action.decision_source).upper() == "RULE_ONLY_FALLBACK"
    )
    review_names = [action.display_name for action in recommendation.actions if action.review_required]
    title = (
        "# TradingAgents 포트폴리오 워치리스트 리포트"
        if snapshot.snapshot_health == "WATCHLIST_ONLY"
        else "# TradingAgents 계좌 운용 리포트"
    )

    action_rows = [
        "| 종목 | 현재 상태 | 포트폴리오 액션 | 지금 할 일 | 조건 충족 시 | 금액(지금) | 금액(조건부) | 우선순위 | 핵심 이유 | 확인 필요 |",
        "|---|---|---|---|---|---:|---:|---:|---|---|",
    ]
    for action in recommendation.actions:
        current_value = snapshot.find_position(action.canonical_ticker)
        action_rows.append(
            f"| {_cell(action.display_name)} | {_cell(_position_label(current_value))} | "
            f"{_cell(present_account_action(action.portfolio_relative_action, language='Korean'))} | "
            f"{_cell(present_account_action(action.action_now, language='Korean'))} | "
            f"{_cell(_conditional_action_label(action))} | "
            f"{_cell(_amount_label(action.delta_krw_now))} | "
            f"{_cell(_amount_label(action.delta_krw_if_triggered))} | "
            f"{action.priority} | {_cell(_localized_rationale(action))} | "
            f"{present_review_required(action.review_required, language='Korean')} |"
        )

    portfolio_risks = _risk_lines(recommendation.portfolio_risks)
    strategy_line = _strategy_priority_line(recommendation)
    scenario_summary_lines = _scenario_summary_lines(recommendation)
    funding_sections = _funding_sections(recommendation)
    sell_side_sections = _sell_side_sections(recommendation, live_sell_side_delta=live_sell_side_delta)
    scenario_table = _scenario_table_v2(recommendation)
    consistency_section = render_consistency_section(live_context_delta)
    return "\n".join(
        [
            title,
            "",
            f"- 기준 시각: `{snapshot.as_of}`",
            f"- 운용 모드: `{mode_label}`",
            f"- 계좌 평가금액: `{_krw(snapshot.account_value_krw)}`",
            f"- 가용 현금: `{_krw(snapshot.available_cash_krw)}`",
            f"- 최소 현금 버퍼: `{_krw(snapshot.constraints.min_cash_buffer_krw)}`",
            f"- 오늘 실행 후 예상 현금: `{_krw(recommendation.recommended_cash_after_now_krw)}`",
            f"- 조건부 실행까지 반영한 예상 현금: `{_krw(recommendation.recommended_cash_after_triggered_krw)}`",
            f"- 시장 분위기: `{market_label}`",
            "",
            "## 핵심 요약",
            "",
            f"- 오늘 바로 실행 가능: {immediate_budgeted_count}개",
            f"- 오늘 장중 pilot 가능: {sum(1 for action in recommendation.actions if action.action_now == 'STARTER_NOW' and action.delta_krw_now > 0)}개",
            f"- 종가 확인 후 실행 후보: {budgeted_trigger_count}개",
            f"- 줄여서 살 후보: {len(_top_add_if_funded(recommendation)[:3])}개",
            f"- 먼저 줄일 후보: {len(_top_trim_if_needed(recommendation)[:3])}개",
            f"- 현재 계좌 여력: 가용 현금 {_krw(snapshot.available_cash_krw)} / 버퍼 {_krw(snapshot.constraints.min_cash_buffer_krw)}",
            _strict_summary_line(snapshot, immediate_budgeted_count, budget_blocked_actionable_count),
            strategy_line,
            *scenario_summary_lines,
            f"- 계좌 상대 액션: 줄여서 재배치 {trim_to_fund_count}개 / 위험 축소 {reduce_risk_count}개",
            f"- Sell-side 구분: 자금 조달 {trim_to_fund_count}개 / 리스크 축소 {reduce_risk_count}개 / 이익실현 {take_profit_count}개 / 손절 {stop_loss_count}개 / 청산 {exit_count}개",
            f"- 실행 신호 구분: 예산 차단 {immediate_budget_blocked_count}개 / 장중 pilot 준비 {pilot_ready_count}개 / 종가 확인 {close_confirm_count}개",
            f"- 전략상 조건부 후보 {strategic_trigger_count}개 / 자금 반영 조건부 후보 {budgeted_trigger_count}개",
            f"- 자금 조달형 후보 {funding_count}개 / 보유 조건부 추가 후보 {held_add_count}개 / 미보유 조건부 관찰 후보 {watch_if_triggered_count}개",
            (
                f"- 즉시 실행 신호 {immediate_actionable_count}개 중 "
                f"{budget_blocked_actionable_count}개는 자금/버퍼 제약으로 미집행 상태입니다."
                if budget_blocked_actionable_count > 0
                else f"- 즉시 실행 신호 {immediate_actionable_count}개 중 실제 예산 반영 주문 {immediate_budgeted_count}개입니다."
            ),
            "",
            "## 액션 요약",
            "",
            *action_rows,
            "",
            "## 운용 시나리오",
            "",
            scenario_table,
            "",
            sell_side_sections,
            "",
            funding_sections,
            "",
            consistency_section,
            "",
            "## 포트폴리오 리스크",
            "",
            portfolio_risks,
            "",
            "## 집계 진단",
            "",
            f"- 지금 실행 후보(예산 반영): {immediate_count}개",
            f"- 즉시 실행 신호: {immediate_actionable_count}개",
            f"- 자금 제약으로 막힌 즉시 신호: {budget_blocked_actionable_count}개",
            f"- 예산 차단 실행 후보: {immediate_budget_blocked_count}개",
            f"- 장중 pilot 준비 후보: {pilot_ready_count}개",
            f"- 종가 확인 후보: {close_confirm_count}개",
            f"- 줄여서 재배치 후보: {trim_to_fund_count}개",
            f"- 위험 축소 후보: {reduce_risk_count}개",
            f"- 이익실현 후보: {take_profit_count}개",
            f"- 손절 조건 후보: {stop_loss_count}개",
            f"- 청산 후보: {exit_count}개",
            f"- 조건부 실행 후보: {strategic_trigger_count}개",
            f"- 조건부 실행 예산 반영 후보: {budgeted_trigger_count}개",
            f"- 트리거형 후보(현금과 무관): {strategic_trigger_count}개",
            f"- 전략상 조건부 후보: {strategic_trigger_count}개",
            f"- 자금 조달형 후보: {funding_count}개",
            f"- 확인 필요 후보: {review_required_count}개",
            f"- Rule-only fallback 후보: {rule_only_fallback_count}개",
            f"- 확인 필요 종목: {', '.join(review_names) if review_names else '없음'}",
            "- 내부 진단과 원본 판단 값은 감사용 JSON 파일에 보관합니다.",
            "",
        ]
    )


def _candidate_counts(recommendation: PortfolioRecommendation) -> dict[str, int]:
    counts = dict(recommendation.candidate_counts or {})
    actions = recommendation.actions
    counts.setdefault(
        "strategic_trigger_candidates_count",
        sum(1 for action in actions if action.action_if_triggered in _TRIGGER_ACTIONS),
    )
    counts.setdefault(
        "budgeted_trigger_candidates_count",
        sum(1 for action in actions if action.delta_krw_if_triggered != 0),
    )
    counts.setdefault(
        "immediate_candidates_count",
        sum(1 for action in actions if action.delta_krw_now != 0),
    )
    counts.setdefault(
        "immediate_actionable_count",
        sum(
            1
            for action in actions
            if action.action_now in {"ADD_NOW", "STARTER_NOW", "REDUCE_NOW", "TRIM_NOW", "TAKE_PROFIT_NOW", "STOP_LOSS_NOW", "EXIT_NOW"}
        ),
    )
    counts.setdefault(
        "immediate_budgeted_count",
        sum(
            1
            for action in actions
            if action.action_now in {"ADD_NOW", "STARTER_NOW", "REDUCE_NOW", "TRIM_NOW", "TAKE_PROFIT_NOW", "STOP_LOSS_NOW", "EXIT_NOW"}
            and action.delta_krw_now != 0
        ),
    )
    counts.setdefault(
        "budget_blocked_actionable_count",
        sum(
            1
            for action in actions
            if action.budget_blocked_actionable and action.delta_krw_now == 0
        ),
    )
    counts.setdefault("immediate_budget_blocked_count", counts["budget_blocked_actionable_count"])
    counts.setdefault(
        "pilot_ready_count",
        sum(1 for action in actions if action.action_now == "STARTER_NOW" or action.action_if_triggered == "STARTER_IF_TRIGGERED"),
    )
    counts.setdefault(
        "close_confirm_count",
        sum(1 for action in actions if action.action_if_triggered in _TRIGGER_ACTIONS),
    )
    counts.setdefault(
        "trim_to_fund_count",
        sum(1 for action in actions if action.portfolio_relative_action == "TRIM_TO_FUND"),
    )
    counts.setdefault(
        "reduce_risk_count",
        sum(1 for action in actions if action.portfolio_relative_action == "REDUCE_RISK"),
    )
    counts.setdefault(
        "take_profit_count",
        sum(1 for action in actions if action.portfolio_relative_action == "TAKE_PROFIT"),
    )
    counts.setdefault(
        "stop_loss_count",
        sum(1 for action in actions if action.portfolio_relative_action == "STOP_LOSS"),
    )
    counts.setdefault(
        "exit_count",
        sum(1 for action in actions if action.portfolio_relative_action == "EXIT"),
    )
    counts.setdefault("funding_candidates_count", 0)
    counts.setdefault(
        "held_add_if_triggered_count",
        sum(1 for action in actions if action.action_now == "HOLD" and action.action_if_triggered == "ADD_IF_TRIGGERED"),
    )
    counts.setdefault(
        "watch_if_triggered_count",
        sum(1 for action in actions if action.action_now == "WATCH" and action.action_if_triggered in _TRIGGER_ACTIONS),
    )
    return counts


def _strict_summary_line(
    snapshot: AccountSnapshot,
    immediate_budgeted_count: int,
    budget_blocked_actionable_count: int,
) -> str:
    if immediate_budgeted_count <= 0 and budget_blocked_actionable_count > 0:
        return f"- 즉시 실행 신호는 있으나({budget_blocked_actionable_count}개) 자금/버퍼 제약으로 오늘 주문은 보류합니다."
    if immediate_budgeted_count <= 0 and snapshot.available_cash_krw < snapshot.constraints.min_cash_buffer_krw:
        return "- 오늘은 신규매수 없음: 가용 현금이 최소 현금 버퍼보다 작아 strict 모드에서는 주문을 보류합니다."
    if immediate_budgeted_count <= 0:
        return "- 오늘은 신규매수 없음: 즉시 실행 조건을 통과한 주문이 없습니다."
    return f"- 오늘 즉시 실행 후보 {immediate_budgeted_count}개를 우선 확인합니다."


def _strategy_priority_line(recommendation: PortfolioRecommendation) -> str:
    names = [str(item.get("display_name") or item.get("canonical_ticker")) for item in _top_add_if_funded(recommendation)]
    if names:
        return f"- 하지만 전략상 우선순위는 {' > '.join(names[:4])} 순입니다."
    return "- 전략상 우선순위는 조건 충족 종목이 생길 때 다시 정렬합니다."


def _sell_side_sections(
    recommendation: PortfolioRecommendation,
    *,
    live_sell_side_delta: list[dict[str, Any]] | None = None,
) -> str:
    actions = list(recommendation.actions)
    live_risk_lines = _live_sell_side_lines(live_sell_side_delta)
    sections = [
        ("오늘 살 후보", [action for action in actions if action.action_now in {"ADD_NOW", "STARTER_NOW"}]),
        ("조건부 살 후보", [action for action in actions if action.action_if_triggered in {"ADD_IF_TRIGGERED", "STARTER_IF_TRIGGERED"}]),
        ("줄여서 살 후보", [action for action in actions if action.portfolio_relative_action == "TRIM_TO_FUND"]),
        ("위험 때문에 줄일 후보", [action for action in actions if action.portfolio_relative_action == "REDUCE_RISK"]),
        ("이익실현 후보", [action for action in actions if action.portfolio_relative_action == "TAKE_PROFIT"]),
        ("손절/청산 후보", [action for action in actions if action.portfolio_relative_action in {"STOP_LOSS", "EXIT"}]),
        ("그냥 보유", [action for action in actions if action.action_now == "HOLD" and action.action_if_triggered == "NONE" and action.portfolio_relative_action == "HOLD"]),
        ("관찰만", [action for action in actions if action.action_now == "WATCH"]),
    ]
    chunks: list[str] = ["## 투자자용 액션 구분"]
    for title, items in sections:
        chunks.extend(["", f"### {title}"])
        if title == "위험 때문에 줄일 후보" and live_risk_lines:
            chunks.extend(live_risk_lines)
        if not items:
            if title != "위험 때문에 줄일 후보" or not live_risk_lines:
                chunks.append("- 없음")
            continue
        chunks.extend(_action_brief_line(action) for action in items[:5])
    return "\n".join(chunks)


def _live_sell_side_lines(values: list[dict[str, Any]] | None) -> list[str]:
    lines: list[str] = []
    for item in values or []:
        if not isinstance(item, dict):
            continue
        ticker = str(item.get("ticker") or "").strip()
        action = str(item.get("new_risk_action") or "").strip()
        delta_type = str(item.get("delta_type") or "").strip()
        if ticker and action:
            lines.append(f"- {ticker}: live delta 기준 {present_account_action(action, language='Korean')} ({delta_type})")
    return lines


def _action_brief_line(action) -> str:
    label = present_account_action(action.portfolio_relative_action, language="Korean")
    reason = _localized_rationale(action)
    level = ""
    if action.risk_action_level:
        raw_level = action.risk_action_level
        price = raw_level.get("price") or raw_level.get("low") or raw_level.get("high")
        if price:
            level = f" / 기준 {price}"
    return f"- {action.display_name}: {label}{level} - {reason}"


def _funding_sections(recommendation: PortfolioRecommendation) -> str:
    add_items = _top_add_if_funded(recommendation)
    trim_items = _top_trim_if_needed(recommendation)
    funding_plan = recommendation.funding_plan or {}
    switch_items = funding_plan.get("switch_candidates") or []
    add_lines = [
        f"- {item.get('display_name') or item.get('canonical_ticker')}: {_short_conditions(item.get('trigger_conditions'))}"
        for item in add_items
    ]
    trim_lines = [
        f"- {item.get('display_name') or item.get('canonical_ticker')}: {_funding_reason_label(item)} / 자금조달 점수 {float(item.get('funding_source_score') or 0):.2f}"
        for item in trim_items
    ]
    return "\n".join(
        [
            "## 전략상 가장 강한 후보",
            "",
            "\n".join(add_lines[:3]) if add_lines else "- 전략상 강한 조건부 후보가 없습니다.",
            "",
            "## 리밸런싱 시 먼저 줄일 후보",
            "",
            "\n".join(trim_lines[:3]) if trim_lines else "- 우선 축소 후보가 없습니다.",
            "",
            "## switch-candidates",
            "",
            (
                "\n".join(
                    f"- 매수 {((item.get('buy') or {}).get('display_name') or (item.get('buy') or {}).get('canonical_ticker') or '-')}"
                    f" / 축소 {((item.get('trim') or {}).get('display_name') or (item.get('trim') or {}).get('canonical_ticker') or '-')}"
                    for item in switch_items
                    if isinstance(item, dict)
                )
                if switch_items
                else "- 스위칭 조합 후보가 없습니다."
            ),
            "",
            "## would-buy-if-funded",
            "",
            "\n".join(add_lines) if add_lines else "- 자금이 생겨도 바로 늘릴 조건부 후보가 없습니다.",
            "",
            "## would-trim-first",
            "",
            "\n".join(trim_lines) if trim_lines else "- 자금 조달을 위해 먼저 줄일 후보가 없습니다.",
        ]
    )


def _scenario_summary_lines(recommendation: PortfolioRecommendation) -> list[str]:
    scenarios = recommendation.scenario_plan or {}
    strict = scenarios.get("strict") or {}
    switch = scenarios.get("switch") or {}
    cash_agnostic = scenarios.get("cash_agnostic") or scenarios.get("aggressive") or {}
    ranking_names = [
        str(item.get("display_name") or item.get("canonical_ticker"))
        for item in (cash_agnostic.get("strategy_ranking") or [])
        if isinstance(item, dict)
    ]
    return [
        f"- Strict: immediate {int(strict.get('immediate_order_count') or 0)} / budgeted triggers {int(strict.get('budgeted_trigger_count') or 0)}",
        f"- Switch: trim {len(switch.get('would_trim_first') or [])} -> buy {len(switch.get('would_buy_if_funded') or [])}",
        (
            f"- Cash-agnostic: {' > '.join(ranking_names[:4])}"
            if ranking_names
            else "- Cash-agnostic: no ranked add candidates"
        ),
    ]


def _scenario_table_v2(recommendation: PortfolioRecommendation) -> str:
    scenarios = recommendation.scenario_plan or {}
    strict = scenarios.get("strict") or {}
    switch = scenarios.get("switch") or {}
    cash_agnostic = scenarios.get("cash_agnostic") or scenarios.get("aggressive") or {}
    rows = [
        "| Scenario | Intent | Plan |",
        "|---|---|---|",
        f"| Strict | Respect cash buffer | Immediate {int(strict.get('immediate_order_count') or 0)} / budgeted triggers {int(strict.get('budgeted_trigger_count') or 0)} |",
        (
            f"| Switch | Trim weaker names to fund stronger names | Sell {_krw(int(switch.get('gross_sell_krw') or 0))} / Buy {_krw(int(switch.get('gross_buy_krw') or 0))} |"
            if switch.get("enabled")
            else "| Switch | Trim weaker names to fund stronger names | Hold |"
        ),
        (
            f"| Cash-agnostic | Ignore cash buffer for strategy ranking | Conditional buy {_krw(int(cash_agnostic.get('gross_buy_krw') or 0))} |"
            if cash_agnostic.get("enabled")
            else "| Cash-agnostic | Ignore cash buffer for strategy ranking | Hold |"
        ),
    ]
    return "\n".join(rows)


def _scenario_table(recommendation: PortfolioRecommendation) -> str:
    scenarios = recommendation.scenario_plan or {}
    strict = scenarios.get("strict") or {}
    switch = scenarios.get("switch") or {}
    aggressive = scenarios.get("aggressive") or {}
    rows = [
        "| 시나리오 | 의미 | 주문 계획 |",
        "|---|---|---|",
        f"| Strict | 현금 버퍼 절대 준수 | 즉시 {int(strict.get('immediate_order_count') or 0)}개 / 조건부 예산 {int(strict.get('budgeted_trigger_count') or 0)}개 |",
        f"| Switch | 줄여서 늘리기 허용 | {'매도 ' + _krw(int(switch.get('gross_sell_krw') or 0)) + ' / 매수 ' + _krw(int(switch.get('gross_buy_krw') or 0)) if switch.get('enabled') else '후보 부족'} |",
        f"| Aggressive | 조건 충족 시 버퍼 일부 희생 | {'조건부 매수 ' + _krw(int(aggressive.get('gross_buy_krw') or 0)) if aggressive.get('enabled') else '보류'} |",
    ]
    return "\n".join(rows)


def _top_add_if_funded(recommendation: PortfolioRecommendation) -> list[dict[str, Any]]:
    funding_plan = recommendation.funding_plan or {}
    values = funding_plan.get("top_add_if_funded")
    return [item for item in values if isinstance(item, dict)] if isinstance(values, list) else []


def _top_trim_if_needed(recommendation: PortfolioRecommendation) -> list[dict[str, Any]]:
    funding_plan = recommendation.funding_plan or {}
    values = funding_plan.get("top_trim_if_funding_needed")
    return [item for item in values if isinstance(item, dict)] if isinstance(values, list) else []


def _funding_reason_label(item: dict[str, Any]) -> str:
    codes = [str(value).strip().upper() for value in (item.get("funding_reason_codes") or item.get("relative_action_reason_codes") or [])]
    action = str(item.get("portfolio_relative_action") or item.get("risk_action") or "").strip().upper()
    if action == "STOP_LOSS" or "INVALIDATION_BROKEN" in codes:
        return "손절 조건"
    if action == "TAKE_PROFIT" or "PROFIT_TAKING" in codes:
        return "이익실현성 축소"
    if action == "EXIT":
        return "청산 후보"
    if "SUPPORT_BROKEN" in codes:
        return "지지선 이탈"
    if "FAILED_BREAKOUT" in codes:
        return "실패 돌파"
    if "THESIS_WEAKENING" in codes:
        return "보유 논리 약화"
    if "REGIME_HEADWIND" in codes:
        return "장중 환경 역풍"
    if "CONCENTRATION" in codes:
        return "계좌 집중도 완화"
    if "OPPORTUNITY_COST" in codes:
        return "더 강한 후보로 재배치"
    if "NO_COVERAGE" in codes:
        return "이번 run 분석 공백"
    if "DATA_QUALITY" in codes:
        return "실행 데이터 품질 확인"
    return "재배치 후보"


def _short_conditions(values: Any) -> str:
    if not isinstance(values, list) or not values:
        return "조건 충족 시 검토"
    cleaned = [sanitize_investor_text(value, language="Korean") for value in values]
    cleaned = [value for value in cleaned if value and value != "없음"]
    return "; ".join(cleaned[:2]) if cleaned else "조건 충족 시 검토"


def _position_label(position) -> str:
    if position is None or int(position.market_value_krw) <= 0:
        return "미보유"
    return f"보유 {_krw(position.market_value_krw)}"


def _conditional_action_label(action) -> str:
    label = present_account_action(action.action_if_triggered, conditional=True, language="Korean")
    conditions = [sanitize_investor_text(item, language="Korean") for item in action.trigger_conditions]
    conditions = [item for item in conditions if item and item != "없음"]
    if not conditions:
        return label
    return f"{label}: {'; '.join(conditions[:2])}"


def _localized_rationale(action) -> str:
    text = sanitize_investor_text(action.rationale, language="Korean")
    if text and text != "없음":
        return text
    if action.action_if_triggered in {"ADD_IF_TRIGGERED", "STARTER_IF_TRIGGERED"}:
        return "조건 충족 전까지 대기합니다."
    if action.action_if_triggered in {"REDUCE_IF_TRIGGERED", "TAKE_PROFIT_IF_TRIGGERED", "STOP_LOSS_IF_TRIGGERED", "EXIT_IF_TRIGGERED"}:
        return "리스크 조건 이탈 시 축소를 검토합니다."
    return "추가 행동보다 관찰이 우선입니다."


def _amount_label(value: int) -> str:
    amount = int(value)
    if amount == 0:
        return "변화 없음"
    if amount > 0:
        return f"매수 {_krw(amount)}"
    return f"매도 {_krw(abs(amount))}"


def _risk_lines(values: tuple[str, ...]) -> str:
    cleaned = []
    for value in values:
        text = sanitize_investor_text(value, language="Korean")
        if text and text not in cleaned:
            cleaned.append(text)
    return "\n".join(f"- {item}" for item in cleaned) if cleaned else "- 특이 리스크 없음"


def _krw(value: int) -> str:
    return f"{int(value):,} KRW"


def _cell(value: object) -> str:
    return str(value).replace("|", "/").replace("\n", " ").strip() or "-"
