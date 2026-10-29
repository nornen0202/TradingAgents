"""Independent, bounded normal research while existing minute workers continue.

Two fixed exchange-local slots, at most two distinct tickers per slot, include
failed/interrupted attempts in the budget. No broker client, order, approval
rewrite or model retry until a desired direction appears exists in this lane.
"""
from dataclasses import replace
from datetime import datetime, time, timedelta, timezone
import math
import os
from pathlib import Path
from zoneinfo import ZoneInfo

from tradingagents.atomic_io import atomic_write_json
from tradingagents.charting.bars import instant
from tradingagents.dataflows.research_evidence import assess_tool_evidence, evidence_review_reason
from tradingagents.scheduled.research_refresh import artifact, make_plan, rows_by_ticker, MAX_TARGETS
from tradingagents.schemas import parse_structured_decision
from .paper_runtime import _latest_source, _read, _runtime_session

SLOTS = {"KR": (time(10, 10), time(13, 10)), "US": (time(10), time(13))}
ZONES = {"KR": "Asia/Seoul", "US": "America/New_York"}
MAX_ADMISSION_MINUTES = 30


def current_entry_authorization(analysis, now, *, ticker=None):
    """Use the same canonical schema and research lifetime as the order planner.

    Legacy/invalid decisions need research; they never become an approval here.
    The public analysis stores its structured decision as JSON text.
    """
    now = instant(now)
    if (not isinstance(analysis, dict) or analysis.get("status") != "success"
            or not isinstance(analysis.get("ticker"), str) or not analysis["ticker"].strip()
            or (ticker is not None and analysis["ticker"] != ticker)):
        return False
    started, finished = instant(analysis.get("started_at")), instant(analysis.get("finished_at"))
    if now is None or started is None or finished is None or not started <= finished <= now:
        return False
    try:
        decision = parse_structured_decision(analysis.get("decision"))
    except (TypeError, ValueError, AttributeError):
        return False
    # The order planner requires original company news and actual tool use for
    # a new entry. An unusable approval must remain eligible for fresh research.
    if (decision.data_coverage.company_news_count < 1
            or "no_tool_calls_detected" in (analysis.get("quality_flags") or [])):
        return False
    if decision.conditional_entry_action.value in {"STARTER", "ADD"}:
        expires = instant(decision.conditional_entry_valid_until)
        return expires is not None and now < expires
    return decision.entry_action.value in {"STARTER", "ADD"} and now - finished < timedelta(hours=24)


def research_lane_enabled(state):
    state = Path(state)
    try:
        lane = _read(state / "research-lane-enabled.json", {})
        strategy = _read(state / "kis-strategy/enabled.json", {})
    except (OSError, ValueError):
        return False
    return (isinstance(lane, dict) and lane.get("mode") == "PAPER_RESEARCH_INDEPENDENT_V1"
            and lane.get("enabled") is True and lane.get("real_orders_enabled") is False
            and isinstance(strategy, dict) and strategy.get("enabled") is True
            and strategy.get("mode") == "KIS_DEMO_STRATEGY"
            and strategy.get("real_orders_enabled") is False
            and strategy.get("allocation_mode") == "DEMO_NATIVE_ONE_SHARE_V1"
            and (state / "actions-drained.json").is_file())


