from __future__ import annotations

from tradingagents.presentation import (
    present_account_action,
    present_market_regime,
    present_review_required,
    present_snapshot_mode,
    sanitize_investor_text,
)

from .account_models import AccountSnapshot, PortfolioCandidate, PortfolioRecommendation


def render_portfolio_report_markdown(
    *,
    snapshot: AccountSnapshot,
    recommendation: PortfolioRecommendation,
    candidates: list[PortfolioCandidate],
) -> str:
    mode_label = present_snapshot_mode(snapshot.snapshot_health, language="Korean")
    market_label = present_market_regime(recommendation.market_regime, language="Korean")
    immediate_count = sum(1 for action in recommendation.actions if action.delta_krw_now != 0)
    conditional_count = sum(1 for action in recommendation.actions if action.delta_krw_if_triggered != 0)
    review_names = [action.display_name for action in recommendation.actions if action.review_required]

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
            f"{action.priority} | {_cell(sanitize_investor_text(action.rationale, language='Korean'))} | "
            f"{present_review_required(action.review_required, language='Korean')} |"
        )

    portfolio_risks = _risk_lines(recommendation.portfolio_risks)
    return "\n".join(
        [
            "# TradingAgents 계좌 운용 리포트",
            "",
            f"- 기준 시각: `{snapshot.as_of}`",
            f"- 운용 모드: `{mode_label}`",
            f"- 계좌 평가금액: `{_krw(snapshot.account_value_krw)}`",
            f"- 오늘 실행 후 예상 현금: `{_krw(recommendation.recommended_cash_after_now_krw)}`",
            f"- 조건부 실행까지 반영한 예상 현금: `{_krw(recommendation.recommended_cash_after_triggered_krw)}`",
            f"- 시장 분위기: `{market_label}`",
            "",
            "## 핵심 요약",
            "",
            f"- 지금 실행 후보: {immediate_count}개",
            f"- 조건부 실행 후보: {conditional_count}개",
            f"- 확인 필요 종목: {', '.join(review_names) if review_names else '없음'}",
            "- 세부 진단과 원본 판단 값은 감사용 JSON 파일에 보관됩니다.",
            "",
            "## 액션 요약",
            "",
            *action_rows,
            "",
            "## 포트폴리오 리스크",
            "",
            portfolio_risks,
            "",
        ]
    )


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


def _amount_label(value: int) -> str:
    amount = int(value)
    if amount == 0:
        return "변동 없음"
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
