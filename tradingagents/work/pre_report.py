"""Acquire real broker observations before allocating an immutable Work event.

This reuses completed research through an overlay; it never submits an order or
reruns company research. Publication timestamps cannot renew input validity.
"""
from __future__ import annotations

from dataclasses import replace
from contextlib import contextmanager, redirect_stderr, redirect_stdout
from datetime import datetime, timedelta, timezone
from pathlib import Path
import json
from zoneinfo import ZoneInfo
from uuid import uuid4

from tradingagents.atomic_io import atomic_write_json, interprocess_file_lock
from tradingagents.scheduled.config import load_scheduled_config
from tradingagents.scheduled.automation_calendar import automated_market_session_status
from tradingagents.scheduled.market_calendar import market_session_state
from tradingagents.scheduled.runner import execute_scheduled_run
from tradingagents.dataflows.market_policy import MAX_EXECUTION_AGE, observation_status
from tradingagents.execution.delivery import handoff_completed_run

from .freshness import aware_datetime
from .packet import build_surface_packet, resolve_archive_roots, load_json

ROOT = Path(__file__).resolve().parents[2]
MAX_PREPARE_AGE = MAX_EXECUTION_AGE


class ProducerBusy(RuntimeError):
    pass


@contextmanager
def producer_lock(path):
    lock = interprocess_file_lock(path, timeout=0)
    try:
        lock.__enter__()
    except TimeoutError as exc:
        raise ProducerBusy from exc
    try:
        yield
    finally:
        lock.__exit__(None, None, None)


def freshness_blockers(packet: dict, *, now: datetime, started_at: datetime, run_id: str) -> list[str]:
    """Require observations from this producer window, not a recently copied cache."""
    body = packet.get("body") or {}
    current = body.get("current") or {}
    receipt = current.get("freshness_receipt") or {}
    blockers = []
    if receipt.get("producer_run_id") != run_id:
        blockers.append("REFRESH_RUN_NOT_SELECTED")
    if receipt.get("market_data_status") != "FRESH":
        blockers.append("MARKET_DATA_NOT_FRESH")
    # Allow minute-resolution provider clocks, but not a previous overlay.
    floor = started_at.replace(second=0, microsecond=0)
    for field in ("market_data_oldest_at", "market_data_latest_at", "account_as_of"):
        observed = aware_datetime(receipt.get(field))
        if observed is None or not floor <= observed <= now or now - observed >= MAX_PREPARE_AGE:
            blockers.append(field.upper() + "_NOT_CURRENT")
    if receipt.get("account_snapshot_health") != "VALID":
        blockers.append("ACCOUNT_NOT_VALID")
    analysis_at = aware_datetime(receipt.get("analysis_completed_at"))
    if (receipt.get("analysis_lineage_status") != "RESOLVED" or analysis_at is None
            or not timedelta(0) <= now - analysis_at < timedelta(hours=36)):
        blockers.append("ANALYSIS_LINEAGE_OR_AGE_INVALID")
    if (current.get("universe_coverage") or {}).get("status") != "COMPLETE":
        blockers.append("UNIVERSE_NOT_COMPLETE")
    if body.get("source_health") != "OK":
        blockers.append("SOURCE_NOT_HEALTHY")
    return blockers


def publish_freshness_blockers(packet: dict, *, now: datetime) -> list[str]:
    current = (packet.get("body") or {}).get("current") or {}
    receipt = current.get("freshness_receipt") or {}
    blockers = []
    for field in ("market_data_oldest_at", "market_data_latest_at", "account_as_of"):
        observed = aware_datetime(receipt.get(field))
        if not observation_status(receipt.get(field), as_of=now)["eligible"]:
            blockers.append(field.upper() + "_EXPIRED_OR_INVALID")
    if receipt.get("account_snapshot_health") != "VALID":
        blockers.append("ACCOUNT_NOT_VALID")
    rows = (current.get("bundle") or {}).get("strategy_table") or []
    if not rows:
        blockers.append("NO_MARKET_ROWS")
    for row in rows:
        expiry = aware_datetime((row.get("execution") or {}).get("valid_until"))
        if expiry is None or expiry <= now:
            blockers.append("ROW_VALIDITY_EXPIRED_OR_MISSING")
            break
    return blockers


