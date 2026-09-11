from __future__ import annotations

import argparse
import json
import os
import re
import shutil
from pathlib import Path
from typing import Any


RUN_ID_PATTERN = re.compile(r"^(?P<year>20\d{2})\d{4}T\d{6}_[A-Za-z0-9_.-]+$")


def _is_within(child: Path, parent: Path) -> bool:
    child_path = os.path.normcase(str(child.resolve()))
    parent_path = os.path.normcase(str(parent.resolve()))
    return os.path.commonpath([child_path, parent_path]) == parent_path


def _load_latest_manifest(archive_dir: Path) -> dict[str, Any] | None:
    latest_path = archive_dir / "latest-run.json"
    if not latest_path.is_file():
        return None
    payload = json.loads(latest_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{latest_path} must contain a JSON object.")
    return payload


def collect_current_private_artifact(
    *,
    archive_dir: Path,
    destination: Path,
    allowed_destination_root: Path,
    expected_label: str,
    github_run_id: str,
) -> Path | None:
    """Copy only the private payload produced by this workflow run.

    ``latest-run.json`` is the canonical pointer written by the scheduled
    runner.  Matching both its label and GitHub run id prevents a failed job
    from silently uploading an older account snapshot.
    """

    archive_dir = archive_dir.resolve()
    destination = destination.resolve()
    allowed_destination_root = allowed_destination_root.resolve()
    if destination == allowed_destination_root or not _is_within(
        destination, allowed_destination_root
    ):
        raise ValueError(
            f"Artifact destination must be a child of {allowed_destination_root}: "
            f"{destination}"
        )

    if destination.exists():
        shutil.rmtree(destination)

    manifest = _load_latest_manifest(archive_dir)
    if manifest is None:
        return None

    label = str(manifest.get("label") or "").strip()
    if label != expected_label:
        return None

    manifest_actions = manifest.get("github_actions")
    if not isinstance(manifest_actions, dict):
        return None
    manifest_github_run_id = str(manifest_actions.get("run_id") or "").strip()
    if manifest_github_run_id != str(github_run_id).strip():
        return None

    run_id = str(manifest.get("run_id") or "").strip()
    match = RUN_ID_PATTERN.fullmatch(run_id)
    if match is None:
        raise ValueError(f"Unsafe or malformed scheduled run id: {run_id!r}")

    runs_root = (archive_dir / "runs").resolve()
    private_dir = (runs_root / match.group("year") / run_id / "portfolio-private").resolve()
    if not _is_within(private_dir, runs_root):
        raise ValueError(f"Private artifact path escaped the archive runs directory: {private_dir}")
    if not private_dir.is_dir():
        return None

    target = destination / run_id
    destination.mkdir(parents=True, exist_ok=True)
    shutil.copytree(private_dir, target)
    return target


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Collect the current scheduled run's bounded private account artifact."
    )
    parser.add_argument("--archive-dir", type=Path, required=True)
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument("--allowed-destination-root", type=Path, required=True)
    parser.add_argument("--expected-label", required=True)
    parser.add_argument("--github-run-id", required=True)
    return parser


def main() -> int:
    args = _parser().parse_args()
    copied = collect_current_private_artifact(
        archive_dir=args.archive_dir,
        destination=args.destination,
        allowed_destination_root=args.allowed_destination_root,
        expected_label=args.expected_label,
        github_run_id=args.github_run_id,
    )
    if copied is None:
        print(
            "::warning::No private account artifact belongs to this workflow run; "
            "an older snapshot will not be uploaded."
        )
        return 0
    print(f"Collected current private account artifact: {copied.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
