from copy import deepcopy
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest

from tradingagents.atomic_io import interprocess_file_lock
from tradingagents.work import pre_report as pre


NOW = datetime.now(timezone.utc)


def packet():
    return {"body": {"source_health": "OK", "current": {
        "universe_coverage": {"status": "COMPLETE"},
        "freshness_receipt": {"producer_run_id": "refreshed", "market_data_status": "FRESH",
            "market_data_oldest_at": NOW.isoformat(), "market_data_latest_at": NOW.isoformat(),
            "account_as_of": NOW.isoformat(), "account_snapshot_health": "VALID",
            "analysis_lineage_status": "RESOLVED", "analysis_completed_at": NOW.isoformat()},
        "bundle": {"strategy_table": [{"execution": {"valid_until": (NOW+timedelta(minutes=10)).isoformat()}}]}}}}


def test_real_observations_and_full_coverage_required():
    original = packet()
    assert pre.freshness_blockers(original, now=NOW, started_at=NOW, run_id="refreshed") == []
    assert original == packet()


@pytest.mark.parametrize("field,value", [
    ("market_data_oldest_at", None),
    ("market_data_oldest_at", (NOW - timedelta(minutes=1)).isoformat()),
    ("market_data_latest_at", (NOW + timedelta(seconds=1)).isoformat()),
    ("account_as_of", "bad"),
    ("account_as_of", (NOW - timedelta(minutes=30)).isoformat()),
    ("account_snapshot_health", "WATCHLIST_ONLY"),
    ("market_data_status", "STALE"),
    ("producer_run_id", "cached-previous-run"),
    ("analysis_lineage_status", "UNVERIFIED"),
    ("analysis_completed_at", (NOW - timedelta(hours=36)).isoformat()),
])
def test_copied_or_invalid_input_is_never_made_current(field, value):
    item = packet()
    item["body"]["current"]["freshness_receipt"][field] = value
    assert pre.freshness_blockers(item, now=NOW, started_at=NOW, run_id="refreshed")


def test_long_refresh_and_incomplete_coverage_block():
    item = packet()
    item["body"]["current"]["universe_coverage"]["status"] = "INCOMPLETE"
    assert "UNIVERSE_NOT_COMPLETE" in pre.freshness_blockers(item, now=NOW, started_at=NOW, run_id="refreshed")
    assert pre.freshness_blockers(packet(), now=NOW + timedelta(minutes=10), started_at=NOW, run_id="refreshed")


def test_final_publish_clock_cannot_be_renewed_by_report_timestamp():
    item = packet()
    item["body"]["current"]["bundle"] = {"strategy_table": [
        {"execution": {"valid_until": (NOW + timedelta(minutes=10)).isoformat()}}]}
    assert pre.publish_freshness_blockers(item, now=NOW + timedelta(minutes=9, seconds=59)) == []
    assert pre.publish_freshness_blockers(item, now=NOW + timedelta(minutes=10))
    item["body"]["current"]["bundle"]["strategy_table"][0]["execution"]["valid_until"] = NOW.isoformat()
    assert "ROW_VALIDITY_EXPIRED_OR_MISSING" in pre.publish_freshness_blockers(item, now=NOW)


