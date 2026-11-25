from contextlib import contextmanager
from datetime import datetime, timedelta
import json
import sqlite3
import sys

import pytest

from tradingagents.atomic_io import atomic_write_json
from tradingagents.execution import demo_runtime, kis_paper, kis_paper_us, paper_runtime, prism_autotrader
from tradingagents.execution.kis_demo import KisDemoClient, RequestPacer
from tradingagents.execution.kis_demo_us import KisDemoUSClient
from tradingagents.execution.kis_strategy_limits import APPROVED_CAPS, DAILY_LIMIT_REVISION
from tradingagents import local_automation
from tests.execution.test_demo_strategy_plan import Harness, native_source, regular_session
from tests.execution.test_kis_strategy_limits import approved_config


def read(path):
    return json.loads(path.read_bytes())


class NormalCli:
    def __init__(self, tmp_path, monkeypatch, market):
        self.h = h = Harness(tmp_path, market)
        self.state, self.runtime = tmp_path / "state", tmp_path / "runtime"
        h.root, h.validation = self.state / "kis-strategy", self.state / "kis-validation"
        self.lane = self.state / "autotrader"
        self.lane_policy = self.lane / "enabled.json"
        self.receipt = self.lane / f"{market.lower()}-vts-candidates.json"
        self.journal = h.root / f"{market.lower()}-strategy.sqlite"
        self.monkeypatch = monkeypatch
        self.open = True
        self.bar_only = False
        self.account_cash = None
        self.other_holdings = []
        self.prepared_at_wire = []
        self.report_dates = []
        prod_tick, candidate_tick = demo_runtime.tick, prism_autotrader.run_autotrader_tick

        def session(*, market, now_local):
            base = regular_session(market=market.upper(), now_local=now_local)
            return base if self.open else {**base, "is_open": False, "phase": "pre_market"}

        monkeypatch.setattr(local_automation, "prepare_environment", lambda: None)
        monkeypatch.setattr(demo_runtime, "tick", lambda *args: prod_tick(*args, clock=lambda: h.now))
        monkeypatch.setattr(demo_runtime, "universe", lambda: {key: (h.ticker,) if key == market else () for key in demo_runtime.ZONES})
        monkeypatch.setattr(demo_runtime, "_runtime_session", session)
        monkeypatch.setattr(paper_runtime, "_runtime_session", session)
        monkeypatch.setattr(kis_paper, "market_session_state", session)
        monkeypatch.setattr(kis_paper_us, "market_session_state", session)
        monkeypatch.setattr(demo_runtime, "broker_context", self.broker)
        monkeypatch.setattr(demo_runtime, "current_quote", self.quote)
        monkeypatch.setattr(demo_runtime.validation, "current_account", self.account)
        monkeypatch.setattr(demo_runtime, "validation_gate", h.gate)
        monkeypatch.setattr(prism_autotrader, "run_autotrader_tick", lambda *args: candidate_tick(*args, clock=lambda: h.now))
        monkeypatch.setattr(prism_autotrader, "_default_broker_executor", lambda *_: pytest.fail("Candidate used the shadow simulator"))
        original_request = h.request

        def request(method, url, **kwargs):
            if method == "POST" and not url.endswith("tokenP") and "ORGN_ODNO" not in kwargs["json"]:
                with sqlite3.connect(self.journal) as reader:
                    attempt = reader.execute("SELECT id FROM strategy_attempts ORDER BY prepared_at DESC LIMIT 1").fetchone()[0]
                    evidence = reader.execute("SELECT evidence FROM strategy_source_evidence WHERE id=?", (attempt,)).fetchone()
                    wire = reader.execute("SELECT status FROM requests WHERE id=?", (attempt,)).fetchone()
                    assert wire == ("UNKNOWN",)
                    for table in ("intents", "paper_intents"):
                        assert reader.execute(f"SELECT 1 FROM {table} WHERE id=?", (attempt,)).fetchone()
                    self.prepared_at_wire.append(json.loads(evidence[0]) if evidence else {})
            response = original_request(method, url, **kwargs)
            if method == "GET":
                params = kwargs["params"]
                date = params.get("INQR_STRT_DT") or params.get("ORD_STRT_DT")
                field = "output1" if h.market == "KR" else "output"
                if date:
                    payload = response.json()
                    payload[field] = [row for row in payload[field] if row["ord_dt"] == date]
            return response

        monkeypatch.setattr(h, "request", request)
        client_type = KisDemoClient if market == "KR" else KisDemoUSClient
        original_orders = client_type.orders

        def orders(client, date):
            self.report_dates.append(date)
            return original_orders(client, date)

        monkeypatch.setattr(client_type, "orders", orders)
        atomic_write_json(self.lane_policy, {"mode": "kis_vts", "enabled": True, "live_orders_confirmed": False})
        atomic_write_json(self.state / "notifications/kis-strategy-enabled.json", {
            "mode": demo_runtime.MODE, "enabled": True, "real_orders_enabled": False,
            "enabled_at": (h.now - timedelta(days=1)).isoformat(),
        })

    @contextmanager
    def broker(self, market, path, clock, tickers, scope, *, limits=None, policy_revision=None):
        h = self.h
        assert market == h.market and scope == h.credentials.scope()
        client_type = KisDemoClient if market == "KR" else KisDemoUSClient
        client = client_type(h.credentials, session=h, pacer=RequestPacer(interval=0), utcnow=clock)
        broker = demo_runtime.make_strategy_broker(market, path, client, clock, tickers, limits, revision=policy_revision)
        try:
            yield broker
        finally:
            broker.close()
            client.close()

    def account(self, market, broker, terms, clock):
        h = self.h
        result = h.account(market, broker, terms, clock)
        native = "krw" if market == "KR" else "usd"
        qty = sum(row["filled"] * (1 if row["side"] == "BUY" else -1) for row in h.orders.values())
        if qty:
            result["positions"][0].update(quantity=qty, sellable_quantity=qty, **{f"market_value_{native}": qty * h.price})
        else:
            result["positions"] = []
        result["positions"].extend(self.other_holdings)
        if self.account_cash is not None:
            result[f"cash_only_buying_power_{native}"] = result[f"cash_{native}"] = self.account_cash
        return result

    def quote(self, market, ticker, clock, *, require_top_of_book=False):
        quote = self.h.quote(market, ticker, clock)
        if self.bar_only:
            return {**quote, "quote_basis": "BAR_ONLY"}
        return {**quote, "quote_basis": "DATED_BOOK", "orderbook_date_basis": "EXPLICIT",
                "orderbook_at": self.h.now.isoformat(), "bid": self.h.price, "ask": self.h.price}

    def source(self, suffix, *, action="STARTER_NOW", parent=None, complete=True, reference=None, cohort=False):
        h = self.h
        identity = f"{h.now:%Y%m%dT%H%M%S}_{suffix}"
        contract = {"ticker": h.ticker, "analysis_asof": (h.now - timedelta(hours=1)).isoformat(),
                    "action_if_triggered": "STARTER", "entry_valid_until": (h.now + timedelta(hours=4)).isoformat(),
                    "entry_action_base": "WAIT", "risk_action": "HOLD", "invalid_if_intraday_below": h.price * .95,
                    "breakout_level": h.price * .99}
        path, _ = native_source(h, identity, action=action, contract=contract)
        manifest = read(path / "run.json")
        manifest["settings"]["run_mode"] = "overlay_only" if parent else "full"
        if parent:
            manifest["overlay_source_run_id"] = parent.name
        manifest["active_universe"] = {"mode": "full_required_coverage", "coverage": {"complete": complete}}
        manifest["tickers"] = [{"ticker": h.ticker, "status": "success",
                                "artifacts": {"analysis_json": f"tickers/{h.ticker}/analysis.json"}}]
        atomic_write_json(path / "run.json", manifest)
        bundle = read(path / "decision_bundle_v2.json")
        bundle["strategy_table"][0].update(provider="kis_microstructure", market_data_basis="EXECUTION_CONTEXT")
        atomic_write_json(path / "decision_bundle_v2.json", bundle)
        candidate_file = path / "portfolio-private/portfolio_candidates.json"
        document = read(candidate_file)
        item = document["candidates"][0]
        item.update(stance="BULLISH", confidence=.9, thesis_strength=.9, setup_quality="COMPELLING",
                    suggested_action_if_triggered="STARTER_IF_TRIGGERED", sector="Tech")
        item["instrument"].update(country=h.market, currency="KRW" if h.market == "KR" else "USD")
        if reference is not False:
            item["data_health"]["price_reference"] = {
            "currency": "KRW" if h.market == "KR" else "USD", "basis": "unadjusted", "source": "kis.fixture",
            "price": h.price if reference is None else reference, "observed_at": manifest["finished_at"],
            }
            item["data_health"]["price_reference"]["source"] = ("kis.domestic_time_itemchartprice" if h.market == "KR"
                                                               else "kis.overseas_time_itemchartprice")
            update_path = path / "tickers" / h.ticker / "execution_update.json"
            update = read(update_path)
            update["price_reference"] = item["data_health"]["price_reference"]
            atomic_write_json(update_path, update)
        if cohort:
            extra = [f"{100_000+i}.KS" if h.market == "KR" else f"X{i:02d}" for i in range(29)]
            selected = [h.ticker, *extra]
            active = manifest["active_universe"]
            active.update(selected_tickers=selected, market=h.market, asof=manifest["started_at"])
            active["coverage"].update(selection_complete=True, analysis_complete=complete,
                                      analysis_expected_count=30, analysis_successful_count=30)
            for ticker in extra:
                path_rel = f"tickers/{ticker}/analysis.json"
                atomic_write_json(path / path_rel, {"status": "success", "ticker": ticker})
                manifest["tickers"].append({"ticker": ticker, "status": "success", "artifacts": {"analysis_json": path_rel}})
                document["candidates"].append({"instrument": {**item["instrument"], "canonical_ticker": ticker}})
                bundle["strategy_table"].append({"ticker": ticker, "raw_codes": {"decision_now": "WAIT"}})
            atomic_write_json(path / "run.json", manifest)
            atomic_write_json(path / "decision_bundle_v2.json", bundle)
        atomic_write_json(candidate_file, document)
        self.configure()
        return path

    def configure(self, *, native=True, candidate=True, daily=False, universe=False):
        config = approved_config({"mode": demo_runtime.MODE, "enabled": True, "real_orders_enabled": False})
        if native:
            config["allocation_mode"] = demo_runtime.demo_strategy_plan.MODE
        if candidate:
            config["prism_candidate_gate"] = True
        if daily:
            config.update(native_limit_revision=DAILY_LIMIT_REVISION, native_daily_buy_limits=APPROVED_CAPS)
        if universe:
            config["native_active_universe"] = True
        atomic_write_json(self.h.root / "enabled.json", config)

    def run(self, command):
        self.monkeypatch.setattr(sys, "argv", ["local_automation", command, "--archive-dir", str(self.h.archive),
                             "--state-dir", str(self.state), "--runtime-dir", str(self.runtime)])
        assert local_automation.main() == 0
        path = (self.lane / f"autotrader-{self.h.market.lower()}-status.json" if command == "autotrader"
                else self.h.archive / "paper/kis-strategy-runtime.json")
        receipt = read(path)
        return receipt if command == "autotrader" else receipt["markets"][self.h.market]

    def fill_events(self):
        return sorted(event["state"] for path in (self.state / "notifications/events").glob("*.json")
                      if (event := read(path))["event"] == "FILL")


