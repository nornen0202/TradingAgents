import json
from datetime import datetime, timedelta, timezone

import pytest

from tradingagents import local_automation as automation
from tradingagents.notifications import advisory, local
from tradingagents.notifications.telegram import NotificationError
from tradingagents.work.packet import sha256_json


NOW = datetime.now(timezone.utc).replace(microsecond=0)


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


def fixture(tmp_path, monkeypatch, surface="youtube"):
    archive, state = tmp_path / "archive", tmp_path / "state"
    spec = advisory.SPECS[surface]
    monkeypatch.delenv(spec[4], raising=False)
    started, finished = NOW - timedelta(hours=2), NOW - timedelta(hours=1)
    summary = ({"total_videos": 40, "successful_videos": 40, "failed_videos": 0}
               if surface == "youtube" else {"messages": 12, "signals": 3, "warnings": 0})
    manifest = {"run_id": f"{surface}_20261013_161315", "status": "success", "summary": summary,
                "started_at": started.isoformat(), "finished_at": finished.isoformat()}
    path = archive / spec[5] / "runs/2026" / manifest["run_id"] / spec[3]
    write(path, manifest)
    body = {"source": {"run_id": manifest["run_id"], "last_run_at": manifest["finished_at"],
                       "status": "success", "health": "OK"}, "events": [{"event_key": "safe-id"}]}
    packet = {"schema": "tradingagents.work-context/v1", "surface": surface,
              "body": body, "source_sha256": sha256_json(body)}
    write(state / "site/work/v1" / surface / "latest.json", packet)
    write(state / "publication.json", {"status": "DELIVERY_VERIFIED"})
    run = {"id": 38335322783, "run_attempt": 2, "status": "completed", "conclusion": "success",
           "head_branch": "main", "head_repository": {"full_name": local.REPOSITORY},
           "path": f".github/workflows/{spec[0]}", "created_at": (started - timedelta(minutes=10)).isoformat(),
           "updated_at": (finished + timedelta(minutes=3)).isoformat()}
    jobs = [{"name": spec[1], "conclusion": "success", "steps": [
        {"name": spec[2], "conclusion": "success", "started_at": started.isoformat(),
         "completed_at": (finished + timedelta(seconds=1)).isoformat()},
        {"name": "Stamp rollback-resistant Pages snapshot", "conclusion": "success"}]},
        {"name": "deploy", "conclusion": "skipped"}]
    def api(endpoint):
        if "/workflows/" in endpoint:
            return {"workflow_runs": [run]}
        if "/jobs?" in endpoint:
            assert "/attempts/2/" in endpoint
            return {"jobs": jobs, "total_count": len(jobs)}
        return run
    monkeypatch.setattr(advisory, "github", api)
    monkeypatch.setattr(automation, "verify_live", lambda _: True)
    monkeypatch.setattr(advisory, "verify_packet_live", lambda *_: True)
    return archive, state, manifest, path, packet, run, jobs


@pytest.mark.parametrize("surface", ["youtube", "prism"])
def test_completed_producer_published_exact_source_sends_once(tmp_path, monkeypatch, surface):
    archive, state, manifest, _, _, _, _ = fixture(tmp_path, monkeypatch, surface)
    advisory.queue_completed(archive, state, now=NOW)
    advisory.queue_completed(archive, state, now=NOW + timedelta(minutes=5))
    events = list((state / "notifications/events").glob("*.json"))
    assert len(events) == 1
    event = local.read(events[0])
    assert event["upstream_run_attempt"] == 2 and event["run_id"] == manifest["run_id"]
    sent = []
    class Client:
        chat_id = "123"
        def __init__(self, **kwargs): pass
        def ensure_private_chat(self): pass
        def send_message(self, message, *, buttons):
            sent.append(message)
            return 42
    monkeypatch.setattr(local, "TelegramBotClient", Client)
    assert local.notify(events[0].stem, archive, state)["status"] == "SENT"
    assert local.notify(events[0].stem, archive, state)["status"] == "NOOP"
    assert len(sent) == 1 and "Work 보고서 완료" in sent[0]
    assert local.read(state / "notifications/results" / events[0].name)["message_ids"] == [42]


@pytest.mark.parametrize("surface", ["youtube", "prism"])
def test_fractional_completion_matches_whole_second_github_step_once(tmp_path, monkeypatch, surface):
    archive, state, manifest, path, packet, _, jobs = fixture(tmp_path, monkeypatch, surface)
    finished = datetime.fromisoformat(manifest["finished_at"])
    jobs[0]["steps"][0]["completed_at"] = finished.isoformat()
    manifest["finished_at"] = finished.replace(microsecond=117583).isoformat()
    write(path, manifest)
    packet["body"]["source"]["last_run_at"] = manifest["finished_at"]
    packet["source_sha256"] = sha256_json(packet["body"])
    write(state / "site/work/v1" / surface / "latest.json", packet)
    advisory.queue_surface(archive, state, surface, now=NOW)
    advisory.queue_surface(archive, state, surface, now=NOW)
    events = list((state / "notifications/events").glob("*.json"))
    assert len(events) == 1
    assert local.notify(events[0].stem, archive, state, dry_run=True)["status"] == "DRY_RUN"


