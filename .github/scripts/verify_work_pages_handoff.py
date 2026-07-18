from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from tradingagents.work.runtime import WorkRuntimeError, validate_work_report


_MARKET_SURFACES = {"kr", "us"}
_SHA256_RE = re.compile(r"[0-9a-f]{64}")


def verify_latest_report(
    archive_dir: Path,
    *,
    surface: str,
    event_id: str,
    report_sha256: str,
) -> dict[str, Any]:
    key, event, report_sha = _validated_binding(surface, event_id, report_sha256)
    report_path = Path(archive_dir) / "work-reports" / key / "latest.json"
    report = _load_object(report_path, label="latest Work report")
    try:
        validate_work_report(report)
    except WorkRuntimeError as exc:
        raise ValueError(f"Latest Work report failed schema validation: {exc}") from exc
    if report.get("surface") != key:
        raise ValueError("Latest Work report surface does not match the handoff")
    if report.get("event_id") != event:
        raise ValueError("Latest Work report event does not match the handoff")
    if str(report.get("report_sha256") or "").lower() != report_sha:
        raise ValueError("Latest Work report hash does not match the handoff")
    event_path = report_path.parent / "events" / f"{report_sha}.json"
    if not event_path.is_file() or event_path.read_bytes() != report_path.read_bytes():
        raise ValueError("Latest Work report is not backed by the exact content-addressed event")
    return {
        "status": "REPORT_VERIFIED",
        "surface": key,
        "event_id": event,
        "report_sha256": report_sha,
        "report_path": str(report_path.resolve()),
    }


def verify_built_site(
    site_dir: Path,
    *,
    surface: str,
    event_id: str,
    report_sha256: str,
) -> dict[str, Any]:
    key, event, report_sha = _validated_binding(surface, event_id, report_sha256)
    strategy_path = Path(site_dir) / "mobile" / "strategy.json"
    payload = _load_object(strategy_path, label="mobile strategy payload")
    markets = payload.get("markets") if isinstance(payload.get("markets"), dict) else {}
    market = markets.get(key) if isinstance(markets.get(key), dict) else {}
    report = market.get("integrated_report") if isinstance(market.get("integrated_report"), dict) else {}
    if not report:
        reference = market.get("reference_report") if isinstance(market.get("reference_report"), dict) else {}
        reason = ((reference.get("lineage") or {}).get("reason") if reference else None) or "missing"
        raise ValueError(
            f"Built site did not bind the Work report to current action cards; lineage reason: {reason}"
        )
    if report.get("event_id") != event:
        raise ValueError("Built site integrated report event does not match the handoff")
    if str(report.get("report_id") or "") != f"{key}:{report_sha[:32]}":
        raise ValueError("Built site integrated report ID does not match the handoff hash")
    lineage = report.get("lineage") if isinstance(report.get("lineage"), dict) else {}
    if lineage.get("status") not in {"CURRENT_PACKET", "CURRENT_ANALYSIS_LINEAGE"}:
        raise ValueError(f"Built site Work report lineage is not current: {lineage.get('status') or 'missing'}")
    return {
        "status": "SITE_VERIFIED",
        "surface": key,
        "event_id": event,
        "report_sha256": report_sha,
        "lineage_status": lineage["status"],
        "strategy_path": str(strategy_path.resolve()),
    }


def _validated_binding(surface: str, event_id: str, report_sha256: str) -> tuple[str, str, str]:
    key = str(surface or "").strip().lower()
    event = str(event_id or "").strip()
    report_sha = str(report_sha256 or "").strip().lower()
    if key not in _MARKET_SURFACES:
        raise ValueError("Work Pages handoff supports only KR/US market reports")
    if not event.startswith(f"{key}:"):
        raise ValueError("Work Pages handoff event does not match its surface")
    if not _SHA256_RE.fullmatch(report_sha):
        raise ValueError("Work Pages handoff report SHA-256 is invalid")
    return key, event, report_sha


def _load_object(path: Path, *, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Could not read {label}: {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"{label} is not a JSON object: {path}")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify exact Work report lineage before and after Pages rebuild.")
    parser.add_argument("phase", choices=("report", "site"))
    parser.add_argument("--surface", required=True, choices=("kr", "us"))
    parser.add_argument("--event-id", required=True)
    parser.add_argument("--report-sha256", required=True)
    parser.add_argument("--archive-dir", type=Path)
    parser.add_argument("--site-dir", type=Path)
    args = parser.parse_args()
    try:
        if args.phase == "report":
            if args.archive_dir is None:
                raise ValueError("--archive-dir is required for report verification")
            result = verify_latest_report(
                args.archive_dir,
                surface=args.surface,
                event_id=args.event_id,
                report_sha256=args.report_sha256,
            )
        else:
            if args.site_dir is None:
                raise ValueError("--site-dir is required for site verification")
            result = verify_built_site(
                args.site_dir,
                surface=args.surface,
                event_id=args.event_id,
                report_sha256=args.report_sha256,
            )
    except ValueError as exc:
        print(json.dumps({"status": "ERROR", "error": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
