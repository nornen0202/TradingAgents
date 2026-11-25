from hashlib import sha256
from io import BytesIO
import json
from pathlib import Path
import sqlite3
import subprocess
from urllib.parse import urlparse

import pytest

from tradingagents import local_automation as local
from tradingagents.execution.autotrader_dashboard import publish_autotrader_dashboard
from tradingagents.execution.prism_autotrader import AutotraderPolicy, initialize_autotrader_db


def _git(*args):
    return subprocess.check_output(["git", *map(str, args)], timeout=120)


@pytest.fixture
def fake_pages(tmp_path):
    state = tmp_path / "state"
    state.mkdir()
    _git("init", "--bare", "--template=", state / "pages.git")
    remote = tmp_path / "public.git"
    _git("init", "--bare", "--template=", remote)
    _git(f"--git-dir={state / 'pages.git'}", "remote", "add", "fork", remote)
    return state, remote


def _seed_ledger(archive: Path, mode: str) -> Path:
    db = archive / "paper" / "autotrader.sqlite"
    initialize_autotrader_db(db, AutotraderPolicy(mode=mode, kr_initial_capital=876543219))
    with sqlite3.connect(db) as conn:
        conn.execute(
            "INSERT INTO autotrader_pending_entries VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            ("private-intent-id", "KR", "PRIVATE-TICKER", "PRIVATE-DISPLAY", "PRIVATE-SECTOR", mode, 6301, 6401,
             6201, 6701, .25, 7, "PRIVATE-MARKET-REGIME", "PRIVATE-RUN", "QUEUED", "t", "t", "t"),
        )
        for status in ("SUBMITTED", "SUBMITTING", "UNKNOWN", "FAILED"):
            conn.execute(
                "INSERT INTO autotrader_order_intents VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                (f"private-{status}", "KR", "PRIVATE-TICKER", "BUY", mode, 71, 8321, "PRIVATE-BROKER-NO",
                 status, "PRIVATE-METADATA", "t", "t"),
            )
        # An inferred close in this VTS table does not confirm a broker fill.
        conn.execute(
            "INSERT INTO autotrader_trades (intent_id, market, ticker, mode, quantity, buy_price, sell_price, "
            "fee_and_tax, net_pnl, return_pct, slot_fraction, holding_days, exit_reason, opened_at, closed_at) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            ("private-close", "KR", "PRIVATE-TICKER", mode, 1, 6301, 6701, 1, 399, 6.3, .25, 1,
             "PRIVATE-EXIT", "t", "t"),
        )
    return db


