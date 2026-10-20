from contextlib import contextmanager
from datetime import datetime, timedelta
import json
import sqlite3

import pytest

from tradingagents.atomic_io import atomic_write_json
from tradingagents.execution import demo_validation as dv
from tools.validate_kis_sessions import main


NOW = datetime.fromisoformat("2026-10-19T10:00:00+09:00")


def session(market, now_local):
    return {"source": "exchange_calendars", "is_open": market == "KR", "phase": "regular" if market == "KR" else "closed",
            "session_open": now_local.replace(hour=9, minute=0, second=0).isoformat(),
            "session_close": now_local.replace(hour=15, minute=30, second=0).isoformat()}


class Harness:
    def __init__(self, tmp_path):
        self.root, self.archive = tmp_path / "state", tmp_path / "archive"
        self.now, self.calls, self.reports = NOW, [], []
        self.submit_status, self.cancel_status = "ACKNOWLEDGED", "ACKNOWLEDGED"
        self.raise_after_submit = self.raise_before_submit = False

    @contextmanager
    def factory(self, market, path, clock):
        path.parent.mkdir(parents=True, exist_ok=True)
        harness = self

        class Broker:
            def __init__(self):
                self.db = sqlite3.connect(path, isolation_level=None)
                self.db.row_factory = sqlite3.Row
                self.db.execute("CREATE TABLE IF NOT EXISTS requests(id TEXT PRIMARY KEY, status TEXT, response TEXT, created_at TEXT)")
                self.db.execute("CREATE TABLE IF NOT EXISTS paper_intents(id TEXT PRIMARY KEY, terms TEXT)")
                self.db.execute("CREATE TABLE IF NOT EXISTS order_state(id TEXT PRIMARY KEY, status TEXT, filled INTEGER, remaining INTEGER)")
                self.db.execute("CREATE TABLE IF NOT EXISTS paper_observations(id TEXT, observed_at TEXT, evidence TEXT)")

            def submit(self, **kwargs):
                harness.calls.append(("submit", kwargs))
                if harness.raise_before_submit:
                    raise RuntimeError("secret must never escape")
                self.db.execute("INSERT INTO requests VALUES (?,?,?,?)", (kwargs["intent_id"], harness.submit_status,
                    json.dumps({"broker_order_id": "fixture-broker-id"}), harness.now.isoformat()))
                terms = {key: kwargs[key] for key in ("ticker", "side", "quantity", "limit_price")}
                if "exchange" in kwargs:
                    terms["exchange"] = kwargs["exchange"]
                self.db.execute("INSERT INTO paper_intents VALUES (?,?)", (kwargs["intent_id"], json.dumps(terms)))
                if harness.raise_after_submit:
                    raise RuntimeError("secret must never escape")
                return {"status": harness.submit_status}

            def reconcile(self, **kwargs):
                harness.calls.append(("reconcile", kwargs))
                report = harness.reports.pop(0)
                if isinstance(report, Exception):
                    raise report
                self.db.execute("INSERT OR REPLACE INTO order_state VALUES (?,?,?,?)", (kwargs["intent_id"], report["status"], report["filled_qty"], report["remaining_qty"]))
                self.db.execute("INSERT INTO paper_observations VALUES (?,?,?)", (kwargs["intent_id"], harness.now.isoformat(), json.dumps(report)))
                return report

            def cancel(self, **kwargs):
                harness.calls.append(("cancel", kwargs))
                self.db.execute("INSERT INTO requests VALUES (?,?,?,?)", ("cancel:" + kwargs["intent_id"], harness.cancel_status,
                    json.dumps({"broker_order_id": "fixture-cancel-id"}), harness.now.isoformat()))
                return {"status": harness.cancel_status}

        broker = Broker()
        try:
            yield broker
        finally:
            broker.db.close()

    def quote(self, market, clock):
        self.calls.append(("quote", market))
        return {"last_price": 40000 if market == "KR" else 250, "observed_at": self.now.isoformat()}

    def account(self, market, broker, terms, clock):
        self.calls.append(("account", market))
        return {}

    def tick(self, **kwargs):
        result = dv.run_campaign(self.archive, self.root, run=kwargs.pop("run", True), clock=lambda: self.now,
            broker_factory=self.factory, quote_loader=self.quote, account_loader=self.account,
            session_resolver=kwargs.pop("session_resolver", session), **kwargs)
        self.now += timedelta(minutes=1)
        return result

    def state(self):
        return json.loads((self.root / "kr-campaign.json").read_text())


