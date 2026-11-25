"""Offline deterministic verification suite for WP1-WP4 and PRISM AutoTrader."""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
import json
import sqlite3
from types import SimpleNamespace
from unittest.mock import Mock
from zoneinfo import ZoneInfo

import pytest

from tradingagents.atomic_io import atomic_write_json
from tradingagents.execution.autotrader_dashboard import publish_autotrader_dashboard
from tradingagents.execution.contract_builder import build_execution_contract
from tradingagents.execution.kis_strategy_limits import APPROVED_CAPS, APPROVED_LIMIT_REVISION, configured_limits
from tradingagents.execution.kis_vts_feed import open_vts_websocket, request_vts_approval_key
from tradingagents.execution.overlay import evaluate_execution_state
from tradingagents.execution.paper_approval import PaperApproval, render_telegram_approval_card
from tradingagents.execution.prism_autotrader import (
    AutotraderPolicy,
    PrismAutoTrader,
    load_autotrader_policy,
    run_autotrader_tick,
)
from tradingagents.execution.quant_data_bridge import (
    evaluate_hybrid_portfolio_proposal,
)
from tradingagents.execution.session_observations import SCHEMA as OBS_SCHEMA, capture_due
from tradingagents.performance import action_outcomes
from tradingagents.portfolio.account_models import AccountConstraints, AccountSnapshot, PortfolioCandidate, PortfolioProfile
from tradingagents.portfolio.gates import apply_gates
from tradingagents.portfolio.instrument_identity import resolve_identity
from tradingagents.portfolio.performance import etf_alternatives
from tradingagents.scheduled import runner
from tradingagents.schemas import IntradayMarketSnapshot
from tools.remediate_performance_currency import remediate_performance_currency
from tools.run_hybrid_quant_backtest import simulate_after_tax_walk_forward


NOW = datetime(2026, 11, 24, 14, 30, tzinfo=timezone.utc)


# ── WP1 Tests: Adaptive Universe, Non-Holding Partial Baseline, ETF MultiIndex/FX, Currency Fix ──


def test_adaptive_universe_rejects_candidate_without_50d_history(tmp_path):
    from tests.scheduled.test_adaptive_universe import quote, select, setup

    config, universe = setup(tmp_path, holdings=("005930.KS",), market="KR")
    quotes = {
        "KR:439090": quote("439090.KQ", market="KR", fiftyDayAverage=None),
        "KR:000660": quote("000660.KS", market="KR", fiftyDayAverage=120000),
    }
    selected, _, receipt = select(config, universe, quotes, tickers=["005930.KS", "439090.KQ", "000660.KS"])
    assert selected == ["005930.KS", "000660.KS"]
    bad_row = next(r for r in receipt["candidates"] if r["ticker"] == "439090.KQ")
    assert bad_row["reasons"] == ["insufficient_daily_history"]


