from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
from types import SimpleNamespace


SCRIPT = Path(__file__).parents[1] / ".github/scripts/overlay_runner_preflight.py"
SPEC = importlib.util.spec_from_file_location("overlay_runner_preflight", SCRIPT)
preflight = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(preflight)


def test_credentials_are_boolean_only_and_market_scoped():
    env = {name: "do-not-print-this" for name in (
        "KIS_APP_KEY", "KIS_APP_SECRET", "KIS_ACCOUNT_NO", "KIS_PRODUCT_CODE",
    )}
    assert preflight.credential_checks(env, "kr") == {
        "kis_api_configuration_present": True, "kis_account_configuration_present": True,
    }
    assert not preflight.credential_checks(env, "us")["us_market_data_configuration_present"]
    env["POLYGON_API_KEY"] = "do-not-print-this"
    checks = preflight.credential_checks(env, "all")
    assert all(checks.values())
    assert "do-not-print-this" not in json.dumps(checks)
    del env["KIS_APP_SECRET"]
    assert not preflight.credential_checks(env, "kr")["kis_api_configuration_present"]


def test_existing_aliases_and_alpaca_pair_are_supported():
    env = {name: "configured" for name in (
        "KIS_Developers_APP_KEY", "KIS_Developers_APP_SECRET",
        "KIS_Developers_ACCOUNT_NO", "KIS_Developers_PRODUCT_CODE",
        "ALPACA_API_KEY_ID", "ALPACA_SECRET_KEY",
    )}
    assert all(preflight.credential_checks(env, "us").values())
    del env["ALPACA_SECRET_KEY"]
    assert not preflight.credential_checks(env, "us")["us_market_data_configuration_present"]


def test_archive_probe_is_isolated_and_preserves_existing_files(tmp_path):
    account = tmp_path / "account.json"
    account.write_bytes(b"must not be opened or changed")
    checks = preflight.probe_archive(str(tmp_path))
    assert all(checks.values()), checks
    assert list(tmp_path.iterdir()) == [account]
    assert account.read_bytes() == b"must not be opened or changed"


def test_archive_probe_rejects_missing_relative_and_root_paths(tmp_path):
    for raw in ("", "relative/archive", str(Path(tmp_path.anchor)), str(tmp_path / "missing")):
        assert not all(preflight.probe_archive(raw).values())


def test_archive_probe_failure_does_not_disclose_path(monkeypatch, tmp_path):
    def fail(*args, **kwargs):
        raise OSError("secret-path-or-account-value")
    monkeypatch.setattr(preflight.tempfile, "mkdtemp", fail)
    result = preflight.probe_archive(str(tmp_path))
    assert not result["isolated_write"]
    assert "secret" not in json.dumps(result)


def test_codex_status_is_bounded_suppressed_and_does_not_login(monkeypatch, tmp_path):
    binary = tmp_path / "codex.exe"
    binary.write_bytes(b"stub")
    seen = []
    def run(command, **kwargs):
        seen.append((command, kwargs))
        return subprocess.CompletedProcess(command, 0)
    monkeypatch.setattr(preflight.subprocess, "run", run)
    assert all(preflight.probe_codex({"CODEX_BINARY": str(binary)}).values())
    command, kwargs = seen[0]
    assert command[1:] == ["login", "status"]
    assert kwargs["timeout"] == 10
    assert kwargs["stdout"] == kwargs["stderr"] == subprocess.DEVNULL
    assert kwargs["stdin"] == subprocess.DEVNULL


def test_codex_timeout_and_explicit_missing_binary_fail_closed(monkeypatch, tmp_path):
    binary = tmp_path / "codex"
    binary.write_bytes(b"stub")
    def fail(command, **kwargs):
        raise subprocess.TimeoutExpired(command, 10)
    monkeypatch.setattr(preflight.subprocess, "run", fail)
    assert not preflight.probe_codex({"CODEX_BINARY": str(binary)})["codex_login_ready"]
    assert not preflight.probe_codex({"CODEX_BINARY": str(tmp_path / "missing")})["codex_binary_present"]


def test_receipt_never_contains_values_and_fails_on_incomplete_checks(monkeypatch):
    monkeypatch.setattr(preflight, "probe_archive", lambda raw: {"isolated_write": False})
    monkeypatch.setattr(preflight, "probe_codex", lambda env: {"codex_login_ready": True})
    env = {"TRADINGAGENTS_ARCHIVE_DIR": "secret-path", "KIS_APP_KEY": "secret-key"}
    result = preflight.collect_preflight(env, "kr")
    assert result["basic_checks_pass"] is False
    assert result["ready_for_live_routing"] is False
    assert "secret" not in json.dumps(result)
    assert "shared_archive_writer_safety_not_proven" in result["limitations"]


def test_main_returns_nonzero_for_failed_diagnostic(monkeypatch, capsys):
    monkeypatch.setattr(preflight, "collect_preflight", lambda env, market: {"basic_checks_pass": False})
    assert preflight.main(["--market", "us"]) == 1
    assert json.loads(capsys.readouterr().out) == {"basic_checks_pass": False}


def test_basic_success_never_promotes_to_live_routing(monkeypatch):
    monkeypatch.setattr(preflight, "os", SimpleNamespace(name="nt"))
    monkeypatch.setattr(preflight, "probe_archive", lambda raw: {"isolated_write": True})
    monkeypatch.setattr(preflight, "probe_codex", lambda env: {"codex_login_ready": False})
    result = preflight.collect_preflight({}, "all")
    assert result["status"] == "basic_checks_pass"
    assert result["basic_checks_pass"] is True
    assert result["ready_for_live_routing"] is False
    assert result["codex_diagnostics"]["codex_login_ready"] is False
    assert not any(result["configuration_diagnostics"].values())