def report(status="OPEN", filled=0, remaining=1):
    return {"status": status, "filled_qty": filled, "remaining_qty": remaining}


def test_finite_campaign_restart_cancel_ack_not_confirmation_and_fill_not_settlement(tmp_path):
    h = Harness(tmp_path)
    one = h.tick()
    assert one["markets"]["KR"]["stages"]["submitted"]["verified"]
    assert not one["markets"]["KR"]["stages"]["filled"]["verified"]
    h.reports = [report(), report("CANCELLED", 0, 0), report("FILLED", 1, 0)]
    two = h.tick()
    assert not two["markets"]["KR"]["stages"]["cancelled"]["verified"]
    three = h.tick()
    assert three["markets"]["KR"]["stages"]["cancelled"]["verified"]
    assert h.state()["status"] == "RUNNING"
    h.tick()
    final = h.tick()
    assert final["markets"]["KR"]["status"] == "VERIFIED"
    assert all(stage["verified"] for stage in final["markets"]["KR"]["stages"].values())
    calls = list(h.calls)
    h.tick()
    assert h.calls == calls
    assert [kind for kind, _ in h.calls].count("submit") == 2
    assert [kind for kind, _ in h.calls].count("cancel") == 1
    assert final["live_orders_enabled"] is False
    assert "settled" not in json.dumps(final)
    assert h.state()["orders"][1]["terms"]["limit_price"] == 40005


def test_default_offline_and_closed_session_never_create_network_client(tmp_path):
    def forbidden(*args, **kwargs):
        raise AssertionError("Network/client creation forbidden")
    for run in (False, True):
        value = dv.run_campaign(tmp_path / "archive", tmp_path / "state", run=run, clock=lambda: NOW,
            broker_factory=forbidden, session_resolver=lambda **kw: {"source": "exchange_calendars", "is_open": False, "phase": "closed"})
        assert value["markets"]["KR"]["status"] == "WAITING_SESSION"
    assert json.loads((tmp_path / "archive/paper/kis-session-validation.json").read_text())["mode"] == "KIS_DEMO"


@pytest.mark.parametrize("status,blocker", [("UNKNOWN", "AMBIGUOUS_ORDER"), ("REJECTED", "ORDER_REJECTED"), ("NOT_SENT", "ORDER_NOT_SENT")])
def test_no_retry_unknown_rejected_or_definitely_not_sent(tmp_path, status, blocker):
    h = Harness(tmp_path)
    h.submit_status = status
    result = h.tick()
    assert result["markets"]["KR"]["blocker"] == blocker
    h.tick()
    assert [kind for kind, _ in h.calls].count("submit") == 1
    assert not result["markets"]["KR"]["stages"]["submitted"]["verified"]


def test_crash_after_order_persistence_recovers_by_read_without_second_post(tmp_path):
    h = Harness(tmp_path)
    h.raise_after_submit = True
    result = h.tick()
    assert "secret" not in json.dumps(result)
    h.reports = [report()]
    h.tick()
    assert [kind for kind, _ in h.calls].count("submit") == 1
    assert [kind for kind, _ in h.calls].count("cancel") == 1


def test_crash_after_campaign_prepare_before_transport_fails_closed(tmp_path):
    h = Harness(tmp_path)
    h.raise_before_submit = True
    h.tick()
    h.raise_before_submit = False
    result = h.tick()
    assert result["markets"]["KR"]["blocker"] == "JOURNAL_RECOVERY_REQUIRED"
    assert [kind for kind, _ in h.calls].count("submit") == 1