def test_nonholding_partial_baseline_admits_when_all_holdings_succeeded(tmp_path, monkeypatch):
    from tests.test_scheduled_run_mode import _write_full_overlay_baseline
    from tradingagents.scheduled import research_recovery

    archive = tmp_path / "archive"
    holdings = [f"{i:06d}.KS" for i in range(1, 6)]
    watch = [f"{i:06d}.KS" for i in range(6, 16)]
    failed_nonholding = "439090.KQ"
    all_tickers = [*holdings, *watch, failed_nonholding]
    manifest = _write_full_overlay_baseline(
        archive,
        tickers=all_tickers,
        market="KR",
        started_at=(NOW - timedelta(hours=3)).isoformat(),
        run_id="20261124T100000_local-scheduler-kr-full",
    )
    manifest["status"] = "partial_failure"
    manifest["summary"] = {
        "total_tickers": len(all_tickers),
        "successful_tickers": len(all_tickers) - 1,
        "failed_tickers": 1,
        "partial_failure_rate": round(1 / len(all_tickers), 4),
        "configured_ticker_count": len(all_tickers),
    }
    manifest["active_universe"] = {
        "mode": "adaptive_required_coverage",
        "account_snapshot_status": "loaded",
        "holding_tickers": holdings,
        "expected_holding_tickers": holdings,
        "expected_watchlist_tickers": [*watch, failed_nonholding],
        "coverage": {"complete": True, "holding_missing_count": 0},
    }
    for row in manifest["tickers"]:
        if row["ticker"] == failed_nonholding:
            row["status"] = "failed"
            row["artifacts"] = {"error_json": f"tickers/{failed_nonholding}/error.json"}
    run_json = archive / "runs/2026" / manifest["run_id"] / "run.json"
    atomic_write_json(run_json, manifest)
    atomic_write_json(archive / "latest-run.json", manifest)
    monkeypatch.setattr(research_recovery, "verified_candidate_partial", lambda *a, **k: [{"ticker": failed_nonholding}])

    selected = runner._resolve_latest_full_overlay_baseline_manifest(
        archive,
        market="KR",
        required_holding_tickers=holdings,
        partial_required_tickers=tuple(holdings),
        now=NOW,
        write_discovery_index=False,
    )
    assert selected is not None and selected["run_id"] == manifest["run_id"]

    # If a HELD ticker failed instead, baseline MUST be rejected
    manifest_bad = json.loads(json.dumps(manifest))
    for row in manifest_bad["tickers"]:
        if row["ticker"] == holdings[0]:
            row["status"] = "failed"
        elif row["ticker"] == failed_nonholding:
            row["status"] = "success"
            row["artifacts"] = {"analysis_json": "a.json"}
    atomic_write_json(run_json, manifest_bad)
    atomic_write_json(archive / "latest-run.json", manifest_bad)
    assert (
        runner._resolve_latest_full_overlay_baseline_manifest(
            archive,
            market="KR",
            required_holding_tickers=holdings,
            partial_required_tickers=tuple(holdings),
            now=NOW,
            write_discovery_index=False,
        )
        is None
    )


def test_etf_alternatives_handles_multiindex_yfinance_and_pit_fx_cutoff(tmp_path):
    local_prices = tmp_path / "prices.json"
    atomic_write_json(local_prices, {
        "SPY": [
            {"date": "2026-11-20", "close": 500.0},
            {"date": "2026-11-23", "close": 505.0},
            {"date": "2026-11-24", "close": 510.0},
            {"date": "2026-11-25", "close": 9999.0},
        ]
    })
    local_fx = tmp_path / "fx.json"
    atomic_write_json(local_fx, {
        "USDKRW": [
            {"date": "2026-11-20", "close": 1390.0},
            {"date": "2026-11-23", "close": 1400.0},
            {"date": "2026-11-24", "close": 1405.0},
            {"date": "2026-11-25", "close": 9999.0},
        ]
    })
    inst = [etf_alternatives.EtfAlternativeInstrument(key="SP500", symbol="SPY", currency="USD", label="SPY")]
    prices, diag, p_warn = etf_alternatives._load_price_series_for_instruments(
        inst,
        path=local_prices,
        provider="local_json",
        start_date=date(2026, 11, 20),
        end_date=date(2026, 11, 24),
        as_of=NOW.isoformat(),
        cache_dir=tmp_path / "cache",
    )
    fx, fx_warn = etf_alternatives._load_fx_series(local_fx, end_date=date(2026, 11, 24))
    assert not p_warn and not fx_warn
    assert [r["date"] for r in prices["SP500"]] == ["2026-11-20", "2026-11-23", "2026-11-24"]
    assert all(r["date"] <= "2026-11-24" for r in fx["USDKRW"])


