"""Bind local advisory publication to a completed, publish-enabled cloud producer."""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from uuid import uuid4

from tradingagents.atomic_io import interprocess_file_lock
from tradingagents.prism_telegram.completion import collection_complete
from tradingagents.work.packet import sha256_json
from .telegram import NotificationError

SPECS = {
    "youtube": ("daily-youtube-reports.yml", "build_youtube_pages", "Run YouTube verification reports",
                "youtube_run.json", "TRADINGAGENTS_YOUTUBE_ARCHIVE_DIR", "youtube-archive"),
    "prism": ("daily-prism-telegram-reports.yml", "build_prism_telegram_pages", "Run PRISM Telegram report collection",
              "prism_telegram_run.json", "TRADINGAGENTS_PRISM_TELEGRAM_ARCHIVE_DIR", "prism-telegram-archive"),
}


def github(endpoint):
    result = subprocess.run(["gh", "api", endpoint], capture_output=True, text=True, check=True, timeout=30)
    return json.loads(result.stdout)


def canonical(archive, surface, run_id):
    from .local import read
    if surface not in SPECS or not re.fullmatch(r"[A-Za-z0-9_-]+", str(run_id)):
        raise NotificationError("Invalid advisory identity.")
    spec = SPECS[surface]
    root = Path(os.getenv(spec[4]) or archive / spec[5])
    paths = list((root / "runs").glob(f"*/{run_id}/{spec[3]}"))
    if len(paths) != 1:
        raise NotificationError("Canonical advisory run is unavailable.")
    manifest = read(paths[0])
    summary = manifest.get("summary") or {}
    complete = (summary.get("total_videos", 0) > 0
                and summary.get("total_videos") == summary.get("successful_videos")
                and summary.get("failed_videos") == 0) if surface == "youtube" else (
                    collection_complete(manifest) and summary["messages"] > 0)
    if manifest.get("run_id") != run_id or manifest.get("status") != "success" or not complete:
        raise NotificationError("Canonical advisory run did not complete successfully.")
    return manifest, hashlib.sha256(paths[0].read_bytes()).hexdigest()


def packet_covers(packet, surface, manifest):
    body = packet.get("body") or {}
    source = body.get("source") or {}
    return (packet.get("schema") == "tradingagents.work-context/v1" and packet.get("surface") == surface
            and packet.get("source_sha256") == sha256_json(body)
            and source.get("run_id") == manifest.get("run_id")
            and source.get("last_run_at") == manifest.get("finished_at")
            and source.get("status") == "success" and source.get("health") == "OK")


def collection_contains_manifest(collection, manifest):
    """Match immutable observations to the precision of the GitHub step clock."""
    from .local import timestamp

    start = timestamp(collection.get("started_at"))
    raw_finish = collection.get("completed_at")
    finish = timestamp(raw_finish)
    began, ended = timestamp(manifest.get("started_at")), timestamp(manifest.get("finished_at"))
    # GitHub's whole-second completion labels the entire second, while the
    # canonical producer retains microseconds. Never admit the next second or
    # add tolerance to a completion that already supplies fractional precision.
    within_end = ended < finish + timedelta(seconds=1) if "." not in raw_finish else ended <= finish
    return start <= finish and start <= began <= ended and within_end


def admitted(run, jobs, surface, manifest):
    """A build alone is insufficient; publish=false and native deployments stay out."""
    from .local import REPOSITORY
    spec = SPECS[surface]
    if (run.get("status") != "completed" or run.get("conclusion") != "success"
            or run.get("head_branch") != "main"
            or (run.get("head_repository") or {}).get("full_name") != REPOSITORY
            or str(run.get("path", "")).split("@", 1)[0] != f".github/workflows/{spec[0]}"):
        return False
    # A cloud deploy (including superseded) retains ownership of its notification.
    deploy = [job for job in jobs if job.get("name") == "deploy"]
    if len(deploy) != 1 or deploy[0].get("conclusion") != "skipped":
        return False
    builds = [job for job in jobs if job.get("name") == spec[1] and job.get("conclusion") == "success"]
    if len(builds) != 1:
        return False
    steps = builds[0].get("steps") or []
    collections = [step for step in steps if step.get("name") == spec[2] and step.get("conclusion") == "success"]
    stamps = [step for step in steps if step.get("name") == "Stamp rollback-resistant Pages snapshot"
              and step.get("conclusion") == "success"]
    if len(collections) != 1 or len(stamps) != 1:
        return False
    return collection_contains_manifest(collections[0], manifest)


