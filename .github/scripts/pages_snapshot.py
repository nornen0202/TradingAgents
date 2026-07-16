from __future__ import annotations

import argparse
import json
import os
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from tradingagents.scheduled.mobile_site import STRATEGY_SCHEMA, assert_strategy_payload_safe


SNAPSHOT_SCHEMA = "tradingagents.pages-snapshot/v1"
SNAPSHOT_FILENAME = "pages-snapshot.json"


def create_snapshot(
    site_dir: Path,
    *,
    repository: str,
    workflow: str,
    run_id: int,
    run_attempt: int,
    commit_sha: str,
    generated_epoch_ms: int | None = None,
    require_strategy_payload: bool = False,
) -> dict[str, Any]:
    root = Path(site_dir)
    if not root.is_dir() or not (root / "index.html").is_file():
        raise ValueError(f"Pages site is incomplete: {root}")
    if require_strategy_payload:
        _validate_strategy_payload(root)
    # Use the snapshot's last materialized file time rather than the later guard
    # step time.  A slow verifier must not make an older site appear newer than
    # a concurrently completed build.
    epoch_ms = int(generated_epoch_ms if generated_epoch_ms is not None else _site_generation_epoch_ms(root))
    if epoch_ms <= 0:
        raise ValueError("Snapshot generation time must be positive.")
    payload = {
        "schema": SNAPSHOT_SCHEMA,
        "generated_at": datetime.fromtimestamp(epoch_ms / 1000, tz=timezone.utc).isoformat(),
        "generated_epoch_ms": epoch_ms,
        "repository": str(repository),
        "workflow": str(workflow),
        "run_id": int(run_id),
        "run_attempt": int(run_attempt),
        "commit_sha": str(commit_sha),
    }
    target = root / SNAPSHOT_FILENAME
    temporary = target.with_suffix(".tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, target)
    return payload


def should_deploy(candidate: dict[str, Any], live: dict[str, Any] | None) -> tuple[bool, str]:
    _validate_snapshot(candidate, label="candidate")
    if live is None:
        return True, "No deployed snapshot marker exists yet."
    _validate_snapshot(live, label="live")
    candidate_time = int(candidate["generated_epoch_ms"])
    live_time = int(live["generated_epoch_ms"])
    if candidate_time > live_time:
        return True, "Candidate snapshot was generated after the deployed snapshot."
    if candidate_time < live_time:
        return False, "Candidate snapshot is older than the deployed snapshot; refusing rollback."
    candidate_order = (int(candidate["run_id"]), int(candidate["run_attempt"]))
    live_order = (int(live["run_id"]), int(live["run_attempt"]))
    if candidate_order > live_order:
        return True, "Snapshot times match and candidate run order is newer."
    return False, "Candidate snapshot is already deployed or superseded."


def fetch_live_snapshot(
    public_base_url: str,
    *,
    attempts: int = 3,
    timeout_seconds: float = 12.0,
    opener: Callable[..., Any] = urllib.request.urlopen,
) -> dict[str, Any] | None:
    base = str(public_base_url or "").strip().rstrip("/")
    if not base.startswith(("https://", "http://")):
        raise ValueError("A valid public Pages base URL is required.")
    url = f"{base}/{SNAPSHOT_FILENAME}?guard={time.time_ns()}"
    request = urllib.request.Request(
        url,
        headers={"Accept": "application/json", "Cache-Control": "no-cache", "User-Agent": "TradingAgents-Pages-Guard/1"},
    )
    last_error: Exception | None = None
    for attempt in range(max(1, int(attempts))):
        try:
            with opener(request, timeout=timeout_seconds) as response:
                payload = json.loads(response.read().decode("utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("Deployed snapshot marker is not a JSON object.")
            _validate_snapshot(payload, label="live")
            return payload
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                return None
            last_error = exc
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
            last_error = exc
        if attempt + 1 < max(1, int(attempts)):
            time.sleep(min(2**attempt, 4))
    raise RuntimeError(f"Could not verify deployed Pages snapshot marker: {last_error}") from last_error


def _validate_strategy_payload(site_dir: Path) -> None:
    mobile = site_dir / "mobile"
    for name in ("private.html", "private.js", "strategy.json"):
        if not (mobile / name).is_file():
            raise ValueError(f"Production Pages snapshot is missing mobile strategy artifact: mobile/{name}")
    for stale_name in ("private.enc.json", "private.json"):
        if (mobile / stale_name).exists():
            raise ValueError(f"Production Pages snapshot contains obsolete mobile artifact: mobile/{stale_name}")
    try:
        payload = json.loads((mobile / "strategy.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError("Mobile strategy payload is invalid JSON.") from exc
    if not isinstance(payload, dict):
        raise ValueError("Mobile strategy payload must be a JSON object.")
    if payload.get("schema") != STRATEGY_SCHEMA:
        raise ValueError("Mobile strategy payload contract is invalid.")
    if not isinstance(payload.get("markets"), dict):
        raise ValueError("Mobile strategy payload is missing markets.")
    assert_strategy_payload_safe(payload)


def _site_generation_epoch_ms(site_dir: Path) -> int:
    mtimes = [
        path.stat().st_mtime_ns // 1_000_000
        for path in site_dir.rglob("*")
        if path.is_file() and path.name not in {SNAPSHOT_FILENAME, Path(SNAPSHOT_FILENAME).with_suffix(".tmp").name}
    ]
    if not mtimes:
        raise ValueError("Pages site has no materialized files.")
    return max(mtimes)


def _validate_snapshot(snapshot: dict[str, Any], *, label: str) -> None:
    if snapshot.get("schema") != SNAPSHOT_SCHEMA:
        raise ValueError(f"Unsupported {label} Pages snapshot schema: {snapshot.get('schema')}")
    for key in ("generated_epoch_ms", "run_id", "run_attempt"):
        try:
            value = int(snapshot[key])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"{label} Pages snapshot has invalid {key}.") from exc
        if value <= 0:
            raise ValueError(f"{label} Pages snapshot has non-positive {key}.")


def _write_outputs(values: dict[str, Any], output_path: str | None) -> None:
    destination = str(output_path or os.getenv("GITHUB_OUTPUT", "")).strip()
    if not destination:
        return
    with Path(destination).open("a", encoding="utf-8", newline="\n") as handle:
        for key, value in values.items():
            handle.write(f"{key}={value}\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Stamp Pages snapshots and block stale deployment rollbacks.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    stamp = subparsers.add_parser("stamp")
    stamp.add_argument("--site-dir", required=True, type=Path)
    stamp.add_argument("--repository", required=True)
    stamp.add_argument("--workflow", required=True)
    stamp.add_argument("--run-id", required=True, type=int)
    stamp.add_argument("--run-attempt", required=True, type=int)
    stamp.add_argument("--commit-sha", required=True)
    stamp.add_argument("--require-strategy-payload", action="store_true")
    stamp.add_argument("--output")

    guard = subparsers.add_parser("guard")
    guard.add_argument("--candidate-generated-epoch-ms", required=True, type=int)
    guard.add_argument("--candidate-run-id", required=True, type=int)
    guard.add_argument("--candidate-run-attempt", required=True, type=int)
    guard.add_argument("--public-base-url", required=True)
    guard.add_argument("--output")
    args = parser.parse_args()

    if args.command == "stamp":
        snapshot = create_snapshot(
            args.site_dir,
            repository=args.repository,
            workflow=args.workflow,
            run_id=args.run_id,
            run_attempt=args.run_attempt,
            commit_sha=args.commit_sha,
            require_strategy_payload=args.require_strategy_payload,
        )
        _write_outputs(
            {
                "generated_epoch_ms": snapshot["generated_epoch_ms"],
                "snapshot_file": SNAPSHOT_FILENAME,
            },
            args.output,
        )
        print(f"Stamped Pages snapshot at {snapshot['generated_at']}.")
        return 0

    candidate = {
        "schema": SNAPSHOT_SCHEMA,
        "generated_epoch_ms": args.candidate_generated_epoch_ms,
        "run_id": args.candidate_run_id,
        "run_attempt": args.candidate_run_attempt,
    }
    live = fetch_live_snapshot(args.public_base_url)
    deploy, reason = should_deploy(candidate, live)
    _write_outputs({"should_deploy": str(deploy).lower(), "reason": reason}, args.output)
    print(reason)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