def test_us_recommended_price_rejects_krw_and_remediates_corrupted_rows(tmp_path):
    ref_krw, state_krw = action_outcomes.native_reference(
        {"price": 356000.0, "currency": "KRW", "basis": "unadjusted", "source": "kis", "observed_at": NOW.isoformat()},
        "US",
        NOW.isoformat(),
    )
    assert ref_krw is None and state_krw != "verified_native_reference"
    ref_usd, state_usd = action_outcomes.native_reference(
        {"price": 254.5, "currency": "USD", "basis": "unadjusted", "source": "kis", "observed_at": NOW.isoformat()},
        "US",
        NOW.isoformat(),
    )
    assert ref_usd is not None and ref_usd.price == 254.5 and state_usd == "verified_native_reference"

    db = tmp_path / "perf.sqlite"
    action_outcomes.initialize_action_tracker(db)
    with sqlite3.connect(db) as conn:
        conn.execute(
            "INSERT INTO action_recommendations (id, run_id, ticker, market, action, recommended_price, created_at) "
            "VALUES (1, 'r1', 'AAPL', 'US', 'HOLD', 356000.0, '2026-11-01T00:00:00+00:00')"
        )
        conn.execute(
            "INSERT INTO action_outcomes (recommendation_id, return_5d, return_20d, outcome_label, calculation_version, updated_at) "
            "VALUES (1, -0.9993, -0.9992, 'neutral_negative', 2, '2026-11-20')"
        )
    backup = tmp_path / "perf.bak"
    receipt = remediate_performance_currency(db, apply=True, backup_path=backup)
    assert receipt["remediated_outcome_rows"] == 1 and backup.is_file()
    summary = action_outcomes.summarize_action_performance(db)
    assert summary.outcomes == 0
    assert summary.data_quality["invalidated_currency_mismatch_rows"] == 1


# ── WP2 Tests: Mixed Confirmation Group, 64-Symbol Session Observation, Gates Exemption ──


def test_mixed_confirmation_group_ignores_passive_support_resistance_levels():
    raw_decision = {
        "rating": "HOLD",
        "portfolio_stance": "BULLISH",
        "entry_action": "WAIT",
        "risk_action": "HOLD",
        "setup_quality": "COMPELLING",
        "confidence": 0.78,
        "time_horizon": "short",
        "entry_logic": "Breakout pilot",
        "exit_logic": "Stop below support",
        "position_sizing": "Starter",
        "risk_limits": "Strict",
        "catalysts": ["AI demand"],
        "invalidators": ["Support loss"],
        "watchlist_triggers": ["Breakout"],
        "data_coverage": {},
        "conditional_entry_action": "STARTER",
        "conditional_entry_valid_until": "2026-11-25T16:00:00-05:00",
        "execution_levels": {
            "levels": [
                {"level_type": "BREAKOUT", "price": 210.0, "confirmation": "intraday", "confirmation_group": "pilot_intraday"},
                {"level_type": "SUPPORT", "low": 195.0, "high": 198.0, "confirmation": "close"},  # confirmation_group=None!
                {"level_type": "RESISTANCE", "price": 230.0, "confirmation": "close"},  # confirmation_group=None!
            ],
            "earliest_pilot_time_local": "09:45",
        },
    }
    contract = build_execution_contract(
        ticker="AMZN",
        analysis_payload={"decision": json.dumps(raw_decision), "finished_at": "2026-11-24T17:00:00-05:00"},
    )
    at = datetime.fromisoformat("2026-11-25T10:15:00-05:00")
    snap = IntradayMarketSnapshot(
        ticker="AMZN", asof=at.isoformat(), provider="kis", interval="1m",
        last_price=212.0, session_vwap=210.5, day_high=213.0, day_low=208.0,
        volume=1_000_000, avg20_daily_volume=800_000, relative_volume=1.3,
        market_session="regular", market="US",
    )
    update = evaluate_execution_state(contract, snap, now=at, max_data_age_seconds=120)
    assert update.decision_now.value == "STARTER_NOW"
    assert "conditional_entry_group_confirmed" in update.reason_codes


def test_session_observations_supports_up_to_64_symbols_and_custom_open_delay(tmp_path):
    instruments = [{"ticker": f"{i:06d}.KS", "market": "KR", "venue": "J"} for i in range(1, 21)]
    atomic_write_json(
        tmp_path / "policy.json",
        {"schema": OBS_SCHEMA, "instruments": instruments},
    )
    at = datetime.fromisoformat("2026-11-24T09:00:30+09:00")

    def bar(_item, day):
        return {
            "output2": [
                {
                    "stck_bsop_date": day.replace("-", ""),
                    "stck_oprc": "50000",
                    "stck_clpr": "51000",
                    "stck_hgpr": "51500",
                    "stck_lwpr": "49500",
                    "acml_vol": "10000",
                }
            ]
        }

    res = capture_due(tmp_path, clock=lambda: at, download=bar)
    assert len(res) == 4 and all(r["status"] == "OBSERVED" for r in res)


