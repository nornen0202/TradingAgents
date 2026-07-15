from __future__ import annotations

import json
import os
from contextlib import contextmanager
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Iterator

from .packet import WORK_SCHEMA, WORK_STATE_SCHEMA, build_surface_packet, canonical_json, seal_packet


class WorkRuntimeError(RuntimeError):
    pass


class WorkRuntime:
    def __init__(self, root: Path) -> None:
        self.root = Path(root)
        self.state_path = self.root / "state" / "state.json"
        self.ledger_path = self.root / "ledger" / "events.jsonl"
        self.outbox_dir = self.root / "outbox"
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
            acknowledged_at = _now(now)
            surface_state.update(
                {
                    "last_acked_event_id": event_id,
                    "last_acked_source_sha256": surface_state.get("pending_source_sha256"),
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
                    "pending_event_id": None,
                    "pending_source_sha256": None,
                    "pending_packet_path": None,
                    "pending_coverage": None,
                    "pending_event_hashes": None,
                    "pending_workflow_contract_sha256": None,
                    "pending_upstream_source_sha256": None,
                }
            )
            state["revision"] = int(state.get("revision") or 0) + 1
            self._append_ledger(
                {
                    "at": acknowledged_at,
                    "surface": key,
                    "event": "acknowledged",
                    "event_id": event_id,
                    "status": status,
                    "state_revision": state["revision"],
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
            }

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
        state_revision: int | None = None,
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
            try:
                state = self._load_state()
            except WorkRuntimeError:
                state = {"schema": WORK_STATE_SCHEMA, "revision": 0, "surfaces": {}}
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
                    "pending_event_id": None,
                    "pending_source_sha256": None,
                    "pending_packet_path": None,
                    "pending_coverage": None,
                    "pending_event_hashes": None,
                    "pending_workflow_contract_sha256": None,
                    "pending_upstream_source_sha256": None,
                }
            )
            requested_revision = max(0, int(state_revision or 0))
            state["revision"] = max(int(state.get("revision") or 0) + 1, requested_revision)
            self._append_ledger(
                {
                    "at": recovered_at,
                    "surface": key,
                    "event": "recovered_visible_receipt",
                    "event_id": event_id,
                    "source_sha256": source_sha256,
                    "state_revision": state["revision"],
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
    body = packet.get("body") if isinstance(packet.get("body"), dict) else {}
    if body.get("kind") in {"youtube", "prism"} and body.get("execution_eligible") is not False:
        raise WorkRuntimeError("Advisory source packet must set execution_eligible=false")
    size = len(json.dumps(packet, ensure_ascii=False, indent=2))
    if size > max_chars:
        raise WorkRuntimeError(f"Work packet is too large: {size} chars > {max_chars}")


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
