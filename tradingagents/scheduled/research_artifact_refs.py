"""Verified, immutable research bytes shared by lightweight overlay runs.

This is storage deduplication, never new research or order authorization. Blobs
live outside the run-retention tree. There is deliberately no automatic GC.
Every consumer verifies the saved manifest, original analysis clocks and bytes;
the original run may have been retired without invalidating its saved evidence.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import date, datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import tempfile

from tradingagents.atomic_io import interprocess_file_lock

SCHEMA = "tradingagents.immutable-research-artifact/v1"
KEYS = frozenset({"report_markdown", "final_state_json", "graph_log_json"})
_MAX_BYTES = 64 * 1024 * 1024
_SHA = re.compile(r"[0-9a-f]{64}")
_OVERLAY_ANALYSIS_FIELDS = frozenset({"intraday_snapshot_attempts", "latest_intraday_snapshot_attempt",
                                     "intraday_snapshot_latest_attempt"})


def _instant(value):
    if isinstance(value, str):
        value = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("Research reference requires an aware timestamp")
    return value.astimezone(timezone.utc)


def _day(value):
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise ValueError("Research reference requires an original date")
    return date.fromisoformat(value)


def _json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("Duplicate research evidence key")
            result[key] = value
        return result

    def constant(_value):
        raise ValueError("Non-finite research evidence")

    result = json.loads(raw, object_pairs_hook=pairs, parse_constant=constant)
    if not isinstance(result, dict):
        raise ValueError("Research evidence must be an object")
    return result


def _safe(root, relative, *, must_exist=True):
    if (not isinstance(relative, str) or not relative or "\\" in relative or ":" in relative
            or PurePosixPath(relative).is_absolute() or ".." in PurePosixPath(relative).parts):
        raise ValueError("Research evidence path must remain relative")
    root = Path(root).absolute()
    path = root.joinpath(*PurePosixPath(relative).parts)
    for part in [*reversed(path.parents), path]:
        if part.exists() or part.is_symlink():
            if part.is_symlink() or getattr(part.lstat(), "st_file_attributes", 0) & 0x400:
                raise ValueError("Research evidence reparse path is forbidden")
    if not path.resolve().is_relative_to(root.resolve()) or (must_exist and not path.is_file()):
        raise ValueError("Research evidence is missing or outside its boundary")
    return path


def _read(path):
    before = path.stat()
    if not 0 < before.st_size <= _MAX_BYTES:
        raise ValueError("Research evidence is empty or exceeds its bound")
    with path.open("rb") as stream:
        raw = stream.read(_MAX_BYTES + 1)
    after = path.stat()
    if (len(raw) != before.st_size or
            (before.st_size, before.st_mtime_ns, before.st_ino) !=
            (after.st_size, after.st_mtime_ns, after.st_ino)):
        raise ValueError("Research evidence changed while being read")
    return raw


class ResearchArtifactStore:
    """One operation's bounded verification cache; no global/stale cache."""

    def __init__(self, archive_dir, *, now=None):
        # A configured archive root may itself be an operator-managed junction.
        # Resolve that trusted boundary once; reject reparse paths below it.
        self.configured_archive = Path(archive_dir).absolute()
        self.archive = self.configured_archive.resolve()
        self.root = self.archive / "research-snapshots"
        self.now = min(_instant(now) if now is not None else datetime.now(timezone.utc),
                       datetime.now(timezone.utc))
        self._manifests = {}
        self._saved_manifests = {}

    @classmethod
    def from_run_dir(cls, run_dir, *, now):
        run_dir = Path(run_dir).absolute()
        if run_dir.parent.parent.name != "runs" or not re.fullmatch(r"\d{4}", run_dir.parent.name):
            raise ValueError("Research reference consumer is outside the archive run tree")
        return cls(run_dir.parent.parent.parent, now=_instant(now))

    def _blob(self, digest):
        if not isinstance(digest, str) or not _SHA.fullmatch(digest):
            raise ValueError("Invalid research blob digest")
        raw = _read(_safe(self.root, f"sha256/{digest[:2]}/{digest}"))
        if hashlib.sha256(raw).hexdigest() != digest:
            raise ValueError("Immutable research blob changed")
        return raw

    def _publish(self, raw):
        digest = hashlib.sha256(raw).hexdigest()
        relative = f"sha256/{digest[:2]}/{digest}"
        target = _safe(self.root, relative, must_exist=False)
        target.parent.mkdir(parents=True, exist_ok=True)
        lock = _safe(self.root, ".publication.lock", must_exist=False)
        with interprocess_file_lock(lock):
            target = _safe(self.root, relative, must_exist=False)
            if target.exists():
                if _read(target) != raw:
                    raise ValueError("Existing immutable research blob differs")
            else:
                fd, name = tempfile.mkstemp(prefix=".publish-", dir=target.parent)
                temporary = Path(name)
                try:
                    with os.fdopen(fd, "wb") as stream:
                        stream.write(raw)
                        stream.flush()
                        os.fsync(stream.fileno())
                    os.chmod(temporary, 0o600)
                    # All writers hold the same lock. Never replace an existing
                    # destination, even if its bytes look damaged or incomplete.
                    if target.exists():
                        raise ValueError("Research blob appeared during publication")
                    temporary.rename(target)
                finally:
                    temporary.unlink(missing_ok=True)
        return digest

    def _validate_manifest(self, manifest, run_id):
        if (manifest.get("run_id") != run_id or not isinstance(run_id, str)
                or not re.fullmatch(r"[A-Za-z0-9_.-]+", run_id)
                or manifest.get("status") not in {"success", "completed", "complete", "partial_failure", "failed"}):
            raise ValueError("Research reference source is not an identified terminal run")
        start, finish = _instant(manifest.get("started_at")), _instant(manifest.get("finished_at"))
        if not start <= finish <= self.now:
            raise ValueError("Research source clocks are reversed or future-dated")
        settings = manifest.get("settings") or {}
        market = settings.get("market_scope") or settings.get("market")
        if market not in {"KR", "US"}:
            raise ValueError("Research source market is missing or invalid")
        return market

    @staticmethod
    def _row(manifest, ticker):
        if not isinstance(ticker, str) or not re.fullmatch(r"[A-Z0-9][A-Z0-9.-]*", ticker):
            raise ValueError("Invalid research ticker")
        rows = manifest.get("tickers")
        if not isinstance(rows, list):
            raise ValueError("Missing research cohort")
        rows = [row for row in rows if isinstance(row, dict) and row.get("ticker") == ticker]
        if len(rows) != 1 or rows[0].get("status") != "success" or not isinstance(rows[0].get("artifacts"), dict):
            raise ValueError("Research reference requires one successful owner row")
        return rows[0]

    def _run_relative(self, source_run_dir):
        source_run_dir = Path(source_run_dir).absolute()
        boundary = (self.configured_archive if source_run_dir.is_relative_to(self.configured_archive)
                    else self.archive)
        relative = source_run_dir.relative_to(boundary).as_posix()
        if not re.fullmatch(r"runs/\d{4}/[A-Za-z0-9_.-]+", relative):
            raise ValueError("Invalid research source run path")
        return relative

    def _source(self, source_run_dir):
        relative = self._run_relative(source_run_dir)
        source_run_dir = self.archive / relative
        if relative not in self._manifests:
            raw = _read(_safe(self.archive, f"{relative}/run.json"))
            manifest = _json(raw)
            self._validate_manifest(manifest, source_run_dir.name)
            if source_run_dir.parent.name != str(manifest["started_at"])[:4]:
                raise ValueError("Research source archive year differs")
            self._manifests[relative] = raw, manifest
        raw, manifest = self._manifests[relative]
        return raw, manifest, self.archive / relative

    def _proof(self, manifest, row, analysis):
        start, finish = _instant(analysis.get("started_at")), _instant(analysis.get("finished_at"))
        row_start, row_finish = _instant(row.get("started_at")), _instant(row.get("finished_at"))
        if (analysis.get("ticker") != row["ticker"] or analysis.get("status") != "success"
                or not start <= finish <= _instant(manifest["finished_at"])
                or not row_start <= row_finish <= _instant(manifest["finished_at"])):
            raise ValueError("Original research identity or chronology is invalid")
        if any(analysis.get(key) != row.get(key) for key in ("analysis_date", "trade_date")):
            raise ValueError("Original research dates differ from the owner row")
        if not _day(analysis.get("trade_date")) <= _day(analysis.get("analysis_date")) <= start.date():
            # Analysis dates are market-local; a positive offset may be one day
            # ahead of UTC while still matching the original aware start date.
            local_day = datetime.fromisoformat(analysis["started_at"].replace("Z", "+00:00")).date()
            if not _day(analysis.get("trade_date")) <= _day(analysis.get("analysis_date")) <= local_day:
                raise ValueError("Original research dates are future-dated")
        return {key: analysis[key] for key in ("started_at", "finished_at", "analysis_date", "trade_date")}

    def make(self, source_run_dir, source_row, key):
        if key not in KEYS:
            raise ValueError("Artifact is outside immutable research allowlist")
        manifest_raw, manifest, source_run_dir = self._source(source_run_dir)
        row = self._row(manifest, source_row.get("ticker"))
        value = row["artifacts"].get(key)
        if (source_row.get("artifacts", {}).get(key) != value
                or source_row.get("artifacts", {}).get("analysis_json") != row["artifacts"].get("analysis_json")
                or any(source_row.get(field) != row.get(field) for field in ("trade_date", "analysis_date"))):
            raise ValueError("Selected artifact differs from archived owner row")
        if isinstance(value, dict):
            self.read_owned(value, key=key, run_dir=source_run_dir, row=row,
                            market=self._validate_manifest(manifest, manifest["run_id"]))
            if _instant(value["source_finished_at"]) > _instant(manifest["started_at"]):
                raise ValueError("Referenced source was unavailable when overlay started")
            return deepcopy(value)
        artifact = _safe(source_run_dir, value)
        analysis_relative = row["artifacts"].get("analysis_json")
        analysis_raw = _read(_safe(source_run_dir, analysis_relative))
        analysis = _json(analysis_raw)
        proof = self._proof(manifest, row, analysis)
        for relative in (value, analysis_relative):
            if not PurePosixPath(relative).is_relative_to(PurePosixPath("tickers") / row["ticker"]):
                raise ValueError("Research artifact escaped its owner ticker")
        raw = _read(artifact)
        # Validate everything before publishing any immutable snapshot.
        reference = {"schema": SCHEMA, "artifact_key": key, "ticker": row["ticker"],
                "market": self._validate_manifest(manifest, manifest["run_id"]),
                "source_run_id": manifest["run_id"], "source_started_at": manifest["started_at"],
                "source_finished_at": manifest["finished_at"], "source_manifest_sha256": self._publish(manifest_raw),
                "artifact_path": value, "artifact_sha256": self._publish(raw), "artifact_size_bytes": len(raw),
                "analysis_path": analysis_relative, "analysis_sha256": self._publish(analysis_raw),
                "research": proof}
        reference["snapshot_sha256"] = self._publish(json.dumps(
            reference, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8"))
        return reference

    def owner_analysis_path(self, run_dir, row):
        relative = (row.get("artifacts") or {}).get("analysis_json")
        if (not isinstance(relative, str) or
                not PurePosixPath(relative).is_relative_to(PurePosixPath("tickers") / str(row.get("ticker")))):
            raise ValueError("Consuming analysis escaped its ticker")
        return _safe(self.archive, f"{self._run_relative(run_dir)}/{relative}")

    def read_owned(self, reference, *, key, run_dir, row, market, analysis=None):
        """Bind saved original research to this consumer's current local owner."""
        if (row.get("status") != "success" or not isinstance(row.get("artifacts"), dict)
                or row["artifacts"].get(key) != reference):
            raise ValueError("Research reference differs from the consuming owner row")
        if market not in {"KR", "US"}:
            raise ValueError("Consuming research market is missing or invalid")
        analysis_path = self.owner_analysis_path(run_dir, row)
        if analysis is None:
            analysis = _json(_read(analysis_path))
        proof = reference.get("research") if isinstance(reference, dict) else None
        if (not isinstance(proof, dict) or not isinstance(analysis, dict)
                or analysis.get("ticker") != row.get("ticker") or analysis.get("status") != "success"
                or any(analysis.get(field) != proof.get(field)
                       for field in ("started_at", "finished_at", "analysis_date", "trade_date"))
                or any(row.get(field) != proof.get(field) for field in ("analysis_date", "trade_date"))):
            raise ValueError("Research reference differs from the consuming original clocks")
        original = _json(self._blob(reference.get("analysis_sha256")))
        def thesis(value):
            return json.dumps({name: item for name, item in value.items() if name not in _OVERLAY_ANALYSIS_FIELDS},
                              sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
        if (thesis(analysis) != thesis(original)
                or ("decision" in row and row["decision"] != analysis.get("decision"))):
            raise ValueError("Research reference differs from the consuming original thesis")
        return self.read(reference, key=key, ticker=row.get("ticker"), market=market)

    def read(self, reference, *, key, ticker, market=None):
        if (not isinstance(reference, dict) or reference.get("schema") != SCHEMA or key not in KEYS
                or reference.get("artifact_key") != key or reference.get("ticker") != ticker):
            raise ValueError("Malformed or mismatched immutable research reference")
        if _json(self._blob(reference.get("snapshot_sha256"))) != {
                name: value for name, value in reference.items() if name != "snapshot_sha256"}:
            raise ValueError("Immutable research snapshot receipt differs")
        manifest_digest = reference.get("source_manifest_sha256")
        if manifest_digest not in self._saved_manifests:
            self._saved_manifests[manifest_digest] = _json(self._blob(manifest_digest))
        manifest = self._saved_manifests[manifest_digest]
        source_market = self._validate_manifest(manifest, reference.get("source_run_id"))
        if reference.get("market") != source_market or (market is not None and market != source_market):
            raise ValueError("Research reference market differs")
        if any(reference.get(f"source_{field}") != manifest[field] for field in ("started_at", "finished_at")):
            raise ValueError("Research reference source clocks differ")
        row = self._row(manifest, ticker)
        # Saved evidence must point to the original local files, never another
        # reference. This keeps the anchor fixed and rejects reference cycles.
        for field, artifact_key in (("artifact_path", key), ("analysis_path", "analysis_json")):
            relative = reference.get(field)
            if (not isinstance(relative, str) or row["artifacts"].get(artifact_key) != relative
                    or "\\" in relative or ":" in relative or ".." in PurePosixPath(relative).parts
                    or not PurePosixPath(relative).is_relative_to(PurePosixPath("tickers") / ticker)):
                raise ValueError("Research reference original owner path differs")
        analysis = _json(self._blob(reference.get("analysis_sha256")))
        if self._proof(manifest, row, analysis) != reference.get("research"):
            raise ValueError("Research reference original clocks differ")
        raw = self._blob(reference.get("artifact_sha256"))
        if type(reference.get("artifact_size_bytes")) is not int or len(raw) != reference["artifact_size_bytes"]:
            raise ValueError("Research reference original size differs")
        return raw
