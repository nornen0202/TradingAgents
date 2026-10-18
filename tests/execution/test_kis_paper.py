from datetime import datetime, timedelta
import json
from urllib.parse import urlsplit

import pytest
import requests
from requests.adapters import HTTPAdapter

from tradingagents.execution.kis_demo import DemoCredentials, DemoError, KisDemoClient, RequestPacer
from tradingagents.execution.kis_paper import KisPaperBroker, PaperOrderPolicy, import_demo_fill, read_paper_account


NOW = "2026-10-19T10:01:00+09:00"


class Response:
    def __init__(self, payload, code=200, headers=None):
        self.payload, self.status_code, self.headers = payload, code, headers or {}

    def json(self):
        return self.payload


class Session:
    def __init__(self, *responses):
        self.responses, self.calls = list(responses), []

    def request(self, method, url, **kwargs):
        self.calls.append((method, url, kwargs))
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response

    def close(self):
        pass


def ack(odno="123"):
    return Response({"rt_cd": "0", "output": {"ODNO": odno, "KRX_FWDG_ORD_ORGNO": "001"}})


def report(*, quantity=1, filled=0, remaining=1, **changes):
    return Response({"rt_cd": "0", "output1": [{"odno": "123", "ord_dt": "20261019", "ord_tmd": "100100",
        "pdno": "005930", "sll_buy_dvsn_cd": "02", "ord_unpr": "70000", "ord_qty": str(quantity),
        "tot_ccld_qty": str(filled), "rmn_qty": str(remaining), "cncl_yn": "N", **changes}]})


def make(tmp_path, *responses, enabled=True, policy=None, account_no="12345678"):
    moment = [datetime.fromisoformat(NOW)]
    session = Session(Response({"access_token": "fixture-token", "expires_in": 86400}), *responses)
    client = KisDemoClient(DemoCredentials("fixture-key", "fixture-secret", account_no, "01"), session=session,
        pacer=RequestPacer(interval=0), utcnow=lambda: moment[0])
    broker = KisPaperBroker(tmp_path / "vts.sqlite", client, policy or PaperOrderPolicy(("005930",)),
                            paper_enabled=enabled, clock=lambda: moment[0])
    return broker, client, session, moment


def order(broker, **changes):
    result = {"intent_id": "vts-intent-1", "ticker": "005930", "side": "BUY", "quantity": 1, "limit_price": 70000,
        "signal": {"signal_id": "signal:fixture-1", "ticker": "005930", "decision_now": "STARTER_NOW", "execution_ready": True,
            "available_at": "2026-10-19T10:00:50+09:00", "valid_until": "2026-10-19T10:02:30+09:00"},
        "quote": {"ticker": "005930", "provider": "kis", "currency": "KRW", "session": "regular", "execution_ready": True,
            "instrument_type": "STOCK", "last_price": 70000, "observed_at": "2026-10-19T10:00:55+09:00", "ingested_at": NOW},
        "account": {"environment": "demo", "account_scope": broker.client.credentials.scope(), "complete": True,
            "observed_at": NOW, "ingested_at": NOW, "nav_krw": 10_000_000, "cash_krw": 9_300_000,
            "positions": [{"ticker": "005930", "quantity": 10, "sellable_quantity": 10, "market_value_krw": 700_000}],
            "cash_only_buying_power_krw": 9_000_000, "cash_only_buying_quantity": 128,
            "capacity_ticker": "005930", "capacity_limit_price": 70000}}
    result.update(changes)
    return result


def test_opt_in_and_host_path_tr_id_isolation(tmp_path):
    b, c, s, _ = make(tmp_path, ack(), enabled=False)
    with pytest.raises(DemoError, match="opt-in"):
        b.submit(**order(b))
    assert not s.calls
    for method, endpoint, tr_id in (("POST", "order-cash", "TTTC0012U"), ("GET", "../inquire-balance", "VTTC8434R"),
                                   ("POST", "https://openapi.koreainvestment.com:9443", "VTTC0012U")):
        with pytest.raises(DemoError, match="allowlist"):
            c.request(method, endpoint, tr_id, body=c._account())
    with pytest.raises(DemoError, match="allowlist"):
        c._http("POST", "/other")
    assert not s.calls
    b.close()


