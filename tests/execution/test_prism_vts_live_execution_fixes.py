"""Deterministic offline tests for PRISM-to-VTS live execution fixes."""
from __future__ import annotations

from datetime import datetime, timedelta
import json
import sqlite3
from zoneinfo import ZoneInfo

import pytest

from tests.execution.test_prism_vts_candidate_path import NormalCli, read
from tradingagents.atomic_io import atomic_write_json
from tradingagents.execution import prism_candidate_runtime
from tradingagents.execution.autotrader_dashboard import publish_autotrader_dashboard
from tradingagents.execution.prism_autotrader import (
    AutotraderPolicy,
    PrismAutoTrader,
    _default_quote_loader,
)


@pytest.fixture(params=["KR", "US"])
def cli(tmp_path, monkeypatch, request):
    return NormalCli(tmp_path, monkeypatch, request.param)


def test_selective_rerun_lineage_admits_verified_thesis_refresh_and_rejects_unverified(cli, monkeypatch):
    h = cli.h
    root = cli.source("production-full", action="WAIT")
    mid_id = f"{h.now:%Y%m%dT%H%M%S}_local-thesis-refresh-{h.market.lower()}"
    mid = h.archive / "runs" / f"{h.now:%Y}" / mid_id
    mid.mkdir(parents=True, exist_ok=True)
    root_manifest = read(root / "run.json")
    mid_manifest = {
        **root_manifest,
        "run_id": mid_id,
        "overlay_source_run_id": root.name,
        "active_universe": None,
        "settings": {**root_manifest["settings"], "run_mode": "selective_rerun_only"},
    }
    atomic_write_json(mid / "run.json", mid_manifest)
    h.now += timedelta(minutes=2)
    leaf = cli.source("production-overlay", action="WAIT", parent=mid)

    monkeypatch.setattr(prism_candidate_runtime, "verified_revision", lambda *a, **k: False)
    blocked = cli.run("autotrader")
    assert "VTS_CANDIDATE_SOURCE_UNVERIFIED" in blocked["blockers"]

    monkeypatch.setattr(prism_candidate_runtime, "verified_revision", lambda *a, **k: True)
    admitted = cli.run("autotrader")
    assert admitted["blockers"] == []
    assert admitted["source_run_id"] == leaf.name
    assert admitted["entries_queued"] == [h.ticker]


def test_bridged_conditional_entry_executes_live_breakout_and_blocks_out_of_band(cli):
    h = cli.h
    cli.open = False
    h.now -= timedelta(hours=2)
    baseline = cli.source("preopen-full", action="WAIT", reference=False)
    assert cli.run("autotrader")["entries_waiting_for_native_price"] == 1

    # Advance to regular session with 195-second batch postprocessing lag and decision_now="NONE"
    h.now += timedelta(hours=2)
    cli.open = True
    overlay = cli.source("intraday-overlay", action="WAIT", parent=baseline)
    obs_at = (h.now - timedelta(seconds=195)).isoformat()
    ref_at = (h.now - timedelta(seconds=130)).isoformat()

    bundle = read(overlay / "decision_bundle_v2.json")
    bundle["strategy_table"][0]["raw_codes"]["decision_now"] = "NONE"
    bundle["strategy_table"][0]["market_data_asof"] = obs_at
    atomic_write_json(overlay / "decision_bundle_v2.json", bundle)

    upd_path = overlay / "tickers" / h.ticker / "execution_update.json"
    upd = read(upd_path)
    upd["decision_now"] = "NONE"
    upd["market_data_asof"] = obs_at
    upd["price_reference"]["observed_at"] = ref_at
    atomic_write_json(upd_path, upd)

    cand_path = overlay / "portfolio-private/portfolio_candidates.json"
    cand_doc = read(cand_path)
    cand_doc["candidates"][0]["data_health"]["price_reference"]["observed_at"] = ref_at
    atomic_write_json(cand_path, cand_doc)

    contract_path = overlay / "tickers" / h.ticker / "execution_contract.json"
    contract = read(contract_path)
    breakout_px = round(h.price * 1.01, 2)
    contract["breakout_level"] = breakout_px
    contract["breakout_confirmation"] = "close_above"
    atomic_write_json(contract_path, contract)

    cli.configure(native=True, candidate=True, daily=True)
    status = cli.run("autotrader")
    assert status["forward_observations"] == 1

    # 1. Live quote below breakout_level -> blocked with ENTRY_CURRENT_PRICE_NOT_CONFIRMED
    below = cli.run("strategy-kis")
    assert "ENTRY_CURRENT_PRICE_NOT_CONFIRMED" in below["blockers"], below
    assert not h.orders

    # 2. Live quote breaks above breakout_level within +3% chase band -> VTS BUY submitted & filled!
    h.price = round(breakout_px * 1.005, 2) if h.market == "US" else int(breakout_px + 1000)
    submitted = cli.run("strategy-kis")
    assert submitted["orders"][0]["status"] == "ACKNOWLEDGED", submitted
    assert submitted["allocation_diagnostics"]["prism_bridged_candidates"]["bridged_entries"] == 1
    h.fill()
    h.now += timedelta(seconds=15)
    filled = cli.run("strategy-kis")
    assert filled["orders"][0]["status"] == "FILLED" and filled["owned"][h.ticker] == 1


