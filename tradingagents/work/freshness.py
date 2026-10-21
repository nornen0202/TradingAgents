"""Source clocks for Work consumers. Publication never renews input data."""
from __future__ import annotations

from datetime import datetime, timedelta
import math
from typing import Any

from tradingagents.dataflows.market_policy import (
    MAX_EXECUTION_AGE, aware_datetime, latest_regular_session_context,
    observation_status, research_observation_policy,
)


def source_execution_max_age(manifest: dict[str, Any]) -> timedelta:
    """A report may tighten, but never extend, the producer's observation age."""
    settings = manifest.get("settings") or {}
    if "execution_max_data_age_seconds" not in settings:
        return MAX_EXECUTION_AGE  # Legacy manifests use the shared policy.
    value = settings["execution_max_data_age_seconds"]
    if isinstance(value, bool):
        return timedelta(0)
    try:
        seconds = float(value)
    except (TypeError, ValueError, OverflowError):
        return timedelta(0)
    if not math.isfinite(seconds) or seconds <= 0:
        return timedelta(0)
    return timedelta(seconds=min(seconds, MAX_EXECUTION_AGE.total_seconds()))


def source_freshness_receipt(
    manifest: dict[str, Any], bundle: dict[str, Any], *, now: datetime,
    analysis_manifest: dict[str, Any], public: bool,
) -> dict[str, Any]:
    rows = [row for row in bundle.get("strategy_table", []) if isinstance(row, dict)]
    max_age = source_execution_max_age(manifest)
    clocks = [observation_status(row.get("market_data_asof"), as_of=now) for row in rows]
    observations = [aware_datetime(row.get("market_data_asof")) for row in rows]
    valid = [value for value in observations if value is not None and value <= now]
    invalid = sum(clock["status"] in {"MISSING", "INVALID"} for clock in clocks)
    future = sum(clock["status"] == "FUTURE" for clock in clocks)
    expired = sum(value + max_age <= now for value in valid)
    state = "MISSING" if not rows or invalid else "INVALID" if future else "STALE" if expired else "FRESH"
    summaries = [item for item in analysis_manifest.get("tickers", []) if isinstance(item, dict)]
    dates = sorted({str(item["trade_date"]) for item in summaries if item.get("trade_date")})
    analysis_times = [aware_datetime(item.get("finished_at")) for item in analysis_manifest.get("tickers", []) if isinstance(item, dict)]
    analysis_times = [value for value in analysis_times if value is not None and value <= now]
    market = str(bundle.get("market") or manifest.get("market") or "").upper()
    calendar = latest_regular_session_context(market, as_of=now)
    research_receipts = []
    for row in rows:
        interval = str(row.get("interval") or row.get("market_data_interval") or
                       ("1d" if row.get("level_basis") == "daily_close" else "unknown"))
        policy = research_observation_policy(row.get("market_data_asof"), as_of=now,
            session=calendar["session"], interval=interval,
            latest_regular_close_at=calendar["latest_regular_close_at"], verified_session=calendar["verified_session"])
        research_receipts.append({"ticker": row.get("ticker"), "research_valid": policy["research_valid"],
                                  "category": policy["category"], "execution_eligible": False})
    research_valid = sum(row["research_valid"] for row in research_receipts)
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
        "execution_max_age_seconds": max_age.total_seconds(),
        "research_market_data_status": "VALID" if rows and research_valid == len(rows) else "PARTIAL" if research_valid else "UNVERIFIED",
        "research_market_data_receipts": research_receipts,
        "research_calendar_verified": calendar["verified_session"],
        "latest_regular_close_at": calendar["latest_regular_close_at"],
        "research_does_not_enable_execution": True,
    }
    if not public:
        receipt.update(
            market_data_row_count=len(rows),
            market_data_observed_count=len(valid),
            market_data_missing_count=invalid,
            market_data_future_count=future,
            market_data_research_observation_count=sum(
                row.get("market_data_basis") == "RESEARCH_OBSERVATION" for row in rows
            ),
        )
        portfolio = manifest.get("portfolio") or {}
        snapshot = portfolio.get("private_coverage_snapshot") or {}
        receipt["account_as_of"] = snapshot.get("as_of")
        receipt["account_snapshot_health"] = snapshot.get("snapshot_health")
    return receipt
