from __future__ import annotations

import io
import json
import tempfile
import unittest
import urllib.error
from pathlib import Path

from tradingagents.notifications.__main__ import _requires_private_chat
from tradingagents.notifications.telegram import (
    AtomicNotificationLedger,
    NotificationError,
    TelegramBotClient,
    chunk_text,
    compose_notification,
    inspect_workflow_run,
    notification_event_key,
)


class _Response:
    def __init__(self, payload: dict, status: int = 200):
        self.payload = json.dumps(payload).encode("utf-8")
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self):
        return self.payload


def _run(**overrides):
    value = {
        "id": 123,
        "name": "Daily Codex Analysis",
        "head_repository": {"full_name": "nornen0202/TradingAgents"},
        "head_branch": "main",
        "conclusion": "success",
        "html_url": "https://github.com/nornen0202/TradingAgents/actions/runs/123",
        "event": "schedule",
        "head_sha": "a" * 40,
        "run_attempt": 1,
        "created_at": "2026-07-15T00:00:00Z",
        "updated_at": "2026-07-15T02:00:00Z",
    }
    value.update(overrides)
    return value


class WorkflowInspectionTests(unittest.TestCase):
    def test_success_requires_a_real_terminal_job_and_infers_market(self):
        result = inspect_workflow_run(
            _run(),
            [
                {"name": "analyze_kr", "conclusion": "success"},
                {"name": "analyze_us", "conclusion": "skipped"},
                {"name": "deploy", "conclusion": "success"},
            ],
            repository="nornen0202/TradingAgents",
        )
        self.assertTrue(result["should_notify"])
        self.assertEqual(result["reason"], "terminal_job_succeeded")
        self.assertEqual(result["surfaces"], ["kr"])

    def test_successful_backup_probe_with_skipped_work_does_not_notify(self):
        result = inspect_workflow_run(
            _run(),
            [{"name": "deploy", "conclusion": "skipped"}],
            repository="nornen0202/TradingAgents",
        )
        self.assertFalse(result["should_notify"])
        self.assertEqual(result["reason"], "no_work_gate_skip")

    def test_failure_notifies_even_when_terminal_job_never_started(self):
        result = inspect_workflow_run(
            _run(conclusion="failure", head_sha=""),
            [{"name": "schedule_gate", "conclusion": "failure"}],
            repository="nornen0202/TradingAgents",
        )
        self.assertTrue(result["should_notify"])
        self.assertEqual(result["reason"], "upstream_failed")

    def test_success_requires_commit_provenance(self):
        with self.assertRaises(NotificationError):
            inspect_workflow_run(
                _run(head_sha=""),
                [{"name": "deploy", "conclusion": "success"}],
                repository="nornen0202/TradingAgents",
            )

    def test_startup_failure_and_stale_runs_still_notify_without_jobs(self):
        for conclusion in ("startup_failure", "stale"):
            with self.subTest(conclusion=conclusion):
                result = inspect_workflow_run(
                    _run(conclusion=conclusion),
                    [],
                    repository="nornen0202/TradingAgents",
                )
                self.assertTrue(result["should_notify"])
                self.assertEqual(result["reason"], "upstream_failed")

    def test_wholly_skipped_workflow_does_not_emit_false_failure_alert(self):
        result = inspect_workflow_run(
            _run(conclusion="skipped"),
            [],
            repository="nornen0202/TradingAgents",
        )
        self.assertFalse(result["should_notify"])
        self.assertEqual(result["reason"], "no_work_workflow_skipped")

    def test_untrusted_repository_or_branch_is_rejected(self):
        with self.assertRaises(NotificationError):
            inspect_workflow_run(
                _run(head_repository={"full_name": "attacker/fork"}),
                [{"name": "deploy", "conclusion": "success"}],
                repository="nornen0202/TradingAgents",
            )
        with self.assertRaises(NotificationError):
            inspect_workflow_run(
                _run(head_branch="feature"),
                [{"name": "deploy", "conclusion": "success"}],
                repository="nornen0202/TradingAgents",
            )


