from datetime import datetime, timedelta
import hashlib
import json
import sqlite3

import pytest

from tradingagents.atomic_io import atomic_write_json
from tradingagents.execution import session_observations as obs
from tradingagents.execution.session_confirmation import load_session_observations


def time(value):
    return datetime.fromisoformat(value + "+09:00")


MON = "2026-11-23"
TUE = "2026-11-24"


def policy(root):
    atomic_write_json(root / "policy.json", {"schema": obs.SCHEMA, "instruments": [
        {"ticker": "069500.KS", "market": "KR", "venue": "J"}]})


def market_bar(_, day):
    return {"output2": [{"stck_bsop_date": day.replace("-", ""), "stck_oprc": "100",
                         "stck_clpr": "105", "stck_hgpr": "106", "stck_lwpr": "98", "acml_vol": "1000"}]}


def test_close_and_open_publish_native_proof_and_preserve_receipt(tmp_path):
    policy(tmp_path)
    obs.capture_due(tmp_path, clock=lambda: time(MON + "T08:59:00"), download=market_bar)
    out = obs.capture_due(tmp_path, clock=lambda: time(MON + "T15:36:00"), download=market_bar)
    assert out[0]["status"] == "OBSERVED_MARKET_ONLY"
    at = time(TUE + "T09:00:10")
    obs.capture_due(tmp_path, clock=lambda: at, download=market_bar)
    receipt = load_session_observations(tmp_path / "confirmations", "069500.KS", "KR")
    assert receipt["regular_close"]["session"] == MON and receipt["regular_close"]["price"] == 105
    assert datetime.fromisoformat(receipt["official_open"]["event_at"]) == at
    assert receipt["official_open"]["price"] == 100
    assert not obs.capture_due(tmp_path, clock=lambda: at, download=lambda *_: pytest.fail("duplicate API"))
    with sqlite3.connect(tmp_path / "observations.sqlite") as db:
        raw, digest = db.execute("SELECT raw_response,source_sha256 FROM observations WHERE stage='close'").fetchone()
        assert hashlib.sha256(raw).hexdigest() == digest
        with pytest.raises(sqlite3.IntegrityError, match="append-only"):
            db.execute("DELETE FROM observations")
    status = obs.observation_status(tmp_path, clock=lambda: time(TUE + "T16:00:00"))
    assert status["markets"]["KR"] == {"completed_sessions": 2, "observation_slots": 2,
        "observed_market_only": 1, "qualification": "TRADING_EVIDENCE_UNVERIFIED"}
    assert status["eligible_for_promotion"] is False


def test_late_open_and_missing_bar_do_not_produce_authority(tmp_path):
    policy(tmp_path)
    now = time(MON + "T09:00:31")
    assert obs.capture_due(tmp_path, clock=lambda: now, download=market_bar)[0]["status"] == "OBSERVED_LATE_OPEN"
    assert not load_session_observations(tmp_path / "confirmations", "069500.KS", "KR")
    day = time(MON + "T15:36:00")
    future = lambda *_: market_bar(None, TUE)
    assert obs.capture_due(tmp_path, clock=lambda: day, download=future)[0]["status"] == "SOURCE_UNVERIFIED"
    assert not obs.capture_due(tmp_path, clock=lambda: day + timedelta(seconds=30),
                               download=lambda *_: pytest.fail("failure backoff"))
    assert obs.capture_due(tmp_path, clock=lambda: day + timedelta(minutes=11), download=market_bar)
    receipt = load_session_observations(tmp_path / "confirmations", "069500.KS", "KR")
    assert "official_open" not in receipt and "regular_close" in receipt


@pytest.mark.parametrize("rows", [[], [{}], [{"stck_bsop_date": "20260230"}]])
def test_empty_missing_or_invalid_session_rows_never_publish(tmp_path, rows):
    policy(tmp_path)
    opened = time(MON + "T09:00:00")
    assert obs.capture_due(tmp_path, clock=lambda: opened,
                           download=lambda *_: {"output2": rows})[0]["status"] == "SOURCE_UNVERIFIED"
    assert not load_session_observations(tmp_path / "confirmations", "069500.KS", "KR")


