from datetime import timedelta
import hashlib
import json

import pytest

from tradingagents.atomic_io import atomic_write_json
from tradingagents.execution import demo_runtime as runtime, demo_token_cache, kis_demo_us
from tradingagents.execution.kis_demo import DemoCredentials, KisDemoClient, RequestPacer
from tradingagents.execution.kis_demo_us import KisDemoUSClient
from tradingagents.execution.kis_strategy_limits import configured_limits, size_with_native_limits
from tradingagents.execution.kis_strategy_v2 import EVIDENCE_SCHEMA, SETTLEMENT_SCHEMA, _buy_observation
from tradingagents.execution.paper_policy_v2 import SCHEMA as POLICY_SCHEMA
from tests.execution.test_demo_runtime import Harness


def configure(root, market, **limits):
    path = root / "enabled.json"
    original = json.loads(path.read_text(encoding="utf-8"))
    atomic_write_json(path, {**original, "native_order_limits": {market: limits}})


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