@pytest.fixture(params=["KR", "US"])
def cli(tmp_path, monkeypatch, request):
    return NormalCli(tmp_path, monkeypatch, request.param)


def test_offhours_queue_native_buy_and_deterministic_exit_use_one_vts_journal(cli):
    h = cli.h
    h.now = h.now.replace(hour=8 if h.market == "KR" else 9, minute=58 if h.market == "KR" else 28)
    baseline = cli.source("production-full", action="WAIT")
    cli.open = False
    producer = cli.run("autotrader")
    receipt = read(cli.receipt)
    assert producer["entries_queued"] == [h.ticker] and producer["entries_executed"] == []
    assert cli.run("strategy-kis")["status"] == "MARKET_CLOSED" and h.calls == []
    h.now = h.now.replace(hour=10, minute=1)
    cli.open = True
    source = cli.source("production-overlay", parent=baseline)
    first = cli.run("strategy-kis")
    assert first["source_run_id"] == source.name
    assert first["orders"][0]["status"] == "ACKNOWLEDGED", first
    assert cli.prepared_at_wire[0]["prism_candidate"]["baseline_id"] == baseline.name
    assert first["owned"][h.ticker] == 0 and first["performance"]["status"] == "NO_FILLS" and cli.fill_events() == []
    assert read(cli.receipt) == receipt  # The strategy never rewrites the candidate queue.

    h.fill()
    h.now += timedelta(seconds=20)
    confirmed = cli.run("strategy-kis")
    assert confirmed["orders"][0]["status"] == "FILLED" and confirmed["owned"][h.ticker] == 1
    assert cli.fill_events() == ["FILLED"] and len(h.orders) == 1

    h.price *= .9
    h.now += timedelta(seconds=15)
    cli.source("exit-overlay", action="EXIT_NOW", parent=baseline)
    producer = cli.run("autotrader")
    assert producer["risk_exit_candidates"] == 1 and producer["exits_executed"] == []
    cli.account_cash = 0  # Verified risk reduction does not need BUY cash.
    sell = cli.run("strategy-kis")
    assert sell["orders"][-1]["status"] == "ACKNOWLEDGED", sell
    assert sell["owned"][h.ticker] == 1 and cli.fill_events() == ["FILLED"]
    assert [item["side"] for item in h.orders.values()] == ["BUY", "SELL"]
    assert cli.prepared_at_wire[-1]["prism_candidate"]["side"] == "SELL"

    h.fill("2")
    h.now += timedelta(seconds=25)
    reconciled = cli.run("strategy-kis")
    assert reconciled["owned"][h.ticker] == 0 and reconciled["orders"][-1]["status"] == "FILLED"
    assert reconciled["evaluation"]["realized_net_pnl"] is None
    assert cli.fill_events() == ["FILLED", "FILLED"]
    cli.run("strategy-kis")
    assert len(h.orders) == 2 and cli.fill_events() == ["FILLED", "FILLED"]


