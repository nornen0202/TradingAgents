from concurrent.futures import ThreadPoolExecutor, TimeoutError
from threading import Event
from types import SimpleNamespace

from tradingagents.llm_clients.codex_app_server import CodexAppServerError
from tradingagents.llm_clients.codex_chat_model import CodexChatModel


def test_parallel_requests_cannot_take_over_session_during_failure_recovery(monkeypatch, tmp_path):
    retry_started = Event()
    release_retry = Event()
    sibling_started = Event()
    sessions = []
    successful_requests = []

    class Session:
        def __init__(self, **kwargs):
            self.index = len(sessions)
            self.closed = False
            sessions.append(self)

        def start(self):
            pass

        def invoke(self, **kwargs):
            if self.index == 0:
                raise CodexAppServerError("interrupted stdio")
            assert not self.closed
            successful_requests.append(kwargs["prompt"])
            return SimpleNamespace(final_text='{"answer":"The evidence supports holding the position."}', notifications=[])

        def close(self):
            self.closed = True

    def retry_delay(self, attempt):
        retry_started.set()
        assert release_retry.wait(timeout=5)
        return 0

    monkeypatch.setattr(CodexChatModel, "_codex_retry_delay", retry_delay)
    llm = CodexChatModel(
        model="gpt-6-sol", codex_workspace_dir=str(tmp_path), codex_max_retries=1,
        session_factory=Session, preflight_runner=lambda **kwargs: None,
    )

    def sibling():
        sibling_started.set()
        return llm.invoke("second analyst")

    with ThreadPoolExecutor(max_workers=2) as pool:
        first = pool.submit(llm.invoke, "first analyst")
        assert retry_started.wait(timeout=5)
        second = pool.submit(sibling)
        assert sibling_started.wait(timeout=5)
        try:
            try:
                second.result(timeout=0.1)
            except TimeoutError:
                pass
            else:
                raise AssertionError("Sibling bypassed the failed turn's session recovery")
            assert len(sessions) == 1
        finally:
            release_retry.set()
        assert first.result(timeout=5).content == second.result(timeout=5).content
    assert len(sessions) == 2
    assert "first analyst" in successful_requests[0]
    assert "second analyst" in successful_requests[1]
    llm.close()
    assert all(session.closed for session in sessions)
