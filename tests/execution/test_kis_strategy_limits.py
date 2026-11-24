from dataclasses import asdict
from datetime import timedelta
from decimal import Decimal
import hashlib
import json

import pytest

from tradingagents.atomic_io import atomic_write_json
from tradingagents.execution import demo_runtime as runtime, demo_token_cache, kis_demo_us
from tradingagents.execution.kis_demo import DemoCredentials, KisDemoClient, RequestPacer
from tradingagents.execution.kis_demo_us import KisDemoUSClient
from tradingagents.execution.kis_strategy_limits import (APPROVED_LIMIT_REVISION, approved_limits, configured_limits,
                                                         size_with_native_limits)
from tradingagents.execution.kis_strategy_v2 import EVIDENCE_SCHEMA, SETTLEMENT_SCHEMA, _buy_observation, current_v2_order_receipt
from tradingagents.execution.paper_policy_v2 import SCHEMA as POLICY_SCHEMA
from tests.execution.test_demo_runtime import Harness


def configure(root, market, **limits):
    path = root / "enabled.json"
    original = json.loads(path.read_text(encoding="utf-8"))
    atomic_write_json(path, {**original, "native_order_limits": {market: limits}})


def approved_config(config):
    return {**config, "native_limit_revision": APPROVED_LIMIT_REVISION,
            "native_order_limits": {market: asdict(limits) for market, limits in approved_limits().items()}}


@pytest.mark.parametrize("change", [{"mode": "KIS_LIVE"}, {"real_orders_enabled": True},
                                    {"native_limit_revision": None}, {"native_order_limits": {}}])
def test_rejects_out_of_scope_approved_configuration(change):
    config = approved_config({"mode": runtime.MODE, "real_orders_enabled": False})
    assert configured_limits(config) == approved_limits()
    with pytest.raises(ValueError, match="exact scoped native policy"):
        configured_limits(config | change)


@pytest.mark.parametrize("market,price", [("KR", 150_000), ("US", 650)])
@pytest.mark.parametrize("case", ["ready", "nav", "cash", "concentration", "daily", "external_open"])
def test_approved_policy_preserves_existing_guarded_journal(tmp_path, monkeypatch, market, price, case):
    monkeypatch.setenv("TRADINGAGENTS_KIS_MARKET_CALENDAR_ENABLED", "false")
    h = Harness(tmp_path, market)
    # First establish the ordinary policy using the same local journal later read by the approved tick.
    state_path = h.root / f"{market.lower()}-strategy.sqlite"
    with h.factory(market, state_path, lambda: h.now, (h.ticker,), h.credentials.scope()) as broker:
        runtime.initialize(broker.db)
        baseline = broker.db.execute("SELECT policy FROM paper_policy").fetchone()[0]
    h.price = price
    h.source(qty=3 if case == "daily" else 1)
    config_path = h.root / "enabled.json"
    original = json.loads(config_path.read_bytes())
    atomic_write_json(config_path, approved_config(original))
    native_client = KisDemoClient if market == "KR" else KisDemoUSClient

    def client(credentials, utcnow):
        return native_client(credentials, session=h, pacer=RequestPacer(interval=0), utcnow=utcnow)

    if market == "KR":
        monkeypatch.setattr(runtime, "KisDemoClient", client)
        monkeypatch.setattr(DemoCredentials, "from_local_settings", classmethod(lambda cls: h.credentials))
    else:
        monkeypatch.setattr(kis_demo_us, "KisDemoUSClient", client)
        monkeypatch.setattr(kis_demo_us, "credentials_from_settings", lambda: h.credentials)
    monkeypatch.setattr(demo_token_cache, "cache_demo_authentication", lambda *_args, **_kwargs: None)
    if case == "external_open":
        field = "rmn_qty" if market == "KR" else "nccs_qty"
        monkeypatch.setattr(native_client, "orders", lambda _, date: [{field: "1", "ord_dt": date, "ord_tmd": "093000"}])

    def account(market, broker, terms, clock):
        out = h.account(market, broker, terms, clock)
        suffix = "krw" if market == "KR" else "usd"
        if case == "nav":
            out[f"nav_{suffix}"] = price * 5
        if case == "cash":
            out[f"cash_only_buying_power_{suffix}"] = price
        if case == "concentration":
            out["positions"][0][f"market_value_{suffix}"] = out[f"nav_{suffix}"] * .35
        return out

    def tick():
        return runtime.tick(h.archive, h.root, h.validation, clock=lambda: h.now, quote_loader=h.quote,
                            account_loader=account, gate=h.gate, tickers={market: (h.ticker,),
                            "KR" if market == "US" else "US": ()})

    receipt = tick()
    row = receipt["markets"][market]
    assert receipt["configured_native_limits"]["markets"][market] == asdict(approved_limits()[market])
    assert row.get("native_policy_journal_bound") is True, row
    if case == "ready":
        assert row["order_counts"]["ACKNOWLEDGED"] == 1 and len(h.orders) == 1
        tick()
        assert len(h.orders) == 1  # Restarted worker plus outstanding original cannot issue another write.
    else:
        assert not h.orders
        expected = {"nav": "NO_STRATEGY_QUANTITY_WITHIN_LIMITS", "cash": "NO_STRATEGY_QUANTITY_WITHIN_LIMITS",
                    "concentration": "KIS_POSITION_CONCENTRATION_LIMIT", "daily": "KIS_DAILY_BUY_RISK_LIMIT",
                    "external_open": "KIS_BROKER_OPEN_OR_UNVERIFIED_ORDERS"}
        assert expected[case] in row["blockers"]
    # Restoring the prior configuration retains the amendment and request evidence.
    atomic_write_json(config_path, original)
    with h.factory(market, state_path, lambda: h.now, (h.ticker,), h.credentials.scope()) as broker:
        assert broker.db.execute("SELECT policy FROM paper_policy").fetchone()[0] == baseline
        assert broker.db.execute("SELECT revision FROM paper_policy_revisions").fetchone()[0] == APPROVED_LIMIT_REVISION