def test_indeterminate_wire_response_is_queried_on_restart_without_economic_effect(cli):
    h = cli.h
    cli.source("production-full")
    assert cli.run("autotrader")["entries_queued"] == [h.ticker]
    h.lost = True
    first = cli.run("strategy-kis")
    assert first["orders"][0]["status"] == "UNKNOWN", first
    assert len(cli.prepared_at_wire) == 1 and first["owned"][h.ticker] == 0
    date = h.now.strftime("%Y%m%d")
    h.fill()  # Even an identical broker row cannot prove the missing local ACK.
    h.now += timedelta(days=1)
    cli.configure(candidate=False)
    cli.report_dates.clear()
    restarted = cli.run("strategy-kis")
    assert "AMBIGUOUS_ORDER" in restarted["blockers"] and cli.report_dates == [date]
    assert restarted["owned"][h.ticker] == 0 and restarted["performance"]["status"] == "NO_FILLS"
    assert len(h.orders) == 1 and cli.fill_events() == []


def test_restart_reconciles_preexisting_partial_and_never_resends(cli):
    h = cli.h
    h.source(qty=2)
    cli.configure(native=False, candidate=False)
    first = cli.run("strategy-kis")
    assert first["orders"][0]["status"] == "ACKNOWLEDGED" and first["orders"][0]["quantity"] == 2, first
    h.fill(qty=1)
    h.now += timedelta(seconds=20)
    cli.configure()
    # This fixture uses the separate five-minute HALT, also effective for hints.
    (cli.lane / "HALT").touch()
    first_restart = cli.run("strategy-kis")
    assert first_restart["orders"][0]["status"] == "PARTIAL" and first_restart["owned"][h.ticker] == 1
    assert cli.fill_events() == ["PARTIAL"] and len(h.orders) == 1
    assert h.orders["1"]["cancelled"] is False  # The five-minute HALT does not cancel a native-only order.
    h.now += timedelta(seconds=20)
    assert cli.run("strategy-kis")["orders"][0]["status"] == "PARTIAL"
    assert cli.fill_events() == ["PARTIAL"] and len(h.orders) == 1