def producer_for(surface, manifest, *, api=None):
    from .local import REPOSITORY, timestamp
    api = api or github
    since = (timestamp(manifest["started_at"]) - timedelta(days=1)).astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    payload = api(f"repos/{REPOSITORY}/actions/workflows/{SPECS[surface][0]}/runs?per_page=100&created=>={since}")
    runs = payload.get("workflow_runs") or []
    # Never infer uniqueness from a truncated result set.
    if len(runs) >= 100:
        raise NotificationError("Advisory producer history requires pagination.")
    matches = []
    for run in runs:
        if run.get("status") != "completed" or run.get("conclusion") != "success":
            continue
        if not (timestamp(run.get("created_at")) <= timestamp(manifest.get("started_at"))
                and timestamp(run.get("updated_at")) >= timestamp(manifest.get("finished_at"))):
            continue
        attempt = int(run.get("run_attempt") or 1)
        jobs = api(f"repos/{REPOSITORY}/actions/runs/{run['id']}/attempts/{attempt}/jobs?per_page=100")
        if jobs.get("total_count", 0) >= 100:
            raise NotificationError("Advisory producer jobs require pagination.")
        if admitted(run, jobs.get("jobs") or [], surface, manifest):
            matches.append((int(run["id"]), attempt))
    if len(matches) != 1:
        raise NotificationError("Advisory completion lacks one publish-enabled producer.")
    return matches[0]


def queue_surface(archive, state, surface, *, now, api=None):
    from .local import read, timestamp, queue
    packet = read(state / "site" / "work" / "v1" / surface / "latest.json")
    run_id = ((packet.get("body") or {}).get("source") or {}).get("run_id")
    if not run_id:
        return
    manifest, digest = canonical(archive, surface, run_id)
    finished = timestamp(manifest.get("finished_at"))
    if not (timestamp(manifest.get("started_at")) <= finished <= now
            and now - finished <= timedelta(hours=24) and packet_covers(packet, surface, manifest)):
        return
    for path in (state / "notifications" / "events").glob("*.json"):
        event = read(path)
        if (event.get("kind"), event.get("surface"), event.get("run_id")) == ("advisory_success", surface, run_id):
            if event.get("manifest_sha256") != digest:
                raise NotificationError("Previously queued advisory source was mutated.")
            return
    run, attempt = producer_for(surface, manifest, api=api)
    queue(state, {"kind": "advisory_success", "surface": surface, "run_id": run_id,
                  "manifest_sha256": digest, "finished_at": manifest["finished_at"],
                  "upstream_run_id": run, "upstream_run_attempt": attempt})


def queue_completed(archive, state, *, now=None, api=None, publication_locked=False):
    """Read the receipt and packet together; only the publisher may reuse its lock."""
    if publication_locked:
        return _queue_completed_locked(archive, state, now=now, api=api)
    try:
        with interprocess_file_lock(state / "publish.lock", timeout=0):
            return _queue_completed_locked(archive, state, now=now, api=api)
    except TimeoutError:
        # A rebuild can expose a new packet before replacing the previous
        # DELIVERY_VERIFIED receipt. Leave admission to the owning publisher.
        return