def test_bridged_protective_exit_sells_on_intraday_hardstop_even_when_bundle_says_hold(cli):
    h = cli.h
    baseline = cli.source("production-full")
    assert cli.run("autotrader")["entries_queued"] == [h.ticker]
    assert cli.run("strategy-kis")["orders"][0]["status"] == "ACKNOWLEDGED"
    h.fill()
    h.now += timedelta(seconds=15)
    assert cli.run("strategy-kis")["owned"][h.ticker] == 1

    # Intraday -10% drop while decision_bundle_v2 keeps decision_now="HOLD" (no LLM rerun)
    h.price = round(h.price * 0.90, 2) if h.market == "US" else int(h.price * 0.90)
    h.now += timedelta(seconds=20)
    hold_overlay = cli.source("hold-overlay", action="WAIT", parent=baseline)
    bundle = read(hold_overlay / "decision_bundle_v2.json")
    bundle["strategy_table"][0]["raw_codes"]["decision_now"] = "HOLD"
    atomic_write_json(hold_overlay / "decision_bundle_v2.json", bundle)
    upd = read(hold_overlay / "tickers" / h.ticker / "execution_update.json")
    upd["decision_now"] = "HOLD"
    atomic_write_json(hold_overlay / "tickers" / h.ticker / "execution_update.json", upd)

    producer = cli.run("autotrader")
    assert producer["risk_exit_candidates"] == 1
    cli.account_cash = 0
    sell = cli.run("strategy-kis")
    assert sell["orders"][-1]["status"] == "ACKNOWLEDGED", sell
    assert sell["allocation_diagnostics"]["prism_bridged_candidates"]["bridged_exits"] == 1
    assert [row["side"] for row in h.orders.values()] == ["BUY", "SELL"]


def test_shadow_prewire_commit_durability_native_ref_and_vts_dashboard_overlay(tmp_path, monkeypatch):
    from tradingagents.dataflows.intraday import kis_quotes

    # Ensure _default_quote_loader never falls back to yfinance when KIS quote fails
    monkeypatch.setattr(kis_quotes.KISQuoteProvider, "fetch", lambda self, ticker: (_ for _ in ()).throw(RuntimeError("no kis")))
    now_ny = datetime(2026, 11, 25, 10, 30, tzinfo=ZoneInfo("America/New_York"))
    assert _default_quote_loader("US", "AAPL", now_ny) is None

    archive, state = tmp_path / "archive", tmp_path / "state"
    run_us = archive / "runs/2026/20261125T150000_us_full"
    atomic_write_json(run_us / "run.json", {
        "run_id": run_us.name, "status": "success", "settings": {"market": "US"}, "finished_at": now_ny.isoformat()
    })
    # Candidate 1 has only KRW-polluted position_metrics -> must be rejected!
    # Candidate 2 has verified USD price_reference -> must be admitted and commit SUBMITTING pre-wire!
    atomic_write_json(run_us / "portfolio-private/portfolio_candidates.json", {
        "batch_metrics": {"market_regime": "constructive"},
        "candidates": [
            {
                "canonical_ticker": "MSFT", "stance": "BULLISH", "suggested_action_now": "STARTER_NOW",
                "confidence": 0.9, "thesis_strength": 0.9, "setup_quality": "COMPELLING",
                "position_metrics": {"current_price": 580000.0}, "data_health": {},
            },
            {
                "canonical_ticker": "NVDA", "stance": "BULLISH", "suggested_action_now": "STARTER_NOW",
                "confidence": 0.9, "thesis_strength": 0.9, "setup_quality": "COMPELLING",
                "position_metrics": {"current_price": 195000.0},
                "data_health": {"price_reference": {
                    "price": 140.0, "currency": "USD", "basis": "unadjusted",
                    "source": "kis.overseas_time_itemchartprice", "observed_at": now_ny.isoformat(),
                }},
            },
        ],
    })

    seen_prewire_status = []

    def check_prewire_commit(mode, market, side, ticker, qty, price, now):
        with sqlite3.connect((archive / "paper/autotrader.sqlite").as_uri() + "?mode=ro", uri=True) as reader:
            row = reader.execute("SELECT status FROM autotrader_order_intents WHERE ticker=?", (ticker,)).fetchone()
            seen_prewire_status.append(row[0] if row else None)
        return {"accepted": True, "order_no": "SHADOW-1", "fill_price": price}

    trader = PrismAutoTrader(
        archive, state,
        policy=AutotraderPolicy(mode="shadow", enabled=True),
        clock=lambda: now_ny,
        session_resolver=lambda market, now_local: {"is_open": True, "phase": "regular"},
        quote_loader=lambda market, ticker, now: 140.0 if ticker == "NVDA" else None,
        broker_executor=check_prewire_commit,
    )
    res = trader.tick_market("US")
    assert [e["ticker"] for e in res["entries_executed"]] == ["NVDA"]
    assert seen_prewire_status == ["SUBMITTING"]

    # Verify VTS private dashboard overlay reads {market}-vts-candidates.json without touching autotrader.sqlite
    atomic_write_json(state / "autotrader/us-vts-candidates.json", {
        "entries": {"LIN": {"reference_price": 527.46, "score": 8.1, "stop_loss": 500.26, "target_price": 590.0}}
    })
    dash = publish_autotrader_dashboard(archive, policy=AutotraderPolicy(mode="kis_vts"), state_dir=state)
    us_dash = json.loads(dash["us_json"].read_text(encoding="utf-8"))
    assert [row["ticker"] for row in us_dash["pending_entries"]] == ["LIN"]