@pytest.fixture
def wired(tmp_path, monkeypatch):
    from tradingagents import local_automation
    monkeypatch.setattr(local_automation, "prepare_environment", lambda: None)
    monkeypatch.setattr(local_automation, "require_storage_headroom", lambda *a: None)
    monkeypatch.setattr(pre, "market_session_state", lambda **kw: {"is_open": True, "phase": "regular"})
    monkeypatch.setattr(pre, "automated_market_session_status", lambda **kw: SimpleNamespace(is_session=True))
    monkeypatch.setattr(pre, "resolve_archive_roots", lambda **kw: {"market": tmp_path / "archive"})
    prepared, configs = [], []
    def prepare(*args, **kw):
        from tradingagents.work.runtime import FreshReportSourceError
        current = datetime.now(timezone.utc)
        item = pre.build_surface_packet(*args, now=current)
        blockers = pre.freshness_blockers(item, now=current, started_at=kw['refresh_started_at'],
            run_id=kw['expected_producer_run_id']) + pre.publish_freshness_blockers(item, now=current)
        if blockers:
            raise FreshReportSourceError(blockers)
        prepared.append(kw)
        return {"result": "NEW", "event_id": "new", "verified_refresh_observations": item['body']['current']['freshness_receipt']}
    runtime = SimpleNamespace(prepare=prepare)

    def execute(config, **kw):
        assert kw["paper_state_dir"] == tmp_path
        assert kw["defer_execution_handoff"] is True
        print("Broker collection progress")
        configs.append(config)
        return {"run_id": "refreshed", "status": "success"}

    def current_packet(*a, **kw):
        item = packet()
        observed = kw["now"].isoformat()
        for field in ("market_data_oldest_at", "market_data_latest_at", "account_as_of"):
            item["body"]["current"]["freshness_receipt"][field] = observed
        item['body']['current']['bundle']['strategy_table'][0]['execution']['valid_until'] = (kw['now']+timedelta(seconds=120)).isoformat()
        return item

    monkeypatch.setattr(pre, "execute_scheduled_run", execute)
    monkeypatch.setattr(pre, "handoff_completed_run", lambda *a, **kw: None)
    monkeypatch.setattr(pre, "build_surface_packet", current_packet)
    return runtime, prepared, configs


@pytest.mark.parametrize("surface", ["kr", "us"])
def test_refresh_before_prepare_preserves_models_and_does_not_rerun_research(wired, tmp_path, surface, capsys):
    runtime, prepared, configs = wired
    result = pre.prepare_market_report(runtime, surface, producer_state_dir=tmp_path)
    assert result["result"] == "NEW"
    assert result["pre_report_refresh"]["status"] == "REFRESHED"
    assert result["pre_report_refresh"]["event_created"] is True
    assert len(prepared) == len(configs) == 1
    assert capsys.readouterr().out == ""
    assert "Broker collection progress" in (tmp_path / "pre-report" / f"{surface}-worker.log").read_text()
    config = configs[0]
    assert config.run.run_mode == "overlay_only"
    assert config.llm.deep_model == config.llm.judge_model == "gpt-6.1-sol"
    assert config.llm.codex_deep_reasoning_effort == config.llm.codex_judge_reasoning_effort == "xhigh"
    assert config.execution.execution_session_gate_enabled
    assert config.execution.execution_lightweight_refresh is True
    assert config.execution.execution_max_data_age_seconds == 120
    assert config.execution.execution_llm_summary_model is None
    assert not config.execution.execution_selective_rerun_enabled
    assert len(config.execution.execution_refresh_checkpoints_local) == 1
    assert prepared[0]["expected_producer_run_id"] == "refreshed"
    assert prepared[0]["refresh_started_at"].utcoffset() is not None


def test_writer_lock_only_covers_collection_not_packet_build_or_event_prepare(wired, tmp_path, monkeypatch):
    runtime, prepared, configs = wired
    execute, build, prepare = pre.execute_scheduled_run, pre.build_surface_packet, runtime.prepare
    phases = []
    def collect(*args, **kwargs):
        with pytest.raises(TimeoutError), interprocess_file_lock(tmp_path / "run-due.lock", timeout=0):
            pytest.fail("another producer must not enter during collection")
        phases.append("collection_locked")
        return execute(*args, **kwargs)
    def build_packet(*args, **kwargs):
        with interprocess_file_lock(tmp_path / "run-due.lock", timeout=0):
            phases.append("packet_read_unlocked")
        return build(*args, **kwargs)
    def consume(*args, **kwargs):
        with interprocess_file_lock(tmp_path / "run-due.lock", timeout=0):
            phases.append("consumer_handoff_unlocked")
    def allocate(*args, **kwargs):
        with interprocess_file_lock(tmp_path / "run-due.lock", timeout=0):
            phases.append("event_prepare_unlocked")
        return prepare(*args, **kwargs)
    monkeypatch.setattr(pre, "execute_scheduled_run", collect)
    monkeypatch.setattr(pre, "handoff_completed_run", consume)
    monkeypatch.setattr(pre, "build_surface_packet", build_packet)
    runtime.prepare = allocate
    result = pre.prepare_market_report(runtime, "us", producer_state_dir=tmp_path)
    assert result["result"] == "NEW"
    assert phases == ["collection_locked", "consumer_handoff_unlocked", "event_prepare_unlocked", "packet_read_unlocked"]


