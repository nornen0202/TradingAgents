from __future__ import annotations

import datetime as dt
import re
from pathlib import Path
from typing import Any, Mapping

from tradingagents.presentation import present_decision, sanitize_investor_text
from tradingagents.schemas import parse_structured_decision


def save_report_bundle(
    final_state: Mapping[str, Any],
    ticker: str,
    save_path: Path,
    *,
    generated_at: dt.datetime | None = None,
    language: str = "English",
) -> Path:
    """Persist a complete TradingAgents report bundle to disk."""

    generated_at = generated_at or dt.datetime.now()
    save_path = Path(save_path)
    save_path.mkdir(parents=True, exist_ok=True)
    labels = _labels_for(language)
    analysis_date = _coerce_text(final_state.get("analysis_date"))
    trade_date = _coerce_text(final_state.get("trade_date"))

    sections: list[str] = []

    investor_summary = _coerce_text(final_state.get("investor_summary_report"))
    if investor_summary:
        summary_dir = save_path / "0_summary"
        summary_dir.mkdir(exist_ok=True)
        _write_text(summary_dir / "investor_summary.md", investor_summary)
        sections.append(investor_summary)

    analysts_dir = save_path / "1_analysts"
    analyst_parts: list[tuple[str, str]] = []
    for file_name, title, key in (
        ("market.md", labels["market_analyst"], "market_report"),
        ("sentiment.md", labels["social_analyst"], "sentiment_report"),
        ("news.md", labels["news_analyst"], "news_report"),
        ("fundamentals.md", labels["fundamentals_analyst"], "fundamentals_report"),
    ):
        content = _coerce_text(final_state.get(key))
        if not content:
            continue
        analysts_dir.mkdir(exist_ok=True)
        _write_text(analysts_dir / file_name, content)
        analyst_parts.append((title, content))

    if analyst_parts:
        sections.append(
            f"## {labels['section_analysts']}\n\n"
            + "\n\n".join(f"### {title}\n{content}" for title, content in analyst_parts)
        )

    debate = final_state.get("investment_debate_state") or {}
    research_dir = save_path / "2_research"
    research_parts: list[tuple[str, str]] = []
    for file_name, title, key in (
        ("bull.md", labels["bull_researcher"], "bull_history"),
        ("bear.md", labels["bear_researcher"], "bear_history"),
        ("manager.md", labels["research_manager"], "judge_decision"),
    ):
        content = _format_section_content(_coerce_text(debate.get(key)), labels)
        if not content:
            continue
        research_dir.mkdir(exist_ok=True)
        _write_text(research_dir / file_name, content)
        research_parts.append((title, content))

    if research_parts:
        sections.append(
            f"## {labels['section_research']}\n\n"
            + "\n\n".join(f"### {title}\n{content}" for title, content in research_parts)
        )

    trader_plan = _format_section_content(_coerce_text(final_state.get("trader_investment_plan")), labels)
    if trader_plan:
        trading_dir = save_path / "3_trading"
        trading_dir.mkdir(exist_ok=True)
        _write_text(trading_dir / "trader.md", trader_plan)
        sections.append(
            f"## {labels['section_trading']}\n\n### {labels['trader']}\n{trader_plan}"
        )

    risk = final_state.get("risk_debate_state") or {}
    risk_dir = save_path / "4_risk"
    risk_parts: list[tuple[str, str]] = []
    for file_name, title, key in (
        ("aggressive.md", labels["aggressive_analyst"], "aggressive_history"),
        ("conservative.md", labels["conservative_analyst"], "conservative_history"),
        ("neutral.md", labels["neutral_analyst"], "neutral_history"),
    ):
        content = _format_section_content(_coerce_text(risk.get(key)), labels)
        if not content:
            continue
        risk_dir.mkdir(exist_ok=True)
        _write_text(risk_dir / file_name, content)
        risk_parts.append((title, content))

    if risk_parts:
        sections.append(
            f"## {labels['section_risk']}\n\n"
            + "\n\n".join(f"### {title}\n{content}" for title, content in risk_parts)
        )

    portfolio_decision = _format_section_content(_coerce_text(risk.get("judge_decision")), labels)
    if portfolio_decision:
        portfolio_dir = save_path / "5_portfolio"
        portfolio_dir.mkdir(exist_ok=True)
        _write_text(portfolio_dir / "decision.md", portfolio_decision)
        sections.append(
            f"## {labels['section_portfolio']}\n\n"
            f"### {labels['portfolio_manager']}\n{portfolio_decision}"
        )

    metadata_lines = [f"{labels['generated_at']}: {generated_at.strftime('%Y-%m-%d %H:%M:%S')}"]
    if analysis_date:
        metadata_lines.append(f"{labels['analysis_date']}: {analysis_date}")
    if trade_date:
        metadata_lines.append(f"{labels['trade_date']}: {trade_date}")

    header = f"# {labels['report_title']}: {ticker}\n\n" + "\n".join(metadata_lines) + "\n\n"
    complete_report = save_path / "complete_report.md"
    _write_text(complete_report, header + "\n\n".join(sections))
    return complete_report