@pytest.mark.parametrize("market,price", [("KR", 100_000), ("US", 100)])
def test_approved_nav_sizing_allows_exact_threshold_without_exceeding_it(market, price):
    suffix = "krw" if market == "KR" else "usd"
    unit_cost = price * Decimal("1.003")
    policy = approved_limits()[market]
    terms = {"side": "BUY", "quantity": 2, "limit_price": price}
    cash = {f"cash_{suffix}": 10_000_000}
    # 20% one-share boundary uses the fee-inclusive order value.
    assert size_with_native_limits(market, terms, cash | {f"nav_{suffix}": unit_cost * 5}, policy) == 1
    assert size_with_native_limits(market, terms, cash | {f"nav_{suffix}": unit_cost * 5 - 1}, policy) == 0
    at_two = {f"nav_{suffix}": price * Decimal("20.06")}
    assert size_with_native_limits(market, terms, cash | at_two, policy) == 2
    assert size_with_native_limits(market, {**terms, "side": "SELL", "quantity": 100}, {}, policy) == policy.max_order_native // price


def configure_v2(root, *, scope, ticker, now, target=.15, observed_at=None, wrong_benchmark=False):
    market, currency = ("KR", "KRW") if ticker.endswith((".KS", ".KQ")) else ("US", "USD")
    path = root / "enabled.json"
    original = json.loads(path.read_text(encoding="utf-8"))
    policy = {"schema": POLICY_SCHEMA, "version": "fixture-v2", "scope": scope, "broker": "kis_vts",
              "market": market, "currency": currency, "frozen_at": now.isoformat(),
              "cash_reserve_fraction": .1, "max_order_fraction": .02, "max_position_fraction": .25,
              "max_sale_fraction": .1, "fee_bps": 30, "drift_band_fraction": .01, "max_quote_age_seconds": 120}
    watchlist = {"version": "fixture-watchlist-v1", "market": market, "known_at": now.isoformat(), "tickers": [ticker]}
    atomic_write_json(path, {**original, "paper_policy_v2": {market: {"policy": policy, "watchlist": watchlist}}})
    clock = (observed_at or now).isoformat()
    receipt = root / f"{market.lower()}-v2-evidence.json"
    settlement = root / f"{market.lower()}-v2-settlement.json"
    benchmark = root / f"{market.lower()}-v2-benchmark.json"
    benchmark_row = {"market": market, "unit": "index_points", "level": 3000, "event_at": clock,
                     "observed_at": clock, "source": f"KIS_{market}_INDEX",
                     "symbol": "WRONG" if wrong_benchmark else "0001" if market == "KR" else "SPX"}
    atomic_write_json(settlement, {"schema": SETTLEMENT_SCHEMA, "account_scope": scope, "market": market,
        "currency": currency, "observed_at": clock, "settled_cash": 9_000_000})
    atomic_write_json(benchmark, benchmark_row)
    atomic_write_json(receipt, {"schema": EVIDENCE_SCHEMA, "market": market, "currency": currency,
        "account_scope": scope, "cash_basis": "REVIEWED_SETTLED_CASH", "orders_reconciled": True,
        "portfolio_complete": True, "observed_at": clock, "settlement_observed_at": clock,
        "portfolio_observed_at": clock, "settled_cash": 9_000_000,
        "settlement_source_sha256": hashlib.sha256(settlement.read_bytes()).hexdigest(),
        "benchmark_source_sha256": hashlib.sha256(benchmark.read_bytes()).hexdigest(), "benchmark": benchmark_row,
        "target_weights": {ticker: target}})
    return receipt


