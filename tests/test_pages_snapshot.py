from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest


SCRIPT = Path(__file__).parents[1] / ".github" / "scripts" / "pages_snapshot.py"
WORKFLOWS = Path(__file__).parents[1] / ".github" / "workflows"
SPEC = importlib.util.spec_from_file_location("pages_snapshot", SCRIPT)
assert SPEC and SPEC.loader
pages_snapshot = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pages_snapshot)


def test_guard_cli_loads_without_project_installation(tmp_path: Path) -> None:
    standalone = tmp_path / "pages_snapshot.py"
    standalone.write_text(SCRIPT.read_text(encoding="utf-8"), encoding="utf-8")

    result = subprocess.run(
        [sys.executable, "-I", "-S", str(standalone), "guard", "--help"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr


def _strategy_payload(site: Path) -> None:
    mobile = site / "mobile"
    mobile.mkdir(parents=True)
    (mobile / "private.html").write_text("private", encoding="utf-8")
    (mobile / "private.js").write_text("private", encoding="utf-8")
    (mobile / "strategy.json").write_text(
        json.dumps(
            {
                "schema": "tradingagents.mobile-strategy/v1",
                "markets": {"kr": {}},
            }
        ),
        encoding="utf-8",
    )


def test_stamp_requires_plaintext_mobile_strategy_payload(tmp_path: Path) -> None:
    site = tmp_path / "site"
    site.mkdir()
    (site / "index.html").write_text("ok", encoding="utf-8")

    with pytest.raises(ValueError, match="mobile strategy artifact"):
        pages_snapshot.create_snapshot(
            site,
            repository="owner/repo",
            workflow="Daily",
            run_id=10,
            run_attempt=1,
            commit_sha="abc",
            generated_epoch_ms=1000,
            require_strategy_payload=True,
        )

    _strategy_payload(site)
    snapshot = pages_snapshot.create_snapshot(
        site,
        repository="owner/repo",
        workflow="Daily",
        run_id=10,
        run_attempt=1,
        commit_sha="abc",
        generated_epoch_ms=1000,
        require_strategy_payload=True,
    )

    assert snapshot["generated_epoch_ms"] == 1000
    assert json.loads((site / "pages-snapshot.json").read_text(encoding="utf-8"))["run_id"] == 10


def test_snapshot_guard_refuses_older_or_duplicate_snapshot() -> None:
    candidate = {
        "schema": pages_snapshot.SNAPSHOT_SCHEMA,
        "generated_epoch_ms": 2000,
        "run_id": 20,
        "run_attempt": 1,
    }
    newer_live = {**candidate, "generated_epoch_ms": 3000, "run_id": 30}
    duplicate_live = dict(candidate)

    assert pages_snapshot.should_deploy(candidate, None)[0] is True
    assert pages_snapshot.should_deploy(candidate, newer_live)[0] is False
    assert pages_snapshot.should_deploy(candidate, duplicate_live)[0] is False


def test_snapshot_guard_breaks_equal_timestamp_tie_by_run_attempt() -> None:
    live = {
        "schema": pages_snapshot.SNAPSHOT_SCHEMA,
        "generated_epoch_ms": 2000,
        "run_id": 20,
        "run_attempt": 1,
    }
    candidate = {**live, "run_attempt": 2}

    assert pages_snapshot.should_deploy(candidate, live)[0] is True


def test_stamp_rejects_obsolete_encrypted_payload(tmp_path: Path) -> None:
    site = tmp_path / "site"
    site.mkdir()
    (site / "index.html").write_text("ok", encoding="utf-8")
    _strategy_payload(site)
    (site / "mobile" / "private.enc.json").write_text("{}", encoding="utf-8")

    with pytest.raises(ValueError, match="obsolete mobile artifact"):
        pages_snapshot.create_snapshot(
            site,
            repository="owner/repo",
            workflow="Daily",
            run_id=10,
            run_attempt=1,
            commit_sha="abc",
            require_strategy_payload=True,
        )


def test_stamp_rejects_raw_account_identifier_in_strategy_payload(tmp_path: Path) -> None:
    site = tmp_path / "site"
    site.mkdir()
    (site / "index.html").write_text("ok", encoding="utf-8")
    _strategy_payload(site)
    strategy_path = site / "mobile" / "strategy.json"
    payload = json.loads(strategy_path.read_text(encoding="utf-8"))
    payload["markets"]["kr"]["account_id"] = "RAW-123456"
    strategy_path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="Forbidden account identifier"):
        pages_snapshot.create_snapshot(
            site,
            repository="owner/repo",
            workflow="Daily",
            run_id=10,
            run_attempt=1,
            commit_sha="abc",
            require_strategy_payload=True,
        )


@pytest.mark.parametrize(
    "workflow_name",
    (
        "daily-codex-analysis.yml",
        "intraday-overlay-refresh.yml",
        "account-portfolio-report-verify.yml",
        "daily-youtube-reports.yml",
        "daily-prism-telegram-reports.yml",
        "work-report-pages-refresh.yml",
    ),
)
def test_pages_workflows_stamp_strategy_snapshot_and_guard_deploy(workflow_name: str) -> None:
    text = (WORKFLOWS / workflow_name).read_text(encoding="utf-8")

    assert "pages_snapshot.py" in text
    assert '"--require-strategy-payload"' in text
    assert "Refuse stale Pages snapshot rollback" in text
    assert "steps.pages_guard.outputs.should_deploy == 'true'" in text
    assert "actions/deploy-pages@v5" not in text


def test_account_all_explicitly_selects_final_us_merged_snapshot() -> None:
    text = (WORKFLOWS / "account-portfolio-report-verify.yml").read_text(encoding="utf-8")

    assert 'elif profile in {"us", "all"}:' in text
    assert 'artifact = "account-performance-pages-us"' in text
    assert "steps.select_account_snapshot.outputs.artifact_name" in text
