from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import os
import shutil
import subprocess
from types import SimpleNamespace

import pytest

from tradingagents.scheduled.research_artifact_refs import KEYS, ResearchArtifactStore

NOW = datetime(2026, 5, 30, 12, tzinfo=timezone.utc)


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value), encoding="utf-8")


@pytest.fixture
def evidence(tmp_path):
    archive = tmp_path / "archive"
    source = archive / "runs/2026/20260530T090000_full"
    row = {"ticker": "AAPL", "status": "success", "decision": "WAIT",
           "started_at": "2026-05-30T09:01:00+00:00", "finished_at": "2026-05-30T09:02:00+00:00",
           "analysis_date": "2026-05-30", "trade_date": "2026-05-29",
           "artifacts": {"analysis_json": "tickers/AAPL/analysis.json",
                         "execution_contract_json": "tickers/AAPL/execution_contract.json",
                         "report_markdown": "tickers/AAPL/report/report.md",
                         "final_state_json": "tickers/AAPL/final_state.json",
                         "graph_log_json": "tickers/AAPL/graph.json"}}
    manifest = {"run_id": source.name, "status": "success",
                "started_at": "2026-05-30T09:00:00+00:00", "finished_at": "2026-05-30T09:03:00+00:00",
                "settings": {"market": "US", "run_mode": "full"}, "tickers": [row]}
    analysis = {k: row[k] for k in ("ticker", "status", "decision", "started_at", "finished_at", "analysis_date", "trade_date")}
    write(source / row["artifacts"]["analysis_json"], analysis)
    write(source / row["artifacts"]["execution_contract_json"], {})
    write(source / row["artifacts"]["final_state_json"], {"final_trade_decision": "WAIT"})
    write(source / row["artifacts"]["graph_log_json"], {"messages": ["original research"]})
    report = source / row["artifacts"]["report_markdown"]
    report.parent.mkdir(parents=True)
    report.write_text("# Original immutable report\n", encoding="utf-8")
    write(source / "run.json", manifest)
    return archive, source, manifest, row


def config(archive, *, lightweight=True, mode="overlay_only"):
    return SimpleNamespace(storage=SimpleNamespace(archive_dir=archive),
                           run=SimpleNamespace(market="US", timezone="UTC", run_mode=mode),
                           execution=SimpleNamespace(execution_lightweight_refresh=lightweight,
                                                     execution_max_data_age_seconds=120))


def bootstrap(evidence, monkeypatch, *, lightweight=True, mode="overlay_only", label="overlay"):
    from tradingagents.scheduled import runner
    archive, _, manifest, _ = evidence
    monkeypatch.setattr(runner, "_copy_latest_microstructure_artifacts", lambda **_: {})
    monkeypatch.setattr(runner, "_execution_checkpoint_timezone", lambda _: "UTC")
    destination = archive / "runs/2026" / label
    rows, _ = runner._bootstrap_overlay_inputs_from_latest_run(
        config=config(archive, lightweight=lightweight, mode=mode), run_dir=destination,
        tickers=["AAPL"], source_manifest=manifest)
    return destination, rows[0]


def publish_overlay(directory, row):
    manifest = {"run_id": directory.name, "status": "success", "started_at": row["started_at"],
                "finished_at": row["finished_at"], "settings": {"market": "US", "run_mode": "overlay_only"},
                "tickers": [row], "_run_dir": str(directory)}
    write(directory / "run.json", manifest)
    return manifest


@pytest.mark.parametrize("key", sorted(KEYS))
def test_snapshot_verifies_exact_original_and_immutable_publication(evidence, key):
    archive, source, _, row = evidence
    original = (source / row["artifacts"][key]).read_bytes()
    store = ResearchArtifactStore(archive, now=NOW)
    ref = store.make(source, row, key)
    assert store.read(ref, key=key, ticker="AAPL", market="US") == original
    assert ref["artifact_sha256"] == hashlib.sha256(original).hexdigest()
    blobs = {p: (p.stat().st_mtime_ns, p.read_bytes()) for p in (archive / "research-snapshots/sha256").glob("*/*")}
    assert ResearchArtifactStore(archive, now=NOW).make(source, row, key) == ref
    assert blobs == {p: (p.stat().st_mtime_ns, p.read_bytes()) for p in blobs}


