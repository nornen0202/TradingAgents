import os
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
        patch.dict(os.environ, {}, clear=True),
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


def test_codex_app_server_seeds_auth_into_isolated_codex_home(tmp_path: Path):
    source_home = tmp_path / "source-home"
    source_home.mkdir()
    (source_home / "auth.json").write_text('{"account":"present"}', encoding="utf-8")
    (source_home / "config.toml").write_text("model = 'gpt-5.5'\n", encoding="utf-8")
    workspace = tmp_path / "workspace"

    class _FakeProc:
        stdin = None
        stdout = None
        stderr = None

    with (
        patch("tradingagents.llm_clients.codex_app_server.resolve_codex_binary", return_value="codex"),
        patch("tradingagents.llm_clients.codex_app_server.subprocess.Popen", return_value=_FakeProc()),
        patch.object(CodexAppServerSession, "_start_reader_threads", return_value=None),
        patch.object(CodexAppServerSession, "_initialize", return_value=None),
        patch.dict(os.environ, {"CODEX_HOME": str(source_home)}, clear=True),
    ):
        session = CodexAppServerSession(
            codex_binary="codex",
            request_timeout=30,
            workspace_dir=str(workspace),
            cleanup_threads=True,
        )
        session.start()

    isolated_home = workspace / ".codex-home"
    assert (isolated_home / "auth.json").read_text(encoding="utf-8") == '{"account":"present"}'
    assert (isolated_home / "config.toml").read_text(encoding="utf-8") == "model = 'gpt-5.5'\n"


def test_codex_app_server_prunes_isolated_home_logs_on_close(tmp_path: Path):
    workspace = tmp_path / "workspace"
    isolated_home = workspace / ".codex-home"
    isolated_home.mkdir(parents=True)
    (isolated_home / "logs_2.sqlite").write_text("log", encoding="utf-8")
    (isolated_home / "logs_2.sqlite-wal").write_text("wal", encoding="utf-8")
    (isolated_home / "auth.json").write_text("{}", encoding="utf-8")

    session = CodexAppServerSession(
        codex_binary="codex",
        request_timeout=30,
        workspace_dir=str(workspace),
        cleanup_threads=True,
    )
    session._codex_home = isolated_home
    session.close()

    assert not (isolated_home / "logs_2.sqlite").exists()
    assert not (isolated_home / "logs_2.sqlite-wal").exists()
    assert (isolated_home / "auth.json").exists()
