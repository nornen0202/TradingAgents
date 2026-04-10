from __future__ import annotations

import datetime as dt
import json
from pathlib import Path
from typing import Any, Mapping

from tradingagents.schemas import StructuredDecisionValidationError, parse_structured_decision


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

    analysts_dir = save_path / "1_analysts"
    analyst_parts: list[tuple[str, str]] = []
    for file_name, title, key in (
        ("market.md", labels["market_analyst"], "market_report"),
        ("sentiment.md", labels["social_analyst"], "sentiment_report"),
        ("news.md", labels["news_analyst"], "news_report"),
        ("fundamentals.md", labels["fundamentals_analyst"], "fundamentals_report"),
    ):
        content = _format_report_content(_coerce_text(final_state.get(key)), language=language)
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
        content = _format_report_content(_coerce_text(debate.get(key)), language=language)
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

    trader_plan = _format_report_content(
        _coerce_text(final_state.get("trader_investment_plan")),
        language=language,
    )
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
        content = _format_report_content(_coerce_text(risk.get(key)), language=language)
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

    portfolio_decision = _format_report_content(_coerce_text(risk.get("judge_decision")), language=language)
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


def _format_report_content(content: str, *, language: str) -> str:
    if not content:
        return content
    try:
        decision = parse_structured_decision(content)
    except StructuredDecisionValidationError:
        return content

    is_korean = str(language).strip().lower() == "korean"
    rating_map = {
        "BUY": "매수",
        "OVERWEIGHT": "비중 확대",
        "HOLD": "보유",
        "UNDERWEIGHT": "비중 축소",
        "SELL": "매도",
        "NO_TRADE": "관망",
    }
    stance_map = {"BULLISH": "상승", "NEUTRAL": "중립", "BEARISH": "하락"}
    action_map = {"NONE": "없음", "WAIT": "대기", "STARTER": "시작 진입", "ADD": "추가 매수", "EXIT": "청산"}
    setup_map = {"WEAK": "약함", "DEVELOPING": "진행 중", "COMPELLING": "매우 유효"}

    def localize_enum(value: str, mapping: dict[str, str]) -> str:
        if not is_korean:
            return value
        return f"{mapping.get(value, value)} ({value})"

    lines = [
        "### 🧭 핵심 판단" if is_korean else "### 🧭 Key Decision",
        (
            f"- **{localize_enum(decision.rating.value, rating_map)}** · "
            f"**{localize_enum(decision.portfolio_stance.value, stance_map)}** · "
            f"**{localize_enum(decision.entry_action.value, action_map)}**"
        ),
        (
            f"- **설정 품질:** {localize_enum(decision.setup_quality.value, setup_map)}  "
            f"| **신뢰도:** `{decision.confidence:.2f}`  "
            f"| **시간축:** `{decision.time_horizon.value}`"
            if is_korean
            else f"- **Setup quality:** {decision.setup_quality.value}  "
            f"| **Confidence:** `{decision.confidence:.2f}`  "
            f"| **Horizon:** `{decision.time_horizon.value}`"
        ),
        "",
        f"**{'진입 로직' if is_korean else 'Entry logic'}**",
        f"- {decision.entry_logic}",
        "",
        f"**{'청산 로직' if is_korean else 'Exit logic'}**",
        f"- {decision.exit_logic}",
        "",
        f"**{'포지션 사이징' if is_korean else 'Position sizing'}**",
        f"- {decision.position_sizing}",
        "",
        f"**{'리스크 한도' if is_korean else 'Risk limits'}**",
        f"- {decision.risk_limits}",
        "",
        f"**{'핵심 촉매' if is_korean else 'Catalysts'}**",
    ]
    lines.extend(f"- {item}" for item in decision.catalysts)
    lines.extend(["", f"**{'무효화 조건' if is_korean else 'Invalidators'}**"])
    lines.extend(f"- {item}" for item in decision.invalidators)
    if decision.watchlist_triggers:
        lines.extend(["", f"**{'관찰 트리거' if is_korean else 'Watchlist triggers'}**"])
        lines.extend(f"- {item}" for item in decision.watchlist_triggers)

    lines.extend(
        [
            "",
            "<details>",
            f"<summary>{'원본 구조화 JSON 보기' if is_korean else 'Show raw structured JSON'}</summary>",
            "",
            "```json",
            json.dumps(decision.to_dict(), ensure_ascii=False, indent=2),
            "```",
            "</details>",
        ]
    )
    return "\n".join(lines)


def _labels_for(language: str) -> dict[str, str]:
    if str(language).strip().lower() == "korean":
        return {
            "report_title": "트레이딩 분석 리포트",
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
        }

    return {
        "report_title": "Trading Analysis Report",
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
    }
