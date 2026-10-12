import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from tradingagents import local_automation as automation
from tradingagents.notifications import local
from tradingagents.notifications.telegram import NotificationError

NOW = datetime(2026, 10, 12, 8, tzinfo=timezone.utc)


def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


def completed(archive, mode="full", **changes):
    run = f"20261012T050000_local-scheduler-kr-{mode}"
    manifest = {"run_id": run, "label": f"local-scheduler-kr-{mode}", "status": "success",
                "started_at": (NOW - timedelta(hours=3)).isoformat(),
                "finished_at": (NOW - timedelta(hours=1)).isoformat(),
                "settings": {"market": "KR", "run_mode": mode},
                "summary": {"total_tickers": 30, "successful_tickers": 30, "failed_tickers": 0},
                "active_universe": {"coverage": {"complete": True}}}
    manifest.update(changes)
    write(archive / "runs" / "2026" / manifest["run_id"] / "run.json", manifest)
    return manifest


def published_strategy(state, manifest, *, analysis=None):
    analysis = analysis or manifest
    write(state / "site/mobile/strategy.json", {"markets": {"kr": {
        "run_id": manifest["run_id"],
        "freshness_receipt": {"producer_run_id": manifest["run_id"],
                              "producer_finished_at": manifest["finished_at"],
                              "analysis_lineage_status": "RESOLVED",
                              "analysis_run_id": analysis["run_id"]},
        "latest_completed_analysis": {"run_id": analysis["run_id"], "status": "success",
                                      "finished_at": analysis["finished_at"]},
    }}})


def prepared(tmp_path, monkeypatch):
    archive, state = tmp_path / "archive", tmp_path / "state"
    manifest = completed(archive)
    write(state / "publication.json", {"status": "DELIVERY_VERIFIED"})
    published_strategy(state, manifest)
    monkeypatch.setattr(automation, "verify_live", lambda site: True)
    local.queue_completed(archive, state, now=NOW)
    path = next((state / "notifications/events").glob("*.json"))
    return archive, state, manifest, path.stem


def test_bootstrap_recovers_today_full_but_not_old_overlays(tmp_path):
    archive, state = tmp_path / "archive", tmp_path / "state"
    full = completed(archive)
    overlay = completed(archive, "overlay_only")
    published_strategy(state, overlay, analysis=full)
    write(state / "publication.json", {"status": "PAGES_PENDING"})
    local.queue_completed(archive, state, now=NOW)
    assert not (state / "notifications/events").exists()
    write(state / "publication.json", {"status": "DELIVERY_VERIFIED"})
    local.queue_completed(archive, state, now=NOW)
    local.queue_completed(archive, state, now=NOW + timedelta(minutes=5))
    assert len(list((state / "notifications/events").glob("*.json"))) == 1
    overlay = completed(archive, "overlay_only", finished_at=(NOW + timedelta(minutes=10)).isoformat())
    published_strategy(state, overlay, analysis=full)
    local.queue_completed(archive, state, now=NOW + timedelta(minutes=15))
    assert len(list((state / "notifications/events").glob("*.json"))) == 2


@pytest.mark.parametrize("change", [
    {"status": "running"}, {"summary": {"failed_tickers": 1}},
    {"finished_at": (NOW + timedelta(minutes=1)).isoformat()},
    {"finished_at": (NOW - timedelta(days=2)).isoformat()},
    {"label": "github-actions-kr"},
])
def test_unfinished_failed_future_or_old_production_is_not_notified(tmp_path, change):
    archive, state = tmp_path / "archive", tmp_path / "state"
    completed(archive, **change)
    write(state / "publication.json", {"status": "DELIVERY_VERIFIED"})
    local.queue_completed(archive, state, now=NOW)
    assert not list((state / "notifications/events").glob("*.json"))


