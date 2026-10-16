"""Point-in-time event board with explicit announcement and correction clocks."""
from __future__ import annotations

from collections import defaultdict
import hashlib
from pathlib import Path
import sqlite3
import threading
from typing import Any, Iterable

from .market_policy import TimestampEnvelope, aware_datetime, source_use_policy

_CAPTURE_LOCK = threading.Lock()
_CAPTURED_DISCLOSURES: list[dict[str, Any]] = []
_FIRST_SEEN_DB: Path | None = None


class EventFirstSeenStore:
    """Durable local detection clock, never represented as publication time."""

    def __init__(self, path: str | Path):
        self.path = Path(path)

    def observe(self, event_key: str, *, detected_at: Any, is_amended: bool = False) -> str:
        detected = aware_datetime(detected_at)
        if detected is None or not event_key:
            raise ValueError("A stable event identity and aware detection time are required")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.path, timeout=30) as connection:
            connection.execute("CREATE TABLE IF NOT EXISTS event_first_seen (event_key TEXT PRIMARY KEY, first_seen_at TEXT NOT NULL, is_amended INTEGER NOT NULL)")
            connection.execute("INSERT OR IGNORE INTO event_first_seen VALUES (?, ?, ?)",
                               (event_key, detected.isoformat(), int(is_amended)))
            row = connection.execute("SELECT first_seen_at FROM event_first_seen WHERE event_key = ?", (event_key,)).fetchone()
        return row[0]


def reset_event_capture(*, first_seen_db: str | Path | None = None) -> None:
    global _FIRST_SEEN_DB
    with _CAPTURE_LOCK:
        _CAPTURED_DISCLOSURES.clear()
        _FIRST_SEEN_DB = Path(first_seen_db) if first_seen_db is not None else None


def snapshot_event_records(ticker: str | None = None) -> list[dict[str, Any]]:
    with _CAPTURE_LOCK:
        return [dict(row) for row in _CAPTURED_DISCLOSURES
                if ticker is None or str(row.get("ticker") or "").upper() == ticker.upper()]


def capture_disclosures(items: Iterable[Any], *, observed_at: Any) -> None:
    records = disclosure_event_records(items, observed_at=observed_at, first_seen_db=_FIRST_SEEN_DB)
    with _CAPTURE_LOCK:
        _CAPTURED_DISCLOSURES.extend(records)


def imported_event_records(payloads: Iterable[dict[str, Any]], *, ticker: str) -> list[dict[str, Any]]:
    """Preserve explicitly dated imported events; never parse free-text dates."""
    records = []
    for payload in payloads:
        if not isinstance(payload, dict):
            continue
        containers = [payload]
        containers += [payload[key] for key in ("earnings_event_pack", "earnings", "payload") if isinstance(payload.get(key), dict)]
        for container in containers:
            for record in container.get("event_records") or []:
                if isinstance(record, dict):
                    records.append({"ticker": ticker, **record})
    return records


def disclosure_event_records(items: Iterable[Any], *, observed_at: Any,
                              first_seen_db: str | Path | None = None) -> list[dict[str, Any]]:
    """Map structured disclosures using actual aware publication clocks only.

    OpenDART's day-only receipt timestamp intentionally remains unverifiable.
    SEC acceptance timestamps can enter once both publication and our local
    observation are known. Content revisions need explicit event lineage from
    the provider rather than a title-based amendment guess.
    """
    observed = aware_datetime(observed_at)
    if observed is None:
        raise ValueError("observed_at must be timezone-aware")
    records = []
    for item in items:
        def get(key):
            return item.get(key) if isinstance(item, dict) else getattr(item, key, None)
        identity = str(get("url") or "")
        if not identity:
            continue
        vendor = str(get("raw_vendor") or "").strip().lower()
        published = aware_datetime(get("published_at"))
        if vendor == "opendart" and not (
            str(get("precision") or "").strip().lower() == "timestamp"
            or get("exact_event_time_known") is True
        ):
            # list.json supplies a receipt DAY. Its legacy DisclosureItem API
            # represents that day as aware KST midnight; timezone awareness
            # does not turn that compatibility value into an actual release
            # time. Only a future explicitly precise adapter can opt in.
            published = None
        version = hashlib.sha256(identity.encode("utf-8")).hexdigest()[:24]
        title = str(get("title") or "")
        is_amended = any(marker in title.lower() for marker in ("정정", "amend", "10-k/a", "10-q/a", "8-k/a"))
        first_seen = EventFirstSeenStore(first_seen_db).observe(identity, detected_at=observed, is_amended=is_amended) if first_seen_db else None
        detected_only = published is None and vendor == "opendart" and first_seen is not None
        records.append({"event_id": version, "version_id": version, "ticker": get("symbol"),
                        "event_type": "disclosure", "title": get("title"), "url": identity,
                        "provider": get("raw_vendor"), "status": "detected" if detected_only else "published",
                        "published_at": published.isoformat() if published else None,
                        "known_at": first_seen if detected_only else published.isoformat() if published else None,
                        "first_seen_at": first_seen, "exact_event_time_known": published is not None,
                        "is_amended": is_amended,
                        "observed_at": observed.isoformat()})
    return records


