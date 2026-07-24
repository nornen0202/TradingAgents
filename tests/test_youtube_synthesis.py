from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from tradingagents.youtube.config import (
    LLMSettings,
    SynthesisSettings,
    YouTubeSiteSettings,
)
from tradingagents.youtube.site import build_youtube_site
from tradingagents.youtube.synthesis import (
    _create_synthesis_llm,
    synthesize_youtube_run,
)


class _FakeSynthesisLLM:
    def __init__(self, response: dict):
        self.response = response
        self.prompts: list[str] = []

    def invoke(self, prompt: str) -> SimpleNamespace:
        self.prompts.append(prompt)
        return SimpleNamespace(
            content=json.dumps(self.response, ensure_ascii=False)
        )


def _llm_settings() -> LLMSettings:
    return LLMSettings(
        provider="codex",
        deep_model="gpt-5.6-sol",
        codex_binary=None,
        codex_reasoning_effort="medium",
        codex_summary="none",
        codex_personality="none",
        codex_workspace_dir=None,
        codex_request_timeout=30.0,
        codex_max_retries=1,
        codex_cleanup_threads=True,
        codex_preflight_mode="workflow_once",
        synthesis_model="gpt-5.6-sol",
        codex_synthesis_reasoning_effort="high",
        codex_synthesis_request_timeout=900.0,
    )


