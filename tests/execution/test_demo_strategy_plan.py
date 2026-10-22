from datetime import timedelta
import json
import sqlite3

import pytest

from tradingagents.atomic_io import atomic_write_json
from tradingagents.execution import demo_runtime, demo_strategy_plan as planner, demo_validation
from tests.execution.test_demo_runtime import Harness


def native_source(h, name="fixture-1", action="STARTER_NOW", contract=None):
    run = h.source(name, action=action)
    bundle = json.loads((run / "decision_bundle_v2.json").read_text())
    bundle["market"] = h.market  # Published bundles use uppercase; run settings may not.
    atomic_write_json(run / "decision_bundle_v2.json", bundle)
    stamp = (h.now - timedelta(seconds=5)).isoformat()
    contract = contract or {"ticker": h.ticker, "analysis_asof": (h.now - timedelta(hours=1)).isoformat(),
        "action_if_triggered": "STARTER", "entry_valid_until": (h.now + timedelta(hours=2)).isoformat(),
        "invalid_if_intraday_below": h.price * .98}
    atomic_write_json(run / "tickers" / h.ticker / "execution_contract.json", contract)
    atomic_write_json(run / "tickers" / h.ticker / "execution_update.json", {
        "ticker": h.ticker, "analysis_asof": contract["analysis_asof"], "market_data_asof": stamp,
        "execution_asof": stamp, "decision_now": action})
    atomic_write_json(run / "portfolio-private/portfolio_candidates.json", {"candidates": [{
        "instrument": {"canonical_ticker": h.ticker}, "structured_decision": {"entry_action": "WAIT",
            "conditional_entry_action": "STARTER", "conditional_entry_valid_until": contract["entry_valid_until"]},
        "review_required": False, "gate_reasons": [], "data_coverage": {"company_news_count": 2},
        "vendor_health": {"fallback_count": 0}, "data_health": {}}]})
    # The reporting account has no usable budget. Never fabricate money in it.
    atomic_write_json(run / "portfolio-private/proposed_orders.json", {"orders": []})
    atomic_write_json(h.root / "enabled.json", {"mode": demo_runtime.MODE, "enabled": True,
        "real_orders_enabled": False, "allocation_mode": planner.MODE})
    return run, contract


@pytest.mark.parametrize("market", ["KR", "US"])
def test_recovered_core_requests_enable_only_new_original_approved_research(tmp_path, market):
    from tests.test_research_evidence import receipt
    from tradingagents.dataflows.research_evidence import assess_tool_evidence
    h = Harness(tmp_path, market)
    run, contract = native_source(h)
    finished = contract["analysis_asof"]
    started = (h.now - timedelta(hours=1, minutes=5)).isoformat()
    telemetry = receipt()
    for outcome in telemetry["request_outcomes"]:
        outcome.update(started_at=started, completed_at=finished)
    evidence = assess_tool_evidence(telemetry, started_at=started, finished_at=finished)
    assert evidence["status"] == "COMPLETE"
    analysis = {"ticker": h.ticker, "started_at": started, "finished_at": finished, "tool_telemetry": telemetry}
    atomic_write_json(run / "tickers" / h.ticker / "analysis.json", analysis)
    path = run / "portfolio-private/portfolio_candidates.json"
    research = json.loads(path.read_text())
    row = research["candidates"][0]
    row["vendor_health"].update(fallback_count=20, request_evidence=evidence)
    atomic_write_json(path, research)
    orders, _ = planner.plan(run, market, h.now, (h.ticker,), {})
    assert len(orders) == 1 and h.calls == []
    # A cached COMPLETE summary cannot clear the real original's evidence.
    analysis["tool_telemetry"] = {"fallback_count": 20, "events": []}
    atomic_write_json(run / "tickers" / h.ticker / "analysis.json", analysis)
    assert planner.plan(run, market, h.now, (h.ticker,), {})[0] == []


def test_complete_data_never_promotes_original_wait_to_buy(tmp_path):
    from tests.test_research_evidence import receipt
    from tradingagents.dataflows.research_evidence import assess_tool_evidence
    h = Harness(tmp_path, "US")
    run, contract = native_source(h)
    finished, started = contract["analysis_asof"], (h.now - timedelta(hours=1, minutes=5)).isoformat()
    telemetry = receipt()
    for outcome in telemetry["request_outcomes"]:
        outcome.update(started_at=started, completed_at=finished)
    evidence = assess_tool_evidence(telemetry, started_at=started, finished_at=finished)
    atomic_write_json(run / "tickers" / h.ticker / "analysis.json",
        {"ticker": h.ticker, "started_at": started, "finished_at": finished, "tool_telemetry": telemetry})
    path = run / "portfolio-private/portfolio_candidates.json"
    research = json.loads(path.read_text())
    research["candidates"][0]["vendor_health"].update(fallback_count=20, request_evidence=evidence)
    research["candidates"][0]["structured_decision"]["conditional_entry_action"] = "NONE"
    atomic_write_json(path, research)
    assert planner.plan(run, "US", h.now, (h.ticker,), {})[0] == []
    assert h.calls == []


