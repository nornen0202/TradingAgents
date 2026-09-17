import json
import pytest

from tradingagents.investor import build_investor_playbook, position_size, trade_economics
from tradingagents.reporting import save_report_bundle
from tradingagents.graph.signal_processing import SignalProcessor
from tradingagents.agents.utils.decision_retry import _fallback_structured_decision_json


def decision_state():
    payload = {"rating": "OVERWEIGHT", "confidence": 0.8, "time_horizon": "medium",
               "entry_logic": "Confirm breakout", "exit_logic": "Stop below 95", "position_sizing": "Within loss budget",
               "risk_limits": "No leverage", "catalysts": ["earnings"], "invalidators": ["support fails"],
               "execution_levels": {"levels": [
                   {"label": "entry", "level_type": "BREAKOUT", "price": 100, "currency": "USD"},
                   {"label": "stop", "level_type": "STOP_LOSS", "price": 95, "currency": "USD"},
                   {"label": "target", "level_type": "TAKE_PROFIT", "price": 110, "currency": "USD"}]}}
    return {"trade_date": "2026-09-10", "final_trade_decision": payload, "risk_debate_state": {"judge_decision": payload}}


def test_cost_aware_economics_does_not_invent_a_win_probability():
    result = trade_economics(100, 95, 110, cost_bps=10)
    assert result["risk_per_share"] == pytest.approx(5.195)
    assert result["reward_per_share"] == pytest.approx(9.79)
    assert result["reward_risk_ratio"] < 2
    assert result["break_even_win_rate"] > 1/3


def test_size_respects_all_budgets_and_existing_holdings():
    result = position_size(capital=10000, cash=500, entry=100, stop=95, existing_position_value=800)
    assert result["shares"] == 1
    assert result["planned_stop_loss"] <= result["loss_budget"]
    assert result["order_authorized"] is False
    assert result["binding_constraints"] == ["position_cap"]


@pytest.mark.parametrize("changes", [{"capital": float("nan")}, {"cash": float("inf")}, {"stop": 101}, {"risk_fraction": 2}, {"entry": 0}])
def test_invalid_sizing_cannot_create_an_order(changes):
    kwargs = dict(capital=10000, cash=500, entry=100, stop=95)
    kwargs.update(changes)
    with pytest.raises(ValueError):
        position_size(**kwargs)


def test_zero_cash_returns_zero_shares():
    assert position_size(capital=10000, cash=0, entry=100, stop=95)["shares"] == 0


def test_ambiguous_or_cross_currency_levels_are_not_combined():
    state = decision_state()
    levels = state["final_trade_decision"]["execution_levels"]["levels"]
    levels.append({"label": "alternative", "level_type": "PULLBACK", "price": 98, "currency": "USD"})
    assert build_investor_playbook(state)["economics"] is None
    levels.pop()
    levels[-1]["currency"] = "KRW"
    assert build_investor_playbook(state)["economics"] is None


def test_invalid_decision_is_review_not_hold():
    assert build_investor_playbook({"final_trade_decision": "not a decision"})["status"] == "REVIEW"


def test_provider_placeholder_is_review_even_though_its_schema_is_valid(tmp_path):
    raw = _fallback_structured_decision_json(context="risk judge", reason="timeout")
    assert SignalProcessor().process_signal(raw) == "REVIEW"
    state = {"final_trade_decision": raw}
    assert build_investor_playbook(state)["reason"] == "decision_unvalidated"
    path = save_report_bundle(state, "AAPL", tmp_path, language="Korean")
    assert "검증된 최종 판단을 얻지 못했습니다" in path.read_text(encoding="utf-8")


def test_nonfinite_price_is_review_and_serializable():
    state = decision_state()
    state["final_trade_decision"]["execution_levels"]["levels"][0]["price"] = float("inf")
    plan = build_investor_playbook(state)
    assert plan["status"] == "REVIEW"
    json.dumps(plan, allow_nan=False)


def test_report_bundle_contains_verified_korean_playbook(tmp_path):
    path = save_report_bundle(decision_state(), "AAPL", tmp_path, language="Korean")
    report = path.read_text(encoding="utf-8")
    assert "투자 전 한눈에 확인" in report
    assert "수익이 날 확률이 아닙니다" in report
    assert "1.88배" in report
    data = json.loads((tmp_path / "0_summary/investor_playbook.json").read_text(encoding="utf-8"))
    assert data["order_authorized"] is False
