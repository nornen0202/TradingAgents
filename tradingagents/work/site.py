from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

from .packet import PROMPT_CONTRACTS, SURFACES, WORK_SCHEMA, build_surface_packet, prompt_path, seal_packet
from .runtime import validate_packet


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
        packet_bytes = (json.dumps(packet, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        packet_sha = hashlib.sha256(packet_bytes).hexdigest()
        event_name = _safe_name(str(packet["event_id"])) + ".json"
        archived_event_path = packet_archive / surface / "events" / event_name
        if archived_event_path.exists() and archived_event_path.read_bytes() != packet_bytes:
            raise ValueError(f"Immutable public Work event collision: {surface}/{event_name}")
        _write_bytes(archived_event_path, packet_bytes)
        events_root = root / surface / "events"
        for prior in _latest_event_files(archived_event_path.parent, limit=120):
            _write_bytes(events_root / prior.name, prior.read_bytes())
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
        _write_json(root / surface / "status.json", status)
        index["streams"][surface] = status

    _write_json(root / "index.json", index)
    return index


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


def _latest_event_files(path: Path, *, limit: int) -> list[Path]:
    if not path.exists():
        return []
    files = [candidate for candidate in path.glob("*.json") if candidate.is_file()]
    files.sort(key=lambda candidate: candidate.stat().st_mtime_ns, reverse=True)
    return files[: max(1, int(limit))]


def _safe_name(value: str) -> str:
    return "".join(character if character.isalnum() or character in "._-" else "-" for character in value)[:160]


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    _write_bytes(path, (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))


def _write_bytes(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
