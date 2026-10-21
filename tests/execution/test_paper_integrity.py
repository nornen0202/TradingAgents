from datetime import datetime, timedelta
import json

import pytest

from test_archive_paper_sizing import archive
from tradingagents.execution.archive_paper import build_step
from tradingagents.execution.paper import PaperBroker
from tradingagents.execution.source_diagnostics import diagnose_source
from tradingagents.execution.demo_runtime import candidates
from tradingagents.execution.paper_quotes import normalize_quote, QuoteClockError
from types import SimpleNamespace
from tradingagents.portfolio.state_store import _build_proposed_orders

AT = datetime.fromisoformat("2026-09-21T10:00:00+09:00")


def write(path, value):
    path.write_text(json.dumps(value), encoding="utf-8")


def test_unallocated_exit_is_not_an_order_and_diagnostics_explain_idle(tmp_path):
    archive(tmp_path)
    path = tmp_path / "decision_bundle_v2.json"
    bundle = json.loads(path.read_text())
    bundle["strategy_table"][0]["raw_codes"] = {"decision_now": "EXIT_NOW", "portfolio_action_now": "HOLD"}
    write(path, bundle)
    write(tmp_path / "portfolio-private/proposed_orders.json", {"orders": []})
    _, step, _ = build_step(tmp_path, AT.isoformat())
    assert step["signals"] == []
    assert diagnose_source(tmp_path, AT)["status"] == "NO_ALLOCATED_ORDERS"


@pytest.mark.parametrize("action,expected", [("TRIM_NOW", "REDUCE_NOW"), ("STOP_LOSS_NOW", "EXIT_NOW")])
def test_explicit_portfolio_risk_sell_aliases_reach_existing_broker_schema(tmp_path, action, expected):
    archive(tmp_path)
    path = tmp_path / "decision_bundle_v2.json"
    bundle = json.loads(path.read_text())
    bundle["strategy_table"][0]["raw_codes"] = {"portfolio_action_now": action}
    write(path, bundle)
    write(tmp_path / "portfolio-private/proposed_orders.json", {"orders": [
        {"canonical_ticker": "TEST", "side": "SELL", "estimated_qty": 1, "delta_krw_now": -20000}]})
    result = candidates(tmp_path, "KR", AT, ("TEST",))
    assert result[0]["side"] == "SELL"
    assert result[0]["signal"]["decision_now"] == expected


def test_duplicate_proposals_never_select_first_arbitrarily(tmp_path):
    archive(tmp_path)
    path = tmp_path / "portfolio-private/proposed_orders.json"
    proposals = json.loads(path.read_text())
    proposals["orders"] *= 2
    write(path, proposals)
    with pytest.raises(ValueError, match="AMBIGUOUS_STRATEGY_PROPOSAL"):
        build_step(tmp_path, AT.isoformat())


@pytest.mark.parametrize("field,value", [("estimated_qty", True), ("estimated_qty", 1.5),
    ("estimated_qty", float("nan")), ("estimated_qty", -1), ("delta_krw_now", -100),
    ("delta_krw_now", 0), ("delta_krw_now", float("inf")), ("delta_krw_now", "100")])
def test_invalid_explicit_proposals_are_not_repaired_into_orders(tmp_path, field, value):
    archive(tmp_path)
    path = tmp_path / "portfolio-private/proposed_orders.json"
    proposals = json.loads(path.read_text())
    proposals["orders"][0][field] = value
    write(path, proposals)
    with pytest.raises(ValueError, match="INVALID_STRATEGY_PROPOSAL"):
        build_step(tmp_path, AT.isoformat())


@pytest.mark.parametrize("clock", [None, "bad", "2026-09-21T10:00:00", (AT+timedelta(seconds=1)).isoformat(), (AT-timedelta(seconds=120)).isoformat()])
def test_source_diagnostics_invalid_clocks_never_report_ready(tmp_path, clock):
    archive(tmp_path)
    path = tmp_path / "decision_bundle_v2.json"
    bundle = json.loads(path.read_text())
    bundle["strategy_table"][0]["market_data_asof"] = clock
    write(path, bundle)
    result = diagnose_source(tmp_path, AT)
    assert result["execution_ready_rows"] == 0
    assert result["status"] == "BLOCKED"


def test_source_degraded_exposes_provider_reason_not_normal_wait(tmp_path):
    archive(tmp_path)
    path = tmp_path / "decision_bundle_v2.json"
    bundle = json.loads(path.read_text())
    bundle["strategy_table"][0]["quality"].update(execution_ready=False, blocking_reasons=["limited_halt_status"])
    write(path, bundle)
    result = diagnose_source(tmp_path, AT)
    assert result["blockers"] == ["SOURCE_DATA_NOT_EXECUTION_READY"]
    assert result["reason_counts"] == {"limited_halt_status": 1}


def test_incomplete_valuation_does_not_claim_a_return_and_history_keeps_quality(tmp_path):
    snapshot, _, _ = archive(tmp_path)
    snapshot["positions"] = [{"canonical_ticker": "TEST", "quantity": 1, "market_price_krw": 20000}]
    broker = PaperBroker(tmp_path / "paper.sqlite")
    try:
        broker.seed(snapshot)
        missing = broker.step(now=AT.isoformat(), quotes={}, signals=[])
        assert missing["valuation_performance"]["return_pct"] is None
        assert missing["valuation_performance"]["status"] == "INCOMPLETE_MARKS"
        later = (AT + timedelta(seconds=30)).isoformat()
        full = broker.step(now=later, quotes={"TEST": {"as_of": later, "price_krw": 20100,
                           "session": "regular", "executable": True, "spread_bps": 5}}, signals=[])
        assert full["valuation_performance"]["pnl_krw"] == 100
        assert full["valuation_performance"]["strategy_only_return_pct"] is None
        assert [r[0] for r in broker.db.execute("SELECT marks_complete FROM observation_quality ORDER BY at")] == [0, 1]
    finally:
        broker.close()


@pytest.mark.parametrize("book_time,reason", [("100001", "ORDERBOOK_FUTURE"), ("095700", "ORDERBOOK_STALE")])
def test_quote_clock_diagnostic_preserves_rejected_event_and_observation(book_time, reason):
    chart = {"rt_cd": "0", "output2": [{"stck_bsop_date": "20260921", "stck_cntg_hour": "095900",
              "stck_oprc": 100, "stck_hgpr": 100, "stck_lwpr": 100, "stck_prpr": 100, "cntg_vol": 1}]}
    book = {"rt_cd": "0", "output1": {"bidp1": 100, "askp1": 100, "aspr_acpt_hour": book_time}}
    with pytest.raises(QuoteClockError) as caught:
        normalize_quote(ticker="005930.KS", market="kr", chart=chart, orderbook=book, observed_at=AT)
    assert caught.value.diagnostic["reason"] == reason
    assert caught.value.diagnostic["observed_at"] == AT.isoformat()


def test_proposal_keeps_approved_whole_share_quantity_and_fractional_fx_price():
    price = 421.14 * 1342.4
    position = SimpleNamespace(market_price_krw=price, available_qty=3)
    snapshot = SimpleNamespace(find_position=lambda _: position)
    action = SimpleNamespace(canonical_ticker="TEST", display_name="TEST", action_now="REDUCE_NOW",
                             delta_krw_now=-3*price, planned_sell_quantity_now=3)
    orders = _build_proposed_orders(snapshot, SimpleNamespace(actions=[action]))
    assert orders[0]["estimated_qty"] == 3
    assert orders[0]["estimated_market_price_krw"] == price