class TelegramTransportTests(unittest.TestCase):
    def test_chunks_unicode_text_without_exceeding_limit(self):
        chunks = chunk_text("가" * 75 + "\n" + "나" * 75, limit=64)
        self.assertGreater(len(chunks), 2)
        self.assertTrue(all(0 < len(item) <= 64 for item in chunks))

    def test_retries_429_and_validates_success_receipt(self):
        calls = []
        sleeps = []

        def opener(_request, timeout):
            calls.append(timeout)
            if len(calls) == 1:
                body = io.BytesIO(
                    json.dumps({"ok": False, "parameters": {"retry_after": 2}}).encode("utf-8")
                )
                raise urllib.error.HTTPError("redacted", 429, "rate limited", {}, body)
            return _Response({"ok": True, "result": {"message_id": 77}})

        client = TelegramBotClient(
            bot_token="token",
            chat_id="42",
            opener=opener,
            sleep=sleeps.append,
        )
        self.assertEqual(client.send_message("hello"), 77)
        self.assertEqual(len(calls), 2)
        self.assertEqual(sleeps, [2.0])

    def test_rejects_http_200_without_ok_receipt(self):
        client = TelegramBotClient(
            bot_token="token",
            chat_id="42",
            max_attempts=1,
            opener=lambda *_args, **_kwargs: _Response({"ok": False}),
        )
        with self.assertRaises(NotificationError):
            client.send_message("hello")

    def test_get_chat_requires_matching_private_receipt(self):
        client = TelegramBotClient(
            bot_token="token",
            chat_id="42",
            opener=lambda *_args, **_kwargs: _Response(
                {"ok": True, "result": {"id": 42, "type": "private"}}
            ),
        )
        self.assertIsNone(client.ensure_private_chat())

    def test_get_chat_rejects_non_private_or_mismatched_receipt_without_secret_values(self):
        cases = (
            {"ok": True, "result": {"id": 42, "type": "supergroup"}},
            {"ok": True, "result": {"id": 999, "type": "private"}},
            {"ok": True, "result": {"type": "private"}},
        )
        for payload in cases:
            with self.subTest(payload=payload):
                client = TelegramBotClient(
                    bot_token="TOP-SECRET-BOT-TOKEN",
                    chat_id="42",
                    max_attempts=1,
                    opener=lambda *_args, _payload=payload, **_kwargs: _Response(_payload),
                )
                with self.assertRaises(NotificationError) as caught:
                    client.ensure_private_chat()
                message = str(caught.exception)
                self.assertNotIn("TOP-SECRET-BOT-TOKEN", message)
                self.assertNotIn("42", message)

    def test_transport_exception_cannot_echo_bot_token_or_chat_id(self):
        def opener(request, **_kwargs):
            raise ValueError(f"invalid destination {request.full_url} chat 42")

        client = TelegramBotClient(
            bot_token="TOP-SECRET-BOT-TOKEN",
            chat_id="42",
            max_attempts=1,
            opener=opener,
        )
        for operation in (client.ensure_private_chat, lambda: client.send_message("hello")):
            with self.subTest(operation=operation), self.assertRaises(NotificationError) as caught:
                operation()
            message = str(caught.exception)
            self.assertNotIn("TOP-SECRET-BOT-TOKEN", message)
            self.assertNotIn("42", message)

    def test_requires_explicit_destination(self):
        with self.assertRaises(NotificationError):
            TelegramBotClient(bot_token="token", chat_id="")

    def test_rejects_group_channel_and_username_destinations(self):
        for chat_id in ("-1001234567890", "-42", "@public_channel", "0042"):
            with self.subTest(chat_id=chat_id), self.assertRaises(NotificationError):
                TelegramBotClient(bot_token="token", chat_id=chat_id)