def test_opening_retry_can_recover_before_proof_deadline(tmp_path):
    policy(tmp_path)
    opened = time(MON + "T09:00:00")
    assert obs.capture_due(tmp_path, clock=lambda: opened, download=lambda *_: {"output2": []})
    early = opened + timedelta(seconds=2)
    assert not obs.capture_due(tmp_path, clock=lambda: early, download=lambda *_: pytest.fail("backoff"))
    retry = opened + timedelta(seconds=10)
    assert obs.capture_due(tmp_path, clock=lambda: retry, download=market_bar)[0]["status"] == "OBSERVED"
    proof = load_session_observations(tmp_path / "confirmations", "069500.KS", "KR")
    assert datetime.fromisoformat(proof["official_open"]["observed_at"]) == retry


def test_modifies_neither_orders_nor_scope_and_uses_only_unadjusted_routes():
    class Client:
        def domestic_daily_itemchartprice(self, ticker, **kwargs):
            assert ticker == "069500" and kwargs["adjusted_price"] == "1" and kwargs["market_division"] == "J"
            return {"verified_contract": True}

        def request_json(self, **kwargs):
            assert kwargs["method"] == "GET"
            assert kwargs["path"] == "/uapi/overseas-price/v1/quotations/dailyprice"
            assert kwargs["params"]["MODP"] == "0"
            return {"verified_contract": True}, {}

    for market, ticker, venue in (("KR", "069500.KS", "J"), ("US", "SPY", "AMS")):
        assert obs._download({"market": market, "ticker": ticker, "venue": venue}, MON, Client())["verified_contract"]


def test_scheduler_roots_flow_into_standard_research_config(tmp_path, monkeypatch):
    from tradingagents.scheduled.config import load_scheduled_config

    monkeypatch.setenv("TRADINGAGENTS_FORWARD_OBSERVATION_ROOT", str(tmp_path / "evidence"))
    path = tmp_path / "test.toml"
    path.write_text('[run]\nmarket="KR"\ntickers=["069500.KS"]\n[storage]\narchive_dir="archive"\nsite_dir="site"\n')
    config = load_scheduled_config(path)
    assert config.execution.session_confirmation_receipts_dir == tmp_path / "evidence/confirmations"
    assert config.storage.daily_history_capture_db == tmp_path / "evidence/research-prices.sqlite"


def test_observation_transport_paces_only_exact_demo_quotes(monkeypatch):
    from types import SimpleNamespace

    calls = []
    monkeypatch.setattr(obs.requests.Session, "request", lambda _, *args, **kwargs: calls.append(args))
    client = obs._QuotationSession(SimpleNamespace(wait=lambda: calls.append("paced")))
    path = "/uapi/domestic-stock/v1/quotations/inquire-daily-itemchartprice"
    client.request("GET", obs.DEMO_HOST + path, headers={"tr_id": "FHKST03010100"}, allow_redirects=False)
    with pytest.raises(obs.DemoError):
        client.request("GET", obs.DEMO_HOST + "/uapi/domestic-stock/v1/trading/inquire-balance", allow_redirects=False)
    with pytest.raises(obs.DemoError):
        client.request("GET", obs.DEMO_HOST + path, headers={"tr_id": "wrong"}, allow_redirects=False)
    assert calls == ["paced", ("GET", obs.DEMO_HOST + path)]


def test_independent_research_command_inherits_capture_root(tmp_path, monkeypatch):
    import os
    import sys
    from tradingagents import local_automation
    from tradingagents.execution import research_runtime

    root = tmp_path / "state" / "forward-observation"
    policy(root)
    monkeypatch.setenv("TRADINGAGENTS_FORWARD_OBSERVATION_ROOT", "")
    monkeypatch.setattr(local_automation, "prepare_environment", lambda: None)
    monkeypatch.setattr(obs, "capture_due", lambda *a, **k: pytest.fail("Research should not collect broker quotes."))
    def research(*args, **kwargs):
        assert os.environ["TRADINGAGENTS_FORWARD_OBSERVATION_ROOT"] == str(root)
        return []
    monkeypatch.setattr(research_runtime, "research_due", research)
    monkeypatch.setattr(sys, "argv", ["local_automation", "research-kis",
        "--archive-dir", str(tmp_path / "archive"), "--state-dir", str(root.parent),
        "--runtime-dir", str(tmp_path / "runtime")])
    assert local_automation.main() == 0