def test_owned_refresh_constructs_exactly_one_guarded_packet(wired, tmp_path, monkeypatch):
    runtime, prepared, configs = wired
    original = pre.build_surface_packet
    calls = []
    def build(*args, **kwargs):
        calls.append(kwargs)
        return original(*args, **kwargs)
    monkeypatch.setattr(pre, 'build_surface_packet', build)
    assert pre.prepare_market_report(runtime, 'us', producer_state_dir=tmp_path)['result'] == 'NEW'
    assert len(calls) == len(prepared) == 1


def test_fresh_fixture_validity_is_not_anchored_to_test_collection_time(wired, tmp_path, monkeypatch):
    import sys
    monkeypatch.setattr(sys.modules[__name__], 'NOW', datetime.now(timezone.utc)-timedelta(hours=2))
    runtime, prepared, configs = wired
    assert pre.prepare_market_report(runtime, 'us', producer_state_dir=tmp_path)['result'] == 'NEW'


def test_expired_cold_read_retries_one_actual_overlay_and_keeps_both_receipts(wired, tmp_path, monkeypatch):
    import json
    from tradingagents.work.runtime import FreshReportSourceError
    runtime, prepared, configs = wired
    original_execute = pre.execute_scheduled_run
    def execute(*args, **kwargs):
        manifest = original_execute(*args, **kwargs)
        manifest['run_id'] = f'refreshed-{len(configs)}'
        return manifest
    calls = []
    def prepare(*args, **kwargs):
        calls.append(kwargs['expected_producer_run_id'])
        if len(calls) == 1:
            raise FreshReportSourceError(['ROW_VALIDITY_EXPIRED_OR_MISSING'], retryable_expiry=True)
        return {'result': 'NEW', 'event_id': 'second-only',
                'verified_refresh_observations': {'producer_run_id': kwargs['expected_producer_run_id']}}
    runtime.prepare = prepare
    monkeypatch.setattr(pre, 'execute_scheduled_run', execute)
    result = pre.prepare_market_report(runtime, 'us', producer_state_dir=tmp_path)
    receipt = result['pre_report_refresh']
    assert calls == ['refreshed-1', 'refreshed-2'] and len(configs) == 2
    assert result['event_id'] == 'second-only' and receipt['refresh_attempt_count'] == receipt['refresh_attempt_limit'] == 2
    first, second = receipt['refresh_attempts']
    assert first['event_created'] is False and first['producer_run_id'] == 'refreshed-1'
    assert first['status'] == 'FRESH_INPUT_UNAVAILABLE' and second['status'] == 'REFRESHED'
    assert second['observations']['producer_run_id'] == 'refreshed-2'
    history = list((tmp_path / 'pre-report/refresh-attempts').glob('*.json'))
    assert len(history) == 1
    durable = json.loads(history[0].read_text(encoding='utf-8'))
    assert durable['attempts'] == receipt['refresh_attempts']
    assert durable['research_rerun'] is False and durable['live_orders_submitted'] is False
    assert all(c.run.run_mode == 'overlay_only' and not c.execution.execution_selective_rerun_enabled
               and c.execution.execution_llm_summary_model is None for c in configs)


def test_repeated_expiry_stops_at_two_without_allocating_an_event(wired, tmp_path):
    from tradingagents.work.runtime import FreshReportSourceError
    runtime, prepared, configs = wired
    def fail(*args, **kwargs):
        raise FreshReportSourceError(['ROW_VALIDITY_EXPIRED_OR_MISSING'], retryable_expiry=True)
    runtime.prepare = fail
    result = pre.prepare_market_report(runtime, 'us', producer_state_dir=tmp_path)
    assert result['status'] == 'FRESH_INPUT_UNAVAILABLE' and result['event_created'] is False
    assert len(configs) == result['refresh_attempt_count'] == result['refresh_attempt_limit'] == 2
    assert len(result['refresh_attempts']) == 2 and not prepared


