from base64 import b64encode
from datetime import datetime, timedelta
import hashlib
import json
from pathlib import Path
import sqlite3
import subprocess
import sys

import pytest

from tradingagents.atomic_io import atomic_write_json, interprocess_file_lock
from tradingagents.execution import demo_runtime, isolated_replay
from tradingagents.execution.contract_builder import build_execution_contract
from tradingagents.execution.kis_demo import DemoCredentials
from tradingagents.execution.overlay import evaluate_execution_state
from tradingagents.execution.strategy_settlement import SCHEMA as SETTLEMENT_SCHEMA
from tradingagents.schemas import IntradayMarketSnapshot
from tests.execution.test_conditional_entry import decision
from tests.execution.test_kis_strategy_limits import configure, configure_v2

SYMBOL = "005930.KS"
BUY = "2026-10-19T09:03:00+09:00"
SELL = "2026-10-19T09:06:00+09:00"
SETTLED = "2026-10-21T16:00:00+09:00"
REPOSITORY = Path(__file__).resolve().parents[2]


def stamp(value, seconds=0):
    return (datetime.fromisoformat(value) + timedelta(seconds=seconds)).isoformat()


def _observation(kind, clock, price):
    return {"kind": kind, "event_at": clock, "observed_at": clock, "price": price,
            "ticker": SYMBOL, "source": "KIS_FIXTURE", "market": "KR", "currency": "KRW", "session": clock[:10]}


def _source(workspace, run_id, moment, *, side="BUY", close=True):
    run_id = datetime.fromisoformat(moment).strftime("%Y%m%dT%H%M%S") + "_" + run_id
    run = workspace / "archive/runs/2026" / run_id
    price = 70000 if side == "BUY" else 70100
    levels = {"levels": [{"level_type": "BREAKOUT", "price": 69000, "confirmation": "intraday"}],
              "earliest_pilot_time_local": "09:00", "min_relative_volume": 1.1}
    thesis = decision(conditional_entry_valid_until=stamp(moment, 240), execution_levels=levels)
    if side == "SELL":
        thesis = decision(conditional_entry_action="NONE", conditional_entry_valid_until=None,
                          execution_levels={"levels": [{"level_type": "INVALIDATION", "price": 70500,
                                                        "confirmation": "intraday"}]})
    contract = build_execution_contract(ticker=SYMBOL, analysis_payload={"decision": json.dumps(thesis),
                                          "trade_date": moment[:10], "finished_at": moment})
    snapshot = IntradayMarketSnapshot(ticker=SYMBOL, asof=moment, provider="kis", market_session="regular",
        market="KR", interval="1m", last_price=price, day_high=price + 100, day_low=price - 100,
        session_vwap=price - 50, volume=1200, avg20_daily_volume=1000, relative_volume=1.2)
    outcome = evaluate_execution_state(contract, snapshot, now=datetime.fromisoformat(moment), max_data_age_seconds=120)
    assert outcome.decision_now.value == ("STARTER_NOW" if side == "BUY" else "EXIT_NOW"), outcome.reason_codes
    for path, payload in {
        "run.json": {"run_id": run_id, "status": "success", "settings": {"market": "kr"},
                     "started_at": moment, "finished_at": moment},
        "decision_bundle_v2.json": {"market": "kr", "generated_at": moment, "analysis_source_run_id": run_id,
            "strategy_table": [{"ticker": SYMBOL, "last_price": price, "market_data_asof": moment,
                "market_session": "regular", "quality": {"execution_ready": True, "generated_in_current_run": True},
                "raw_codes": {"decision_now": outcome.decision_now.value}}]},
        "portfolio-private/account_snapshot.json": {"as_of": moment, "account_value_krw": 10000000, "positions": []},
        "portfolio-private/proposed_orders.json": {"orders": [{"canonical_ticker": SYMBOL, "side": side,
                "estimated_qty": 1, "delta_krw_now": 100000 if side == "BUY" else -100000}]},
    }.items():
        atomic_write_json(run / path, payload)
    if side == "BUY":
        proof = {
            "plan": {"ticker": SYMBOL, "market": "KR", "currency": "KRW", "origin_session": "2026-10-16",
                "created_at": "2026-10-16T15:00:00+09:00", "valid_sessions": 2, "quote_max_age_seconds": 120,
                "max_open_delay_seconds": 30, "execution_window_seconds": 600, "max_gap_bps": 200,
                "alternatives": [[{"id": "close", "stage": "close", "direction": "above", "level": 69000},
                                  {"id": "open", "stage": "next_day", "direction": "above", "level": 69000}]]},
            "regular_close": _observation("final_regular_close" if close else "quote", "2026-10-16T15:30:00+09:00", price),
            "official_open": _observation("official_regular_open", "2026-10-19T09:00:00+09:00", price),
            "live_quote": _observation("quote", moment, price),
        }
        atomic_write_json(run / f"tickers/{SYMBOL}/execution_contract.json", {**contract.to_dict(), "entry_confirmation_v2": proof})
    return run


