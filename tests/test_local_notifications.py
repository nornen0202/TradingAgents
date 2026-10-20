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


@pytest.mark.parametrize("published", ["current", "superseded", "pending", "live_mismatch"])
def test_notification_waits_for_publisher_then_revalidates(
        tmp_path, monkeypatch, publication_contention, published):
    archive, state, manifest, key = prepared(tmp_path, monkeypatch)
    write(state / "publication.json", {"status": "PAGES_PENDING"})

    def finish_publication():
        write(state / "publication.json", {"status": (
            "PAGES_PENDING" if published == "pending" else "DELIVERY_VERIFIED")})
        if published == "superseded":
            published_strategy(state, {**manifest, "run_id": "another-run"})

    checks = []
    monkeypatch.setattr(automation, "verify_live", lambda _: checks.append(True) or published != "live_mismatch")
    clock = publication_contention(on_release=finish_publication)
    if published == "current":
        assert local.notify(key, archive, state, dry_run=True)["status"] == "DRY_RUN"
        assert checks == [True]
    else:
        with pytest.raises(NotificationError, match="this analysis run"):
            local.notify(key, archive, state, dry_run=True)
    assert clock.released and 45 <= clock.elapsed < 46
    assert not (state / "notifications/results" / f"{key}.json").exists()


def test_busy_publisher_times_out_without_telegram_or_receipt(
        tmp_path, monkeypatch, publication_contention):
    archive, state, _, key = prepared(tmp_path, monkeypatch)
    monkeypatch.setattr(local, "TelegramBotClient", lambda **_: pytest.fail("must not send without publication lock"))
    clock = publication_contention(release_after=1000)
    with pytest.raises(TimeoutError):
        local.notify(key, archive, state)
    assert not clock.released and 0 < clock.elapsed <= 300
    assert not (state / "notifications/results" / f"{key}.json").exists()


@pytest.mark.parametrize("mode", ["full", "overlay_only"])
def test_completion_message_distinguishes_research_from_quote_refresh(tmp_path, monkeypatch, mode):
    archive, state = tmp_path / "archive", tmp_path / "state"
    manifest = completed(archive, mode)
    write(state / "publication.json", {"status": "DELIVERY_VERIFIED"})
    published_strategy(state, manifest)
    monkeypatch.setattr(automation, "verify_live", lambda _: True)
    text, _, _ = local.compose({"kind": "success", "run_id": manifest["run_id"],
                                "market": "kr", "finished_at": manifest["finished_at"]}, archive, state)
    if mode == "overlay_only":
        assert text.splitlines()[0] == "TradingAgents KR 시세·계좌 갱신 완료"
        assert "새로운 전체 분석 완료가 아닙니다" in text
        assert "30/30 갱신 성공" in text
    else:
        assert text.splitlines()[0] == "TradingAgents KR 투자 분석 완료"
        assert "30/30 분석 성공" in text
    assert "공개 전략 데이터 반영" in text


def pre_report_completed(archive, market="kr", **changes):
    values = {"run_id": f"20261012T130000_pre-report-{market}-overlay",
              "label": f"pre-report-{market}-overlay",
              "settings": {"market": market.upper(), "run_mode": "overlay_only"}}
    values.update(changes)
    return completed(archive, "overlay_only", **values)


@pytest.mark.parametrize("market", ["kr", "us"])
def test_pre_report_refresh_queues_and_sends_once_after_exact_live_publication(tmp_path, monkeypatch, market):
    archive, state = tmp_path / "archive", tmp_path / "state"
    manifest = pre_report_completed(archive, market)
    write(state / "notifications/enabled.json", {"started_at": (NOW - timedelta(days=1)).isoformat()})
    write(state / "publication.json", {"status": "DELIVERY_VERIFIED"})
    published_strategy(state, manifest)
    strategy = local.read(state / "site/mobile/strategy.json")
    strategy["markets"][market] = strategy["markets"].pop("kr")
    write(state / "site/mobile/strategy.json", strategy)
    monkeypatch.setattr(automation, "verify_live", lambda _: True)
    sent = []

    class Client:
        chat_id = "123"
        def __init__(self, **kwargs): pass
        def ensure_private_chat(self): pass
        def send_message(self, message, *, buttons):
            sent.append(message)
            return 42

    monkeypatch.setattr(local, "TelegramBotClient", Client)
    local.queue_completed(archive, state, now=NOW)
    local.queue_completed(archive, state, now=NOW + timedelta(minutes=1))
    events = list((state / "notifications/events").glob("*.json"))
    assert len(events) == 1
    assert local.notify(events[0].stem, archive, state)["status"] == "SENT"
    assert local.notify(events[0].stem, archive, state)["status"] == "NOOP"
    assert len(sent) == 1
    assert sent[0].splitlines()[0] == f"TradingAgents {market.upper()} 시세·계좌 갱신 완료"
    assert "새로운 전체 분석 완료가 아닙니다" in sent[0]


