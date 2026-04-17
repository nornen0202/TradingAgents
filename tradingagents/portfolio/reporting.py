from __future__ import annotations

from typing import Any

from tradingagents.presentation import (
    present_account_action,
    present_market_regime,
    present_review_required,
    present_snapshot_mode,
    sanitize_investor_text,
)

from .account_models import AccountSnapshot, PortfolioCandidate, PortfolioRecommendation


_TRIGGER_ACTIONS = {"ADD_IF_TRIGGERED", "STARTER_IF_TRIGGERED", "REDUCE_IF_TRIGGERED", "EXIT_IF_TRIGGERED"}


def render_portfolio_report_markdown(
    *,
    snapshot: AccountSnapshot,
    recommendation: PortfolioRecommendation,
    candidates: list[PortfolioCandidate],
) -> str:
    mode_label = present_snapshot_mode(snapshot.snapshot_health, language="Korean")
    market_label = present_market_regime(recommendation.market_regime, language="Korean")
    counts = _candidate_counts(recommendation)
    immediate_count = counts["immediate_candidates_count"]
    immediate_actionable_count = counts["immediate_actionable_count"]
    immediate_budgeted_count = counts["immediate_budgeted_count"]
    budget_blocked_actionable_count = counts["budget_blocked_actionable_count"]
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
        "| 종목 | 현재 상태 | 지금 할 일 | 조건 충족 시 | 금액(지금) | 금액(조건부) | 우선순위 | 핵심 이유 | 확인 필요 |",
        "|---|---|---|---|---:|---:|---:|---|---|",
    ]
    for action in recommendation.actions:
        current_value = snapshot.find_position(action.canonical_ticker)
        action_rows.append(
            f"| {_cell(action.display_name)} | {_cell(_position_label(current_value))} | "
            f"{_cell(present_account_action(action.action_now, language='Korean'))} | "
            f"{_cell(_conditional_action_label(action))} | "
            f"{_cell(_amount_label(action.delta_krw_now))} | "
            f"{_cell(_amount_label(action.delta_krw_if_triggered))} | "
            f"{action.priority} | {_cell(_localized_rationale(action))} | "
            f"{present_review_required(action.review_required, language='Korean')} |"
        )

    portfolio_risks = _risk_lines(recommendation.portfolio_risks)
    strategy_line = _strategy_priority_line(recommendation)
    funding_sections = _funding_sections(recommendation)
    scenario_table = _scenario_table(recommendation)
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
            _strict_summary_line(snapshot, immediate_budgeted_count, budget_blocked_actionable_count),
            strategy_line,
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
            funding_sections,
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
        sum(1 for action in actions if action.action_now in {"ADD_NOW", "STARTER_NOW", "REDUCE_NOW", "TRIM_NOW", "EXIT_NOW"}),
    )
    counts.setdefault(
        "immediate_budgeted_count",
        sum(
            1
            for action in actions
            if action.action_now in {"ADD_NOW", "STARTER_NOW", "REDUCE_NOW", "TRIM_NOW", "EXIT_NOW"} and action.delta_krw_now != 0
        ),
    )
    counts.setdefault(
        "budget_blocked_actionable_count",
        sum(1 for action in actions if action.action_now in {"ADD_NOW", "STARTER_NOW"} and action.delta_krw_now == 0),
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
        f"- {item.get('display_name') or item.get('canonical_ticker')}: 자금조달 점수 {float(item.get('funding_source_score') or 0):.2f}"
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
    if action.action_if_triggered in {"REDUCE_IF_TRIGGERED", "EXIT_IF_TRIGGERED"}:
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
