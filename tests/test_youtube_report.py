from __future__ import annotations

from datetime import datetime, timezone
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import requests

from tradingagents.dataflows.youtube_video import (
    YouTubeTranscript,
    YouTubeVideoBundle,
    YouTubeVideoMetadata,
    _download_transcript_track,
    _youtube_dl_options,
    extract_youtube_video_id,
    _parse_json3_segments,
)
from tradingagents.youtube_report import build_youtube_video_report, summarize_financial_entities


class YouTubeVideoReportTests(unittest.TestCase):
    def test_extract_youtube_video_id_supports_common_url_forms(self):
        self.assertEqual(
            extract_youtube_video_id("https://www.youtube.com/watch?v=u2BEOgr8ze8"),
            "u2BEOgr8ze8",
        )
        self.assertEqual(extract_youtube_video_id("https://youtu.be/u2BEOgr8ze8"), "u2BEOgr8ze8")
        self.assertEqual(extract_youtube_video_id("https://www.youtube.com/shorts/u2BEOgr8ze8"), "u2BEOgr8ze8")
        self.assertEqual(extract_youtube_video_id("u2BEOgr8ze8"), "u2BEOgr8ze8")

    def test_parse_json3_segments_normalizes_caption_text(self):
        payload = {
            "events": [
                {
                    "tStartMs": 1000,
                    "dDurationMs": 2100,
                    "segs": [
                        {"utf8": "오라클"},
                        {"utf8": " RPO"},
                        {"utf8": " 5,530억 달러"},
                    ],
                },
                {"tStartMs": 3100, "dDurationMs": 500, "segs": [{"utf8": "[음악]"}]},
            ]
        }

        segments = _parse_json3_segments(payload)

        self.assertEqual(len(segments), 1)
        self.assertEqual(segments[0].start_seconds, 1.0)
        self.assertEqual(segments[0].text, "오라클 RPO 5,530억 달러")

    def test_download_transcript_track_treats_rate_limit_as_unavailable(self):
        class RateLimitedSession:
            def get(self, _url, timeout):
                response = requests.Response()
                response.status_code = 429
                return response

        with patch("tradingagents.dataflows.youtube_video._caption_session", return_value=RateLimitedSession()), patch(
            "tradingagents.dataflows.youtube_video._respect_caption_throttle"
        ), patch("tradingagents.dataflows.youtube_video.time.sleep"):
            transcript = _download_transcript_track(
                {"url": "https://www.youtube.com/api/timedtext", "ext": "json3"},
                language="ko",
                source="automatic",
                timeout_seconds=1.0,
            )

        self.assertIsNone(transcript)

    def test_download_transcript_track_retries_rate_limit_with_browser_headers(self):
        class FakeResponse:
            def __init__(self, status_code: int, text: str = "", headers: dict[str, str] | None = None):
                self.status_code = status_code
                self.text = text
                self.headers = headers or {}

            def raise_for_status(self):
                if self.status_code >= 400:
                    raise requests.HTTPError(str(self.status_code))

            def json(self):
                return {"events": [{"tStartMs": 0, "dDurationMs": 1000, "segs": [{"utf8": "오라클"}]}]}

        class FakeSession:
            def __init__(self):
                self.calls = 0

            def get(self, _url, timeout):
                self.calls += 1
                if self.calls == 1:
                    return FakeResponse(429, headers={"Retry-After": "1"})
                return FakeResponse(200, text='{"events":[]}')

        session = FakeSession()
        with patch("tradingagents.dataflows.youtube_video._caption_session", return_value=session), patch(
            "tradingagents.dataflows.youtube_video._respect_caption_throttle"
        ), patch("tradingagents.dataflows.youtube_video.time.sleep") as sleep:
            transcript = _download_transcript_track(
                {"url": "https://www.youtube.com/api/timedtext", "ext": "json3"},
                language="ko",
                source="automatic",
                timeout_seconds=1.0,
            )

        self.assertEqual(session.calls, 2)
        sleep.assert_called_once()
        self.assertIsNotNone(transcript)
        self.assertEqual(transcript.raw_text, "오라클")

    def test_youtube_dl_options_uses_optional_cookie_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            cookie_path = Path(tmp) / "cookies.txt"
            cookie_path.write_text("# Netscape HTTP Cookie File\n", encoding="utf-8")
            with patch.dict(os.environ, {"YOUTUBE_COOKIES_FILE": str(cookie_path)}, clear=False):
                options = _youtube_dl_options(skip_download=True)

        self.assertEqual(options["cookiefile"], str(cookie_path))

    def test_summarize_financial_entities_extracts_video_claims(self):
        transcript = (
            "첫 번째 종목은 오라클이야. 티커는 ORCL. RPO가 5,530억 달러라고 말한다. "
            "시장 우려는 오픈 AI 집중이다. 두 번째 종목은 서비스 나우야. 티커는 NOW. "
            "AI 제품 매출이 성장했고 자사주 매입보다 수주가 중요하다고 말한다."
        )

        summaries = summarize_financial_entities(transcript)
        tickers = [summary.entity.ticker for summary in summaries]

        self.assertIn("ORCL", tickers)
        self.assertIn("NOW", tickers)
        oracle = next(summary for summary in summaries if summary.entity.ticker == "ORCL")
        self.assertTrue(any("5,530억 달러" in claim for claim in oracle.numeric_claims))
        self.assertTrue(any("우려" in risk for risk in oracle.risk_points))

    def test_build_report_includes_collection_status_and_entity_table(self):
        transcript = YouTubeTranscript(
            language="ko",
            language_name="Korean",
            source="automatic",
            track_ext="json3",
            segments=(),
            raw_text=(
                "오라클 티커는 ORCL. RPO가 5,530억 달러라고 말한다. "
                "세일즈 포스 티커는 CRM. 자사주 매입 규모가 250억 달러라고 말한다."
            ),
        )
        bundle = YouTubeVideoBundle(
            metadata=YouTubeVideoMetadata(
                video_id="u2BEOgr8ze8",
                url="https://www.youtube.com/watch?v=u2BEOgr8ze8",
                title="현시점 월가에서 가장 저평가 됐다는 ' 종목 5개",
                channel="경제사냥꾼",
                channel_id="UC7usMJDHmtbs_oegmzQKKMA",
                upload_date="20260527",
                published_at=datetime(2026, 5, 27, tzinfo=timezone.utc),
                duration_seconds=793,
                view_count=6400,
                like_count=None,
                description="",
                thumbnail_url="",
                tags=(),
                categories=(),
            ),
            transcript=transcript,
            transcript_status="available",
            available_manual_caption_languages=(),
            available_auto_caption_languages=("ko", "en"),
        )

        report = build_youtube_video_report(bundle, generated_at=datetime(2026, 5, 28, 9, 0, 0))

        self.assertIn("## 1. 분석 가능 수준", report)
        self.assertIn("automatic, Korean, json3", report)
        self.assertIn("Oracle (ORCL)", report)
        self.assertIn("Salesforce (CRM)", report)
        self.assertIn("5,530억 달러", report)


if __name__ == "__main__":
    unittest.main()