def test_reviewed_v2_receipt_requires_both_exact_source_documents(tmp_path):
    from datetime import datetime
    now = datetime.fromisoformat("2026-10-22T10:01:00+09:00")
    scope, ticker = "scoped-fixture", "005930.KS"
    atomic_write_json(tmp_path / "enabled.json", {})
    args = (tmp_path, "KR", "KRW", scope, ticker, now, 120, 10_000_000)
    receipt = configure_v2(tmp_path, scope=scope, ticker=ticker, now=now)
    assert _buy_observation(*args)[:2] == ("9000000", .15)
    settlement = tmp_path / "kr-v2-settlement.json"
    settlement.write_bytes(settlement.read_bytes() + b"\n")
    with pytest.raises(ValueError, match="bytes differ"):
        _buy_observation(*args)
    configure_v2(tmp_path, scope=scope, ticker=ticker, now=now)
    modified = json.loads(receipt.read_bytes()) | {"settled_cash": 9_100_000}
    atomic_write_json(receipt, modified)
    with pytest.raises(ValueError, match="does not match"):
        _buy_observation(*args)
    configure_v2(tmp_path, scope=scope, ticker=ticker, now=now)
    (tmp_path / "kr-v2-benchmark.json").unlink()
    with pytest.raises(FileNotFoundError):
        _buy_observation(*args)


@pytest.mark.parametrize("market,field", [("KR", "rmn_qty"), ("US", "nccs_qty")])
def test_broker_order_receipt_uses_native_session_and_explicit_remainder(tmp_path, market, field):
    h = Harness(tmp_path, market)
    requests = []

    class Client:
        credentials = h.credentials
        rows = [{field: "1", "ord_dt": h.now.strftime("%Y%m%d"), "ord_tmd": h.now.strftime("%H%M%S")}]

        def orders(self, date):
            requests.append(date)
            return self.rows

    client = Client()
    result = current_v2_order_receipt(market, client, clock=lambda: h.now)
    assert result["market"] == market and result["open_order_count"] == 1
    assert requests == [h.now.strftime("%Y%m%d")]
    client.rows = []
    assert current_v2_order_receipt(market, client, clock=lambda: h.now)["open_order_count"] == 0
    client.rows = [{}]
    with pytest.raises(ValueError, match="remainder"):
        current_v2_order_receipt(market, client, clock=lambda: h.now)


@pytest.mark.parametrize("change", [{"ord_dt": None}, {"ord_dt": "20990101"}, {"ord_dt": "20260230"},
                                    {"ord_tmd": None}, {"ord_tmd": "09000"}, {"ord_tmd": "240001"},
                                    {"ord_tmd": "151500"}])
def test_korean_receipt_rejects_unverifiable_order_times(tmp_path, change):
    h = Harness(tmp_path, "KR")

    class Client:
        credentials = h.credentials

        def orders(self, date):
            return [{"ord_dt": date, "ord_tmd": "090000", "rmn_qty": "0"} | change]

    with pytest.raises(ValueError, match="time"):
        current_v2_order_receipt("KR", Client(), clock=lambda: h.now)


def test_optional_v2_stops_on_broker_open_order_absent_from_strategy_journal(tmp_path, monkeypatch):
    h = Harness(tmp_path, "KR")
    configure(h.root, "KR", max_order_native=runtime.CAPS["KR"], cash_floor_native=0,
              max_order_nav=.1, one_share_nav_ceiling=.2)
    configure_v2(h.root, scope=h.credentials.scope(), ticker=h.ticker, now=h.now)
    monkeypatch.setattr(KisDemoClient, "orders", lambda _, date: [{"rmn_qty": "1", "ord_dt": date, "ord_tmd": "090000"}])
    row = h.tick()
    assert not row["orders"] and not h.orders
    assert "KIS_V2_ADMISSION_UNVERIFIED" in row["blockers"]


