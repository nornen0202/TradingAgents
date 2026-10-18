"""Real guarded KR/US brokers with deterministic HTTP fixtures; no network."""
from contextlib import contextmanager
from datetime import datetime, timedelta
import json
from pathlib import Path
import sqlite3
from zoneinfo import ZoneInfo

import pytest

from tradingagents.atomic_io import atomic_write_json
from tradingagents.execution import demo_runtime as runtime
from tradingagents.execution.kis_demo import DemoCredentials, KisDemoClient, RequestPacer
from tradingagents.execution.kis_demo_us import KisDemoUSClient
from tradingagents.execution.kis_paper import KisPaperBroker, PaperOrderPolicy, execution_notional
from tradingagents.execution.kis_paper_us import KisPaperUSBroker, USPaperOrderPolicy


class Response:
    status_code = 200
    headers = {}
    def __init__(self, payload):
        self.payload = payload
    def json(self):
        return self.payload


class Harness:
    def __init__(self, path, market):
        self.archive, self.root, self.validation = path / "archive", path / "state", path / "validation"
        self.market, self.ticker = market, "005930.KS" if market == "KR" else "AAPL"
        self.now = datetime(2026, 10, 19, 10, 0, tzinfo=ZoneInfo(runtime.ZONES[market]))
        self.price = 70000 if market == "KR" else 200
        self.credentials = DemoCredentials("fixture-key", "fixture-secret", "12345678", "01")
        self.orders, self.calls, self.gate_open = {}, [], True
        self.lost = self.raise_before = False
        atomic_write_json(self.root / "enabled.json", {"mode": runtime.MODE, "enabled": True, "real_orders_enabled": False})
        self.source()

    def source(self, name="fixture-1", *, action="STARTER_NOW", qty=1, changes=None):
        run = self.archive / "runs/2026" / name
        moment = (self.now - timedelta(seconds=5)).isoformat()
        code = "BUY" if action in {"STARTER_NOW", "ADD_NOW", "BUY_NOW"} else "SELL"
        bundle = {"market": self.market.lower(), "generated_at": moment, "analysis_source_run_id": name,
            "strategy_table": [{"ticker": self.ticker, "last_price": self.price, "market_data_asof": moment,
                "market_session": "regular", "quality": {"execution_ready": True, "generated_in_current_run": True},
                "raw_codes": {"decision_now": action}}]}
        if changes:
            changes(bundle)
        for filename, payload in {
            "run.json": {"run_id": name, "status": "success", "settings": {"market": self.market.lower()}, "started_at": moment, "finished_at": moment},
            "decision_bundle_v2.json": bundle,
            "portfolio-private/account_snapshot.json": {"as_of": moment, "account_value_krw": 10000000, "positions": []},
            "portfolio-private/proposed_orders.json": {"orders": [{"canonical_ticker": self.ticker, "side": code, "estimated_qty": qty, "delta_krw_now": 500000 if code == "BUY" else -500000}]},
        }.items():
            atomic_write_json(run / filename, payload)
        return run

    def request(self, method, url, **kwargs):
        self.calls.append((method, url))
        assert url.startswith("https://openapivts.koreainvestment.com:29443/")
        assert kwargs["allow_redirects"] is False
        if url.endswith("tokenP"):
            return Response({"access_token": "fixture-token", "expires_in": 86400})
        if method == "POST":
            body = kwargs["json"]
            if "ORGN_ODNO" in body:
                self.orders[body["ORGN_ODNO"]]["cancelled"] = True
                return Response({"rt_cd": "0", "output": {"ODNO": "cancel-1", "KRX_FWDG_ORD_ORGNO": "001"}})
            identity = str(len(self.orders) + 1)
            self.orders[identity] = {"body": body, "time": self.now, "filled": 0, "amount": 0, "cancelled": False,
                                      "side": "BUY" if kwargs["headers"]["tr_id"] in {"VTTC0012U", "VTTT1002U"} else "SELL"}
            if self.lost:
                raise TimeoutError("PRIVATE_TRANSPORT_MESSAGE")
            return Response({"rt_cd": "0", "output": {"ODNO": identity, "KRX_FWDG_ORD_ORGNO": "001"}})
        rows = []
        for identity, order in self.orders.items():
            body, moment = order["body"], order["time"]
            remaining = 0 if order["cancelled"] else int(body["ORD_QTY"]) - order["filled"]
            common = {"odno": identity, "pdno": body["PDNO"], "sll_buy_dvsn_cd": "02" if order["side"] == "BUY" else "01"}
            if self.market == "KR":
                rows.append({**common, "ord_dt": moment.strftime("%Y%m%d"), "ord_tmd": moment.strftime("%H%M%S"),
                    "ord_unpr": body["ORD_UNPR"], "ord_qty": body["ORD_QTY"], "tot_ccld_qty": str(order["filled"]),
                    "rmn_qty": str(remaining), "cncl_yn": "Y" if order["cancelled"] else "N", "tot_ccld_amt": str(order["amount"])})
            else:
                seoul = moment.astimezone(ZoneInfo("Asia/Seoul"))
                rows.append({**common, "ord_dt": moment.strftime("%Y%m%d"), "dmst_ord_dt": seoul.strftime("%Y%m%d"), "thco_ord_tmd": seoul.strftime("%H%M%S"),
                    "ovrs_excg_cd": "NASD", "tr_crcy_cd": "USD", "ft_ord_qty": body["ORD_QTY"], "ft_ord_unpr3": body["OVRS_ORD_UNPR"],
                    "ft_ccld_qty": str(order["filled"]), "ft_ccld_amt3": str(order["amount"]), "nccs_qty": str(remaining),
                    "prcs_stat_name": "취소완료" if order["cancelled"] else "완료", "rjct_rson": ""})
        return Response({"rt_cd": "0", "output1" if self.market == "KR" else "output": rows})

    def close(self):
        pass

    @contextmanager
    def factory(self, market, path, clock, tickers, scope):
        assert market == self.market and scope == self.credentials.scope()
        cls = KisDemoClient if market == "KR" else KisDemoUSClient
        client = cls(self.credentials, session=self, pacer=RequestPacer(interval=0), utcnow=clock)
        broker = (KisPaperBroker(path, client, PaperOrderPolicy(("005930",)), paper_enabled=True, clock=clock) if market == "KR" else
                  KisPaperUSBroker(path, client, USPaperOrderPolicy((), allowed_tickers=("AAPL",)), paper_enabled=True, clock=clock))
        try:
            yield broker
        finally:
            broker.close()

    def gate(self, root, market, now):
        if market != self.market or not self.gate_open:
            raise ValueError("not verified")
        return self.credentials.scope()

    def quote(self, market, ticker, clock):
        return {"ticker": ticker[:6] if market == "KR" else ticker, "exchange": "NASD", "provider": "kis", "currency": "KRW" if market == "KR" else "USD",
            "session": "regular", "execution_ready": True, "instrument_type": "STOCK", "last_price": self.price,
            "observed_at": self.now.isoformat(), "ingested_at": self.now.isoformat()}

    def account(self, market, broker, terms, clock):
        suffix = "krw" if market == "KR" else "usd"
        return {"environment": "demo", "market": market, "currency": "KRW" if market == "KR" else "USD", "account_scope": self.credentials.scope(), "complete": True,
            "observed_at": self.now.isoformat(), "ingested_at": self.now.isoformat(), f"nav_{suffix}": 10000000, f"cash_{suffix}": 9000000,
            "positions": [{"ticker": terms["ticker"], "exchange": "NASD", "quantity": 10, "sellable_quantity": 10, f"market_value_{suffix}": self.price*10}],
            f"cash_only_buying_power_{suffix}": 9000000, "cash_only_buying_quantity": 100, "capacity_ticker": terms["ticker"], "capacity_limit_price": terms["limit_price"], "capacity_exchange": "NASD"}

    def tick(self, **kwargs):
        return runtime.tick(self.archive, self.root, self.validation, clock=lambda: self.now, broker_factory=self.factory,
            quote_loader=kwargs.pop("quote_loader", self.quote), account_loader=kwargs.pop("account_loader", self.account),
            gate=kwargs.pop("gate", self.gate), tickers={"KR": ("005930.KS",), "US": ("AAPL",)}, **kwargs)["markets"][self.market]

    def fill(self, identity="1", qty=1, amount=None):
        self.orders[identity].update(filled=qty, amount=amount if amount is not None else self.price * qty)


