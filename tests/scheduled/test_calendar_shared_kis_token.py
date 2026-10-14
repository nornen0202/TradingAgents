from datetime import datetime, timedelta, timezone
from contextlib import contextmanager
import json
from pathlib import Path
import subprocess
import sys
from unittest.mock import Mock

import pytest
import requests

from tradingagents.portfolio import kis
from tradingagents.scheduled.automation_calendar import (
    SEOUL,
    automated_market_session_status,
)


class HolidayResponse:
    def __init__(self, payload):
        self.payload = payload

    def read(self):
        return json.dumps(self.payload).encode("utf-8")

    def close(self):
        pass


@pytest.mark.parametrize("near_expiry_cache", [False, True])
def test_calendar_then_account_issue_only_one_token(tmp_path, monkeypatch, near_expiry_cache):
    """The broker rejects a second token issue within the same minute."""
    now = datetime.now(SEOUL)
    token_path = tmp_path / "shared-token.json"
    if near_expiry_cache:
        token_path.write_text(json.dumps({
            "access_token": "old-token",
            "expires_at": (datetime.now(timezone.utc) + timedelta(minutes=10)).isoformat(),
        }), encoding="utf-8")
    monkeypatch.setenv("TRADINGAGENTS_KIS_MARKET_CALENDAR_ENABLED", "1")
    monkeypatch.setenv("KIS_APP_KEY", "test-key")
    monkeypatch.setenv("KIS_APP_SECRET", "test-secret")
    monkeypatch.setenv("KIS_TOKEN_FILE_CACHE_ENABLED", "1")
    monkeypatch.delenv("KIS_BASE_URL", raising=False)
    monkeypatch.setattr(kis, "_default_token_cache_path", lambda **_: token_path)
    issues = []

    def issue(*_args, **_kwargs):
        issues.append(True)
        response = requests.Response()
        response.url = kis.REAL_BASE_URL + "/oauth2/tokenP"
        response.status_code = 200 if len(issues) == 1 else 403
        response._content = json.dumps(
            {"access_token": "shared-token", "expires_in": 86400}
            if len(issues) == 1 else {"error_code": "EGW00133"}
        ).encode("utf-8")
        return response

    session = Mock()
    session.post.side_effect = issue
    monkeypatch.setattr(kis.requests, "Session", lambda: session)

    def opener(request, **_kwargs):
        if request.full_url.endswith("/oauth2/tokenP"):
            # Reproduce the previous calendar's independent authentication path.
            return HolidayResponse(issue().json())
        assert request.get_header("Authorization") == "Bearer shared-token"
        assert request.get_method() == "GET"
        return HolidayResponse({"rt_cd": "0", "output": [
            {"bass_dt": now.strftime("%Y%m%d"), "opnd_yn": "Y"},
        ]})

    status = automated_market_session_status(
        "kr", now, cache_path=tmp_path / "calendar.json", opener=opener,
    )
    assert status.is_session is True
    account_client = kis.KisClient(app_key="test-key", app_secret="test-secret")
    assert account_client.ensure_access_token() == "shared-token"
    assert len(issues) == 1
    assert "shared-token" not in (tmp_path / "calendar.json").read_text(encoding="utf-8")


@pytest.mark.parametrize("failure", ["http_403", "refresh_lock", "token_persist"])
def test_shared_token_failure_keeps_calendar_closed(tmp_path, monkeypatch, failure):
    monkeypatch.setenv("TRADINGAGENTS_KIS_MARKET_CALENDAR_ENABLED", "1")
    monkeypatch.setenv("KIS_APP_KEY", "test-key")
    monkeypatch.setenv("KIS_APP_SECRET", "test-secret")
    monkeypatch.setenv("KIS_TOKEN_FILE_CACHE_ENABLED", "1")
    monkeypatch.delenv("KIS_BASE_URL", raising=False)
    monkeypatch.setattr(kis, "_default_token_cache_path", lambda **_: tmp_path / "token.json")
    response = requests.Response()
    response.status_code = 403 if failure == "http_403" else 200
    response._content = json.dumps({"access_token": "token", "expires_in": 86400}).encode()
    session = Mock()
    session.post.return_value = response
    monkeypatch.setattr(kis.requests, "Session", lambda: session)

    def storage_failure(*_a, **_k):
        raise OSError("test storage unavailable")

    @contextmanager
    def lock_failure(*_a, **_k):
        raise OSError("test refresh lock unavailable")
        yield

    if failure == "refresh_lock":
        monkeypatch.setattr(kis, "interprocess_file_lock", lock_failure)
    if failure == "token_persist":
        monkeypatch.setattr(kis, "atomic_write_json", storage_failure)
    opener = Mock(side_effect=AssertionError("holiday read must not run without a shared token"))
    path = tmp_path / "calendar.json"
    status = automated_market_session_status("kr", datetime.now(SEOUL), cache_path=path, opener=opener)
    assert status.is_session is None
    assert status.source == "kis_official_unavailable"
    assert not path.exists()
    opener.assert_not_called()


def test_calendar_rejects_redirected_token_destination(tmp_path, monkeypatch):
    monkeypatch.setenv("TRADINGAGENTS_KIS_MARKET_CALENDAR_ENABLED", "1")
    monkeypatch.setenv("KIS_APP_KEY", "test-key")
    monkeypatch.setenv("KIS_APP_SECRET", "test-secret")
    monkeypatch.setenv("KIS_BASE_URL", "https://unexpected.invalid")
    opener = Mock(side_effect=AssertionError("credentials must not leave the official endpoint"))
    status = automated_market_session_status(
        "kr", datetime.now(SEOUL), cache_path=tmp_path / "calendar.json", opener=opener,
    )
    assert status.is_session is None
    opener.assert_not_called()


def test_cached_calendar_token_needs_no_cli_or_llm_stack(tmp_path):
    path = tmp_path / "token.json"
    path.write_text(json.dumps({
        "access_token": "test-cached-token",
        "expires_at": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
    }), encoding="utf-8")
    code = '''
import os, sys
from pathlib import Path
os.environ["KIS_TOKEN_FILE_CACHE_ENABLED"] = "1"
from tradingagents.scheduled.automation_calendar import _shared_kis_access_token
from tradingagents.portfolio import kis
kis._default_token_cache_path = lambda **_: Path(sys.argv[1])
assert _shared_kis_access_token(("test-key", "test-secret"), timeout=8) == "test-cached-token"
assert "cli.utils" not in sys.modules
assert "langchain_core" not in sys.modules
assert "tradingagents.agents" not in sys.modules
assert "tradingagents.portfolio.pipeline" not in sys.modules
'''
    result = subprocess.run([sys.executable, "-c", code, str(path)], capture_output=True, text=True, timeout=20)
    assert result.returncode == 0, result.stderr


def test_calendar_workflows_install_shared_token_http_dependency():
    for workflow in ["daily-codex-analysis", "intraday-overlay-refresh", "scheduled-actions-watchdog"]:
        source = (Path(".github/workflows") / f"{workflow}.yml").read_text(encoding="utf-8")
        calendar_install = next(line for line in source.splitlines() if "pip install" in line and "exchange-calendars" in line)
        assert '"requests>=2.32,<3"' in calendar_install


def test_lazy_portfolio_exports_keep_the_pipeline_functions():
    import tradingagents.portfolio as portfolio
    from tradingagents.portfolio import pipeline

    assert portfolio.load_snapshot_for_profile is pipeline.load_snapshot_for_profile
    assert portfolio.run_portfolio_pipeline is pipeline.run_portfolio_pipeline