def test_deleted_source_does_not_break_chain_consumers_or_materialization(evidence, tmp_path, monkeypatch):
    from tradingagents.portfolio.semantic_judge import _load_context_by_ticker, build_semantic_verdicts
    from tradingagents.scheduled.config import SiteSettings
    from tradingagents.scheduled.site import _render_ticker_page
    archive, source, _, original_row = evidence
    original = {key: (source / original_row["artifacts"][key]).read_bytes() for key in KEYS}
    destination, row = bootstrap(evidence, monkeypatch)
    refs = {key: deepcopy(row["artifacts"][key]) for key in KEYS}
    for key in KEYS:
        assert not (destination / original_row["artifacts"][key]).exists()
    manifest = publish_overlay(destination, row)
    saved_bytes = sum(p.stat().st_size for p in (archive / "research-snapshots/sha256").glob("*/*"))
    assert source.is_relative_to(tmp_path)
    shutil.rmtree(source)
    store = ResearchArtifactStore(archive)
    for key in KEYS:
        assert store.read(refs[key], key=key, ticker="AAPL") == original[key]
    contexts = _load_context_by_ticker(destination, manifest)
    assert contexts["AAPL"]["final_state"]["final_trade_decision"] == "WAIT"
    monkeypatch.setattr("tradingagents.portfolio.semantic_judge._create_semantic_llm",
                        lambda *_: pytest.fail("disabled semantic must not create a model"))
    assert build_semantic_verdicts(candidates=[], run_dir=destination, manifest=manifest,
                                  llm_settings=None, portfolio_settings=SimpleNamespace(semantic_judge_enabled=False)) == ([], [], [])
    page = _render_ticker_page(manifest, row, SiteSettings())
    assert "Original immutable report" in page
    second, next_row = bootstrap((archive, destination, manifest, row), monkeypatch, label="next_overlay")
    assert {key: next_row["artifacts"][key] for key in KEYS} == refs
    assert sum(p.stat().st_size for p in (archive / "research-snapshots/sha256").glob("*/*")) == saved_bytes
    next_manifest = publish_overlay(second, next_row)
    third, local_row = bootstrap((archive, second, next_manifest, next_row), monkeypatch,
                                 lightweight=False, label="ordinary_overlay")
    for key in KEYS:
        assert isinstance(local_row["artifacts"][key], str)
        assert (third / local_row["artifacts"][key]).read_bytes() == original[key]
    assert (third / local_row["artifacts"]["analysis_json"]).read_bytes() == (destination / row["artifacts"]["analysis_json"]).read_bytes()


@pytest.mark.parametrize("lightweight,mode", [(False, "overlay_only"), (True, "full")])
def test_nonlightweight_and_full_preserve_existing_local_copy(evidence, monkeypatch, lightweight, mode):
    archive, source, _, original_row = evidence
    destination, row = bootstrap(evidence, monkeypatch, lightweight=lightweight, mode=mode)
    for key in KEYS:
        assert isinstance(row["artifacts"][key], str)
        assert (destination / row["artifacts"][key]).read_bytes() == (source / original_row["artifacts"][key]).read_bytes()
    assert not (archive / "research-snapshots").exists()


