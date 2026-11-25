"""Refresh actual execution inputs between research slots under one producer lock.

This producer never renews a saved signal. It reuses the existing research
baseline, fetches new observations and runs the existing execution engine.
"""
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
import re
from time import perf_counter
from zoneinfo import ZoneInfo

from tradingagents.atomic_io import atomic_write_json
from tradingagents.charting.bars import instant
from tradingagents.execution.paper_runtime import _latest_source, _read, _runtime_session
from tradingagents.execution.refresh_policy import MAX_CONSECUTIVE_FAILURES
from tradingagents.execution.source_diagnostics import diagnose_source


ATTEMPT_INTERVAL_SECONDS = 60
FAILURE_RETRY_SECONDS = 300
EXECUTION_LANE_MODE = "KIS_EXECUTION_REFRESH_V1"
_COMPLETED_ATTEMPTS = {"COMPLETED", "COMPLETED_PARTIAL"}


def execution_refresh_enabled(state):
    """Only the existing explicitly enabled simulation lanes need this producer."""
    for lane, mode in (("paper", "LOCAL_PAPER_ONLY"), ("kis-strategy", "KIS_DEMO_STRATEGY")):
        settings = _read(Path(state) / lane / "enabled.json", {})
        if (isinstance(settings, dict) and settings.get("enabled") is True
                and settings.get("mode") == mode and settings.get("real_orders_enabled") is False):
            return True
    return False


def execution_lane_enabled(state):
    """Choose the producer lock independently of the current order switches."""
    try:
        settings = _read(Path(state) / "execution-refresh-enabled.json", {})
    except (OSError, ValueError):
        return False
    return (isinstance(settings, dict) and settings.get("mode") == EXECUTION_LANE_MODE
            and settings.get("enabled") is True and settings.get("real_orders_enabled") is False)


def quote_producer_lock_path(state):
    return Path(state) / ("execution-refresh.lock" if execution_lane_enabled(state) else "run-due.lock")


def _produced_source_health(archive, market, run_id, finished_at):
    if not isinstance(run_id, str) or not re.fullmatch(r"\d{8}T\d{6}_[A-Za-z0-9_-]{1,120}", run_id):
        return None
    source = archive / "runs" / run_id[:4] / run_id
    try:
        manifest = _read(source / "run.json", {})
        completed = instant(manifest.get("finished_at"))
        if (manifest.get("run_id") != run_id or manifest.get("status") != "success"
                or str((manifest.get("settings") or {}).get("market", "")).lower() != market
                or completed is None or completed > finished_at):
            return None
        return diagnose_source(source, finished_at, include_proposals=False)
    except (AttributeError, OSError, TypeError, ValueError):
        return None