@pytest.fixture(params=["KR", "US"])
def h(tmp_path, request):
    return Harness(tmp_path, request.param)


def test_gate_independent_no_client_before_success_and_closed_no_network(h):
    h.gate_open = False
    assert h.tick()["status"] == "WAITING_VALIDATION"
    assert not h.calls and not list(h.root.glob("*.sqlite"))
    h.gate_open = True
    assert h.tick(session_resolver=lambda **kw: {"source": "exchange_calendars", "is_open": False, "phase": "closed"})["status"] == "MARKET_CLOSED"
    assert not h.calls


def test_real_broker_lifecycle_restart_duplicate_and_marked_pnl(h):
    first = h.tick()
    assert first["orders"][0]["status"] == "ACKNOWLEDGED"
    assert first["performance"]["status"] == "NO_FILLS"
    h.now += timedelta(seconds=20)
    h.fill(amount=h.price - 1)
    second = h.tick()
    assert len(h.orders) == 1 and second["orders"][0]["status"] == "FILLED"
    assert second["performance"]["gross_pnl"] == 1
    assert second["performance"]["net_pnl"] is None
    h.tick()
    assert len(h.orders) == 1
    h.now += timedelta(seconds=20)
    h.source("fixture-2", action="EXIT_NOW", qty=5)
    sold = h.tick()
    assert sold["orders"][-1]["quantity"] == 1  # Never sell unrelated/probe holdings.
    h.now += timedelta(seconds=20)
    h.fill("2", amount=h.price + 2)
    final = h.tick()
    assert final["owned"][h.ticker] == 0 and final["performance"]["gross_pnl"] == 3
    assert len(h.orders) == 2


