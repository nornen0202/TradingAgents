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
    site_root = Path(site_dir)
    strategy_path = site_root / "mobile" / "strategy.json"
    payload = _load_object(strategy_path, label="mobile strategy payload")
    markets = payload.get("markets") if isinstance(payload.get("markets"), dict) else {}
    market = markets.get(key) if isinstance(markets.get(key), dict) else {}
    report = market.get("integrated_report") if isinstance(market.get("integrated_report"), dict) else {}
    publication_mode = "CURRENT_ACTION_CARDS"
    if not report:
        reference = market.get("reference_report") if isinstance(market.get("reference_report"), dict) else {}
        if not reference:
            raise ValueError("Built site did not publish the Work report in the strategy payload")
        report = reference
        publication_mode = "ANALYSIS_REFERENCE"
    if report.get("event_id") != event:
        raise ValueError("Built site Work report event does not match the handoff")
    if str(report.get("report_id") or "") != f"{key}:{report_sha[:32]}":
        raise ValueError("Built site Work report ID does not match the handoff hash")
    lineage = report.get("lineage") if isinstance(report.get("lineage"), dict) else {}
    if publication_mode == "CURRENT_ACTION_CARDS":
        if lineage.get("status") not in {"CURRENT_PACKET", "CURRENT_ANALYSIS_LINEAGE"}:
            raise ValueError(
                f"Built site Work report lineage is not current: {lineage.get('status') or 'missing'}"
            )
    else:
        _verify_safe_analysis_reference(report, lineage=lineage)

    public_report_path = site_root / "work" / "v1" / key / "report" / "latest.json"
    public_report = _load_object(public_report_path, label="public Work report")
    try:
        validate_work_report(public_report)
    except WorkRuntimeError as exc:
        raise ValueError(f"Public Work report failed schema validation: {exc}") from exc
    if (
        public_report.get("surface") != key
        or public_report.get("event_id") != event
        or str(public_report.get("report_sha256") or "").lower() != report_sha
    ):
        raise ValueError("Public Work report feed does not match the handoff")
    public_event_path = public_report_path.parent / "events" / f"{report_sha}.json"
    if not public_event_path.is_file() or public_event_path.read_bytes() != public_report_path.read_bytes():
        raise ValueError("Public Work report is not backed by the exact content-addressed event")
    return {
        "status": "SITE_VERIFIED",
        "surface": key,
        "event_id": event,
        "report_sha256": report_sha,
        "lineage_status": lineage["status"],
        "publication_mode": publication_mode,
        "current_action_cards_enriched": lineage.get("current_action_cards_enriched") is True,
        "strategy_path": str(strategy_path.resolve()),
        "public_report_path": str(public_report_path.resolve()),
    }


def _verify_safe_analysis_reference(report: dict[str, Any], *, lineage: dict[str, Any]) -> None:
    if lineage.get("status") != "PAST_REFERENCE":
        raise ValueError(
            f"Built site reference report has unsupported lineage: {lineage.get('status') or 'missing'}"
        )
    if lineage.get("current_action_cards_enriched") is not False:
        raise ValueError("Built site reference report can influence current action cards")
    if report.get("analysis_only") is not True:
        raise ValueError("Built site reference report is not marked analysis-only")
    structured = report.get("structured_report") if isinstance(report.get("structured_report"), dict) else {}
    for strategy in structured.get("strategies") or []:
        if isinstance(strategy, dict) and "execution" in strategy:
            raise ValueError("Built site reference report retained a stale per-ticker execution gate")


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