def _index(clock, price, kind="intraday_index"):
    return {"source": "KIS_KOSPI_FIXTURE", "symbol": "0001", "market": "KR", "kind": kind,
            "event_at": clock, "observed_at": clock, "price": price}


def _row(side, order_id, clock, price):
    return {"odno": order_id, "pdno": SYMBOL[:6], "sll_buy_dvsn_cd": "02" if side == "BUY" else "01",
            "ord_dt": clock[:10].replace("-", ""), "ord_tmd": clock[11:19].replace(":", ""),
            "ord_unpr": str(price), "ord_qty": "1", "tot_ccld_qty": "1", "rmn_qty": "0",
            "cncl_yn": "N", "tot_ccld_amt": str(price)}


def _tape(clock, *, positions=0, price=70000, rows=(), order_side="BUY", lost=False):
    code, order_id = ("VTTC0012U", "1") if order_side == "BUY" else ("VTTC0011U", "2")
    return {
        "as_of": clock, "tickers": [SYMBOL], "index": _index(clock, 3000),
        "quotes": {SYMBOL: {"ticker": SYMBOL[:6], "provider": "kis", "currency": "KRW", "session": "regular",
            "execution_ready": True, "instrument_type": "STOCK", "last_price": price,
            "observed_at": clock, "ingested_at": clock}},
        "responses": {
            "VTTC8434R": {"body": {"rt_cd": "0", "output1": [
                {"pdno": SYMBOL[:6], "hldg_qty": str(positions), "ord_psbl_qty": str(positions), "evlu_amt": str(price * positions)}
            ] if positions else [], "output2": [{"dnca_tot_amt": "9000000", "tot_evlu_amt": "10000000"}]}},
            "VTTC8908R": {"body": {"rt_cd": "0", "output": {"nrcvb_buy_amt": "9000000", "nrcvb_buy_qty": "100"}}},
            "VTTC0081R": {"body": {"rt_cd": "0", "output1": list(rows)}},
            code: {"expect": {"PDNO": SYMBOL[:6], "ORD_DVSN": "00", "ORD_QTY": "1", "ORD_UNPR": str(price)},
                   "response_lost": lost, "body": {"rt_cd": "0", "output": {"ODNO": order_id, "KRX_FWDG_ORD_ORGNO": "001"}}},
        },
    }


def _fixture(tmp_path, name, doc):
    path = tmp_path / f"{name}.json"
    atomic_write_json(path, {"schema": isolated_replay.SCHEMA, **doc})
    return path


def _args(workspace, action, fixture=None, *, scheduler=False):
    if scheduler:
        command = ["tradingagents.local_automation", "strategy-kis", "--isolated-replay", str(workspace),
                   "--replay-action", action]
    else:
        command = ["cli.main", "paper-replay", action, "--workspace", str(workspace)]
    return [sys.executable, "-m", *command] + (["--fixture-input", str(fixture)] if fixture else [])


def _command(workspace, action, fixture=None, *, scheduler=False):
    run = subprocess.run(_args(workspace, action, fixture, scheduler=scheduler), cwd=REPOSITORY,
                         capture_output=True, encoding="utf-8", check=False, timeout=60)
    assert run.returncode == 0, (run.stdout, run.stderr)
    result = json.loads(run.stdout)
    assert result["real_orders_enabled"] is False and result["network_requests_sent"] == 0
    return result