def refresh_due(archive, state, *, now, dry_run=False, clock=None, executor=None,
                session_resolver=None):
    """Caller owns the existing producer lock; no new worker or order lane."""
    archive, state = Path(archive), Path(state)
    now = instant(now)
    if now is None:
        raise ValueError("Aware refresh clock required")
    clock = clock or (lambda: datetime.now(timezone.utc))
    if not execution_refresh_enabled(state):
        return []
    session_resolver = session_resolver or _runtime_session
    results = []
    for market, zone in (("kr", "Asia/Seoul"), ("us", "America/New_York")):
        if not session_resolver(market=market, now_local=now).get("is_open"):
            continue
        source = _latest_source(archive, market, now)
        # Collect once per minute even when the previous observation is still
        # valid. Skipping a 59-second-old source adds another polling interval
        # AND collection latency, leaving a gap in the 120-second consumer TTL.
        # Only the attempt receipt controls cadence; source clocks are unchanged.
        path = state / "execution-refresh" / f"{market}.json"
        prior = _read(path, {})
        started = instant(prior.get("started_at"))
        day = now.astimezone(ZoneInfo(zone)).date().isoformat()
        failures = prior.get("consecutive_failures", 0) if prior.get("session_date") == day else 0
        target = f"execution-freshness-{market}"
        # Windows launches drift by fractions of a second. Allow one successful
        # refresh per minute UTC slot; failed/in-flight attempts retain the
        # full elapsed cooldown.
        completed = prior.get("status") in _COMPLETED_ATTEMPTS
        next_success_slot = (started is not None and completed
            and int(now.timestamp()) // ATTEMPT_INTERVAL_SECONDS
            > int(started.timestamp()) // ATTEMPT_INTERVAL_SECONDS)
        cooldown = ATTEMPT_INTERVAL_SECONDS if completed else FAILURE_RETRY_SECONDS
        if started and (now - started).total_seconds() < cooldown and not next_success_slot:
            results.append({"target": target, "status": "REFRESH_COOLDOWN"})
            continue
        if not isinstance(failures, int) or isinstance(failures, bool) or failures < 0 or failures >= MAX_CONSECUTIVE_FAILURES:
            results.append({"target": target, "status": "REFRESH_RETRY_LIMIT"})
            continue
        # A quote overlay cannot create its own full research baseline. Wait
        # without consuming an attempt when the existing selector cannot find
        # one. This is only an admission check: the executor still resolves and
        # validates the current universe, holdings and source artifacts itself.
        # Never pass the observed manifest through as a pinned authorization.
        try:
            from tradingagents.scheduled.runner import _resolve_latest_full_overlay_baseline_manifest
            discovery_evidence = {}
            lookup_started = perf_counter()
            baseline = _resolve_latest_full_overlay_baseline_manifest(
                archive, market=market.upper(), now=now, write_discovery_index=False,
                partial_required_tickers=() if market == "kr" else None,
                discovery_evidence=discovery_evidence)
            discovery_evidence["elapsed_seconds"] = round(perf_counter() - lookup_started, 3)
        except Exception as exc:
            results.append({"target": target, "status": "REFRESH_BASELINE_UNVERIFIED",
                            "error_type": type(exc).__name__})
            continue
        if baseline is None:
            results.append({"target": target, "status": "WAITING_RESEARCH_BASELINE"})
            continue
        if dry_run:
            results.append({"target": target, "status": "DUE"})
            continue
        receipt = {"market": market, "session_date": day, "started_at": now.isoformat(),
                   "previous_source_run_id": source.name if source else None,
                   "baseline_lookup": {**discovery_evidence, "selected_run_id": baseline.get("run_id")},
                   "status": "STARTED", "consecutive_failures": failures + 1,
                   "real_orders_enabled": False}
        atomic_write_json(path, receipt)
        try:
            from tradingagents.scheduled.config import load_scheduled_config
            from tradingagents.scheduled.runner import execute_scheduled_run, _verified_completed_partial_overlay
            from tradingagents.local_automation import require_storage_headroom
            root = Path(__file__).resolve().parents[2]
            config = load_scheduled_config(root / "config" / (
                "scheduled_analysis_korea.toml" if market == "kr" else "scheduled_analysis.toml"))
            require_storage_headroom(archive, state, config.llm.codex_workspace_dir)
            checkpoint = now.astimezone(ZoneInfo(zone)).strftime("%H:%M")
            config = replace(config, run=replace(config.run, run_mode="overlay_only"),
                storage=replace(config.storage, archive_dir=archive), execution=replace(config.execution,
                    execution_refresh_enabled=True, execution_lightweight_refresh=True,
                    execution_max_data_age_seconds=120, execution_llm_summary_model=None,
                    execution_refresh_checkpoints_kst=(),
                    execution_refresh_checkpoints_local=(checkpoint,), execution_checkpoint_timezone=zone,
                    execution_session_gate_enabled=True, execution_selective_rerun_enabled=False))
            result = (executor or execute_scheduled_run)(config, run_label=f"local-freshness-{market}-overlay",
                skip_site_build=True, paper_state_dir=state)
            status = "COMPLETED" if result.get("status") == "success" else "FAILED"
            if status == "FAILED" and _verified_completed_partial_overlay(result):
                status = "COMPLETED_PARTIAL"
                receipt["missing_candidate_count"] = len(result["overlay_universe"]["missing_candidate_tickers"])
            receipt.update(status=status, source_run_id=result.get("run_id"),
                           producer_revision=result.get("source_revision"),
                           actual_baseline_run_id=result.get("overlay_source_run_id"))
            if status in _COMPLETED_ATTEMPTS:
                receipt["consecutive_failures"] = 0
        except Exception as exc:
            receipt.update(status="FAILED", error_type=type(exc).__name__)
        finished = clock()
        receipt["finished_at"] = finished.isoformat()
        if receipt["status"] == "COMPLETED":
            receipt["source_diagnostics"] = _produced_source_health(archive, market, receipt["source_run_id"], finished)
        atomic_write_json(path, receipt)
        results.append({"target": target, "status": receipt["status"]})
    return results