def test_guarded_success_is_acknowledged_not_filled_and_is_durable(tmp_path):
    b, c, s, moment = make(tmp_path, ack())
    args = order(b)
    receipt = b.submit(**args)
    assert receipt["status"] == "ACKNOWLEDGED"
    assert receipt["live_orders_enabled"] is False
    assert len(s.calls) == 2
    for method, url, kwargs in s.calls:
        parsed = urlsplit(url)
        assert parsed.scheme == "https"
        assert parsed.netloc == "openapivts.koreainvestment.com:29443"
        assert parsed.hostname == "openapivts.koreainvestment.com" and parsed.port == 29443
        assert parsed.username is None and parsed.password is None
        assert not parsed.query and not parsed.fragment
        assert (method, parsed.path) in {
            ("POST", "/oauth2/tokenP"),
            ("POST", "/uapi/domestic-stock/v1/trading/order-cash"),
        }
        assert kwargs["allow_redirects"] is False
    assert s.calls[-1][2]["headers"]["tr_id"] == "VTTC0012U"
    assert s.calls[-1][2]["json"]["ORD_DVSN"] == "00"
    assert b.db.execute("SELECT count(*) FROM lifecycle_events WHERE kind='FILL'").fetchone()[0] == 0
    assert b.db.execute("SELECT mode FROM lifecycle_events WHERE kind='INTENT'").fetchone()[0] == "demo"
    b.close()
    moment[0] += timedelta(days=1)
    b = KisPaperBroker(tmp_path / "vts.sqlite", c, PaperOrderPolicy(("005930",)), paper_enabled=True, clock=lambda: moment[0])
    args["quote"] = args["account"] = {}  # No renewed observation is needed for a duplicate.
    assert b.submit(**args)["duplicate"] is True
    assert len(s.calls) == 2
    with pytest.raises(DemoError, match="reused"):
        b.submit(**{**args, "quantity": 2})
    b.close()


@pytest.mark.parametrize("location,key,value", [
    ("quote", "observed_at", None), ("quote", "observed_at", "2026-10-19"),
    ("quote", "observed_at", "bad-clock"), ("quote", "observed_at", "2026-10-19T10:00:55"),
    ("quote", "observed_at", "2026-10-19T10:01:01+09:00"), ("quote", "observed_at", "2026-10-19T09:59:00+09:00"),
    ("quote", "ingested_at", "2026-10-19T10:01:01+09:00"), ("quote", "ingested_at", "2026-10-19T10:00:54+09:00"),
    ("account", "observed_at", None), ("account", "ingested_at", "bad-clock"),
    ("account", "observed_at", "2026-10-19T10:01:01+09:00"), ("account", "observed_at", "2026-10-19T09:59:00+09:00"),
    ("signal", "available_at", None), ("signal", "available_at", "2026-10-19T10:01:01+09:00"),
    ("signal", "valid_until", "2026-10-19T10:01:00+09:00"), ("signal", "valid_until", "2026-10-19"),
])
def test_missing_invalid_future_and_stale_clocks_never_send(tmp_path, location, key, value):
    b, _, s, _ = make(tmp_path)
    args = order(b)
    args[location][key] = value
    with pytest.raises(DemoError):
        b.submit(**args)
    assert not s.calls
    assert b.db.execute("SELECT count(*) FROM paper_intents").fetchone()[0] == 0
    b.close()


@pytest.mark.parametrize("location,key,value", [
    ("quote", "ticker", "000660"), ("quote", "currency", "USD"), ("quote", "session", "after_hours"),
    ("quote", "provider", "tradingview_mcp"), ("quote", "execution_ready", False),
    ("quote", "last_price", float("nan")), ("quote", "instrument_type", "UNKNOWN"),
    ("signal", "execution_ready", False), ("signal", "decision_now", "NONE"),
    ("account", "complete", False), ("account", "environment", "real"), ("account", "account_scope", "wrong"),
    ("account", "positions", None), ("account", "cash_krw", -1),
    ("account", "cash_only_buying_power_krw", 1), ("account", "cash_only_buying_quantity", 0),
    ("account", "capacity_ticker", "000660"), ("account", "capacity_limit_price", 69000),
])
def test_scope_risk_and_identity_fail_closed(tmp_path, location, key, value):
    b, _, s, _ = make(tmp_path)
    args = order(b)
    args[location][key] = value
    with pytest.raises(DemoError):
        b.submit(**args)
    assert not s.calls
    b.close()


@pytest.mark.parametrize("change", [{"quantity": True}, {"quantity": 1.0}, {"quantity": 0}, {"quantity": -1},
    {"limit_price": 70001}, {"limit_price": 75000}, {"quantity": 2}, {"ticker": "NVDA"}, {"ticker": "000660"}])
