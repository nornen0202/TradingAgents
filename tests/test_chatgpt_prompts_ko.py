from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMPTS = (
    "prompts_kr_for_chatgpt.md",
    "prompts_us_for_chatgpt.md",
    "prompts_overlay_context_followup_for_chatgpt.md",
    "prompts_youtube_prism_context_followup_for_chatgpt.md",
)


def test_prompts_stay_compact_and_korean_action_first() -> None:
    for name in PROMPTS:
        text = (ROOT / "Docs" / name).read_text(encoding="utf-8")
        assert len(text) < 12_000, name
        assert "한국어" in text, name

    for name in ("prompts_kr_for_chatgpt.md", "prompts_us_for_chatgpt.md"):
        text = (ROOT / "Docs" / name).read_text(encoding="utf-8")
        assert "종목별 투자 전략표" in text, name
        assert "보유 유지" in text, name
        assert "종가 확인 후 판단" in text, name
        assert "웹 검색/심층 조사" in text, name
        assert "account_snapshot.json" in text, name
        assert "portfolio_report.json" in text, name
        assert "account_performance_report.json" in text, name
        assert "프로젝트 원안" in text, name
        assert "최신 웹 검증" in text, name
        assert "`단기`" in text and "`중기`" in text and "`장기`" in text, name
        assert "모든 보유 종목" in text, name
        assert "계좌 식별정보가 제거됐는가" in text, name
        assert "AVOID_OR_EXCLUDE" not in text, name
        assert "WAIT_CLOSE" not in text, name

    kr = (ROOT / "Docs" / "prompts_kr_for_chatgpt.md").read_text(encoding="utf-8")
    assert "DART" in kr
    assert "한국거래소/KIND" in kr
    assert "KOSPI/KOSDAQ" in kr

    us = (ROOT / "Docs" / "prompts_us_for_chatgpt.md").read_text(encoding="utf-8")
    assert "SEC EDGAR" in us
    assert "정규장, pre-market, after-hours" in us
    assert "USD/KRW" in us


def test_youtube_previous_day_fallback_is_explicitly_non_actionable() -> None:
    text = (ROOT / "Docs" / "prompts_youtube_prism_context_followup_for_chatgpt.md").read_text(
        encoding="utf-8"
    )
    assert "직전 KST 날짜" in text
    assert "실행 판단 상향 근거로 사용하지 않는다" in text