def test_candidate_halt_cancels_outstanding_candidate_order_before_the_timeout(cli):
    h = cli.h
    cli.source("production-full")
    assert cli.run("autotrader")["entries_queued"] == [h.ticker]
    assert cli.run("strategy-kis")["orders"][0]["status"] == "ACKNOWLEDGED"
    (cli.lane / "HALT").touch()
    h.now += timedelta(seconds=10)
    halted = cli.run("strategy-kis")
    assert "PRISM_CANDIDATE_HALTED" in halted["blockers"]
    assert halted["orders"][0]["status"] == "OPEN" and halted["orders"][0]["cancel_status"] == "ACKNOWLEDGED"
    assert h.orders["1"]["cancelled"] is True
    h.now += timedelta(seconds=10)
    final = cli.run("strategy-kis")
    assert final["orders"][0]["status"] == "CANCELLED" and final["orders"][0]["cancel_status"] == "CONFIRMED"
    assert final["owned"][h.ticker] == 0 and cli.fill_events() == []


def test_preexisting_hold_on_5m_transport_keeps_candidate_forward_observations(cli):
    h = cli.h
    cli.source("production-full")
    (cli.lane / "HALT").touch()
    producer = cli.run("autotrader")
    assert producer["transmission_halted"] and producer["broker_orders_sent"] == 0
    assert producer["entries_queued"] == [h.ticker] and producer["forward_observations"] == 1
    observations = list((cli.lane / "forward-observations" / h.market.lower()).glob("*.json"))
    assert len(observations) == 1 and read(observations[0])["mode"] == "observe_only"
    assert cli.run("strategy-kis")["blockers"] == ["PRISM_CANDIDATE_HALTED"]
    assert not h.orders and not cli.fill_events()
    (cli.lane / "HALT").unlink()  # Separate, simulated activation cannot reuse the paused receipt.
    assert "PRISM_CANDIDATE_NOT_ADMITTED" in cli.run("strategy-kis")["blockers"]
    assert not h.orders


