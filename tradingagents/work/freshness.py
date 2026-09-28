"""Source clocks for Work consumers. Publication never renews input data."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any


def aware_datetime(value: Any) -> datetime | None:
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return parsed if parsed.tzinfo is not None else None
    except (TypeError, ValueError):
        return None


def source_freshness_receipt(
    manifest: dict[str, Any], bundle: dict[str, Any], *, now: datetime,
    analysis_manifest: dict[str, Any], public: bool,
) -> dict[str, Any]:
    rows = [row for row in bundle.get("strategy_table", []) if isinstance(row, dict)]
    observations = [aware_datetime(row.get("market_data_asof")) for row in rows]
    valid = [value for value in observations if value is not None]
    invalid = len(observations) - len(valid)
    future = sum(value > now for value in valid)
    expired = sum(value + timedelta(minutes=30) <= now for value in valid)
    state = "MISSING" if not rows or invalid else "INVALID" if future else "STALE" if expired else "FRESH"
    summaries = [item for item in analysis_manifest.get("tickers", []) if isinstance(item, dict)]
    dates = sorted({str(item["trade_date"]) for item in summaries if item.get("trade_date")})
    analysis_times = [aware_datetime(item.get("finished_at")) for item in analysis_manifest.get("tickers", []) if isinstance(item, dict)]
    analysis_times = [value for value in analysis_times if value is not None]
    receipt = {
        "schema": "tradingagents.source-freshness/v1",
        "producer_run_id": manifest.get("run_id"),
        "producer_started_at": manifest.get("started_at"),
        "producer_finished_at": manifest.get("finished_at"),
        "analysis_run_id": analysis_manifest.get("run_id"),
        "analysis_lineage_status": "RESOLVED" if analysis_manifest else "UNVERIFIED",
        "analysis_completed_at": max(analysis_times).isoformat() if analysis_times else None,
        "analysis_trade_date_oldest": dates[0] if dates else None,
        "analysis_trade_date_latest": dates[-1] if dates else None,
        "market_data_oldest_at": min(valid).isoformat() if valid else None,
        "market_data_latest_at": max(valid).isoformat() if valid else None,
        "market_data_status": state,
        "publication_does_not_refresh_inputs": True,
    }
    if not public:
        portfolio = manifest.get("portfolio") or {}
        snapshot = portfolio.get("private_coverage_snapshot") or {}
        receipt["account_as_of"] = snapshot.get("as_of")
        receipt["account_snapshot_health"] = snapshot.get("snapshot_health")
    return receipt
