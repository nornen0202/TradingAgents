from datetime import datetime, timedelta, timezone
import json
from types import SimpleNamespace

import pytest

from tradingagents.atomic_io import atomic_write_json, interprocess_file_lock
from tradingagents.execution import delivery, demo_runtime, paper_runtime, selective_rerun

NOW = datetime(2026, 10, 19, 1, tzinfo=timezone.utc)


@pytest.mark.parametrize("items, expected", [
    ([], ""),
    ([{"title": "earnings", "providerPublishTime": NOW.timestamp()}], "earnings"),
    ([{"content": {"title": "guidance", "pubDate": NOW.isoformat()}}], "guidance"),
    ([{"title": "future", "providerPublishTime": (NOW + timedelta(seconds=1)).timestamp()}], ""),
    ([{"title": "old", "providerPublishTime": (NOW - timedelta(days=4)).timestamp()}], ""),
    ([{"content": {"title": "bad", "pubDate": "2026-02-30"}}], ""),
    ([{"content": {"title": "naive", "pubDate": "2026-10-19T01:00:00"}}], ""),
    ([{"title": "missing"}, None, "bad"], ""),
])
def test_shared_news_requires_locally_verified_publication_clock(monkeypatch, items, expected):
    monkeypatch.setattr(selective_rerun.yf, "Ticker", lambda _: SimpleNamespace(news=items))
    assert selective_rerun._fetch_fresh_headlines("AAPL", analysis_as_of=NOW) == expected


def test_news_cache_empty_is_not_a_second_fetch(monkeypatch, tmp_path):
    from tradingagents.live.news_delta import build_news_delta
    monkeypatch.setattr("tradingagents.live.news_delta._fetch_latest_news_text", lambda **_: pytest.fail("second network fetch"))
    assert build_news_delta(ticker="AAPL", market="US", as_of=NOW.isoformat(), news_text="") == []
    assert build_news_delta(ticker="AAPL", market="US", as_of=NOW.isoformat(), news_text="raised guidance") == ["earnings_estimate_upgraded"]
    atomic_write_json(tmp_path / "analysis.json", {"decision": "HOLD"})
    monkeypatch.setattr(selective_rerun, "_fetch_fresh_headlines", lambda *a, **k: pytest.fail("second network fetch"))
    assert selective_rerun.collect_event_signals(run_dir=tmp_path, analysis_as_of=NOW, news_context={},
        ticker_summaries=[{"ticker": "AAPL", "status": "success", "artifacts": {"analysis_json": "analysis.json"}}]) == {}


def setup_handoff(tmp_path, monkeypatch):
    monkeypatch.setenv("TRADINGAGENTS_LOCAL_PAPER_STATE_DIR", str(tmp_path))
    for lane, mode in (("paper", "LOCAL_PAPER_ONLY"), ("kis-strategy", "KIS_DEMO_STRATEGY")):
        atomic_write_json(tmp_path / lane / "enabled.json", {"mode": mode, "enabled": True, "real_orders_enabled": False})
    return {"run_id": "fixture", "status": "success", "settings": {"run_mode": "overlay_only"}, "finished_at": NOW.isoformat()}


def test_handoff_preserves_existing_roots_and_independent_consumers(tmp_path, monkeypatch):
    manifest = setup_handoff(tmp_path, monkeypatch)
    seen = []
    def paper(archive, root, *, lock_timeout):
        assert lock_timeout == 15
        seen.append(root)
        raise TimeoutError()
    def strategy(archive, root, validation):
        seen.extend([root, validation])
        return {"checked_at": NOW.isoformat(), "markets": {"US": {"status": "WAITING_VALIDATION", "secret": "DO_NOT_PUBLISH"}}}
    monkeypatch.setattr(paper_runtime, "tick", paper)
    monkeypatch.setattr(demo_runtime, "tick", strategy)
    result = delivery.handoff_completed_run(tmp_path / "archive", manifest)
    assert set(seen) == {tmp_path / x for x in ("paper", "kis-strategy", "kis-validation")}
    assert result["consumers"]["paper"]["status"] == "EXISTING_CONSUMER_RUNNING"
    assert result["consumers"]["kis_strategy"]["status"] == "COMPLETED"
    assert "DO_NOT_PUBLISH" not in json.dumps(result)
    assert result["real_orders_enabled"] is False