@pytest.mark.parametrize("stop", ["halt", "expiry"])
def test_candidate_still_has_to_be_valid_after_transport_pacing(cli, monkeypatch, stop):
    h = cli.h
    if stop == "expiry":
        regular = h.now
        h.now -= timedelta(hours=18) - timedelta(seconds=50)
        cli.open = False
        baseline = cli.source("offhours-full")
        assert cli.run("autotrader")["entries_queued"] == [h.ticker]
        h.now, cli.open = regular, True
        cli.source("production-overlay", parent=baseline)
    else:
        cli.source("production-full")
        assert cli.run("autotrader")["entries_queued"] == [h.ticker]
    original_wait = RequestPacer.wait

    def wait(pacer):
        original_wait(pacer)
        with sqlite3.connect(cli.journal) as reader:
            if reader.execute("SELECT 1 FROM requests WHERE status='UNKNOWN'").fetchone():
                if stop == "halt":
                    (cli.lane / "HALT").touch()
                else:
                    h.now += timedelta(seconds=46)

    monkeypatch.setattr(RequestPacer, "wait", wait)
    result = cli.run("strategy-kis")
    assert result["orders"][0]["status"] == "NOT_SENT", result
    assert (cli.lane / "HALT").exists() == (stop == "halt")
    assert not h.orders and not cli.fill_events()


def test_offhours_repeated_publication_does_not_renew_entry_expiry(cli):
    h = cli.h
    cli.open = False
    cli.source("production-full", action="WAIT")
    assert cli.run("autotrader")["entries_queued"] == [h.ticker]
    receipt = read(cli.receipt)
    h.now += timedelta(minutes=1)
    cli.run("autotrader")
    next_receipt = read(cli.receipt)
    assert next_receipt["produced_at"] != receipt["produced_at"]
    assert next_receipt["entry_expires_at"] == receipt["entry_expires_at"]
    h.now += timedelta(hours=18)
    expired = cli.run("autotrader")
    assert expired["entry_research_expired"] and expired["entries_queued"] == []
    assert read(cli.receipt)["entry_expires_at"] == receipt["entry_expires_at"] and not h.calls


@pytest.mark.parametrize("condition", ["expired_entry", "older_lot"])
def test_verified_exit_recovers_after_entry_expiry_or_a_long_journal(cli, condition):
    h = cli.h
    full = cli.source("production-full")
    assert cli.run("autotrader")["entries_queued"] == [h.ticker]
    assert cli.run("strategy-kis")["orders"][0]["status"] == "ACKNOWLEDGED"
    h.fill()
    h.now += timedelta(seconds=5)
    assert cli.run("strategy-kis")["owned"][h.ticker] == 1
    if condition == "older_lot":
        with sqlite3.connect(cli.journal) as db:
            ticker, run_id, terms = db.execute("SELECT ticker,run_id,terms FROM strategy_attempts").fetchone()
            db.executemany("INSERT INTO strategy_attempts VALUES (?,?,?,?,?,?)", [
                (f"interrupted-{i}", ticker, run_id, (h.now + timedelta(seconds=i + 1)).isoformat(), terms, "NOT_SENT")
                for i in range(101)
            ])
    h.now += timedelta(days=1)
    h.price *= .9
    cli.source("exit-source", action="EXIT_NOW", parent=full if condition == "expired_entry" else None)
    producer = cli.run("autotrader")
    assert producer["entry_research_expired"] is (condition == "expired_entry")
    assert producer["risk_exit_candidates"] == 1
    sell = cli.run("strategy-kis")
    assert sell["orders"][-1]["status"] == "ACKNOWLEDGED", sell
    assert [item["side"] for item in h.orders.values()] == ["BUY", "SELL"]
    assert sell["owned"][h.ticker] == 1 and cli.fill_events() == ["FILLED"]