def test_unfilled_cancel_after_five_minutes_ack_not_confirmation(h):
    h.tick()
    h.now += timedelta(minutes=5)
    pending = h.tick()
    assert pending["orders"][0]["status"] == "OPEN"
    assert pending["orders"][0]["cancel_status"] == "ACKNOWLEDGED"
    h.now += timedelta(minutes=1)
    final = h.tick()
    assert final["orders"][0]["status"] == "CANCELLED"
    assert final["orders"][0]["cancel_status"] == "CONFIRMED"
    assert len(h.orders) == 1


def test_unknown_response_never_replayed_or_followed_by_new_order(h):
    h.lost = True
    first = h.tick()
    assert first["orders"][0]["status"] == "UNKNOWN"
    h.now += timedelta(seconds=20)
    h.source("fixture-2")
    again = h.tick()
    assert "AMBIGUOUS_ORDER" in again["blockers"]
    assert len(h.orders) == 1
    assert "PRIVATE_TRANSPORT_MESSAGE" not in json.dumps(again)


def test_partial_fill_aggregates_once_and_cancel_remainder(tmp_path):
    h = Harness(tmp_path, "US")
    h.source(qty=2)
    h.tick()
    h.now += timedelta(seconds=20)
    h.fill(qty=1, amount=199)
    assert h.tick()["owned"]["AAPL"] == 1
    h.now += timedelta(minutes=5)
    h.tick()
    h.now += timedelta(minutes=1)
    row = h.tick()
    assert row["owned"]["AAPL"] == 1
    assert row["performance"]["gross_pnl"] == 1
    assert row["orders"][0]["status"] == "CANCELLED"


@pytest.mark.parametrize("change", [
    lambda b: b.update(generated_at="2026-10-20T10:00:00+09:00"),
    lambda b: b.update(generated_at="bad"),
    lambda b: b["strategy_table"][0].update(market_data_asof=None),
    lambda b: b["strategy_table"][0].update(market_data_asof="2026-10-20T10:00:00+09:00"),
    lambda b: b["strategy_table"][0]["quality"].update(execution_ready=False),
    lambda b: b["strategy_table"][0]["raw_codes"].update(decision_now="WAIT"),
])
def test_invalid_future_missing_or_unapproved_strategy_cannot_order(h, change):
    h.source(changes=change)
    h.tick()
    assert not h.orders


def test_expired_source_halt_and_foreign_account_never_order(h):
    h.now += timedelta(minutes=3)
    assert h.tick()["status"] == "WAITING_SIGNAL"
    h.source("fixture-2")
    (h.root / "HALT").touch()
    assert "HALTED" in h.tick()["blockers"]
    assert not h.orders


def test_account_scope_and_stale_quote_block_native_broker(h):
    def wrong(*args):
        account = h.account(*args)
        account["account_scope"] = "wrong"
        return account
    assert h.tick(account_loader=wrong)["orders"][0]["status"] == "BLOCKED"
    assert not h.orders
    h.source("fixture-2")
    def stale(*args):
        quote = h.quote(*args)
        quote["observed_at"] = (h.now - timedelta(minutes=3)).isoformat()
        return quote
    h.tick(quote_loader=stale)
    assert not h.orders


def test_halt_still_cancels_existing_order(h):
    h.tick()
    (h.root / "HALT").touch()
    h.now += timedelta(seconds=20)
    value = h.tick()
    assert value["orders"][0]["cancel_status"] == "ACKNOWLEDGED"
    assert len(h.orders) == 1