@pytest.mark.parametrize("changes", [
    {"label": "pre-report-us-overlay"},
    {"label": "pre-report-kr-overlay-custom"},
    {"label": "manual-readonly-postclose-kr"},
    {"settings": {"market": "KR", "run_mode": "full"}},
    {"settings": {"market": "KR"}},
    {"settings": {"market": "XX", "run_mode": "overlay_only"}},
])
def test_pre_report_producer_identity_is_exact_and_fails_closed(tmp_path, monkeypatch, changes):
    archive, state = tmp_path / "archive", tmp_path / "state"
    manifest = pre_report_completed(archive, **changes)
    write(state / "publication.json", {"status": "DELIVERY_VERIFIED"})
    published_strategy(state, manifest)
    monkeypatch.setattr(automation, "verify_live", lambda _: True)
    local.queue_completed(archive, state, now=NOW)
    assert not list((state / "notifications/events").glob("*.json"))
    event = {"kind": "success", "run_id": manifest["run_id"], "market": "kr",
             "finished_at": manifest["finished_at"]}
    with pytest.raises(NotificationError, match="successfully"):
        local.compose(event, archive, state)


@pytest.mark.parametrize("failure", ["previous_source", "pending_publication", "live_mismatch", "incomplete"])
def test_pre_report_refresh_keeps_existing_delivery_guards(tmp_path, monkeypatch, failure):
    archive, state = tmp_path / "archive", tmp_path / "state"
    manifest = pre_report_completed(archive)
    write(state / "notifications/enabled.json", {"started_at": (NOW - timedelta(days=1)).isoformat()})
    write(state / "publication.json", {"status": "DELIVERY_VERIFIED"})
    published_strategy(state, manifest)
    monkeypatch.setattr(automation, "verify_live", lambda _: failure != "live_mismatch")
    if failure == "previous_source":
        published_strategy(state, {**manifest, "run_id": "previous"})
    elif failure == "pending_publication":
        write(state / "publication.json", {"status": "PAGES_PENDING"})
    elif failure == "incomplete":
        manifest["active_universe"]["coverage"]["complete"] = False
        write(archive / "runs/2026" / manifest["run_id"] / "run.json", manifest)
    local.queue_completed(archive, state, now=NOW)
    if failure in {"previous_source", "pending_publication"}:
        assert not list((state / "notifications/events").glob("*.json"))
    with pytest.raises(NotificationError):
        local.compose({"kind": "success", "run_id": manifest["run_id"], "market": "kr",
                       "finished_at": manifest["finished_at"]}, archive, state)


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


def test_market_admission_yields_to_publisher_without_blocking_failures(tmp_path, monkeypatch):
    archive, state = tmp_path / "archive", tmp_path / "state"
    manifest = completed(archive)
    write(state / "publication.json", {"status": "DELIVERY_VERIFIED"})
    published_strategy(state, manifest)
    calls = []
    monkeypatch.setattr(local, "reconcile", lambda _, **kw: calls.append("existing failures"))
    with local.interprocess_file_lock(state / "publish.lock", timeout=0):
        local.reconcile_safely(archive, state)
        assert not list((state / "notifications/events").glob("*.json"))
        local.queue_completed(archive, state, now=NOW, publication_locked=True)
    assert calls == ["existing failures"]
    assert len(list((state / "notifications/events").glob("*.json"))) == 1


def test_pending_publication_preserves_success_retry_budget_but_reports_failure(tmp_path, monkeypatch):
    _, state, _, success = prepared(tmp_path, monkeypatch)
    write(state / "publication.json", {"status": "PAGES_PENDING"})
    failure = local.queue_failure(state, stage="publish", source_key="today", error_type="ValueError",
                                  finished_at=NOW.isoformat())
    calls = []
    local.reconcile(state, now=NOW, runner=lambda args, **kw: calls.append(args) or SimpleNamespace(
        returncode=0, stdout="[]"))
    assert not (state / "notifications/dispatches" / f"{success}.json").exists()
    assert local.read(state / "notifications/dispatches" / f"{failure}.json")["attempts"] == 1
    assert sum(c[1] == "workflow" for c in calls) == 1


def test_busy_rebuild_under_old_verified_receipt_does_not_spend_completion_attempt(tmp_path, monkeypatch):
    archive, state, _, success = prepared(tmp_path, monkeypatch)
    failure = local.queue_failure(state, stage="publish", source_key="today", error_type="ValueError",
                                  finished_at=NOW.isoformat())
    actual = local.reconcile
    calls = []
    def reconcile(destination, **kwargs):
        return actual(destination, now=NOW, runner=lambda args, **kw: calls.append(args) or SimpleNamespace(
            returncode=0, stdout="[]"), **kwargs)
    monkeypatch.setattr(local, "reconcile", reconcile)
    with local.interprocess_file_lock(state / "publish.lock", timeout=0):
        local.reconcile_safely(archive, state)
    assert not (state / "notifications/dispatches" / f"{success}.json").exists()
    assert local.read(state / "notifications/dispatches" / f"{failure}.json")["attempts"] == 1
    assert sum(c[1] == "workflow" for c in calls) == 1


