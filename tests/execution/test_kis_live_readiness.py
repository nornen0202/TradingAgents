from dataclasses import replace
from datetime import datetime, timedelta, timezone
import json

import pytest

from tradingagents.atomic_io import atomic_write_json
from tradingagents.execution.broker_adapter import Account, Intent
from tradingagents.execution.kis_live_readiness import MODE, SCHEMA, MarketUsage, preview
from tradingagents.portfolio.kis import REAL_BASE_URL
from tradingagents.scheduled.market_calendar import market_session_state


NOW = datetime(2026, 11, 24, 15, tzinfo=timezone.utc)


def fixture(tmp_path, market):
    state = tmp_path / "kis-live-readiness"
    ticker, venue, currency, limit = ("005930", "KRX", "KRW", "70000") if market == "KR" else ("AAPL", "NASD", "USD", "200.01")
    now = NOW.replace(hour=1) if market == "KR" else NOW
    scope = "fixture:" + "a" * 64
    config = {"schema": SCHEMA, "mode": MODE, "enabled": True, "environment": "real", "host": REAL_BASE_URL,
              "real_orders_enabled": False, "evidence_scope": "ISOLATED_FIXTURE", "market": market,
              "approved_at": (now - timedelta(minutes=3)).isoformat(), "expires_at": (now + timedelta(minutes=3)).isoformat(),
              "revoked": False, "account_scope": scope, "allowed_instruments": {ticker: venue},
              "max_order_native": "100000" if market == "KR" else "500", "max_daily_buy_native": "100000" if market == "KR" else "500",
              "max_daily_orders": 3}
    account = Account(scope, currency, now.isoformat(), "100000", {ticker: "1"})
    intent = Intent("fixture-intent", ticker, "BUY", "1", limit, currency, (now + timedelta(minutes=1)).isoformat())
    return state, config, intent, {"account": account, "usage": MarketUsage("2026-11-24", 0, "0", False),
        "quote": {"observed_at": now.isoformat(), "ticker": ticker, "exchange": venue, "currency": currency,
                  "execution_ready": True, "ask": limit, "bid": limit},
        "session": market_session_state(market=market, now_local=now), "now": now}


@pytest.mark.parametrize("market,side,tr_id", [("KR", "BUY", "TTTC0012U"), ("KR", "SELL", "TTTC0011U"),
                                              ("US", "BUY", "TTTT1002U"), ("US", "SELL", "TTTT1006U")])
def test_official_production_contract_with_fixture_only_account(tmp_path, market, side, tr_id):
    state, config, intent, args = fixture(tmp_path, market)
    atomic_write_json(state / "approval.json", config)
    result = preview(state, replace(intent, side=side), **args)
    assert result["status"] == "CONTRACT_READY" and result["live_order_requests"] == 0
    request = result["fixture_request"]
    assert request["host"] == "https://openapi.koreainvestment.com:9443" and request["method"] == "POST"
    assert request["tr_id"] == tr_id and request["body"]["ORD_DVSN"] == "00"
    assert request["body"]["CANO"] == "00000000"
    assert ("ORD_UNPR" if market == "KR" else "OVRS_ORD_UNPR") in request["body"]
    audits = [json.loads(p.read_text()) for p in (state / "audit").glob("*.json")]
    assert len(audits) == 1 and "fixture_request" not in audits[0] and config["account_scope"] not in str(audits)


@pytest.mark.parametrize("broken", ["no_approval", "mode", "enabled", "host", "scope", "expired", "revoked",
                                    "halt", "cash", "oversell", "pending", "closed", "stale", "daily_limit"])
def test_refuses_invalid_approval_and_pretrade_evidence(tmp_path, broken):
    state, config, intent, args = fixture(tmp_path, "US")
    edits = {"mode": {"mode": "KIS_DEMO"}, "enabled": {"enabled": False}, "revoked": {"revoked": True},
             "host": {"host": "https://openapivts.koreainvestment.com:29443"}, "expired": {"expires_at": NOW.isoformat()}}
    if broken != "no_approval":
        atomic_write_json(state / "approval.json", {**config, **edits.get(broken, {})})
    if broken == "halt":
        (state / "HALT").touch()
    if broken == "scope":
        args["account"] = replace(args["account"], scope="different-account")
    if broken == "cash":
        args["account"] = replace(args["account"], settled_cash="200.01")
    if broken == "oversell":
        intent = replace(intent, quantity="2", side="SELL")
    if broken == "pending":
        args["usage"] = replace(args["usage"], unresolved=True)
    if broken == "daily_limit":
        args["usage"] = replace(args["usage"], orders=3)
    if broken == "closed":
        args["session"]["is_open"] = False
    if broken == "stale":
        args["quote"]["observed_at"] = (NOW - timedelta(seconds=120)).isoformat()
    with pytest.raises(ValueError, match="LIVE_"):
        preview(state, intent, **args)
    audits = [json.loads(p.read_text()) for p in (state / "audit").glob("*.json")]
    assert len(audits) == 1 and audits[0]["status"] == "BLOCKED" and audits[0]["live_order_requests"] == 0