class AtomicLedgerTests(unittest.TestCase):
    def test_delivery_is_deduplicated_and_does_not_persist_message_content(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "ledger.json"
            sent = []
            ledger = AtomicNotificationLedger(path)
            first = ledger.deliver(
                event_key="event-1",
                chunks=["private message", "second"],
                buttons=[[{"text": "private", "url": "https://example.test/#key=secret"}]],
                sender=lambda text, _buttons: sent.append(text) or len(sent),
                receipt_metadata={"upstream_run_id": 1},
            )
            second = ledger.deliver(
                event_key="event-1",
                chunks=["private message", "second"],
                buttons=[[{"text": "private", "url": "https://example.test/#key=secret"}]],
                sender=lambda *_args: 999,
                receipt_metadata={"upstream_run_id": 1},
            )
            self.assertEqual(first["status"], "SENT")
            self.assertEqual(second["status"], "NOOP")
            self.assertEqual(sent, ["private message", "second"])
            stored = path.read_text(encoding="utf-8")
            self.assertNotIn("private message", stored)
            self.assertNotIn("secret", stored)

    def test_partial_delivery_resumes_at_unsent_chunk(self):
        with tempfile.TemporaryDirectory() as temp:
            ledger = AtomicNotificationLedger(Path(temp) / "ledger.json")
            first_calls = []

            def first_sender(text, _buttons):
                first_calls.append(text)
                if len(first_calls) == 2:
                    raise NotificationError("network")
                return 10

            with self.assertRaises(NotificationError):
                ledger.deliver(
                    event_key="event-2",
                    chunks=["one", "two", "three"],
                    buttons=None,
                    sender=first_sender,
                    receipt_metadata={},
                )

            resumed = []
            result = ledger.deliver(
                event_key="event-2",
                chunks=["one", "two", "three"],
                buttons=None,
                sender=lambda text, _buttons: resumed.append(text) or 20 + len(resumed),
                receipt_metadata={},
            )
            self.assertEqual(result["status"], "SENT")
            self.assertEqual(resumed, ["two", "three"])

    def test_corrupt_ledger_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "ledger.json"
            path.write_text("not-json", encoding="utf-8")
            with self.assertRaises(NotificationError):
                AtomicNotificationLedger(path).deliver(
                    event_key="event-3",
                    chunks=["hello"],
                    buttons=None,
                    sender=lambda *_args: 1,
                    receipt_metadata={},
                )


class CompositionTests(unittest.TestCase):
    def test_only_sensitive_links_or_private_cards_require_get_chat_validation(self):
        public = [[{"text": "report", "url": "https://example.test/mobile/"}]]
        private = [[{"text": "private", "url": "https://example.test/private.html#key=abc&market=kr"}]]
        self.assertFalse(_requires_private_chat(public, cards_only=False))
        self.assertTrue(_requires_private_chat(private, cards_only=False))
        self.assertTrue(_requires_private_chat([], cards_only=True))

    def test_remote_success_includes_public_mobile_and_fragment_private_links(self):
        context = inspect_workflow_run(
            _run(),
            [
                {"name": "analyze_kr", "conclusion": "success"},
                {"name": "deploy", "conclusion": "success"},
            ],
            repository="nornen0202/TradingAgents",
        )
        with tempfile.TemporaryDirectory() as temp:
            chunks, buttons, metadata = compose_notification(
                context,
                archive_dir=Path(temp),
                public_base_url="https://example.test/TradingAgents",
                mobile_dashboard_key="A" * 43,
            )
        urls = [button["url"] for row in buttons for button in row]
        self.assertTrue(chunks)
        self.assertIn("kr", metadata["surfaces"])
        self.assertIn("https://example.test/TradingAgents/mobile/?market=kr", urls)
        self.assertIn(
            f"https://example.test/TradingAgents/mobile/private.html#key={'A' * 43}&market=kr",
            urls,
        )

    def test_youtube_uses_existing_mobile_safe_report_without_private_key_link(self):
        context = inspect_workflow_run(
            _run(name="Daily YouTube Verified Reports"),
            [{"name": "deploy", "conclusion": "success"}],
            repository="nornen0202/TradingAgents",
        )
        with tempfile.TemporaryDirectory() as temp:
            _chunks, buttons, _metadata = compose_notification(
                context,
                archive_dir=Path(temp),
                public_base_url="https://example.test/TradingAgents",
                mobile_dashboard_key="A" * 43,
            )
        urls = [button["url"] for row in buttons for button in row]
        self.assertIn("https://example.test/TradingAgents/youtube/", urls)
        self.assertFalse(any("#key=" in url for url in urls))

    def test_private_cards_are_loaded_only_from_matching_archive_window(self):
        with tempfile.TemporaryDirectory() as temp:
            archive = Path(temp)
            run_dir = archive / "runs" / "2026" / "20260715T010000_github-actions-kr"
            run_dir.mkdir(parents=True)
            (run_dir / "run.json").write_text(
                json.dumps(
                    {
                        "run_id": run_dir.name,
                        "label": "github-actions-kr",
                        "status": "success",
                        "started_at": "2026-07-15T10:00:00+09:00",
                        "finished_at": "2026-07-15T10:45:00+09:00",
                        "settings": {"market": "KR"},
                        "summary": {
                            "total_tickers": 1,
                            "successful_tickers": 1,
                            "failed_tickers": 0,
                        },
                        "active_universe": {
                            "ticker_universe_mode": "config_only",
                            "missing_holding_tickers": [],
                            "missing_watchlist_tickers": [],
                            "missing_analysis_tickers": [],
                            "failed_analysis_tickers": [],
                            "unexpected_analysis_tickers": [],
                            "duplicate_analysis_tickers": [],
                            "coverage": {
                                "complete": True,
                                "selection_complete": True,
                                "analysis_complete": True,
                                "analysis_expected_count": 1,
                                "analysis_successful_count": 1,
                                "holding_missing_count": 0,
                                "watchlist_missing_count": 0,
                                "analysis_failed_count": 0,
                                "analysis_missing_count": 0,
                                "analysis_unexpected_count": 0,
                                "analysis_duplicate_count": 0,
                            },
                        },
                        "tickers": [{"ticker": "005930.KS", "status": "success"}],
                        "github_actions": {
                            "run_id": 123,
                            "run_attempt": 1,
                            "repository": "nornen0202/TradingAgents",
                            "workflow": "Daily Codex Analysis",
                            "sha": "a" * 40,
                        },
                    }
                ),
                encoding="utf-8",
            )
            (run_dir / "decision_bundle_v2.json").write_text(
                json.dumps(
                    {
                        "run_id": run_dir.name,
                        "market": "KR",
                        "generated_at": "2026-07-15T10:40:00+09:00",
                        "analysis_source_run_id": run_dir.name,
                        "execution_source_run_id": run_dir.name,
                        "quality": {
                            "decision_ready": True,
                            "conditional_strategy_ready": True,
                            "total_rows": 1,
                        },
                        "summary": {"immediate_action_count": 1},
                        "strategy_table": [
                            {
                                "table_priority": 1,
                                "ticker": "005930.KS",
                                "is_held": True,
                                "strategy_ko": "보유 유지",
                                "last_price": 70000,
                                "market_data_asof": "2026-07-15T10:35:00+09:00",
                                "data_status_ko": "실시간",
                                "execution_condition_ko": "조건 확인",
                                "risk_condition_ko": "지지선 이탈",
                                "quality": {
                                    "row_mode": "IMMEDIATE",
                                    "execution_ready": True,
                                    "generated_in_current_run": True,
                                    "freshness_class": "LIVE_CHECKPOINT",
                                    "conditional_strategy_ready": True,
                                },
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )
            context = inspect_workflow_run(
                _run(created_at="2026-07-15T01:00:00Z", updated_at="2026-07-15T02:00:00Z"),
                [
                    {"name": "analyze_kr", "conclusion": "success"},
                    {"name": "deploy", "conclusion": "success"},
                ],
                repository="nornen0202/TradingAgents",
            )
            chunks, buttons, metadata = compose_notification(
                context,
                archive_dir=archive,
                public_base_url="https://example.test/TradingAgents",
                mobile_dashboard_key=None,
                cards_only=True,
            )
            _full_chunks, full_buttons, _full_metadata = compose_notification(
                context,
                archive_dir=archive,
                public_base_url="https://example.test/TradingAgents",
                mobile_dashboard_key="A" * 43,
            )
            manifest_path = run_dir / "run.json"
            incomplete_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            incomplete_manifest["active_universe"]["coverage"]["complete"] = False
            manifest_path.write_text(json.dumps(incomplete_manifest), encoding="utf-8")
            blocked_chunks, _blocked_buttons, _blocked_metadata = compose_notification(
                context,
                archive_dir=archive,
                public_base_url="https://example.test/TradingAgents",
                mobile_dashboard_key=None,
                cards_only=True,
            )
            incomplete_manifest["active_universe"]["coverage"]["complete"] = True
            manifest_path.write_text(json.dumps(incomplete_manifest), encoding="utf-8")
            bundle_path = run_dir / "decision_bundle_v2.json"
            stale_bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
            stale_bundle["strategy_table"][0]["market_data_asof"] = "2026-07-15T09:00:00+09:00"
            bundle_path.write_text(json.dumps(stale_bundle), encoding="utf-8")
            stale_chunks, _stale_buttons, _stale_metadata = compose_notification(
                context,
                archive_dir=archive,
                public_base_url="https://example.test/TradingAgents",
                mobile_dashboard_key=None,
                cards_only=True,
            )
            incomplete_manifest["github_actions"]["run_id"] = 999
            manifest_path.write_text(json.dumps(incomplete_manifest), encoding="utf-8")
            unmatched_chunks, _unmatched_buttons, unmatched_metadata = compose_notification(
                context,
                archive_dir=archive,
                public_base_url="https://example.test/TradingAgents",
                mobile_dashboard_key=None,
                cards_only=True,
            )
        self.assertIn("005930.KS", "\n".join(chunks))
        self.assertIn("보유/즉시", "\n".join(chunks))
        self.assertEqual(buttons, [])
        self.assertEqual(metadata["run_ids"], [run_dir.name])
        private_urls = [
            button["url"]
            for row in full_buttons
            for button in row
            if "private.html" in button["url"]
        ]
        self.assertEqual(len(private_urls), 1)
        self.assertIn(f"&run={run_dir.name}", private_urls[0])
        self.assertNotIn("005930.KS", "\n".join(blocked_chunks))
        self.assertIn("UNIVERSE_INCOMPLETE", "\n".join(blocked_chunks))
        self.assertNotIn("005930.KS", "\n".join(stale_chunks))
        self.assertIn("ROW_NOT_FRESH_IMMEDIATE", "\n".join(stale_chunks))
        self.assertEqual(unmatched_chunks, [])
        self.assertEqual(unmatched_metadata["run_ids"], [])

    def test_missing_dashboard_key_keeps_public_alert_but_omits_private_content(self):
        context = inspect_workflow_run(
            _run(),
            [
                {"name": "analyze_kr", "conclusion": "success"},
                {"name": "deploy", "conclusion": "success"},
            ],
            repository="nornen0202/TradingAgents",
        )
        with tempfile.TemporaryDirectory() as temp:
            chunks, buttons, _metadata = compose_notification(
                context,
                archive_dir=Path(temp),
                public_base_url="https://example.test/TradingAgents",
                mobile_dashboard_key=None,
            )

        text = "\n".join(chunks)
        urls = [button["url"] for row in buttons for button in row]
        self.assertIn("MOBILE_DASHBOARD_KEY", text)
        self.assertIn("분석·배포 완료", text)
        self.assertFalse(any("private.html" in url or "#key=" in url for url in urls))

    def test_failure_message_does_not_expose_dashboard_key(self):
        context = inspect_workflow_run(
            _run(conclusion="failure"),
            [{"name": "analyze_kr", "conclusion": "failure"}],
            repository="nornen0202/TradingAgents",
        )
        chunks, buttons, _ = compose_notification(
            context,
            archive_dir=Path("missing"),
            public_base_url="https://example.test/TradingAgents",
            mobile_dashboard_key="do-not-leak",
        )
        self.assertNotIn("do-not-leak", "\n".join(chunks) + json.dumps(buttons))

    def test_event_key_is_stable_and_destination_scoped(self):
        first = notification_event_key(
            repository="r/x", upstream_run_id=1, conclusion="success", chat_id="one"
        )
        second = notification_event_key(
            repository="r/x", upstream_run_id=1, conclusion="success", chat_id="one"
        )
        other = notification_event_key(
            repository="r/x", upstream_run_id=1, conclusion="success", chat_id="two"
        )
        self.assertEqual(first, second)
        self.assertNotEqual(first, other)


class WorkflowDefinitionTests(unittest.TestCase):
    def test_central_workflow_is_remote_safe_and_secret_scoped(self):
        path = Path(__file__).parents[1] / ".github" / "workflows" / "tradingagents-mobile-notifications.yml"
        text = path.read_text(encoding="utf-8")
        self.assertIn("workflow_run:", text)
        self.assertIn("runs-on: ubuntu-latest", text)
        self.assertIn("head_repository.full_name == github.repository", text)
        self.assertIn("head_branch == 'main'", text)
        self.assertIn("TELEGRAM_NOTIFICATION_CHAT_ID", text)
        self.assertIn("MOBILE_DASHBOARD_KEY", text)
        self.assertIn("--cards-only", text)

    def test_every_pages_builder_receives_the_mobile_encryption_key(self):
        root = Path(__file__).parents[1] / ".github" / "workflows"
        expected_counts = {
            "daily-codex-analysis.yml": 1,
            "intraday-overlay-refresh.yml": 1,
            "account-portfolio-report-verify.yml": 4,
            "daily-youtube-reports.yml": 1,
            "daily-prism-telegram-reports.yml": 1,
        }
        assignment = (
            "TRADINGAGENTS_MOBILE_DASHBOARD_KEY: "
            "${{ secrets.MOBILE_DASHBOARD_KEY }}"
        )
        for filename, expected in expected_counts.items():
            text = (root / filename).read_text(encoding="utf-8")
            self.assertEqual(text.count(assignment), expected, filename)


if __name__ == "__main__":
    unittest.main()