def test_gate_loss_cleans_up_without_starting_new_order(h):
    h.tick()
    h.gate_open = False
    h.now += timedelta(seconds=20)
    assert h.tick()["orders"][0]["cancel_status"] == "ACKNOWLEDGED"
    assert len(h.orders) == 1


@pytest.mark.parametrize("config", ["broken", [], {}, {"mode": "real", "enabled": True, "real_orders_enabled": False}, {"mode": runtime.MODE, "enabled": True, "real_orders_enabled": True}])
def test_explicit_demo_only_activation_required(h, config):
    (h.root / "enabled.json").write_text(config if isinstance(config, str) else json.dumps(config))
    assert h.tick()["status"] == "DISABLED"
    assert not h.calls


def test_missing_and_forged_validation_proof_never_opens_gate(tmp_path):
    now = datetime.fromisoformat("2026-10-19T10:00:00+09:00")
    with pytest.raises((ValueError, TypeError)):
        runtime.validation_gate(tmp_path, "KR", now)
    from tradingagents.execution import demo_validation as dv
    state = dv._new("KR", now)
    state.update(status="VERIFIED", finished=True)
    state["stages"] = {name: {"verified": True, "observed_at": now.isoformat(), "source": "KIS_DEMO_BROKER_ACK" if name == "submitted" else "KIS_DEMO_BROKER_REPORT"} for name in dv.STAGES}
    atomic_write_json(tmp_path / "kr-campaign.json", state)
    with pytest.raises(ValueError):
        runtime.validation_gate(tmp_path, "KR", now)


@pytest.mark.parametrize("raw", [None, "bad", "NaN", "-1", "0", "201"])
def test_missing_invalid_impossible_fill_money_not_invented(raw):
    assert execution_notional({"ft_ccld_amt3": raw}, 1, {"side": "BUY", "limit_price": 200}, market="US") is None


def test_missing_fill_amount_stays_incomplete_then_recovers(h):
    h.tick()
    h.now += timedelta(seconds=20)
    h.fill(amount="bad")
    assert h.tick()["performance"]["status"] == "INCOMPLETE"
    h.now += timedelta(seconds=20)
    h.fill(amount=h.price-1)
    assert h.tick()["performance"]["gross_pnl"] == 1


def test_us_budget_only_needs_dated_fx_and_no_usd_is_invented(tmp_path):
    h = Harness(tmp_path, "US")
    run = h.source(qty=None)
    assert "BUDGET_FX_UNVERIFIED" in h.tick()["blockers"]
    snapshot = runtime.read(run / "portfolio-private/account_snapshot.json")
    snapshot["cash_diagnostics"] = {"fx_quote": {"base_currency": "USD", "quote_currency": "KRW", "kind": "BROKER_REFERENCE_RATE",
        "source": "kis.inquire_present_balance.output2.frst_bltn_exrt", "observed_at": h.now.isoformat(), "rate": 1400}}
    atomic_write_json(run / "portfolio-private/account_snapshot.json", snapshot)
    assert h.tick()["orders"][0]["quantity"] == 1


def test_cashflow_regression_is_not_a_performance_result(h):
    h.tick()
    h.now += timedelta(seconds=20)
    h.fill(amount=h.price-1)
    h.tick()
    path = h.root / f"{h.market.lower()}-strategy.sqlite"
    with sqlite3.connect(path) as db:
        identity, moment, raw = db.execute("SELECT * FROM paper_observations LIMIT 1").fetchone()
        row = json.loads(raw)
        row["fill_notional"] -= 1
        db.execute("INSERT INTO paper_observations VALUES (?,?,?)", (identity, (h.now+timedelta(seconds=1)).isoformat(), json.dumps(row)))
    h.now += timedelta(seconds=10)
    assert h.tick()["blockers"] == ["RUNTIME_EVIDENCE_UNVERIFIED"]


def test_daily_attempt_budget_and_completed_results_stay_visible_closed(h):
    for index in range(1, 4):
        h.source(f"fixture-{index}")
        h.tick()
        h.now += timedelta(seconds=15)
        h.fill(str(index))
        h.tick()
        h.now += timedelta(seconds=15)
    h.source("fixture-4")
    value = h.tick()
    assert len(h.orders) == 3 and "DAILY_ORDER_LIMIT" in value["blockers"]
    closed = h.tick(session_resolver=lambda **kw: {"source": "exchange_calendars", "is_open": False, "phase": "closed"})
    assert closed["status"] == "MARKET_CLOSED" and closed["order_counts"]["FILLED"] == 3
    assert closed["performance"]["status"] == "INCOMPLETE"
    assert closed["performance_history"][-1]["status"] == "AVAILABLE"