def _queue_completed_locked(archive, state, *, now=None, api=None):
    from .local import read
    now = now or datetime.now(timezone.utc)
    if read(state / "publication.json").get("status") != "DELIVERY_VERIFIED":
        return
    errors = []
    for surface in SPECS:
        try:
            queue_surface(archive, state, surface, now=now, api=api)
        except Exception as exc:
            # One collector's metadata/API failure must not starve the other.
            errors.append(type(exc).__name__)
    if errors:
        raise NotificationError("Advisory preparation pending: " + ",".join(errors))


def verify_packet_live(site, surface):
    from tradingagents.local_automation import PUBLIC_BASE
    relative = f"work/v1/{surface}/latest.json"
    path = site / relative
    request = Request(f"{PUBLIC_BASE}/{relative}?verify={uuid4().hex}", headers={"Cache-Control": "no-cache"})
    with urlopen(request, timeout=30) as response:
        return response.read(path.stat().st_size + 1) == path.read_bytes()


def compose(event, archive, state, *, api=None):
    from .local import PUBLICATION_LOCK_TIMEOUT_SECONDS, REPOSITORY, read, timestamp
    from tradingagents.local_automation import verify_live, PUBLIC_BASE
    api = api or github
    surface = event.get("surface")
    manifest, digest = canonical(archive, surface, event.get("run_id"))
    if digest != event.get("manifest_sha256") or manifest.get("finished_at") != event.get("finished_at"):
        raise NotificationError("Advisory canonical source binding changed.")
    finished = timestamp(manifest.get("finished_at"))
    if not (timestamp(manifest.get("started_at")) <= finished <= datetime.now(timezone.utc)
            and datetime.now(timezone.utc) - finished <= timedelta(hours=24)):
        raise NotificationError("Advisory completion is outside its delivery window.")
    run_id, attempt = event.get("upstream_run_id"), event.get("upstream_run_attempt")
    if not isinstance(run_id, int) or run_id <= 0 or not isinstance(attempt, int) or attempt <= 0:
        raise NotificationError("Invalid advisory producer provenance.")
    run = api(f"repos/{REPOSITORY}/actions/runs/{run_id}")
    jobs = api(f"repos/{REPOSITORY}/actions/runs/{run_id}/attempts/{attempt}/jobs?per_page=100")
    if (run.get("run_attempt") != attempt or jobs.get("total_count", 0) >= 100
            or not admitted(run, jobs.get("jobs") or [], surface, manifest)):
        raise NotificationError("Advisory producer is not an admitted completed attempt.")
    with interprocess_file_lock(state / "publish.lock", timeout=PUBLICATION_LOCK_TIMEOUT_SECONDS):
        packet = read(state / "site" / "work" / "v1" / surface / "latest.json")
        if (read(state / "publication.json").get("status") != "DELIVERY_VERIFIED"
                or not packet_covers(packet, surface, manifest) or not verify_live(state / "site")
                or not verify_packet_live(state / "site", surface)):
            raise NotificationError("Advisory Pages delivery is not verified for this source.")
    summary = manifest["summary"]
    detail = (f"영상 {summary['successful_videos']}/{summary['total_videos']}건 처리 · 실패 0"
              if surface == "youtube" else f"메시지 {summary['messages']}건 · 신호 {summary.get('signals', 0)}건")
    text = (f"TradingAgents {'YouTube' if surface == 'youtube' else 'PRISM'} 자료 처리·게시 완료\n"
            f"완료 시각: {event['finished_at']}\n{detail}\n공개 자료의 원본 실행과 실제 게시를 확인했습니다.\n"
            "외부 자료의 검증 상태와 불확실성을 유지합니다. 신규 투자 분석·Work 보고서 완료나 주문 신호를 뜻하지 않습니다.")
    path = "youtube/" if surface == "youtube" else "prism-telegram/"
    return text, [[{"text": "공개 자료 보기", "url": f"{PUBLIC_BASE}/{path}"}]], {
        "conclusion": "success", "run_ids": [event["run_id"]], "surfaces": [surface],
        "upstream_run_id": run_id, "upstream_run_attempt": attempt, "source_sha256": packet["source_sha256"]}
