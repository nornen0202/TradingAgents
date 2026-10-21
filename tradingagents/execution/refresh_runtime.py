"""Refresh actual execution inputs between research slots, under run-due.lock.

This producer never renews a saved signal. It reuses the existing research
baseline, fetches new observations and runs the existing execution engine.
"""
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

from tradingagents.atomic_io import atomic_write_json
from tradingagents.charting.bars import instant
from tradingagents.execution.paper_runtime import _latest_source, _read, _runtime_session


REFRESH_AFTER_SECONDS = 120
ATTEMPT_INTERVAL_SECONDS = 300
MAX_CONSECUTIVE_FAILURES = 3


def _source_observations_fresh(bundle, now):
    """Publication cannot make an old or unverifiable observation fresh."""
    if not isinstance(bundle, dict):
        return False
    generated = instant(bundle.get("generated_at"))
    if generated is None or not 0 <= (now - generated).total_seconds() < REFRESH_AFTER_SECONDS:
        return False
    rows = bundle.get("strategy_table")
    if not isinstance(rows, list) or not rows:
        return False
    for row in rows:
        observed = instant(row.get("market_data_asof")) if isinstance(row, dict) else None
        if observed is None or not 0 <= (now - observed).total_seconds() < REFRESH_AFTER_SECONDS:
            return False
    return True


def execution_refresh_enabled(state):
    """Only the existing explicitly enabled simulation lanes need this producer."""
    for lane, mode in (("paper", "LOCAL_PAPER_ONLY"), ("kis-strategy", "KIS_DEMO_STRATEGY")):
        settings = _read(Path(state) / lane / "enabled.json", {})
        if (isinstance(settings, dict) and settings.get("enabled") is True
                and settings.get("mode") == mode and settings.get("real_orders_enabled") is False):
            return True
    return False


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
        bundle = _read(source / "decision_bundle_v2.json", {}) if source else {}
        if _source_observations_fresh(bundle, now):
            continue
        path = state / "execution-refresh" / f"{market}.json"
        prior = _read(path, {})
        started = instant(prior.get("started_at"))
        day = now.astimezone(ZoneInfo(zone)).date().isoformat()
        failures = prior.get("consecutive_failures", 0) if prior.get("session_date") == day else 0
        target = f"execution-freshness-{market}"
        # Windows launches drift by fractions of a second. A successful 09:05:05
        # must not suppress the next scheduled 09:10:04 tick. Allow one successful
        # refresh per five-minute UTC slot; failed/in-flight attempts retain the
        # full elapsed cooldown. The source-age gate above still applies.
        next_success_slot = (started is not None and prior.get("status") == "COMPLETED"
            and int(now.timestamp()) // ATTEMPT_INTERVAL_SECONDS
            > int(started.timestamp()) // ATTEMPT_INTERVAL_SECONDS)
        if started and (now - started).total_seconds() < ATTEMPT_INTERVAL_SECONDS and not next_success_slot:
            results.append({"target": target, "status": "REFRESH_COOLDOWN"})
            continue
        if not isinstance(failures, int) or isinstance(failures, bool) or failures < 0 or failures >= MAX_CONSECUTIVE_FAILURES:
            results.append({"target": target, "status": "REFRESH_RETRY_LIMIT"})
            continue
        if dry_run:
            results.append({"target": target, "status": "DUE"})
            continue
        receipt = {"market": market, "session_date": day, "started_at": now.isoformat(),
                   "previous_source_run_id": source.name if source else None,
                   "status": "STARTED", "consecutive_failures": failures + 1,
                   "real_orders_enabled": False}
        atomic_write_json(path, receipt)
        try:
            from tradingagents.scheduled.config import load_scheduled_config
            from tradingagents.scheduled.runner import execute_scheduled_run
            from tradingagents.local_automation import require_storage_headroom
            root = Path(__file__).resolve().parents[2]
            config = load_scheduled_config(root / "config" / (
                "scheduled_analysis_korea.toml" if market == "kr" else "scheduled_analysis.toml"))
            require_storage_headroom(archive, state, config.llm.codex_workspace_dir)
            checkpoint = now.astimezone(ZoneInfo(zone)).strftime("%H:%M")
            config = replace(config, run=replace(config.run, run_mode="overlay_only"),
                storage=replace(config.storage, archive_dir=archive), execution=replace(config.execution,
                    execution_refresh_enabled=True, execution_refresh_checkpoints_kst=(),
                    execution_refresh_checkpoints_local=(checkpoint,), execution_checkpoint_timezone=zone,
                    execution_session_gate_enabled=True, execution_selective_rerun_enabled=False))
            result = (executor or execute_scheduled_run)(config, run_label=f"local-freshness-{market}-overlay",
                skip_site_build=True, paper_state_dir=state)
            receipt.update(status="COMPLETED" if result.get("status") == "success" else "FAILED",
                           source_run_id=result.get("run_id"))
            if receipt["status"] == "COMPLETED":
                receipt["consecutive_failures"] = 0
        except Exception as exc:
            receipt.update(status="FAILED", error_type=type(exc).__name__)
        receipt["finished_at"] = clock().isoformat()
        atomic_write_json(path, receipt)
        results.append({"target": target, "status": receipt["status"]})
    return results