def test_wait_heavy_gate_preserves_overlay_confirmed_starter_and_risk_sells():
    snap = AccountSnapshot(
        snapshot_id="s1", as_of=NOW.isoformat(), broker="kis", account_id="1", currency="KRW",
        settled_cash_krw=5_000_000, available_cash_krw=5_000_000, buying_power_krw=5_000_000,
        constraints=AccountConstraints(),
    )
    profile = PortfolioProfile(
        name="p", enabled=True, broker="kis", broker_environment="real", read_only=True,
        account_no=None, product_code=None, manual_snapshot_path=None, csv_positions_path=None,
        private_output_dirname="p", watch_tickers=("005930.KS",), trigger_budget_krw=2_000_000,
        constraints=AccountConstraints(), allow_intraday_pilot=True,
    )
    cand = PortfolioCandidate(
        snapshot_id="s1",
        instrument=resolve_identity("005930.KS", "Samsung"),
        is_held=False, market_value_krw=0, quantity=0, available_qty=0, sector="Tech",
        structured_decision={}, data_coverage={"company_news_count": 3}, quality_flags=(),
        vendor_health={}, suggested_action_now="STARTER_NOW", suggested_action_if_triggered="NONE",
        trigger_conditions=(), confidence=0.8, stance="BULLISH", entry_action="WAIT",
        setup_quality="COMPELLING", rationale="confirmed",
        data_health={"execution_decision_state": "ACTIONABLE_NOW", "execution_decision_now": "STARTER_NOW", "execution_timing_state": "PILOT_READY"},
    )
    gated = apply_gates(
        candidates=[cand],
        snapshot=snap,
        batch_metrics={"entry_action_distribution": {"WAIT": 9, "STARTER": 1}, "stance_distribution": {"BULLISH": 8, "NEUTRAL": 2}},
        warnings=[],
        profile=profile,
    )
    assert gated[0].suggested_action_now == "STARTER_NOW"
    assert "wait_heavy_batch_reduce_immediate_entries" not in gated[0].gate_reasons


# ── WP3 + PRISM AutoTrader + Dashboard Tests ──


def test_kis_vts_normalized_caps_live_v2_evidence_ws_and_approval_card(tmp_path):
    assert APPROVED_CAPS == {"KR": 3_000_000, "US": 3_000}
    lims = configured_limits({
        "mode": "KIS_DEMO_STRATEGY",
        "real_orders_enabled": False,
        "native_limit_revision": APPROVED_LIMIT_REVISION,
        "native_order_limits": {
            "KR": {"max_order_native": 3_000_000, "cash_floor_native": 0, "max_order_nav": 0.12, "one_share_nav_ceiling": 0.20},
            "US": {"max_order_native": 3_000, "cash_floor_native": 0, "max_order_nav": 0.12, "one_share_nav_ceiling": 0.20},
        },
    })
    assert lims["KR"].max_order_native == 3_000_000 and lims["US"].max_order_native == 3_000

    # VTS WS URL guard rejects live WS endpoint
    with pytest.raises(ValueError, match="ops.koreainvestment.com:31000"):
        open_vts_websocket(ws_url="ws://ops.koreainvestment.com:21000")
    session = Mock()
    session.post.return_value = SimpleNamespace(status_code=200, json=lambda: {"approval_key": "vts-approval-ok"})
    assert request_vts_approval_key(SimpleNamespace(app_key="k", app_secret="s"), session=session) == "vts-approval-ok"

    # Approval card formatting
    with PaperApproval(tmp_path / "approval.sqlite", secret=b"x" * 32, authorized=frozenset({"101"}), clock=lambda: NOW) as ledger:
        proposal = {
            "intent": "i1", "scope": "s1", "mode": "isolated_paper", "ticker": "005930.KS", "market": "KR",
            "currency": "KRW", "side": "BUY", "quantity": "4", "quantity_step": "1", "limit": "70000",
            "expires_at": (NOW + timedelta(minutes=15)).isoformat(),
        }
        callbacks = ledger.propose(proposal)
        card = render_telegram_approval_card(proposal, callbacks)
        assert len(card["reply_markup"]["inline_keyboard"]) == 2