def test_regular_publication_stages_only_read_only_aggregate_dashboard(tmp_path, monkeypatch, fake_pages):
    from tradingagents.notifications import local as notifications
    from tradingagents.scheduled import config

    archive = tmp_path / "archive"
    db = _seed_ledger(archive, "kis_vts")
    with sqlite3.connect(db) as conn:
        conn.execute(
            "INSERT INTO autotrader_order_intents VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            ("private-shadow", "KR", "PRIVATE-SHADOW", "BUY", "shadow", 30, 999, None,
             "SUBMITTED", "PRIVATE-SHADOW", "t", "t"),
        )
    original_db = sha256(db.read_bytes()).hexdigest()
    state, _ = fake_pages
    bare = state / "pages.git"
    assert not (bare / "info" / "exclude").exists() and not (bare / "hooks" / "pre-push").exists()
    local.atomic_write_json(state / "autotrader" / "enabled.json", {"mode": "kis_vts"})
    # Simulate leftover files from a prior product generation with the same public names.
    stale = state / "site" / "autotrader"
    local.atomic_write_json(stale / "raw.json", {"intent_id": "PRIVATE-STALE"})
    local.atomic_write_json(stale / "dashboard_data.json", {"account_summary": {"cash": 432198765}})
    (stale / "index.html").write_text("PRIVATE-STALE", encoding="utf-8")
    load_config = config.load_scheduled_config

    def offline_config(*args, **kwargs):
        from dataclasses import replace

        conf = load_config(*args, **kwargs)
        return replace(conf, site=replace(conf.site, refresh_research_prices=False))

    monkeypatch.setattr(config, "load_scheduled_config", offline_config)
    monkeypatch.setattr(notifications, "reconcile_safely", lambda *a, **k: None)
    monkeypatch.setattr(local, "ensure_branch_pages", lambda *_: None)
    for variable in ("TRADINGAGENTS_YOUTUBE_ARCHIVE_DIR", "TRADINGAGENTS_PRISM_TELEGRAM_ARCHIVE_DIR"):
        monkeypatch.delenv(variable, raising=False)
    monkeypatch.setenv("GH_TOKEN", "synthetic-offline-token")
    snapshot = local.script("pages_snapshot")
    mirror = local.script("publish_ai_context")
    monkeypatch.setattr(mirror, "publish", lambda *_: None)

    def offline_script(name):
        if name == "pages_snapshot":
            return snapshot
        if name == "publish_ai_context":
            return mirror
        return original_script(name)

    original_script = local.script
    monkeypatch.setattr(local, "script", offline_script)
    git_run = local.git_run
    outbound_commits = []
    probed = set()
    overrides = {}
    gitdir = f"--git-dir={bare}"

    def public_git_bytes(path):
        return _git(gitdir, "show", f"{outbound_commits[-1]}:{path}")

    monkeypatch.setattr(snapshot, "fetch_live_snapshot", lambda *_: (
        json.loads(public_git_bytes("pages-snapshot.json")) if outbound_commits else None
    ))

    def staged_http(request, *, timeout):
        path = urlparse(request.full_url).path.removeprefix("/TradingAgents/")
        probed.add(path)
        return BytesIO(overrides[path] if path in overrides else public_git_bytes(path))

    monkeypatch.setattr("urllib.request.urlopen", staged_http)

    def capture_push(args, **kwargs):
        if len(args) > 1 and args[1] == "push":
            assert args[2] == "fork"
            commit, destination = args[3].split(":", 1)
            assert destination == "refs/heads/gh-pages"
            outbound_commits.append(commit)
            return ""
        return git_run(args, **kwargs)

    monkeypatch.setattr(local, "git_run", capture_push)
    result = local.publish(archive, state, tmp_path / "runtime", publication_locked=True)

    assert outbound_commits == [result["commit"]]
    tip = outbound_commits[0]
    _git(gitdir, "cat-file", "-e", f"{tip}^{{commit}}")
    assert result["status"] == "DELIVERY_VERIFIED"
    manifest = json.loads(public_git_bytes("pages-snapshot.json"))
    artifacts = manifest["autotrader_artifacts"]
    assert set(artifacts) == {
        "autotrader/dashboard_data.json", "autotrader/us_dashboard_data.json", "autotrader/index.html",
    }
    assert set(artifacts) <= probed
    for path, binding in artifacts.items():
        content = public_git_bytes(path)
        assert binding == {"sha256": sha256(content).hexdigest(), "size": len(content)}
    overrides["autotrader/us_dashboard_data.json"] = b'{"account_summary":{"cash":432198765}}'
    assert not local.verify_live(state / "site")
    assert set(_git(gitdir, "ls-tree", "-r", "--name-only", tip, "--", "autotrader").decode().splitlines()) == {
        "autotrader/dashboard_data.json", "autotrader/us_dashboard_data.json", "autotrader/index.html",
    }
    assert _git(gitdir, "show", f"{tip}:index.html")
    kr = json.loads(_git(gitdir, "show", f"{tip}:autotrader/dashboard_data.json"))
    us = json.loads(_git(gitdir, "show", f"{tip}:autotrader/us_dashboard_data.json"))
    page = _git(gitdir, "show", f"{tip}:autotrader/index.html").decode("utf-8")
    assert kr["queued_candidates"] == 1
    assert kr["accepted_pending_fill_confirmation"] == 1
    assert kr["submission_unknown"] == 2
    assert kr["not_accepted"] == 1
    assert kr["confirmed_unfilled"] is kr["confirmed_fills"] is kr["simulated_round_trip_samples"] is None
    assert us["observation_status"] == "no_order_samples" and us["accepted_pending_fill_confirmation"] == 0
    assert "접수 기록 · 체결 여부 미확인" in page
    assert "브로커에서 확인한 미체결</th><td>확인 자료 없음" in page
    assert "브로커에서 확인한 체결</th><td>확인 자료 없음" in page
    assert "제출 주문 표본 없음" in page
    for value in (json.dumps(kr), json.dumps(us), page):
        assert not any(secret in value for secret in (
            "PRIVATE-", "private-intent", "876543219", "876,543,219", "account_summary", "intent_id",
            "win_rate_pct", "season_return_pct", "payoff_ratio",
        ))
    assert sha256(db.read_bytes()).hexdigest() == original_db
    assert not (archive / "paper" / "dashboard").exists()


