from __future__ import annotations

from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from tradingagents.dataflows.youtube_video import YouTubeTranscript, YouTubeVideoBundle, YouTubeVideoMetadata
from tradingagents.scheduled.config import SiteSettings
from tradingagents.scheduled.site import build_site as build_scheduled_site
from tradingagents.youtube.channel import YouTubeVideoReference, dedupe_video_references, filter_references_by_window
from tradingagents.youtube.config import (
    ChannelSettings,
    LLMSettings,
    StorageSettings,
    VerificationSettings,
    YouTubeDailyConfig,
    YouTubeSiteSettings,
    load_youtube_config,
)
from tradingagents.youtube.runner import execute_youtube_run
from tradingagents.youtube.site import build_youtube_site
from tradingagents.youtube.verifier import (
    CONTRADICTED,
    LLM_FAILED,
    STALE,
    UNVERIFIED,
    VERIFIED,
    MarketSnapshot,
    VerifiedVideoReport,
    _extract_json_object,
    _verify_claims,
    verify_youtube_bundle,
)
from tradingagents.youtube_report import build_youtube_video_report


class FakeResponse:
    def __init__(self, content: str):
        self.content = content


class FakeLLM:
    def __init__(self, responses: list[str]):
        self.responses = responses

    def invoke(self, _prompt: str):
        if not self.responses:
            raise RuntimeError("no fake response left")
        return FakeResponse(self.responses.pop(0))