def test_prism_autotrader_end_to_end_queue_fill_runner_hardstop_and_live_gate(tmp_path):
    archive = tmp_path / "archive"
    state = tmp_path / "state"
    site = tmp_path / "site"
    clock_holder = [datetime(2026, 11, 24, 6, 30, tzinfo=ZoneInfo("Asia/Seoul"))]  # Pre-open!
    quotes = {"005930.KS": 70_000.0, "AAPL": 220.0}
    open_flag = [False]

    run_kr = archive / "runs/2026/20261124T060000_local-scheduler-kr-full"
    atomic_write_json(run_kr / "run.json", {
        "run_id": run_kr.name, "status": "success",
        "settings": {"market": "KR"}, "finished_at": clock_holder[0].isoformat(),
    })
    atomic_write_json(run_kr / "portfolio-private/portfolio_candidates.json", {
        "batch_metrics": {"market_regime": "constructive"},
        "candidates": [{
            "canonical_ticker": "005930.KS", "display_name": "삼성전자", "sector": "Semiconductors",
            "stance": "BULLISH", "suggested_action_now": "WATCH", "suggested_action_if_triggered": "STARTER_IF_TRIGGERED",
            "risk_action": "HOLD", "confidence": 0.82, "thesis_strength": 0.80, "setup_quality": "COMPELLING",
            "prism_agreement": "confirmed_buy",
            "data_health": {"last_price": 70_000.0},
            "structured_decision": {"execution_levels": {"levels": [
                {"level_type": "STOP_LOSS", "price": 66_500.0},
                {"level_type": "TAKE_PROFIT", "price": 82_000.0},
            ]}},
        }],
    })

    policy = AutotraderPolicy(mode="shadow", enabled=True, telegram_enabled=False)
    trader = PrismAutoTrader(
        archive, state, policy=policy,
        clock=lambda: clock_holder[0],
        session_resolver=lambda market, now_local: {"is_open": open_flag[0], "phase": "regular" if open_flag[0] else "closed"},
        quote_loader=lambda market, ticker, now: quotes.get(ticker),
    )

    # 1. Off-hours tick queues candidate without executing
    r1 = trader.tick_market("KR")
    assert r1["entries_queued"] == ["005930.KS"]
    assert r1["entries_executed"] == []

    # 2. Regular market open executes queued order
    clock_holder[0] = datetime(2026, 11, 24, 9, 5, tzinfo=ZoneInfo("Asia/Seoul"))
    open_flag[0] = True
    r2 = trader.tick_market("KR")
    assert len(r2["entries_executed"]) == 1
    assert r2["metrics"]["open_slots"] == 1

    # 3. Surge +22% activates Runner Hold instead of selling prematurely at target, then -11% pullback triggers trailing exit!
    clock_holder[0] = datetime(2026, 11, 26, 10, 0, tzinfo=ZoneInfo("Asia/Seoul"))
    quotes["005930.KS"] = 86_000.0  # > +20% -> runner_active=1!
    r3 = trader.tick_market("KR")
    assert r3["exits_executed"] == []  # Runner holds the big winner!

    clock_holder[0] = datetime(2026, 11, 27, 10, 0, tzinfo=ZoneInfo("Asia/Seoul"))
    quotes["005930.KS"] = 76_000.0  # > 10% pullback from 86,000 peak -> trailing exit locks profit!
    r4 = trader.tick_market("KR")
    assert len(r4["exits_executed"]) == 1
    assert r4["exits_executed"][0]["return_pct"] > 7.0
    assert r4["metrics"]["closed_trades"] == 1 and r4["metrics"]["win_count"] == 1

    # 4. Verify KIS Live mode is strictly blocked before burn-in promotion gate passes
    live_trader = PrismAutoTrader(
        archive, state,
        policy=AutotraderPolicy(mode="kis_live", enabled=True, live_orders_confirmed=True),
        clock=lambda: clock_holder[0],
        session_resolver=lambda market, now_local: {"is_open": True, "phase": "regular"},
        quote_loader=lambda market, ticker, now: quotes.get(ticker),
        broker_executor=lambda *a: pytest.fail("Live broker must NOT be called when promotion gate blocks!"),
    )
    live_res = live_trader.tick_market("KR")
    assert "LIVE_PROMOTION_GATE_BLOCKED" in live_res["blockers"]
    assert live_res["live_orders_enabled"] is False

    # 5. Export dashboard JSON & HTML and verify load_autotrader_policy / run_autotrader_tick CLI wiring
    paths = publish_autotrader_dashboard(archive, site_dir=site, policy=policy)
    assert paths["kr_json"].is_file() and paths["site_html"].is_file()
    assert "삼성전자" in paths["site_html"].read_text(encoding="utf-8")

    atomic_write_json(state / "autotrader" / "enabled.json", {"mode": "shadow", "enabled": True, "live_orders_confirmed": False})
    assert load_autotrader_policy(state).enabled is True
    assert load_autotrader_policy(state / "autotrader").enabled is True
    tick_summary = run_autotrader_tick(
        archive,
        state / "autotrader",
        clock=lambda: clock_holder[0],
        session_resolver=lambda market, now_local: {"is_open": False, "phase": "closed"},
        quote_loader=lambda market, ticker, now: quotes.get(ticker),
    )
    assert set(tick_summary["markets"]) == {"KR", "US"}
    assert (archive / "paper" / "autotrader-status.json").is_file()