@pytest.mark.parametrize("bad_artifact", ["extra_file", "json_extra_key", "duplicate_value", "html_content"])
def test_push_rejects_unsafe_exact_staged_tree(tmp_path, fake_pages, bad_artifact):
    from tradingagents.execution.public_autotrader_dashboard import build_public_autotrader_dashboard

    state, remote = fake_pages
    site = state / "site"
    site.mkdir()
    (site / "index.html").write_text("synthetic")
    local.atomic_write_json(site / "pages-snapshot.json", {})
    build_public_autotrader_dashboard(tmp_path / "archive", site, mode="kis_vts")
    target = site / "autotrader"
    json_path = target / "dashboard_data.json"
    if bad_artifact == "extra_file":
        local.atomic_write_json(target / "extra.json", {"unlisted": "fixture"})
    elif bad_artifact == "json_extra_key":
        data = json.loads(json_path.read_bytes())
        local.atomic_write_json(json_path, {**data, "account_summary": {"fixture": 123}})
    elif bad_artifact == "duplicate_value":
        json_path.write_bytes(json_path.read_bytes().replace(b'{\n', b'{\n  "market": "private",\n', 1))
    else:
        with (target / "index.html").open("ab") as file:
            file.write(b"<!-- private fixture -->")
    with pytest.raises(ValueError, match="autotrader publication"):
        local.push_site(site, state)
    assert not _git(f"--git-dir={remote}", "for-each-ref", "refs/heads/gh-pages")


def test_missing_ledger_and_live_scope_write_no_private_data(tmp_path):
    from tradingagents.execution.public_autotrader_dashboard import build_public_autotrader_dashboard

    archive = tmp_path / "archive"
    site = tmp_path / "site"
    build_public_autotrader_dashboard(archive, site, mode="kis_vts")
    kr = json.loads((site / "autotrader" / "dashboard_data.json").read_bytes())
    assert kr["observation_status"] == "ledger_unavailable"
    assert kr["queued_candidates"] is kr["confirmed_fills"] is None
    assert not archive.exists()

    db = _seed_ledger(archive, "kis_live")
    original_db = sha256(db.read_bytes()).hexdigest()
    build_public_autotrader_dashboard(archive, site, mode="kis_live")
    kr = json.loads((site / "autotrader" / "dashboard_data.json").read_bytes())
    assert kr["observation_status"] == "unavailable" and kr["scope"] is None
    assert kr["queued_candidates"] is kr["accepted_pending_fill_confirmation"] is None
    assert sha256(db.read_bytes()).hexdigest() == original_db


