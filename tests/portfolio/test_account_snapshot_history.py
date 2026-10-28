"""Account history discovery must stay bounded and honor the account clock."""
from datetime import datetime
import json
from pathlib import Path

import pytest

from tradingagents.portfolio.performance.engine import _load_snapshot_history


AT = datetime.fromisoformat("2026-10-28T23:00:00+09:00")


def write(run, *, as_of="2026-10-28T22:00:00+09:00", profile="us_kis_default", **updates):
    private = run / "portfolio-private"
    private.mkdir(parents=True, exist_ok=True)
    payload = {"snapshot_id": run.name, "as_of": as_of, "account_value_krw": 1000000, **updates}
    (private / "account_snapshot.json").write_text(json.dumps(payload), encoding="utf-8")
    (private / "status.json").write_text(json.dumps({"profile": profile, "snapshot_health": "VALID"}), encoding="utf-8")
    return private


def load(run_dir, **kwargs):
    return _load_snapshot_history(run_dir=run_dir, profile_name="us_kis_default", analysis_as_of=AT, **kwargs)


def test_known_layouts_load_without_entering_ticker_or_evidence_directories(tmp_path, monkeypatch):
    runs = tmp_path / "archive/runs"
    flat, yearly = runs / "legacy-flat", runs / "2026/current"
    write(flat)
    write(yearly)
    write(runs / "2025/previous-year", as_of="2025-12-31T12:00:00+09:00")
    write(yearly / "tickers/AAPL/copied-run")
    write(flat / "evidence/copied-run")
    write(runs / "2026/other-profile", profile="kr_kis_default")
    original = Path.iterdir
    visited = []
    allowed = {runs, runs / "2025", runs / "2026"}

    def bounded(path):
        visited.append(path)
        assert path in allowed, f"Unexpected recursive history traversal: {path}"
        return original(path)

    monkeypatch.setattr(Path, "iterdir", bounded)
    monkeypatch.setattr(Path, "rglob", lambda *a, **kw: pytest.fail("Unbounded history traversal"))
    rows = load(yearly)
    assert {row["snapshot_id"] for row in rows} == {"legacy-flat", "current", "previous-year"}
    assert all(row["snapshot_health"] == "VALID" for row in rows)
    assert set(visited) == allowed


@pytest.mark.parametrize("as_of,expected", [
    ("2026-10-28T22:59:59+09:00", True),
    ("2026-10-28T14:00:00Z", True),
    ("2026-10-28T23:00:01+09:00", False),
    ("2026-10-29T00:00:00+09:00", False),
    (None, False), ("invalid", False), ("2026-10-28T22:00:00", False),
    ("2026-10-28", False),
])
def test_history_rejects_future_missing_invalid_or_unverifiable_clock(tmp_path, as_of, expected):
    run = tmp_path / "runs/2026/current"
    write(run, as_of=as_of)
    rows = load(run)
    assert len(rows) == int(expected)


@pytest.mark.parametrize("where", ["outside-runs", "runs/2026/missing"])
def test_empty_history_returns_no_rows(tmp_path, where):
    assert load(tmp_path / where) == []


@pytest.mark.parametrize("clock", [None, "invalid", "2026-10-28T23:00:00"])
def test_history_requires_explicit_verifiable_analysis_clock(tmp_path, clock):
    with pytest.raises(ValueError, match="analysis_as_of"):
        _load_snapshot_history(run_dir=tmp_path, profile_name="us_kis_default", analysis_as_of=clock)


@pytest.mark.parametrize("bad_file", ["account_snapshot.json", "status.json"])
def test_malformed_history_is_skipped_without_dropping_valid_snapshot(tmp_path, bad_file):
    run = tmp_path / "runs/2026/current"
    write(run)
    broken = write(tmp_path / "runs/2026/broken")
    (broken / bad_file).write_text("invalid", encoding="utf-8")
    assert [row["snapshot_id"] for row in load(run)] == ["current"]


def test_legacy_snapshot_without_status_keeps_profile_and_health_behavior(tmp_path):
    run = tmp_path / "runs/legacy"
    private = write(run, snapshot_health="WATCHLIST_ONLY")
    (private / "status.json").unlink()
    assert load(run)[0]["snapshot_health"] == "WATCHLIST_ONLY"