@pytest.mark.parametrize("completed,finished,expected", [
    ("2026-10-15T23:07:41Z", "2026-10-16T08:07:41.999999+09:00", True),
    ("2026-10-15T23:07:41Z", "2026-10-16T08:07:42+09:00", False),
    ("2026-10-15T23:07:41.100Z", "2026-10-16T08:07:41.117583+09:00", False),
    ("2026-10-15T23:07:41.117583Z", "2026-10-16T08:07:41.117583+09:00", True),
    ("2026-10-15T23:07:41.000Z", "2026-10-16T08:07:41.000001+09:00", False),
    ("2026-10-15T23:07:41Z", "2026-10-16T08:07:28+09:00", False),
])
def test_advisory_attempt_respects_timestamp_precision(tmp_path, monkeypatch, completed, finished, expected):
    _, _, manifest, _, _, run, jobs = fixture(tmp_path, monkeypatch, "prism")
    jobs[0]["steps"][0].update(started_at="2026-10-15T23:07:29Z", completed_at=completed)
    manifest.update(started_at="2026-10-16T08:07:29.975497+09:00", finished_at=finished)
    assert advisory.admitted(run, jobs, "prism", manifest) is expected


@pytest.mark.parametrize("change", ["gate", "publish_false", "failed", "cloud_deployed", "superseded", "wrong_attempt_time", "untrusted"])
def test_no_event_for_non_publish_or_non_native_skipped_deploy(tmp_path, monkeypatch, change):
    archive, state, _, _, _, run, jobs = fixture(tmp_path, monkeypatch)
    if change == "gate": jobs[0]["steps"][0]["conclusion"] = "skipped"
    if change == "publish_false": jobs[0]["steps"][1]["conclusion"] = "skipped"
    if change == "failed": run["conclusion"] = "failure"
    if change in {"cloud_deployed", "superseded"}: jobs[1]["conclusion"] = "success"
    if change == "wrong_attempt_time": jobs[0]["steps"][0]["started_at"] = NOW.isoformat()
    if change == "untrusted": run["head_branch"] = "untrusted"
    with pytest.raises(NotificationError, match="preparation pending"):
        advisory.queue_completed(archive, state, now=NOW)
    assert not list((state / "notifications/events").glob("*.json"))


@pytest.mark.parametrize("change", ["old", "future", "old_publication", "wrong_hash", "pending"])
def test_queue_requires_recent_exact_published_source(tmp_path, monkeypatch, change):
    archive, state, manifest, path, packet, _, _ = fixture(tmp_path, monkeypatch)
    if change in {"old", "future"}:
        manifest["finished_at"] = (NOW + timedelta(days=2 if change == "future" else -2)).isoformat()
        manifest["started_at"] = (NOW - timedelta(days=3)).isoformat()
        write(path, manifest)
        packet["body"]["source"]["last_run_at"] = manifest["finished_at"]
        packet["source_sha256"] = sha256_json(packet["body"])
    if change == "old_publication": packet["body"]["source"]["run_id"] = "old_run"
    if change == "wrong_hash": packet["source_sha256"] = "0" * 64
    write(state / "site/work/v1/youtube/latest.json", packet)
    if change == "pending": write(state / "publication.json", {"status": "PAGES_PENDING"})
    if change == "old_publication":
        with pytest.raises(NotificationError): advisory.queue_completed(archive, state, now=NOW)
    else:
        advisory.queue_completed(archive, state, now=NOW)
    assert not list((state / "notifications/events").glob("*.json"))


@pytest.mark.parametrize("change", ["changed_manifest", "superseded", "live_packet", "live_site", "new_attempt"])
def test_sender_rechecks_source_attempt_and_actual_live_delivery(tmp_path, monkeypatch, change):
    archive, state, manifest, path, packet, run, _ = fixture(tmp_path, monkeypatch)
    advisory.queue_completed(archive, state, now=NOW)
    key = next((state / "notifications/events").glob("*.json")).stem
    if change == "changed_manifest": manifest["summary"]["total_videos"] = 41; write(path, manifest)
    if change == "superseded":
        packet["body"]["source"]["run_id"] = "newer_run"
        packet["source_sha256"] = sha256_json(packet["body"])
        write(state / "site/work/v1/youtube/latest.json", packet)
    if change == "live_packet": monkeypatch.setattr(advisory, "verify_packet_live", lambda *_: False)
    if change == "live_site": monkeypatch.setattr(automation, "verify_live", lambda _: False)
    if change == "new_attempt": run["run_attempt"] = 3
    with pytest.raises(NotificationError): local.notify(key, archive, state, dry_run=True)


def test_publisher_lock_is_held_during_exact_packet_verification(tmp_path, monkeypatch):
    archive, state, *_ = fixture(tmp_path, monkeypatch)
    advisory.queue_completed(archive, state, now=NOW)
    key = next((state / "notifications/events").glob("*.json")).stem
    def verify(*_):
        with pytest.raises(TimeoutError):
            with local.interprocess_file_lock(state / "publish.lock", timeout=0):
                pytest.fail("publisher could replace the packet")
        return True
    monkeypatch.setattr(advisory, "verify_packet_live", verify)
    assert local.notify(key, archive, state, dry_run=True)["status"] == "DRY_RUN"


