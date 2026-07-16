from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

from .packet import (
    PROMPT_CONTRACTS,
    SURFACES,
    WORK_REPORT_SCHEMA,
    WORK_SCHEMA,
    build_surface_packet,
    prompt_path,
    seal_packet,
)
from .runtime import validate_packet, validate_work_report


def build_work_site(
    *,
    site_dir: Path,
    archive_dir: Path,
    public_base_url: str = "",
) -> dict[str, Any]:
    root = Path(site_dir) / "work" / "v1"
    if root.exists():
        shutil.rmtree(root)
    (root / "prompts").mkdir(parents=True, exist_ok=True)
    base = str(public_base_url or "").strip().rstrip("/")
    packet_archive = Path(archive_dir) / "work-public" / "v1"
    index: dict[str, Any] = {
        "schema": WORK_SCHEMA,
        "streams": {},
    }

    for surface in SURFACES:
        source_prompt = prompt_path(surface)
        target_prompt = root / "prompts" / source_prompt.name
        shutil.copy2(source_prompt, target_prompt)
        packet = _fit_packet_budget(
            build_surface_packet(surface, archive_dir=archive_dir, public=True),
            max_chars=180_000,
        )
        validate_packet(packet, max_chars=180_000)
        if not _is_safe_public_packet(packet, surface=surface):
            raise ValueError(f"Refusing to publish unsafe public Work packet: {surface}")
        packet_bytes = (json.dumps(packet, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        packet_sha = hashlib.sha256(packet_bytes).hexdigest()
        event_name = _safe_name(str(packet["event_id"])) + ".json"
        archived_event_path = packet_archive / surface / "events" / event_name
        if archived_event_path.exists() and archived_event_path.read_bytes() != packet_bytes:
            raise ValueError(f"Immutable public Work event collision: {surface}/{event_name}")
        _write_bytes(archived_event_path, packet_bytes)
        events_root = root / surface / "events"
        cache_path = archived_event_path.parent.parent / "public-cache-v2.json"
        approved = _load_public_cache(cache_path, surface=surface)
        approved[event_name] = packet_sha
        safe_events = _latest_safe_event_files(
            archived_event_path.parent,
            surface=surface,
            approved_sha256=approved,
            limit=120,
        )
        for prior in safe_events:
            _write_bytes(events_root / prior.name, prior.read_bytes())
        _write_json(
            cache_path,
            {
                "schema": "tradingagents.work-public-cache/v2",
                "surface": surface,
                "events": {prior.name: hashlib.sha256(prior.read_bytes()).hexdigest() for prior in safe_events},
            },
        )
        _write_bytes(root / surface / "latest.json", packet_bytes)

        prefix = f"{base}/work/v1" if base else "/work/v1"
        status = {
            "schema": WORK_SCHEMA,
            "surface": surface,
            "event_id": packet["event_id"],
            "source_sha256": packet["source_sha256"],
            "packet_sha256": packet_sha,
            "prompt_contract_version": PROMPT_CONTRACTS[surface],
            "prompt_sha256": packet["prompt_sha256"],
            "skill_sha256": packet["skill_sha256"],
            "task_manifest_sha256": packet["task_manifest_sha256"],
            "workflow_contract_sha256": packet["workflow_contract_sha256"],
            "status_url": f"{prefix}/{surface}/status.json",
            "latest_url": f"{prefix}/{surface}/latest.json",
            "event_url": f"{prefix}/{surface}/events/{event_name}",
            "prompt_url": f"{prefix}/prompts/{source_prompt.name}",
            "source_health": (packet.get("body") or {}).get("source_health"),
            "report_mode": (packet.get("body") or {}).get("report_mode"),
        }
        report_status = _publish_latest_report(
            root=root,
            archive_dir=Path(archive_dir),
            surface=surface,
            url_prefix=prefix,
        )
        if report_status:
            status["integrated_report"] = report_status
        _write_json(root / surface / "status.json", status)
        index["streams"][surface] = status

    _write_json(root / "index.json", index)
    return index


def _publish_latest_report(
    *,
    root: Path,
    archive_dir: Path,
    surface: str,
    url_prefix: str,
) -> dict[str, Any]:
    latest_source = archive_dir / "work-reports" / surface / "latest.json"
    if not latest_source.is_file():
        return {}
    try:
        report = json.loads(latest_source.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Invalid latest Work report for {surface}: {exc}") from exc
    if not isinstance(report, dict):
        raise ValueError(f"Invalid latest Work report for {surface}: expected object")
    validate_work_report(report)
    if report.get("schema") != WORK_REPORT_SCHEMA or report.get("surface") != surface:
        raise ValueError(f"Latest Work report binding mismatch: {surface}")
    report_sha = str(report["report_sha256"])
    content_source = archive_dir / "work-reports" / surface / "events" / f"{report_sha}.json"
    if not content_source.is_file() or content_source.read_bytes() != latest_source.read_bytes():
        raise ValueError(f"Latest Work report is not backed by its content-addressed event: {surface}")
    target_root = root / surface / "report"
    _write_bytes(target_root / "events" / f"{report_sha}.json", content_source.read_bytes())
    _write_bytes(target_root / "latest.json", latest_source.read_bytes())
    return {
        "schema": WORK_REPORT_SCHEMA,
        "report_id": report.get("report_id"),
        "report_sha256": report_sha,
        "event_id": report.get("event_id"),
        "source_sha256": report.get("source_sha256"),
        "published_at": report.get("published_at"),
        "latest_url": f"{url_prefix}/{surface}/report/latest.json",
        "event_url": f"{url_prefix}/{surface}/report/events/{report_sha}.json",
    }


def _fit_packet_budget(packet: dict[str, Any], *, max_chars: int) -> dict[str, Any]:
    fitted = json.loads(json.dumps(packet, ensure_ascii=False))
    body = fitted.get("body") if isinstance(fitted.get("body"), dict) else {}
    events = body.get("events") if isinstance(body.get("events"), list) else None
    omitted = 0
    while events and len(json.dumps(fitted, ensure_ascii=False, indent=2)) > max_chars:
        events.pop()
        omitted += 1
        coverage = body.get("coverage") if isinstance(body.get("coverage"), dict) else {}
        coverage["transmitted_events"] = len(events)
        coverage["truncated"] = True
        coverage["omitted_due_to_packet_budget"] = omitted
        body["coverage"] = coverage
        fitted = seal_packet(str(packet.get("surface") or ""), body=body)
        body = fitted["body"]
        events = body.get("events") if isinstance(body.get("events"), list) else None
    return fitted


def _latest_safe_event_files(
    path: Path,
    *,
    surface: str,
    approved_sha256: dict[str, str],
    limit: int,
) -> list[Path]:
    """Return current-contract public events and purge unsafe legacy packets.

    ``work-public`` predates the public/private split and is persistent across
    Pages rebuilds.  Copying its files verbatim can therefore re-publish a
    legacy market packet containing portfolio membership or account actions.
    A packet is retained only when it was approved by the v2 cache ledger,
    is sealed by the current contract, and satisfies the current public
    recovery shape.  The first v2 build consequently removes all unproven
    legacy events.  Invalid files are deleted from the public-event cache; the
    private run archive is not modified.
    """

    if not path.exists():
        return []
    candidates = [candidate for candidate in path.glob("*.json") if candidate.is_file()]
    candidates.sort(key=lambda candidate: candidate.stat().st_mtime_ns, reverse=True)
    safe: list[Path] = []
    for candidate in candidates:
        try:
            candidate_sha = hashlib.sha256(candidate.read_bytes()).hexdigest()
        except OSError:
            candidate_sha = ""
        try:
            packet = json.loads(candidate.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            packet = None
        if (
            approved_sha256.get(candidate.name) == candidate_sha
            and isinstance(packet, dict)
            and _is_safe_public_packet(packet, surface=surface)
        ):
            if len(safe) < max(1, int(limit)):
                safe.append(candidate)
            continue
        try:
            candidate.unlink()
        except OSError as exc:
            raise RuntimeError(f"Could not purge unsafe public Work event {candidate}: {exc}") from exc
    return safe


def _load_public_cache(path: Path, *, surface: str) -> dict[str, str]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(payload, dict):
        return {}
    if payload.get("schema") != "tradingagents.work-public-cache/v2" or payload.get("surface") != surface:
        return {}
    events = payload.get("events") if isinstance(payload.get("events"), dict) else {}
    return {
        str(name): str(digest)
        for name, digest in events.items()
        if str(name).endswith(".json") and len(str(digest)) == 64
    }


_PRIVATE_MARKET_PACKET_KEYS = {
    "account",
    "account_id",
    "account_no",
    "account_number",
    "action_if_triggered",
    "action_now",
    "actions",
    "average_cost",
    "avg_price",
    "cash_available",
    "cash_balance",
    "cost_basis",
    "current_weight",
    "delta_krw",
    "delta_krw_if_triggered",
    "delta_krw_now",
    "holding",
    "holdings",
    "is_held",
    "is_owned",
    "market_value",
    "portfolio",
    "portfolio_relative_action",
    "position_metrics",
    "position_size",
    "position_value",
    "private_portfolio_overlay",
    "quantity",
    "shares",
    "target_value",
    "target_weight",
    "target_weight_if_triggered",
    "target_weight_now",
}


def _is_safe_public_packet(packet: dict[str, Any], *, surface: str) -> bool:
    """Verify integrity, current contract, and market privacy before publish."""

    if str(packet.get("surface") or "") != surface:
        return False
    try:
        validate_packet(packet, max_chars=180_000)
    except Exception:
        return False
    body = packet.get("body") if isinstance(packet.get("body"), dict) else {}
    expected = seal_packet(surface, body=body)
    if set(packet) != set(expected) or any(packet.get(key) != expected.get(key) for key in expected):
        return False
    if surface not in {"kr", "us"}:
        return True
    if _contains_private_market_key(body):
        return False
    current = body.get("current") if isinstance(body.get("current"), dict) else {}
    bundle = current.get("bundle") if isinstance(current.get("bundle"), dict) else {}
    if bundle:
        scope = bundle.get("transmission_scope") if isinstance(bundle.get("transmission_scope"), dict) else {}
        quality = bundle.get("quality") if isinstance(bundle.get("quality"), dict) else {}
        if scope.get("public_recovery_only") is not True:
            return False
        if scope.get("portfolio_membership_omitted") is not True:
            return False
        if quality.get("portfolio_membership_omitted") is not True:
            return False
    coverage = current.get("universe_coverage") if isinstance(current.get("universe_coverage"), dict) else {}
    if coverage and coverage.get("portfolio_coverage_details_omitted") is not True:
        return False
    return True


def _contains_private_market_key(value: Any) -> bool:
    if isinstance(value, dict):
        for key, item in value.items():
            if str(key).strip().lower() in _PRIVATE_MARKET_PACKET_KEYS:
                return True
            if _contains_private_market_key(item):
                return True
    elif isinstance(value, list):
        return any(_contains_private_market_key(item) for item in value)
    return False


def _safe_name(value: str) -> str:
    return "".join(character if character.isalnum() or character in "._-" else "-" for character in value)[:160]


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    _write_bytes(path, (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))


def _write_bytes(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