def test_integer_limit_tick_and_notional_limits(tmp_path, change):
    b, _, s, _ = make(tmp_path)
    with pytest.raises(DemoError):
        b.submit(**order(b, **change))
    assert not s.calls
    b.close()


def test_calendar_holiday_and_no_weekday_fallback(tmp_path, monkeypatch):
    b, _, s, moment = make(tmp_path)
    moment[0] = datetime.fromisoformat("2026-10-18T10:01:00+09:00")  # Sunday
    with pytest.raises(DemoError, match="session"):
        b.submit(**order(b))
    assert not s.calls
    moment[0] = datetime.fromisoformat(NOW)
    monkeypatch.setattr("tradingagents.execution.kis_paper.market_session_state", lambda **_: {
        "source": "weekday_clock_fallback", "phase": "regular", "is_open": True})
    with pytest.raises(DemoError, match="session"):
        b.submit(**order(b))
    assert not s.calls
    b.close()


def test_timeout_unknown_is_not_retried_after_restart_and_new_orders_block(tmp_path):
    b, c, s, moment = make(tmp_path, requests.Timeout())
    args = order(b)
    assert b.submit(**args)["status"] == "UNKNOWN"
    b.close()
    b = KisPaperBroker(tmp_path / "vts.sqlite", c, PaperOrderPolicy(("005930",)), paper_enabled=True, clock=lambda: moment[0])
    assert b.submit(**args)["status"] == "UNKNOWN"
    with pytest.raises(DemoError, match="ambiguous"):
        b.submit(**{**args, "intent_id": "new-intent"})
    assert len(s.calls) == 2
    assert b.reconcile(intent_id=args["intent_id"])["requires_manual_reconciliation"]
    b.close()


def test_partial_fill_cancel_ack_and_confirmed_cancel_are_distinct(tmp_path):
    b, _, s, moment = make(tmp_path, ack(), report(quantity=2, filled=1, remaining=1),
        report(quantity=2, filled=1, remaining=1), ack("124"), report(quantity=2, filled=1, remaining=0, cncl_yn="Y"),
        policy=PaperOrderPolicy(("005930",), max_order_krw=200000))
    b.submit(**order(b, quantity=2))
    moment[0] += timedelta(seconds=10)
    first = b.reconcile(intent_id="vts-intent-1")
    assert first["status"] == "PARTIAL" and first["filled_qty"] == 1
    assert first["settlement_known"] is False and first["fill_time_known"] is False
    cancelled = b.cancel(intent_id="vts-intent-1")
    assert cancelled["status"] == "ACKNOWLEDGED" and cancelled["cancellation_confirmed"] is False
    count = len(s.calls)
    assert b.cancel(intent_id="vts-intent-1")["duplicate"]
    assert len(s.calls) == count
    moment[0] += timedelta(seconds=1)
    assert b.reconcile(intent_id="vts-intent-1")["status"] == "CANCELLED"
    assert b.db.execute("SELECT count(*) FROM lifecycle_events WHERE kind='FILL'").fetchone()[0] == 0
    assert s.calls[-2][2]["headers"]["tr_id"] == "VTTC0013U"
    b.close()


def test_reconciliation_and_cancellation_are_known_only_after_response(tmp_path):
    b, _, s, moment = make(tmp_path, ack(), report(remaining=0, cncl_yn="Y"))
    b.submit(**order(b))
    started = moment[0]
    original_request = s.request

    def delayed_request(method, url, **kwargs):
        response = original_request(method, url, **kwargs)
        if url.endswith("inquire-daily-ccld"):
            moment[0] += timedelta(seconds=5)
        return response

    s.request = delayed_request
    result = b.reconcile(intent_id="vts-intent-1")
    received = moment[0].astimezone(datetime.fromisoformat(result["observed_at"]).tzinfo)
    assert received > started
    assert datetime.fromisoformat(result["observed_at"]) == received
    assert datetime.fromisoformat(result["ingested_at"]) >= received
    stored = b.db.execute("SELECT observed_at,evidence FROM paper_observations").fetchone()
    assert datetime.fromisoformat(stored["observed_at"]) == received
    assert json.loads(stored["evidence"])["ingested_at"] == result["ingested_at"]
    cancellation = b.db.execute("SELECT occurred_at,available_at,ingested_at FROM lifecycle_events WHERE kind='CANCEL'").fetchone()
    assert datetime.fromisoformat(cancellation["occurred_at"]) == received
    assert datetime.fromisoformat(cancellation["available_at"]) >= received
    assert datetime.fromisoformat(cancellation["ingested_at"]) >= received
    b.close()