def test_advisory_api_failure_does_not_starve_existing_notifications(tmp_path, monkeypatch):
    def fail(*_): raise RuntimeError("offline")
    monkeypatch.setattr(advisory, "queue_completed", fail)
    calls = []
    monkeypatch.setattr(local, "reconcile", lambda _: calls.append("dispatched"))
    local.reconcile_safely(tmp_path / "archive", tmp_path / "state")
    assert calls == ["dispatched"]


def test_changed_immutable_source_cannot_create_a_second_completion(tmp_path, monkeypatch):
    archive, state, manifest, path, _, _, _ = fixture(tmp_path, monkeypatch)
    advisory.queue_completed(archive, state, now=NOW)
    manifest["changed_after_completion"] = True
    write(path, manifest)
    with pytest.raises(NotificationError): advisory.queue_completed(archive, state, now=NOW)
    assert len(list((state / "notifications/events").glob("*.json"))) == 1


def test_one_advisory_failure_does_not_starve_the_other_surface(tmp_path, monkeypatch):
    fixture(tmp_path, monkeypatch, "youtube")
    archive, state, *_ = fixture(tmp_path, monkeypatch, "prism")
    # This fake API exposes only PRISM, so the YouTube producer cannot validate.
    with pytest.raises(NotificationError): advisory.queue_completed(archive, state, now=NOW)
    events = [local.read(p) for p in (state / "notifications/events").glob("*.json")]
    assert len(events) == 1 and events[0]["surface"] == "prism"


def test_packet_http_verification_rejects_stale_or_extra_bytes(tmp_path, monkeypatch):
    path = tmp_path / "work/v1/youtube/latest.json"
    write(path, {"body": "current", "source_sha256": "hash"})
    class Response:
        def __init__(self, data): self.data = data
        def __enter__(self): return self
        def __exit__(self, *_): pass
        def read(self, size): return self.data[:size]
    for data, expected in [(path.read_bytes(), True), (b"old", False), (path.read_bytes() + b"x", False)]:
        monkeypatch.setattr(advisory, "urlopen", lambda request, timeout: Response(data))
        assert advisory.verify_packet_live(tmp_path, "youtube") is expected


@pytest.mark.parametrize("surface", ["youtube", "prism"])
def test_rebuild_cannot_queue_new_packet_under_previous_verified_receipt(tmp_path, monkeypatch, surface):
    archive, state, *_ = fixture(tmp_path, monkeypatch, surface)
    # A publisher has rebuilt the packet but has not replaced its old verified
    # receipt yet. The independent run-due reconciler must not admit this mix.
    with local.interprocess_file_lock(state / "publish.lock", timeout=0):
        advisory.queue_completed(archive, state, now=NOW)
        assert not list((state / "notifications/events").glob("*.json"))
        write(state / "publication.json", {"status": "PAGES_PENDING"})
    advisory.queue_completed(archive, state, now=NOW)
    assert not list((state / "notifications/events").glob("*.json"))
    write(state / "publication.json", {"status": "DELIVERY_VERIFIED"})
    advisory.queue_completed(archive, state, now=NOW)
    advisory.queue_completed(archive, state, now=NOW)
    assert len(list((state / "notifications/events").glob("*.json"))) == 1


@pytest.mark.parametrize("surface", ["youtube", "prism"])
def test_advisory_admission_keeps_publisher_excluded_until_event_is_bound(tmp_path, monkeypatch, surface):
    archive, state, *_ = fixture(tmp_path, monkeypatch, surface)
    original_api = advisory.github

    def api(endpoint):
        with pytest.raises(TimeoutError):
            with local.interprocess_file_lock(state / "publish.lock", timeout=0):
                pytest.fail("publisher could replace the packet during admission")
        return original_api(endpoint)

    advisory.queue_completed(archive, state, now=NOW, api=api)
    assert len(list((state / "notifications/events").glob("*.json"))) == 1


@pytest.mark.parametrize("surface", ["youtube", "prism"])
def test_publisher_owner_can_queue_verified_advisory_without_reentering_lock(tmp_path, monkeypatch, surface):
    archive, state, *_ = fixture(tmp_path, monkeypatch, surface)
    monkeypatch.setattr(local, "reconcile", lambda _: None)
    with local.interprocess_file_lock(state / "publish.lock", timeout=0):
        local.reconcile_safely(archive, state, publication_locked=True)
    assert len(list((state / "notifications/events").glob("*.json"))) == 1


def test_busy_publisher_does_not_starve_other_notification_dispatch(tmp_path, monkeypatch):
    archive, state, *_ = fixture(tmp_path, monkeypatch)
    calls = []
    monkeypatch.setattr(local, "reconcile", lambda _: calls.append("existing notification"))
    with local.interprocess_file_lock(state / "publish.lock", timeout=0):
        local.reconcile_safely(archive, state)
    assert calls == ["existing notification"]
    assert not list((state / "notifications/events").glob("*.json"))