def test_cancellation_race_is_observed_fill_and_no_chasing_order(tmp_path):
    h = Harness(tmp_path)
    h.tick()
    h.reports = [report("FILLED", 1, 0)]
    result = h.tick()
    assert result["markets"]["KR"]["status"] == "ATTENTION"
    assert result["markets"]["KR"]["blocker"] == "CANCELLATION_RACE"
    assert result["markets"]["KR"]["stages"]["filled"]["verified"]
    assert not result["markets"]["KR"]["stages"]["cancelled"]["verified"]
    h.tick()
    assert [kind for kind, _ in h.calls].count("submit") == 1


def test_unknown_cancel_never_replayed_and_ack_is_not_cancelled(tmp_path):
    h = Harness(tmp_path)
    h.tick()
    h.cancel_status = "UNKNOWN"
    h.reports = [report(), report(), report("CANCELLED", 0, 0)]
    h.tick()
    result = h.tick()
    assert result["markets"]["KR"]["blocker"] == "AMBIGUOUS_CANCELLATION"
    result = h.tick()
    assert result["markets"]["KR"]["blocker"] == "CANCELLATION_NOT_CONFIRMED"
    assert [kind for kind, _ in h.calls].count("cancel") == 1


def test_unfilled_fill_probe_is_cancelled_after_five_minutes(tmp_path):
    h = Harness(tmp_path)
    h.tick()
    h.reports = [report(), report("CANCELLED", 0, 0), report(), report(), report("CANCELLED", 0, 0)]
    h.tick()
    h.tick()
    h.tick()
    h.tick()
    assert [kind for kind, _ in h.calls].count("cancel") == 1
    h.now += timedelta(minutes=5)
    h.tick()
    result = h.tick()
    assert result["markets"]["KR"]["blocker"] == "FILL_NOT_OBSERVED"
    assert [kind for kind, _ in h.calls].count("submit") == 2
    assert [kind for kind, _ in h.calls].count("cancel") == 2


def test_halt_prevents_new_risk_but_cleans_up_pending_order(tmp_path):
    h = Harness(tmp_path)
    h.root.mkdir()
    (h.root / "HALT").touch()
    assert h.tick()["markets"]["KR"]["blocker"] == "HALTED"
    assert not h.calls
    (h.root / "HALT").unlink()
    h.tick()
    (h.root / "HALT").touch()
    h.reports = [report()]
    h.tick()
    assert [kind for kind, _ in h.calls].count("cancel") == 1


@pytest.mark.parametrize("mutate", [lambda s: s.update(checked_at="2099-01-01T00:00:00Z"),
    lambda s: s.update(campaign_id="new-campaign"), lambda s: s.update(status="VERIFIED"),
    lambda s: s.update(orders=[{"intent_id": "fake"}]), lambda s: s["stages"]["filled"].update(verified=True)])
def test_invalid_state_is_permanently_blocked_not_reset(tmp_path, mutate):
    h = Harness(tmp_path)
    state = dv._new("KR", NOW)
    mutate(state)
    atomic_write_json(h.root / "kr-campaign.json", state)
    assert h.tick()["markets"]["KR"]["blocker"] == "STATE_INVALID"
    h.tick()
    assert not h.calls


@pytest.mark.parametrize("status", ["RUNNING", "WAITING_SESSION", "BLOCKED"])
def test_finished_nonterminal_state_is_invalid_not_silently_skipped(tmp_path, status):
    h = Harness(tmp_path)
    state = dv._new("KR", NOW)
    state.update(status=status, finished=True)
    atomic_write_json(h.root / "kr-campaign.json", state)
    result = h.tick()
    assert result["markets"]["KR"]["blocker"] == "STATE_INVALID"
    assert result["markets"]["KR"]["status"] == "ATTENTION"
    assert not h.calls