@pytest.mark.parametrize('blockers,retryable', [
    (['ROW_VALIDITY_EXPIRED_OR_MISSING'], False),
    (['ACCOUNT_NOT_VALID'], True),
    (['ROW_VALIDITY_EXPIRED_OR_MISSING', 'SESSION_ENDED_DURING_PREPARE'], True),
    (['MARKET_DATA_FROM_FUTURE'], True),
])
def test_other_or_unverified_failures_do_not_retry_broker_collection(wired, tmp_path, blockers, retryable):
    from tradingagents.work.runtime import FreshReportSourceError
    runtime, prepared, configs = wired
    def fail(*args, **kwargs):
        raise FreshReportSourceError(blockers, retryable_expiry=retryable)
    runtime.prepare = fail
    result = pre.prepare_market_report(runtime, 'us', producer_state_dir=tmp_path)
    assert result['status'] == 'FRESH_INPUT_UNAVAILABLE' and len(configs) == 1 and not prepared
    assert not (tmp_path / 'pre-report/refresh-attempts').exists()


def test_retry_never_competes_with_a_new_healthy_producer(wired, tmp_path):
    from tradingagents.work.runtime import FreshReportSourceError
    runtime, prepared, configs = wired
    owner = interprocess_file_lock(tmp_path / 'run-due.lock', timeout=0)
    def fail(*args, **kwargs):
        owner.__enter__()
        raise FreshReportSourceError(['ROW_VALIDITY_EXPIRED_OR_MISSING'], retryable_expiry=True)
    runtime.prepare = fail
    try:
        result = pre.prepare_market_report(runtime, 'us', producer_state_dir=tmp_path)
        assert result['status'] == 'BUSY_NO_STATE_ADVANCE' and result['event_created'] is False
        assert len(configs) == 1 and not prepared
        with pytest.raises(TimeoutError), interprocess_file_lock(tmp_path / 'run-due.lock', timeout=0):
            pytest.fail('Existing producer ownership must be preserved')
    finally:
        owner.__exit__(None, None, None)


def test_market_closing_before_retry_prevents_another_collection(wired, tmp_path, monkeypatch):
    from tradingagents.work.runtime import FreshReportSourceError
    runtime, prepared, configs = wired
    states = iter([True, True, True, False])
    monkeypatch.setattr(pre, 'market_session_state', lambda **kwargs: {'is_open': next(states), 'phase': 'closed'})
    def fail(*args, **kwargs):
        raise FreshReportSourceError(['ROW_VALIDITY_EXPIRED_OR_MISSING'], retryable_expiry=True)
    runtime.prepare = fail
    result = pre.prepare_market_report(runtime, 'us', producer_state_dir=tmp_path)
    assert result['status'] == 'MARKET_CLOSED' and result['event_created'] is False
    assert len(configs) == 1 and not prepared and result['refresh_attempt_count'] == 2


def test_busy_producer_does_not_start_or_allocate_event(wired, tmp_path):
    runtime, prepared, configs = wired
    with interprocess_file_lock(tmp_path / "run-due.lock", timeout=0):
        result = pre.prepare_market_report(runtime, "us", producer_state_dir=tmp_path)
    assert result["status"] == "BUSY_NO_STATE_ADVANCE"
    assert not prepared and not configs


def test_closed_market_has_no_report_or_broker_calls(wired, tmp_path, monkeypatch):
    runtime, prepared, configs = wired
    monkeypatch.setattr(pre, "market_session_state", lambda **kw: {"is_open": False, "phase": "closed"})
    result = pre.prepare_market_report(runtime, "us", producer_state_dir=tmp_path)
    assert result["status"] == "MARKET_CLOSED"
    assert not prepared and not configs


@pytest.mark.parametrize("is_session,expected", [(False, "MARKET_CLOSED"), (None, "CALENDAR_UNVERIFIED")])
def test_official_calendar_can_veto_exchange_clock(wired, tmp_path, monkeypatch, is_session, expected):
    runtime, prepared, configs = wired
    monkeypatch.setattr(pre, "automated_market_session_status",
                        lambda **kw: SimpleNamespace(is_session=is_session, source="official"))
    result = pre.prepare_market_report(runtime, "kr", producer_state_dir=tmp_path)
    assert result["status"] == expected
    assert not prepared and not configs