def test_site_reuses_verified_manifest_only_within_each_run(evidence, tmp_path, monkeypatch):
    from tradingagents.scheduled import site
    from tradingagents.scheduled.config import SiteSettings
    archive, source, source_manifest, first = evidence
    second = deepcopy(first)
    second["ticker"] = "MSFT"
    second["artifacts"] = {key: value.replace("AAPL", "MSFT") for key, value in first["artifacts"].items()}
    shutil.copytree(source / "tickers/AAPL", source / "tickers/MSFT")
    analysis_path = source / second["artifacts"]["analysis_json"]
    analysis = json.loads(analysis_path.read_bytes())
    analysis["ticker"] = "MSFT"
    write(analysis_path, analysis)
    source_manifest["tickers"].append(second)
    write(source / "run.json", source_manifest)
    source_store = ResearchArtifactStore(archive, now=NOW)
    references = [source_store.make(source, row, "report_markdown") for row in (first, second)]
    manifests = []
    for name in ("overlay_one", "overlay_two"):
        destination = archive / "runs/2026" / name
        rows = deepcopy([first, second])
        for row, reference in zip(rows, references):
            write(destination / row["artifacts"]["analysis_json"],
                  json.loads((source / row["artifacts"]["analysis_json"]).read_bytes()))
            row["artifacts"]["report_markdown"] = reference
        manifest = publish_overlay(destination, rows[0])
        manifest["finished_at"] = "2026-05-30T10:00:00+00:00"
        manifest["tickers"] = rows
        manifest["active_universe"] = {"expected_watchlist_tickers": ["AAPL", "MSFT"]}
        write(destination / "run.json", manifest)
        manifests.append(manifest)
    expected = {(manifest["run_id"], row["ticker"]): site._render_ticker_page(
                    manifest, row, SiteSettings(), manifests=manifests, portfolio_summary={})
                for manifest in manifests for row in site._public_ticker_summaries(manifest)}
    monkeypatch.setattr(site, "_load_run_manifests", lambda _: manifests)
    monkeypatch.setattr(site, "_select_published_manifests", lambda *_: manifests)
    for target in ("tradingagents.scheduled.site._build_youtube_site_addon",
                   "tradingagents.scheduled.site._build_prism_telegram_site_addon",
                   "tradingagents.work.site.build_work_site",
                   "tradingagents.scheduled.mobile_site.build_mobile_site",
                   "tradingagents.scheduled.ai_context.build_ai_context"):
        monkeypatch.setattr(target, lambda *args, **kwargs: None)
    digest = references[0]["source_manifest_sha256"]
    reads = []
    original_blob = ResearchArtifactStore._blob
    def counted_blob(self, value):
        if value == digest:
            reads.append(value)
        return original_blob(self, value)
    monkeypatch.setattr(ResearchArtifactStore, "_blob", counted_blob)
    output = tmp_path / "site"
    site.build_site(archive, output, SiteSettings())
    assert len(reads) == 2  # One verified manifest per run, rather than per ticker.
    for (run_id, ticker), page in expected.items():
        assert (output / "runs" / run_id / f"{ticker}.html").read_text(encoding="utf-8") == page
    # A new run must enforce its own earlier cutoff, not inherit a later cache.
    manifests[1]["finished_at"] = "2026-05-30T08:00:00+00:00"
    with pytest.raises(ValueError, match="future-dated"):
        site.build_site(archive, output, SiteSettings())


def test_cached_site_manifest_still_checks_each_owner(evidence, monkeypatch):
    from tradingagents.scheduled.config import SiteSettings
    from tradingagents.scheduled.site import _render_ticker_page
    destination, row = bootstrap(evidence, monkeypatch)
    manifest = publish_overlay(destination, row)
    store = ResearchArtifactStore.from_run_dir(destination, now=manifest["finished_at"])
    _render_ticker_page(manifest, row, SiteSettings(), research_store=store)
    owner = destination / row["artifacts"]["analysis_json"]
    analysis = json.loads(owner.read_bytes())
    analysis["decision"] = "BUY"
    write(owner, analysis)
    with pytest.raises(ValueError, match="original thesis"):
        _render_ticker_page(manifest, row, SiteSettings(), research_store=store)