def build_event_timeline(records: Iterable[dict[str, Any]], *, analysis_as_of: Any,
                         ticker: str | None = None) -> dict[str, Any]:
    """Return only versions locally observed and publicly knowable at ``as_of``.

    ``scheduled_at`` may be in the future. ``published_at`` is an actual
    disclosure clock and cannot be future-dated or substituted with a fiscal
    period end. A schedule without an actual publication must use
    ``status='scheduled'``. Unknown-time disclosures stay out of the evidence.
    Corrections require an available predecessor; we never rewrite its history.
    """
    as_of = aware_datetime(analysis_as_of)
    if as_of is None:
        raise ValueError("analysis_as_of must be a timezone-aware timestamp")
    rejected: list[dict[str, Any]] = []
    versions: dict[str, dict[str, Any]] = {}
    conflicts: set[str] = set()
    for index, raw in enumerate(records):
        if not isinstance(raw, dict):
            rejected.append({"index": index, "reason": "INVALID_EVENT"})
            continue
        if ticker and str(raw.get("ticker") or "").upper() != ticker.upper():
            continue
        raw = dict(raw)
        if "published_at" not in raw and "event_time" in raw:
            raw["published_at"] = raw["event_time"]
        if "observed_at" not in raw and "ingested_at" in raw:
            raw["observed_at"] = raw["ingested_at"]
        event_id, version_id = str(raw.get("event_id") or ""), str(raw.get("version_id") or "")
        reason = None
        status = str(raw.get("status") or "published").lower()
        clocks = {key: aware_datetime(raw.get(key)) for key in
                  ("scheduled_at", "published_at", "observed_at", "known_at")}
        first_seen = aware_datetime(raw.get("first_seen_at"))
        if any(value > as_of for key, value in clocks.items() if key != "scheduled_at" and value is not None) or (first_seen is not None and first_seen > as_of):
            # Neither event identities nor exclusion counts from a later
            # observation may change an earlier replay snapshot.
            continue
        alias_conflict = False
        envelope = raw.get("timestamp_envelope")
        if envelope is not None and not isinstance(envelope, dict):
            alias_conflict = True
        for aliases in (raw, envelope if isinstance(envelope, dict) else {}):
            for alias, key in (("event_time", "published_at"), ("published_at", "published_at"),
                               ("ingested_at", "observed_at"), ("observed_at", "observed_at")):
                if alias in aliases and (aware_datetime(aliases[alias]) != clocks[key]
                        or (aliases[alias] is not None and aware_datetime(aliases[alias]) is None)):
                    alias_conflict = True
            if aliases.get("evaluated_at") is not None and aware_datetime(aliases["evaluated_at"]) is None:
                alias_conflict = True
        if isinstance(envelope, dict) and raw.get("evaluated_at") is not None and envelope.get("evaluated_at") is not None:
            alias_conflict |= aware_datetime(raw["evaluated_at"]) != aware_datetime(envelope["evaluated_at"])
        if not event_id or not version_id:
            reason = "EVENT_IDENTITY_MISSING"
        elif alias_conflict:
            reason = "TIMESTAMP_ALIAS_CONFLICT"
        elif status not in {"scheduled", "published", "corrected", "cancelled", "detected"}:
            reason = "EVENT_STATUS_INVALID"
        elif clocks["observed_at"] is None or clocks["known_at"] is None:
            reason = "AVAILABILITY_CLOCK_MISSING_OR_INVALID"
        elif raw.get("first_seen_at") is not None and (first_seen is None
                or first_seen > clocks["observed_at"] or first_seen > as_of
                or (clocks["published_at"] is not None and first_seen < clocks["published_at"])):
            reason = "FIRST_SEEN_CLOCK_INVALID"
        elif any(clocks[key] is None for key in ("scheduled_at", "published_at") if raw.get(key) is not None):
            reason = "EVENT_CLOCK_INVALID"
        elif status == "scheduled" and (clocks["scheduled_at"] is None or clocks["published_at"] is not None):
            reason = "SCHEDULE_CLOCK_INVALID"
        elif status == "detected" and (aware_datetime(raw.get("first_seen_at")) is None
                or aware_datetime(raw.get("first_seen_at")) != clocks["known_at"]
                or raw.get("exact_event_time_known") is not False or raw.get("published_at") is not None):
            reason = "DETECTION_CLOCK_UNVERIFIED"
        elif status not in {"scheduled", "detected"} and clocks["published_at"] is None:
            reason = "DISCLOSURE_TIME_UNVERIFIED"
        elif clocks["known_at"] > clocks["observed_at"]:
            reason = "EVENT_CLOCK_ORDER_INVALID"
        elif clocks["published_at"] and clocks["published_at"] > clocks["known_at"]:
            reason = "EVENT_CLOCK_ORDER_INVALID"
        elif status == "corrected" and not raw.get("supersedes_version_id"):
            reason = "CORRECTION_PREDECESSOR_MISSING"
        elif raw.get("provider") and not source_use_policy(raw["provider"], entitlement=raw.get("entitlement"))["allowed"]:
            reason = "EVENT_SOURCE_NOT_ENTITLED"
        if reason:
            rejected.append({"index": index, "event_id": event_id, "version_id": version_id, "reason": reason})
            continue
        # Whitelist source evidence: unvalidated alternative clocks/payloads
        # cannot accidentally leak later versions into the chart or replay.
        item = {key: raw.get(key) for key in ("event_id", "version_id", "ticker", "event_type", "title", "url",
                "provider", "supersedes_version_id", "fiscal_period_end", "market_timezone", "first_seen_at",
                "exact_event_time_known", "is_amended") if raw.get(key) is not None}
        item.update(status=status, **{key: value.isoformat() if value else None for key, value in clocks.items()})
        item["is_amended"] = raw.get("is_amended") is True or status == "corrected"
        item["available_at"] = max(clocks["known_at"], clocks["observed_at"]).isoformat()
        item["timestamp_envelope"] = TimestampEnvelope.from_mapping(item, evaluated_at=as_of.isoformat()).to_dict()
        item.update({key: item["timestamp_envelope"][key] for key in ("event_time", "ingested_at", "evaluated_at")})
        if version_id in versions and versions[version_id] != item:
            conflicts.add(version_id)
            rejected.append({"index": index, "event_id": event_id, "version_id": version_id, "reason": "CONFLICTING_EVENT_VERSION"})
        else:
            versions[version_id] = item
    for version_id in conflicts:
        versions.pop(version_id, None)
    accepted: dict[str, dict[str, Any]] = {}
    ordered = sorted(versions.values(), key=lambda row: (row["available_at"], row["version_id"]))
    # Compare aware datetime instants rather than lexical timezone offsets.
    ordered.sort(key=lambda row: (aware_datetime(row["available_at"]), row["version_id"]))
    for item in ordered:
        predecessor = item.get("supersedes_version_id")
        if predecessor:
            previous = accepted.get(str(predecessor))
            if (previous is None or previous["event_id"] != item["event_id"]
                    or aware_datetime(previous["known_at"]) >= aware_datetime(item["known_at"])):
                rejected.append({"event_id": item["event_id"], "version_id": item["version_id"], "reason": "CORRECTION_LINEAGE_UNVERIFIED"})
                continue
        accepted[item["version_id"]] = item
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in accepted.values():
        groups[item["event_id"]].append(item)
    events = []
    for event_id in sorted(groups):
        history = groups[event_id]
        superseded = {item.get("supersedes_version_id") for item in history}
        leaves = [item for item in history if item["version_id"] not in superseded]
        if len(leaves) != 1:
            rejected.append({"event_id": event_id, "reason": "EVENT_VERSION_LINEAGE_AMBIGUOUS"})
            continue
        events.append({**leaves[0], "versions": history})
    return {"schema": "tradingagents.event-timeline/v1", "analysis_as_of": as_of.isoformat(),
            "events": events, "rejected": rejected,
            "publication_does_not_refresh_inputs": True}
