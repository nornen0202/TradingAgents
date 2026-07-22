from __future__ import annotations

import io
import json
import tempfile
import unittest
import urllib.error
from datetime import datetime, timedelta, timezone
from pathlib import Path

from tradingagents.notifications.__main__ import _requires_private_chat
from tradingagents.notifications.telegram import (
    AtomicNotificationLedger,
    NotificationError,
    TelegramBotClient,
    _diagnostic_signature,
    chunk_text,
    compose_notification,
    inspect_workflow_run,
    notification_event_key,
    notification_incident_key,
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
    def test_run_name_template_is_resolved_from_trusted_workflow_path(self):
        result = inspect_workflow_run(
            _run(
                name=(
                    "Intraday Overlay Refresh [profile=kr] [run_mode=overlay_only] "
                    "[request_scope=default_universe] [recovery_source=native]"
                ),
                path=".github/workflows/intraday-overlay-refresh.yml",
            ),
            [
                {"name": "overlay_refresh_kr", "conclusion": "success"},
                {"name": "deploy_overlay", "conclusion": "success"},
            ],
            repository="nornen0202/TradingAgents",
        )

        self.assertEqual(result["workflow_name"], "Intraday Overlay Refresh")
        self.assertTrue(result["should_notify"])

    def test_unknown_workflow_path_cannot_spoof_supported_name(self):
        with self.assertRaisesRegex(NotificationError, "Unsupported upstream workflow"):
            inspect_workflow_run(
                _run(
                    name="Daily Codex Analysis",
                    path=".github/workflows/untrusted.yml",
                ),
                [{"name": "deploy", "conclusion": "success"}],
                repository="nornen0202/TradingAgents",
            )

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

    def test_successful_work_report_handoff_is_silent_but_failure_is_actionable(self):
        success = inspect_workflow_run(
            _run(
                name="Work Report Pages Refresh",
                path=".github/workflows/work-report-pages-refresh.yml",
                event="workflow_dispatch",
                display_title=(
                    "Work Report Pages Refresh [profile=kr] [run_mode=work_report_handoff] "
                    "[request_scope=exact_report] [recovery_source=local_work]"
                ),
            ),
            [{"name": "build_work_report_pages", "conclusion": "success"}, {"name": "deploy", "conclusion": "success"}],
            repository="nornen0202/TradingAgents",
        )
        failure = inspect_workflow_run(
            _run(
                name="Work Report Pages Refresh",
                path=".github/workflows/work-report-pages-refresh.yml",
                event="workflow_dispatch",
                conclusion="failure",
                head_sha="b" * 40,
                display_title=(
                    "Work Report Pages Refresh [profile=kr] [run_mode=work_report_handoff] "
                    "[request_scope=exact_report] [recovery_source=local_work]"
                ),
            ),
            [{"name": "build_work_report_pages", "conclusion": "failure"}],
            repository="nornen0202/TradingAgents",
        )

        self.assertFalse(success["should_notify"])
        self.assertEqual(success["reason"], "successful_silent_handoff")
        self.assertTrue(failure["should_notify"])
        self.assertEqual(failure["reason"], "upstream_failed")
        self.assertEqual(failure["recovery_source"], "local_work")

    def test_superseded_pages_guard_does_not_emit_completion_notification(self):
        result = inspect_workflow_run(
            _run(name="Intraday Overlay Refresh"),
            [
                {"name": "overlay_refresh_us", "conclusion": "success"},
                {
                    "name": "deploy_overlay",
                    "conclusion": "success",
                    "steps": [
                        {"name": "Refuse stale Pages snapshot rollback", "conclusion": "success"},
                        {"name": "Deploy overlay refresh site to GitHub Pages", "conclusion": "skipped"},
                    ],
                },
            ],
            repository="nornen0202/TradingAgents",
        )
        self.assertFalse(result["should_notify"])
        self.assertEqual(result["reason"], "no_work_superseded")

    def test_real_pages_deploy_emits_completion_notification(self):
        result = inspect_workflow_run(
            _run(name="Intraday Overlay Refresh"),
            [
                {"name": "overlay_refresh_us", "conclusion": "success"},
                {
                    "name": "deploy_overlay",
                    "conclusion": "success",
                    "steps": [
                        {"name": "Refuse stale Pages snapshot rollback", "conclusion": "success"},
                        {"name": "Deploy overlay refresh site to GitHub Pages", "conclusion": "success"},
                    ],
                },
            ],
            repository="nornen0202/TradingAgents",
        )
        self.assertTrue(result["should_notify"])
        self.assertEqual(result["reason"], "terminal_job_succeeded")

    def test_failure_notifies_even_when_terminal_job_never_started(self):
        result = inspect_workflow_run(
            _run(conclusion="failure", head_sha=""),
            [{"name": "schedule_gate", "conclusion": "failure"}],
            repository="nornen0202/TradingAgents",
        )
        self.assertTrue(result["should_notify"])
        self.assertEqual(result["reason"], "upstream_failed")

    def test_intraday_recovery_failure_is_eligible_and_matches_native_incident(self):
        recovery = inspect_workflow_run(
            _run(
                name="Intraday Overlay Refresh",
                event="workflow_dispatch",
                conclusion="failure",
                display_title=(
                    "Intraday Overlay Refresh [profile=us] "
                    "[run_mode=overlay_only] [request_scope=default_universe] "
                    "[recovery_source=cloud_watchdog]"
                ),
            ),
            [
                {
                    "name": "overlay_refresh_us",
                    "conclusion": "failure",
                    "steps": [{"name": "Run overlay refresh mode", "conclusion": "failure"}],
                }
            ],
            repository="nornen0202/TradingAgents",
        )
        native = inspect_workflow_run(
            _run(
                name="Intraday Overlay Refresh",
                event="schedule",
                conclusion="failure",
                display_title=(
                    "Intraday Overlay Refresh [profile=us] "
                    "[run_mode=overlay_only] [request_scope=default_universe] "
                    "[recovery_source=native]"
                ),
            ),
            [
                {
                    "name": "overlay_refresh_us",
                    "conclusion": "failure",
                    "steps": [{"name": "Run overlay refresh mode", "conclusion": "failure"}],
                }
            ],
            repository="nornen0202/TradingAgents",
        )

        self.assertTrue(recovery["should_notify"])
        self.assertEqual(recovery["reason"], "upstream_failed")
        self.assertEqual(recovery["recovery_source"], "cloud_watchdog")
        self.assertEqual(recovery["failure_fingerprint"], native["failure_fingerprint"])

    def test_manual_or_distinct_failure_context_gets_a_distinct_fingerprint(self):
        base_title = (
            "Intraday Overlay Refresh [profile=us] [run_mode=overlay_only] "
            "[request_scope=default_universe]"
        )
        automated = inspect_workflow_run(
            _run(
                name="Intraday Overlay Refresh",
                event="schedule",
                conclusion="failure",
                display_title=f"{base_title} [recovery_source=native]",
            ),
            [{"name": "overlay_refresh_us", "conclusion": "failure"}],
            repository="nornen0202/TradingAgents",
        )
        manual = inspect_workflow_run(
            _run(
                name="Intraday Overlay Refresh",
                event="workflow_dispatch",
                conclusion="failure",
                display_title=f"{base_title} [recovery_source=manual]",
            ),
            [{"name": "overlay_refresh_us", "conclusion": "failure"}],
            repository="nornen0202/TradingAgents",
        )
        deploy_failure = inspect_workflow_run(
            _run(
                name="Intraday Overlay Refresh",
                event="workflow_dispatch",
                conclusion="failure",
                display_title=f"{base_title} [recovery_source=cloud_watchdog]",
            ),
            [{"name": "deploy_overlay", "conclusion": "failure"}],
            repository="nornen0202/TradingAgents",
        )

        self.assertNotEqual(automated["failure_fingerprint"], manual["failure_fingerprint"])
        self.assertNotEqual(automated["failure_fingerprint"], deploy_failure["failure_fingerprint"])

    def test_log_signature_deduplicates_same_root_across_runs_but_distinguishes_errors(self):
        title = (
            "Intraday Overlay Refresh [profile=us] [run_mode=overlay_only] "
            "[request_scope=default_universe] [recovery_source=native]"
        )
        jobs = [{"name": "overlay_refresh_us", "conclusion": "failure"}]
        baseline_signature = _diagnostic_signature(
            "2026-07-17T00:00:00Z RuntimeError: OVERLAY_BASELINE_HOLDING_COVERAGE_GAP"
        )
        timeout_signature = _diagnostic_signature(
            "2026-07-17T00:01:00Z TimeoutError: KIS quote request timed out"
        )
        first = inspect_workflow_run(
            _run(id=100, name="Intraday Overlay Refresh", conclusion="failure", display_title=title),
            jobs,
            repository="nornen0202/TradingAgents",
            failure_diagnostics={"job.log": baseline_signature},
        )
        same = inspect_workflow_run(
            _run(id=101, name="Intraday Overlay Refresh", conclusion="failure", display_title=title),
            jobs,
            repository="nornen0202/TradingAgents",
            failure_diagnostics={"job.log": baseline_signature},
        )
        different = inspect_workflow_run(
            _run(id=102, name="Intraday Overlay Refresh", conclusion="failure", display_title=title),
            jobs,
            repository="nornen0202/TradingAgents",
            failure_diagnostics={"job.log": timeout_signature},
        )
        self.assertEqual(first["failure_fingerprint"], same["failure_fingerprint"])
        self.assertNotEqual(first["failure_fingerprint"], different["failure_fingerprint"])

    def test_missing_log_signature_fails_open_per_run(self):
        title = (
            "Intraday Overlay Refresh [profile=us] [run_mode=overlay_only] "
            "[request_scope=default_universe] [recovery_source=native]"
        )
        jobs = [{"name": "overlay_refresh_us", "conclusion": "failure"}]
        first = inspect_workflow_run(
            _run(id=200, name="Intraday Overlay Refresh", conclusion="failure", display_title=title),
            jobs,
            repository="nornen0202/TradingAgents",
        )
        second = inspect_workflow_run(
            _run(id=201, name="Intraday Overlay Refresh", conclusion="failure", display_title=title),
            jobs,
            repository="nornen0202/TradingAgents",
        )
        self.assertNotEqual(first["failure_fingerprint"], second["failure_fingerprint"])
        self.assertEqual(first["failure_context"]["diagnostic_mode"], "run_scoped_fallback")

    def test_intraday_native_failure_keeps_first_root_alert(self):
        result = inspect_workflow_run(
            _run(
                name="Intraday Overlay Refresh",
                event="schedule",
                conclusion="failure",
                display_title=(
                    "Intraday Overlay Refresh [profile=us] [recovery_source=native]"
                ),
            ),
            [{"name": "overlay_refresh_us", "conclusion": "failure"}],
            repository="nornen0202/TradingAgents",
        )

        self.assertTrue(result["should_notify"])
        self.assertEqual(result["reason"], "upstream_failed")
        self.assertEqual(result["recovery_source"], "native")

    def test_unattempted_cancelled_probe_is_no_work(self):
        result = inspect_workflow_run(
            _run(conclusion="cancelled"),
            [{"name": "deploy", "conclusion": "skipped"}],
            repository="nornen0202/TradingAgents",
        )

        self.assertFalse(result["should_notify"])
        self.assertEqual(result["reason"], "no_work_unattempted")

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
                buttons=[[{"text": "private", "url": "https://example.test/?opaque=secret"}]],
                sender=lambda text, _buttons: sent.append(text) or len(sent),
                receipt_metadata={"upstream_run_id": 1},
            )
            second = ledger.deliver(
                event_key="event-1",
                chunks=["private message", "second"],
                buttons=[[{"text": "private", "url": "https://example.test/?opaque=secret"}]],
                sender=lambda *_args: 999,
                receipt_metadata={"upstream_run_id": 1},
            )
            self.assertEqual(first["status"], "SENT")
            self.assertEqual(second["status"], "NOOP")
            self.assertEqual(sent, ["private message", "second"])
            stored = path.read_text(encoding="utf-8")
            self.assertNotIn("private message", stored)
            self.assertNotIn("secret", stored)

    def test_incident_cooldown_sends_first_suppresses_duplicate_and_expires(self):
        with tempfile.TemporaryDirectory() as temp:
            now = [datetime(2026, 7, 17, 0, 0, tzinfo=timezone.utc)]
            sent = []
            ledger = AtomicNotificationLedger(
                Path(temp) / "ledger.json",
                clock=lambda: now[0],
            )

            first = ledger.deliver(
                event_key="run-1",
                incident_key="incident-a",
                incident_cooldown_seconds=3600,
                chunks=["failure one"],
                buttons=None,
                sender=lambda text, _buttons: sent.append(text) or len(sent),
                receipt_metadata={},
            )
            now[0] += timedelta(minutes=30)
            duplicate = ledger.deliver(
                event_key="run-2",
                incident_key="incident-a",
                incident_cooldown_seconds=3600,
                chunks=["same incident, different run"],
                buttons=None,
                sender=lambda text, _buttons: sent.append(text) or len(sent),
                receipt_metadata={},
            )
            now[0] += timedelta(minutes=31)
            reminder = ledger.deliver(
                event_key="run-3",
                incident_key="incident-a",
                incident_cooldown_seconds=3600,
                chunks=["same incident after cooldown"],
                buttons=None,
                sender=lambda text, _buttons: sent.append(text) or len(sent),
                receipt_metadata={},
            )

            self.assertEqual(first["status"], "SENT")
            self.assertEqual(duplicate["reason"], "INCIDENT_COOLDOWN")
            self.assertEqual(reminder["status"], "SENT")
            self.assertEqual(sent, ["failure one", "same incident after cooldown"])
            stored = json.loads((Path(temp) / "ledger.json").read_text(encoding="utf-8"))
            self.assertEqual(stored["incidents"]["incident-a"]["suppressed_count"], 1)

    def test_distinct_incident_is_not_suppressed_inside_cooldown(self):
        with tempfile.TemporaryDirectory() as temp:
            sent = []
            ledger = AtomicNotificationLedger(Path(temp) / "ledger.json")
            for event_key, incident_key in (("run-1", "incident-a"), ("run-2", "incident-b")):
                ledger.deliver(
                    event_key=event_key,
                    incident_key=incident_key,
                    incident_cooldown_seconds=3600,
                    chunks=[incident_key],
                    buttons=None,
                    sender=lambda text, _buttons: sent.append(text) or len(sent),
                    receipt_metadata={},
                )
            self.assertEqual(sent, ["incident-a", "incident-b"])

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
                    incident_key="incident-partial",
                    incident_cooldown_seconds=3600,
                    chunks=["one", "two", "three"],
                    buttons=None,
                    sender=first_sender,
                    receipt_metadata={},
                )

            resumed = []
            result = ledger.deliver(
                event_key="event-2",
                incident_key="incident-partial",
                incident_cooldown_seconds=3600,
                chunks=["one", "two", "three"],
                buttons=None,
                sender=lambda text, _buttons: resumed.append(text) or 20 + len(resumed),
                receipt_metadata={},
            )
            self.assertEqual(result["status"], "SENT")
            self.assertEqual(resumed, ["two", "three"])

    def test_pending_incident_suppresses_a_different_run_until_resume_or_expiry(self):
        with tempfile.TemporaryDirectory() as temp:
            ledger = AtomicNotificationLedger(Path(temp) / "ledger.json")
            with self.assertRaises(NotificationError):
                ledger.deliver(
                    event_key="run-partial",
                    incident_key="incident-partial",
                    incident_cooldown_seconds=3600,
                    chunks=["one", "two"],
                    buttons=None,
                    sender=lambda *_args: (_ for _ in ()).throw(NotificationError("network")),
                    receipt_metadata={},
                )
            duplicate = ledger.deliver(
                event_key="run-next",
                incident_key="incident-partial",
                incident_cooldown_seconds=3600,
                chunks=["same incident"],
                buttons=None,
                sender=lambda *_args: 99,
                receipt_metadata={},
            )
            self.assertEqual(duplicate["reason"], "INCIDENT_COOLDOWN")

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
    def test_only_private_card_content_requires_get_chat_validation(self):
        public = [[{"text": "report", "url": "https://example.test/mobile/"}]]
        self.assertFalse(_requires_private_chat(public, cards_only=False))
        self.assertTrue(_requires_private_chat([], cards_only=True))

    def test_remote_success_includes_plaintext_mobile_strategy_link(self):
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
            )
        urls = [button["url"] for row in buttons for button in row]
        self.assertTrue(chunks)
        self.assertIn("kr", metadata["surfaces"])
        self.assertIn("https://example.test/TradingAgents/mobile/?market=kr", urls)
        self.assertIn("https://example.test/TradingAgents/strategy.html?market=kr", urls)
        self.assertIn("https://example.test/TradingAgents/mobile/strategy.html?market=kr", urls)
        self.assertFalse(any("#" in url for url in urls))

    def test_youtube_uses_existing_mobile_safe_report(self):
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
            )
        urls = [button["url"] for row in buttons for button in row]
        self.assertIn("https://example.test/TradingAgents/youtube/", urls)
        self.assertFalse(any("#" in url for url in urls))

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
                cards_only=True,
            )
            _full_chunks, full_buttons, _full_metadata = compose_notification(
                context,
                archive_dir=archive,
                public_base_url="https://example.test/TradingAgents",
            )
            manifest_path = run_dir / "run.json"
            incomplete_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            incomplete_manifest["active_universe"]["coverage"]["complete"] = False
            manifest_path.write_text(json.dumps(incomplete_manifest), encoding="utf-8")
            blocked_chunks, _blocked_buttons, _blocked_metadata = compose_notification(
                context,
                archive_dir=archive,
                public_base_url="https://example.test/TradingAgents",
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
                cards_only=True,
            )
            incomplete_manifest["github_actions"]["run_id"] = 999
            manifest_path.write_text(json.dumps(incomplete_manifest), encoding="utf-8")
            unmatched_chunks, _unmatched_buttons, unmatched_metadata = compose_notification(
                context,
                archive_dir=archive,
                public_base_url="https://example.test/TradingAgents",
                cards_only=True,
            )
        self.assertIn("005930.KS", "\n".join(chunks))
        self.assertIn("보유/즉시", "\n".join(chunks))
        self.assertEqual(buttons, [])
        self.assertEqual(metadata["run_ids"], [run_dir.name])
        strategy_urls = [
            button["url"]
            for row in full_buttons
            for button in row
            if "strategy.html" in button["url"]
        ]
        self.assertEqual(len(strategy_urls), 2)
        self.assertTrue(all(f"&run={run_dir.name}" in url for url in strategy_urls))
        self.assertNotIn("005930.KS", "\n".join(blocked_chunks))
        self.assertIn("UNIVERSE_INCOMPLETE", "\n".join(blocked_chunks))
        self.assertNotIn("005930.KS", "\n".join(stale_chunks))
        self.assertIn("ROW_NOT_FRESH_IMMEDIATE", "\n".join(stale_chunks))
        self.assertEqual(unmatched_chunks, [])
        self.assertEqual(unmatched_metadata["run_ids"], [])

    def test_plaintext_strategy_link_is_direct(self):
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
            )

        text = "\n".join(chunks)
        urls = [button["url"] for row in buttons for button in row]
        self.assertIn("분석·배포 완료", text)
        self.assertIn("https://example.test/TradingAgents/strategy.html?market=kr", urls)
        self.assertIn("https://example.test/TradingAgents/mobile/strategy.html?market=kr", urls)
        self.assertFalse(any("#" in url for url in urls))

    def test_failure_message_contains_only_failure_context(self):
        context = inspect_workflow_run(
            _run(conclusion="failure"),
            [{"name": "analyze_kr", "conclusion": "failure"}],
            repository="nornen0202/TradingAgents",
        )
        chunks, buttons, _ = compose_notification(
            context,
            archive_dir=Path("missing"),
            public_base_url="https://example.test/TradingAgents",
        )
        rendered = "\n".join(chunks) + json.dumps(buttons)
        self.assertIn("TradingAgents 자동화 FAILURE", rendered)
        self.assertNotIn("private.html", rendered)

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

    def test_incident_key_is_fingerprint_and_destination_scoped(self):
        first = notification_incident_key(
            repository="r/x", failure_fingerprint="a" * 64, chat_id="one"
        )
        second = notification_incident_key(
            repository="r/x", failure_fingerprint="a" * 64, chat_id="one"
        )
        other = notification_incident_key(
            repository="r/x", failure_fingerprint="b" * 64, chat_id="one"
        )
        self.assertEqual(first, second)
        self.assertNotEqual(first, other)
        self.assertEqual(
            notification_incident_key(
                repository="r/x", failure_fingerprint="invalid", chat_id="one"
            ),
            "",
        )