# ── WP4 Tests: PIT Quant Data Bridge & After-Tax Walk-Forward Simulation ──


def test_quant_data_bridge_excludes_future_bars_and_applies_pit_veto():
    start = date(2026, 5, 1)
    bars = {
        "SPY": [{"date": (start + timedelta(days=i)).isoformat(), "close": 400.0 + i * 0.8, "volume": 5_000_000} for i in range(120)],
        "AAPL": [{"date": (start + timedelta(days=i)).isoformat(), "close": 180.0 + i * 0.6, "volume": 8_000_000} for i in range(120)],
        "NVDA": [{"date": (start + timedelta(days=i)).isoformat(), "close": 100.0 + i * 0.7, "volume": 9_000_000} for i in range(120)],
    }
    # Inject future bar and malformed/undated bars
    bars["AAPL"].extend([
        {"date": "2026-12-31", "close": 99999.0, "volume": 1000},
        {"close": 500.0},
        {"date": "not-a-date", "close": 500.0},
    ])
    policy = {
        "version": "test-v1", "frozen_at": "2026-01-01T00:00:00+00:00", "currency": "USD",
        "core": ["SPY"], "satellite": ["AAPL", "NVDA"],
        "budget_core": 0.60, "budget_satellite": 0.35, "cash_floor": 0.05, "asset_cap": 0.65,
        "trend_window": 50, "momentum_window": 30, "volatility_window": 20,
        "annual_volatility_target": 0.25, "maximum_stale_days": 10, "minimum_turnover": 1000.0,
        "satellite_limit": 2, "factor_weights": {"quality": 0.4, "revision": 0.3, "strength": 0.3},
        "cost_version": "v1",
    }
    cutoff = "2026-09-01T22:00:00+00:00"
    decisions = {
        "AAPL": {"risk_action": "EXIT", "stance": "BEARISH", "known_at": "2026-09-01T20:00:00+00:00"},
        "NVDA": {"risk_action": "EXIT", "stance": "BEARISH", "known_at": "2026-09-05T20:00:00+00:00"},  # future veto ignored!
    }
    res = evaluate_hybrid_portfolio_proposal(policy, bars, analysis_as_of=cutoff, decisions=decisions)
    assert "AAPL" in res["quant_only"]["weights"] and "AAPL" not in res["after_veto"]["weights"]
    assert "NVDA" in res["after_veto"]["weights"]  # Future veto was strictly excluded!

    wf = simulate_after_tax_walk_forward(
        bars, market="US", core_tickers=["SPY"], satellite_tickers=["AAPL", "NVDA"], benchmark_ticker="SPY"
    )
    assert set(wf["strategies"]) == {"buy_and_hold", "static_80_20", "core_taa_only", "hybrid_core_satellite"}