@pytest.mark.parametrize("field,value", [
    ("started_at", None), ("started_at", "bad"), ("started_at", "2026-05-30T09:01:00"),
    ("finished_at", "2026-05-31T12:00:00+00:00"), ("finished_at", "2026-05-30T08:00:00+00:00"),
    ("analysis_date", None), ("analysis_date", "2026-02-30"), ("analysis_date", "2026-05-31"),
    ("trade_date", None), ("trade_date", "bad"), ("trade_date", "2026-05-31"),
])
def test_invalid_original_clocks_fail_before_snapshot_publication(evidence, field, value):
    archive, source, manifest, row = evidence
    analysis_path = source / row["artifacts"]["analysis_json"]
    analysis = json.loads(analysis_path.read_bytes())
    analysis[field] = value
    row[field] = value
    write(analysis_path, analysis)
    write(source / "run.json", manifest)
    with pytest.raises(ValueError):
        ResearchArtifactStore(archive, now=NOW).make(source, row, "final_state_json")
    assert not (archive / "research-snapshots").exists()


@pytest.mark.parametrize("field,value", [("started_at", None), ("finished_at", None),
    ("finished_at", "2026-05-31T01:00:00+00:00"), ("finished_at", "bad"),
    ("finished_at", "2026-05-30T09:03:00"), ("finished_at", "2026-05-30T08:00:00+00:00")])
def test_invalid_terminal_clock_fails(evidence, field, value):
    archive, source, manifest, row = evidence
    manifest[field] = value
    write(source / "run.json", manifest)
    with pytest.raises(ValueError):
        ResearchArtifactStore(archive, now=NOW).make(source, row, "report_markdown")


@pytest.mark.parametrize("value", ["../outside.json", "/outside.json", "C:/outside.json", "tickers/MSFT/state.json", ""])
def test_artifact_escape_empty_and_missing_are_rejected(evidence, value):
    archive, source, manifest, row = evidence
    row["artifacts"]["final_state_json"] = value
    write(source / "run.json", manifest)
    with pytest.raises(ValueError):
        ResearchArtifactStore(archive, now=NOW).make(source, row, "final_state_json")


@pytest.mark.parametrize("blob_field", ["source_manifest_sha256", "analysis_sha256", "artifact_sha256", "snapshot_sha256"])
@pytest.mark.parametrize("damage", ["missing", "empty", "changed"])
def test_snapshot_damage_fails_closed_even_after_source_is_gone(evidence, tmp_path, blob_field, damage):
    archive, source, _, row = evidence
    ref = ResearchArtifactStore(archive, now=NOW).make(source, row, "final_state_json")
    assert source.is_relative_to(tmp_path)
    shutil.rmtree(source)
    digest = ref[blob_field]
    blob = archive / "research-snapshots/sha256" / digest[:2] / digest
    if damage == "missing":
        blob.unlink()
    else:
        blob.write_bytes(b"" if damage == "empty" else b'{"changed":true}')
    with pytest.raises(ValueError):
        ResearchArtifactStore(archive, now=NOW).read(ref, key="final_state_json", ticker="AAPL")


@pytest.mark.parametrize("field,value", [("ticker", "MSFT"), ("market", "KR"),
    ("source_finished_at", "2026-05-31T12:00:00+00:00"), ("artifact_path", "../wrong"),
    ("artifact_size_bytes", 0), ("source_run_id", "wrong"), ("artifact_key", "analysis_json")])
def test_reference_metadata_cannot_be_rebound(evidence, field, value):
    archive, source, _, row = evidence
    ref = ResearchArtifactStore(archive, now=NOW).make(source, row, "final_state_json")
    ref[field] = value
    with pytest.raises(ValueError):
        ResearchArtifactStore(archive, now=NOW).read(ref, key="final_state_json", ticker="AAPL", market="US")


def test_publishing_concurrently_never_replaces_or_changes_blob(evidence):
    archive, source, _, row = evidence
    def publish(_):
        return ResearchArtifactStore(archive, now=NOW).make(source, row, "report_markdown")
    with ThreadPoolExecutor(max_workers=4) as pool:
        refs = list(pool.map(publish, range(8)))
    assert all(ref == refs[0] for ref in refs)
    assert len(list((archive / "research-snapshots/sha256").glob("*/*"))) == 4
    assert not list((archive / "research-snapshots").rglob(".publish-*"))