@pytest.mark.parametrize("bad_reference", ["missing", "other_day", "daily_proxy", "same_order_quote"])
def test_offhours_conditional_without_native_reference_waits_for_a_verified_overlay(cli, bad_reference):
    h = cli.h
    regular = h.now
    h.now -= timedelta(hours=2)
    cli.open = False
    baseline = cli.source("offhours-full", action="WAIT", reference=False)
    path = baseline / "portfolio-private/portfolio_candidates.json"
    document = read(path)
    document["candidates"][0]["position_metrics"] = {"current_price": h.price * 1400}
    atomic_write_json(path, document)
    status = cli.run("autotrader")
    assert status["entries_waiting_for_native_price"] == 1
    assert read(cli.receipt)["entries"][h.ticker]["reference_price"] is None
    assert cli.run("strategy-kis")["status"] == "MARKET_CLOSED" and not h.calls
    cli.open, h.now = True, regular
    candidate_source = cli.source("first-overlay", parent=baseline, reference=False if bad_reference == "missing" else None)
    if bad_reference != "missing":
        path = candidate_source / "portfolio-private/portfolio_candidates.json"
        current = read(path)
        reference = current["candidates"][0]["data_health"]["price_reference"]
        if bad_reference == "other_day":
            reference["observed_at"] = (h.now - timedelta(days=1)).isoformat()
        elif bad_reference == "daily_proxy":
            reference["source"] = "yahoo.daily"
        else:
            reference["observed_at"] = h.now.isoformat()  # Exact timestamp of the order quote.
        atomic_write_json(path, current)
        update_path = candidate_source / "tickers" / h.ticker / "execution_update.json"
        update = read(update_path)
        update["price_reference"] = reference
        atomic_write_json(update_path, update)
    assert "PRISM_CANDIDATE_NOT_ADMITTED" in cli.run("strategy-kis")["blockers"]
    assert not h.orders
    h.now += timedelta(seconds=30)
    cli.source("priced-overlay", parent=baseline)
    assert cli.run("strategy-kis")["orders"][0]["status"] == "ACKNOWLEDGED"
    assert len(h.orders) == 1


@pytest.mark.parametrize("block", ["previous_session", "wrong_currency", "bar_only", "price_reversal", "none"])
def test_native_cohort_admission_rechecks_official_book_and_current_selection(cli, block, monkeypatch):
    h = cli.h
    regular = h.now
    if block == "previous_session":
        h.now -= timedelta(days=1)
    root = cli.source("cohort-full", cohort=True)
    if block == "previous_session":
        h.now = regular
        cli.source("current-overlay", parent=root, cohort=True)
    if block == "wrong_currency":
        path = root / "portfolio-private/portfolio_candidates.json"
        document = read(path)
        document["candidates"][-1]["instrument"]["currency"] = "JPY"
        atomic_write_json(path, document)
    cli.configure(candidate=False, daily=True, universe=True)
    # The regulatory source has the approved name but the static policy does not.
    monkeypatch.setattr(demo_runtime, "universe", lambda: {"KR": ("000660.KS",), "US": ("MSFT",)})
    if block == "bar_only":
        cli.bar_only = True
    if block == "price_reversal":
        h.price *= .98  # Still above invalidation, below the actual breakout.
    result = cli.run("strategy-kis")
    scope = result["allocation_diagnostics"]["daily_universe"]
    assert scope["entry_names"] == (0 if block in {"previous_session", "wrong_currency"} else 30)
    if block == "none":
        assert result["orders"][0]["status"] == "ACKNOWLEDGED" and len(h.orders) == 1, result
        assert cli.prepared_at_wire[0]["native_active_universe"]["side"] == "BUY"
    else:
        if block in {"price_reversal", "bar_only"}:
            why = "ENTRY_CURRENT_PRICE_NOT_CONFIRMED" if block == "price_reversal" else "KIS_TOP_OF_BOOK_UNVERIFIED"
            assert why in result["blockers"], result
        assert h.orders == {}