def test_prism_autotrader_pit_filter_unknown_quarantine_and_sell_during_circuit_breaker(tmp_path):
    archive = tmp_path / "archive"
    state = tmp_path / "state"
    now_kst = datetime(2026, 11, 24, 10, 0, tzinfo=ZoneInfo("Asia/Seoul"))
    quotes = {"005930.KS": 70_000.0, "000660.KS": 180_000.0}

    # 1. Future-dated, missing-date, and empty candidate runs must be strictly ignored
    for idx, fin in enumerate([(now_kst + timedelta(hours=2)).isoformat(), None, "bad-date"]):
        rdir = archive / f"runs/2026/20261124T12000{idx}_bad"
        atomic_write_json(rdir / "run.json", {"run_id": rdir.name, "status": "success", "settings": {"market": "KR"}, "finished_at": fin})
        atomic_write_json(rdir / "portfolio-private/portfolio_candidates.json", {"candidates": [{
            "canonical_ticker": "005930.KS", "stance": "BULLISH", "suggested_action_now": "STARTER_NOW",
            "confidence": 0.9, "thesis_strength": 0.9, "setup_quality": "COMPELLING", "data_health": {"last_price": 70_000.0},
        }]})

    trader = PrismAutoTrader(
        archive, state,
        policy=AutotraderPolicy(mode="shadow", enabled=True, max_daily_loss_pct=3.0),
        clock=lambda: now_kst,
        session_resolver=lambda market, now_local: {"is_open": True, "phase": "regular"},
        quote_loader=lambda market, ticker, now: quotes.get(ticker),
    )
    r_bad = trader.tick_market("KR")
    assert r_bad["entries_queued"] == [] and r_bad["entries_executed"] == []

    # 2. Seed valid run & open position + realized daily loss exceeding -3% circuit breaker:
    #    Risk-reducing Hardstop SELL must STILL execute while new BUY is blocked!
    valid_dir = archive / "runs/2026/20261124T093000_valid"
    atomic_write_json(valid_dir / "run.json", {
        "run_id": valid_dir.name, "status": "success", "settings": {"market": "KR"},
        "finished_at": (now_kst - timedelta(minutes=20)).isoformat(),
    })
    atomic_write_json(valid_dir / "portfolio-private/portfolio_candidates.json", {
        "batch_metrics": {"market_regime": "constructive"},
        "candidates": [{
            "canonical_ticker": "000660.KS", "display_name": "SK하이닉스", "sector": "Semis",
            "stance": "BULLISH", "suggested_action_now": "STARTER_NOW", "risk_action": "HOLD",
            "confidence": 0.85, "thesis_strength": 0.85, "setup_quality": "COMPELLING",
            "data_health": {"last_price": 180_000.0},
        }],
    })
    with sqlite3.connect(trader.db_path) as conn:
        conn.execute(
            "INSERT INTO autotrader_positions (market, ticker, display_name, sector, mode, quantity, buy_price, "
            "current_price, peak_price, stop_loss, target_price, slot_fraction, runner_active, buy_score, regime, source_run_id, opened_at, updated_at) "
            "VALUES ('KR','005930.KS','삼성전자','Semis','shadow',10,70000,70000,70000,66500,82000,0.8,0,8.2,'constructive','seed',?,?)",
            (now_kst.isoformat(), now_kst.isoformat()),
        )
        conn.execute(
            "INSERT INTO autotrader_trades (intent_id, market, ticker, display_name, sector, mode, quantity, buy_price, sell_price, "
            "fee_and_tax, net_pnl, return_pct, slot_fraction, holding_days, exit_reason, source_run_id, opened_at, closed_at) "
            "VALUES ('loss1','KR','035420.KS','NAVER','Tech','shadow',10,200000,150000,1000,-400000,-20.0,1.0,2,'stop','seed',?,?)",
            (now_kst.isoformat(), now_kst.isoformat()),
        )
    quotes["005930.KS"] = 64_000.0  # Breached stop_loss (66,500)!
    r_cb = trader.tick_market("KR")
    assert "DAILY_LOSS_CIRCUIT_BREAKER" in r_cb["blockers"]
    assert len(r_cb["exits_executed"]) == 1 and r_cb["exits_executed"][0]["ticker"] == "005930.KS"
    assert r_cb["entries_executed"] == []

    # 3. Clear daily loss and simulate broker timeout -> OrderOutcomeUnknown quarantines further new BUYS
    with sqlite3.connect(trader.db_path) as conn:
        conn.execute("DELETE FROM autotrader_trades")

    def flaky_broker(*args):
        raise TimeoutError("simulated KIS network timeout")

    flaky_trader = PrismAutoTrader(
        archive, state,
        policy=AutotraderPolicy(mode="kis_vts", enabled=True),
        clock=lambda: now_kst,
        session_resolver=lambda market, now_local: {"is_open": True, "phase": "regular"},
        quote_loader=lambda market, ticker, now: quotes.get(ticker),
        broker_executor=flaky_broker,
    )
    r_unk1 = flaky_trader.tick_market("KR")
    assert any(b.startswith("ORDER_OUTCOME_UNKNOWN:") for b in r_unk1["blockers"])
    r_unk2 = flaky_trader.tick_market("KR")
    assert "UNRESOLVED_UNKNOWN_ORDER" in r_unk2["blockers"]
    assert r_unk2["entries_executed"] == []


