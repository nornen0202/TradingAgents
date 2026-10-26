"""Fake processes and plain fixture files only; never start Codex or SQLite."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from types import SimpleNamespace
import subprocess
import tomllib

import pytest

from tradingagents.llm_clients import codex_app_server as server


class FakeProc:
    def __init__(self, *, stubborn=False):
        self.stdin = SimpleNamespace(close=lambda: None)
        self.running = True
        self.stubborn = stubborn

    def terminate(self):
        if not self.stubborn:
            self.running = False

    def kill(self):
        if not self.stubborn:
            self.running = False

    def wait(self, timeout=None):
        if self.running:
            raise subprocess.TimeoutExpired("fake-only", timeout)
        return 0

    def poll(self):
        return None if self.running else 0


@pytest.fixture(autouse=True)
def no_live_codex(monkeypatch):
    launches = []
    monkeypatch.setattr(server.os, "environ", {})
    monkeypatch.setattr(server, "resolve_codex_binary", lambda _: "fake-codex")
    monkeypatch.setattr(server.CodexAppServerSession, "_source_codex_home", staticmethod(lambda: None))
    monkeypatch.setattr(server.CodexAppServerSession, "_start_reader_threads", lambda _: None)
    monkeypatch.setattr(server.CodexAppServerSession, "_initialize", lambda _: None)
    def spawn(args, **kwargs):
        proc = FakeProc()
        launches.append((args, kwargs, proc))
        return proc
    monkeypatch.setattr(server.subprocess, "Popen", spawn)
    return launches


def session(workspace):
    return server.CodexAppServerSession(codex_binary="fake", request_timeout=30,
                                        workspace_dir=str(workspace), cleanup_threads=True)


def test_three_same_workspace_roles_get_distinct_sqlite_scopes(tmp_path, no_live_codex):
    workspace = tmp_path / "workspace"
    roles = [session(workspace) for _ in range(3)]
    with ThreadPoolExecutor(max_workers=3) as pool:
        list(pool.map(lambda s: s.start(), roles))
    assert len({s._sqlite_home for s in roles}) == 3
    assert len(no_live_codex) == 3
    for args, kwargs, proc in no_live_codex:
        home = Path(kwargs["env"]["CODEX_SQLITE_HOME"])
        assert home.is_dir() and home.parent == workspace / ".codex-home"
        assert kwargs["env"]["CODEX_HOME"] == str(workspace / ".codex-home")
        assert args[:4] == ["fake-codex", "app-server", "--listen", "stdio://"]
        assert args[4] == "-c" and tomllib.loads(args[5]) == {"sqlite_home": str(home)}
        assert proc.running
    for s in roles:
        s.close()


def test_existing_seed_and_inherited_sqlite_setting_are_not_rewritten(tmp_path, monkeypatch, no_live_codex):
    source = tmp_path / "fixture-source"
    source.mkdir()
    seed = {"auth.json": b'{"fixture":"not-a-credential"}',
            "config.toml": b'sqlite_home = "Z:/fixture-legacy"\nmodel = "fixture-model"\n'}
    for name, content in seed.items():
        (source / name).write_bytes(content)
    monkeypatch.setattr(server.CodexAppServerSession, "_source_codex_home", staticmethod(lambda: source))
    monkeypatch.setenv("CODEX_SQLITE_HOME", "Z:/fixture-inherited")
    s = session(tmp_path / "workspace")
    s.start()
    for name, content in seed.items():
        assert (source / name).read_bytes() == content
        assert (s._codex_home / name).read_bytes() == content
    args, kwargs, _ = no_live_codex[0]
    assert tomllib.loads(args[5])["sqlite_home"] == kwargs["env"]["CODEX_SQLITE_HOME"] == str(s._sqlite_home)
    s.close()


def test_start_reuses_live_process_but_restart_allocates_a_new_scope(tmp_path, no_live_codex):
    s = session(tmp_path / "workspace")
    s.start()
    old = s._sqlite_home
    s.start()
    assert len(no_live_codex) == 1 and s._sqlite_home == old
    s.close()
    s.start()
    assert len(no_live_codex) == 2 and s._sqlite_home != old and old.is_dir()
    s.close()


def test_close_only_prunes_own_logs_after_exit_and_preserves_other_session_and_legacy(tmp_path):
    a, b = session(tmp_path / "workspace"), session(tmp_path / "workspace")
    a.start()
    b.start()
    paths = [a._sqlite_home / "logs_5.sqlite", a._sqlite_home / "logs_5.sqlite-wal",
             a._sqlite_home / "state_5.sqlite", b._sqlite_home / "logs_5.sqlite",
             a._codex_home / "logs_5.sqlite", a._codex_home / "state_5.sqlite"]
    for path in paths:
        path.write_bytes(b"plain fixture, not a SQLite database")
    a.close()
    assert not paths[0].exists() and not paths[1].exists()
    assert all(p.read_bytes() == b"plain fixture, not a SQLite database" for p in paths[2:])
    assert b._proc.running
    a.close()  # A late repeated close cannot prune B or the shared legacy home.
    assert paths[3].exists() and paths[4].exists()
    b.close()
    assert paths[4].exists() and paths[5].exists()


def test_unconfirmed_termination_retains_process_and_all_logs(tmp_path, monkeypatch):
    proc = FakeProc(stubborn=True)
    monkeypatch.setattr(server.subprocess, "Popen", lambda *a, **k: proc)
    s = session(tmp_path / "workspace")
    s.start()
    log = s._sqlite_home / "logs_5.sqlite"
    log.write_bytes(b"plain fixture")
    s.close()
    assert s._proc is proc and proc.running and log.read_bytes() == b"plain fixture"


@pytest.mark.parametrize("stage", ["popen", "initialize"])
def test_start_failure_never_prunes_unowned_files(tmp_path, monkeypatch, stage):
    workspace = tmp_path / "workspace"
    legacy = workspace / ".codex-home"
    legacy.mkdir(parents=True)
    keep = legacy / "logs_5.sqlite"
    keep.write_bytes(b"plain legacy fixture")
    s = session(workspace)
    if stage == "popen":
        def fail(*a, **k):
            raise OSError("fake spawn failed")
        monkeypatch.setattr(server.subprocess, "Popen", fail)
        expected = server.CodexAppServerBinaryError
    else:
        def fail(*a, **k):
            raise server.CodexAppServerError("fake initialize failed")
        monkeypatch.setattr(server.CodexAppServerSession, "_initialize", fail)
        expected = server.CodexAppServerError
    with pytest.raises(expected):
        s.start()
    s.close()
    assert keep.read_bytes() == b"plain legacy fixture"


@pytest.mark.parametrize("text", ["", "bad\npath", "bad\x00path", "../escape"])
def test_invalid_workspace_path_is_rejected_before_launch(text, no_live_codex):
    with pytest.raises(server.CodexAppServerStorageError):
        session(text)
    assert not no_live_codex


def test_toml_quote_preserves_windows_escapes_without_argument_injection(tmp_path, no_live_codex, monkeypatch):
    # A Unicode directory is real; a quoted Windows representation is checked
    # by the same JSON/TOML serialization without creating an invalid filename.
    s = session(tmp_path / "한글 space")
    s.start()
    args = no_live_codex[0][0]
    assert tomllib.loads(args[5])["sqlite_home"] == str(s._sqlite_home)
    import json
    value = 'G:\\fixture\\quoted"name\\sqlite-session'
    assert tomllib.loads("sqlite_home=" + json.dumps(value, ensure_ascii=False))["sqlite_home"] == value
    s.close()


def test_replaced_scope_identity_cannot_prune_replacement(tmp_path):
    s = session(tmp_path / "workspace")
    s.start()
    home = s._sqlite_home
    home.rename(home.with_name(home.name + "-retained"))
    home.mkdir()
    foreign = home / "logs_5.sqlite"
    foreign.write_bytes(b"replacement fixture")
    s.close()
    assert foreign.read_bytes() == b"replacement fixture"


def test_reparse_attributes_are_rejected_before_launch(tmp_path, monkeypatch, no_live_codex):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    original = Path.lstat
    def attrs(path):
        if path == workspace:
            return SimpleNamespace(st_file_attributes=0x400, st_mode=original(path).st_mode)
        return original(path)
    s = session(workspace)
    monkeypatch.setattr(Path, "lstat", attrs)
    with pytest.raises(server.CodexAppServerStorageError):
        s.start()
    assert not no_live_codex


def test_file_symlink_or_junction_home_is_refused(tmp_path, no_live_codex):
    workspace, external = tmp_path / "workspace", tmp_path / "external"
    workspace.mkdir()
    external.mkdir()
    try:
        (workspace / ".codex-home").symlink_to(external, target_is_directory=True)
    except OSError:
        pytest.skip("Native directory symlink permission unavailable")
    with pytest.raises(server.CodexAppServerStorageError):
        session(workspace).start()
    assert not no_live_codex and list(external.iterdir()) == []