def test_valid_gate_requires_owner_and_original_terminal_broker_proofs(tmp_path):
    from tradingagents.execution import demo_validation as dv
    now = datetime.fromisoformat("2026-10-19T10:00:00+09:00")
    state = dv._new("KR", now)
    state.update(status="VERIFIED", finished=True, blocker="")
    state["stages"] = {name: {"verified": True, "observed_at": now.isoformat(), "source": "KIS_DEMO_BROKER_ACK" if name == "submitted" else "KIS_DEMO_BROKER_REPORT"} for name in dv.STAGES}
    with sqlite3.connect(tmp_path / "kr-vts.sqlite") as db:
        db.executescript("""CREATE TABLE owner(scope TEXT); INSERT INTO owner VALUES ('validated-scope');
            CREATE TABLE requests(id TEXT,status TEXT,response TEXT,created_at TEXT);
            CREATE TABLE paper_intents(id TEXT,terms TEXT); CREATE TABLE order_state(id TEXT,status TEXT,filled INTEGER,remaining INTEGER);
            CREATE TABLE paper_observations(id TEXT,observed_at TEXT,evidence TEXT); CREATE TABLE reconciliation_issues(id TEXT);""")
        for number, status in ((1, "CANCELLED"), (2, "FILLED")):
            identity = f"{dv.CAMPAIGN}:KR:{number}"
            terms = {"ticker": "069500", "side": "BUY", "quantity": 1, "limit_price": 40000}
            state["orders"].append({"intent_id": identity, "purpose": "cancel" if number == 1 else "fill", "prepared_at": now.isoformat(), "terms": terms, "done": True, "cancel_attempted": number == 1})
            db.execute("INSERT INTO requests VALUES (?,?,?,?)", (identity, "ACKNOWLEDGED", '{"broker_order_id":"fixture"}', now.isoformat()))
            db.execute("INSERT INTO paper_intents VALUES (?,?)", (identity, json.dumps(terms)))
            db.execute("INSERT INTO order_state VALUES (?,?,?,?)", (identity, status, number-1, 0))
            db.execute("INSERT INTO paper_observations VALUES (?,?,?)", (identity, now.isoformat(), json.dumps({"status": status, "filled_qty": number-1, "remaining_qty": 0})))
        db.execute("INSERT INTO requests VALUES (?,?,?,?)", (f"cancel:{dv.CAMPAIGN}:KR:1", "ACKNOWLEDGED", '{}', now.isoformat()))
    atomic_write_json(tmp_path / "kr-campaign.json", state)
    assert runtime.validation_gate(tmp_path, "KR", now) == "validated-scope"
    with sqlite3.connect(tmp_path / "kr-vts.sqlite") as db:
        db.execute("INSERT INTO reconciliation_issues VALUES ('unresolved')")
    with pytest.raises(ValueError):
        runtime.validation_gate(tmp_path, "KR", now)


def test_reset_or_manual_reduction_cannot_leave_fictitious_performance(h):
    h.tick()
    h.now += timedelta(seconds=20)
    h.fill()
    def reset(*args):
        account = h.account(*args)
        account["positions"] = []
        return account
    value = h.tick(account_loader=reset)
    assert "STRATEGY_ACCOUNT_POSITION_UNVERIFIED" in value["blockers"]
    assert value["performance"]["status"] == "INCOMPLETE"
    assert value["performance"]["gross_pnl"] is None
    assert len(h.orders) == 1


def test_strategy_consumption_and_terms_cannot_be_reset(h):
    h.tick()
    with sqlite3.connect(h.root / f"{h.market.lower()}-strategy.sqlite") as db:
        with pytest.raises(sqlite3.IntegrityError):
            db.execute("UPDATE strategy_attempts SET terms='{}'")
        with pytest.raises(sqlite3.IntegrityError):
            db.execute("DELETE FROM strategy_attempts")
    h.tick()
    assert len(h.orders) == 1


def test_account_read_crossing_entry_cutoff_does_not_submit(h):
    h.now = h.now.replace(hour=15, minute=19 if h.market == "KR" else 49, second=55)
    h.source()
    def delayed(*args):
        account = h.account(*args)
        h.now += timedelta(seconds=10)
        return account
    value = h.tick(account_loader=delayed)
    assert "SESSION_EDGE" in value["blockers"] and not h.orders


def test_halt_created_during_read_prevents_submission(h):
    def halt(*args):
        (h.root / "HALT").touch()
        return h.account(*args)
    value = h.tick(account_loader=halt)
    assert "HALTED" in value["blockers"] and not h.orders
