from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest


MODULE_PATH = Path(".github/scripts/collect_private_account_artifact.py")
SPEC = importlib.util.spec_from_file_location("collect_private_account_artifact", MODULE_PATH)
collector = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = collector
SPEC.loader.exec_module(collector)


def _write_run(
    archive: Path,
    *,
    run_id: str,
    github_run_id: str,
    label: str = "github-actions-kr",
    content: str = "current",
) -> None:
    private = archive / "runs" / run_id[:4] / run_id / "portfolio-private"
    private.mkdir(parents=True)
    (private / "account_snapshot.json").write_text(content, encoding="utf-8")
    (archive / "latest-run.json").write_text(
        json.dumps(
            {
                "run_id": run_id,
                "label": label,
                "github_actions": {"run_id": int(github_run_id)},
            }
        ),
        encoding="utf-8",
    )


def test_collects_only_private_payload_for_current_workflow_run(tmp_path: Path) -> None:
    archive = tmp_path / "archive"
    old_private = (
        archive
        / "runs"
        / "2026"
        / "20260910T010203_github-actions-kr"
        / "portfolio-private"
    )
    old_private.mkdir(parents=True)
    (old_private / "old.json").write_text("old", encoding="utf-8")
    run_id = "20260911T020304_github-actions-kr"
    _write_run(archive, run_id=run_id, github_run_id="123")

    temp_root = tmp_path / "runner-temp"
    destination = temp_root / "portfolio-artifacts-123"
    copied = collector.collect_current_private_artifact(
        archive_dir=archive,
        destination=destination,
        allowed_destination_root=temp_root,
        expected_label="github-actions-kr",
        github_run_id="123",
    )

    assert copied == destination / run_id
    assert (copied / "account_snapshot.json").read_text(encoding="utf-8") == "current"
    assert not (destination / old_private.parent.name).exists()


@pytest.mark.parametrize(
    ("label", "github_run_id"),
    [("github-actions-us", "123"), ("github-actions-kr", "999")],
)
def test_refuses_to_upload_an_older_or_wrong_market_snapshot(
    tmp_path: Path, label: str, github_run_id: str
) -> None:
    archive = tmp_path / "archive"
    _write_run(
        archive,
        run_id="20260911T020304_github-actions-kr",
        github_run_id=github_run_id,
        label=label,
    )
    temp_root = tmp_path / "runner-temp"

    copied = collector.collect_current_private_artifact(
        archive_dir=archive,
        destination=temp_root / "portfolio-artifacts-123",
        allowed_destination_root=temp_root,
        expected_label="github-actions-kr",
        github_run_id="123",
    )

    assert copied is None


def test_rejects_destination_outside_runner_temp(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="must be a child"):
        collector.collect_current_private_artifact(
            archive_dir=tmp_path / "archive",
            destination=tmp_path / "workspace",
            allowed_destination_root=tmp_path / "runner-temp",
            expected_label="github-actions-kr",
            github_run_id="123",
        )


def test_rejects_malformed_canonical_run_id(tmp_path: Path) -> None:
    archive = tmp_path / "archive"
    archive.mkdir()
    (archive / "latest-run.json").write_text(
        json.dumps(
            {
                "run_id": "../../escape",
                "label": "github-actions-kr",
                "github_actions": {"run_id": 123},
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="malformed"):
        collector.collect_current_private_artifact(
            archive_dir=archive,
            destination=tmp_path / "runner-temp" / "portfolio-artifacts-123",
            allowed_destination_root=tmp_path / "runner-temp",
            expected_label="github-actions-kr",
            github_run_id="123",
        )
