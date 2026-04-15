from pathlib import Path
from unittest.mock import patch

from tradingagents.llm_clients.codex_app_server import CodexAppServerSession


def test_codex_app_server_sets_isolated_codex_home(tmp_path: Path):
    workspace = tmp_path / "workspace"
    captured: dict[str, object] = {}

    class _FakeProc:
        stdin = None
        stdout = None
        stderr = None

    def _fake_popen(*args, **kwargs):
        captured["args"] = args
        captured["kwargs"] = kwargs
        return _FakeProc()

    with (
        patch("tradingagents.llm_clients.codex_app_server.resolve_codex_binary", return_value="codex"),
        patch("tradingagents.llm_clients.codex_app_server.subprocess.Popen", side_effect=_fake_popen),
        patch.object(CodexAppServerSession, "_start_reader_threads", return_value=None),
        patch.object(CodexAppServerSession, "_initialize", return_value=None),
    ):
        session = CodexAppServerSession(
            codex_binary="codex",
            request_timeout=30,
            workspace_dir=str(workspace),
            cleanup_threads=True,
        )
        session.start()

    env = captured["kwargs"]["env"]
    assert "CODEX_HOME" in env
    assert str(workspace / ".codex-home") == env["CODEX_HOME"]