@pytest.mark.parametrize("seconds,broker_time", [(-1, "100100"), (5, "100106")])
def test_delayed_reconciliation_rejects_regressed_clock_or_future_broker_time(tmp_path, seconds, broker_time):
    b, _, s, moment = make(tmp_path, ack(), report(ord_tmd=broker_time))
    b.submit(**order(b))
    original_request = s.request

    def delayed_request(method, url, **kwargs):
        response = original_request(method, url, **kwargs)
        if url.endswith("inquire-daily-ccld"):
            moment[0] += timedelta(seconds=seconds)
        return response

    s.request = delayed_request
    with pytest.raises(DemoError):
        b.reconcile(intent_id="vts-intent-1")
    assert b.db.execute("SELECT count(*) FROM paper_observations").fetchone()[0] == 0
    assert b.db.execute("SELECT count(*) FROM lifecycle_events WHERE kind='CANCEL'").fetchone()[0] == 0
    assert b.status()["unresolved_count"] == 1
    b.close()


@pytest.mark.parametrize("changes", [{"ord_dt": "20261020"}, {"ord_tmd": "100101"}, {"ord_dt": ""},
    {"ord_tmd": "1001"}, {"ord_tmd": "246001"}, {"ord_tmd": "100059"}, {"pdno": "000660"}])
def test_bad_broker_order_time_or_identity_blocks_followup(tmp_path, changes):
    b, _, s, _ = make(tmp_path, ack(), report(**changes))
    b.submit(**order(b))
    with pytest.raises(DemoError):
        b.reconcile(intent_id="vts-intent-1")
    with pytest.raises(DemoError):
        b.submit(**order(b, intent_id="vts-intent-2"))
    assert len(s.calls) == 3
    b.close()


def test_empty_order_report_is_unresolved_not_empty_filled(tmp_path):
    b, _, _, _ = make(tmp_path, ack(), Response({"rt_cd": "0", "output1": []}))
    b.submit(**order(b))
    with pytest.raises(DemoError, match="Missing"):
        b.reconcile(intent_id="vts-intent-1")
    assert b.status()["unresolved_count"] == 1
    b.close()


def test_budget_cash_reservation_and_policy_immutability_survive_restart(tmp_path):
    policy = PaperOrderPolicy(("005930",), max_daily_buy_krw=140000)
    b, c, s, moment = make(tmp_path, ack(), ack("124"), policy=policy)
    args = order(b)
    args["account"]["cash_krw"] = 100000
    b.submit(**args)
    with pytest.raises(DemoError, match="reserved cash"):
        b.submit(**{**args, "intent_id": "vts-intent-2"})
    args["account"]["cash_krw"] = 900000
    b.submit(**{**args, "intent_id": "vts-intent-2"})
    b.close()
    with pytest.raises(DemoError, match="Policy changed"):
        KisPaperBroker(tmp_path / "vts.sqlite", c, PaperOrderPolicy(("005930",)), paper_enabled=True)
    b = KisPaperBroker(tmp_path / "vts.sqlite", c, policy, paper_enabled=True, clock=lambda: moment[0])
    with pytest.raises(DemoError, match="Daily paper buy"):
        b.submit(**{**args, "intent_id": "vts-intent-3"})
    assert len(s.calls) == 3
    b.close()


def test_protective_sell_does_not_require_buying_capacity_or_cash(tmp_path):
    b, _, s, _ = make(tmp_path, ack())
    args = order(b, side="SELL")
    args["signal"]["decision_now"] = "REDUCE_NOW"
    args["account"]["cash_krw"] = 0
    args["account"].pop("cash_only_buying_power_krw")
    args["account"].pop("cash_only_buying_quantity")
    assert b.submit(**args)["status"] == "ACKNOWLEDGED"
    assert s.calls[-1][2]["headers"]["tr_id"] == "VTTC0011U"
    assert s.calls[-1][2]["json"]["SLL_TYPE"] == "01"
    b.close()


def test_sell_reservations_cannot_oversell(tmp_path):
    b, _, _, _ = make(tmp_path, ack())
    args = order(b, side="SELL")
    args["signal"]["decision_now"] = "EXIT_NOW"
    args["account"]["positions"][0]["sellable_quantity"] = 1
    b.submit(**args)
    with pytest.raises(DemoError, match="unreserved"):
        b.submit(**{**args, "intent_id": "vts-intent-2"})
    b.close()