def test_handoff_never_retries_a_timed_out_consumer_callback(tmp_path, monkeypatch):
    manifest = setup_handoff(tmp_path, monkeypatch)
    attempts = {"paper": 0, "kis": 0}
    def paper(*args, lock_timeout):
        assert lock_timeout == 15
        attempts["paper"] += 1
        raise TimeoutError("consumer may already have made progress")
    def strategy(*args):
        attempts["kis"] += 1
        raise TimeoutError("unknown broker outcome must not trigger retry")
    monkeypatch.setattr(paper_runtime, "tick", paper)
    monkeypatch.setattr(demo_runtime, "tick", strategy)
    result = delivery.handoff_completed_run(tmp_path / "archive", manifest)
    assert attempts == {"paper": 1, "kis": 1}
    assert all(row["status"] == "EXISTING_CONSUMER_RUNNING" for row in result["consumers"].values())


@pytest.mark.parametrize("outcome", ["success", "failed", "timeout"])
def test_lightweight_handoff_wakes_existing_workers_without_claiming_consumption(tmp_path, monkeypatch, outcome):
    manifest = setup_handoff(tmp_path, monkeypatch)
    manifest["settings"]["execution_lightweight_refresh"] = True
    monkeypatch.setattr(delivery, "_scheduled_worker_root_matches", lambda root: root == tmp_path)
    monkeypatch.setattr(paper_runtime, "tick", lambda *a, **k: pytest.fail("inline consumer would delay producer"))
    monkeypatch.setattr(demo_runtime, "tick", lambda *a: pytest.fail("inline broker must not run"))
    commands = []
    def run(command, **kwargs):
        commands.append(command)
        assert kwargs == {"capture_output": True, "timeout": 5, "check": False,
                          "creationflags": getattr(delivery.subprocess, "CREATE_NO_WINDOW", 0)}
        if outcome == "timeout":
            raise delivery.subprocess.TimeoutExpired(command, 5)
        return SimpleNamespace(returncode=0 if outcome == "success" else 1)
    monkeypatch.setattr(delivery.subprocess, "run", run)
    result = delivery.handoff_completed_run(tmp_path / "archive", manifest)
    assert sorted(command[-1] for command in commands) == [
        "\\TradingAgents\\LocalAutomation-paper", "\\TradingAgents\\LocalAutomation-strategy-kis"]
    assert all(command[:-1] == ["schtasks.exe", "/Run", "/TN"] for command in commands)
    assert result["delivery_mode"] == "SCHEDULED_WORKER_WAKE"
    expected = "WAKE_REQUESTED" if outcome == "success" else "SCHEDULED_TICK_PENDING"
    assert all(row == {"status": expected} for row in result["consumers"].values())


@pytest.mark.parametrize("config", [[], {}, {"enabled": False},
    {"mode": "KIS_DEMO_STRATEGY", "enabled": True, "real_orders_enabled": True}])
def test_scheduled_handoff_cannot_enable_disabled_or_live_lane(tmp_path, monkeypatch, config):
    manifest = setup_handoff(tmp_path, monkeypatch)
    manifest["settings"]["execution_lightweight_refresh"] = True
    monkeypatch.setattr(delivery, "_scheduled_worker_root_matches", lambda _: True)
    for lane in ("paper", "kis-strategy"):
        atomic_write_json(tmp_path / lane / "enabled.json", config)
    monkeypatch.setattr(delivery.subprocess, "run", lambda *a, **k: pytest.fail("disabled worker wake"))
    result = delivery.handoff_completed_run(tmp_path / "archive", manifest)
    assert all(row == {"status": "DISABLED"} for row in result["consumers"].values())


def test_scheduled_handoff_requires_explicit_matching_launcher_root(tmp_path, monkeypatch):
    monkeypatch.setattr(delivery, "os", SimpleNamespace(name="nt", getenv=lambda _: str(tmp_path / "production")))
    assert delivery._scheduled_worker_root_matches(tmp_path / "production")
    assert not delivery._scheduled_worker_root_matches(tmp_path / "preview")
    monkeypatch.setattr(delivery, "os", SimpleNamespace(name="nt", getenv=lambda _: None))
    assert not delivery._scheduled_worker_root_matches(tmp_path)


@pytest.mark.parametrize("change", ["unset", "failed", "full", "disabled", "live", "malformed"])
def test_handoff_never_enables_trading(tmp_path, monkeypatch, change):
    manifest = setup_handoff(tmp_path, monkeypatch)
    if change == "unset":
        monkeypatch.delenv("TRADINGAGENTS_LOCAL_PAPER_STATE_DIR")
    if change == "failed":
        manifest["status"] = "failed"
    if change == "full":
        manifest["settings"]["run_mode"] = "full"
    for lane in ("paper", "kis-strategy"):
        path = tmp_path / lane / "enabled.json"
        config = json.loads(path.read_text())
        if change == "disabled":
            config["enabled"] = False
        if change == "live":
            config["real_orders_enabled"] = True
        if change == "malformed":
            config = []
        atomic_write_json(path, config)
    monkeypatch.setattr(paper_runtime, "tick", lambda *a, **k: pytest.fail("must remain off"))
    monkeypatch.setattr(demo_runtime, "tick", lambda *a: pytest.fail("must remain off"))
    delivery.handoff_completed_run(tmp_path / "archive", manifest)