def _callback(workspace, tmp_path, clock, token, name, *, secret=None):
    marker = json.loads((workspace / ".paper-replay.json").read_text(encoding="utf-8"))
    return _fixture(tmp_path, f"callback-{name}", {"as_of": clock, "supplied_secret": secret or marker["secret"],
        "update": {"update_id": 1, "callback_query": {"id": name, "from": {"id": 101, "is_bot": False}, "data": token,
                   "message": {"from": {"id": 202, "is_bot": True}, "chat": {"id": -303}}}}})


def _wire(workspace):
    path = workspace / "wire.jsonl"
    if not path.exists():
        return []
    rows = map(json.loads, path.read_text(encoding="utf-8").splitlines())
    return [row["tr_id"] for row in rows if row["method"] == "POST"]


def _settlement(order, broker_id):
    scope = DemoCredentials("unused", "unused", "00000001", "01").scope()
    original = f"Synthetic settlement evidence for broker order {broker_id}".encode()
    return {"source_base64": b64encode(original).decode(), "document": {
        "schema": SETTLEMENT_SCHEMA, "environment": "demo", "market": "KR", "currency": "KRW",
        "account_scope": scope, "intent_id": order["id"], "broker_order_id": broker_id,
        "revision_id": order["id"] + ":fixture-v1", "previous_revision_id": None,
        "attribution": "ORDER_EXECUTION", "cost_coverage": "ALL_COMPONENTS_IN_TRADING_CURRENCY",
        "source": {"kind": "KIS_DEMO_SETTLEMENT_DOCUMENT", "sha256": hashlib.sha256(original).hexdigest(),
                   "observed_at": SETTLED, "available_at": SETTLED},
        "review": {"approved": True, "reviewer_id": "offline-fixture-reviewer", "reviewed_at": SETTLED},
        "corrections_checked_through": SETTLED, "fills": [{
            "fill_id": f"fixture-fill-{broker_id}", "quantity": 1, "price": order["fill_notional"],
            "commission": 1, "tax": 0, "fx_cost": 0, "other_cost": 0, "currency": "KRW",
            "executed_at": stamp(order["prepared_at"], 1), "confirmed_at": stamp(order["prepared_at"], 2),
            "settled_at": "2026-10-21T15:40:00+09:00"}],
    }}