def test_removed_state_cannot_restart_existing_journal_budget(tmp_path):
    h = Harness(tmp_path)
    h.tick()
    (h.root / "kr-campaign.json").unlink()
    result = h.tick()
    assert result["markets"]["KR"]["blocker"] == "JOURNAL_RECOVERY_REQUIRED"
    assert [kind for kind, _ in h.calls].count("submit") == 1


@pytest.mark.parametrize("change", [{"source": "weekday_clock_fallback"}, {"session_open": "2099-01-01T00:00:00Z"},
                                  {"session_open": None}, {"session_close": None}])
def test_unknown_or_invalid_calendar_blocks_before_network(tmp_path, change):
    h = Harness(tmp_path)
    result = h.tick(session_resolver=lambda **kwargs: {**session(**kwargs), **change})
    assert result["markets"]["KR"]["status"] == "BLOCKED"
    assert not h.calls


def chart_and_book(market="KR", day="20261019", time="095900"):
    if market == "KR":
        bar = {"stck_bsop_date": day, "stck_cntg_hour": time, "stck_oprc": "40000", "stck_hgpr": "40005",
               "stck_lwpr": "39995", "stck_prpr": "40000", "cntg_vol": "10"}
        book = {"stck_bsop_date": day, "aspr_acpt_hour": "100000", "bidp1": "39995", "askp1": "40005"}
    else:
        bar = {"xymd": day, "xhms": time, "open": "250", "high": "251", "low": "249", "last": "250", "evol": "10"}
        book = {"dymd": day, "dhms": "230000", "pbid1": "249.99", "pask1": "250.01"}
    return {"rt_cd": "0", "output2": [bar]}, {"rt_cd": "0", "output1": book}


@pytest.mark.parametrize("market", ["KR", "US"])
def test_dated_quote_normal_and_terms_in_correct_currency(market):
    now = NOW if market == "KR" else datetime.fromisoformat("2026-10-19T10:00:00-04:00")
    chart, book = chart_and_book(market)
    quote = dv.normalize_validation_quote(market=market, chart=chart, orderbook=book, observed_at=now)
    assert quote["quote_basis"] == "DATED_BOOK"
    assert quote["currency"] == ("KRW" if market == "KR" else "USD")
    assert dv._terms(market, quote, "fill")["quantity"] == 1
    assert dv._terms(market, quote, "fill")["limit_price"] <= dv.MARKETS[market]["cap"]


@pytest.mark.parametrize("market", ["KR", "US"])
@pytest.mark.parametrize("day,time", [("", "095900"), ("20261020", "095900"), ("bad", "095900"),
                                    ("20261019", ""), ("20260230", "095900"), ("20261019", "100100"),
                                    ("20261019", "090000")])
def test_missing_invalid_future_and_stale_bar_dates_excluded(market, day, time):
    now = NOW if market == "KR" else datetime.fromisoformat("2026-10-19T10:00:00-04:00")
    chart, book = chart_and_book(market, day, time)
    with pytest.raises(ValueError):
        dv.normalize_validation_quote(market=market, chart=chart, orderbook=book, observed_at=now)


@pytest.mark.parametrize("market", ["KR", "US"])
def test_empty_bars_are_not_executable(market):
    chart, book = chart_and_book(market)
    chart["output2"] = []
    with pytest.raises(ValueError):
        dv.normalize_validation_quote(market=market, chart=chart, orderbook=book, observed_at=NOW)


def test_domestic_undated_book_is_excluded_without_inventing_date_or_bid_ask():
    chart, book = chart_and_book()
    del book["output1"]["stck_bsop_date"]
    book["output1"]["bidp1"] = "999999999"
    quote = dv.normalize_validation_quote(market="KR", chart=chart, orderbook=book, observed_at=NOW)
    assert quote["quote_basis"] == "BAR_ONLY"
    assert "bid" not in quote and "ask" not in quote and "orderbook_date_basis" not in quote
    assert dv._terms("KR", quote, "fill")["limit_price"] == 40005


