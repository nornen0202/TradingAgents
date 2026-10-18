"""Acquire a present-time candle vintage for an existing archived analysis.

This does not rerun an agent, alter its plan or backdate knowledge. Repeated
refreshes append separate timestamped vintages; earlier replay stays unchanged.
"""
from __future__ import annotations

from datetime import datetime, timezone
import json
import hashlib
from pathlib import Path
from zoneinfo import ZoneInfo

from tradingagents.atomic_io import atomic_write_json, interprocess_file_lock
from tradingagents.agents.utils.instrument_resolver import resolve_instrument
from .capture import ChartCapture
from .report import render_review, _checkpoint_payloads
from .snapshot import get_replay_snapshot
from .bars import instant


def _json(path):
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
        return value if isinstance(value, dict) else {}
    except (OSError, ValueError):
        return {}


def reobserve_existing_evidence(ticker_dir, *, db_paths=()):
    """Observe legacy artifacts now, preserving historic decision/expiry clocks.

    Missing old ingestion remains unknown in every frame before this operation.
    This copies existing local evidence only; it never fetches data or reruns an
    execution decision, and it cannot renew a market quote or plan's expiry.
    """
    directory = Path(ticker_dir).resolve()
    analysis = _json(directory / "analysis.json")
    analysis_known = instant(analysis.get("finished_at"))
    if analysis_known is None:
        raise ValueError("Existing analysis requires a verified completion timestamp")
    observed = datetime.now(timezone.utc)
    if analysis_known > observed:
        raise ValueError("Analysis completion cannot be in the future")
    copied, skipped = [], []
    with interprocess_file_lock(directory / ".chart-refresh.lock"):
        for stem in ("execution_update", "execution_contract"):
            source = _json(directory / (stem + ".json"))
            if not source:
                skipped.append(stem + ":missing")
                continue
            if source.get("ticker") and str(source["ticker"]).upper() != directory.name.upper():
                skipped.append(stem + ":ticker_mismatch")
                continue
            # A valid recorded ingestion already has its own provenance. Do
            # not repackage newer source data just to move it forward in time.
            old_ingested = instant(source.get("ingested_at"))
            if old_ingested is not None:
                skipped.append(stem + ":already_dated")
                continue
            if source.get("ingested_at") not in (None, ""):
                skipped.append(stem + ":invalid_ingestion")
                continue
            fingerprint = hashlib.sha256(json.dumps(source, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
            if any(item.get("source_sha256") == fingerprint and item.get("provenance") == "reobserved_archive"
                   and instant(item.get("ingested_at")) is not None and instant(item["ingested_at"]) <= observed
                   for item in _checkpoint_payloads(directory, stem)):
                skipped.append(stem + ":already_reobserved")
                continue
            event = instant(source.get("execution_asof")) if stem == "execution_update" else (
                instant(source.get("event_time")) if source.get("event_time") is not None else analysis_known)
            if event is None or event > observed or (stem == "execution_contract" and event < analysis_known):
                skipped.append(stem + ":invalid_event_clock")
                continue
            if stem == "execution_update":
                market = instant(source.get("market_data_asof"))
                if source.get("market_data_asof") is not None and (market is None or market > event):
                    skipped.append(stem + ":invalid_market_clock")
                    continue
            payload = {**source, "ingested_at": observed.isoformat(),
                       "archive_observed_at": observed.isoformat(), "provenance": "reobserved_archive",
                       "source_sha256": fingerprint,
                       "original_analysis_finished_at": analysis_known.isoformat(),
                       "observation_does_not_refresh_inputs": True}
            if stem == "execution_contract" and "event_time" not in payload:
                payload["event_time"] = event.isoformat()
            checkpoint = directory / "execution/checkpoints" / (stem + "_reobserved_" + observed.strftime("%Y%m%dT%H%M%S%fZ") + ".json")
            atomic_write_json(checkpoint, payload)
            copied.append(stem)
    cutoff = datetime.now(timezone.utc)
    snapshot = get_replay_snapshot(directory.name, cutoff, ticker_dir=directory, db_paths=db_paths)
    (directory / "investment_review.html").write_text(render_review(snapshot), encoding="utf-8")
    return {"ticker": directory.name, "observed_at": observed.isoformat(), "reobserved": copied,
            "skipped": skipped, "original_analysis_preserved": True, "backdated": False,
            "provider_requests": 0, "broker_orders_sent": 0}


def _acquire_existing_review(ticker_dir, *, db_paths=(), loader=None):
    directory = Path(ticker_dir).resolve()
    if not (directory / "analysis.json").is_file():
        raise ValueError("Existing ticker analysis required")
    instrument = resolve_instrument(directory.name)
    symbol = instrument.primary_symbol
    if loader is None:
        from tradingagents.dataflows.stockstats_utils import load_ohlcv
        loader = load_ohlcv
    started = datetime.now(timezone.utc)
    curr_date = started.astimezone(ZoneInfo(instrument.timezone)).date().isoformat()
    recorder = ChartCapture(symbol)
    token = recorder.activate()
    try:
        # Existing loader performs local date filtering and captures the exact
        # validated frame. It may reuse its short cache; observed_at is now.
        loader(symbol, curr_date)
    finally:
        recorder.reset(token)
    cutoff = datetime.now(timezone.utc)
    payload = recorder.artifact(analysis_as_of=cutoff)
    payload.update(ticker=directory.name, source="present_time_review_refresh", observed_at=cutoff.isoformat(),
                   original_analysis_preserved=True, backdated=False, execution_authorized=False)
    if not payload.get("bars"):
        raise ValueError("No completed, dated bars captured; archive preserved")
    # Never replace an earlier vintage. Current and checkpoint payloads are
    # selected per candle's original observed_at by the shared replay function.
    primary = directory / "chart_evidence.json"
    with interprocess_file_lock(directory / ".chart-refresh.lock"):
        target = primary if not primary.exists() else directory / "execution" / "checkpoints" / ("chart_evidence_" + cutoff.strftime("%Y%m%dT%H%M%S%fZ") + ".json")
        atomic_write_json(target, payload)
    snapshot = get_replay_snapshot(directory.name, cutoff, ticker_dir=directory, db_paths=db_paths)
    output = directory / "investment_review.html"
    output.write_text(render_review(snapshot), encoding="utf-8")
    return {"ticker": directory.name, "captured_at": cutoff.isoformat(), "bar_count": len(payload["bars"]),
            "providers": payload.get("providers"), "source_run_id": directory.parents[1].name,
            "original_analysis_preserved": True, "backdated": False, "broker_orders_sent": 0}


def refresh_existing_review(ticker_dir, *, db_paths=(), loader=None):
    """Refresh with a durable, safe outcome receipt, including unavailable data."""
    directory = Path(ticker_dir).resolve()
    if not (directory / "analysis.json").is_file():
        raise ValueError("Existing ticker analysis required")
    result, failure = None, None
    try:
        result = _acquire_existing_review(directory, db_paths=db_paths, loader=loader)
    except Exception as exc:
        failure = exc
    checked = datetime.now(timezone.utc)
    receipt = {"schema": "tradingagents.chart-capture-status/v1", "ticker": directory.name,
               "status": "UNAVAILABLE" if failure else "REFRESHED", "checked_at": checked.isoformat(),
               "observed_at": checked.isoformat(), "broker_orders_sent": 0,
               "original_analysis_preserved": True, "backdated": False,
               "error_type": type(failure).__name__ if failure else None,
               "completed_bar_count": result["bar_count"] if result else None,
               "providers": result.get("providers", []) if result else []}
    with interprocess_file_lock(directory / ".chart-refresh.lock"):
        history = directory / "execution" / "checkpoints" / ("chart_capture_status_" + checked.strftime("%Y%m%dT%H%M%S%fZ") + ".json")
        atomic_write_json(history, receipt)
        atomic_write_json(directory / "chart_capture_status.json", receipt)
    if failure is not None:
        raise failure
    return result