def test_session_ending_during_refresh_does_not_allocate_event(wired, tmp_path, monkeypatch):
    runtime, prepared, configs = wired
    states = iter([True, True, False])
    monkeypatch.setattr(pre, "market_session_state", lambda **kw: {"is_open": next(states), "phase": "regular"})
    result = pre.prepare_market_report(runtime, "us", producer_state_dir=tmp_path)
    assert result["status"] == "FRESH_INPUT_UNAVAILABLE"
    assert "SESSION_ENDED_DURING_REFRESH" in result["blockers"]
    assert not prepared


def test_failed_account_does_not_allocate_event(wired, tmp_path, monkeypatch):
    runtime, prepared, configs = wired
    monkeypatch.setattr(pre, "build_surface_packet", lambda *a, **kw: packet())
    item = packet()
    item["body"]["current"]["freshness_receipt"]["account_snapshot_health"] = "WATCHLIST_ONLY"
    monkeypatch.setattr(pre, "build_surface_packet", lambda *a, **kw: deepcopy(item))
    result = pre.prepare_market_report(runtime, "kr", producer_state_dir=tmp_path)
    assert result["status"] == "FRESH_INPUT_UNAVAILABLE"
    assert "ACCOUNT_NOT_VALID" in result["blockers"]
    assert not prepared


@pytest.mark.parametrize("error", [RuntimeError, TimeoutError])
def test_broker_error_receipt_does_not_leak_request(wired, tmp_path, monkeypatch, error):
    runtime, prepared, configs = wired

    def fail(*a, **kw):
        raise error("secret account request")

    monkeypatch.setattr(pre, "execute_scheduled_run", fail)
    result = pre.prepare_market_report(runtime, "kr", producer_state_dir=tmp_path)
    assert result["status"] == "FRESH_INPUT_UNAVAILABLE"
    assert "secret" not in str(result)
    assert not prepared


@pytest.mark.parametrize("case", ["fresh", "expired", "future", "running", "missing", "wrong_id", "bad_account", "changed_during_prepare"])
def test_busy_adoption_requires_immutable_same_run_and_current_observations(wired, tmp_path, monkeypatch, case):
    import json
    runtime, prepared, configs = wired
    current = datetime.now(timezone.utc)
    started = current - timedelta(seconds=30)
    finished = current - timedelta(seconds=1)
    run_id = "20261029T000000-existing"
    item = packet()
    receipt = item["body"]["current"]["freshness_receipt"]
    receipt["producer_run_id"] = run_id
    for field in ("market_data_oldest_at", "market_data_latest_at", "account_as_of"):
        receipt[field] = current.isoformat()
    item['body']['current']['bundle']['strategy_table'][0]['execution']['valid_until'] = (current+timedelta(seconds=120)).isoformat()
    if case == "bad_account": receipt["account_snapshot_health"] = "INVALID"
    monkeypatch.setattr(pre, "build_surface_packet", lambda *a, **kw: deepcopy(item))
    path = tmp_path/"archive"/"runs"/"2026"/run_id/"run.json"
    path.parent.mkdir(parents=True)
    manifest = {"run_id":run_id,"status":"success","started_at":started.isoformat(),"finished_at":finished.isoformat()}
    if case == "expired": manifest["finished_at"] = (current-timedelta(minutes=3)).isoformat()
    if case == "future": manifest["finished_at"] = (current+timedelta(minutes=1)).isoformat()
    if case == "running": manifest["status"] = "running"
    if case == "wrong_id": manifest["run_id"] = "other"
    if case != "missing": path.write_text(json.dumps(manifest))
    if case == "changed_during_prepare":
        def reject(*a, **kw): raise RuntimeError("run no longer selected")
        runtime.prepare = reject
    with interprocess_file_lock(tmp_path/"run-due.lock", timeout=0):
        result = pre.prepare_market_report(runtime, "us", producer_state_dir=tmp_path)
    assert not configs
    if case == "fresh":
        assert result["pre_report_refresh"]["status"] == "ADOPTED_COMPLETED_PRODUCER"
        assert prepared[0]["expected_producer_run_id"] == run_id
        assert prepared[0]["refresh_started_at"] == started
    else:
        assert result["status"] == "BUSY_NO_STATE_ADVANCE"
        assert not prepared