def test_immediate_handoff_consumes_original_signal_once_and_expiry_stays_strict(tmp_path, monkeypatch):
    from tests.execution.test_demo_runtime import Harness
    h = Harness(tmp_path, "KR")
    # Producer finishes with 10 seconds left; next minute polling is too late.
    h.now += timedelta(seconds=105)
    manifest = setup_handoff(tmp_path / "delivery", monkeypatch)
    # Keep the harness's original enabled state and guarded broker/journal.
    real_tick = demo_runtime.tick
    def consume(*_):
        return real_tick(h.archive, h.root, h.validation, clock=lambda: h.now,
                         broker_factory=h.factory, quote_loader=h.quote, account_loader=h.account,
                         gate=h.gate,
                         tickers={"KR": (h.ticker,), "US": ("AAPL",)})
    monkeypatch.setattr(demo_runtime, "tick", consume)
    monkeypatch.setattr(paper_runtime, "tick", lambda *a, **k: {"markets": {}})
    delivery.handoff_completed_run(h.archive, manifest)
    assert len(h.orders) == 1
    delivery.handoff_completed_run(h.archive, manifest)
    assert len(h.orders) == 1  # stable identity, never a second original order
    h.now += timedelta(seconds=10)
    assert demo_runtime.candidates(h.archive / "runs/2026/fixture-1", "KR", h.now, (h.ticker,)) == []
    with interprocess_file_lock(h.root / "strategy.lock", timeout=0):
        result = delivery.handoff_completed_run(h.archive, manifest)
    assert result["consumers"]["kis_strategy"]["status"] == "EXISTING_CONSUMER_RUNNING"


def test_runner_finishes_slow_news_before_price_and_hands_off_only_published_run(tmp_path, monkeypatch):
    from tradingagents.scheduled import runner
    from tradingagents.scheduled.config import load_scheduled_config
    from tests.test_scheduled_run_mode import _fake_overlay_updates
    config_file = tmp_path / "config.toml"
    config_file.write_text('[run]\ntickers=["AAPL"]\nrun_mode="full"\n'
        f'[storage]\narchive_dir="{tmp_path.as_posix()}"\nsite_dir="{(tmp_path / "site").as_posix()}"\n'
        '[execution]\nenabled=true\ncheckpoints_kst=["00:00"]\n', encoding="utf-8")
    events = []
    clock = [NOW]
    class Clock(datetime):
        @classmethod
        def now(cls, tz=None):
            return clock[0].astimezone(tz)
    monkeypatch.setattr(runner, "datetime", Clock)
    monkeypatch.setattr(runner, "_resolve_run_trade_date", lambda **_: "2026-10-16")
    monkeypatch.setattr(runner, "_run_single_ticker", lambda **_: {"ticker": "AAPL", "status": "success", "artifacts": {}, "metrics": {}})
    def news(**kwargs):
        assert kwargs["analysis_as_of"] == NOW
        events.append("news")
        clock[0] += timedelta(seconds=90)
        return {"AAPL": "dated earnings guidance"}
    monkeypatch.setattr(runner, "collect_event_news", news)
    monkeypatch.setattr(runner, "collect_event_signals", lambda **_: {})
    def prices(**kwargs):
        events.append("prices")
        assert clock[0] == NOW + timedelta(seconds=90)
        return _fake_overlay_updates(**kwargs)
    monkeypatch.setattr(runner, "_run_execution_overlay_passes", prices)
    def context(**kwargs):
        assert kwargs["news_context"] == {"AAPL": "dated earnings guidance"}
        events.append("cached_delta")
        return {}
    monkeypatch.setattr(runner, "build_live_context_delta", context)
    def handoff(archive, manifest, **kwargs):
        events.append("handoff")
        saved = next((archive / "runs").glob("*/*/run.json"))
        assert json.loads(saved.read_text(encoding="utf-8"))["finished_at"] == manifest["finished_at"]
        assert datetime.fromisoformat(manifest["finished_at"]) == clock[0]
    monkeypatch.setattr(delivery, "handoff_completed_run", handoff)
    monkeypatch.setattr(runner, "build_site", lambda *a, **k: events.append("site"))
    runner.execute_scheduled_run(load_scheduled_config(config_file), run_label="delivery-test")
    assert events == ["news", "prices", "cached_delta", "handoff", "site"]