def completed_busy_source(surface: str, *, archive: Path, config,
                          youtube_archive_dir=None, prism_archive_dir=None):
    """Select only an immutable, genuinely current completed producer.

    This is a read-only consumer of a completed run, never ownership of the
    active writer. Runtime.prepare pins this same run and revalidates clocks.
    """
    now = datetime.now(timezone.utc)
    pointer = load_json(archive / 'latest-run.json')
    settings = pointer.get('settings') if isinstance(pointer.get('settings'), dict) else {}
    candidate = str(pointer.get('run_id') or '') if str(settings.get('market') or '').lower() == surface else None
    packet = build_surface_packet(surface, archive_dir=archive,
        youtube_archive_dir=youtube_archive_dir, prism_archive_dir=prism_archive_dir, now=now,
        **({'expected_producer_run_id': candidate} if candidate else {}))
    receipt = (packet.get("body", {}).get("current", {}).get("freshness_receipt") or {})
    run_id = str(receipt.get("producer_run_id") or "")
    if not run_id or Path(run_id).name != run_id or "/" in run_id or "\\" in run_id:
        return None
    path = archive / "runs" / run_id[:4] / run_id / "run.json"
    if not path.is_file():
        return None
    manifest = json.loads(path.read_text(encoding="utf-8"))
    started = aware_datetime(manifest.get("started_at"))
    finished = aware_datetime(manifest.get("finished_at"))
    now = datetime.now(timezone.utc)
    if (manifest.get("run_id") != run_id or manifest.get("status") != "success"
            or started is None or finished is None or not started <= finished <= now
            or now - finished >= MAX_PREPARE_AGE):
        return None
    session = market_session_state(market=surface.upper(), now_local=now,
                                   calendar_name=config.execution.execution_session_calendar)
    if not session.get("is_open") or automated_market_session_status(market=surface, now=now).is_session is not True:
        return None
    if freshness_blockers(packet, now=now, started_at=started, run_id=run_id):
        return None
    return manifest, started, receipt


def prepare_market_report(runtime, surface: str, *, producer_state_dir: Path,
                          archive_dir: Path | None = None, youtube_archive_dir: Path | None = None,
                          prism_archive_dir: Path | None = None, report_context_v1: bool = False) -> dict:
    """Retry actual broker collection once only for verified row expiry.

    Slow cold reads may consume a valid producer's short row lifetime. The
    second attempt uses the same producer lock, calendar checks and immutable
    runtime validation; it never renews the first input or reruns research.
    """
    options = dict(producer_state_dir=producer_state_dir, archive_dir=archive_dir,
        youtube_archive_dir=youtube_archive_dir, prism_archive_dir=prism_archive_dir,
        report_context_v1=report_context_v1)
    first = _prepare_market_report_once(runtime, surface, **options)
    if not (first.get('status') == 'FRESH_INPUT_UNAVAILABLE'
            and set(first.get('blockers') or []) == {'ROW_VALIDITY_EXPIRED_OR_MISSING'}
            and first.get('retryable_expiry') is True and first.get('event_created') is False):
        return first
    receipt_id = uuid4().hex
    history_path = Path(producer_state_dir) / 'pre-report' / 'refresh-attempts' / f'{surface}-{receipt_id}.json'
    history = {'schema': 'tradingagents.pre-report-attempts/v1', 'surface': surface,
        'refresh_attempt_limit': 2, 'attempts': [first], 'status': 'RETRYING_ACTUAL_BROKER_REFRESH',
        'research_rerun': False, 'live_orders_submitted': False}
    # Preserve the failed observation even if the process stops during retry.
    atomic_write_json(history_path, history)
    second = _prepare_market_report_once(runtime, surface, **options)
    current = dict(second.get('pre_report_refresh') or second)
    history.update(status=current.get('status'), attempts=[first, dict(current)],
        finished_at=datetime.now(timezone.utc).isoformat())
    atomic_write_json(history_path, history)
    current.update(refresh_attempt_count=2, refresh_attempt_limit=2,
        refresh_attempt_receipt_id=receipt_id, refresh_attempts=history['attempts'])
    atomic_write_json(Path(producer_state_dir) / 'pre-report' / f'{surface}.json', current)
    return {**second, 'pre_report_refresh': current} if 'pre_report_refresh' in second else current