@pytest.mark.parametrize("market", ["KR", "US"])
def test_native_strategy_uses_demo_capacity_and_proves_two_distinct_fills(tmp_path, market):
    h = Harness(tmp_path, market)
    run, contract = native_source(h)
    first = h.tick()
    assert first["orders"][0]["status"] == "ACKNOWLEDGED"
    assert first["allocation_diagnostics"]["real_account_allocation_used"] is False
    assert first["performance"]["status"] == "NO_FILLS"
    assert json.loads((run / "portfolio-private/proposed_orders.json").read_text()) == {"orders": []}
    h.now += timedelta(seconds=20)
    h.fill(amount=h.price-1)
    assert h.tick()["orders"][0]["status"] == "FILLED"
    h.now += timedelta(seconds=20)
    native_source(h, "fixture-2", contract={**contract, "ingested_at": h.now.isoformat()})
    h.tick()
    assert len(h.orders) == 1  # A refreshed observation does not create another entry.
    native_source(h, "fixture-3", action="EXIT_NOW", contract=contract)
    assert h.tick()["orders"][-1]["quantity"] == 1
    h.now += timedelta(seconds=20)
    h.fill("2", amount=h.price+2)
    done = h.tick()
    assert done["owned"][h.ticker] == 0 and done["performance"]["gross_pnl"] == 3
    with sqlite3.connect(h.root / f"{market.lower()}-strategy.sqlite") as db:
        assert db.execute("SELECT COUNT(*) FROM strategy_source_evidence").fetchone()[0] == 2
        with pytest.raises(sqlite3.IntegrityError, match="immutable"):
            db.execute("UPDATE strategy_source_evidence SET evidence='{}'")
    native_source(h, "fixture-4", contract=contract)
    h.tick()
    assert len(h.orders) == 2  # Same thesis cannot restart after the exit.


@pytest.mark.parametrize("change", ["wait", "no_approval", "review", "fallback", "missing_news", "future",
    "stale", "undated", "bad_date", "expired", "mismatch", "future_update", "future_contract", "missing_contract"])
def test_native_plan_rejects_missing_unapproved_and_invalid_evidence(tmp_path, change):
    h = Harness(tmp_path, "US")
    run, contract = native_source(h)
    bundle_path = run / "decision_bundle_v2.json"
    bundle = json.loads(bundle_path.read_text())
    research_path = run / "portfolio-private/portfolio_candidates.json"
    research = json.loads(research_path.read_text())
    row = research["candidates"][0]
    if change == "wait":
        bundle["strategy_table"][0]["raw_codes"]["decision_now"] = "NONE"
    if change == "no_approval":
        row["structured_decision"]["conditional_entry_action"] = "NONE"
    if change == "review":
        row["review_required"] = True
    if change == "fallback":
        row["vendor_health"]["fallback_count"] = 3
    if change == "missing_news":
        row["data_coverage"] = {}
    if change in {"future", "stale", "undated", "bad_date"}:
        value = {"future": (h.now+timedelta(seconds=1)).isoformat(), "stale": (h.now-timedelta(seconds=121)).isoformat(),
                 "undated": None, "bad_date": "2026-02-30T12:00:00Z"}[change]
        bundle["strategy_table"][0]["market_data_asof"] = value
    if change == "expired":
        contract["entry_valid_until"] = (h.now-timedelta(seconds=1)).isoformat()
        row["structured_decision"]["conditional_entry_valid_until"] = contract["entry_valid_until"]
    if change == "future_contract":
        contract["analysis_asof"] = (h.now+timedelta(seconds=1)).isoformat()
    update_path = run / "tickers" / h.ticker / "execution_update.json"
    update = json.loads(update_path.read_text())
    if change == "mismatch":
        update["decision_now"] = "NONE"
    if change == "future_update":
        update["execution_asof"] = (h.now+timedelta(seconds=1)).isoformat()
    atomic_write_json(update_path, update)
    atomic_write_json(bundle_path, bundle)
    atomic_write_json(research_path, research)
    contract_path = run / "tickers" / h.ticker / "execution_contract.json"
    atomic_write_json(contract_path, contract)
    if change == "missing_contract":
        contract_path.unlink()
    orders, diagnostics = planner.plan(run, "US", h.now, (h.ticker,), {})
    assert orders == [] and sum(diagnostics["reason_counts"].values()) == 1
    assert h.calls == []


def test_native_sell_does_not_adopt_probe_or_manual_holdings(tmp_path):
    h = Harness(tmp_path, "US")
    native_source(h, action="EXIT_NOW")
    row = h.tick()
    assert row["allocation_diagnostics"]["reason_counts"] == {"NO_STRATEGY_OWNED_POSITION": 1}
    assert not h.orders


def test_native_does_not_require_reporting_account_allocation_artifact(tmp_path):
    h = Harness(tmp_path, "US")
    run, _ = native_source(h)
    (run / "portfolio-private/proposed_orders.json").unlink()
    (run / "portfolio-private/account_snapshot.json").unlink()
    row = h.tick()
    assert row["orders"][0]["status"] == "ACKNOWLEDGED"
    assert row["source_diagnostics"]["allocated_orders"] is None