def _write_video_artifacts(
    run_dir: Path,
    video_id: str,
    *,
    title: str,
    claim: str,
) -> dict:
    video_dir = run_dir / "videos" / video_id
    video_dir.mkdir(parents=True)
    summary_path = video_dir / "public_summary.json"
    report_path = video_dir / "final_report.md"
    summary_path.write_text(
        json.dumps(
            {
                "video_id": video_id,
                "title": title,
                "channel": "박종훈의 지식한방",
                "transcript_status": "available",
                "claim_status_summary": {"VERIFIED": 1},
                "claims": [
                    {
                        "claim_id": "C1",
                        "claim_text": claim,
                        "status": "VERIFIED",
                        "confidence": 0.8,
                        "investor_implication": "조건을 확인한다.",
                    }
                ],
                "evidence": [
                    {
                        "evidence_id": "E1",
                        "claim_id": "C1",
                        "title": "공식 근거",
                        "url": "https://example.test/official",
                        "source": "official",
                    }
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    report_path.write_text(
        f"# {title}\n\n{claim}\n",
        encoding="utf-8",
    )
    return {
        "video_id": video_id,
        "title": title,
        "channel": "박종훈의 지식한방",
        "status": "VERIFIED",
        "published_at": "2026-07-25T09:00:00+09:00",
        "video_url": f"https://www.youtube.com/watch?v={video_id}",
        "public_summary_path": summary_path.relative_to(run_dir).as_posix(),
        "final_report_path": report_path.relative_to(run_dir).as_posix(),
    }


def test_cross_video_synthesis_uses_sol_high_and_validates_actions(
    tmp_path: Path,
) -> None:
    videos = [
        _write_video_artifacts(
            tmp_path,
            "video000001",
            title="반도체 수요",
            claim="TSM의 수요는 강하지만 가격 확인이 필요하다.",
        ),
        _write_video_artifacts(
            tmp_path,
            "video000002",
            title="금리 경로",
            claim="금리 상승은 성장주 밸류에이션 부담이다.",
        ),
    ]
    fake = _FakeSynthesisLLM(
        {
            "title": "YouTube 종합 투자 인사이트",
            "as_of": "2026-07-25T10:00:00+09:00",
            "executive_summary": "반도체는 조건부 긍정, 금리는 위험 요인이다.",
            "market_regime": {
                "label": "선별 장세",
                "direction": "MIXED",
                "confidence": 0.75,
                "rationale": "영상 간 공통점과 상충점을 비교했다.",
            },
            "consensus_insights": [
                {
                    "theme": "AI 수요",
                    "direction": "POSITIVE",
                    "confidence": 0.8,
                    "summary": "수요는 유지된다.",
                    "supporting_video_ids": [
                        "video000001",
                        "unknown-video",
                    ],
                    "counterpoints": ["금리 부담"],
                }
            ],
            "contradictions": [],
            "ticker_strategies": [
                {
                    "ticker": "TSM",
                    "name": "TSMC",
                    "action": "BUY_ON_CONFIRMATION",
                    "thesis": "수요 확인 후 접근한다.",
                    "entry_conditions": ["전고점 회복과 거래량 확인"],
                    "hold_conditions": ["수요 전망 유지"],
                    "reduce_sell_conditions": ["수요 전망 하향"],
                    "invalidation_conditions": ["핵심 지지선 종가 이탈"],
                    "confidence": 0.76,
                    "video_ids": ["video000001", "unknown-video"],
                },
                {
                    "ticker": "VAGUE",
                    "action": "BUY_ON_CONFIRMATION",
                    "thesis": "구체 조건이 없다.",
                    "entry_conditions": [],
                    "invalidation_conditions": [],
                    "confidence": 0.9,
                    "video_ids": ["video000002"],
                },
            ],
            "portfolio_strategy": {
                "buy_conditions": ["조건 확인 후 분할 접근"],
                "hold_conditions": ["실적 가정 유지"],
                "reduce_sell_conditions": ["가정 훼손"],
                "avoid_conditions": ["추격 매수"],
                "cash_and_sizing": ["시험 비중부터 시작"],
            },
            "checkpoints": ["다음 실적 발표"],
            "risk_notes": ["YouTube 단독으로 주문하지 않는다."],
        }
    )

    result = synthesize_youtube_run(
        run_id="youtube_20260725_100000",
        run_dir=tmp_path,
        videos=videos,
        llm_settings=_llm_settings(),
        synthesis_settings=SynthesisSettings(enabled=True),
        generated_at=datetime(2026, 7, 25, 10, 0, tzinfo=timezone.utc),
        llm_factory=lambda _settings: fake,
    )

    assert result.status == "success"
    assert result.receipt["model"] == "gpt-5.6-sol"
    assert result.receipt["reasoning_effort"] == "high"
    assert result.structured_report["source_video_count"] == 2
    assert (
        result.structured_report["consensus_insights"][0][
            "supporting_video_ids"
        ]
        == ["video000001"]
    )
    assert result.structured_report["ticker_strategies"][0]["action"] == (
        "BUY_ON_CONFIRMATION"
    )
    assert result.structured_report["ticker_strategies"][1]["action"] == "WATCH"
    assert "조건 확인 후 분할매수 검토" in result.report_markdown
    assert "video000001" in fake.prompts[0]
    assert "video000002" in fake.prompts[0]
    assert "untrusted source data" in fake.prompts[0]


def test_synthesis_client_receives_quality_first_model_and_effort() -> None:
    calls: list[tuple[str, str, dict]] = []

    def fake_create_llm_client(*, provider: str, model: str, **kwargs):
        calls.append((provider, model, kwargs))
        return SimpleNamespace(get_llm=lambda: object())

    with patch(
        "tradingagents.youtube.synthesis.create_llm_client",
        side_effect=fake_create_llm_client,
    ):
        assert _create_synthesis_llm(_llm_settings()) is not None

    assert calls == [
        (
            "codex",
            "gpt-5.6-sol",
            {
                "codex_binary": None,
                "codex_reasoning_effort": "high",
                "codex_summary": "none",
                "codex_personality": "none",
                "codex_workspace_dir": None,
                "codex_request_timeout": 900.0,
                "codex_max_retries": 1,
                "codex_cleanup_threads": True,
                "codex_preflight_mode": "workflow_once",
                "model_role": "youtube_synthesis",
            },
        )
    ]


def test_synthesis_client_uses_isolated_workspace() -> None:
    calls: list[dict] = []

    def fake_create_llm_client(*, provider: str, model: str, **kwargs):
        calls.append(kwargs)
        return SimpleNamespace(get_llm=lambda: object())

    settings = replace(
        _llm_settings(),
        codex_workspace_dir="C:/runner/work/youtube",
    )
    with patch(
        "tradingagents.youtube.synthesis.create_llm_client",
        side_effect=fake_create_llm_client,
    ):
        assert _create_synthesis_llm(settings) is not None

    assert calls[0]["codex_workspace_dir"].replace("\\", "/").endswith(
        "/youtube/youtube-synthesis"
    )


def test_site_publishes_synthesis_first_for_pc_and_mobile(tmp_path: Path) -> None:
    archive_dir = tmp_path / "archive"
    site_dir = tmp_path / "site"
    run_dir = (
        archive_dir
        / "runs"
        / "2026"
        / "youtube_20260725_100000"
    )
    synthesis_dir = run_dir / "synthesis"
    synthesis_dir.mkdir(parents=True)
    markdown = (
        "# YouTube 종합 투자 인사이트\n\n"
        "## 한눈에 보는 결론\n\n"
        "조건을 확인한 뒤 분할 접근합니다.\n"
    )
    structured = {
        "version": 1,
        "title": "YouTube 종합 투자 인사이트",
        "as_of": "2026-07-25T10:00:00+09:00",
        "status": "success",
        "executive_summary": "조건을 확인한 뒤 분할 접근합니다.",
        "source_video_count": 2,
        "source_video_ids": ["video000001", "video000002"],
    }
    (synthesis_dir / "report.md").write_text(markdown, encoding="utf-8")
    (synthesis_dir / "report.json").write_text(
        json.dumps(structured, ensure_ascii=False),
        encoding="utf-8",
    )
    (run_dir / "youtube_run.json").write_text(
        json.dumps(
            {
                "version": 2,
                "run_id": "youtube_20260725_100000",
                "status": "success",
                "started_at": "2026-07-25T10:00:00+09:00",
                "summary": {
                    "total_videos": 2,
                    "successful_videos": 2,
                    "failed_videos": 0,
                },
                "videos": [],
                "synthesis": {
                    "status": "success",
                    "report_path": "synthesis/report.md",
                    "structured_report_path": "synthesis/report.json",
                    "model_receipt": {
                        "model": "gpt-5.6-sol",
                        "reasoning_effort": "high",
                    },
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    build_youtube_site(
        archive_dir,
        site_dir,
        YouTubeSiteSettings("YouTube 리포트", 10, 10),
    )

    index_html = (site_dir / "youtube" / "index.html").read_text(
        encoding="utf-8"
    )
    pc_html = (site_dir / "youtube" / "insights.html").read_text(
        encoding="utf-8"
    )
    mobile_html = (
        site_dir / "mobile" / "youtube-insights.html"
    ).read_text(encoding="utf-8")

    assert index_html.index("CODEX CROSS-VIDEO SYNTHESIS") < index_html.index(
        "최근 리포트"
    )
    assert "PC 종합 리포트" in index_html
    assert "모바일 종합 리포트" in index_html
    assert "gpt-5.6-sol · reasoning high" in pc_html
    assert "조건을 확인한 뒤 분할 접근합니다." in pc_html
    assert pc_html.count("<h1>") == 1
    assert "<h2>YouTube 종합 투자 인사이트</h2>" not in pc_html
    assert "PC 버전" in mobile_html
    assert (site_dir / "youtube" / "insights.json").is_file()


def test_synthesis_includes_all_daily_eligible_videos_within_budget(
    tmp_path: Path,
) -> None:
    videos = [
        _write_video_artifacts(
            tmp_path,
            f"video{i:06d}",
            title=f"영상 {i}",
            claim=f"검증 주장 {i}",
        )
        for i in range(30)
    ]
    fake = _FakeSynthesisLLM(
        {
            "executive_summary": "30개 영상을 모두 검토했다.",
            "market_regime": {},
            "consensus_insights": [],
            "contradictions": [],
            "ticker_strategies": [],
            "portfolio_strategy": {},
            "checkpoints": [],
            "risk_notes": [],
        }
    )

    result = synthesize_youtube_run(
        run_id="youtube_all_daily",
        run_dir=tmp_path,
        videos=videos,
        llm_settings=_llm_settings(),
        synthesis_settings=SynthesisSettings(
            enabled=True,
            max_videos=100,
            max_input_chars=360000,
        ),
        llm_factory=lambda _settings: fake,
    )

    assert result.status == "success"
    assert result.structured_report["source_video_count"] == 30
    assert result.receipt["source_video_count"] == 30
    assert "video000029" in fake.prompts[0]


def test_synthesis_excludes_failed_manifest_and_summary_artifacts(
    tmp_path: Path,
) -> None:
    successful = _write_video_artifacts(
        tmp_path,
        "video_good01",
        title="정상 분석",
        claim="정상 분석만 종합 입력에 포함한다.",
    )
    failed_manifest = _write_video_artifacts(
        tmp_path,
        "video_fail01",
        title="매니페스트 실패",
        claim="이 내용은 포함되면 안 된다.",
    )
    failed_manifest["status"] = "llm_failed"
    failed_summary = _write_video_artifacts(
        tmp_path,
        "video_fail02",
        title="요약 실패",
        claim="이 내용도 포함되면 안 된다.",
    )
    failed_summary_path = tmp_path / failed_summary["public_summary_path"]
    failed_summary_payload = json.loads(failed_summary_path.read_text(encoding="utf-8"))
    failed_summary_payload["status"] = "unverified"
    failed_summary_payload["llm_status"] = "llm_failed"
    failed_summary_path.write_text(
        json.dumps(failed_summary_payload, ensure_ascii=False),
        encoding="utf-8",
    )
    fake = _FakeSynthesisLLM(
        {
            "executive_summary": "정상 영상만 검토했다.",
            "market_regime": {},
            "consensus_insights": [],
            "contradictions": [],
            "ticker_strategies": [],
            "portfolio_strategy": {},
            "checkpoints": [],
            "risk_notes": [],
        }
    )

    result = synthesize_youtube_run(
        run_id="youtube_excludes_failed",
        run_dir=tmp_path,
        videos=[successful, failed_manifest, failed_summary],
        llm_settings=_llm_settings(),
        synthesis_settings=SynthesisSettings(enabled=True),
        llm_factory=lambda _settings: fake,
    )

    assert result.status == "success"
    assert result.structured_report["source_video_count"] == 1
    assert "video_good01" in fake.prompts[0]
    assert "video_fail01" not in fake.prompts[0]
    assert "video_fail02" not in fake.prompts[0]