def test_daily_buy_revision_binds_existing_journal_and_caps_cost_after_restart(cli):
    h = cli.h
    h.price = APPROVED_CAPS[h.market] // 2

    def propose(source_id, *, action="STARTER_NOW"):
        run = h.source(source_id, action=action)
        path = run / "portfolio-private/proposed_orders.json"
        proposals = read(path)
        proposals["orders"][0]["delta_krw_now"] = h.price * (2 if action == "STARTER_NOW" else -2)
        atomic_write_json(path, proposals)

    propose("fixture-1")
    cli.configure(native=False, candidate=False)
    assert "KIS_DAILY_BUY_RISK_LIMIT" in cli.run("strategy-kis")["blockers"]
    assert not h.orders
    h.now += timedelta(days=1)
    propose("fixture-2")
    cli.configure(native=False, candidate=False, daily=True)
    assert cli.run("strategy-kis")["orders"][-1]["status"] == "ACKNOWLEDGED"
    h.fill()
    h.now += timedelta(seconds=10)
    propose("fixture-3")
    result = cli.run("strategy-kis")
    assert "KIS_DAILY_BUY_RISK_LIMIT" in result["blockers"] and len(h.orders) == 1
    assert result["orders"][-1]["status"] == "BLOCKED"
    assert cli.run("strategy-kis")["orders"][-1]["status"] == "BLOCKED" and len(h.orders) == 1
    assert read(h.archive / "paper/kis-strategy-runtime.json")["configured_native_limits"]["daily_buy_limits"] == APPROVED_CAPS
    h.now += timedelta(seconds=10)
    propose("fixture-4", action="EXIT_NOW")
    cli.account_cash = 0
    assert cli.run("strategy-kis")["orders"][-1]["status"] == "ACKNOWLEDGED"
    assert [row["side"] for row in h.orders.values()] == ["BUY", "SELL"]


@pytest.mark.parametrize("reversed_price", [False, True])
def test_native_cli_rechecks_named_next_open_and_close_group_with_live_book(cli, monkeypatch, reversed_price):
    from tradingagents.execution import session_confirmation

    h = cli.h
    h.now = h.now.replace(hour=9, minute=18 if h.market == "KR" else 48)
    source = cli.source("cohort-full", cohort=True)
    cli.configure(candidate=False, daily=True, universe=True)
    prev = h.now - timedelta(days=3)
    past = regular_session(market=h.market, now_local=prev)
    current = regular_session(market=h.market, now_local=h.now)
    sessions = [(when.date().isoformat(), datetime.fromisoformat(d["session_open"]), datetime.fromisoformat(d["session_close"]))
                for when, d in ((prev, past), (h.now, current))]
    monkeypatch.setattr(session_confirmation, "_schedule", lambda market, origin: sessions)
    origin_at = sessions[0][2] - timedelta(hours=1)
    paths = source / "tickers" / h.ticker
    contract = read(paths / "execution_contract.json")
    contract["analysis_asof"] = origin_at.isoformat()
    stages = ("close", "next_open", "next_session_quote")
    trigger = h.price * .995
    contract["structured_levels"] = [{"level_type": "BREAKOUT", "price": trigger, "confirmation": stage,
                                      "confirmation_group": "confirmed"} for stage in stages]
    atomic_write_json(paths / "execution_contract.json", contract)
    analysis = read(paths / "analysis.json")
    analysis.update(started_at=(origin_at - timedelta(minutes=5)).isoformat(), finished_at=origin_at.isoformat())
    atomic_write_json(paths / "analysis.json", analysis)
    update = read(paths / "execution_update.json")
    update["analysis_asof"] = origin_at.isoformat()
    currency = "KRW" if h.market == "KR" else "USD"
    references = {"source": "kis", "ticker": h.ticker, "market": h.market, "currency": currency, "price": h.price}
    open_at = sessions[1][1].isoformat()
    close_at = sessions[0][2].isoformat()
    archived_quote = update["market_data_asof"]
    update["entry_confirmation_v2"] = {
        "plan": {"ticker": h.ticker, "market": h.market, "currency": currency, "origin_session": sessions[0][0],
                 "created_at": origin_at.isoformat(), "valid_sessions": 1, "quote_max_age_seconds": 120,
                 "max_open_delay_seconds": 60, "execution_window_seconds": 1800, "max_gap_bps": 200,
                 "alternatives": [[{"id": f"confirmed-{i}", "stage": stage, "direction": "above", "level": trigger}
                                   for i, stage in enumerate(stages)]]},
        "regular_close": {**references, "session": sessions[0][0], "kind": "final_regular_close", "event_at": close_at, "observed_at": close_at},
        "official_open": {**references, "session": sessions[1][0], "kind": "official_regular_open", "event_at": open_at, "observed_at": open_at},
        "live_quote": {**references, "session": sessions[1][0], "kind": "quote", "event_at": archived_quote, "observed_at": archived_quote},
    }
    atomic_write_json(paths / "execution_update.json", update)
    if reversed_price:
        h.price *= .99
    result = cli.run("strategy-kis")
    if reversed_price:
        assert result["blockers"] == ["ENTRY_CURRENT_CONDITIONS_NOT_CONFIRMED"] and not h.orders
    else:
        assert result["orders"][0]["status"] == "ACKNOWLEDGED" and len(h.orders) == 1, result