def test_existing_corrupt_blob_is_never_repaired_or_overwritten(evidence):
    archive, source, _, row = evidence
    ref = ResearchArtifactStore(archive, now=NOW).make(source, row, "report_markdown")
    digest = ref["artifact_sha256"]
    blob = archive / "research-snapshots/sha256" / digest[:2] / digest
    blob.write_bytes(b"corrupt original evidence")
    with pytest.raises(ValueError):
        ResearchArtifactStore(archive, now=NOW).make(source, row, "report_markdown")
    assert blob.read_bytes() == b"corrupt original evidence"


def test_strict_recovery_rejects_refs_and_unknown_generic_consumers(evidence, monkeypatch):
    from tradingagents.scheduled.research_recovery import _artifact_hashes
    from tradingagents.scheduled.runner import _resolve_artifact_source as runner_resolve
    from tradingagents.scheduled.site import _resolve_artifact_source as site_resolve
    destination, row = bootstrap(evidence, monkeypatch)
    with pytest.raises(ValueError, match="artifact path"):
        _artifact_hashes(destination.resolve(), row)
    for resolve in (runner_resolve, site_resolve):
        with pytest.raises(ValueError, match="explicit verified"):
            resolve(destination, row["artifacts"]["report_markdown"])


def test_cutoff_is_inclusive_and_future_original_is_rejected(evidence):
    archive, source, manifest, row = evidence
    boundary = datetime.fromisoformat(manifest["finished_at"])
    ref = ResearchArtifactStore(archive, now=boundary).make(source, row, "final_state_json")
    assert ResearchArtifactStore(archive, now=boundary).read(ref, key="final_state_json", ticker="AAPL")
    with pytest.raises(ValueError):
        ResearchArtifactStore(archive, now=boundary.replace(microsecond=0, second=0, minute=2)).read(
            ref, key="final_state_json", ticker="AAPL")


def test_snapshot_copied_bytes_are_independent_of_original_changes(evidence):
    archive, source, _, row = evidence
    store = ResearchArtifactStore(archive, now=NOW)
    ref = store.make(source, row, "report_markdown")
    original = (source / row["artifacts"]["report_markdown"]).read_bytes()
    (source / row["artifacts"]["report_markdown"]).write_text("changed later", encoding="utf-8")
    assert ResearchArtifactStore(archive, now=NOW).read(ref, key="report_markdown", ticker="AAPL") == original


@pytest.mark.parametrize("field,value", [("analysis_date", "2026-05-29"), ("trade_date", "2026-05-28"),
    ("started_at", "2026-05-30T09:00:59+00:00"), ("finished_at", "2026-05-30T09:01:59+00:00")])
def test_current_analysis_must_bind_to_same_original_snapshot(evidence, monkeypatch, field, value):
    from tradingagents.portfolio.semantic_judge import _load_context_by_ticker
    from tradingagents.scheduled.config import SiteSettings
    from tradingagents.scheduled.site import _render_ticker_page
    archive, _, _, _ = evidence
    destination, row = bootstrap(evidence, monkeypatch)
    manifest = publish_overlay(destination, row)
    analysis_path = destination / row["artifacts"]["analysis_json"]
    analysis = json.loads(analysis_path.read_bytes())
    analysis[field] = value
    write(analysis_path, analysis)
    for action in (
        lambda: _load_context_by_ticker(destination, manifest),
        lambda: _render_ticker_page(manifest, row, SiteSettings()),
        lambda: ResearchArtifactStore(archive).make(destination, row, "report_markdown"),
    ):
        with pytest.raises(ValueError, match="consuming original clocks"):
            action()


def test_site_and_semantic_reject_different_market(evidence, monkeypatch):
    from tradingagents.portfolio.semantic_judge import _load_context_by_ticker
    from tradingagents.scheduled.config import SiteSettings
    from tradingagents.scheduled.site import _render_ticker_page
    destination, row = bootstrap(evidence, monkeypatch)
    manifest = publish_overlay(destination, row)
    manifest["settings"]["market"] = "KR"
    for action in (lambda: _load_context_by_ticker(destination, manifest),
                   lambda: _render_ticker_page(manifest, row, SiteSettings())):
        with pytest.raises(ValueError, match="market differs"):
            action()