@pytest.mark.parametrize("day,time,valid", [
    ("20261019", "095900", True), ("", "095900", False),
    ("20261020", "095900", False), ("bad", "095900", False),
    ("20261019", "100100", False), ("20261019", "090000", False),
])
def test_domestic_strategy_quote_uses_dated_bar_without_book(monkeypatch, day, time, valid):
    from types import SimpleNamespace
    from tradingagents.execution import demo_runtime
    from tradingagents.portfolio.kis import KisClient

    chart, _ = chart_and_book(day=day, time=time)
    calls = []
    def fetch(code, **kwargs):
        calls.append((code, kwargs))
        return chart
    client = SimpleNamespace(domestic_time_itemchartprice=fetch,
                             session=SimpleNamespace(close=lambda: calls.append("closed")))
    monkeypatch.setattr(KisClient, "from_api_keys", lambda **kwargs: client)
    if valid:
        quote = demo_runtime.current_quote("KR", "034020.KS", lambda: NOW)
        assert quote["quote_basis"] == "BAR_ONLY"
        assert quote["ticker"] == "034020" and quote["instrument_type"] == "STOCK"
        assert "bid" not in quote and "ask" not in quote
        assert dv._at(quote["observed_at"]) == datetime.fromisoformat("2026-10-19T10:00:00+09:00")
        assert demo_runtime.limit_price(quote, "SELL", "KR") == 40000
    else:
        with pytest.raises(ValueError):
            demo_runtime.current_quote("KR", "034020.KS", lambda: NOW)
    assert calls[0] == ("034020", {"input_hour": "100000", "include_past_data": "N"})
    assert calls[-1] == "closed"


@pytest.mark.parametrize("date,time", [(None, "230000"), ("bad", "230000"), ("20261020", "230000"),
                                    ("20261019", "230001"), ("20261019", None), ("20261019", "225000")])
def test_us_book_missing_invalid_future_stale_date_blocks(date, time):
    chart, book = chart_and_book("US")
    book["output1"].update(dymd=date, dhms=time)
    with pytest.raises(ValueError):
        dv.normalize_validation_quote(market="US", chart=chart, orderbook=book,
                                      observed_at=datetime.fromisoformat("2026-10-19T10:00:00-04:00"))


def test_paper_health_safe_fresh_projection_and_unverified_future(tmp_path):
    row = {"checked_at": NOW.isoformat(), "status": "MARKET_CLOSED", "broker_orders_sent": 0, "real_orders_enabled": False,
           "secret": "private", "order_counts": {"FILLED": 2}, "last_fill_at": (NOW - timedelta(minutes=1)).isoformat()}
    receipt = {"mode": "LOCAL_PAPER_ONLY", "enabled": True, "real_orders_enabled": False, "broker_orders_sent": 0,
               "checked_at": NOW.isoformat(), "markets": {"kr": row, "us": row}}
    atomic_write_json(tmp_path / "paper/status.json", receipt)
    result = dv.local_paper_health(tmp_path, NOW)
    assert result["status"] == "RECENT_TICK_CONFIRMED"
    assert result["markets"]["KR"]["order_counts"]["FILLED"] == 2
    assert "secret" not in json.dumps(result)
    assert dv.local_paper_health(tmp_path, NOW - timedelta(seconds=1))["status"] == "UNVERIFIED"
    assert dv.local_paper_health(tmp_path, NOW + timedelta(seconds=181))["status"] == "UNVERIFIED"


def test_cli_defaults_offline(tmp_path, monkeypatch, capsys):
    calls = []
    monkeypatch.setattr("tools.validate_kis_sessions.run_campaign", lambda *args, **kwargs: calls.append(kwargs) or {"mode": "KIS_DEMO"})
    assert main(["--archive-root", str(tmp_path), "--state-root", str(tmp_path / "state")]) == 0
    assert calls == [{"run": False}]
    assert "KIS_DEMO" in capsys.readouterr().out