@pytest.mark.parametrize("against", ["shadow", "incomplete", "stale", "foreign", "cash", "halt", "live", "slots"])
def test_normal_entrypoints_preserve_the_separate_admission_boundaries(cli, against, monkeypatch):
    h = cli.h
    cli.source("production-full", complete=against != "incomplete")
    prior = None
    if against == "shadow":
        prism_autotrader.initialize_autotrader_db(h.archive / "paper/autotrader.sqlite")
        atomic_write_json(cli.receipt, {"schema": prism_autotrader.AUTOTRADER_SCHEMA, "mode": "shadow",
                      "market": h.market, "entries": {h.ticker: {"reference_price": h.price}}})
    elif against == "live":
        atomic_write_json(cli.lane_policy, {"mode": "kis_live", "enabled": True, "live_orders_confirmed": True,
                          "live_promotion_override": "force"})
        assert cli.run("autotrader")["blockers"] == ["LIVE_PROMOTION_GATE_BLOCKED"]
    else:
        producer = cli.run("autotrader")
        if against == "incomplete":
            assert producer["blockers"] == ["VTS_CANDIDATE_SOURCE_UNVERIFIED"] and not cli.receipt.is_file()
        else:
            prior = read(cli.receipt)
    if against == "stale":
        def stale(market, ticker, clock, **options):
            return {**cli.quote(market, ticker, clock, **options), "observed_at": (h.now - timedelta(seconds=120)).isoformat()}
        monkeypatch.setattr(demo_runtime, "current_quote", stale)
    elif against == "foreign":
        monkeypatch.setattr(demo_runtime, "current_quote", lambda *args, **options: {**cli.quote(*args, **options), "session": "post_market"})
    elif against == "cash":
        cli.account_cash = 0
    elif against == "slots":
        suffix = "krw" if h.market == "KR" else "usd"
        cli.other_holdings = [{"ticker": str(100_000 + i) if h.market == "KR" else "X" + chr(65 + i),
                               "exchange": "NASD", "quantity": 1, "sellable_quantity": 1,
                               f"market_value_{suffix}": h.price} for i in range(10)]
    elif against == "halt":
        (cli.lane / "HALT").touch()
        status = cli.run("autotrader")
        assert status["blockers"] == ["KILL_SWITCH_ACTIVE"] and status["entries_queued"] == [h.ticker]
        assert read(cli.receipt) == {**prior, "transmission_halted": True}
    result = cli.run("strategy-kis")
    expected = {"incomplete": "NO_RECENT_COMPLETED_SOURCE", "cash": "NO_STRATEGY_QUANTITY_WITHIN_LIMITS",
                "halt": "PRISM_CANDIDATE_HALTED", "stale": "CANDIDATE_EVIDENCE_UNVERIFIED"}
    assert expected.get(against, "PRISM_CANDIDATE_NOT_ADMITTED") in result["blockers"], result
    assert h.orders == {} and cli.prepared_at_wire == [] and cli.fill_events() == []
