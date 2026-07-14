from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


REQUIRED_ROW_FIELDS = ("ticker", "strategy_ko", "data_status_ko")
REQUIRED_LIVE_FIELDS = ("last_price", "market_data_asof", "session_vwap", "relative_volume")


def _load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(path)
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"Expected an object: {path}")
    return payload


def _latest_run_dir(archive_dir: Path) -> Path:
    latest = _load_json(archive_dir / "latest-run.json")
    run_id = str(latest.get("run_id") or "")
    started_at = str(latest.get("started_at") or "")
    if not run_id or len(started_at) < 4:
        raise ValueError("latest-run.json is missing run_id or started_at")
    return archive_dir / "runs" / started_at[:4] / run_id


def validate_bundle(bundle: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if int(bundle.get("version") or 0) < 2:
        errors.append("decision bundle version must be >= 2")
    rows = bundle.get("strategy_table")
    if not isinstance(rows, list) or not rows:
        return [*errors, "strategy_table must contain at least one row"]
    quality = bundle.get("quality") if isinstance(bundle.get("quality"), dict) else {}
    decision_ready = quality.get("decision_ready") is True
    conditional_strategy_ready = quality.get("conditional_strategy_ready") is True
    ready_rows = 0
    conditional_rows = 0
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            errors.append(f"strategy_table[{index}] is not an object")
            continue
        for field in REQUIRED_ROW_FIELDS:
            if row.get(field) in (None, ""):
                errors.append(f"strategy_table[{index}] missing {field}")
        row_ready = bool((row.get("quality") or {}).get("execution_ready"))
        row_conditional = bool((row.get("quality") or {}).get("conditional_strategy_ready"))
        if row_ready:
            ready_rows += 1
        if row_conditional:
            conditional_rows += 1
        if row_ready or row_conditional:
            for field in REQUIRED_LIVE_FIELDS:
                if row.get(field) in (None, ""):
                    errors.append(f"current-session strategy row {row.get('ticker')} missing {field}")
        promotion = str((row.get("quality") or {}).get("current_execution_promotion") or "")
        if row_ready and promotion and promotion != "POSSIBLE":
            errors.append(f"execution-ready row {row.get('ticker')} has promotion={promotion}")
        if (
            not row_ready
            and not row_conditional
            and str(row.get("strategy_code") or "") in {"BUY_NOW", "SELL", "REDUCE"}
        ):
            errors.append(
                f"blocked row {row.get('ticker')} exposes immediate strategy {row.get('strategy_code')}"
            )
    actual_ratio = ready_rows / len(rows)
    declared_ratio = float(quality.get("fresh_row_ratio") or 0.0)
    if abs(actual_ratio - declared_ratio) > 0.001:
        errors.append(f"fresh_row_ratio mismatch: declared={declared_ratio:.4f}, actual={actual_ratio:.4f}")
    if decision_ready and actual_ratio < float(quality.get("minimum_fresh_row_ratio") or 0.8):
        errors.append("decision_ready=true but fresh row ratio is below the minimum")
    blocked_held = [
        str(row.get("ticker") or "")
        for row in rows
        if isinstance(row, dict)
        and row.get("is_held") is True
        and not bool((row.get("quality") or {}).get("execution_ready"))
    ]
    if decision_ready and blocked_held:
        errors.append(f"decision_ready=true with blocked held rows: {', '.join(blocked_held)}")
    actual_conditional_ratio = conditional_rows / len(rows)
    declared_conditional_ratio = float(quality.get("conditional_row_ratio") or 0.0)
    if abs(actual_conditional_ratio - declared_conditional_ratio) > 0.001:
        errors.append(
            "conditional_row_ratio mismatch: "
            f"declared={declared_conditional_ratio:.4f}, actual={actual_conditional_ratio:.4f}"
        )
    if conditional_strategy_ready and actual_conditional_ratio < float(
        quality.get("minimum_fresh_row_ratio") or 0.8
    ):
        errors.append("conditional_strategy_ready=true but conditional row ratio is below the minimum")
    if decision_ready and not conditional_strategy_ready:
        errors.append("decision_ready=true requires conditional_strategy_ready=true")
    return errors


def verify_run_dir(run_dir: Path, *, require_ready: bool = False) -> dict[str, Any]:
    bundle_path = run_dir / "decision_bundle_v2.json"
    bundle = _load_json(bundle_path)
    errors = validate_bundle(bundle)
    decision_ready = bool((bundle.get("quality") or {}).get("decision_ready"))
    if require_ready and not decision_ready:
        errors.append("decision bundle is not ready for intraday investment decisions")
    return {
        "run_id": bundle.get("run_id") or run_dir.name,
        "decision_ready": decision_ready,
        "conditional_strategy_ready": bool(
            (bundle.get("quality") or {}).get("conditional_strategy_ready")
        ),
        "fresh_row_ratio": (bundle.get("quality") or {}).get("fresh_row_ratio"),
        "row_count": len(bundle.get("strategy_table") or []),
        "bundle_sha256": hashlib.sha256(bundle_path.read_bytes()).hexdigest(),
        "errors": errors,
    }


def verify_site(site_dir: Path, *, market: str) -> dict[str, Any]:
    target = site_dir / "latest" / market.lower()
    status = _load_json(target / "status.json")
    errors: list[str] = []
    source = {}
    if (target / "source.json").exists():
        source = _load_json(target / "source.json")
        for name in ("decision_bundle.json", "strategy_table_ko.md", "decision_bundle_status.json"):
            if not (target / name).is_file():
                errors.append(f"stable latest artifact missing: {name}")
    elif status.get("decision_ready") is True:
        errors.append("status says decision-ready but source.json is missing")
    return {
        "market": market.upper(),
        "latest_run_id": status.get("latest_run_id"),
        "latest_decision_ready": status.get("decision_ready") is True,
        "latest_conditional_strategy_ready": status.get("conditional_strategy_ready") is True,
        "stable_source_run_id": source.get("decision_ready_run_id"),
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate decision bundle and stable Pages artifacts.")
    parser.add_argument("--archive-dir", type=Path)
    parser.add_argument("--run-dir", type=Path)
    parser.add_argument("--latest", action="store_true")
    parser.add_argument("--require-ready", action="store_true")
    parser.add_argument("--site-dir", type=Path)
    parser.add_argument("--market", choices=("kr", "us"))
    args = parser.parse_args()

    if args.site_dir:
        if not args.market:
            raise SystemExit("--market is required with --site-dir")
        result = verify_site(args.site_dir, market=args.market)
    else:
        run_dir = args.run_dir
        if run_dir is None and args.latest and args.archive_dir:
            run_dir = _latest_run_dir(args.archive_dir)
        if run_dir is None:
            raise SystemExit("Provide --run-dir or --archive-dir --latest")
        result = verify_run_dir(run_dir, require_ready=args.require_ready)
    print(json.dumps(result, ensure_ascii=False))
    if result.get("errors"):
        for error in result["errors"]:
            print(f"::error::{error}")
        return 1
    if result.get("conditional_strategy_ready") is True or result.get("latest_conditional_strategy_ready") is True:
        print("::warning::Decision bundle supports conditional strategy only; recheck live order and market status before execution.")
    elif result.get("decision_ready") is False or result.get("latest_decision_ready") is False:
        print("::warning::Decision bundle is valid but not ready for current-session investment decisions.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