@pytest.mark.parametrize("market", ["KR", "US"])
@pytest.mark.parametrize("case", ["floor", "nav", "one_share"])
def test_normal_kis_strategy_enforces_configured_native_limits(tmp_path, monkeypatch, market, case):
    monkeypatch.setenv("TRADINGAGENTS_KIS_MARKET_CALENDAR_ENABLED", "false")
    case_account = Harness(tmp_path, market)
    native_client = KisDemoClient if market == "KR" else KisDemoUSClient

    def client(credentials, utcnow):
        return native_client(credentials, session=case_account, pacer=RequestPacer(interval=0), utcnow=utcnow)

    if market == "KR":
        monkeypatch.setattr(runtime, "KisDemoClient", client)
        monkeypatch.setattr(DemoCredentials, "from_local_settings", classmethod(lambda cls: case_account.credentials))
    else:
        monkeypatch.setattr(kis_demo_us, "KisDemoUSClient", client)
        monkeypatch.setattr(kis_demo_us, "credentials_from_settings", lambda: case_account.credentials)
    monkeypatch.setattr(demo_token_cache, "cache_demo_authentication", lambda *_args, **_kwargs: None)
    price_fraction = case_account.price / 10_000_000
    configure(case_account.root, market, max_order_native=runtime.CAPS[market],
              cash_floor_native=9_000_000 if case == "floor" else 1,
              max_order_nav=price_fraction * .75,
              one_share_nav_ceiling=price_fraction * 1.25 if case != "nav" else 0)
    markets = runtime.tick(case_account.archive, case_account.root, case_account.validation,
        clock=lambda: case_account.now, quote_loader=case_account.quote, account_loader=case_account.account,
        gate=case_account.gate, tickers={market: (case_account.ticker,), "KR" if market == "US" else "US": ()})["markets"]
    result = markets[market]
    if case == "one_share":
        order, = result["orders"]
        assert order["quantity"] == 1 and order["status"] == "ACKNOWLEDGED"
    else:
        assert not result["orders"] and not case_account.orders
        assert result["blockers"] == ["NO_STRATEGY_QUANTITY_WITHIN_LIMITS"]


@pytest.mark.parametrize("market", ["KR", "US"])
def test_native_override_rejects_cap_increase_and_keeps_sell_authority(market):
    raw = {"max_order_native": runtime.CAPS[market], "cash_floor_native": 999_999_999,
           "max_order_nav": .01, "one_share_nav_ceiling": .02}
    with pytest.raises(ValueError, match="hard cap"):
        configured_limits({"native_order_limits": {market: {**raw, "max_order_native": runtime.CAPS[market] + 1}}})
    limits = configured_limits({"native_order_limits": {market: raw}})[market]
    assert size_with_native_limits(market, {"side": "SELL", "limit_price": runtime.CAPS[market], "quantity": 1}, {}, limits) == 1


def test_native_one_share_exception_only_reduces_a_valid_multi_share_request():
    limits = configured_limits({"native_order_limits": {"KR": {"max_order_native": 100000,
        "cash_floor_native": 100000, "max_order_nav": .03, "one_share_nav_ceiling": .05}}})["KR"]
    terms = {"side": "BUY", "limit_price": 40000, "quantity": 2}
    account = {"nav_krw": 1_000_000, "cash_krw": 200000}
    assert size_with_native_limits("KR", terms, account, limits) == 1
    assert size_with_native_limits("KR", terms, {**account, "cash_krw": 140000}, limits) == 0


@pytest.mark.parametrize("case", ["stale", "wait", "within_band", "wrong_benchmark", "ready", "cash_unknown_after_buy"])
def test_standard_strategy_uses_v2_only_after_scoped_evidence(tmp_path, case):
    h = Harness(tmp_path, "KR")
    configure(h.root, "KR", max_order_native=runtime.CAPS["KR"], cash_floor_native=2000000,
              max_order_nav=.006, one_share_nav_ceiling=.008)
    receipt = configure_v2(h.root, scope=h.credentials.scope(), ticker=h.ticker, now=h.now,
                           target=.001 if case == "within_band" else .15,
                           observed_at=h.now - timedelta(minutes=3) if case == "stale" else None,
                           wrong_benchmark=case == "wrong_benchmark")
    if case == "wait":
        h.source(action="WAIT")
    result = h.tick()
    if case in {"stale", "wait", "within_band", "wrong_benchmark"}:
        assert not result["orders"] and not h.orders
        if case != "wait":
            assert "KIS_V2_ADMISSION_UNVERIFIED" in result["blockers"]
        return
    assert result["orders"][0]["status"] == "ACKNOWLEDGED"
    assert result["orders"][0]["quantity"] == 1
    if case == "cash_unknown_after_buy":
        h.fill()
        h.now += timedelta(seconds=7)
        assert h.tick()["owned"][h.ticker] == 1
        receipt.unlink()
        h.now += timedelta(seconds=5)
        h.source("fixture-2", action="EXIT_NOW")
        result = h.tick()
        assert result["orders"][-1]["side"] == "SELL" and result["orders"][-1]["quantity"] == 1