@pytest.mark.parametrize("invalid", [None, "full_original", "missing", "failed", "older", "future",
                                     "wrong_market", "incomplete", "wrong_lineage", "not_live", "pending"])
def test_only_verified_newer_overlay_can_retire_obsolete_notice(tmp_path, monkeypatch, invalid):
    archive, state = tmp_path / "archive", tmp_path / "state"
    old = completed(archive, mode="full" if invalid == "full_original" else "overlay_only")
    key = local.queue(state, {"kind": "success", "run_id": old["run_id"], "market": "kr",
                              "finished_at": old["finished_at"]})
    newer = completed(archive, mode="overlay_only", run_id="20261012T073000_local-freshness-kr-overlay",
                      started_at=(NOW - timedelta(minutes=45)).isoformat(),
                      finished_at=(NOW - timedelta(minutes=30)).isoformat())
    if invalid == "failed": newer["status"] = "failed"
    if invalid == "older": newer["finished_at"] = (NOW - timedelta(hours=2)).isoformat()
    if invalid == "future": newer["finished_at"] = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
    if invalid == "wrong_market": newer["settings"]["market"] = "US"
    if invalid == "incomplete": newer["active_universe"]["coverage"]["complete"] = False
    path = archive / "runs/2026" / newer["run_id"] / "run.json"
    write(path, newer)
    if invalid == "missing": path.unlink()
    write(state / "publication.json", {"status": "PAGES_PENDING" if invalid == "pending" else "DELIVERY_VERIFIED"})
    published_strategy(state, newer)
    if invalid == "wrong_lineage":
        payload = local.read(state / "site/mobile/strategy.json")
        payload["markets"]["kr"]["freshness_receipt"]["producer_run_id"] = "unbound"
        write(state / "site/mobile/strategy.json", payload)
    monkeypatch.setattr(automation, "verify_live", lambda _: invalid != "not_live")
    monkeypatch.setattr(local, "TelegramBotClient", lambda **kw: pytest.fail("Obsolete notice sent"))
    if invalid:
        with pytest.raises(NotificationError): local.notify(key, archive, state)
        assert not (state / "notifications/results" / f"{key}.json").exists()
    else:
        result = local.notify(key, archive, state)
        assert result["status"] == "NOOP" and result["message_ids"] == []
        assert result["reason"] == "SUPERSEDED_BY_VERIFIED_PUBLICATION"
        assert result["superseded_by_run_id"] == newer["run_id"]
        local.reconcile(state, now=NOW, runner=lambda *a, **kw: pytest.fail("Repeated skip dispatch"))
        assert local.read(state / "notifications/dispatches" / f"{key}.json")["status"] == "POLICY_SKIPPED"
        # A later policy check must never overwrite an existing SENT receipt.
        path = state / "notifications/results" / f"{key}.json"
        write(path, {"status": "SENT", "local_event_id": key, "message_ids": [42]})
        before = path.read_bytes()
        assert local.notify(key, archive, state)["status"] == "SENT"
        assert path.read_bytes() == before


def test_workflow_keeps_cloud_path_and_uses_bound_main_local_receipt():
    workflow = yaml.safe_load(Path('.github/workflows/tradingagents-mobile-notifications.yml').read_text(encoding='utf-8'))
    jobs = workflow['jobs']
    assert 'upstream_run_id' in jobs['resolve']['if'] and "inputs.local_event_id == ''" in jobs['resolve']['if']
    job = jobs['notify_local']
    assert "github.ref == 'refs/heads/main'" in job['if']
    assert job['runs-on'] == ['tradingagents-pages']
    assert job['steps'][0]['with']['ref'] == 'main'
    sender = next(step for step in job['steps'] if 'TELEGRAM_BOT_TOKEN' in step.get('env', {}))
    assert 'DEPLOYMENT_TELEGRAM_BOT_TOKEN' in sender['env']['TELEGRAM_BOT_TOKEN']
    fallback = next(step for step in job['steps'] if step.get('uses', '').startswith('actions/setup-python@'))
    assert "steps.local_python.outputs.unavailable == 'true'" in fallback['if']
    assert fallback['with']['python-version'] == '3.13'
    probe = next(step for step in job['steps'] if step.get('id') == 'local_python')
    assert not probe.get('env') and 'secrets.' not in probe['run']
    assert 'WaitForExit(10000)' in probe['run']
    assert "$env:LOCAL_PYTHON_UNAVAILABLE -eq 'true'" in sender['run']
    assert "Join-Path $env:pythonLocation 'python.exe'" in sender['run']
    assert len(jobs['notify_remote']['steps']) == 6
