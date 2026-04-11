from __future__ import annotations

from .account_models import AccountSnapshot, PortfolioCandidate, PortfolioRecommendation


def render_portfolio_report_markdown(
    *,
    snapshot: AccountSnapshot,
    recommendation: PortfolioRecommendation,
    candidates: list[PortfolioCandidate],
) -> str:
    action_rows = [
        "| 종목 | 현재 평가금액 | 액션 now | 금액 now | 액션 if triggered | 금액 if triggered | 우선순위 | 판단 경로 | 근거 |",
        "|---|---:|---|---:|---|---:|---:|---|---|",
    ]
    for action in recommendation.actions:
        current_value = snapshot.find_position(action.canonical_ticker)
        action_rows.append(
            f"| {action.display_name} | {int(current_value.market_value_krw if current_value else 0):,} | "
            f"{action.action_now} | {action.delta_krw_now:,} | {action.action_if_triggered} | "
            f"{action.delta_krw_if_triggered:,} | {action.priority} | {action.decision_source} | "
            f"{action.rationale} |"
        )

    judgment_rows = [
        "| 종목 | timing_readiness | trigger_type | review_required | reason_codes | gate_reasons |",
        "|---|---:|---|---|---|---|",
    ]
    for action in recommendation.actions:
        judgment_rows.append(
            f"| {action.display_name} | {action.timing_readiness:.2f} | {action.trigger_type or '-'} | "
            f"{'yes' if action.review_required else 'no'} | "
            f"{', '.join(action.reason_codes) or '-'} | "
            f"{', '.join(action.gate_reasons) or '-'} |"
        )

    health_rows = [
        "| 종목 | company_news | disclosures | social_source | fallback | quality_flags |",
        "|---|---:|---:|---|---:|---|",
    ]
    for candidate in candidates:
        health_rows.append(
            f"| {candidate.instrument.display_name} | "
            f"{int(candidate.data_coverage.get('company_news_count', 0) or 0)} | "
            f"{int(candidate.data_coverage.get('disclosures_count', 0) or 0)} | "
            f"{candidate.data_coverage.get('social_source', 'unavailable')} | "
            f"{int(candidate.vendor_health.get('fallback_count', 0) or 0)} | "
            f"{', '.join(candidate.quality_flags) or '-'} |"
        )

    portfolio_risks = "\n".join(f"- {item}" for item in recommendation.portfolio_risks) or "- 없음"
    return "\n".join(
        [
            "# TradingAgents 계좌 운용 리포트",
            "",
            f"- Snapshot ID: `{snapshot.snapshot_id}`",
            f"- Snapshot health: `{snapshot.snapshot_health}`",
            f"- 기준 시각: `{snapshot.as_of}`",
            f"- 계좌 평가금액: `{snapshot.account_value_krw:,} KRW`",
            f"- 추천 현금(now 이후): `{recommendation.recommended_cash_after_now_krw:,} KRW`",
            f"- 추천 현금(triggered 이후): `{recommendation.recommended_cash_after_triggered_krw:,} KRW`",
            f"- 시장 레짐: `{recommendation.market_regime}`",
            "",
            "## 액션 요약",
            "",
            *action_rows,
            "",
            "## 판단 메타데이터",
            "",
            *judgment_rows,
            "",
            "## Data Health / Source Health",
            "",
            *health_rows,
            "",
            "## 배치 요약",
            "",
            f"- decision_distribution: `{recommendation.data_health_summary.get('decision_distribution')}`",
            f"- stance_distribution: `{recommendation.data_health_summary.get('stance_distribution')}`",
            f"- entry_action_distribution: `{recommendation.data_health_summary.get('entry_action_distribution')}`",
            f"- avg_confidence: `{recommendation.data_health_summary.get('avg_confidence')}`",
            f"- company_news_zero_ratio: `{recommendation.data_health_summary.get('company_news_zero_ratio')}`",
            f"- snapshot_health: `{recommendation.data_health_summary.get('snapshot_health')}`",
            f"- warnings: `{recommendation.data_health_summary.get('warning_flags')}`",
            "",
            "## 포트폴리오 리스크",
            "",
            portfolio_risks,
            "",
        ]
    )
