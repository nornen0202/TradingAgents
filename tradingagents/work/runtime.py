from __future__ import annotations

import json
import math
import os
import re
import unicodedata
from contextlib import contextmanager
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Iterator

from .packet import (
    WORK_REPORT_SCHEMA,
    WORK_SCHEMA,
    WORK_STATE_SCHEMA,
    build_surface_packet,
    canonical_json,
    resolve_archive_roots,
    seal_packet,
    sha256_json,
)


class WorkRuntimeError(RuntimeError):
    pass


class WorkRuntime:
    def __init__(self, root: Path) -> None:
        self.root = Path(root)
        self.state_path = self.root / "state" / "state.json"
        self.ledger_path = self.root / "ledger" / "events.jsonl"
        self.outbox_dir = self.root / "outbox"
        self.drafts_dir = self.root / "drafts"
        self.latest_dir = self.root / "context"
        self.lock_dir = self.root / "locks"

    def prepare(
        self,
        surface: str,
        *,
        archive_dir: Path | None = None,
        youtube_archive_dir: Path | None = None,
        prism_archive_dir: Path | None = None,
        now: datetime | None = None,
    ) -> dict[str, Any]:
        key = surface.lower()
        with self.lock("state"):
            source_packet = build_surface_packet(
                key,
                archive_dir=archive_dir,
                youtube_archive_dir=youtube_archive_dir,
                prism_archive_dir=prism_archive_dir,
                now=now,
                public=False,
            )
            state = self._load_state()
            surface_state = state["surfaces"].setdefault(key, {})
            packet, event_hashes, material_noop = _delivery_packet(source_packet, surface_state)
            validate_packet(packet)
            event_id = str(packet["event_id"])
            event_path = self.outbox_dir / key / f"{_safe_name(event_id)}.json"
            event_bytes = (json.dumps(packet, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
            if event_path.exists():
                if event_path.read_bytes() != event_bytes:
                    raise WorkRuntimeError(f"Immutable event collision: {event_id}")
            else:
                _atomic_write_bytes(event_path, event_bytes)

            last_acked = str(surface_state.get("last_acked_event_id") or "")
            pending = str(surface_state.get("pending_event_id") or "")
            prepared_at = _now(now)
            coverage = _coverage_snapshot(packet)

            if _source_regressed(source_packet, surface_state):
                result = "SOURCE_REGRESSION"
                self._append_ledger(
                    {
                        "at": prepared_at,
                        "surface": key,
                        "event": "source_regression",
                        "event_id": event_id,
                        "coverage": coverage,
                        "previous_coverage": surface_state.get("last_acked_coverage"),
                    }
                )
            elif material_noop or last_acked == event_id:
                result = "NOOP"
                self._append_ledger(
                    {
                        "at": prepared_at,
                        "surface": key,
                        "event": "noop",
                        "event_id": event_id,
                    }
                )
            else:
                result = "RESUME" if pending == event_id else "NEW"
                if pending and pending != event_id:
                    self._append_ledger(
                        {
                            "at": prepared_at,
                            "surface": key,
                            "event": "superseded_pending",
                            "event_id": pending,
                            "superseded_by": event_id,
                        }
                    )
                if pending != event_id:
                    for field in (
                        "pending_report_id",
                        "pending_report_sha256",
                        "pending_report_path",
                        "pending_report_latest_path",
                        "pending_report_published_at",
                    ):
                        surface_state[field] = None
                surface_state.update(
                    {
                        "pending_event_id": event_id,
                        "pending_source_sha256": packet["source_sha256"],
                        "pending_packet_path": str(event_path.resolve()),
                        "pending_coverage": coverage,
                        "pending_event_hashes": event_hashes,
                        "pending_workflow_contract_sha256": packet["workflow_contract_sha256"],
                        "pending_upstream_source_sha256": source_packet["source_sha256"],
                        "prepared_at": prepared_at,
                    }
                )
                self._append_ledger(
                    {
                        "at": prepared_at,
                        "surface": key,
                        "event": "prepared" if result == "NEW" else "resumed",
                        "event_id": event_id,
                        "source_sha256": packet["source_sha256"],
                        "packet_path": str(event_path.resolve()),
                    }
                )

            latest = {
                "schema": WORK_SCHEMA,
                "surface": key,
                "event_id": event_id,
                "source_sha256": packet["source_sha256"],
                "packet_path": str(event_path.resolve()),
                "result": result,
                "updated_at": prepared_at,
            }
            _atomic_write_json(self.latest_dir / key / "latest.json", latest)
            surface_state["last_prepare_result"] = result
            surface_state["last_checked_at"] = prepared_at
            self._save_state(state)
            return {
                **latest,
                "prompt_path": str((Path(__file__).with_name("prompts") / _prompt_filename(key)).resolve()),
                "packet_chars": len(event_bytes.decode("utf-8")),
                "publish_required": key in {"kr", "us"},
                "report_markdown_path": str(
                    (self.drafts_dir / key / f"{_safe_name(event_id)}.md").resolve()
                ),
                "report_structured_path": str(
                    (self.drafts_dir / key / f"{_safe_name(event_id)}.json").resolve()
                ),
            }

    def publish(
        self,
        surface: str,
        event_id: str,
        source_sha256: str,
        *,
        report_markdown: str,
        structured_report: dict[str, Any],
        archive_dir: Path | None = None,
        now: datetime | None = None,
    ) -> dict[str, Any]:
        """Bind a final model report to an immutable packet and archive it by content hash."""

        key = surface.lower()
        effective_now = now or datetime.now().astimezone()
        with self.lock("state"):
            state = self._load_state()
            surface_state = state["surfaces"].setdefault(key, {})
            pending = str(surface_state.get("pending_event_id") or "")
            if pending != event_id:
                raise WorkRuntimeError(
                    f"Cannot publish {event_id}; current pending event is {pending or '(none)'}"
                )
            packet_path = Path(str(surface_state.get("pending_packet_path") or ""))
            packet = _load_json_object(packet_path, label="pending Work packet")
            validate_packet(packet)
            if packet.get("surface") != key or packet.get("event_id") != event_id:
                raise WorkRuntimeError("Publish surface/event does not match the immutable Work packet")
            if packet.get("source_sha256") != source_sha256:
                raise WorkRuntimeError("Publish source SHA-256 does not match the immutable Work packet")
            if surface_state.get("pending_source_sha256") != source_sha256:
                raise WorkRuntimeError("Publish source SHA-256 does not match canonical pending state")

            draft = json.loads(json.dumps(structured_report, ensure_ascii=False))
            _validate_report_draft(
                draft,
                surface=key,
                event_id=event_id,
                source_sha256=source_sha256,
            )
            _validate_report_packet_coverage(draft, packet, now=effective_now)
            markdown = str(report_markdown or "").strip()
            material = {
                "schema": WORK_REPORT_SCHEMA,
                "surface": key,
                "event_id": event_id,
                "source_sha256": source_sha256,
                "prompt_contract_version": packet.get("prompt_contract_version"),
                "workflow_contract_sha256": packet.get("workflow_contract_sha256"),
                "policy": _report_policy(),
                "report_markdown": markdown,
                "structured_report": draft,
            }
            report_sha256 = sha256_json(material)
            report_id = f"{key}:{report_sha256[:32]}"
            published_at = _now(effective_now)
            report = {
                **material,
                "report_id": report_id,
                "report_sha256": report_sha256,
                "published_at": published_at,
            }
            validate_work_report(report)

            archive_root = resolve_archive_roots(archive_dir=archive_dir)["market"]
            report_root = archive_root / "work-reports" / key
            report_path = report_root / "events" / f"{report_sha256}.json"
            if report_path.exists():
                existing = _load_json_object(report_path, label="content-addressed Work report")
                validate_work_report(existing)
                if _report_material(existing) != material:
                    raise WorkRuntimeError(f"Immutable Work report collision: {report_sha256}")
                report = existing
                published_at = str(existing.get("published_at") or published_at)
            else:
                _atomic_write_json(report_path, report)
            latest_path = report_root / "latest.json"
            _atomic_write_bytes(latest_path, report_path.read_bytes())

            surface_state.update(
                {
                    "pending_report_id": report_id,
                    "pending_report_sha256": report_sha256,
                    "pending_report_path": str(report_path.resolve()),
                    "pending_report_latest_path": str(latest_path.resolve()),
                    "pending_report_published_at": published_at,
                }
            )
            self._append_ledger(
                {
                    "at": published_at,
                    "surface": key,
                    "event": "report_published",
                    "event_id": event_id,
                    "source_sha256": source_sha256,
                    "report_id": report_id,
                    "report_sha256": report_sha256,
                    "report_path": str(report_path.resolve()),
                }
            )
            self._save_state(state)
            return {
                "schema": WORK_REPORT_SCHEMA,
                "surface": key,
                "event_id": event_id,
                "source_sha256": source_sha256,
                "report_id": report_id,
                "report_sha256": report_sha256,
                "report_path": str(report_path.resolve()),
                "latest_path": str(latest_path.resolve()),
                "published_at": published_at,
                "status": "PUBLISHED",
            }

    def acknowledge(self, surface: str, event_id: str, *, status: str = "rendered", now: datetime | None = None) -> dict[str, Any]:
        key = surface.lower()
        with self.lock("state"):
            state = self._load_state()
            surface_state = state["surfaces"].setdefault(key, {})
            pending = str(surface_state.get("pending_event_id") or "")
            if pending != event_id:
                raise WorkRuntimeError(
                    f"Cannot acknowledge {event_id}; current pending event is {pending or '(none)'}"
                )
            report = self._pending_report(surface_state, surface=key, event_id=event_id)
            if key in {"kr", "us"} and report is None:
                raise WorkRuntimeError(
                    f"Cannot acknowledge market event {event_id}; publish the final Work report first"
                )
            acknowledged_at = _now(now)
            acknowledged_source_sha256 = surface_state.get("pending_source_sha256")
            surface_state.update(
                {
                    "last_acked_event_id": event_id,
                    "last_acked_source_sha256": acknowledged_source_sha256,
                    "last_acked_packet_path": surface_state.get("pending_packet_path"),
                    "last_acked_coverage": surface_state.get("pending_coverage"),
                    "acked_event_hashes": surface_state.get("pending_event_hashes")
                    or surface_state.get("acked_event_hashes")
                    or {},
                    "last_acked_workflow_contract_sha256": surface_state.get(
                        "pending_workflow_contract_sha256"
                    ),
                    "last_acked_upstream_source_sha256": surface_state.get(
                        "pending_upstream_source_sha256"
                    ),
                    "last_acked_at": acknowledged_at,
                    "last_acked_status": status,
                    "last_acked_report_id": report.get("report_id") if report else None,
                    "last_acked_report_sha256": report.get("report_sha256") if report else None,
                    "last_acked_report_path": surface_state.get("pending_report_path") if report else None,
                    "pending_event_id": None,
                    "pending_source_sha256": None,
                    "pending_packet_path": None,
                    "pending_coverage": None,
                    "pending_event_hashes": None,
                    "pending_workflow_contract_sha256": None,
                    "pending_upstream_source_sha256": None,
                    "pending_report_id": None,
                    "pending_report_sha256": None,
                    "pending_report_path": None,
                    "pending_report_latest_path": None,
                    "pending_report_published_at": None,
                }
            )
            state["revision"] = int(state.get("revision") or 0) + 1
            self._append_ledger(
                {
                    "at": acknowledged_at,
                    "surface": key,
                    "event": "acknowledged",
                    "event_id": event_id,
                    "source_sha256": acknowledged_source_sha256,
                    "status": status,
                    "state_revision": state["revision"],
                    "report_id": report.get("report_id") if report else None,
                    "report_sha256": report.get("report_sha256") if report else None,
                }
            )
            self._save_state(state)
            return {
                "schema": WORK_STATE_SCHEMA,
                "surface": key,
                "event_id": event_id,
                "status": status,
                "state_revision": state["revision"],
                "acknowledged_at": acknowledged_at,
                "report_id": report.get("report_id") if report else None,
                "report_sha256": report.get("report_sha256") if report else None,
            }

    def _pending_report(
        self,
        surface_state: dict[str, Any],
        *,
        surface: str,
        event_id: str,
    ) -> dict[str, Any] | None:
        path_value = str(surface_state.get("pending_report_path") or "")
        if not path_value:
            return None
        report = _load_json_object(Path(path_value), label="pending Work report")
        validate_work_report(report)
        if report.get("surface") != surface or report.get("event_id") != event_id:
            raise WorkRuntimeError("Pending Work report does not match the event being acknowledged")
        if report.get("source_sha256") != surface_state.get("pending_source_sha256"):
            raise WorkRuntimeError("Pending Work report source does not match canonical pending state")
        if report.get("report_sha256") != surface_state.get("pending_report_sha256"):
            raise WorkRuntimeError("Pending Work report hash does not match canonical pending state")
        return report

    def status(self, surface: str | None = None) -> dict[str, Any]:
        state = self._load_state()
        if surface:
            return {
                "schema": WORK_STATE_SCHEMA,
                "revision": state.get("revision"),
                "surface": surface.lower(),
                "state": (state.get("surfaces") or {}).get(surface.lower(), {}),
            }
        return state

    def recover(
        self,
        surface: str,
        event_id: str,
        source_sha256: str,
        *,
        report_sha256: str | None = None,
        state_revision: int | None = None,
        archive_dir: Path | None = None,
        now: datetime | None = None,
    ) -> dict[str, Any]:
        """Recover canonical acknowledgement state from a visible receipt and immutable outbox packet."""

        key = surface.lower()
        with self.lock("state"):
            event_path = self.outbox_dir / key / f"{_safe_name(event_id)}.json"
            try:
                packet = json.loads(event_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                raise WorkRuntimeError(f"Recovery packet is unavailable: {event_path}: {exc}") from exc
            if not isinstance(packet, dict):
                raise WorkRuntimeError(f"Recovery packet is not an object: {event_path}")
            validate_packet(packet)
            if packet.get("surface") != key or packet.get("event_id") != event_id:
                raise WorkRuntimeError("Recovery receipt does not match the immutable outbox packet")
            if packet.get("source_sha256") != source_sha256:
                raise WorkRuntimeError("Recovery source SHA-256 does not match the immutable outbox packet")
            requested_revision = int(state_revision or 0)
            if requested_revision < 1:
                raise WorkRuntimeError("Recovery requires the positive state revision from a visible ACK receipt")
            state_was_valid = False
            state = {"schema": WORK_STATE_SCHEMA, "revision": 0, "surfaces": {}}
            if self.state_path.exists():
                try:
                    state = self._load_state()
                except WorkRuntimeError:
                    pass
                else:
                    state_was_valid = True
                    existing_surface_state = (state.get("surfaces") or {}).get(key)
                    if existing_surface_state is not None and (
                        not isinstance(existing_surface_state, dict) or existing_surface_state
                    ):
                        raise WorkRuntimeError(
                            "Recovery cannot replace existing canonical state for this surface"
                        )

            normalized_report_sha256 = str(report_sha256 or "").strip().lower() or None
            if key in {"kr", "us"} and normalized_report_sha256 is None:
                raise WorkRuntimeError("Market recovery requires report_sha256 from the visible ACK receipt")
            if not _ledger_has_acknowledgement(
                self.ledger_path,
                surface=key,
                event_id=event_id,
                state_revision=requested_revision,
                report_sha256=normalized_report_sha256 if key in {"kr", "us"} else None,
            ):
                raise WorkRuntimeError(
                    "Recovery receipt is not backed by the canonical acknowledgement ledger"
                )

            report = None
            report_path = None
            if normalized_report_sha256 is not None:
                report, report_path = _load_recovery_report(
                    surface=key,
                    event_id=event_id,
                    source_sha256=source_sha256,
                    report_sha256=normalized_report_sha256,
                    archive_dir=archive_dir,
                )
            previous_revision = int(state.get("revision") or 0) if state_was_valid else 0
            body = packet.get("body") if isinstance(packet.get("body"), dict) else {}
            event_hashes = {
                str(item.get("event_key")): str(item.get("content_sha256"))
                for item in (body.get("events") or [])
                if isinstance(item, dict) and item.get("event_key") and item.get("content_sha256")
            }
            recovered_at = _now(now)
            surface_state = state["surfaces"].setdefault(key, {})
            surface_state.update(
                {
                    "last_acked_event_id": event_id,
                    "last_acked_source_sha256": source_sha256,
                    "last_acked_packet_path": str(event_path.resolve()),
                    "last_acked_coverage": _coverage_snapshot(packet),
                    "acked_event_hashes": event_hashes,
                    "last_acked_workflow_contract_sha256": packet.get("workflow_contract_sha256"),
                    "last_acked_upstream_source_sha256": body.get("source_snapshot_sha256")
                    or source_sha256,
                    "last_acked_at": recovered_at,
                    "last_acked_status": "recovered_visible_receipt",
                    "last_acked_report_id": report.get("report_id") if report else None,
                    "last_acked_report_sha256": report.get("report_sha256") if report else None,
                    "last_acked_report_path": str(report_path.resolve()) if report_path else None,
                    "pending_event_id": None,
                    "pending_source_sha256": None,
                    "pending_packet_path": None,
                    "pending_coverage": None,
                    "pending_event_hashes": None,
                    "pending_workflow_contract_sha256": None,
                    "pending_upstream_source_sha256": None,
                    "pending_report_id": None,
                    "pending_report_sha256": None,
                    "pending_report_path": None,
                    "pending_report_latest_path": None,
                    "pending_report_published_at": None,
                }
            )
            # Recovery reconstructs an already acknowledged receipt; it does
            # not create a new analysis/ACK revision.  Preserve the greatest
            # canonical revision seen across sequential surface recovery.
            state["revision"] = max(previous_revision, requested_revision)
            self._append_ledger(
                {
                    "at": recovered_at,
                    "surface": key,
                    "event": "recovered_visible_receipt",
                    "event_id": event_id,
                    "source_sha256": source_sha256,
                    "state_revision": state["revision"],
                    "report_id": report.get("report_id") if report else None,
                    "report_sha256": report.get("report_sha256") if report else None,
                }
            )
            self._save_state(state)
            return {
                "schema": WORK_STATE_SCHEMA,
                "surface": key,
                "event_id": event_id,
                "status": "recovered_visible_receipt",
                "state_revision": state["revision"],
                "recovered_at": recovered_at,
                "report_id": report.get("report_id") if report else None,
                "report_sha256": report.get("report_sha256") if report else None,
            }

    @contextmanager
    def lock(self, surface: str) -> Iterator[None]:
        self.lock_dir.mkdir(parents=True, exist_ok=True)
        path = self.lock_dir / f"{_safe_name(surface)}.lock"
        try:
            descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError as exc:
            try:
                age = datetime.now().timestamp() - path.stat().st_mtime
            except OSError:
                age = 0
            if age > timedelta(hours=2).total_seconds():
                path.unlink(missing_ok=True)
                descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            else:
                raise WorkRuntimeError(f"BUSY_NO_STATE_ADVANCE: {surface}") from exc
        try:
            os.write(descriptor, str(os.getpid()).encode("ascii"))
            os.close(descriptor)
            yield
        finally:
            try:
                os.close(descriptor)
            except OSError:
                pass
            path.unlink(missing_ok=True)

    def _load_state(self) -> dict[str, Any]:
        if not self.state_path.exists():
            return {"schema": WORK_STATE_SCHEMA, "revision": 0, "surfaces": {}}
        try:
            payload = json.loads(self.state_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise WorkRuntimeError(f"Invalid canonical Work state: {self.state_path}: {exc}") from exc
        if not isinstance(payload, dict) or payload.get("schema") != WORK_STATE_SCHEMA:
            raise WorkRuntimeError(f"Unsupported canonical Work state schema: {self.state_path}")
        if not isinstance(payload.get("surfaces"), dict):
            payload["surfaces"] = {}
        return payload

    def _save_state(self, state: dict[str, Any]) -> None:
        _atomic_write_json(self.state_path, state)

    def _append_ledger(self, event: dict[str, Any]) -> None:
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
        with self.ledger_path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(canonical_json(event) + "\n")
            handle.flush()
            os.fsync(handle.fileno())


def _ledger_has_acknowledgement(
    ledger_path: Path,
    *,
    surface: str,
    event_id: str,
    state_revision: int,
    report_sha256: str | None,
) -> bool:
    try:
        lines = ledger_path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return False
    for line in reversed(lines):
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(item, dict):
            continue
        try:
            item_revision = int(item.get("state_revision") or 0)
        except (TypeError, ValueError):
            continue
        if (
            item.get("event") != "acknowledged"
            or str(item.get("surface") or "").lower() != surface
            or item.get("event_id") != event_id
            or item_revision != state_revision
        ):
            continue
        if report_sha256 is not None and item.get("report_sha256") != report_sha256:
            continue
        return True
    return False


def _load_recovery_report(
    *,
    surface: str,
    event_id: str,
    source_sha256: str,
    report_sha256: str,
    archive_dir: Path | None,
) -> tuple[dict[str, Any], Path]:
    archive_root = resolve_archive_roots(archive_dir=archive_dir)["market"]
    report_root = archive_root / "work-reports" / surface
    report_path = report_root / "events" / f"{report_sha256}.json"
    report = _load_json_object(report_path, label="recovery Work report")
    validate_work_report(report)
    if (
        report.get("surface") != surface
        or report.get("event_id") != event_id
        or report.get("source_sha256") != source_sha256
        or report.get("report_sha256") != report_sha256
    ):
        raise WorkRuntimeError("Recovery report does not match the visible ACK receipt and packet")
    latest_path = report_root / "latest.json"
    try:
        latest_bytes = latest_path.read_bytes()
        report_bytes = report_path.read_bytes()
    except OSError as exc:
        raise WorkRuntimeError(f"Recovery report latest pointer is unavailable: {exc}") from exc
    if latest_bytes != report_bytes:
        raise WorkRuntimeError("Recovery report is stale; it is not the latest content-addressed report")
    return report, report_path


def validate_packet(packet: dict[str, Any], *, max_chars: int = 600_000) -> None:
    required = (
        "schema",
        "surface",
        "event_id",
        "prompt_contract_version",
        "prompt_sha256",
        "skill_sha256",
        "task_manifest_sha256",
        "workflow_contract_sha256",
        "source_sha256",
        "body",
    )
    missing = [key for key in required if packet.get(key) in (None, "")]
    if missing:
        raise WorkRuntimeError(f"Work packet missing required keys: {', '.join(missing)}")
    if packet.get("schema") != WORK_SCHEMA:
        raise WorkRuntimeError(f"Unsupported Work packet schema: {packet.get('schema')}")
    surface = str(packet.get("surface") or "").strip().lower()
    if surface not in {"kr", "us", "youtube", "prism"}:
        raise WorkRuntimeError(f"Unsupported Work packet surface: {surface}")
    body = packet.get("body")
    if not isinstance(body, dict):
        raise WorkRuntimeError("Work packet body must be a JSON object")
    source_sha256 = str(packet.get("source_sha256") or "")
    if sha256_json(body) != source_sha256:
        raise WorkRuntimeError("Work packet source SHA-256 does not match its body")
    embedded_contract_hashes = {
        "prompt_sha256": packet.get("prompt_sha256"),
        "skill_sha256": packet.get("skill_sha256"),
        "task_manifest_sha256": packet.get("task_manifest_sha256"),
    }
    expected_workflow_contract_sha256 = sha256_json(
        {
            "version": packet.get("prompt_contract_version"),
            **embedded_contract_hashes,
        }
    )
    if packet.get("workflow_contract_sha256") != expected_workflow_contract_sha256:
        raise WorkRuntimeError("Work packet workflow contract SHA-256 is invalid")
    event_material = {
        "schema": WORK_SCHEMA,
        "surface": surface,
        "prompt_contract_version": packet.get("prompt_contract_version"),
        "workflow_contract_sha256": expected_workflow_contract_sha256,
        "source_sha256": source_sha256,
    }
    expected_event_id = f"{surface}:{sha256_json(event_material)[:32]}"
    if packet.get("event_id") != expected_event_id:
        raise WorkRuntimeError("Work packet event ID does not match its sealed content")
    if body.get("kind") in {"youtube", "prism"} and body.get("execution_eligible") is not False:
        raise WorkRuntimeError("Advisory source packet must set execution_eligible=false")
    size = len(json.dumps(packet, ensure_ascii=False, indent=2))
    if size > max_chars:
        raise WorkRuntimeError(f"Work packet is too large: {size} chars > {max_chars}")


_REPORT_STANCES = {"BUY", "HOLD", "REDUCE", "SELL", "AVOID", "RESEARCH"}
_ACTIONABLE_REPORT_STANCES = {"BUY", "HOLD", "REDUCE", "SELL", "AVOID"}
_REPORT_PORTFOLIO_ROLES = {"HOLDING", "WATCHLIST", "DISCOVERY"}
_REPORT_EXECUTION_READINESS = {
    "READY_NOW",
    "WAIT_FOR_TRIGGER",
    "NEEDS_LIVE_RECHECK",
    "MARKET_CLOSED",
    "DATA_OUTAGE",
    "RESEARCH_ONLY",
}
_EXTERNAL_EVIDENCE_RECEIPT_SCHEMA = "tradingagents.external-evidence-receipt/v1"
_EXTERNAL_EVIDENCE_SOURCES = ("youtube", "prism")
_HEALTHY_EXTERNAL_EVIDENCE_STATES = {"OK"}
_EXTERNAL_EVIDENCE_AFFECTED_FIELDS = {
    "ranking",
    "confidence",
    "position_size_within_existing_risk_limits",
    "research_priority",
}
_CONTRACT_PLACEHOLDER_RE = re.compile(
    r"^(?:none|null|n\s*/?\s*a|not\s+available|tbd|todo|unknown|pending|"
    r"없음|해당\s*없음|미정|미확인|산출\s*없음|추후\s*(?:확인|결정)|"
    r"(?:조건|트리거)\s*(?:충족\s*)?(?:시|때)?|(?:조건|데이터)\s*확인\s*(?:필요)?|"
    r"(?:확인|검토)\s*(?:필요|예정))$",
    re.IGNORECASE,
)
_CONTRACT_TAUTOLOGY_RE = re.compile(
    r"^(?:(?:매수|매도|보유|진입|청산|무효화)?\s*조건(?:이)?\s*"
    r"충족(?:되면|될\s*때|시)?(?:\s*(?:매수|매도|보유|진입|청산|실행))?|"
    r"(?:if|when)\s+(?:the\s+)?(?:entry|exit|buy|sell|trigger)?\s*conditions?\s+"
    r"(?:are\s+)?met(?:\s*(?:then|,)?\s*(?:buy|sell|hold|act|execute))?|"
    r"(?:when\s+)?trigger(?:ed)?\s+when\s+trigger(?:ed)?)$",
    re.IGNORECASE,
)
_CONCRETE_CONDITION_ANCHOR_RE = re.compile(
    r"(?:\d|[%$₩]|[<>≤≥]|이상|이하|상회|하회|돌파|이탈|교차|전환|증가|감소|"
    r"상향|하향|확대|축소|발생|해소|가격|종가|시가|고가|저가|vwap|거래량|"
    r"거래대금|수급|스프레드|spread|volume|price|close|open|earnings|guidance|"
    r"실적|가이던스|공시|filing|뉴스|news|halt|vi|luld|지지|저항|리스크|위험)",
    re.IGNORECASE,
)
_MARKET_EMPTY_STATE_RE = re.compile(
    r"(?:지금\s*실행\s*가능|현재\s*조건부\s*실행\s*가능|조건부\s*재확인)"
    r"\s*(?:여부\s*)?(?::|-|–|—)\s*"
    r"(?:\(\s*)?(?:없음|해당\s*없음|none|no\s+(?:actions?|items?|candidates?)|"
    r"n\s*/?\s*a|null)(?:\s*\))?(?=$|[\s.!?,;|])",
    re.IGNORECASE | re.MULTILINE,
)
_MARKET_RAW_STATUS_RE = re.compile(r"\bblocked\s*[- ]?\s*stale\b", re.IGNORECASE)
_REPORT_FORBIDDEN_KEYS = {
    "access_token",
    "account_product_code",
    "account_id",
    "account_no",
    "account_number",
    "acnt_prdt_cd",
    "approval_key",
    "api_key",
    "app_key",
    "app_secret",
    "appkey",
    "appsecret",
    "authorization",
    "bot_token",
    "broker_account_id",
    "broker_account_no",
    "cano",
    "client_id",
    "client_secret",
    "customer_id",
    "custtype",
    "mobile_dashboard_key",
    "odno",
    "order_id",
    "order_no",
    "order_number",
    "order_reference",
    "password",
    "private_key",
    "refresh_token",
    "secret",
    "session_file",
    "telegram_session",
    "token",
}
_REPORT_FORBIDDEN_KEYS_COLLAPSED = {key.replace("_", "") for key in _REPORT_FORBIDDEN_KEYS}
_REPORT_SECRET_MARKERS = (
    "MOBILE_DASHBOARD_KEY",
    "TELEGRAM_BOT_TOKEN",
    "KIS_APP_KEY",
    "KIS_APP_SECRET",
    "OPENAI_API_KEY",
    "telegram-stock-ai-agent.session",
    "Authorization: Bearer ",
)
_REPORT_SENSITIVE_VALUE_PATTERNS = (
    re.compile(
        r"(?i)(?:\baccount\s*(?:number|no\.?|id)|계좌\s*(?:번호|ID)|\bCANO|\bACNT_PRDT_CD|"
        r"\bODNO|\border[_\s-]?(?:id|no|number|reference)|\bclient[_\s-]?id|"
        r"\bcustomer[_\s-]?id|\bbroker[_\s-]?account[_\s-]?id)"
        r"(?:\s*[:=#]\s*|\s+)(?=[A-Z0-9._-]{3,}(?:\b|$))(?=[A-Z0-9._-]*\d)[A-Z0-9._-]+"
    ),
    re.compile(
        r"(?i)\b(?:access|refresh)[_\s-]?token"
        r"(?:\s*[:=#]\s*|\s+)[A-Z0-9._-]{3,}"
    ),
    re.compile(r"(?i)(?:[A-Z]:[\\/]+Users[\\/]+[^\\/\s]+|/(?:Users|home)/[^/\s]+)"),
)


def validate_work_report(report: dict[str, Any], *, max_chars: int = 500_000) -> None:
    required = (
        "schema",
        "surface",
        "event_id",
        "source_sha256",
        "prompt_contract_version",
        "workflow_contract_sha256",
        "report_id",
        "report_sha256",
        "published_at",
        "policy",
        "report_markdown",
        "structured_report",
    )
    missing = [key for key in required if report.get(key) in (None, "")]
    if missing:
        raise WorkRuntimeError(f"Work report missing required keys: {', '.join(missing)}")
    if report.get("schema") != WORK_REPORT_SCHEMA:
        raise WorkRuntimeError(f"Unsupported Work report schema: {report.get('schema')}")
    surface = str(report.get("surface") or "").lower()
    if surface not in {"kr", "us", "youtube", "prism"}:
        raise WorkRuntimeError(f"Unsupported Work report surface: {surface}")
    report_sha = str(report.get("report_sha256") or "")
    if len(report_sha) != 64 or any(character not in "0123456789abcdef" for character in report_sha):
        raise WorkRuntimeError("Work report SHA-256 is invalid")
    if report.get("report_id") != f"{surface}:{report_sha[:32]}":
        raise WorkRuntimeError("Work report ID does not match its content hash")
    if sha256_json(_report_material(report)) != report_sha:
        raise WorkRuntimeError("Work report content hash verification failed")
    if _parse_datetime(report.get("published_at")) is None:
        raise WorkRuntimeError("Work report published_at is invalid")
    if report.get("policy") != _report_policy():
        raise WorkRuntimeError("Work report policy is missing or unsupported")
    _validate_report_draft(
        report.get("structured_report"),
        surface=surface,
        event_id=str(report.get("event_id") or ""),
        source_sha256=str(report.get("source_sha256") or ""),
    )
    markdown = str(report.get("report_markdown") or "")
    if not markdown.strip():
        raise WorkRuntimeError("Work report Markdown is empty")
    if "\x00" in markdown or _find_sensitive_report_text(markdown):
        raise WorkRuntimeError("Work report Markdown contains a blocked secret, identifier, or local path")
    if surface in {"kr", "us"} and _contains_blocked_market_markdown(markdown):
        raise WorkRuntimeError("Market investor Markdown contains a blocked empty-state or raw status code")
    size = len(json.dumps(report, ensure_ascii=False, indent=2))
    if size > max_chars:
        raise WorkRuntimeError(f"Work report is too large: {size} chars > {max_chars}")


def _validate_report_draft(
    draft: Any,
    *,
    surface: str,
    event_id: str,
    source_sha256: str,
) -> None:
    if not isinstance(draft, dict):
        raise WorkRuntimeError("Structured Work report must be a JSON object")
    binding = draft.get("binding") if isinstance(draft.get("binding"), dict) else {}
    expected_binding = {
        "surface": surface,
        "event_id": event_id,
        "source_sha256": source_sha256,
    }
    if any(binding.get(key) != value for key, value in expected_binding.items()):
        raise WorkRuntimeError("Structured Work report binding does not match the prepared packet")
    required = (
        "title",
        "generated_at",
        "summary",
        "top_actions",
        "strategies",
        "coverage_receipt",
        "source_summary",
        "next_checkpoint",
    )
    missing = [key for key in required if key not in draft]
    if missing:
        raise WorkRuntimeError(f"Structured Work report missing keys: {', '.join(missing)}")
    if not str(draft.get("title") or "").strip() or _parse_datetime(draft.get("generated_at")) is None:
        raise WorkRuntimeError("Structured Work report title/generated_at is invalid")
    top_actions = draft.get("top_actions")
    strategies = draft.get("strategies")
    if not isinstance(top_actions, list) or len(top_actions) > 20:
        raise WorkRuntimeError("Structured Work report top_actions must be a list of at most 20 items")
    if not isinstance(strategies, list) or len(strategies) > 250:
        raise WorkRuntimeError("Structured Work report strategies must be a list of at most 250 items")
    if not isinstance(draft.get("source_summary"), dict):
        raise WorkRuntimeError("Structured Work report source_summary must be an object")
    if surface in {"kr", "us"}:
        ranks: set[float] = set()
        strategy_tickers: set[str] = set()
        for index, strategy in enumerate(strategies):
            if not isinstance(strategy, dict) or not str(strategy.get("ticker") or "").strip():
                raise WorkRuntimeError(f"Structured market strategy {index} is missing a ticker")
            ticker = str(strategy.get("ticker") or "").strip().upper()
            if ticker in strategy_tickers:
                raise WorkRuntimeError(f"Structured market report repeats canonical tickers: {ticker}")
            strategy_tickers.add(ticker)
            rank = strategy.get("rank")
            if (
                isinstance(rank, bool)
                or not isinstance(rank, (int, float))
                or not math.isfinite(float(rank))
                or float(rank) <= 0
            ):
                raise WorkRuntimeError(f"Structured market strategy {ticker} rank must be positive numeric")
            normalized_rank = float(rank)
            if normalized_rank in ranks:
                raise WorkRuntimeError(f"Structured market strategy rank must be unique: {rank}")
            ranks.add(normalized_rank)
            portfolio_role = str(strategy.get("portfolio_role") or "").strip().upper()
            if portfolio_role not in _REPORT_PORTFOLIO_ROLES:
                raise WorkRuntimeError(
                    f"Structured market strategy {ticker} has invalid portfolio_role"
                )
            thesis = strategy.get("thesis") if isinstance(strategy.get("thesis"), dict) else {}
            execution = strategy.get("execution") if isinstance(strategy.get("execution"), dict) else {}
            stance = str(thesis.get("stance") or "").upper()
            readiness = str(execution.get("readiness") or "").upper()
            if stance not in _REPORT_STANCES:
                raise WorkRuntimeError(f"Structured market strategy {index} has invalid thesis stance")
            if readiness not in _REPORT_EXECUTION_READINESS:
                raise WorkRuntimeError(f"Structured market strategy {index} has invalid execution readiness")
            confidence = thesis.get("confidence")
            if (
                isinstance(confidence, bool)
                or not isinstance(confidence, (int, float))
                or not math.isfinite(float(confidence))
                or not 0 <= float(confidence) <= 1
            ):
                raise WorkRuntimeError(
                    f"Structured market strategy {ticker} confidence must be numeric from 0 to 1"
                )
            entry_conditions = thesis.get("entry_conditions", [])
            invalidation_conditions = thesis.get("invalidation_conditions", [])
            if not isinstance(entry_conditions, list):
                raise WorkRuntimeError(f"Structured market strategy {index} entry_conditions must be a list")
            if not isinstance(invalidation_conditions, list):
                raise WorkRuntimeError(
                    f"Structured market strategy {index} invalidation_conditions must be a list"
                )
            if not _has_meaningful_contract_value(thesis.get("invalidation_action")):
                raise WorkRuntimeError(
                    f"Structured market strategy {ticker} thesis requires invalidation_action"
                )
            if stance in _ACTIONABLE_REPORT_STANCES:
                _validate_condition_list(entry_conditions, ticker=ticker, field="entry_conditions")
                _validate_condition_list(
                    invalidation_conditions,
                    ticker=ticker,
                    field="invalidation_conditions",
                )
                for field in ("horizon", "position_sizing"):
                    if not _has_meaningful_contract_value(thesis.get(field)):
                        raise WorkRuntimeError(
                            f"Structured market strategy {ticker} actionable thesis requires {field}"
                        )
            else:
                if entry_conditions:
                    _validate_condition_list(entry_conditions, ticker=ticker, field="entry_conditions")
                if invalidation_conditions:
                    _validate_condition_list(
                        invalidation_conditions,
                        ticker=ticker,
                        field="invalidation_conditions",
                    )
                if (not entry_conditions or not invalidation_conditions) and not _has_meaningful_contract_value(
                    thesis.get("data_needed_reason")
                ):
                    raise WorkRuntimeError(
                        f"Structured market strategy {ticker} RESEARCH thesis requires data_needed_reason when conditions are incomplete"
                    )
            _validate_strategy_action_contract(execution, ticker=ticker, readiness=readiness)
            for field in ("required_rechecks", "blockers"):
                if not isinstance(execution.get(field, []), list):
                    raise WorkRuntimeError(
                        f"Structured market strategy {index} execution {field} must be a list"
                    )
            contributions = strategy.get("source_contributions", [])
            if not isinstance(contributions, list):
                raise WorkRuntimeError(f"Structured market strategy {index} source_contributions must be a list")
            for contribution in contributions:
                if not isinstance(contribution, dict):
                    raise WorkRuntimeError(
                        f"Structured market strategy {index} has an invalid source contribution"
                    )
                if contribution.get("execution_gate_override") is True:
                    raise WorkRuntimeError("External evidence cannot override an execution gate")
        _validate_top_actions(top_actions, strategies)
    forbidden = _find_forbidden_report_key(draft)
    if forbidden:
        raise WorkRuntimeError(f"Structured Work report contains forbidden key: {forbidden}")
    if _find_sensitive_report_text(draft):
        raise WorkRuntimeError("Structured Work report contains a blocked secret, identifier, or local path")


def _validate_report_packet_coverage(
    draft: dict[str, Any],
    packet: dict[str, Any],
    *,
    now: datetime,
) -> None:
    surface = str(packet.get("surface") or "").lower()
    if surface not in {"kr", "us"}:
        return
    body = packet.get("body") if isinstance(packet.get("body"), dict) else {}
    current = body.get("current") if isinstance(body.get("current"), dict) else {}
    bundle = current.get("bundle") if isinstance(current.get("bundle"), dict) else {}
    packet_rows = [row for row in (bundle.get("strategy_table") or []) if isinstance(row, dict)]
    expected = {
        _report_ticker_identity(row.get("ticker"))
        for row in packet_rows
        if _report_ticker_identity(row.get("ticker"))
    }
    strategies = [item for item in (draft.get("strategies") or []) if isinstance(item, dict)]
    rendered_identities = [
        _report_ticker_identity(item.get("ticker"))
        for item in strategies
        if _report_ticker_identity(item.get("ticker"))
    ]
    rendered = set(rendered_identities)
    duplicates = sorted(
        identity for identity in rendered if rendered_identities.count(identity) > 1
    )
    missing = sorted(expected - rendered)
    unknown = sorted(rendered - expected)
    if duplicates:
        raise WorkRuntimeError(
            "Structured market report repeats canonical tickers: " + ", ".join(duplicates)
        )
    if missing:
        raise WorkRuntimeError(
            "Structured market report omits prepared packet tickers: " + ", ".join(missing)
        )
    if unknown:
        raise WorkRuntimeError(
            "Structured market report contains unknown tickers: " + ", ".join(unknown)
        )
    packet_coverage = (
        current.get("universe_coverage")
        if isinstance(current.get("universe_coverage"), dict)
        else {}
    )
    if draft.get("coverage_receipt") != packet_coverage:
        raise WorkRuntimeError(
            "Structured market report coverage_receipt does not exactly match the prepared packet"
        )

    model_provenance = (
        body.get("model_provenance")
        if isinstance(body.get("model_provenance"), dict)
        else {}
    )
    if draft.get("model_receipt") != model_provenance:
        raise WorkRuntimeError(
            "Structured market report model_receipt does not exactly match the prepared packet"
        )

    _validate_external_evidence_binding(draft, packet, strategies=strategies)

    packet_by_identity = {
        _report_ticker_identity(row.get("ticker")): row
        for row in packet_rows
        if _report_ticker_identity(row.get("ticker"))
    }
    strategy_by_identity = {
        _report_ticker_identity(item.get("ticker")): item
        for item in strategies
        if _report_ticker_identity(item.get("ticker"))
    }
    for identity in sorted(expected):
        _validate_report_execution_gate(
            strategy_by_identity[identity],
            packet_by_identity[identity],
            ticker=identity,
            now=now,
        )


def _validate_external_evidence_binding(
    draft: dict[str, Any],
    packet: dict[str, Any],
    *,
    strategies: list[dict[str, Any]],
) -> None:
    body = packet.get("body") if isinstance(packet.get("body"), dict) else {}
    context = (
        body.get("supporting_context")
        if isinstance(body.get("supporting_context"), dict)
        else {}
    )
    expected_receipt = _external_evidence_receipt(context)
    if context.get("receipt_contract") != expected_receipt:
        raise WorkRuntimeError(
            "Prepared packet external-evidence receipt contract does not match its transmitted events"
        )
    source_summary = (
        draft.get("source_summary") if isinstance(draft.get("source_summary"), dict) else {}
    )
    if source_summary.get("external_evidence_receipt") != expected_receipt:
        raise WorkRuntimeError(
            "Structured market report external-evidence receipt does not exactly match the prepared packet"
        )

    transmitted: dict[tuple[str, str], set[str]] = {}
    matched_by_ticker: dict[str, set[tuple[str, str]]] = {}
    for source in _EXTERNAL_EVIDENCE_SOURCES:
        payload = context.get(source) if isinstance(context.get(source), dict) else {}
        healthy = str(payload.get("source_health") or "").strip().upper()
        for event in payload.get("events") or []:
            if not isinstance(event, dict) or event.get("event_key") is None:
                continue
            pair = (source, str(event.get("event_key")))
            relevance = event.get("relevance") if isinstance(event.get("relevance"), dict) else {}
            matched = {
                identity
                for ticker in (relevance.get("matched_tickers") or [])
                if (identity := _report_ticker_identity(ticker))
            }
            transmitted[pair] = matched
            if healthy not in _HEALTHY_EXTERNAL_EVIDENCE_STATES:
                continue
            for identity in matched:
                matched_by_ticker.setdefault(identity, set()).add(pair)

    any_relevant_healthy_event = bool(matched_by_ticker)
    any_source_contribution = False
    for strategy in strategies:
        identity = _report_ticker_identity(strategy.get("ticker"))
        contributions = strategy.get("source_contributions") or []
        if contributions:
            any_source_contribution = True
        qualifying_pairs: set[tuple[str, str]] = set()
        for contribution in contributions:
            if not isinstance(contribution, dict):
                continue
            source = str(contribution.get("source") or "").strip().lower()
            if source not in _EXTERNAL_EVIDENCE_SOURCES:
                continue
            event_key = str(contribution.get("event_key") or "").strip()
            affected_field = str(contribution.get("affected_field") or "").strip()
            if not event_key or not affected_field:
                raise WorkRuntimeError(
                    f"Structured market strategy {identity} external contribution requires event_key and affected_field"
                )
            if affected_field not in _EXTERNAL_EVIDENCE_AFFECTED_FIELDS:
                raise WorkRuntimeError(
                    f"Structured market strategy {identity} external contribution has unsupported affected_field"
                )
            pair = (source, event_key)
            if pair not in transmitted:
                raise WorkRuntimeError(
                    f"Structured market strategy {identity} cites an event outside the prepared packet"
                )
            if identity in transmitted[pair]:
                qualifying_pairs.add(pair)

        required_pairs = matched_by_ticker.get(identity, set())
        if required_pairs and not (required_pairs & qualifying_pairs):
            raise WorkRuntimeError(
                f"Structured market strategy {identity} omits a matched healthy external-evidence contribution"
            )
        if any_relevant_healthy_event and not required_pairs:
            reason = str(strategy.get("no_relevant_evidence_reason") or "").strip()
            if not reason:
                raise WorkRuntimeError(
                    f"Structured market strategy {identity} requires no_relevant_evidence_reason"
                )

    if any_relevant_healthy_event and not any_source_contribution:
        raise WorkRuntimeError(
            "Structured market report source_contributions cannot be empty when relevant healthy external evidence exists"
        )


def _external_evidence_receipt(context: dict[str, Any]) -> dict[str, Any]:
    sources: dict[str, Any] = {}
    for source in _EXTERNAL_EVIDENCE_SOURCES:
        payload = context.get(source) if isinstance(context.get(source), dict) else {}
        events = [event for event in (payload.get("events") or []) if isinstance(event, dict)]
        sources[source] = {
            "source_health": payload.get("source_health"),
            "event_keys": [
                str(event.get("event_key"))
                for event in events
                if event.get("event_key") is not None
            ],
            "coverage": payload.get("coverage") if isinstance(payload.get("coverage"), dict) else {},
        }
    return {
        "schema": _EXTERNAL_EVIDENCE_RECEIPT_SCHEMA,
        "sources": sources,
    }


def _validate_condition_list(items: list[Any], *, ticker: str, field: str) -> None:
    if not items:
        raise WorkRuntimeError(
            f"Structured market strategy {ticker} actionable thesis requires nonempty {field}"
        )
    for index, item in enumerate(items):
        text = _contract_text(item)
        if (
            not text
            or _CONTRACT_PLACEHOLDER_RE.fullmatch(text)
            or _CONTRACT_TAUTOLOGY_RE.fullmatch(text)
            or not _CONCRETE_CONDITION_ANCHOR_RE.search(text)
        ):
            raise WorkRuntimeError(
                f"Structured market strategy {ticker} {field}[{index}] must be concrete and non-placeholder"
            )


def _contract_text(value: Any) -> str:
    if isinstance(value, str):
        raw = value
    elif isinstance(value, dict) and value:
        raw = canonical_json(value)
    else:
        return ""
    normalized = unicodedata.normalize("NFKC", raw).replace("\u200b", "")
    normalized = re.sub(r"[*_`~]+", "", normalized)
    normalized = " ".join(normalized.split())
    return normalized.strip(" \t\r\n-–—:;,.!?()[]{}\"'")


def _has_meaningful_contract_value(value: Any) -> bool:
    if isinstance(value, str):
        text = _contract_text(value)
        return bool(text and not _CONTRACT_PLACEHOLDER_RE.fullmatch(text))
    if isinstance(value, dict):
        return bool(value) and any(_has_meaningful_contract_value(item) for item in value.values())
    if isinstance(value, (list, tuple)):
        return bool(value) and any(_has_meaningful_contract_value(item) for item in value)
    return (
        not isinstance(value, bool)
        and isinstance(value, (int, float))
        and math.isfinite(float(value))
    )


def _validate_strategy_action_contract(
    execution: dict[str, Any],
    *,
    ticker: str,
    readiness: str,
) -> None:
    action_now = _has_report_action(execution.get("action_now"))
    action_if_triggered = _has_report_action(execution.get("action_if_triggered"))
    if readiness == "READY_NOW":
        if not action_now:
            raise WorkRuntimeError(
                f"Structured market strategy {ticker} READY_NOW requires action_now"
            )
        if action_if_triggered:
            raise WorkRuntimeError(
                f"Structured market strategy {ticker} READY_NOW cannot carry action_if_triggered"
            )
    elif readiness == "WAIT_FOR_TRIGGER":
        if not action_if_triggered:
            raise WorkRuntimeError(
                f"Structured market strategy {ticker} WAIT_FOR_TRIGGER requires action_if_triggered"
            )
        if action_now:
            raise WorkRuntimeError(
                f"Structured market strategy {ticker} WAIT_FOR_TRIGGER cannot carry action_now"
            )
    elif action_now or action_if_triggered:
        raise WorkRuntimeError(
            f"Structured market strategy {ticker} non-actionable readiness cannot carry an action"
        )


def _validate_top_actions(top_actions: list[Any], strategies: list[Any]) -> None:
    strategy_by_ticker = {
        str(strategy.get("ticker") or "").strip().upper(): strategy
        for strategy in strategies
        if isinstance(strategy, dict) and str(strategy.get("ticker") or "").strip()
    }
    seen: set[str] = set()
    for index, top_action in enumerate(top_actions):
        if not isinstance(top_action, dict):
            raise WorkRuntimeError(f"Structured market top_action {index} must be an object")
        ticker = str(top_action.get("ticker") or "").strip().upper()
        if ticker not in strategy_by_ticker:
            raise WorkRuntimeError(
                f"Structured market top_action {index} references unknown strategy ticker: {ticker or '(missing)'}"
            )
        if ticker in seen:
            raise WorkRuntimeError(f"Structured market top_actions repeat ticker: {ticker}")
        seen.add(ticker)
        strategy = strategy_by_ticker[ticker]
        execution = strategy.get("execution") if isinstance(strategy.get("execution"), dict) else {}
        strategy_readiness = str(execution.get("readiness") or "").strip().upper()
        top_readiness = str(top_action.get("readiness") or "").strip().upper()
        if top_readiness != strategy_readiness:
            raise WorkRuntimeError(
                f"Structured market top_action {ticker} readiness does not match its strategy"
            )
        expected_action = (
            execution.get("action_now")
            if strategy_readiness == "READY_NOW"
            else execution.get("action_if_triggered")
            if strategy_readiness == "WAIT_FOR_TRIGGER"
            else None
        )
        supplied_action = top_action.get("action")
        if _has_report_action(expected_action):
            if not _has_report_action(supplied_action) or not _report_actions_equal(
                supplied_action,
                expected_action,
            ):
                raise WorkRuntimeError(
                    f"Structured market top_action {ticker} action does not match its strategy"
                )
        elif _has_report_action(supplied_action):
            raise WorkRuntimeError(
                f"Structured market top_action {ticker} action is not allowed for its strategy readiness"
            )


def _report_actions_equal(left: Any, right: Any) -> bool:
    if isinstance(left, str) and isinstance(right, str):
        return " ".join(left.split()).casefold() == " ".join(right.split()).casefold()
    return canonical_json(left) == canonical_json(right)


def _validate_report_execution_gate(
    strategy: dict[str, Any],
    packet_row: dict[str, Any],
    *,
    ticker: str,
    now: datetime,
) -> None:
    report_execution = (
        strategy.get("execution") if isinstance(strategy.get("execution"), dict) else {}
    )
    packet_execution = (
        packet_row.get("execution") if isinstance(packet_row.get("execution"), dict) else {}
    )
    report_readiness = str(report_execution.get("readiness") or "").strip().upper()
    packet_readiness = str(packet_execution.get("readiness") or "").strip().upper()
    if report_readiness == "READY_NOW" and packet_readiness != "READY_NOW":
        raise WorkRuntimeError(
            f"Structured market strategy {ticker} promotes packet execution to READY_NOW"
        )
    if report_readiness == "WAIT_FOR_TRIGGER" and packet_readiness not in {
        "READY_NOW",
        "WAIT_FOR_TRIGGER",
    }:
        raise WorkRuntimeError(
            f"Structured market strategy {ticker} promotes a blocked packet to WAIT_FOR_TRIGGER"
        )

    packet_valid_until = _parse_datetime(packet_execution.get("valid_until"))
    report_valid_until = _parse_datetime(report_execution.get("valid_until"))
    if packet_valid_until and report_valid_until and report_valid_until > packet_valid_until:
        raise WorkRuntimeError(
            f"Structured market strategy {ticker} extends the packet execution validity"
        )

    executable = report_readiness in {"READY_NOW", "WAIT_FOR_TRIGGER"}
    if executable:
        effective_now = _parse_datetime(now.isoformat())
        quality = packet_row.get("quality") if isinstance(packet_row.get("quality"), dict) else {}
        if quality.get("expired_at_build") is True:
            raise WorkRuntimeError(
                f"Structured market strategy {ticker} makes an expired packet row executable"
            )
        if packet_valid_until is None or effective_now is None or packet_valid_until <= effective_now:
            raise WorkRuntimeError(
                f"Structured market strategy {ticker} uses packet execution validity that has expired"
            )
        if report_valid_until is None or report_valid_until <= effective_now:
            raise WorkRuntimeError(
                f"Structured market strategy {ticker} has no current execution validity"
            )
        packet_as_of = _parse_datetime(packet_execution.get("as_of"))
        report_as_of = _parse_datetime(report_execution.get("as_of"))
        if packet_as_of is None or report_as_of != packet_as_of:
            raise WorkRuntimeError(
                f"Structured market strategy {ticker} execution as_of does not match the packet"
            )

    for field in ("blockers", "required_rechecks"):
        packet_items = _normalized_report_items(packet_execution.get(field))
        report_items = _normalized_report_items(report_execution.get(field))
        missing_items = sorted(packet_items - report_items)
        if missing_items:
            raise WorkRuntimeError(
                f"Structured market strategy {ticker} omits packet execution {field}: "
                + ", ".join(missing_items)
            )

    if report_readiness != "READY_NOW" and _has_report_action(report_execution.get("action_now")):
        raise WorkRuntimeError(
            f"Structured market strategy {ticker} has action_now without READY_NOW"
        )
    if report_readiness != "WAIT_FOR_TRIGGER" and _has_report_action(
        report_execution.get("action_if_triggered")
    ):
        raise WorkRuntimeError(
            f"Structured market strategy {ticker} has action_if_triggered without WAIT_FOR_TRIGGER"
        )


def _has_report_action(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        text = _contract_text(value)
        return bool(text and not _CONTRACT_PLACEHOLDER_RE.fullmatch(text))
    if isinstance(value, (list, dict, tuple, set)):
        return bool(value)
    return bool(value)


def _contains_blocked_market_markdown(markdown: str) -> bool:
    normalized = unicodedata.normalize("NFKC", str(markdown or "")).replace("\u200b", "")
    normalized = re.sub(r"[*_`~]+", "", normalized)
    normalized = re.sub(r"[ \t\f\v]+", " ", normalized)
    return bool(
        _MARKET_RAW_STATUS_RE.search(normalized)
        or _MARKET_EMPTY_STATE_RE.search(normalized)
    )


def _normalized_report_items(value: Any) -> set[str]:
    if not isinstance(value, list):
        return set()
    return {
        " ".join(str(item).split()).casefold()
        for item in value
        if " ".join(str(item).split())
    }


def _report_ticker_identity(value: Any) -> str:
    ticker = str(value or "").strip().upper()
    for suffix in (".KS", ".KQ"):
        if ticker.endswith(suffix):
            return ticker[: -len(suffix)]
    return ticker


def _find_forbidden_report_key(value: Any) -> str | None:
    if isinstance(value, dict):
        for key, item in value.items():
            normalized = re.sub(r"[^a-z0-9]+", "_", str(key).strip().lower()).strip("_")
            if (
                normalized in _REPORT_FORBIDDEN_KEYS
                or normalized.replace("_", "") in _REPORT_FORBIDDEN_KEYS_COLLAPSED
            ):
                return str(key)
            nested = _find_forbidden_report_key(item)
            if nested:
                return nested
    elif isinstance(value, list):
        for item in value:
            nested = _find_forbidden_report_key(item)
            if nested:
                return nested
    return None


def _find_sensitive_report_text(value: Any) -> str | None:
    if isinstance(value, dict):
        for item in value.values():
            matched = _find_sensitive_report_text(item)
            if matched:
                return matched
    elif isinstance(value, list):
        for item in value:
            matched = _find_sensitive_report_text(item)
            if matched:
                return matched
    elif isinstance(value, str):
        if any(marker in value for marker in _REPORT_SECRET_MARKERS):
            return "secret_marker"
        for pattern in _REPORT_SENSITIVE_VALUE_PATTERNS:
            if pattern.search(value):
                return pattern.pattern
    return None


def _report_policy() -> dict[str, Any]:
    return {
        "visibility": "investor_safe_no_credentials",
        "external_evidence_profile": "balanced_external",
        "external_evidence_may_affect": [
            "ranking",
            "confidence",
            "position_size_within_existing_risk_limits",
            "research_priority",
        ],
        "external_evidence_may_bypass_execution_gate": False,
        "thesis_is_independent_from_execution_readiness": True,
    }


def _report_material(report: dict[str, Any]) -> dict[str, Any]:
    return {
        key: report.get(key)
        for key in (
            "schema",
            "surface",
            "event_id",
            "source_sha256",
            "prompt_contract_version",
            "workflow_contract_sha256",
            "policy",
            "report_markdown",
            "structured_report",
        )
    }


def _load_json_object(path: Path, *, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise WorkRuntimeError(f"Invalid {label}: {path}: {exc}") from exc
    if not isinstance(payload, dict):
        raise WorkRuntimeError(f"Invalid {label}: expected JSON object: {path}")
    return payload


def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    _atomic_write_bytes(path, (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))


def _atomic_write_bytes(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    with temporary.open("wb") as handle:
        handle.write(content)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def _safe_name(value: str) -> str:
    return "".join(character if character.isalnum() or character in "._-" else "-" for character in value)[:160]


def _prompt_filename(surface: str) -> str:
    return {
        "kr": "market_kr.md",
        "us": "market_us.md",
        "youtube": "youtube.md",
        "prism": "prism.md",
    }[surface]


def _now(value: datetime | None) -> str:
    return (value or datetime.now().astimezone()).isoformat()


def _coverage_snapshot(packet: dict[str, Any]) -> dict[str, Any]:
    body = packet.get("body") if isinstance(packet.get("body"), dict) else {}
    coverage = body.get("coverage") if isinstance(body.get("coverage"), dict) else {}
    if coverage:
        return {
            key: coverage.get(key)
            for key in (
                "total_unique_events",
                "window_events",
                "transmitted_events",
                "truncated",
                "oldest_occurred_at",
                "newest_occurred_at",
            )
        }
    current = body.get("current") if isinstance(body.get("current"), dict) else {}
    universe = (
        current.get("universe_coverage")
        if isinstance(current.get("universe_coverage"), dict)
        else {}
    )
    return {
        "current_run_id": current.get("run_id"),
        "current_started_at": current.get("started_at"),
        "session_id": body.get("session_id"),
        "source_health": body.get("source_health"),
        "universe_status": universe.get("status"),
        "universe_complete": universe.get("complete"),
        "universe_source_run_id": universe.get("source_run_id"),
        "expected_holding_count": universe.get("expected_holding_count"),
        "missing_holding_count": universe.get("missing_holding_count"),
        "expected_watchlist_count": universe.get("expected_watchlist_count"),
        "missing_watchlist_count": universe.get("missing_watchlist_count"),
        "expected_analysis_count": universe.get("expected_analysis_count"),
        "missing_analysis_count": universe.get("missing_analysis_count"),
        "analysis_total_count": universe.get("analysis_total_count"),
        "analysis_failed_count": universe.get("analysis_failed_count"),
    }


def _source_regressed(packet: dict[str, Any], surface_state: dict[str, Any]) -> bool:
    if not surface_state.get("last_acked_event_id"):
        return False
    body = packet.get("body") if isinstance(packet.get("body"), dict) else {}
    if body.get("source_health") == "MISSING":
        return True
    current = _coverage_snapshot(packet)
    previous = surface_state.get("last_acked_coverage")
    if not isinstance(previous, dict):
        return False
    current_started = _parse_datetime(current.get("current_started_at"))
    previous_started = _parse_datetime(previous.get("current_started_at"))
    if previous_started and (not current_started or current_started < previous_started):
        return True
    current_total = current.get("total_unique_events")
    previous_total = previous.get("total_unique_events")
    if isinstance(previous_total, int) and previous_total > 0 and current_total == 0:
        return True
    current_newest = _parse_datetime(current.get("newest_occurred_at"))
    previous_newest = _parse_datetime(previous.get("newest_occurred_at"))
    return bool(previous_newest and (not current_newest or current_newest < previous_newest))


def _delivery_packet(
    packet: dict[str, Any],
    surface_state: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, str], bool]:
    surface = str(packet.get("surface") or "")
    if surface not in {"youtube", "prism"}:
        return packet, {}, False
    body = packet.get("body") if isinstance(packet.get("body"), dict) else {}
    events = [item for item in (body.get("events") or []) if isinstance(item, dict)]
    current = {
        str(item.get("event_key") or ""): str(item.get("content_sha256") or "")
        for item in events
        if item.get("event_key") and item.get("content_sha256")
    }
    previous = surface_state.get("acked_event_hashes")
    previous = previous if isinstance(previous, dict) else {}
    contract_changed = str(surface_state.get("last_acked_workflow_contract_sha256") or "") != str(
        packet.get("workflow_contract_sha256") or ""
    )
    upstream_changed = str(surface_state.get("last_acked_upstream_source_sha256") or "") != str(
        packet.get("source_sha256") or ""
    )
    new_keys = [key for key, value in current.items() if key not in previous]
    revised_keys = [key for key, value in current.items() if key in previous and str(previous.get(key)) != value]
    unchanged_keys = [key for key, value in current.items() if str(previous.get(key) or "") == value]
    selected = set(current) if contract_changed else (set(new_keys) | set(revised_keys))
    delivery_body = dict(body)
    delivery_body["source_snapshot_sha256"] = packet.get("source_sha256")
    delivery_body["events"] = [item for item in events if str(item.get("event_key") or "") in selected]
    delivery_body["delta"] = {
        "new_events": len(new_keys),
        "revised_events": len(revised_keys),
        "unchanged_events": len(unchanged_keys),
        "delivered_event_keys": [str(item.get("event_key")) for item in delivery_body["events"]],
    }
    merged = dict(previous)
    merged.update(current)
    if len(merged) > 4000:
        keep = list(merged.items())[-4000:]
        merged = dict(keep)
    material_noop = bool(previous) and not selected and not contract_changed and not upstream_changed
    return seal_packet(surface, body=delivery_body), merged, material_noop


def _parse_datetime(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.astimezone()
