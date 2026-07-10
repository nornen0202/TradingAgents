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
        assert "AVOID_OR_EXCLUDE" not in text, name
        assert "WAIT_CLOSE" not in text, name


def test_youtube_previous_day_fallback_is_explicitly_non_actionable() -> None:
    text = (ROOT / "Docs" / "prompts_youtube_prism_context_followup_for_chatgpt.md").read_text(
        encoding="utf-8"
    )
    assert "직전 KST 날짜" in text
    assert "실행 판단 상향 근거로 사용하지 않는다" in text