def select_targets(source_dir, source, observation_dir, *, market, now, allowed, cap, excluded=()):
    """Eligibility for research is not entry authority; orders recheck all limits."""
    rows = rows_by_ticker(source)
    bundle = _read(observation_dir / "decision_bundle_v2.json", {})
    generated = instant(bundle.get("generated_at"))
    if generated is None or not 0 <= (now - generated).total_seconds() < 120:
        return []
    candidates, seen = [], set()
    for row in bundle.get("strategy_table", []):
        ticker = row.get("ticker")
        if ticker in seen:
            raise ValueError("Duplicate research observation")
        seen.add(ticker)
        observed, price = instant(row.get("market_data_asof")), row.get("last_price")
        if (ticker not in rows or ticker not in allowed or ticker in excluded
                or observed is None or not observed <= generated <= now
                or not 0 <= (now - observed).total_seconds() < 120
                or row.get("market_session") != "regular"
                or isinstance(price, bool) or not isinstance(price, (int, float))
                or not math.isfinite(price) or not 0 < price <= cap):
            continue
        analysis = _read(artifact(source_dir, rows[ticker], "analysis_json"))
        if not isinstance(analysis, dict):
            analysis = {}
        telemetry = analysis.get("tool_telemetry") or {}
        if not isinstance(telemetry, dict):
            telemetry = {"request_schema": "unverified"}
        health = {"fallback_count": telemetry.get("fallback_count", 0)}
        evidence = assess_tool_evidence(telemetry, started_at=analysis.get("started_at"), finished_at=analysis.get("finished_at"))
        if evidence is not None:
            health["request_evidence"] = evidence
        # Existing executable approvals proceed in the minute lane immediately.
        # This research worker only revisits unapproved/reviewed original theses.
        invalidated = (row.get("raw_codes") or {}).get("decision_state") == "INVALIDATED"
        if current_entry_authorization(analysis, now, ticker=ticker) and not evidence_review_reason(health) and not invalidated:
            continue
        confidence = row.get("confidence")
        score = float(confidence) if isinstance(confidence, (int, float)) and math.isfinite(confidence) else 0
        candidates.append((-score, ticker))
    return [ticker for _, ticker in sorted(candidates)[:MAX_TARGETS]]