def test_new_completion_waits_for_exact_published_lineage(tmp_path, monkeypatch):
    archive, state = tmp_path / "archive", tmp_path / "state"
    previous = completed(archive, run_id="20261010T050000_local-scheduler-kr-full",
                         started_at=(NOW - timedelta(days=2, hours=3)).isoformat(),
                         finished_at=(NOW - timedelta(days=2)).isoformat())
    current = completed(archive)
    write(state / "publication.json", {"status": "DELIVERY_VERIFIED"})
    published_strategy(state, previous)
    monkeypatch.setattr(automation, "verify_live", lambda _: True)
    local.queue_completed(archive, state, now=NOW)
    assert not list((state / "notifications/events").glob("*.json"))

    # A previously queued event must also fail closed if only the older
    # strategy is live; a verified publication status is insufficient.
    key = local.queue(state, {"kind": "success", "run_id": current["run_id"],
                              "market": "kr", "finished_at": current["finished_at"]})
    with pytest.raises(NotificationError, match="this analysis run"):
        local.notify(key, archive, state, dry_run=True)

    published_strategy(state, current)
    assert local.notify(key, archive, state, dry_run=True)["status"] == "DRY_RUN"


def test_live_verification_holds_the_publication_lane(tmp_path, monkeypatch):
    archive, state, _, key = prepared(tmp_path, monkeypatch)
    def verify(_):
        with pytest.raises(TimeoutError):
            with local.interprocess_file_lock(state / "publish.lock", timeout=0):
                pytest.fail("publisher could rewrite the validated strategy")
        return True
    monkeypatch.setattr(automation, "verify_live", verify)
    assert local.notify(key, archive, state, dry_run=True)["status"] == "DRY_RUN"


def test_dispatch_is_not_sent_and_active_owner_prevents_retry(tmp_path, monkeypatch):
    archive, state, _, key = prepared(tmp_path, monkeypatch)
    calls = []
    def runner(args, **kwargs):
        calls.append(args)
        return SimpleNamespace(returncode=0, stdout="[]")
    local.reconcile(state, now=NOW, runner=runner)
    receipt = local.read(state / "notifications/dispatches" / f"{key}.json")
    assert receipt['status'] == 'DISPATCH_ACCEPTED'
    local.reconcile(state, now=NOW + timedelta(minutes=5), runner=runner)
    assert len(calls) == 2
    def active(args, **kwargs):
        assert args[1:3] == ['run', 'list']
        return SimpleNamespace(stdout=json.dumps([{'displayTitle': f'[local={key}]', 'status': 'in_progress'}]))
    local.reconcile(state, now=NOW + timedelta(minutes=20), runner=active)
    write(state / 'notifications/results' / f'{key}.json', {'status': 'SENT', 'local_event_id': key, 'message_ids': [7]})
    local.reconcile(state, now=NOW + timedelta(minutes=21), runner=lambda *a, **k: pytest.fail('duplicate dispatch'))
    assert local.read(state / 'notifications/dispatches' / f'{key}.json')['status'] == 'DELIVERY_VERIFIED'


def test_dispatch_retry_budget_survives_new_scheduler_tick(tmp_path, monkeypatch):
    _, state, _, key = prepared(tmp_path, monkeypatch)
    calls = []
    def runner(args, **kwargs):
        calls.append(args)
        return SimpleNamespace(returncode=1, stdout='[]')
    for minutes in [0, 16, 32, 48, 64]:
        local.reconcile(state, now=NOW + timedelta(minutes=minutes), runner=runner)
    assert sum(c[1] == 'workflow' for c in calls) == 3
    assert local.read(state / 'notifications/dispatches' / f'{key}.json')['attempts'] == 3


def test_incident_cooldown_is_policy_skip_not_delivery(tmp_path):
    key = local.queue_failure(tmp_path, stage='analysis', source_key='a' * 64,
                              error_type='TimeoutError', finished_at=NOW.isoformat())
    write(tmp_path / 'notifications/results' / f'{key}.json',
          {'status': 'NOOP', 'reason': 'INCIDENT_COOLDOWN', 'local_event_id': key, 'message_ids': []})
    local.reconcile(tmp_path, now=NOW, runner=lambda *a, **k: pytest.fail('retransmission'))
    assert local.read(tmp_path / 'notifications/dispatches' / f'{key}.json')['status'] == 'POLICY_SKIPPED'