def test_shadow_sample_and_private_dashboard_remain_distinct(tmp_path):
    archive, site = tmp_path / "archive", tmp_path / "site"
    _seed_ledger(archive, "shadow")
    paths = publish_autotrader_dashboard(archive, site_dir=site, policy=AutotraderPolicy(mode="shadow"))
    private = json.loads(paths["kr_json"].read_bytes())
    public = json.loads((site / "autotrader" / "dashboard_data.json").read_bytes())
    assert private["pending_entries"][0]["intent_id"] == "private-intent-id"
    assert private["account_summary"]["initial_capital"] == 876543219
    assert public["simulated_matches"] == public["simulated_round_trip_samples"] == 1
    assert public["accepted_pending_fill_confirmation"] is public["confirmed_fills"] is None
    assert "청산 표본" in paths["site_html"].read_text(encoding="utf-8")

@pytest.mark.parametrize("mode,enabled,kill_switch,halt,private_write", [
    ("shadow", True, False, False, True),
    ("shadow", True, True, False, False),
    ("shadow", False, False, False, False),
    ("shadow", True, False, True, False),
    ("kis_vts", True, False, False, False),
    ("kis_live", True, False, False, False),
])
def test_autotrader_cli_keeps_execution_gates_and_never_writes_site(
    tmp_path, monkeypatch, mode, enabled, kill_switch, halt, private_write,
):
    import sys
    from tradingagents.execution import prism_autotrader

    archive, state = tmp_path / "archive", tmp_path / "state"
    _seed_ledger(archive, "shadow")
    lane = state / "autotrader"
    local.atomic_write_json(lane / "enabled.json", {"mode": mode, "enabled": enabled, "kill_switch": kill_switch})
    if halt:
        (lane / "HALT").touch()
    published_site = state / "site" / "autotrader"
    published_site.mkdir(parents=True)
    staging_file = published_site / "dashboard_data.json"
    staging_file.write_bytes(b"publisher-owned bytes")
    monkeypatch.setattr(prism_autotrader, "run_autotrader_tick", lambda *args: {"status": "fixture"})
    monkeypatch.setattr(local, "prepare_environment", lambda: None)
    monkeypatch.setattr(sys, "argv", ["local_automation", "autotrader", "--archive-dir", str(archive),
                                    "--state-dir", str(state), "--runtime-dir", str(tmp_path / "runtime")])

    assert local.main() == 0
    assert (archive / "paper" / "dashboard" / "dashboard_data.json").is_file() is private_write
    assert list(published_site.iterdir()) == [staging_file]
    assert staging_file.read_bytes() == b"publisher-owned bytes"


def test_concurrent_private_writer_cannot_replace_public_dashboard(tmp_path, monkeypatch):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Event

    from tradingagents.execution import autotrader_dashboard
    from tradingagents.execution.public_autotrader_dashboard import build_public_autotrader_dashboard

    archive, site = tmp_path / "archive", tmp_path / "site"
    _seed_ledger(archive, "shadow")
    private_write_entered, public_write_finished = Event(), Event()
    write = autotrader_dashboard.atomic_write_bytes

    def wait_for_public_build(path, data):
        private_write_entered.set()
        if not public_write_finished.wait(45):
            raise RuntimeError("Public dashboard write did not run during the private write")
        write(path, data)

    monkeypatch.setattr(autotrader_dashboard, "atomic_write_bytes", wait_for_public_build)
    with ThreadPoolExecutor(max_workers=1) as pool:
        private_writer = pool.submit(publish_autotrader_dashboard, archive)
        try:
            assert private_write_entered.wait(45)
            public = build_public_autotrader_dashboard(archive, site, mode="shadow")
            original = {path: path.read_bytes() for path in public.parent.iterdir()}
        finally:
            public_write_finished.set()
        private = private_writer.result(timeout=45)
    assert len(original) == 3
    assert {path: path.read_bytes() for path in public.parent.iterdir()} == original
    assert b"private-intent-id" in private["kr_json"].read_bytes()
    assert all(b"private-intent-id" not in data for data in original.values())
