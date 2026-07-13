from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

from tradingagents.dataflows.youtube_video import (
    YouTubeTranscript,
    YouTubeTranscriptSegment,
    YouTubeVideoBundle,
    YouTubeVideoMetadata,
)
from tradingagents.scheduled.config import SiteSettings
from tradingagents.scheduled.site import build_site as build_scheduled_site
from tradingagents.youtube.channel import YouTubeVideoReference, dedupe_video_references, filter_references_by_window
from tradingagents.youtube.config import (
    ChannelSettings,
    DEFAULT_CHANNEL_URLS,
    LLMSettings,
    StorageSettings,
    VerificationSettings,
    YouTubeDailyConfig,
    YouTubeSiteSettings,
    load_youtube_config,
)
from tradingagents.youtube.research import collect_research_evidence, fallback_research_plan
from tradingagents.youtube.runner import (
    _archived_verification_is_current,
    execute_youtube_run,
)
from tradingagents.youtube.site import build_youtube_site
from tradingagents.youtube.verifier import (
    CONTRADICTED,
    LLM_FAILED,
    STALE,
    UNVERIFIED,
    VERIFIED,
    MarketSnapshot,
    VerifiedVideoReport,
    _adaptive_transcript_chars_for_llm,
    _extract_json_object,
    _transcript_chunks_for_llm,
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
        self.prompts: list[str] = []

    def invoke(self, _prompt: str):
        self.prompts.append(_prompt)
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

    def test_research_evidence_collector_uses_planned_queries_and_excerpts_only(self):
        generated_at = datetime(2026, 5, 29, 13, 0, tzinfo=timezone.utc)
        plan = {
            "claims": [
                {
                    "claim_id": "C1",
                    "claim_text": "코스피가 정책 리스크로 하락했다",
                    "queries": [{"query": "코스피 정책 리스크 하락"}],
                }
            ]
        }

        evidence = collect_research_evidence(
            plan,
            generated_at=generated_at,
            max_queries=4,
            max_evidence_items=4,
            max_evidence_per_claim=2,
            fetch_web_pages=True,
            max_web_pages=1,
            search_provider=lambda query, _limit, _generated_at: [
                {
                    "title": "코스피 정책 뉴스",
                    "source_url": "https://news.example/article",
                    "publisher": "Example News",
                    "excerpt": f"{query} 관련 기사 요약",
                    "source_tier": "news",
                }
            ],
            url_fetcher=lambda _url, _limit: {
                "publisher": "Example News",
                "excerpt": "추가 본문 근거. RAW_TRANSCRIPT_FULL_SHOULD_NOT_APPEAR",
                "source_tier": "news",
            },
        )

        self.assertEqual(evidence["status"], VERIFIED)
        self.assertEqual(evidence["items"][0]["claim_id"], "C1")
        self.assertIn("코스피 정책 뉴스", evidence["items"][0]["title"])
        self.assertFalse(evidence["source_policy"]["raw_transcript_included"])

    def test_research_evidence_collector_skips_low_relevance_results(self):
        generated_at = datetime(2026, 5, 29, 13, 0, tzinfo=timezone.utc)
        plan = {
            "claims": [
                {
                    "claim_id": "C1",
                    "entity": "IFR",
                    "claim_text": "IFR에 따르면 한국 공장의 로봇 밀도가 세계 최상위권이다",
                    "queries": [{"query": "IFR robot density Korea factories"}],
                }
            ]
        }

        evidence = collect_research_evidence(
            plan,
            generated_at=generated_at,
            max_queries=2,
            max_evidence_items=4,
            max_evidence_per_claim=3,
            fetch_web_pages=False,
            max_web_pages=0,
            search_provider=lambda _query, _limit, _generated_at: [
                {
                    "title": "Ford and Constellium expand aluminum recycling deal",
                    "source_url": "https://finance.yahoo.com/news/ford-constellium-aluminum",
                    "publisher": "Yahoo Finance",
                    "excerpt": "Automotive aluminum supply agreement update.",
                    "source_tier": "news",
                },
                {
                    "title": "IFR report shows Korea has high robot density in factories",
                    "source_url": "https://ifr.org/news/korea-robot-density",
                    "publisher": "International Federation of Robotics",
                    "excerpt": "The IFR robot density report compares industrial robot installations by country.",
                    "source_tier": "official",
                },
            ],
        )

        self.assertEqual(evidence["evidence_count"], 1)
        self.assertIn("IFR report", evidence["items"][0]["title"])
        self.assertIn("score:", evidence["items"][0]["relevance"])
        self.assertTrue(any("low_relevance_skipped:C1" in item for item in evidence["errors"]))

    def test_fallback_research_plan_builds_claim_queries(self):
        plan = fallback_research_plan(
            {
                "entities": [
                    {
                        "ticker": "005930.KS",
                        "name": "삼성전자",
                        "claims": ["반도체 정책 수혜를 받을 수 있다"],
                        "numeric_claims": ["52주 고점 90000원"],
                    }
                ]
            },
            video_title="삼성전자 영상",
            max_queries=2,
        )

        self.assertEqual(plan["status"], "fallback")
        self.assertEqual(len(plan["claims"]), 2)
        self.assertIn("삼성전자", plan["claims"][0]["queries"][0]["query"])

    def test_transcript_chunks_sample_late_claim_dense_sections(self):
        segments = []
        for index in range(20):
            if index == 18:
                text = "후반 핵심 주장. NVDA 엔비디아 실적과 매출 35% 성장, 목표가 1200달러, 리스크는 밸류에이션."
            else:
                text = f"일반 시장 설명 {index}. 특별한 종목 언급은 거의 없습니다."
            segments.append(
                YouTubeTranscript(
                    language="ko",
                    language_name="Korean",
                    source="automatic",
                    segments=(),
                    raw_text=text,
                )
            )
        bundle = _fake_bundle("chunk00001")
        transcript_segments = tuple(
            type("Segment", (), {"start_seconds": float(index * 60), "duration_seconds": 30.0, "text": item.raw_text})()
            for index, item in enumerate(segments)
        )
        bundle = replace(
            bundle,
            transcript=YouTubeTranscript(
                language="ko",
                language_name="Korean",
                source="automatic",
                segments=transcript_segments,
                raw_text=" ".join(item.raw_text for item in segments),
                track_ext="json3",
            ),
        )

        with patch.dict(
            "os.environ",
            {
                "TRADINGAGENTS_YOUTUBE_TRANSCRIPT_CHUNK_CHARS": "180",
                "TRADINGAGENTS_YOUTUBE_TRANSCRIPT_MAX_CHUNKS": "5",
                "TRADINGAGENTS_YOUTUBE_TRANSCRIPT_MIN_COVERAGE_CHUNKS": "3",
            },
            clear=False,
        ):
            chunks = _transcript_chunks_for_llm(bundle, max_chars=700)

        joined = "\n".join(chunk["text"] for chunk in chunks)
        self.assertIn("NVDA", joined)
        self.assertTrue(any(chunk["start_seconds"] >= 900 for chunk in chunks))

    def test_adaptive_transcript_budget_extends_long_automatic_captions(self):
        long_text = (
            "엔비디아 매출 35% 성장과 IFR 로봇 밀도, 한국 공장 자동화 수치를 검증해야 한다. "
        ) * 900
        transcript = YouTubeTranscript(
            language="ko",
            language_name="Korean",
            source="automatic",
            segments=(
                YouTubeTranscriptSegment(
                    start_seconds=0.0,
                    duration_seconds=60.0,
                    text=long_text[:2500],
                ),
            ),
            raw_text=long_text,
            track_ext="json3",
        )
        bundle = _fake_bundle("abcdefghijk")
        bundle = replace(
            bundle,
            metadata=replace(bundle.metadata, duration_seconds=2400),
            transcript=transcript,
        )
        settings = _verification_settings()

        adaptive_budget = _adaptive_transcript_chars_for_llm(bundle, verification_settings=settings)
        self.assertGreater(adaptive_budget, settings.max_transcript_chars_for_llm)
        self.assertLessEqual(adaptive_budget, settings.extended_transcript_chars_for_llm)

        disabled = replace(settings, adaptive_transcript_budget_enabled=False)
        self.assertEqual(
            _adaptive_transcript_chars_for_llm(bundle, verification_settings=disabled),
            settings.max_transcript_chars_for_llm,
        )

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
                json.dumps(
                    {
                        "version": 1,
                        "claims": [
                            {
                                "claim_id": "C1",
                                "entity": "Oracle",
                                "ticker": "ORCL",
                                "claim_text": "52주 고점은 200달러 부근",
                                "claim_type": "numeric",
                                "time_window": "최근",
                                "queries": [{"query": "Oracle 52 week high 200", "language": "en", "source_priority": ["market"], "reason": "price verification"}],
                                "required_evidence": ["market_data"],
                                "asr_suspect_terms": [],
                            }
                        ],
                        "global_queries": [],
                        "closed_source_claims": [],
                        "asr_suspect_terms": [],
                    },
                    ensure_ascii=False,
                ),
                json.dumps(
                    {
                        "version": 1,
                        "overall_status": "supported",
                        "claims": [
                            {
                                "claim_id": "C1",
                                "claim_text": "52주 고점은 200달러 부근",
                                "status": "supported",
                                "confidence": 0.91,
                                "supporting_evidence_ids": ["E1"],
                                "contradicting_evidence_ids": [],
                                "verified_facts": ["공개 데이터와 대체로 일치"],
                                "counterpoints": [],
                                "investor_implication": "실적 전 고점 재돌파 여부 확인",
                                "manual_check_required": False,
                                "notes": "",
                            }
                        ],
                        "data_quality_notes": [],
                        "investor_checkpoints": ["실적"],
                    },
                    ensure_ascii=False,
                ),
                "# 최종 투자자 리포트\n\n- 영상 주장과 공개 데이터를 분리했습니다.",
            ]
        )

        verified = verify_youtube_bundle(
            bundle,
            draft,
            llm_settings=_llm_settings(),
            verification_settings=_verification_settings(research_enabled=True),
            market_data_provider=lambda ticker: MarketSnapshot(ticker, datetime.now(timezone.utc).isoformat(), fifty_two_week_high=198.0),
            external_data_provider=lambda _ticker, _generated_at: {"status": VERIFIED},
            research_evidence_provider=lambda _plan, _claims, _generated_at: {
                "version": 1,
                "status": VERIFIED,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "query_count": 1,
                "evidence_count": 1,
                "items": [
                    {
                        "evidence_id": "E1",
                        "claim_id": "C1",
                        "title": "ORCL market data",
                        "source_url": "https://finance.yahoo.com/quote/ORCL",
                        "publisher": "Yahoo Finance",
                        "published_at": None,
                        "source_tier": "market_or_news",
                        "excerpt": "52-week high near 198",
                    }
                ],
                "errors": [],
                "source_policy": {"raw_transcript_included": False},
            },
            llm_factory=lambda _settings: llm,
            generated_at=datetime(2026, 5, 28, 22, 0, tzinfo=timezone.utc),
        )

        self.assertEqual(verified.status, VERIFIED)
        self.assertIn("최종 투자자 리포트", verified.final_report_markdown)
        self.assertEqual(verified.verification["claims"]["entities"][0]["ticker"], "ORCL")
        self.assertEqual(verified.verification["version"], 4)
        self.assertEqual(verified.verification["claim_verification"]["claims"][0]["status"], "supported")
        self.assertEqual(verified.verification["evidence"]["evidence_count"], 1)
        self.assertEqual(len(llm.prompts), 4)
        self.assertNotIn("transcript_for_claim_extraction", llm.prompts[0])
        self.assertIn("transcript_chunks_for_claim_extraction", llm.prompts[0])
        self.assertNotIn("transcript_private_excerpt", llm.prompts[1])
        self.assertIn("transcript_private_chunks", llm.prompts[1])

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

    def test_verify_bundle_maps_macro_placeholders_to_market_symbols(self):
        bundle = _fake_bundle("KWDrgODHL60")
        draft = build_youtube_video_report(bundle, generated_at=datetime(2026, 5, 29, 8, 0))
        llm = FakeLLM(
            [
                json.dumps(
                    {
                        "overall_thesis": "매크로 영상",
                        "entities": [
                            {"ticker": "MARKET", "name": "한국 증시/코스피", "claims": ["코스피 하락"], "numeric_claims": [], "risks": [], "watch_items": []},
                            {"ticker": "OIL", "name": "국제유가/브렌트유", "claims": ["브렌트유 반등"], "numeric_claims": [], "risks": [], "watch_items": []},
                        ],
                        "verification_items": [],
                    },
                    ensure_ascii=False,
                ),
                "# 최종 투자자 리포트\n\n- 매크로 심볼을 확인했습니다.",
            ]
        )
        requested_symbols: list[str] = []
        external_symbols: list[str] = []

        def market_provider(symbol: str) -> MarketSnapshot:
            requested_symbols.append(symbol)
            return MarketSnapshot(symbol, datetime.now(timezone.utc).isoformat(), current_price=100.0)

        verified = verify_youtube_bundle(
            bundle,
            draft,
            llm_settings=_llm_settings(),
            verification_settings=_verification_settings(),
            market_data_provider=market_provider,
            external_data_provider=lambda ticker, _generated_at: external_symbols.append(ticker) or {"status": VERIFIED},
            llm_factory=lambda _settings: llm,
            generated_at=datetime(2026, 5, 29, 8, 0, tzinfo=timezone.utc),
        )

        self.assertEqual(requested_symbols, ["^KS11", "BZ=F"])
        self.assertEqual(external_symbols, [])
        self.assertEqual([item["ticker"] for item in verified.verification["entity_results"]], ["^KS11", "BZ=F"])
        self.assertEqual([item["original_ticker"] for item in verified.verification["entity_results"]], ["MARKET", "OIL"])

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
                    "https://www.youtube.com/@fixture/videos",
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
            first_video_dir = next(archive_dir.glob("runs/*/youtube_*/videos/video000001"))
            site_index = site_dir / "youtube" / "index.html"

            self.assertEqual(manifest["summary"]["total_videos"], 3)
            self.assertEqual(manifest["source_policy"]["research_pipeline_version"], 4)
            self.assertEqual(manifest["max_entries_per_url"], 25)
            self.assertEqual(manifest["parallel_video_execution"]["max_parallel_videos"], 1)
            self.assertEqual(manifest["videos"][0]["channel"], "경제사냥꾼")
            self.assertEqual(manifest["videos"][0]["source_url"], "https://www.youtube.com/@fixture/videos")
            self.assertIn("hqdefault.jpg", manifest["videos"][0]["thumbnail_url"])
            self.assertTrue(run_manifest.is_file())
            self.assertTrue((first_video_dir / "research_plan.json").is_file())
            self.assertTrue((first_video_dir / "evidence.json").is_file())
            self.assertTrue((first_video_dir / "claim_verification.json").is_file())
            self.assertTrue(site_index.is_file())
            site_html = site_index.read_text(encoding="utf-8")
            self.assertIn("Video", site_html)
            self.assertIn("출처/채널: 경제사냥꾼 · @fixture / 동영상", site_html)
            self.assertIn("hqdefault.jpg", site_html)
            public_summary = json.loads((first_video_dir / "public_summary.json").read_text(encoding="utf-8"))
            self.assertEqual(public_summary["source_url"], "https://www.youtube.com/@fixture/videos")
            self.assertIn("hqdefault.jpg", public_summary["thumbnail_url"])

    def test_runner_processes_videos_in_parallel_when_configured(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = _daily_config(root / "archive", root / "site")
            config = replace(config, channel=replace(config.channel, max_parallel_videos=2))
            refs = tuple(
                YouTubeVideoReference(
                    f"parallel00{i}",
                    f"https://www.youtube.com/watch?v=parallel00{i}",
                    f"Parallel {i}",
                    "fixture",
                    datetime.now(timezone.utc) - timedelta(hours=1),
                )
                for i in range(1, 4)
            )
            lock = threading.Lock()
            active_fetches = 0
            max_active_fetches = 0

            def fetcher(url: str, *, fetch_transcript: bool = True):
                nonlocal active_fetches, max_active_fetches
                if fetch_transcript:
                    with lock:
                        active_fetches += 1
                        max_active_fetches = max(max_active_fetches, active_fetches)
                    time.sleep(0.05)
                    with lock:
                        active_fetches -= 1
                return _fake_bundle(url[-11:], transcript=fetch_transcript)

            manifest = execute_youtube_run(
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

            self.assertEqual(manifest["summary"]["total_videos"], 3)
            self.assertTrue(manifest["parallel_video_execution"]["enabled"])
            self.assertEqual(manifest["parallel_video_execution"]["max_parallel_videos"], 2)
            self.assertGreaterEqual(max_active_fetches, 2)

    def test_runner_uses_configured_channel_entry_limit(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = _daily_config(root / "archive", root / "site")
            config = replace(config, channel=replace(config.channel, max_entries_per_url=7))
            requested_limits: list[int] = []

            execute_youtube_run(
                config,
                reference_lister=lambda _urls, limit: requested_limits.append(limit) or (),
                video_fetcher=lambda _url, *, fetch_transcript=True: (_ for _ in ()).throw(RuntimeError("no videos")),
                bundle_verifier=lambda _bundle, _draft, _generated_at: (_ for _ in ()).throw(RuntimeError("no videos")),
            )

            self.assertEqual(requested_limits, [7])

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

            self.assertEqual(calls, [(recent_id, True), (old_id, False)])

    def test_runner_excludes_videos_without_usable_transcript(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = _daily_config(root / "archive", root / "site")
            video_id = "notext00001"
            refs = (
                YouTubeVideoReference(
                    video_id,
                    f"https://www.youtube.com/watch?v={video_id}",
                    "No transcript",
                    "fixture",
                    datetime.now(timezone.utc) - timedelta(hours=1),
                ),
            )

            manifest = execute_youtube_run(
                config,
                reference_lister=lambda _urls, _limit: refs,
                video_fetcher=lambda url, *, fetch_transcript=True: _fake_bundle(url[-11:], transcript=False),
                bundle_verifier=lambda _bundle, _draft, _generated_at: (_ for _ in ()).throw(RuntimeError("should skip")),
            )

            self.assertEqual(manifest["summary"]["total_videos"], 0)
            self.assertEqual(manifest["summary"]["skipped_no_transcript"], 1)
            self.assertFalse((root / "site" / "youtube" / "feed.json").read_text(encoding="utf-8").count("No transcript"))

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
                "verification.json": json.dumps(
                    {"version": 4, "status": VERIFIED, "evidence": {"evidence_count": 1}},
                    ensure_ascii=False,
                ),
                "research_plan.json": json.dumps({"version": 1, "claims": []}, ensure_ascii=False),
                "evidence.json": json.dumps({"version": 1, "items": []}, ensure_ascii=False),
                "claim_verification.json": json.dumps({"version": 1, "claims": []}, ensure_ascii=False),
                "final_report.md": "# Reused final\n",
                "public_summary.json": json.dumps(
                    {"video_id": video_id, "status": VERIFIED, "transcript_status": "available", "transcript_chars": 240},
                    ensure_ascii=False,
                ),
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

            self.assertEqual(calls, [])
            self.assertEqual(manifest["summary"]["reused_videos"], 1)
            self.assertEqual(manifest["videos"][0]["reused_from_run"], "youtube_previous")
            self.assertIn("Reused final", next(archive_dir.glob("runs/*/youtube_*/videos/reuse000001/final_report.md")).read_text(encoding="utf-8"))

    def test_runner_invalidates_archived_reports_from_pre_role_routing_pipeline(self):
        self.assertFalse(_archived_verification_is_current({"version": 3, "evidence": {}}))
        self.assertTrue(_archived_verification_is_current({"version": 4, "evidence": {}}))

    def test_site_builder_preserves_root_site_and_does_not_copy_raw_transcript(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive_dir = root / "archive"
            run_dir = archive_dir / "runs" / "2026" / "youtube_20260528_220000"
            video_dir = run_dir / "videos" / "u2BEOgr8ze8"
            video_dir.mkdir(parents=True)
            (video_dir / "final_report.md").write_text("# Final\n\n짧은 근거만 공개합니다.", encoding="utf-8")
            (video_dir / "public_summary.json").write_text(
                json.dumps({"video_id": "u2BEOgr8ze8", "status": VERIFIED, "transcript_status": "available"}, ensure_ascii=False),
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
                                "channel": "Fixture channel",
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
            youtube_index = (site_dir / "youtube" / "index.html").read_text(encoding="utf-8")
            feed = json.loads((site_dir / "youtube" / "feed.json").read_text(encoding="utf-8"))

            self.assertEqual((site_dir / "index.html").read_text(encoding="utf-8"), "ROOT_SITE")
            self.assertNotIn("RAW_TRANSCRIPT_FULL_SHOULD_NOT_PUBLISH", public_text)
            self.assertTrue((site_dir / "youtube" / "feed.json").is_file())
            self.assertIn("출처/채널: Fixture channel", youtube_index)
            self.assertIn("https://i.ytimg.com/vi/u2BEOgr8ze8/hqdefault.jpg", youtube_index)
            self.assertEqual(feed["items"][0]["thumbnail_url"], "https://i.ytimg.com/vi/u2BEOgr8ze8/hqdefault.jpg")

    def test_site_builder_hides_collection_failures_from_report_lists(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive_dir = root / "archive"
            run_dir = archive_dir / "runs" / "2026" / "youtube_20260528_220000"
            ok_dir = run_dir / "videos" / "u2BEOgr8ze8"
            failed_dir = run_dir / "videos" / "failed00001"
            unavailable_dir = run_dir / "videos" / "notext00001"
            ok_dir.mkdir(parents=True)
            failed_dir.mkdir(parents=True)
            unavailable_dir.mkdir(parents=True)
            (ok_dir / "final_report.md").write_text("# Final\n\n공개 리포트입니다.", encoding="utf-8")
            (ok_dir / "public_summary.json").write_text(
                json.dumps({"video_id": "u2BEOgr8ze8", "status": VERIFIED, "transcript_status": "available"}, ensure_ascii=False),
                encoding="utf-8",
            )
            (failed_dir / "public_summary.json").write_text(
                json.dumps({"video_id": "failed00001", "status": "failed"}, ensure_ascii=False),
                encoding="utf-8",
            )
            (unavailable_dir / "final_report.md").write_text("# No text\n", encoding="utf-8")
            (unavailable_dir / "metadata.json").write_text(
                json.dumps({"transcript_status": "unavailable"}, ensure_ascii=False),
                encoding="utf-8",
            )
            (unavailable_dir / "public_summary.json").write_text(
                json.dumps({"video_id": "notext00001", "status": UNVERIFIED, "transcript_status": "unavailable"}, ensure_ascii=False),
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
                            {
                                "video_id": "notext00001",
                                "title": "Hidden unavailable transcript",
                                "video_url": "https://www.youtube.com/watch?v=notext00001",
                                "status": UNVERIFIED,
                                "metadata_path": "videos/notext00001/metadata.json",
                                "final_report_path": "videos/notext00001/final_report.md",
                                "public_summary_path": "videos/notext00001/public_summary.json",
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
            self.assertNotIn("Hidden unavailable transcript", index_html)
            self.assertIn("Visible fixture", run_html)
            self.assertNotIn("Hidden collection failure", run_html)
            self.assertNotIn("Hidden unavailable transcript", run_html)
            self.assertEqual(feed_titles, ["Visible fixture"])
            self.assertTrue((site_dir / "youtube" / "runs" / "youtube_20260528_220000" / "u2BEOgr8ze8.html").is_file())
            self.assertFalse((site_dir / "youtube" / "runs" / "youtube_20260528_220000" / "failed00001.html").exists())
            self.assertFalse((site_dir / "youtube" / "runs" / "youtube_20260528_220000" / "notext00001.html").exists())

    def test_site_builder_hides_legacy_reports_without_transcript_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            archive_dir = root / "archive"
            run_dir = archive_dir / "runs" / "2026" / "youtube_legacy"
            legacy_dir = run_dir / "videos" / "legacy00001"
            legacy_dir.mkdir(parents=True)
            (legacy_dir / "final_report.md").write_text(
                "# Legacy\n\n자막 본문이나 ASR 전문이 포함되어 있지 않아 확인할 수 없습니다.",
                encoding="utf-8",
            )
            (legacy_dir / "public_summary.json").write_text(
                json.dumps({"video_id": "legacy00001", "status": UNVERIFIED}, ensure_ascii=False),
                encoding="utf-8",
            )
            (run_dir / "youtube_run.json").write_text(
                json.dumps(
                    {
                        "run_id": "youtube_legacy",
                        "status": "success",
                        "started_at": "2026-05-28T22:00:00+09:00",
                        "videos": [
                            {
                                "video_id": "legacy00001",
                                "title": "Legacy no transcript",
                                "status": UNVERIFIED,
                                "final_report_path": "videos/legacy00001/final_report.md",
                                "public_summary_path": "videos/legacy00001/public_summary.json",
                            }
                        ],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            site_dir = root / "site"
            build_youtube_site(archive_dir, site_dir, YouTubeSiteSettings("YouTube 리포트", 10, 10))

            index_html = (site_dir / "youtube" / "index.html").read_text(encoding="utf-8")
            run_html = (site_dir / "youtube" / "runs" / "youtube_legacy" / "index.html").read_text(encoding="utf-8")
            feed = json.loads((site_dir / "youtube" / "feed.json").read_text(encoding="utf-8"))
            public_text = "\n".join(path.read_text(encoding="utf-8") for path in (site_dir / "youtube").rglob("*") if path.is_file())

            self.assertNotIn("Legacy no transcript", index_html)
            self.assertNotIn("Legacy no transcript", run_html)
            self.assertEqual(feed["items"], [])
            self.assertFalse((site_dir / "youtube" / "runs" / "youtube_legacy" / "legacy00001.html").exists())
            self.assertNotIn("자막 본문이나 ASR 전문", public_text)

    def test_github_actions_workflow_schedule_and_pages_artifact(self):
        workflow = Path(".github/workflows/daily-youtube-reports.yml").read_text(encoding="utf-8")

        self.assertIn("Target: after the US intraday overlay window", workflow)
        self.assertIn("20 20 * * *", workflow)
        self.assertIn("55 20 * * *", workflow)
        self.assertIn("25 21 * * *", workflow)
        self.assertIn("55 21 * * *", workflow)
        self.assertIn("every day including", workflow)
        self.assertIn("schedule_gate", workflow)
        self.assertIn("actions: read", workflow)
        self.assertNotIn("concurrency:\n  group: daily-youtube-verified-reports", workflow)
        self.assertIn("scheduled_workflow_gate.py", workflow)
        self.assertIn("EVENT_SCHEDULE: ${{ github.event.schedule }}", workflow)
        self.assertNotIn("SCHEDULE_GATE_BLOCK_US_INTRADAY_OVERLAY", workflow)
        self.assertIn("SCHEDULE_GATE_TARGETS_JSON", workflow)
        self.assertIn('"target_jobs": ["build_youtube_pages"]', workflow)
        self.assertIn('"name": "daily-codex-us-pages"', workflow)
        self.assertIn('"name": "intraday-overlay-us-publish"', workflow)
        self.assertNotIn("0 13 * * *", workflow)
        self.assertNotIn("17 14 * * *", workflow)
        self.assertNotIn("47 14 * * *", workflow)
        self.assertNotIn("* * 1-5", workflow)
        self.assertIn("actions/upload-pages-artifact", workflow)
        self.assertIn("tradingagents.youtube.runner", workflow)
        self.assertIn("max_entries_per_url", workflow)
        self.assertIn('default: "100"', workflow)
        self.assertIn("--max-entries-per-url", workflow)
        self.assertIn("max_parallel_videos", workflow)
        self.assertIn("--max-parallel-videos", workflow)
        self.assertIn("config/scheduled_analysis.toml", workflow)
        config_text = Path("config/youtube_daily.toml").read_text(encoding="utf-8")
        self.assertIn("research_enabled = true", config_text)
        self.assertIn("max_research_queries", config_text)
        self.assertIn("max_entries_per_url = 25", config_text)
        self.assertIn("max_videos = 100", config_text)
        self.assertIn("max_parallel_videos = 4", config_text)
        self.assertIn("[asr]", config_text)
        self.assertIn('model = "auto"', config_text)
        self.assertIn("beam_size = 5", config_text)
        self.assertIn("max_transcript_chars_for_llm = 24000", config_text)
        self.assertIn("adaptive_transcript_budget_enabled = true", config_text)
        self.assertIn("extended_transcript_chars_for_llm = 48000", config_text)
        self.assertIn("evidence_relevance_gate_enabled = true", config_text)
        self.assertIn("min_evidence_relevance_score = 0.12", config_text)
        self.assertIn("YOUTUBE_COOKIES_FILE", workflow)
        self.assertIn("YOUTUBE_PROXY", workflow)
        self.assertIn("YOUTUBE_VISITOR_DATA", workflow)
        self.assertIn("YOUTUBE_PO_TOKEN", workflow)
        self.assertIn("YOUTUBE_SUBS_PO_TOKEN", workflow)
        self.assertIn("YOUTUBE_GVS_PO_TOKEN", workflow)
        self.assertIn("YOUTUBE_PLAYER_CLIENTS", workflow)
        self.assertIn("TRADINGAGENTS_YOUTUBE_ASR_FALLBACK", workflow)
        self.assertIn("TRADINGAGENTS_YOUTUBE_ASR_MODEL", workflow)
        self.assertIn('TRADINGAGENTS_YOUTUBE_ASR_MODEL: "auto"', workflow)
        self.assertIn("TRADINGAGENTS_YOUTUBE_ASR_COMPUTE_TYPE", workflow)
        self.assertIn('TRADINGAGENTS_YOUTUBE_ASR_BEAM_SIZE: "5"', workflow)
        self.assertIn("actions/setup-node", workflow)
        self.assertIn("Start bgutil PO token provider", workflow)
        self.assertIn("TRADINGAGENTS_YOUTUBE_BGUTIL_BASE_URL", workflow)
        self.assertIn("Probe YouTube ASR and PO token runtime", workflow)
        self.assertNotIn("OPENAI_API_KEY", workflow)
        self.assertLess(workflow.index("Run YouTube verification reports"), workflow.index("Configure GitHub Pages"))
        self.assertLess(workflow.index("Configure GitHub Pages"), workflow.index("Upload GitHub Pages artifact"))
        self.assertIn("continue-on-error: true", workflow)

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

    def test_youtube_daily_config_includes_all_default_channels(self):
        config = load_youtube_config("config/youtube_daily.toml")
        expected_urls = {
            "https://www.youtube.com/@%EA%B2%BD%EC%A0%9C%EC%82%AC%EB%83%A5%EA%BE%BC/videos",
            "https://www.youtube.com/@%EA%B2%BD%EC%A0%9C%EC%82%AC%EB%83%A5%EA%BE%BC/shorts",
            "https://www.youtube.com/@sosumonkey/videos",
            "https://www.youtube.com/@815moneytalk/videos",
            "https://www.youtube.com/@supe-tv/videos",
            "https://www.youtube.com/@3protv/videos",
            "https://www.youtube.com/@plus_tv_official/videos",
        }

        self.assertEqual(config.channel.name, "투자 유튜브 채널")
        self.assertEqual(set(config.channel.urls), expected_urls)
        self.assertEqual(config.channel.max_videos, 100)
        self.assertEqual(config.channel.max_entries_per_url, 25)
        self.assertEqual(config.channel.max_parallel_videos, 4)
        self.assertEqual(set(DEFAULT_CHANNEL_URLS), expected_urls)
        self.assertEqual(config.asr.model, "auto")
        self.assertEqual(config.asr.device, "auto")
        self.assertEqual(config.asr.beam_size, 5)
        self.assertEqual(config.asr.max_chunks, 12)
        self.assertIn("엔비디아", config.asr.hotwords)

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
                json.dumps({"video_id": "u2BEOgr8ze8", "status": VERIFIED, "transcript_status": "available"}, ensure_ascii=False),
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
    transcript_text = (
        "오라클 티커는 ORCL. 52주 고점은 200달러 부근이라고 말한다. "
        "영상은 투자자가 확인해야 할 숫자 주장과 리스크, 후속 체크포인트를 설명한다. "
    ) * 3
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
            thumbnail_url=f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg",
            tags=(),
            categories=(),
        ),
        transcript=(
            YouTubeTranscript(
                language="ko",
                language_name="Korean",
                source="automatic",
                segments=(),
                raw_text=transcript_text,
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


def _verification_settings(*, research_enabled: bool = False) -> VerificationSettings:
    return VerificationSettings(
        mode="external_full",
        publish_unverified=True,
        max_claims_per_video=8,
        strict_llm=True,
        research_enabled=research_enabled,
        max_research_queries=4,
        max_evidence_items=6,
        max_evidence_per_claim=2,
        fetch_web_pages=False,
        max_web_pages=0,
        max_transcript_chars_for_llm=12000,
    )


def _daily_config(archive_dir: Path, site_dir: Path) -> YouTubeDailyConfig:
    return YouTubeDailyConfig(
        channel=ChannelSettings(
            name="경제사냥꾼",
            urls=("https://www.youtube.com/@fixture/videos", "https://www.youtube.com/@fixture/shorts"),
            lookback_hours=24,
            timezone="Asia/Seoul",
            max_videos=3,
            max_entries_per_url=25,
            max_parallel_videos=1,
        ),
        llm=_llm_settings(),
        verification=_verification_settings(),
        storage=StorageSettings(archive_dir=archive_dir, site_dir=site_dir),
        site=YouTubeSiteSettings("YouTube 리포트", 10, 10),
    )


if __name__ == "__main__":
    unittest.main()