def test_cli_and_separate_schedulers_reconcile_once_before_measuring_settled_fixture(tmp_path):
    workspace = tmp_path / "workspace"
    assert _command(workspace, "init")["status"] == "INITIALIZED"
    version = "fixture-1"
    preregister = _fixture(tmp_path, "policy", {"as_of": "2026-10-18T10:00:00+09:00",
        "policy": {"version": version, "market": "KR", "sample_kind": "round_trip", "minimum_sessions": 60,
                   "cost_version": "fixture-reviewed-costs-v1", "benchmark": "KOSPI_FIXTURE"}})
    assert isolated_replay.command(workspace, "promotion-start", preregister)["observed_sessions"] == 0
    _source(workspace, "fixture-buy", stamp(BUY, -5))
    preview = _fixture(tmp_path, "buy-preview", _tape(BUY))
    first = _command(workspace, "tick", preview, scheduler=True)
    assert first["strategy"]["orders"] == [] and not _wire(workspace)
    [tokens] = first["approval_previews"].values()
    forged = _callback(workspace, tmp_path, BUY, tokens["approve"], "forged", secret="a" * 64)
    with pytest.raises(ValueError, match="Unauthorized"):
        isolated_replay.command(workspace, "callback", forged)
    good = _callback(workspace, tmp_path, BUY, tokens["approve"], "approve-buy")
    assert _command(workspace, "callback", good)["status"] == "RECORDED"
    assert isolated_replay.command(workspace, "callback", good)["status"] == "REPLAY"
    sent_at = stamp(BUY, 2)
    dispatch = _fixture(tmp_path, "buy-dispatch", _tape(sent_at))
    args = _args(workspace, "tick", dispatch, scheduler=True)
    with subprocess.Popen(args, cwd=REPOSITORY, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8") as a:
        with subprocess.Popen(args, cwd=REPOSITORY, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8") as b:
            results = [process.communicate(timeout=60) for process in (a, b)]
            assert all(process.returncode == 0 for process in (a, b)), results
    assert _wire(workspace) == ["VTTC0012U"]
    assert any(json.loads(stdout).get("strategy", {}).get("order_counts", {}).get("ACKNOWLEDGED") == 1
               for stdout, _ in results)
    buy = _row("BUY", "1", sent_at, 70000)
    observed = isolated_replay.command(workspace, "tick", _fixture(tmp_path, "buy-filled",
        _tape(stamp(BUY, 10), positions=1, rows=[buy])))
    assert observed["strategy"]["owned"] == {SYMBOL: 1}
    assert observed["strategy"]["performance"]["settlement_known"] is False
    _source(workspace, "fixture-sell", stamp(SELL, -5), side="SELL")
    sell_tape = _fixture(tmp_path, "sell-preview",
        _tape(SELL, positions=1, price=70100, rows=[buy], order_side="SELL") | {"index": None})
    sell = isolated_replay.command(workspace, "tick", sell_tape)
    [tokens] = sell["approval_previews"].values()
    assert isolated_replay.command(workspace, "callback",
        _callback(workspace, tmp_path, SELL, tokens["approve"], "approve-sell"))["status"] == "RECORDED"
    sell_sent = stamp(SELL, 2)
    isolated_replay.command(workspace, "tick", _fixture(tmp_path, "sell-dispatch",
        _tape(sell_sent, positions=1, price=70100, rows=[buy], order_side="SELL") | {"index": None}))
    final = isolated_replay.command(workspace, "tick", _fixture(tmp_path, "sell-filled",
        _tape(stamp(SELL, 8), price=70100, rows=[buy, _row("SELL", "2", sell_sent, 70100)], order_side="SELL")))
    assert _wire(workspace) == ["VTTC0012U", "VTTC0011U"]
    assert final["strategy"]["evaluation"]["status"] == "AVAILABLE_GROSS_ONLY"
    assert final["strategy"]["owned"] == {SYMBOL: 0}
    receipt = json.loads((workspace / "archive/paper/kis-strategy-runtime.json").read_text(encoding="utf-8"))
    assert receipt["evidence_scope"] == "ISOLATED_FIXTURE"
    with sqlite3.connect(workspace / "state/kr-strategy.sqlite") as db:
        buy_evidence, sell_evidence = [
            json.loads(db.execute("SELECT evidence FROM strategy_source_evidence WHERE id=?", (order["id"],)).fetchone()[0])["admission"]
            for order in final["strategy"]["orders"]
        ]
    assert buy_evidence["confirmation"]["conditions"]["close"]["observation_as_of"] == "2026-10-16T06:30:00+00:00"
    assert buy_evidence["index"]["source"] == "KIS_KOSPI_FIXTURE"
    assert sell_evidence["index"] == {"status": "UNVERIFIED"}
    next_entry = stamp(SELL, 15)
    _source(workspace, "fixture-next-entry", stamp(next_entry, -5))
    before_settlement = isolated_replay.command(workspace, "tick", _fixture(tmp_path, "next-entry",
        _tape(next_entry, rows=[buy, _row("SELL", "2", sell_sent, 70100)])))
    assert before_settlement["strategy"]["blockers"] == ["ADDITIONAL_ADMISSION_REQUIRED"]
    assert not before_settlement["approval_previews"] and _wire(workspace) == ["VTTC0012U", "VTTC0011U"]
    settled = _fixture(tmp_path, "settlement", {"as_of": SETTLED, "tickers": [SYMBOL],
        "settlements": [_settlement(order, str(i)) for i, order in enumerate(final["strategy"]["orders"], 1)]})
    result = _command(workspace, "settlement", settled, scheduler=True)
    assert result["imported"] == 2 and result["strategy"]["evaluation"]["realized_net_pnl"] == 98
    assert isolated_replay.command(workspace, "settlement", settled)["imported"] == 0
    promotion_input = _fixture(tmp_path, "promotion", {"as_of": SETTLED, "version": version, "tickers": [SYMBOL],
        "session": "2026-10-21", "starting_nav": 10000000,
        "index_close": _index("2026-10-21T15:30:00+09:00", 3010, "final_regular_close"),
        "previous_index_close": _index("2026-10-20T15:30:00+09:00", 3000, "final_regular_close")})
    status = _command(workspace, "promotion-record", promotion_input, scheduler=True)
    assert status["unique_samples"] == status["observed_sessions"] == 1 and status["missing_sessions"] == 2
    assert status["checks"]["forward_observation"] is status["eligible_for_review"] is False
    retry = isolated_replay.command(workspace, "promotion-record", promotion_input)
    assert retry == {**status, "network_requests_sent": 0}


def test_invalid_closed_bar_future_index_and_lost_ack_fail_without_a_second_post(tmp_path):
    workspace = tmp_path / "workspace"
    isolated_replay.command(workspace, "init")
    _source(workspace, "fixture-buy", stamp(BUY, -5), close=False)
    tick = _fixture(tmp_path, "tick", _tape(BUY))
    result = isolated_replay.command(workspace, "tick", tick)
    assert not result["approval_previews"] and not _wire(workspace)
    _source(workspace, "fixture-buy", stamp(BUY, -5))
    result = isolated_replay.command(workspace, "tick", _fixture(tmp_path, "future-index",
        _tape(BUY) | {"index": _index(stamp(BUY, 1), 3000)}))
    assert not result["approval_previews"] and not _wire(workspace)
    [tokens] = isolated_replay.command(workspace, "tick", tick)["approval_previews"].values()
    isolated_replay.command(workspace, "callback", _callback(workspace, tmp_path, BUY, tokens["approve"], "approve"))
    sent_at = stamp(BUY, 2)
    lost = _fixture(tmp_path, "lost", _tape(sent_at, lost=True))
    assert isolated_replay.command(workspace, "tick", lost)["strategy"]["order_counts"]["UNKNOWN"] == 1
    retry = _fixture(tmp_path, "retry", _tape(stamp(BUY, 10), rows=[_row("BUY", "1", sent_at, 70000)]))
    assert isolated_replay.command(workspace, "tick", retry)["strategy"]["order_counts"]["UNKNOWN"] == 1
    lookup = _fixture(tmp_path, "lookup", _tape(stamp(BUY, 10), rows=[_row("BUY", "1", sent_at, 70000)])
                      | {"trade_date": "20261019"})
    assert isolated_replay.command(workspace, "inspect-orders", lookup)["rows"] == 1
    assert _wire(workspace) == ["VTTC0012U"]
    with pytest.raises(ValueError, match="backwards"):
        isolated_replay.command(workspace, "tick", tick)


def test_fixture_workspace_cannot_fall_through_to_operational_transport(tmp_path, monkeypatch):
    workspace = tmp_path / "workspace"
    isolated_replay.command(workspace, "init")
    monkeypatch.setattr(demo_runtime, "broker_context", lambda *_: pytest.fail("Operational broker"))
    with pytest.raises(ValueError, match="different evidence scope"):
        demo_runtime.tick(workspace / "archive", workspace / "state", workspace / "validation")
    with pytest.raises(ValueError, match="requires isolated ports"):
        demo_runtime.tick(workspace / "archive", workspace / "state", workspace / "validation",
                          evidence_scope=demo_runtime.FIXTURE_SCOPE)
    scheduler = _args(workspace, "tick", scheduler=True) + ["--state-dir", str(tmp_path)]
    result = subprocess.run(scheduler, cwd=REPOSITORY, capture_output=True, check=False, timeout=60)
    assert result.returncode == 2 and b"no operational arguments" in result.stderr


def test_fixture_calendar_never_calls_operational_kis_with_provider_enabled(tmp_path, monkeypatch):
    from tradingagents.scheduled import automation_calendar

    monkeypatch.setenv("TRADINGAGENTS_KIS_MARKET_CALENDAR_ENABLED", "true")
    monkeypatch.setattr(automation_calendar, "automated_market_session_status",
                        lambda *_args, **_kwargs: pytest.fail("Operational market calendar"))
    workspace = tmp_path / "workspace"
    isolated_replay.command(workspace, "init")
    _source(workspace, "fixture-buy", stamp(BUY, -5))
    result = isolated_replay.command(workspace, "tick", _fixture(tmp_path, "buy", _tape(BUY)))
    assert result["approval_previews"] and not _wire(workspace)


def test_approval_remains_bound_to_the_producer_document_bytes(tmp_path):
    workspace = tmp_path / "workspace"
    isolated_replay.command(workspace, "init")
    run = _source(workspace, "fixture-buy", stamp(BUY, -5))
    tick = _fixture(tmp_path, "tick", _tape(BUY))
    [tokens] = isolated_replay.command(workspace, "tick", tick)["approval_previews"].values()
    approved = _callback(workspace, tmp_path, BUY, tokens["approve"], "approval")
    isolated_replay.command(workspace, "callback", approved)
    source = run / "decision_bundle_v2.json"
    old = json.loads(source.read_text(encoding="utf-8"))
    atomic_write_json(source, {**old, "fixture_producer_revision": 2})
    later = _fixture(tmp_path, "later", _tape(stamp(BUY, 2)))
    result = isolated_replay.command(workspace, "tick", later)
    [revised] = result["approval_previews"].values()
    assert revised != tokens and not result["strategy"]["orders"] and not _wire(workspace)


def test_separate_scheduler_cannot_enter_while_another_process_owns_the_replay(tmp_path):
    workspace = tmp_path / "workspace"
    isolated_replay.command(workspace, "init")
    fixture = _fixture(tmp_path, "tick", _tape(BUY))
    with interprocess_file_lock(workspace / "replay.lock", timeout=0):
        result = _command(workspace, "tick", fixture, scheduler=True)
        assert result["status"] == "REPLAY_ALREADY_RUNNING"
    assert not (workspace / "clock.json").exists() and not _wire(workspace)


@pytest.mark.parametrize("floor,one_share,allowed", [(9000000, .008, False), (1000, 0, False), (1000, .008, True)])
def test_isolated_vts_respects_the_same_native_limits(tmp_path, floor, one_share, allowed):
    workspace = tmp_path / "workspace"
    isolated_replay.command(workspace, "init")
    configure(workspace / "state", "KR", max_order_native=100000, cash_floor_native=floor,
              max_order_nav=.006, one_share_nav_ceiling=one_share)
    scope = DemoCredentials("unused", "unused", "00000001", "01").scope()
    configure_v2(workspace / "state", scope=scope, ticker=SYMBOL, now=datetime.fromisoformat(BUY))
    _source(workspace, "fixture-buy", stamp(BUY, -5))
    tick = _fixture(tmp_path, "native-limits", _tape(BUY))
    result = isolated_replay.command(workspace, "tick", tick)
    assert bool(result["approval_previews"]) is allowed
    if not allowed:
        assert result["strategy"]["blockers"] == ["NO_STRATEGY_QUANTITY_WITHIN_LIMITS"]
        assert not _wire(workspace)
        return
    [tokens] = result["approval_previews"].values()
    isolated_replay.command(workspace, "callback", _callback(workspace, tmp_path, BUY, tokens["approve"], "approve"))
    allowed_tick = _fixture(tmp_path, "native-buy", _tape(stamp(BUY, 2)))
    final = isolated_replay.command(workspace, "tick", allowed_tick)
    assert final["strategy"]["orders"][0]["quantity"] == 1
    assert _wire(workspace) == ["VTTC0012U"]
    with sqlite3.connect(workspace / "state/kr-strategy.sqlite") as db:
        evidence, = db.execute("SELECT evidence FROM strategy_source_evidence").fetchone()
    assert json.loads(evidence)["sizing_v2"]["policy_version"] == "fixture-v2"
