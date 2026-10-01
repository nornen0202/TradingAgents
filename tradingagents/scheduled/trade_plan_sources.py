"""Bounded, exact-run inputs for the public conditional trade-plan renderer.

This reader never searches for a newer or older account to fill missing inputs.
It returns only sizing fields, not broker identifiers or raw response text.
"""

from __future__ import annotations

import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


_RUN_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,159}")
_TICKER = re.compile(r"[A-Z0-9][A-Z0-9.^=-]{0,23}")
_MAX_JSON_BYTES = 2 * 1024 * 1024
_SOURCE_REASON_CODES = frozenset(
    {
        "SOURCE_RUN_PARTIAL_FAILURE",
        "SOURCE_RUN_INCOMPLETE",
        "PORTFOLIO_RUN_INCOMPLETE",
        "PENDING_ORDERS_UNVERIFIED",
        "EXACT_RUN_ACCOUNT_NOT_VERIFIED",
    }
)


class _SourceUnavailable(ValueError):
    """Only allowlisted internal codes may reach the presentation layer."""

    def __init__(self, code: str):
        self.code = (
            code if code in _SOURCE_REASON_CODES else "EXACT_RUN_ACCOUNT_NOT_VERIFIED"
        )
        super().__init__(self.code)


def _object(path: Path) -> dict[str, Any]:
    if not path.is_file() or path.stat().st_size > _MAX_JSON_BYTES:
        raise ValueError("missing_or_oversized_artifact")
    with path.open("rb") as handle:
        content = handle.read(_MAX_JSON_BYTES + 1)
    if len(content) > _MAX_JSON_BYTES:
        raise ValueError("oversized_artifact")
    value = json.loads(content)
    if not isinstance(value, dict):
        raise ValueError("invalid_artifact_object")
    return value


def _time(value: Any) -> datetime:
    parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timestamp_timezone_missing")
    return parsed


def _number(value: Any) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError("invalid_numeric_field")
    if not math.isfinite(value):
        raise ValueError("invalid_numeric_field")
    return value


def _sizing_snapshot(snapshot: dict[str, Any]) -> dict[str, Any]:
    if snapshot.get("snapshot_health") != "VALID" or snapshot.get("currency") != "KRW":
        raise ValueError("account_snapshot_not_valid")
    result = {"as_of": snapshot["as_of"], "snapshot_health": "VALID", "currency": "KRW"}
    for key in ("available_cash_krw", "buying_power_krw", "settled_cash_krw"):
        # A missing cash field must not silently become zero or another cash field.
        result[key] = _number(snapshot.get(key))
    constraints = snapshot.get("constraints")
    if not isinstance(constraints, dict):
        raise ValueError("account_constraints_missing")
    buffer = _number(constraints.get("min_cash_buffer_krw"))
    if buffer < 0:
        raise ValueError("invalid_cash_buffer")
    result["constraints"] = {"min_cash_buffer_krw": buffer}
    for field in (
        "min_trade_krw",
        "max_order_count_per_day",
        "max_single_name_weight",
        "max_daily_turnover_ratio",
        "max_sector_weight",
    ):
        if field not in constraints:
            continue
        value = _number(constraints[field])
        if value < 0 or (field.endswith(("weight", "ratio")) and value > 1):
            raise ValueError("invalid_account_constraint")
        result["constraints"][field] = value
    positions = snapshot.get("positions")
    if not isinstance(positions, list) or len(positions) > 1000:
        raise ValueError("invalid_positions")
    safe_positions = []
    identities = set()
    for position in positions:
        if not isinstance(position, dict):
            raise ValueError("invalid_position")
        ticker = position.get("canonical_ticker")
        if (
            not isinstance(ticker, str)
            or not _TICKER.fullmatch(ticker)
            or ticker in identities
        ):
            raise ValueError("invalid_or_duplicate_ticker")
        identities.add(ticker)
        quantity = _number(position.get("quantity"))
        available = _number(position.get("available_qty"))
        if quantity < 0 or available < 0 or available > quantity:
            raise ValueError("invalid_position_quantity")
        safe_positions.append(
            {
                "canonical_ticker": ticker,
                "quantity": quantity,
                "available_qty": available,
            }
        )
    result["positions"] = safe_positions
    pending = snapshot.get("pending_orders")
    warnings = snapshot.get("warnings") or []
    if (
        not isinstance(pending, list)
        or len(pending) > 1000
        or any(
            "pending-order lookup failed" in str(warning).lower()
            for warning in warnings
        )
    ):
        raise _SourceUnavailable("PENDING_ORDERS_UNVERIFIED")
    safe_pending = []
    for order in pending:
        if not isinstance(order, dict):
            raise _SourceUnavailable("PENDING_ORDERS_UNVERIFIED")
        ticker, side = order.get("canonical_ticker"), order.get("side")
        try:
            remaining = _number(order.get("remaining_qty"))
        except ValueError as exc:
            raise _SourceUnavailable("PENDING_ORDERS_UNVERIFIED") from exc
        if (
            not isinstance(ticker, str)
            or not _TICKER.fullmatch(ticker)
            or side not in {"buy", "sell"}
            or remaining < 0
        ):
            raise _SourceUnavailable("PENDING_ORDERS_UNVERIFIED")
        safe_pending.append(
            {"canonical_ticker": ticker, "side": side, "remaining_qty": remaining}
        )
    result["pending_orders"] = safe_pending
    return result