def _prepare_market_report_once(runtime, surface: str, *, producer_state_dir: Path,
                          archive_dir: Path | None = None, youtube_archive_dir: Path | None = None,
                          prism_archive_dir: Path | None = None, report_context_v1: bool = False) -> dict:
    if surface not in {"kr", "us"}:
        raise ValueError("Broker refresh only supports kr/us")
    from .runtime import FreshReportSourceError
    state = Path(producer_state_dir)
    receipt_path = state / "pre-report" / f"{surface}.json"
    receipt = {"schema": "tradingagents.pre-report-refresh/v1", "surface": surface,
               "status": "ERROR", "event_created": False, "live_orders_submitted": False}

    def finish(**fields):
        receipt.update(fields, checked_at=datetime.now(timezone.utc).isoformat())
        atomic_write_json(receipt_path, receipt)
        return dict(receipt)

    # Same lock as the minute production lane. Never start a competing
    # writer or kill a healthy worker. BUSY may consume only an independently
    # validated completed result; it never uses the active writer's artifacts.
    try:
        config = load_scheduled_config(ROOT / "config" / (
            "scheduled_analysis_korea.toml" if surface == "kr" else "scheduled_analysis.toml"))
        session = market_session_state(market=surface.upper(), now_local=datetime.now(timezone.utc),
                                       calendar_name=config.execution.execution_session_calendar)
        if not session.get("is_open"):
            return finish(status="MARKET_CLOSED" if session.get("phase") == "closed" else "CALENDAR_UNVERIFIED",
                          session=session)
        with producer_lock(state / "run-due.lock"):
            from tradingagents.local_automation import prepare_environment, require_storage_headroom
            prepare_environment()
            archive = resolve_archive_roots(archive_dir=archive_dir)["market"]
            started = datetime.now(timezone.utc)
            session = market_session_state(market=surface.upper(), now_local=started,
                                           calendar_name=config.execution.execution_session_calendar)
            if not session.get("is_open"):
                return finish(status="MARKET_CLOSED" if session.get("phase") == "closed" else "CALENDAR_UNVERIFIED",
                              session=session)
            official = automated_market_session_status(market=surface, now=started)
            if official.is_session is not True:
                return finish(status="MARKET_CLOSED" if official.is_session is False else "CALENDAR_UNVERIFIED",
                              session=session, calendar_source=official.source)
            require_storage_headroom(archive, state, config.llm.codex_workspace_dir)
            checkpoint = started.astimezone(ZoneInfo(config.execution.execution_checkpoint_timezone)).strftime("%H:%M")
            config = replace(config,
                run=replace(config.run, run_mode="overlay_only"),
                storage=replace(config.storage, archive_dir=archive),
                execution=replace(config.execution, execution_refresh_enabled=True,
                    execution_lightweight_refresh=True, execution_max_data_age_seconds=120,
                    execution_llm_summary_model=None,
                    execution_refresh_checkpoints_kst=(), execution_refresh_checkpoints_local=(checkpoint,),
                    execution_session_gate_enabled=True, execution_selective_rerun_enabled=False),
            )
            # Preserve the Work CLI's single JSON response. Producer progress
            # belongs in local maintenance logs, not the consumer packet/output.
            receipt_path.parent.mkdir(parents=True, exist_ok=True)
            with (receipt_path.parent / f"{surface}-worker.log").open("a", encoding="utf-8") as log:
                with redirect_stdout(log), redirect_stderr(log):
                    manifest = execute_scheduled_run(config, run_label=f"pre-report-{surface}-overlay",
                        skip_site_build=True, paper_state_dir=state, defer_execution_handoff=True)
                    receipt['producer_run_id'] = manifest.get('run_id')
        # Completed producer artifacts are immutable. Release writer ownership
        # before the expensive read-only packet builds and Work state lock.
        # Runtime.prepare checks the exact run and clocks again before allocation.
        # Inline consumers may wait on broker/account locks. Keep their normal
        # guarded handoff, but never hold the producer lock while they finish.
        handoff_completed_run(archive, manifest, state_root=state)
        now = datetime.now(timezone.utc)
        blockers = []
        session = market_session_state(market=surface.upper(), now_local=now,
                                       calendar_name=config.execution.execution_session_calendar)
        if not session.get("is_open"):
            blockers.append("SESSION_ENDED_DURING_REFRESH")
        if manifest.get("status") != "success":
            blockers.append("REFRESH_NOT_SUCCESSFUL")
        if blockers:
            return finish(status="FRESH_INPUT_UNAVAILABLE", blockers=blockers)
        # Runtime.prepare constructs the packet once and validates the exact
        # producer, current source clocks, account, rows and session before any
        # event/state allocation. A second preflight packet ages the same quotes.
        result = runtime.prepare(surface, archive_dir=archive,
            youtube_archive_dir=youtube_archive_dir, prism_archive_dir=prism_archive_dir, fresh_report=True,
            expected_producer_run_id=manifest.get("run_id"), refresh_started_at=started,
            report_context_v1=report_context_v1)
        saved = finish(status="REFRESHED", observations=result.get('verified_refresh_observations', {}),
                       event_created=result.get("result") in {"NEW", "RESUME"})
        return {**result, "pre_report_refresh": saved}
    except FreshReportSourceError as exc:
        return finish(status='FRESH_INPUT_UNAVAILABLE', blockers=list(exc.blockers),
                      retryable_expiry=exc.retryable_expiry)
    except ProducerBusy:
        # A minute producer may own the writer lock while its previous immutable
        # result is still fresh. Reuse only verified observations; no TTL renewal,
        # broker calls, handoff, waiting loop, or duplicate producer is needed.
        try:
            archive = resolve_archive_roots(archive_dir=archive_dir)["market"]
            selected = completed_busy_source(surface, archive=archive, config=config,
                youtube_archive_dir=youtube_archive_dir, prism_archive_dir=prism_archive_dir)
            if selected is not None:
                manifest, started, clocks = selected
                result = runtime.prepare(surface, archive_dir=archive,
                    youtube_archive_dir=youtube_archive_dir, prism_archive_dir=prism_archive_dir,
                    fresh_report=True, expected_producer_run_id=manifest["run_id"],
                    refresh_started_at=started, report_context_v1=report_context_v1)
                saved = finish(status="ADOPTED_COMPLETED_PRODUCER", producer_run_id=manifest["run_id"],
                    producer_started_at=manifest["started_at"], producer_finished_at=manifest["finished_at"],
                    event_created=result.get("result") in {"NEW", "RESUME"})
                return {**result, "pre_report_refresh": saved}
        except Exception as exc:
            return finish(status="BUSY_NO_STATE_ADVANCE", blockers=["PRODUCER_ALREADY_RUNNING"],
                          adoption_error_type=type(exc).__name__,
                          **({'adoption_blockers': list(exc.blockers)} if isinstance(exc, FreshReportSourceError) else {}))
        return finish(status="BUSY_NO_STATE_ADVANCE", blockers=["PRODUCER_ALREADY_RUNNING"])
    except Exception as exc:
        # Broker errors can contain private request details. Keep the durable
        # public-facing receipt limited to an error type, never credentials.
        return finish(status="FRESH_INPUT_UNAVAILABLE", blockers=["REFRESH_FAILED"], error_type=type(exc).__name__)