def research_due(archive, state, *, now=None, dry_run=False, executor=None, session_resolver=None,
                 prepare=None, universe_loader=None, catch_up_market=None):
    archive, state = Path(archive), Path(state)
    now = instant(now or datetime.now(timezone.utc))
    if now is None:
        raise ValueError("Aware research clock required")
    settings = _read(state / "kis-strategy/enabled.json", {})
    if (not isinstance(settings, dict) or settings.get("enabled") is not True
            or settings.get("mode") != "KIS_DEMO_STRATEGY" or settings.get("real_orders_enabled") is not False
            or settings.get("allocation_mode") != "DEMO_NATIVE_ONE_SHARE_V1"):
        return []
    if (state / "kis-strategy/HALT").exists() or (state / "kis-validation/HALT").exists():
        return [{"status": "HALTED"}]
    if not (state / "actions-drained.json").is_file():
        return [{"status": "WAITING_LOCAL_AUTOMATION_AUTHORITY"}]
    if research_lane_enabled(state):
        # Preserve the existing full-run target windows, attempt receipts,
        # preflight and failed-only recovery. Only ownership of the long call
        # moves to this independent research lock.
        from tradingagents.local_automation import run_due
        daily = run_due(archive, state, now=now, dry_run=dry_run, research_only=True,
                        **({"catch_up_market": catch_up_market} if catch_up_market else {}))
        if any(row.get("status") == "DUE" for row in daily):
            return [{"status": "DAILY_RESEARCH_DUE" if dry_run else "DAILY_RESEARCH_ATTEMPTED", "decisions": daily}]
        if catch_up_market:
            return [{"status": "DAILY_RESEARCH_CATCHUP_HELD", "decisions": daily}]
    elif catch_up_market:
        return [{"status": "INDEPENDENT_RESEARCH_LANE_NOT_ENABLED"}]
    from .demo_runtime import CAPS, universe
    from tradingagents.scheduled.config import load_scheduled_config
    from tradingagents.scheduled.runner import (
        execute_scheduled_run, _resolve_latest_full_overlay_baseline_manifest,
        _resolve_latest_overlay_source_manifest,
    )
    from tradingagents.scheduled.research_refresh import manifest_path
    allowed = (universe_loader or universe)()
    results = []
    for market, clocks in SLOTS.items():
        local = now.astimezone(ZoneInfo(ZONES[market]))
        session = (session_resolver or _runtime_session)(market=market.lower(), now_local=now)
        if session.get("is_open") is not True or session.get("phase") != "regular":
            continue
        due = [i for i, slot in enumerate(clocks) if local.time().replace(tzinfo=None) >= slot]
        if not due:
            continue
        # An older missed slot never queues behind a newer slot.
        slot = due[-1]
        boundary = datetime.combine(local.date(), clocks[slot], tzinfo=local.tzinfo)
        if (local - boundary).total_seconds() >= MAX_ADMISSION_MINUTES * 60:
            continue
        day = local.date().isoformat()
        path = state / "research-refresh" / market.lower() / f"{day}-{slot}.json"
        if path.exists():
            continue  # STARTED and FAILED also consume their original slot.
        prior = [_read(p) for p in path.parent.glob(f"{day}-*.json")]
        excluded = {t for receipt in prior for t in receipt.get("targets", [])}
        baseline = _resolve_latest_full_overlay_baseline_manifest(archive, market=market, now=now)
        if baseline is None:
            results.append({"market": market, "status": "WAITING_RESEARCH_BASELINE"})
            continue
        source = _resolve_latest_overlay_source_manifest(archive, market=market,
                    tickers=list(rows_by_ticker(baseline)))
        observation_dir = _latest_source(archive, market.lower(), now,
                                        required_artifacts=("decision_bundle_v2.json",))
        if source is None or observation_dir is None:
            continue
        source_dir = manifest_path(archive, source["run_id"]).parent
        targets = select_targets(source_dir, source, observation_dir, market=market, now=now,
                                 allowed=allowed[market], cap=CAPS[market], excluded=excluded)
        if not targets:
            results.append({"market": market, "status": "NO_RESEARCH_TARGET_WITHIN_EXISTING_LIMITS"})
            continue
        plan = make_plan(archive, source, targets, now=now,
                         reasons=["scheduled_thesis_refresh", "verify_current_required_evidence"])
        receipt = {"market": market, "session_date": day, "slot": slot, "targets": targets,
                   "started_at": now.isoformat(), "plan": plan, "status": "STARTED",
                   "source_revision": os.getenv("TRADINGAGENTS_SOURCE_SHA"),
                   "real_orders_enabled": False, "broker_orders_sent": 0}
        if dry_run:
            results.append({**receipt, "status": "DUE"})
            continue
        admission_error = None
        if prepare is None:
            from tradingagents.local_automation import LocalStorageHeadroomError, require_storage_headroom
            try:
                root = Path(__file__).resolve().parents[2]
                config_path = root / "config" / ("scheduled_analysis_korea.toml" if market == "KR" else "scheduled_analysis.toml")
                config = load_scheduled_config(config_path)
                require_storage_headroom(archive, state, config.llm.codex_workspace_dir)
            except LocalStorageHeadroomError:
                from tradingagents.notifications.local import queue_failure
                queue_failure(state, stage="preflight", source_key=f"research-refresh:{market}:{day}:{slot}",
                              error_type="LocalStorageHeadroomError", finished_at=now.isoformat())
                results.append({"market": market, "status": "STORAGE_BLOCKED", "broker_orders_sent": 0})
                continue
            except Exception as exc:
                admission_error = exc
        atomic_write_json(path, receipt)
        stage = "preflight"
        try:
            if admission_error is not None:
                raise admission_error
            root = Path(__file__).resolve().parents[2]
            config_path = root / "config" / ("scheduled_analysis_korea.toml" if market == "KR" else "scheduled_analysis.toml")
            config = load_scheduled_config(config_path)
            if prepare is None:
                from tradingagents.local_automation import preflight, require_storage_headroom
                require_storage_headroom(archive, state, config.llm.codex_workspace_dir)
                preflight(config_path)
            else:
                prepare(config_path)
            config = replace(config, run=replace(config.run, run_mode="selective_rerun_only"),
                storage=replace(config.storage, archive_dir=archive),
                execution=replace(config.execution, execution_refresh_enabled=False),
                portfolio=replace(config.portfolio, enabled=False))
            stage = "research"
            result = (executor or execute_scheduled_run)(config, run_label=f"local-thesis-refresh-{market.lower()}",
                skip_site_build=True, defer_execution_handoff=True, research_refresh_plan=plan)
            if result.get("status") != "success" or not result.get("research_refresh"):
                raise ValueError("Research revision did not complete")
            receipt.update(status="COMPLETED", source_run_id=result["run_id"])
        except Exception as exc:
            receipt.update(status="FAILED", error_type=type(exc).__name__, failure_stage=stage)
        receipt["finished_at"] = datetime.now(timezone.utc).isoformat()
        atomic_write_json(path, receipt)
        results.append(receipt)
        break  # Re-evaluate current clocks after a long research pass.
    return results