def _coerce_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return "\n".join(str(item) for item in value)
    return str(value)


def _write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def _format_section_content(content: str, labels: dict[str, str]) -> str:
    sanitized = _strip_raw_json_details(content)
    if not sanitized:
        return ""
    try:
        decision = parse_structured_decision(sanitized)
    except Exception:
        return sanitized

    presentation = present_decision(decision, language=labels["language"])
    lines = [
        f"#### {labels['decision_heading']}",
        f"- {labels['decision_investment_view']}: `{presentation.investment_view}`",
        f"- {labels['decision_action_summary']}: {presentation.action_summary}",
        f"- {labels['decision_market_view']}: {presentation.market_view}",
        f"- {labels['decision_readiness']}: {presentation.setup_summary}",
        f"- {labels['decision_conviction']}: {presentation.conviction_label}",
        f"- {labels['decision_horizon']}: {presentation.horizon_label}",
        f"- {labels['decision_data_status']}: {presentation.data_status}",
        "",
        f"**{labels['decision_entry_logic']}**",
        f"- {sanitize_investor_text(decision.entry_logic, language=labels['language'])}",
        "",
        f"**{labels['decision_exit_logic']}**",
        f"- {sanitize_investor_text(decision.exit_logic, language=labels['language'])}",
        "",
        f"**{labels['decision_position_sizing']}**",
        f"- {sanitize_investor_text(decision.position_sizing, language=labels['language'])}",
        "",
        f"**{labels['decision_risk_limits']}**",
        f"- {sanitize_investor_text(decision.risk_limits, language=labels['language'])}",
        "",
        f"**{labels['decision_catalysts']}**",
    ]
    catalysts = decision.catalysts or (labels["none"],)
    invalidators = decision.invalidators or (labels["none"],)
    lines.extend(f"- {sanitize_investor_text(item, language=labels['language'])}" for item in catalysts)
    lines.extend(["", f"**{labels['decision_invalidators']}**"])
    lines.extend(f"- {sanitize_investor_text(item, language=labels['language'])}" for item in invalidators)
    if decision.watchlist_triggers:
        lines.extend(["", f"**{labels['decision_watchlist_triggers']}**"])
        lines.extend(
            f"- {sanitize_investor_text(item, language=labels['language'])}"
            for item in decision.watchlist_triggers
        )
    return "\n".join(lines)


def _strip_raw_json_details(content: str) -> str:
    if not content:
        return ""
    pattern = re.compile(
        r"<details>\s*<summary>.*?JSON.*?</summary>\s*(.*?)\s*</details>",
        flags=re.IGNORECASE | re.DOTALL,
    )
    match = pattern.search(content)
    if not match:
        return content.strip()

    candidate = match.group(1).strip()
    fenced_match = re.match(r"^```(?:json)?\s*(.*?)\s*```$", candidate, flags=re.IGNORECASE | re.DOTALL)
    if fenced_match:
        candidate = fenced_match.group(1).strip()
    return candidate or content.strip()