def load_trade_plan_sources(
    archive_dir: Path, market_payload: dict[str, Any]
) -> dict[str, Any]:
    """Load identifier-free sizing inputs bound to the displayed source run.

    Fail closed for missing/incomplete provenance, path traversal, cross-run
    artifacts, invalid quantities, and mismatched account capture timestamps.
    Old but coherent accounts are returned with their original timestamp; the
    renderer is responsible for labelling their age and execution readiness.
    """
    result: dict[str, Any] = {
        "account_snapshot": None,
        "fx_krw_per_usd": None,
        "fx_asof": None,
        "status": "UNAVAILABLE",
        "fx_status": "EXPLICIT_USD_KRW_REFERENCE_UNAVAILABLE",
    }
    try:
        market = str(market_payload.get("market") or "").upper()
        run_id = market_payload.get("run_id")
        source = market_payload.get("source") or {}
        if (
            market not in {"KR", "US"}
            or not isinstance(run_id, str)
            or not _RUN_ID.fullmatch(run_id)
        ):
            raise ValueError("invalid_source_identity")
        if source.get("run_id") != run_id:
            raise ValueError("source_run_mismatch")
        runs_root = (Path(archive_dir) / "runs").resolve()
        paths = list(runs_root.glob(f"*/{run_id}/run.json"))
        direct = runs_root / run_id / "run.json"
        if direct.is_file():
            paths.append(direct)
        if len(paths) != 1:
            raise ValueError("exact_run_missing_or_ambiguous")
        manifest_path = paths[0].resolve()
        if not manifest_path.is_relative_to(runs_root):
            raise ValueError("run_path_outside_archive")
        run_dir = manifest_path.parent
        manifest = _object(manifest_path)
        manifest_market = (manifest.get("settings") or {}).get(
            "market"
        ) or manifest.get("market")
        if manifest.get("run_id") != run_id or str(manifest_market).upper() != market:
            raise ValueError("manifest_identity_mismatch")
        portfolio = manifest.get("portfolio") or {}
        if manifest.get("status") == "partial_failure":
            raise _SourceUnavailable("SOURCE_RUN_PARTIAL_FAILURE")
        if manifest.get("status") != "success":
            raise _SourceUnavailable("SOURCE_RUN_INCOMPLETE")
        if portfolio.get("status") != "success":
            raise _SourceUnavailable("PORTFOLIO_RUN_INCOMPLETE")
        artifact = (portfolio.get("artifacts") or {}).get("account_snapshot_json")
        if not isinstance(artifact, str) or not artifact.strip():
            raise ValueError("account_artifact_not_declared")
        relative = Path(artifact)
        snapshot_path = (
            relative if relative.is_absolute() else run_dir / relative
        ).resolve()
        if (
            not snapshot_path.is_relative_to(run_dir)
            or snapshot_path.name != "account_snapshot.json"
        ):
            raise ValueError("account_artifact_outside_source_run")
        snapshot = _object(snapshot_path)
        coverage = portfolio.get("private_coverage_snapshot") or {}
        if coverage.get("holding_set_complete") is not True:
            raise ValueError("account_coverage_incomplete")
        if not snapshot.get("snapshot_id") or snapshot.get(
            "snapshot_id"
        ) != coverage.get("snapshot_id"):
            raise ValueError("account_capture_identity_mismatch")
        observed = _time(snapshot.get("as_of"))
        if observed != _time(coverage.get("as_of")):
            raise ValueError("account_capture_time_mismatch")
        started = _time(manifest.get("started_at"))
        finished = _time(manifest.get("finished_at"))
        if not started <= observed <= finished <= datetime.now(timezone.utc):
            raise ValueError("account_capture_outside_source_run")
        safe = _sizing_snapshot(snapshot)
        expected = coverage.get("canonical_holding_tickers")
        if not isinstance(expected, list) or set(expected) != {
            p["canonical_ticker"] for p in safe["positions"]
        }:
            raise ValueError("account_holdings_mismatch")
        result.update(
            account_snapshot=safe, status="EXACT_RUN_ACCOUNT", source_run_id=run_id
        )
        quote = (snapshot.get("cash_diagnostics") or {}).get("fx_quote")
        if market == "US" and isinstance(quote, dict):
            try:
                fx = _number(quote.get("rate"))
                fx_observed = _time(quote.get("observed_at"))
                if (
                    (
                        quote.get("base_currency"),
                        quote.get("quote_currency"),
                        quote.get("source"),
                    )
                    != (
                        "USD",
                        "KRW",
                        "kis.inquire_present_balance.output2.frst_bltn_exrt",
                    )
                    or fx <= 0
                    or not started <= fx_observed <= finished
                ):
                    raise ValueError("invalid_fx_reference")
            except (ValueError, TypeError, OverflowError):
                result["fx_status"] = "INVALID_USD_KRW_REFERENCE"
            else:
                result.update(
                    fx_krw_per_usd=fx,
                    fx_asof=quote["observed_at"],
                    fx_status="BROKER_REFERENCE_RATE",
                    fx_source=quote["source"],
                )
    except _SourceUnavailable as exc:
        result.update(account_snapshot=None, status="UNAVAILABLE", reason=exc.code)
    except (OSError, ValueError, TypeError, KeyError, AttributeError, OverflowError):
        # Do not emit exception strings: a malformed artifact could contain an
        # account identifier or a private filesystem path in the error message.
        result.update(
            account_snapshot=None,
            status="UNAVAILABLE",
            reason="EXACT_RUN_ACCOUNT_NOT_VERIFIED",
        )
    return result