def test_no_automatic_requests_retry_adapter_allowed():
    session = requests.Session()
    session.mount("https://", HTTPAdapter(max_retries=1))
    with pytest.raises(DemoError, match="automatic HTTP retries"):
        KisDemoClient(DemoCredentials("fixture-key", "fixture-secret", "12345678", "01"), session=session)


def test_retry_adapter_changed_after_construction_is_still_blocked(tmp_path):
    b, c, s, _ = make(tmp_path)
    s.adapters = {"https://": HTTPAdapter(max_retries=1)}
    with pytest.raises(DemoError, match="automatic HTTP retries"):
        c.authenticate()
    assert not s.calls
    b.close()


def test_crash_between_intent_and_transport_does_not_retry_or_unblock(tmp_path):
    b, c, s, moment = make(tmp_path)
    args = order(b)
    terms = {key: args[key] for key in ("ticker", "side", "quantity", "limit_price")}
    b.db.execute("INSERT INTO paper_intents VALUES (?,?,?,?)", (
        args["intent_id"], json.dumps(terms, sort_keys=True), args["signal"]["signal_id"], NOW))
    b.close()
    b = KisPaperBroker(tmp_path / "vts.sqlite", c, PaperOrderPolicy(("005930",)), paper_enabled=True, clock=lambda: moment[0])
    assert b.submit(**args)["status"] == "UNKNOWN"
    with pytest.raises(DemoError, match="ambiguous"):
        b.submit(**{**args, "intent_id": "new-intent"})
    assert not s.calls
    b.close()


def test_clock_expiry_during_auth_wait_never_posts_cash_order(tmp_path):
    b, c, s, moment = make(tmp_path, ack())
    waits = [0]

    def wait():
        waits[0] += 1
        if waits[0] == 2:
            moment[0] += timedelta(seconds=120)

    c.pacer.wait = wait
    assert b.submit(**order(b))["status"] == "NOT_SENT"
    assert len(s.calls) == 1  # Authentication only.
    assert b.submit(**order(b))["status"] == "NOT_SENT"
    assert len(s.calls) == 1
    b.close()


def test_session_close_during_auth_wait_never_posts_cash_order(tmp_path):
    b, c, s, moment = make(tmp_path, ack())
    moment[0] = datetime.fromisoformat("2026-10-19T15:29:59+09:00")
    args = order(b)
    args["signal"]["available_at"] = args["quote"]["observed_at"] = "2026-10-19T15:29:58+09:00"
    args["signal"]["valid_until"] = "2026-10-19T15:31:00+09:00"
    args["quote"]["ingested_at"] = args["account"]["observed_at"] = args["account"]["ingested_at"] = moment[0].isoformat()
    waits = [0]

    def wait():
        waits[0] += 1
        if waits[0] == 2:
            moment[0] += timedelta(seconds=2)

    c.pacer.wait = wait
    assert b.submit(**args)["status"] == "NOT_SENT"
    assert len(s.calls) == 1
    b.close()


def test_cancel_timeout_is_unknown_and_never_resent(tmp_path):
    b, _, s, moment = make(tmp_path, ack(), report(), requests.Timeout())
    b.submit(**order(b))
    moment[0] += timedelta(seconds=1)
    assert b.cancel(intent_id="vts-intent-1")["status"] == "UNKNOWN"
    calls = len(s.calls)
    assert b.cancel(intent_id="vts-intent-1")["status"] == "UNKNOWN"
    assert len(s.calls) == calls
    with pytest.raises(DemoError, match="ambiguous"):
        b.submit(**order(b, intent_id="new-intent"))
    b.close()


def test_read_only_facade_can_reconcile_but_not_cancel(tmp_path):
    b, c, s, moment = make(tmp_path, ack(), report())
    b.submit(**order(b))
    b.close()
    b = KisPaperBroker(tmp_path / "vts.sqlite", c, PaperOrderPolicy(("005930",)), clock=lambda: moment[0])
    assert b.reconcile(intent_id="vts-intent-1")["status"] == "OPEN"
    calls = len(s.calls)
    with pytest.raises(DemoError, match="opt-in"):
        b.cancel(intent_id="vts-intent-1")
    assert len(s.calls) == calls
    b.close()


def test_concentration_and_daily_order_caps_are_deterministic(tmp_path):
    b, _, s, _ = make(tmp_path, ack(), policy=PaperOrderPolicy(("005930",), max_daily_orders=1))
    args = order(b)
    args["account"]["positions"][0]["market_value_krw"] = 3_490_000
    with pytest.raises(DemoError, match="concentration"):
        b.submit(**args)
    assert not s.calls
    args["account"]["positions"][0]["market_value_krw"] = 700_000
    b.submit(**args)
    with pytest.raises(DemoError, match="Daily paper order"):
        b.submit(**{**args, "intent_id": "second-intent"})
    b.close()