def _labels_for(language: str) -> dict[str, str]:
    if str(language).strip().lower() == "korean":
        return {
            "language": "Korean",
            "report_title": "트레이딩 분석 리포트",
            "none": "없음",
            "generated_at": "생성 시각",
            "analysis_date": "분석 기준일",
            "trade_date": "시장 데이터 기준일",
            "section_analysts": "I. 애널리스트 팀 리포트",
            "section_research": "II. 리서치 팀 판단",
            "section_trading": "III. 트레이딩 팀 계획",
            "section_risk": "IV. 리스크 관리 팀 판단",
            "section_portfolio": "V. 포트폴리오 매니저 최종 판단",
            "market_analyst": "시장 애널리스트",
            "social_analyst": "소셜 애널리스트",
            "news_analyst": "뉴스 애널리스트",
            "fundamentals_analyst": "펀더멘털 애널리스트",
            "bull_researcher": "강세 리서처",
            "bear_researcher": "약세 리서처",
            "research_manager": "리서치 매니저",
            "trader": "트레이더",
            "aggressive_analyst": "공격형 리스크 애널리스트",
            "conservative_analyst": "보수형 리스크 애널리스트",
            "neutral_analyst": "중립 리스크 애널리스트",
            "portfolio_manager": "포트폴리오 매니저",
            "decision_heading": "핵심 판단",
            "decision_investment_view": "투자 의견",
            "decision_action_summary": "오늘의 판단",
            "decision_market_view": "방향성",
            "decision_readiness": "실행 준비도",
            "decision_conviction": "판단 강도",
            "decision_horizon": "운용 기간",
            "decision_data_status": "자료 상태",
            "decision_entry_logic": "진입 논리",
            "decision_exit_logic": "청산 논리",
            "decision_position_sizing": "포지션 크기",
            "decision_risk_limits": "리스크 한도",
            "decision_catalysts": "상승 촉매",
            "decision_invalidators": "무효화 조건",
            "decision_watchlist_triggers": "관찰 트리거",
        }

    return {
        "language": "English",
        "report_title": "Trading Analysis Report",
        "none": "None",
        "generated_at": "Generated",
        "analysis_date": "Analysis date",
        "trade_date": "Market data date",
        "section_analysts": "I. Analyst Team Reports",
        "section_research": "II. Research Team Decision",
        "section_trading": "III. Trading Team Plan",
        "section_risk": "IV. Risk Management Team Decision",
        "section_portfolio": "V. Portfolio Manager Decision",
        "market_analyst": "Market Analyst",
        "social_analyst": "Social Analyst",
        "news_analyst": "News Analyst",
        "fundamentals_analyst": "Fundamentals Analyst",
        "bull_researcher": "Bull Researcher",
        "bear_researcher": "Bear Researcher",
        "research_manager": "Research Manager",
        "trader": "Trader",
        "aggressive_analyst": "Aggressive Analyst",
        "conservative_analyst": "Conservative Analyst",
        "neutral_analyst": "Neutral Analyst",
        "portfolio_manager": "Portfolio Manager",
        "decision_heading": "Key Decision",
        "decision_investment_view": "Investment view",
        "decision_action_summary": "Today",
        "decision_market_view": "Market view",
        "decision_readiness": "Execution readiness",
        "decision_conviction": "Conviction",
        "decision_horizon": "Operating horizon",
        "decision_data_status": "Source status",
        "decision_entry_logic": "Entry logic",
        "decision_exit_logic": "Exit logic",
        "decision_position_sizing": "Position sizing",
        "decision_risk_limits": "Risk limits",
        "decision_catalysts": "Catalysts",
        "decision_invalidators": "Invalidators",
        "decision_watchlist_triggers": "Watchlist triggers",
    }