class WorkflowDefinitionTests(unittest.TestCase):
    def test_central_workflow_is_remote_safe_and_secret_scoped(self):
        path = Path(__file__).parents[1] / ".github" / "workflows" / "tradingagents-mobile-notifications.yml"
        text = path.read_text(encoding="utf-8")
        self.assertIn("workflow_run:", text)
        self.assertIn("runs-on: ubuntu-latest", text)
        self.assertIn("head_repository.full_name == github.repository", text)
        self.assertIn("head_branch == 'main'", text)
        self.assertIn("TELEGRAM_NOTIFICATION_CHAT_ID", text)
        self.assertNotIn("MOBILE_DASHBOARD_KEY", text)
        self.assertIn("--cards-only", text)
        self.assertIn("group: tradingagents-mobile-notification-ledger", text)
        self.assertIn("actions/cache/restore@55cc8345863c7cc4c66a329aec7e433d2d1c52a9", text)
        self.assertIn("actions/cache/save@55cc8345863c7cc4c66a329aec7e433d2d1c52a9", text)
        self.assertIn("if: ${{ always() }}", text)
        self.assertIn("telegram-notification-ledger-v1-", text)
        private_job = text.split("  notify_private_cards:", 1)[1]
        setup = private_job.index("      - name: Set up Python")
        send = private_job.index(
            "      - name: Send private action-card continuation when available"
        )
        self.assertLess(setup, send)
        self.assertIn(
            "uses: actions/setup-python@ece7cb06caefa5fff74198d8649806c4678c61a1",
            private_job[setup:send],
        )

    def test_intraday_and_notification_workflows_use_direct_strategy_payload(self):
        root = Path(__file__).parents[1] / ".github" / "workflows"
        for filename in (
            "intraday-overlay-refresh.yml",
            "tradingagents-mobile-notifications.yml",
        ):
            text = (root / filename).read_text(encoding="utf-8")
            self.assertNotIn("MOBILE_DASHBOARD_KEY", text, filename)
        intraday = (root / "intraday-overlay-refresh.yml").read_text(encoding="utf-8")
        self.assertIn("--require-strategy-payload", intraday)

    def test_intraday_recovery_sources_and_local_retry_budget_are_explicit(self):
        root = Path(__file__).parents[1]
        workflow = (root / ".github" / "workflows" / "intraday-overlay-refresh.yml").read_text(
            encoding="utf-8"
        )
        local_dispatcher = (root / "tools" / "dispatch_intraday_overlay.ps1").read_text(
            encoding="utf-8"
        )

        self.assertIn("[recovery_source=${{", workflow)
        self.assertIn("TRADINGAGENTS_RECOVERY_SOURCE", workflow)
        self.assertIn("cloud_watchdog", workflow)
        self.assertIn("local_watchdog", workflow)
        self.assertIn("--require-strategy-payload", workflow)
        self.assertIn("MaxIdenticalFailedAttempts", local_dispatcher)
        self.assertIn("FailureCooldownMinutes", local_dispatcher)
        self.assertIn("recovery_source=local_watchdog", local_dispatcher)
        self.assertIn('$eligibleProfiles = if ($Profile -eq "all") { @("kr", "us") }', local_dispatcher)
        self.assertIn("$_ -notin $exhaustedProfiles", local_dispatcher)
        self.assertIn("foreach ($dispatchProfile in $eligibleProfiles)", local_dispatcher)
        self.assertIn('"profile=$dispatchProfile"', local_dispatcher)
        self.assertNotIn('"profile=$Profile",', local_dispatcher)
        self.assertIn("Get-FailureDiagnosticSignature", local_dispatcher)
        self.assertIn('"diagnostic=unavailable"', local_dispatcher)
        self.assertIn("$activeRuns = @($allRuns | Where-Object", local_dispatcher)
        self.assertIn("regardless_of_age=true", local_dispatcher)
        self.assertIn("$activeCoverage", local_dispatcher)
        self.assertIn("$parsedRuns = $runsJson | ConvertFrom-Json", local_dispatcher)
        self.assertIn("$allRuns = @($parsedRuns)", local_dispatcher)
        self.assertNotIn("$allRuns = @($runsJson | ConvertFrom-Json)", local_dispatcher)
        self.assertNotIn(
            'return (Get-RunRecoverySource -Run $Run) -ne "manual"',
            local_dispatcher,
        )
        self.assertIn('(Get-RunRecoverySource -Run $_) -ne "manual"', local_dispatcher)


if __name__ == "__main__":
    unittest.main()
