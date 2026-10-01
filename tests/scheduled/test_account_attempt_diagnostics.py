from __future__ import annotations

import json

import pytest

from tradingagents.scheduled.account_site import _latest_public_market_snapshot
from tradingagents.scheduled.ai_context import public_context, render_payload


def add_run(root, name, stamp, *, health="VALID", snapshot=True, portfolio_status="success", account_stamp=None):
    directory = root / name
    private = directory / "portfolio-private"
    private.mkdir(parents=True)
    if snapshot:
        (private / "account_snapshot.json").write_text(json.dumps({
            "snapshot_health": health, "as_of": account_stamp or stamp,
            "account_id": "PRIVATE-ACCOUNT", "snapshot_id": "PRIVATE-SNAPSHOT",
            "warnings": ["PRIVATE-WARNING"], "positions": [], "total_equity_krw": 123,
        }))
    return {"_run_dir": str(directory), "run_id": name, "settings": {"market": "US"},
            "started_at": stamp, "finished_at": stamp,
            "portfolio": {"status": portfolio_status, "error": "PRIVATE-ERROR"}}


@pytest.mark.parametrize("health", ["CAPITAL_CONSTRAINED", "INVALID_SNAPSHOT", "WATCHLIST_ONLY"])
def test_new_nonvalid_attempt_does_not_replace_valid_account(tmp_path, health):
    old = add_run(tmp_path, "old", "2026-01-01T10:00:00+00:00")
    new = add_run(tmp_path, "new", "2026-01-01T11:00:00+00:00", health=health)
    result = _latest_public_market_snapshot([old, new], market="us")
    assert result["run_id"] == "old"
    assert result["snapshot_health"] == "VALID"
    assert result["as_of"] == old["started_at"]
    assert result["latest_attempt"] == {
        "status": health, "account_as_of": new["started_at"],
        "run_started_at": new["started_at"], "run_finished_at": new["finished_at"],
        "selected_for_public_account": False,
    }
    assert "PRIVATE" not in json.dumps(result)


@pytest.mark.parametrize("portfolio_status,expected", [
    ("failed", "PIPELINE_FAILED"), ("skipped", "PIPELINE_SKIPPED"),
    ("disabled", "PIPELINE_DISABLED"), ("unknown-private-value", "SNAPSHOT_NOT_PUBLISHED"),
])
def test_missing_snapshot_reports_only_sanitized_pipeline_status(tmp_path, portfolio_status, expected):
    old = add_run(tmp_path, "old", "2026-01-01T10:00:00+00:00")
    new = add_run(tmp_path, "new", "2026-01-01T11:00:00+00:00", snapshot=False, portfolio_status=portfolio_status)
    result = _latest_public_market_snapshot([new, old], market="us")
    assert result["snapshot_health"] == "VALID"
    assert result["latest_attempt"]["status"] == expected
    assert result["latest_attempt"]["account_as_of"] is None
    assert "PRIVATE" not in json.dumps(result)
    assert "unknown-private-value" not in json.dumps(result)


def test_no_valid_account_remains_unavailable(tmp_path):
    new = add_run(tmp_path, "new", "2026-01-01T11:00:00+00:00", health="CAPITAL_CONSTRAINED")
    result = _latest_public_market_snapshot([new], market="us")
    assert result["status"] == "unavailable"
    assert result["snapshot_health"] == "UNAVAILABLE"
    assert result["as_of"] is None and result["positions"] == []
    assert result["latest_attempt"]["status"] == "CAPITAL_CONSTRAINED"
    assert result["latest_attempt"]["selected_for_public_account"] is False


def test_latest_pipeline_completion_does_not_refresh_account_clock(tmp_path):
    old = add_run(tmp_path, "old", "2026-01-01T11:00:00+00:00")
    later = add_run(tmp_path, "later", "2026-01-01T12:00:00+00:00", account_stamp="2026-01-01T10:00:00+00:00")
    result = _latest_public_market_snapshot([later, old], market="us")
    assert result["run_id"] == "old" and result["as_of"] == old["started_at"]
    assert result["latest_attempt"]["account_as_of"] == "2026-01-01T10:00:00+00:00"
    assert result["latest_attempt"]["run_finished_at"] == "2026-01-01T12:00:00+00:00"
    assert result["latest_attempt"]["selected_for_public_account"] is False


def test_unknown_health_and_invalid_clock_are_not_disclosed_verbatim(tmp_path):
    unknown = add_run(tmp_path, "unknown", "2026-01-01T11:00:00+00:00", health="PRIVATE-HEALTH")
    result = _latest_public_market_snapshot([unknown], market="us")
    assert result["latest_attempt"]["status"] == "UNVERIFIED_HEALTH"
    assert "PRIVATE" not in json.dumps(result)
    invalid = add_run(tmp_path, "invalid", "2026-01-01T12:00:00+00:00", account_stamp="PRIVATE-CLOCK")
    result = _latest_public_market_snapshot([invalid], market="us")
    assert result["latest_attempt"]["status"] == "UNVERIFIED_ACCOUNT_CLOCK"
    assert result["latest_attempt"]["account_as_of"] is None


def test_compact_json_and_txt_project_diagnostic_without_private_extensions(tmp_path):
    old = add_run(tmp_path, "old", "2026-01-01T10:00:00+00:00")
    new = add_run(tmp_path, "new", "2026-01-01T11:00:00+00:00", health="CAPITAL_CONSTRAINED")
    account = _latest_public_market_snapshot([new, old], market="us")
    account["latest_attempt"].update(account_id="PRIVATE-ACCOUNT", error="PRIVATE-ERROR")
    payload = public_context("us", {}, account, {}, generated_at="2026-01-01T12:00:00Z")
    assert payload["account"]["as_of"] == old["started_at"]
    assert payload["account"]["snapshot_health"] == "VALID"
    assert payload["account"]["latest_attempt"]["status"] == "CAPITAL_CONSTRAINED"
    assert "PRIVATE" not in json.dumps(payload)
    rendered = render_payload(payload)
    assert "CAPITAL_CONSTRAINED" in rendered and "PRIVATE" not in rendered