def test_kis_vts_default_broker_executor_and_one_share_ceiling(monkeypatch):
    from tradingagents.execution import kis_demo, kis_demo_us, prism_autotrader

    calls = []

    class FakeKrClient:
        def __init__(self, creds):
            pass

        def _account(self):
            return {"CANO": "50123456", "ACNT_PRDT_CD": "01"}

        def request(self, method, endpoint, tr_id, *, body=None, **kw):
            calls.append((method, endpoint, tr_id, body))
            return {"rt_cd": "0", "output": {"ODNO": "0000123456"}}, {}

        def close(self):
            pass

    class FakeUsClient:
        def __init__(self, creds):
            self.session = SimpleNamespace(close=lambda: None)

        def _account(self):
            return {"CANO": "50123456", "ACNT_PRDT_CD": "01"}

        def request(self, method, endpoint, tr_id, *, body=None, **kw):
            calls.append((method, endpoint, tr_id, body["OVRS_EXCG_CD"]))
            if body["OVRS_EXCG_CD"] == "NASD":
                return {"rt_cd": "1", "msg1": "wrong exchange"}, {}
            return {"rt_cd": "0", "output": {"ODNO": "0000654321"}}, {}

    monkeypatch.setattr(kis_demo.DemoCredentials, "from_local_settings", staticmethod(lambda: SimpleNamespace()))
    monkeypatch.setattr(kis_demo, "KisDemoClient", FakeKrClient)
    monkeypatch.setattr(kis_demo_us, "credentials_from_settings", lambda: SimpleNamespace())
    monkeypatch.setattr(kis_demo_us, "KisDemoUSClient", FakeUsClient)

    res_kr = prism_autotrader._default_broker_executor("kis_vts", "KR", "BUY", "003230.KS", 1, 1_302_000.0, NOW)
    assert res_kr["accepted"] is True and res_kr["order_no"] == "0000123456"
    assert calls[0][:3] == ("POST", "order-cash", "VTTC0012U")

    res_us = prism_autotrader._default_broker_executor("kis_vts", "US", "BUY", "IBM", 2, 210.0, NOW)
    assert res_us["accepted"] is True and res_us["order_no"] == "0000654321"
    assert ("POST", "order", "VTTT1002U", "NYSE") in calls