@pytest.mark.parametrize("case", ["empty", "duplicate", "future_run", "undated_run"])
def test_source_manifest_and_cardinality_are_verified(tmp_path, case):
    h = Harness(tmp_path, "US")
    run, _ = native_source(h)
    bundle = json.loads((run / "decision_bundle_v2.json").read_text())
    manifest = json.loads((run / "run.json").read_text())
    if case == "empty":
        bundle["strategy_table"] = []
    if case == "duplicate":
        bundle["strategy_table"] *= 2
    if case == "future_run":
        manifest["finished_at"] = (h.now + timedelta(seconds=1)).isoformat()
    if case == "undated_run":
        manifest["finished_at"] = None
    atomic_write_json(run / "decision_bundle_v2.json", bundle)
    atomic_write_json(run / "run.json", manifest)
    if case == "empty":
        orders, diag = planner.plan(run, "US", h.now, (h.ticker,), {})
        assert orders == [] and diag["eligible_candidates"] == 0
    else:
        with pytest.raises((ValueError, TypeError)):
            planner.plan(run, "US", h.now, (h.ticker,), {})
    assert not h.calls


@pytest.mark.parametrize("market", ["KR", "US"])
def test_native_quantity_keeps_order_cap_and_demo_cash_checks(tmp_path, market):
    h = Harness(tmp_path, market)
    native_source(h)
    def no_cash(*args):
        account = h.account(*args)
        account[f"cash_only_buying_power_{'krw' if market == 'KR' else 'usd'}"] = 0
        return account
    assert "NO_STRATEGY_QUANTITY_WITHIN_LIMITS" in h.tick(account_loader=no_cash)["blockers"]
    assert not h.orders
    h.price = demo_runtime.CAPS[market] + 1
    assert "NO_STRATEGY_QUANTITY_WITHIN_LIMITS" in h.tick()["blockers"]
    assert not h.orders


def test_expiry_during_account_lookup_does_not_consume_strategy_intent(tmp_path):
    h = Harness(tmp_path, "US")
    native_source(h)
    def delayed_account(*args):
        h.now += timedelta(seconds=121)
        return h.account(*args)
    row = h.tick(account_loader=delayed_account)
    assert "STRATEGY_SIGNAL_EXPIRED_DURING_PREPARATION" in row["blockers"]
    assert not h.orders
    with sqlite3.connect(h.root / "us-strategy.sqlite") as db:
        assert db.execute("SELECT COUNT(*) FROM strategy_attempts").fetchone()[0] == 0


@pytest.mark.parametrize("case", ["clear", "halted", "missing", "bad_date", "future", "stale"])
def test_submission_halt_evidence_uses_original_verified_clock(monkeypatch, case):
    from tests.dataflows.test_us_halts import NOW, feed, status
    from tradingagents.dataflows.intraday import us_halts
    halt = status(feed())
    if case == "halted":
        halt.update(status="halted", is_clear=False)
    if case == "missing":
        halt.pop("published_at")
    if case == "bad_date":
        halt["published_at"] = "2026-02-30T00:00:00Z"
    if case == "future":
        halt["published_at"] = (NOW + timedelta(seconds=1)).isoformat()
    if case == "stale":
        halt["published_at"] = (NOW - timedelta(seconds=120)).isoformat()
    monkeypatch.setattr(demo_validation, "normalize_kis_bars", lambda *a, **k: [])
    monkeypatch.setattr(us_halts.current_halts, "fetch", lambda *a, **k: halt)
    if case == "clear":
        result = demo_validation.attach_us_halt_evidence({}, {"output2": []}, "AAPL", lambda: NOW)
        assert result["halt_status"]["published_at"] == halt["published_at"]
        assert result["luld_status"]["is_clear"] is True
        assert result["reg_sho_status"]["short_sale_status"] == "unknown"
    else:
        with pytest.raises(ValueError, match="US_TRADING_HALT_NOT_CLEAR"):
            demo_validation.attach_us_halt_evidence({}, {"output2": []}, "AAPL", lambda: NOW)
def test_strategy_quote_must_recheck_the_requested_symbols_halt(monkeypatch):
    from types import SimpleNamespace
    from tradingagents.portfolio.kis import KisClient
    h = SimpleNamespace(session=SimpleNamespace(close=lambda: None),
        overseas_time_itemchartprice=lambda *a, **k: {"output2": [{}]},
        overseas_asking_price=lambda *a, **k: {})
    monkeypatch.setattr(KisClient, "from_api_keys", lambda **_: h)
    monkeypatch.setattr(demo_validation, "normalize_validation_quote", lambda **_: {"last_price": 100})
    seen = []
    def halt(quote, chart, ticker, clock):
        seen.append(ticker)
        raise ValueError("US_TRADING_HALT_NOT_CLEAR")
    monkeypatch.setattr(demo_validation, "attach_us_halt_evidence", halt)
    with pytest.raises(ValueError, match="US_TRADING_HALT_NOT_CLEAR"):
        demo_runtime.current_quote("US", "MSFT", lambda: None)
    assert seen == ["MSFT"]