def test_read_account_uses_cash_only_capacity_and_preserves_observation(tmp_path):
    b, c, s, _ = make(tmp_path,
        Response({"rt_cd": "0", "output1": [], "output2": [{"dnca_tot_amt": "10000000", "tot_evlu_amt": "10000000"}]}),
        Response({"rt_cd": "0", "output": {"nrcvb_buy_amt": "200000", "nrcvb_buy_qty": "2", "max_buy_amt": "9000000"}}))
    account = read_paper_account(c, ticker="005930", limit_price=70000, clock=lambda: datetime.fromisoformat(NOW))
    assert account["positions"] == []
    assert account["cash_only_buying_power_krw"] == 200000
    assert account["cash_only_buying_quantity"] == 2
    assert s.calls[-1][2]["headers"]["tr_id"] == "VTTC8908R"
    assert s.calls[-1][2]["params"]["ORD_DVSN"] == "01"
    assert account["environment"] == "demo"
    b.close()


@pytest.mark.parametrize("totals", [[], {}, {"dnca_tot_amt": ""}, {"dnca_tot_amt": "NaN", "tot_evlu_amt": "10"}])
def test_invalid_account_totals_never_become_zero_holdings(tmp_path, totals):
    b, c, _, _ = make(tmp_path,
        Response({"rt_cd": "0", "output1": [], "output2": totals}),
        Response({"rt_cd": "0", "output": {"nrcvb_buy_amt": "200000", "nrcvb_buy_qty": "2"}}))
    with pytest.raises(DemoError):
        read_paper_account(c, ticker="005930", limit_price=70000)
    b.close()


def test_explicit_vts_fill_import_never_labels_real_and_requires_known_clocks(tmp_path):
    b, _, _, moment = make(tmp_path, ack(), report(filled=1, remaining=0))
    b.submit(**order(b))
    moment[0] += timedelta(seconds=10)
    b.reconcile(intent_id="vts-intent-1")
    receipt = {"environment": "demo", "account_scope": b.client.credentials.scope(), "intent_id": "vts-intent-1",
        "fill_id": "fixture-fill-1", "ticker": "005930", "side": "BUY", "quantity": 1, "price": 70000, "cost": 100,
        "currency": "KRW", "executed_at": "2026-10-19T10:01:02+09:00", "confirmed_at": "2026-10-19T10:01:03+09:00",
        "settled_at": "2026-10-19T10:01:04+09:00"}
    for change in ({"environment": "real"}, {"settled_at": None}, {"executed_at": "bad-date"},
                   {"confirmed_at": "2026-10-19T10:01:11+09:00"}, {"quantity": 2}, {"price": 71000}):
        with pytest.raises(DemoError):
            import_demo_fill(b, {**receipt, **change})
    assert import_demo_fill(b, receipt)
    assert not import_demo_fill(b, receipt)
    row = b.db.execute("SELECT mode,payload_json FROM lifecycle_events WHERE kind='FILL'").fetchone()
    assert row["mode"] == "demo" and json.loads(row["payload_json"])["source"] == "kis_vts"
    with pytest.raises(ValueError, match="different evidence"):
        import_demo_fill(b, {**receipt, "cost": 101})
    assert b.db.execute("SELECT count(*) FROM lifecycle_events WHERE mode='actual'").fetchone()[0] == 0
    b.close()


def test_cli_defaults_offline_and_requires_opt_in_before_credentials(tmp_path, monkeypatch, capsys):
    from tools.kis_paper import main
    monkeypatch.setattr("tools.kis_paper.check", lambda *, connect: {"status": "OFFLINE" if not connect else "READ_CONNECTION_VERIFIED"})
    assert main(["readiness"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "OFFLINE" and result["live_orders_enabled"] is False
    assert result["paper_order_connection_verified"] is False
    monkeypatch.setattr("tools.kis_paper.DemoCredentials.from_local_settings", lambda: pytest.fail("must not load keys"))
    assert main(["submit", "--policy", str(tmp_path / "missing.json"), "--journal", str(tmp_path / "none.sqlite"), "--input", str(tmp_path / "missing.json")]) == 2
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "BLOCKED"
    assert not (tmp_path / "none.sqlite").exists()
