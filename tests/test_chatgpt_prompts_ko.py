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
        assert "보유 유지" in text, name
        assert "종가 확인 후 판단" in text, name
        assert "웹 검색/심층 조사" in text, name
        assert "https://nornen0202.github.io/TradingAgents/index.html" in text, name
        assert "https://nornen0202.github.io/TradingAgents/llms.txt" in text, name
        assert "mobile/strategy.json" in text, name
        assert "mobile/public.json" in text, name
        assert "account/public.json" in text, name
        assert "파일을 직접 첨부하지 않고" in text, name
        assert "404" in text, name
        assert "프로젝트 원안" in text, name
        assert "최신 웹 검증" in text, name
        assert "`단기`" in text and "`중기`" in text and "`장기`" in text, name
        assert "모든 보유 종목" in text, name
        assert "모바일용 핵심 전략표" in text, name
        assert "종목별 상세 전략표" in text, name
        assert "| 종목 | 현재 행동 | 단기 조건 | 중장기 판단 | 위험/재확인 |" in text, name
        assert "추가 현금 투입 시나리오" in text, name
        assert "다른 계좌" in text, name
        assert "최소 4개" in text, name
        assert "최소 6개월" in text, name
        assert "현재 충족 여부·판정시각" in text, name
        assert "취소·재평가 조건" in text, name
        assert "같은 문구를 조건 없이 단독으로 쓰지 마라" in text, name
        assert "미완성 답변" in text, name
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
    assert "최소 4개 시나리오를 USD와 KRW로" in us


def test_youtube_previous_day_fallback_is_explicitly_non_actionable() -> None:
    text = (ROOT / "Docs" / "prompts_youtube_prism_context_followup_for_chatgpt.md").read_text(
        encoding="utf-8"
    )
    assert "직전 KST 날짜" in text
    assert "실행 판단 상향 근거로 사용하지 않는다" in text