def test_canonical_validation_and_telegram_receipt_deduplicate(tmp_path, monkeypatch):
    archive, state, _, key = prepared(tmp_path, monkeypatch)
    sent = []
    class Client:
        chat_id = '123'
        def __init__(self, **kwargs): pass
        def ensure_private_chat(self): pass
        def send_message(self, message, *, buttons):
            sent.append(message)
            return 42
    monkeypatch.setattr(local, 'TelegramBotClient', Client)
    assert local.notify(key, archive, state)['status'] == 'SENT'
    assert local.notify(key, archive, state)['status'] == 'NOOP'
    assert len(sent) == 1
    assert '30/30' in sent[0] and '재확인' in sent[0]
    assert local.read(state / 'notifications/results' / f'{key}.json')['message_ids'] == [42]
    monkeypatch.setattr(automation, 'verify_live', lambda _: False)
    with pytest.raises(NotificationError, match='delivery'):
        local.notify(key, archive, state)


def test_outbox_tampering_and_incomplete_coverage_fail_closed(tmp_path, monkeypatch):
    archive, state, manifest, key = prepared(tmp_path, monkeypatch)
    manifest['active_universe']['coverage']['complete'] = False
    write(archive / 'runs/2026' / manifest['run_id'] / 'run.json', manifest)
    with pytest.raises(NotificationError, match='successfully'):
        local.notify(key, archive, state, dry_run=True)
    path = state / 'notifications/events' / f'{key}.json'
    event = local.read(path); event['market'] = 'us'; write(path, event)
    with pytest.raises(NotificationError, match='binding'):
        local.notify(key, archive, state, dry_run=True)


def test_failure_outbox_preserves_first_real_time_and_omits_error_text(tmp_path):
    key = local.queue_failure(tmp_path, stage='analysis', source_key='a' * 64,
                              error_type='TimeoutError', finished_at=NOW.isoformat())
    assert local.queue_failure(tmp_path, stage='analysis', source_key='a' * 64,
                               error_type='TimeoutError', finished_at=(NOW + timedelta(minutes=5)).isoformat()) == key
    event = local.read(tmp_path / 'notifications/events' / f'{key}.json')
    assert event['finished_at'] == NOW.isoformat()
    assert set(event) == {'schema', 'kind', 'stage', 'source_key', 'error_type', 'finished_at'}


def test_preflight_failure_records_terminal_attempt_and_queues_failure(tmp_path, monkeypatch):
    import tradingagents.scheduled.runner as scheduled
    target = SimpleNamespace(name='daily-codex-kr', workflow_file='daily-codex-analysis.yml', inputs={'profile': 'kr'},
                             window_start_kst=NOW, max_failed_attempts=2)
    monkeypatch.setattr(automation, 'script', lambda _: SimpleNamespace(due_targets=lambda *a, **k: [target]))
    monkeypatch.setattr(scheduled, '_iter_run_manifests_desc', lambda _: [])
    def fail(_): raise RuntimeError('secret-bearing diagnostic must not be stored')
    monkeypatch.setattr(automation, 'preflight', fail)
    with pytest.raises(RuntimeError): automation.run_due(tmp_path / 'archive', tmp_path, now=NOW)
    receipt = local.read(next((tmp_path / 'attempts').glob('*.json')))
    assert receipt['exit_code'] == 1 and receipt['stage'] == 'preflight' and receipt['finished_at']
    event = local.read(next((tmp_path / 'notifications/events').glob('*.json')))
    assert event['error_type'] == 'RuntimeError'
    assert 'secret-bearing' not in json.dumps(event)


def test_notification_transport_failure_does_not_terminate_production(tmp_path, monkeypatch):
    def fail(*args, **kwargs): raise RuntimeError('transport')
    monkeypatch.setattr(local, 'reconcile', fail)
    local.reconcile_safely(tmp_path, tmp_path)


def test_workflow_keeps_cloud_path_and_uses_bound_main_local_receipt():
    workflow = yaml.safe_load(Path('.github/workflows/tradingagents-mobile-notifications.yml').read_text(encoding='utf-8'))
    jobs = workflow['jobs']
    assert 'upstream_run_id' in jobs['resolve']['if'] and "inputs.local_event_id == ''" in jobs['resolve']['if']
    job = jobs['notify_local']
    assert "github.ref == 'refs/heads/main'" in job['if']
    assert job['runs-on'] == ['tradingagents-pages']
    assert job['steps'][0]['with']['ref'] == 'main'
    assert 'DEPLOYMENT_TELEGRAM_BOT_TOKEN' in job['steps'][1]['env']['TELEGRAM_BOT_TOKEN']
    assert len(jobs['notify_remote']['steps']) == 6