def test_source_selection_cannot_replace_archived_artifact(evidence):
    archive, source, _, row = evidence
    selected = deepcopy(row)
    selected["artifacts"]["final_state_json"] = "tickers/AAPL/graph.json"
    with pytest.raises(ValueError, match="archived owner"):
        ResearchArtifactStore(archive, now=NOW).make(source, selected, "final_state_json")


def test_clock_date_boundary_in_korea_and_partial_terminal_source(evidence):
    archive, source, manifest, row = evidence
    manifest.update(started_at="2026-05-30T00:00:00+09:00", finished_at="2026-05-30T00:03:00+09:00", status="partial_failure")
    manifest["settings"]["market"] = "KR"
    row.update(started_at="2026-05-30T00:01:00+09:00", finished_at="2026-05-30T00:02:00+09:00")
    analysis = json.loads((source / row["artifacts"]["analysis_json"]).read_bytes())
    analysis.update(started_at=row["started_at"], finished_at=row["finished_at"])
    write(source / row["artifacts"]["analysis_json"], analysis)
    write(source / "run.json", manifest)
    ref = ResearchArtifactStore(archive, now=NOW).make(source, row, "final_state_json")
    assert ref["research"]["analysis_date"] == "2026-05-30"
    assert ResearchArtifactStore(archive, now=NOW).read(ref, key="final_state_json", ticker="AAPL", market="KR")


def test_source_changes_during_read_fail_without_publication(evidence, monkeypatch):
    from tradingagents.scheduled import research_artifact_refs as refs
    archive, source, _, row = evidence
    original_read = refs._read
    def changing(path):
        if path.name == "final_state.json":
            raise ValueError("Research evidence changed while being read")
        return original_read(path)
    monkeypatch.setattr(refs, "_read", changing)
    with pytest.raises(ValueError, match="changed while"):
        ResearchArtifactStore(archive, now=NOW).make(source, row, "final_state_json")
    assert not (archive / "research-snapshots").exists()


def _symlink(link, target):
    try:
        link.symlink_to(target, target_is_directory=target.is_dir())
    except OSError as error:
        if os.name == "nt" and target.is_dir():
            created = subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(target)], capture_output=True)
            if created.returncode == 0:
                return
        pytest.skip(f"Platform cannot create test symlink: {error}")


def test_configured_archive_root_may_be_an_operator_junction(evidence, tmp_path):
    archive, source, _, row = evidence
    alias = tmp_path / "configured-archive"
    _symlink(alias, archive)
    aliased_source = alias / source.relative_to(archive)
    store = ResearchArtifactStore(alias, now=NOW)
    assert store.archive == archive.resolve()
    ref = store.make(aliased_source, row, "report_markdown")
    assert store.read(ref, key="report_markdown", ticker="AAPL")


def test_publication_lock_reparse_never_writes_outside_store(evidence, tmp_path):
    archive, source, _, row = evidence
    root = archive / "research-snapshots"
    root.mkdir()
    outside = tmp_path / "outside-lock"
    outside.write_bytes(b"")
    _symlink(root / ".publication.lock", outside)
    with pytest.raises(ValueError, match="reparse"):
        ResearchArtifactStore(archive, now=NOW).make(source, row, "report_markdown")
    assert outside.read_bytes() == b""


def test_reparse_blob_and_source_artifact_fail_closed(evidence, tmp_path):
    archive, source, _, row = evidence
    artifact = source / row["artifacts"]["report_markdown"]
    outside = tmp_path / "outside-report"
    outside.write_bytes(artifact.read_bytes())
    artifact.unlink()
    _symlink(artifact, outside)
    with pytest.raises(ValueError, match="reparse"):
        ResearchArtifactStore(archive, now=NOW).make(source, row, "report_markdown")


def test_invalid_query_clock_is_rejected(evidence):
    archive, *_ = evidence
    for value in ("bad", datetime(2026, 5, 30), False):
        with pytest.raises(ValueError):
            ResearchArtifactStore(archive, now=value)