class YouTubeDailyTests(unittest.TestCase):
    def test_channel_window_filter_dedupes_videos_and_shorts(self):
        now = datetime(2026, 5, 28, 22, 0, tzinfo=timezone.utc)
        refs = [
            YouTubeVideoReference("aaaaaaaaaaa", "https://www.youtube.com/watch?v=aaaaaaaaaaa", "A", "videos", now - timedelta(hours=2)),
            YouTubeVideoReference("aaaaaaaaaaa", "https://www.youtube.com/watch?v=aaaaaaaaaaa", "A short", "shorts", now - timedelta(hours=2)),
            YouTubeVideoReference("bbbbbbbbbbb", "https://www.youtube.com/watch?v=bbbbbbbbbbb", "B", "videos", now - timedelta(hours=26)),
            YouTubeVideoReference("ccccccccccc", "https://www.youtube.com/watch?v=ccccccccccc", "C", "shorts", None),
        ]

        deduped = dedupe_video_references(refs)
        selected = filter_references_by_window(deduped, now=now, lookback_hours=24)

        self.assertEqual([item.video_id for item in deduped], ["aaaaaaaaaaa", "bbbbbbbbbbb", "ccccccccccc"])
        self.assertEqual([item.video_id for item in selected], ["aaaaaaaaaaa", "ccccccccccc"])

    def test_llm_json_parser_accepts_fenced_json_and_rejects_invalid_payload(self):
        parsed = _extract_json_object('```json\n{"entities":[{"ticker":"ORCL"}]}\n```')

        self.assertEqual(parsed["entities"][0]["ticker"], "ORCL")
        with self.assertRaises(ValueError):
            _extract_json_object("no json here")

    def test_verification_statuses_include_contradicted_unverified_stale(self):
        fresh = datetime.now(timezone.utc).isoformat()
        stale = (datetime.now(timezone.utc) - timedelta(days=5)).isoformat()

        _, verified_status = _verify_claims(
            ["52주 고점은 200달러 부근"],
            MarketSnapshot("ORCL", fresh, fifty_two_week_high=198.0),
            {"status": VERIFIED},
        )
        _, contradicted_status = _verify_claims(
            ["52주 고점은 100달러"],
            MarketSnapshot("ORCL", fresh, fifty_two_week_high=200.0),
            {"status": VERIFIED},
        )
        _, unverified_status = _verify_claims(
            ["Bloomberg에 따르면 목표가가 올랐다"],
            MarketSnapshot("ORCL", fresh, fifty_two_week_high=200.0),
            {"status": UNVERIFIED},
        )
        _, stale_status = _verify_claims(
            ["52주 고점은 200달러 부근"],
            MarketSnapshot("ORCL", stale, fifty_two_week_high=200.0),
            {"status": VERIFIED},
        )

        self.assertEqual(verified_status, VERIFIED)
        self.assertEqual(contradicted_status, CONTRADICTED)
        self.assertEqual(unverified_status, UNVERIFIED)
        self.assertEqual(stale_status, STALE)

    def test_verify_bundle_uses_codex_json_then_final_markdown(self):
        bundle = _fake_bundle("u2BEOgr8ze8")
        draft = build_youtube_video_report(bundle, generated_at=datetime(2026, 5, 28, 22, 0))
        llm = FakeLLM(
            [
                '```json\n{"overall_thesis":"오라클 확인","entities":[{"ticker":"ORCL","name":"Oracle","claims":["52주 고점은 200달러 부근"],"numeric_claims":["52주 고점 200"],"risks":[],"watch_items":["실적"]}],"verification_items":[]}\n```',
                "# 최종 투자자 리포트\n\n- 영상 주장과 공개 데이터를 분리했습니다.",
            ]
        )

        verified = verify_youtube_bundle(
            bundle,
            draft,
            llm_settings=_llm_settings(),
            verification_settings=_verification_settings(),
            market_data_provider=lambda ticker: MarketSnapshot(ticker, datetime.now(timezone.utc).isoformat(), fifty_two_week_high=198.0),
            external_data_provider=lambda _ticker, _generated_at: {"status": VERIFIED},
            llm_factory=lambda _settings: llm,
            generated_at=datetime(2026, 5, 28, 22, 0, tzinfo=timezone.utc),
        )

        self.assertEqual(verified.status, VERIFIED)
        self.assertIn("최종 투자자 리포트", verified.final_report_markdown)
        self.assertEqual(verified.verification["claims"]["entities"][0]["ticker"], "ORCL")

    def test_verify_bundle_marks_llm_failed_when_codex_json_is_broken(self):
        bundle = _fake_bundle("u2BEOgr8ze8")
        draft = build_youtube_video_report(bundle, generated_at=datetime(2026, 5, 28, 22, 0))

        verified = verify_youtube_bundle(
            bundle,
            draft,
            llm_settings=_llm_settings(),
            verification_settings=_verification_settings(),
            market_data_provider=lambda ticker: MarketSnapshot(ticker, datetime.now(timezone.utc).isoformat(), fifty_two_week_high=198.0),
            external_data_provider=lambda _ticker, _generated_at: {"status": VERIFIED},
            llm_factory=lambda _settings: FakeLLM(["broken json"]),
            generated_at=datetime(2026, 5, 28, 22, 0, tzinfo=timezone.utc),
        )

        self.assertEqual(verified.status, LLM_FAILED)
        self.assertEqual(verified.verification["llm_status"], LLM_FAILED)

    def test_runner_creates_archive_manifest_and_public_site(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive_dir = root / "archive"
            site_dir = root / "site"
            config = _daily_config(archive_dir, site_dir)
            refs = tuple(
                YouTubeVideoReference(
                    f"video00000{i}",
                    f"https://www.youtube.com/watch?v=video00000{i}",
                    f"Video {i}",
                    "fixture",
                    datetime.now(timezone.utc) - timedelta(hours=i),
                )
                for i in range(1, 4)
            )

            manifest = execute_youtube_run(
                config,
                reference_lister=lambda _urls, _limit: refs,
                video_fetcher=lambda url: _fake_bundle(url[-11:]),
                bundle_verifier=lambda bundle, _draft, _generated_at: VerifiedVideoReport(
                    status=VERIFIED,
                    final_report_markdown=f"# Final {bundle.metadata.video_id}\n\n- 공개 요약입니다.",
                    verification={
                        "status": VERIFIED,
                        "llm_status": "success",
                        "generated_at": datetime.now(timezone.utc).isoformat(),
                        "entity_results": [],
                        "source_policy": {"raw_transcript_published": False},
                    },
                ),
            )

            run_manifest = next(archive_dir.glob("runs/*/*/youtube_run.json"))
            site_index = site_dir / "youtube" / "index.html"

            self.assertEqual(manifest["summary"]["total_videos"], 3)
            self.assertTrue(run_manifest.is_file())
            self.assertTrue(site_index.is_file())
            self.assertIn("Video", site_index.read_text(encoding="utf-8"))

    def test_runner_fetches_transcript_only_after_window_filter(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = _daily_config(root / "archive", root / "site")
            recent_id = "recent00001"
            old_id = "oldvideo001"
            refs = (
                YouTubeVideoReference(
                    recent_id,
                    f"https://www.youtube.com/watch?v={recent_id}",
                    "Recent",
                    "fixture",
                    datetime.now(timezone.utc) - timedelta(hours=1),
                ),
                YouTubeVideoReference(
                    old_id,
                    f"https://www.youtube.com/watch?v={old_id}",
                    "Old",
                    "fixture",
                    None,
                ),
            )
            calls: list[tuple[str, bool]] = []

            def fetcher(url: str, *, fetch_transcript: bool = True):
                video_id = url[-11:]
                calls.append((video_id, fetch_transcript))
                published_at = datetime.now(timezone.utc) - (timedelta(hours=1) if video_id == recent_id else timedelta(days=3))
                return _fake_bundle(video_id, published_at=published_at, transcript=fetch_transcript)

            execute_youtube_run(
                config,
                reference_lister=lambda _urls, _limit: refs,
                video_fetcher=fetcher,
                bundle_verifier=lambda bundle, _draft, _generated_at: VerifiedVideoReport(
                    status=VERIFIED,
                    final_report_markdown=f"# Final {bundle.metadata.video_id}\n",
                    verification={
                        "status": VERIFIED,
                        "llm_status": "success",
                        "generated_at": datetime.now(timezone.utc).isoformat(),
                        "entity_results": [],
                        "source_policy": {"raw_transcript_published": False},
                    },
                ),
            )

            self.assertEqual(calls, [(recent_id, False), (recent_id, True), (old_id, False)])

    def test_runner_reuses_previous_successful_video_without_caption_fetch(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive_dir = root / "archive"
            site_dir = root / "site"
            config = _daily_config(archive_dir, site_dir)
            video_id = "reuse000001"
            previous_video_dir = archive_dir / "runs" / "2026" / "youtube_previous" / "videos" / video_id
            previous_video_dir.mkdir(parents=True)
            for filename, text in {
                "metadata.json": "{}",
                "draft_report.md": "# Draft\n",
                "verification.json": json.dumps({"status": VERIFIED}, ensure_ascii=False),
                "final_report.md": "# Reused final\n",
                "public_summary.json": json.dumps({"video_id": video_id, "status": VERIFIED}, ensure_ascii=False),
            }.items():
                (previous_video_dir / filename).write_text(text, encoding="utf-8")
            refs = (
                YouTubeVideoReference(
                    video_id,
                    f"https://www.youtube.com/watch?v={video_id}",
                    "Reusable",
                    "fixture",
                    datetime.now(timezone.utc) - timedelta(hours=1),
                ),
            )
            calls: list[tuple[str, bool]] = []

            def fetcher(url: str, *, fetch_transcript: bool = True):
                calls.append((url[-11:], fetch_transcript))
                return _fake_bundle(url[-11:], transcript=fetch_transcript)

            manifest = execute_youtube_run(
                config,
                reference_lister=lambda _urls, _limit: refs,
                video_fetcher=fetcher,
                bundle_verifier=lambda _bundle, _draft, _generated_at: (_ for _ in ()).throw(RuntimeError("should reuse")),
            )

            self.assertEqual(calls, [(video_id, False)])
            self.assertEqual(manifest["summary"]["reused_videos"], 1)
            self.assertEqual(manifest["videos"][0]["reused_from_run"], "youtube_previous")
            self.assertIn("Reused final", next(archive_dir.glob("runs/*/youtube_*/videos/reuse000001/final_report.md")).read_text(encoding="utf-8"))

    def test_site_builder_preserves_root_site_and_does_not_copy_raw_transcript(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive_dir = root / "archive"
            run_dir = archive_dir / "runs" / "2026" / "youtube_20260528_220000"
            video_dir = run_dir / "videos" / "u2BEOgr8ze8"
            video_dir.mkdir(parents=True)
            (video_dir / "final_report.md").write_text("# Final\n\n짧은 근거만 공개합니다.", encoding="utf-8")
            (video_dir / "public_summary.json").write_text(
                json.dumps({"video_id": "u2BEOgr8ze8", "status": VERIFIED}, ensure_ascii=False),
                encoding="utf-8",
            )
            (video_dir / "raw_transcript.txt").write_text("RAW_TRANSCRIPT_FULL_SHOULD_NOT_PUBLISH", encoding="utf-8")
            (run_dir / "youtube_run.json").write_text(
                json.dumps(
                    {
                        "run_id": "youtube_20260528_220000",
                        "status": "success",
                        "started_at": "2026-05-28T22:00:00+09:00",
                        "summary": {"total_videos": 1, "successful_videos": 1, "failed_videos": 0},
                        "videos": [
                            {
                                "video_id": "u2BEOgr8ze8",
                                "title": "Fixture video",
                                "video_url": "https://www.youtube.com/watch?v=u2BEOgr8ze8",
                                "status": VERIFIED,
                                "final_report_path": "videos/u2BEOgr8ze8/final_report.md",
                                "public_summary_path": "videos/u2BEOgr8ze8/public_summary.json",
                            }
                        ],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            site_dir = root / "site"
            site_dir.mkdir()
            (site_dir / "index.html").write_text("ROOT_SITE", encoding="utf-8")

            build_youtube_site(archive_dir, site_dir, YouTubeSiteSettings("YouTube 리포트", 10, 10))
            public_text = "\n".join(path.read_text(encoding="utf-8") for path in (site_dir / "youtube").rglob("*") if path.is_file())

            self.assertEqual((site_dir / "index.html").read_text(encoding="utf-8"), "ROOT_SITE")
            self.assertNotIn("RAW_TRANSCRIPT_FULL_SHOULD_NOT_PUBLISH", public_text)
            self.assertTrue((site_dir / "youtube" / "feed.json").is_file())

    def test_site_builder_hides_collection_failures_from_report_lists(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive_dir = root / "archive"
            run_dir = archive_dir / "runs" / "2026" / "youtube_20260528_220000"
            ok_dir = run_dir / "videos" / "u2BEOgr8ze8"
            failed_dir = run_dir / "videos" / "failed00001"
            ok_dir.mkdir(parents=True)
            failed_dir.mkdir(parents=True)
            (ok_dir / "final_report.md").write_text("# Final\n\n공개 리포트입니다.", encoding="utf-8")
            (ok_dir / "public_summary.json").write_text(
                json.dumps({"video_id": "u2BEOgr8ze8", "status": VERIFIED}, ensure_ascii=False),
                encoding="utf-8",
            )
            (failed_dir / "public_summary.json").write_text(
                json.dumps({"video_id": "failed00001", "status": "failed"}, ensure_ascii=False),
                encoding="utf-8",
            )
            (run_dir / "youtube_run.json").write_text(
                json.dumps(
                    {
                        "run_id": "youtube_20260528_220000",
                        "status": "partial_failure",
                        "started_at": "2026-05-28T22:00:00+09:00",
                        "summary": {"total_videos": 2, "successful_videos": 1, "failed_videos": 1},
                        "videos": [
                            {
                                "video_id": "u2BEOgr8ze8",
                                "title": "Visible fixture",
                                "video_url": "https://www.youtube.com/watch?v=u2BEOgr8ze8",
                                "status": VERIFIED,
                                "final_report_path": "videos/u2BEOgr8ze8/final_report.md",
                                "public_summary_path": "videos/u2BEOgr8ze8/public_summary.json",
                            },
                            {
                                "video_id": "failed00001",
                                "title": "Hidden collection failure",
                                "video_url": "https://www.youtube.com/watch?v=failed00001",
                                "status": "failed",
                                "public_summary_path": "videos/failed00001/public_summary.json",
                            },
                        ],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            site_dir = root / "site"
            build_youtube_site(archive_dir, site_dir, YouTubeSiteSettings("YouTube 리포트", 10, 10))

            index_html = (site_dir / "youtube" / "index.html").read_text(encoding="utf-8")
            run_html = (site_dir / "youtube" / "runs" / "youtube_20260528_220000" / "index.html").read_text(
                encoding="utf-8"
            )
            feed = json.loads((site_dir / "youtube" / "feed.json").read_text(encoding="utf-8"))
            feed_titles = [item.get("title") for item in feed["items"]]

            self.assertIn("Visible fixture", index_html)
            self.assertNotIn("Hidden collection failure", index_html)
            self.assertIn("Visible fixture", run_html)
            self.assertNotIn("Hidden collection failure", run_html)
            self.assertEqual(feed_titles, ["Visible fixture"])

    def test_github_actions_workflow_schedule_and_pages_artifact(self):
        workflow = Path(".github/workflows/daily-youtube-reports.yml").read_text(encoding="utf-8")

        self.assertIn("0 13 * * *", workflow)
        self.assertIn("actions/upload-pages-artifact", workflow)
        self.assertIn("tradingagents.youtube.runner", workflow)
        self.assertIn("config/scheduled_analysis_korea.toml", workflow)
        self.assertIn("YOUTUBE_COOKIES_FILE", workflow)

    def test_python_module_runner_site_only_entrypoint(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "tradingagents.youtube.runner",
                    "--site-only",
                    "--archive-dir",
                    str(root / "archive"),
                    "--site-dir",
                    str(root / "site"),
                ],
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((root / "site" / "youtube" / "index.html").is_file())

    def test_youtube_archive_defaults_to_shared_archive_in_actions(self):
        with tempfile.TemporaryDirectory() as tmp:
            shared_archive = Path(tmp) / "tradingagents-archive"
            with patch.dict(
                "os.environ",
                {
                    "TRADINGAGENTS_ARCHIVE_DIR": str(shared_archive),
                    "TRADINGAGENTS_YOUTUBE_ARCHIVE_DIR": "",
                },
                clear=False,
            ):
                config = load_youtube_config("config/youtube_daily.toml")

        self.assertEqual(config.storage.archive_dir, shared_archive / "youtube-archive")

    def test_scheduled_site_build_preserves_youtube_addon_and_home_link(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive_dir = root / "archive"
            site_dir = root / "site"
            youtube_run = archive_dir / "youtube-archive" / "runs" / "2026" / "youtube_20260528_220000"
            video_dir = youtube_run / "videos" / "u2BEOgr8ze8"
            video_dir.mkdir(parents=True)
            (video_dir / "final_report.md").write_text("# Final\n\n공개 리포트입니다.", encoding="utf-8")
            (video_dir / "public_summary.json").write_text(
                json.dumps({"video_id": "u2BEOgr8ze8", "status": VERIFIED}, ensure_ascii=False),
                encoding="utf-8",
            )
            (youtube_run / "youtube_run.json").write_text(
                json.dumps(
                    {
                        "run_id": "youtube_20260528_220000",
                        "status": "success",
                        "started_at": "2026-05-28T22:00:00+09:00",
                        "summary": {"total_videos": 1, "successful_videos": 1, "failed_videos": 0},
                        "videos": [
                            {
                                "video_id": "u2BEOgr8ze8",
                                "title": "Fixture video",
                                "video_url": "https://www.youtube.com/watch?v=u2BEOgr8ze8",
                                "status": VERIFIED,
                                "final_report_path": "videos/u2BEOgr8ze8/final_report.md",
                                "public_summary_path": "videos/u2BEOgr8ze8/public_summary.json",
                            }
                        ],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            with patch.dict("os.environ", {"TRADINGAGENTS_YOUTUBE_ARCHIVE_DIR": ""}, clear=False):
                build_scheduled_site(archive_dir, site_dir, SiteSettings(title="TA", subtitle="Daily"))

            home = (site_dir / "index.html").read_text(encoding="utf-8")
            self.assertIn("youtube/index.html", home)
            self.assertTrue((site_dir / "youtube" / "index.html").is_file())
            self.assertIn("Fixture video", (site_dir / "youtube" / "index.html").read_text(encoding="utf-8"))


def _fake_bundle(
    video_id: str,
    *,
    published_at: datetime | None = None,
    transcript: bool = True,
) -> YouTubeVideoBundle:
    video_id = video_id[-11:]
    return YouTubeVideoBundle(
        metadata=YouTubeVideoMetadata(
            video_id=video_id,
            url=f"https://www.youtube.com/watch?v={video_id}",
            title=f"Video {video_id}",
            channel="경제사냥꾼",
            channel_id="UC7usMJDHmtbs_oegmzQKKMA",
            upload_date="20260528",
            published_at=published_at or datetime.now(timezone.utc) - timedelta(hours=1),
            duration_seconds=600,
            view_count=1000,
            like_count=None,
            description="",
            thumbnail_url="",
            tags=(),
            categories=(),
        ),
        transcript=(
            YouTubeTranscript(
                language="ko",
                language_name="Korean",
                source="automatic",
                segments=(),
                raw_text="오라클 티커는 ORCL. 52주 고점은 200달러 부근이라고 말한다.",
                track_ext="json3",
            )
            if transcript
            else None
        ),
        transcript_status="available" if transcript else "skipped",
        available_manual_caption_languages=(),
        available_auto_caption_languages=("ko",),
    )


def _llm_settings() -> LLMSettings:
    return LLMSettings(
        provider="codex",
        deep_model="gpt-5.5",
        codex_binary=None,
        codex_reasoning_effort="medium",
        codex_summary="none",
        codex_personality="none",
        codex_workspace_dir=None,
        codex_request_timeout=30.0,
        codex_max_retries=1,
        codex_cleanup_threads=True,
        codex_preflight_mode="workflow_once",
    )


def _verification_settings() -> VerificationSettings:
    return VerificationSettings(
        mode="external_full",
        publish_unverified=True,
        max_claims_per_video=8,
        strict_llm=True,
    )


def _daily_config(archive_dir: Path, site_dir: Path) -> YouTubeDailyConfig:
    return YouTubeDailyConfig(
        channel=ChannelSettings(
            name="경제사냥꾼",
            urls=("https://www.youtube.com/@fixture/videos", "https://www.youtube.com/@fixture/shorts"),
            lookback_hours=24,
            timezone="Asia/Seoul",
            max_videos=3,
        ),
        llm=_llm_settings(),
        verification=_verification_settings(),
        storage=StorageSettings(archive_dir=archive_dir, site_dir=site_dir),
        site=YouTubeSiteSettings("YouTube 리포트", 10, 10),
    )


if __name__ == "__main__":
    unittest.main()