def test_fabricated_success_without_orders_or_journal_cannot_be_published(tmp_path):
    h = Harness(tmp_path)
    state = dv._new("KR", NOW)
    for name in dv.STAGES:
        dv._prove(state, name, NOW)
    state.update(status="VERIFIED", finished=True)
    atomic_write_json(h.root / "kr-campaign.json", state)
    result = h.tick(run=False)
    assert result["markets"]["KR"]["blocker"] == "STATE_INVALID"
    assert not any(stage["verified"] for stage in result["markets"]["KR"]["stages"].values())
    assert not h.calls


@pytest.mark.parametrize("sql", ["DELETE FROM paper_intents", "UPDATE paper_intents SET terms='{}'",
    "DELETE FROM requests", "UPDATE requests SET response='{}'"])
def test_ack_proof_requires_immutable_matching_journal(tmp_path, sql):
    h = Harness(tmp_path)
    h.tick()
    with sqlite3.connect(h.root / "kr-vts.sqlite") as db:
        db.execute(sql)
    result = h.tick(run=False)
    assert result["markets"]["KR"]["blocker"] == "STATE_INVALID"
    assert not result["markets"]["KR"]["stages"]["submitted"]["verified"]


def test_corrupt_done_flag_cannot_hide_pending_order(tmp_path):
    h = Harness(tmp_path)
    h.tick()
    state = h.state()
    state["orders"][0]["done"] = True
    atomic_write_json(h.root / "kr-campaign.json", state)
    result = h.tick()
    assert result["markets"]["KR"]["blocker"] == "STATE_INVALID"
    assert [kind for kind, _ in h.calls].count("submit") == 1


def test_completed_proofs_require_persisted_cumulative_observations(tmp_path):
    h = Harness(tmp_path)
    h.tick()
    h.reports = [report(), report("CANCELLED", 0, 0), report("FILLED", 1, 0)]
    for _ in range(4):
        h.tick()
    with sqlite3.connect(h.root / "kr-vts.sqlite") as db:
        db.execute("DELETE FROM paper_observations")
    result = h.tick(run=False)
    assert result["markets"]["KR"]["blocker"] == "STATE_INVALID"


def test_us_campaign_uses_usd_cap_and_separate_nasdaq_terms(tmp_path):
    h = Harness(tmp_path)
    h.now = datetime.fromisoformat("2026-10-19T10:00:00-04:00")
    def us_session(market, now_local):
        return {"source": "exchange_calendars", "is_open": market == "US", "phase": "regular" if market == "US" else "closed",
            "session_open": now_local.replace(hour=9, minute=30, second=0).isoformat(),
            "session_close": now_local.replace(hour=16, minute=0, second=0).isoformat()}
    h.tick(session_resolver=us_session)
    h.reports = [report(), report("CANCELLED", 0, 0), report("FILLED", 1, 0)]
    for _ in range(4):
        result = h.tick(session_resolver=us_session)
    assert result["markets"]["US"]["status"] == "VERIFIED"
    assert result["markets"]["KR"]["status"] == "WAITING_SESSION"
    submissions = [value for kind, value in h.calls if kind == "submit"]
    assert all(item["ticker"] == "AAPL" and item["exchange"] == "NASD" and item["limit_price"] <= 500 for item in submissions)
    assert submissions[1]["limit_price"] == 250.01


@pytest.mark.parametrize("market", ["KR", "US"])
def test_actual_client_broker_seam_uses_dedicated_credentials_and_auth_cache(tmp_path, monkeypatch, market):
    from tradingagents.execution.kis_demo import DemoCredentials, KisDemoClient
    from tradingagents.execution.kis_demo_us import KisDemoUSClient
    credentials = DemoCredentials("fixture-key", "fixture-secret", "12345678", "01")
    monkeypatch.setattr(DemoCredentials, "from_local_settings", lambda: credentials)
    monkeypatch.setattr("tradingagents.execution.kis_demo_us.credentials_from_settings", lambda: credentials)
    cached = []
    monkeypatch.setattr("tradingagents.execution.demo_token_cache.cache_demo_authentication", lambda client, **kw: cached.append((client, kw)))
    with dv.broker_context(market, tmp_path / f"{market}.sqlite", lambda: NOW) as broker:
        assert type(broker.client) is (KisDemoClient if market == "KR" else KisDemoUSClient)
        assert cached == [(broker.client, {"market": market})]
        assert broker.client._token is None
        assert broker.enabled is True