def test_only_existing_intraday_append_fields_may_differ(evidence, monkeypatch):
    from tradingagents.scheduled.runner import _append_analysis_intraday_attempt
    archive, _, _, _ = evidence
    destination, row = bootstrap(evidence, monkeypatch)
    manifest = publish_overlay(destination, row)
    _append_analysis_intraday_attempt(run_dir=destination, ticker_summary=row,
                                     attempt_payload={"status": "success", "checked_at": row["finished_at"]})
    ref = row["artifacts"]["final_state_json"]
    store = ResearchArtifactStore(archive)
    assert store.read_owned(ref, key="final_state_json", run_dir=destination, row=row, market="US")
    assert store.make(destination, row, "final_state_json") == ref
    path = destination / row["artifacts"]["analysis_json"]
    analysis = json.loads(path.read_bytes())
    analysis["decision"] = "BUY"
    write(path, analysis)
    with pytest.raises(ValueError, match="original thesis"):
        ResearchArtifactStore(archive).read_owned(ref, key="final_state_json", run_dir=destination, row=row, market="US")
    with pytest.raises(ValueError, match="original thesis"):
        bootstrap((archive, destination, manifest, row), monkeypatch, label="changed_thesis")


@pytest.mark.parametrize("leaf", ["lock", "artifact"])
def test_windows_reparse_attribute_is_rejected_without_symlink_privilege(evidence, monkeypatch, leaf):
    from pathlib import Path
    archive, source, _, row = evidence
    root = archive / "research-snapshots"
    root.mkdir()
    path = root / ".publication.lock" if leaf == "lock" else source / row["artifacts"]["report_markdown"]
    if leaf == "lock":
        path.write_bytes(b"")
    before = path.read_bytes()
    original = Path.lstat
    class Reparse:
        def __init__(self, actual):
            self.actual = actual
            self.st_file_attributes = getattr(actual, "st_file_attributes", 0) | 0x400
        def __getattr__(self, field):
            return getattr(self.actual, field)
    def attributes(candidate, *args, **kwargs):
        actual = original(candidate, *args, **kwargs)
        return Reparse(actual) if candidate == path else actual
    monkeypatch.setattr(Path, "lstat", attributes)
    with pytest.raises(ValueError, match="reparse"):
        ResearchArtifactStore(archive, now=NOW).make(source, row, "report_markdown")
    assert path.read_bytes() == before


@pytest.mark.parametrize("field,value", [("started_at", None), ("started_at", "2026-05-30T12:00:00"),
                                       ("market", None), ("analysis_json", "../../outside.json")])
def test_reference_consumer_requires_own_clock_market_and_local_path(evidence, monkeypatch, field, value):
    from tradingagents.portfolio.semantic_judge import _load_context_by_ticker
    destination, row = bootstrap(evidence, monkeypatch)
    manifest = publish_overlay(destination, row)
    if field == "market":
        manifest["settings"][field] = value
    elif field == "analysis_json":
        row["artifacts"][field] = value
    else:
        manifest[field] = value
    with pytest.raises(ValueError):
        _load_context_by_ticker(destination, manifest)


def test_initial_blob_paths_are_validated_only_after_boundary_exists_and_writer_lock(evidence, monkeypatch):
    from tradingagents.scheduled import research_artifact_refs as module
    from tradingagents.atomic_io import interprocess_file_lock
    archive, source, _, row = evidence
    original = module._safe
    validations = []
    def guarded(root, relative, *, must_exist=True):
        if root.name == "research-snapshots" and relative.startswith("sha256/") and not must_exist:
            assert root.is_dir(), "Resolve only an established snapshot boundary"
            with pytest.raises(TimeoutError), interprocess_file_lock(root/".publication.lock", timeout=0):
                pytest.fail("Initial blob path validation must be inside the publication lock")
            validations.append(relative)
        return original(root, relative, must_exist=must_exist)
    monkeypatch.setattr(module, "_safe", guarded)
    ResearchArtifactStore(archive, now=NOW).make(source, row, "report_markdown")
    assert validations
