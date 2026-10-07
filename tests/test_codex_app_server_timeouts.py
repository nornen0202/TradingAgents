from unittest.mock import patch
from concurrent.futures import ThreadPoolExecutor
from threading import Event

import pytest

from tradingagents.llm_clients.codex_app_server import (
    CodexAppServerError,
    CodexAppServerSession,
    CodexAppServerTimeoutError,
)
from tradingagents.scheduled.failure_diagnostics import failure_diagnostics


def session(timeout=0.02):
    return CodexAppServerSession(
        codex_binary="unused", request_timeout=timeout,
        workspace_dir="unused", cleanup_threads=True,
    )


def test_stale_responses_do_not_starve_ready_turn_notifications():
    client = session()
    first = {"id": "late-response-1", "result": {}}
    second = {"id": "late-response-2", "result": {}}
    client._pending.append(first)
    client._stdout_queue.put(second)
    client._stdout_queue.put({
        "method": "item/completed", "params": {
            "turnId": "turn-1",
            "item": {"type": "agentMessage", "phase": "final_answer", "text": "done"},
        },
    })
    client._stdout_queue.put({
        "method": "turn/completed", "params": {"turn": {"id": "turn-1", "status": "completed"}},
    })

    text, notifications = client._collect_turn("turn-1")

    assert text == "done"
    assert len(notifications) == 2
    assert client._stdout_queue.empty()
    assert not client._pending


def test_stale_responses_are_dropped_even_when_turn_fails():
    client = session()
    response = {"id": "late-response", "result": {}}
    client._pending.append(response)
    client._stdout_queue.put({
        "method": "turn/completed", "params": {
            "turn": {"id": "turn-1", "status": "failed", "error": {"message": "provider failed"}},
        },
    })

    with pytest.raises(CodexAppServerError, match="provider failed"):
        client._collect_turn("turn-1")
    assert not client._pending


def test_tiny_queue_wait_reports_configured_operation_budget():
    client = session(timeout=600)
    with (
        patch.object(client, "_remaining_timeout", return_value=0.003),
        patch.object(client, "_next_message", side_effect=CodexAppServerTimeoutError("0.003s")),
    ):
        with pytest.raises(CodexAppServerTimeoutError, match="Codex turn turn-1 after 600s") as caught:
            client._next_message_before(123, "Codex turn turn-1")
    assert "0.003" not in str(caught.value)
    assert failure_diagnostics(caught.value)["retryability"] == "RETRYABLE"


def test_expired_absolute_deadline_has_typed_timeout():
    client = session(timeout=600)
    with patch("tradingagents.llm_clients.codex_app_server.time.monotonic", return_value=101):
        with pytest.raises(CodexAppServerTimeoutError, match="after 600s"):
            client._remaining_timeout(100, "turn/start")


def test_empty_stdout_queue_times_out_after_dropping_stale_response():
    client = session()
    response = {"id": "late-response", "result": {}}
    client._pending.append(response)
    with pytest.raises(CodexAppServerTimeoutError, match="Codex turn turn-1 after 0.02s"):
        client._collect_turn("turn-1")
    assert not client._pending


def test_native_tool_policy_error_remains_generic_and_fails_fast():
    client = session(timeout=600)
    client._stderr_lines.append('error="pwsh.exe" rejected: blocked by policy')
    with pytest.raises(CodexAppServerError, match="native tool") as caught:
        client._next_message(600)
    assert not isinstance(caught.value, CodexAppServerTimeoutError)


def test_request_discards_stale_replies_and_preserves_early_notifications():
    client = session(timeout=1)
    notification = {"method": "item/completed", "params": {"turnId": "turn-1"}}
    client._pending.append({"id": "old-request", "result": {}})
    client._stdout_queue.put(notification)
    client._stdout_queue.put({"id": "duplicate-old-request", "result": {}})
    client._stdout_queue.put({"id": "current-request", "result": {"ok": True}})
    with (
        patch("tradingagents.llm_clients.codex_app_server.uuid.uuid4", return_value="current-request"),
        patch.object(client, "_write"),
    ):
        assert client.request("turn/start") == {"ok": True}
    assert list(client._pending) == [notification]
    assert client._stdout_queue.empty()


def test_overlapping_rpc_requests_are_serialized_without_losing_replies():
    client = session(timeout=1)
    first_sent, second_started, second_sent, release_first = (Event() for _ in range(4))

    def write(payload):
        if payload["method"] == "first":
            first_sent.set()
            assert release_first.wait(2)
        else:
            second_sent.set()
        client._stdout_queue.put({"id": payload["id"], "result": {"owner": payload["method"]}})

    def second_request():
        second_started.set()
        return client.request("second")

    with patch.object(client, "_write", side_effect=write), ThreadPoolExecutor(max_workers=2) as pool:
        first = pool.submit(client.request, "first")
        try:
            assert first_sent.wait(1)
            second = pool.submit(second_request)
            assert second_started.wait(1)
            assert not second_sent.wait(0.05)
        finally:
            release_first.set()
        assert first.result(timeout=2) == {"owner": "first"}
        assert second.result(timeout=2) == {"owner": "second"}
    assert not client._pending