def test_realistic_us_split_header_and_book_are_normalized_together():
    chart, book = chart_and_book("US")
    values = book["output1"]
    book = {"rt_cd": "0", "output1": {"dymd": values["dymd"], "dhms": values["dhms"], "code": "AAPL", "curr": "USD"},
            "output2": {"pbid1": values["pbid1"], "pask1": values["pask1"], "vbid1": "10", "vask1": "20"}}
    quote = dv.normalize_validation_quote(market="US", chart=chart, orderbook=book,
        observed_at=datetime.fromisoformat("2026-10-19T10:00:00-04:00"))
    assert quote["bid"] == 249.99 and quote["ask"] == 250.01
    book["output2"]["code"] = "WRONG"
    with pytest.raises(ValueError):
        dv.normalize_validation_quote(market="US", chart=chart, orderbook=book,
            observed_at=datetime.fromisoformat("2026-10-19T10:00:00-04:00"))


@pytest.mark.parametrize("observed,day,bar_time,book_day,book_time", [
    ("2026-10-19T22:33:59+09:00", "20261019", "093200", "20261019", "223359"),
    ("2026-10-20T02:00:00+09:00", "20261019", "125900", "20261020", "020000"),
    ("2026-11-03T00:00:00+09:00", "20261102", "095900", "20261103", "000000"),
])
def test_us_book_korea_clock_across_midnight_and_dst(observed, day, bar_time, book_day, book_time):
    chart, book = chart_and_book("US", day, bar_time)
    book["output1"].update(dymd=book_day, dhms=book_time)
    now = datetime.fromisoformat(observed)
    quote = dv.normalize_validation_quote(market="US", chart=chart, orderbook=book, observed_at=now)
    assert quote["execution_ready"] is True
    assert 0 <= (now - datetime.fromisoformat(quote["observed_at"])).total_seconds() <= 120
    # Fixed timezone interpretation must never choose a convenient zone or
    # substitute retrieval time to admit future/stale broker timestamps.
    for delta in (timedelta(seconds=1), timedelta(seconds=-121), timedelta(days=-1)):
        bad = now + delta
        book["output1"].update(dymd=bad.strftime("%Y%m%d"), dhms=bad.strftime("%H%M%S"))
        with pytest.raises(ValueError, match="Book future or stale"):
            dv.normalize_validation_quote(market="US", chart=chart, orderbook=book, observed_at=now)


@pytest.mark.parametrize("status", ["ACTIVE", "VALUATION_ONLY"])
def test_successful_local_paper_statuses_remain_visible(tmp_path, status):
    row = {"checked_at": NOW.isoformat(), "status": status, "broker_orders_sent": 0, "real_orders_enabled": False}
    atomic_write_json(tmp_path / "paper/status.json", {"mode": "LOCAL_PAPER_ONLY", "enabled": True,
        "checked_at": NOW.isoformat(), "real_orders_enabled": False, "broker_orders_sent": 0, "markets": {"kr": row, "us": row}})
    assert dv.local_paper_health(tmp_path, NOW)["markets"]["KR"]["status"] == status


def test_session_windows_and_us_timezone_use_authoritative_calendar():
    for market, moment in (("KR", "2026-10-19T09:05:00+09:00"), ("US", "2026-10-19T22:35:00+09:00")):
        value = dv._runtime_session(market=market, now_local=datetime.fromisoformat(moment))
        assert value["is_open"] is True and value["source"] == "exchange_calendars"
        assert dv._at(value["session_open"]) <= datetime.fromisoformat(moment) < dv._at(value["session_close"])
