from datetime import datetime
from importlib import import_module
from unittest.mock import Mock

import pytest

from tradingagents.agents.utils.decision_clock import build_decision_clock_context
from tradingagents.graph.propagation import Propagator


def test_jnj_preopen_instant_is_identical_from_kst_and_utc():
    state = Propagator().create_initial_state("JNJ", "2026-09-29", "2026-09-30")
    kst = build_decision_clock_context(state, now=datetime.fromisoformat("2026-09-30T22:20:00+09:00"))
    utc = build_decision_clock_context(state, now=datetime.fromisoformat("2026-09-30T13:20:00+00:00"))
    assert kst == utc
    assert "2026-09-30T09:20:00-04:00" in kst
    assert "Research as-of date (date only): 2026-09-30" in kst
    assert "Daily price reference date (date only): 2026-09-29" in kst
    assert "matches exchange runtime date: True" in kst
    assert "Do not roll a deadline" in kst


@pytest.mark.parametrize("symbol,instant,expected", [
    ("JNJ", "2026-01-15T14:20:00+00:00", "2026-01-15T09:20:00-05:00"),
    ("005930", "2026-09-30T00:20:00+00:00", "2026-09-30T09:20:00+09:00"),
    ("JNJ", "2026-10-01T01:00:00+09:00", "2026-09-30T12:00:00-04:00"),
])
def test_clock_uses_exchange_timezone_and_dst(symbol, instant, expected):
    state = Propagator().create_initial_state(symbol, "2026-09-29", "2026-09-30")
    assert expected in build_decision_clock_context(state, now=datetime.fromisoformat(instant))


def test_historical_date_does_not_become_current_intraday_asof():
    state = Propagator().create_initial_state("JNJ", "2026-09-28", "2026-09-28")
    context = build_decision_clock_context(state, now=datetime.fromisoformat("2026-09-30T13:20:00+00:00"))
    assert "matches exchange runtime date: False" in context
    assert "Research as-of date (date only): 2026-09-28" in context
    assert "NOT the historical as-of instant" in context
    assert "preserve the research cutoff" in context


@pytest.mark.parametrize("profile", [None, {}, {"timezone": "Bad/Timezone"}, {"timezone": 1}])
def test_missing_or_invalid_timezone_stays_unverified(profile):
    context = build_decision_clock_context({"instrument_profile": profile})
    assert "Exchange-local runtime instant: UNVERIFIED" in context
    assert "matches exchange runtime date: False" in context


def test_naive_runtime_clock_is_rejected():
    with pytest.raises(ValueError, match="timezone-aware"):
        build_decision_clock_context({}, now=datetime(2026, 9, 30, 22, 20))


@pytest.mark.parametrize("module_name,factory,structured", [
    ("managers.research_manager", "create_research_manager", True),
    ("trader.trader", "create_trader", True),
    ("managers.portfolio_manager", "create_portfolio_manager", True),
    ("risk_mgmt.aggressive_debator", "create_aggressive_debator", False),
    ("risk_mgmt.conservative_debator", "create_conservative_debator", False),
    ("risk_mgmt.neutral_debator", "create_neutral_debator", False),
])
def test_decision_and_risk_stages_receive_clock(monkeypatch, module_name, factory, structured):
    module = import_module("tradingagents.agents." + module_name)
    state = Propagator().create_initial_state("JNJ", "2026-09-29", "2026-09-30")
    state.update(investment_plan="{}", trader_investment_plan="{}")
    clock = build_decision_clock_context(state, now=datetime.fromisoformat("2026-09-30T13:20:00+00:00"))
    clock_builder = Mock(return_value=clock)
    monkeypatch.setattr(module, "build_decision_clock_context", clock_builder)
    llm, memory = Mock(), Mock()
    memory.get_memories.return_value = []
    if structured:
        invoke = Mock(return_value=(Mock(), "{}"))
        monkeypatch.setattr(module, "invoke_structured_decision_with_retry", invoke)
        getattr(module, factory)(llm, memory)(state)
        prompt = str(invoke.call_args.args[1])
    else:
        llm.invoke.return_value.content = "risk analysis"
        getattr(module, factory)(llm)(state)
        prompt = llm.invoke.call_args.args[0]
    clock_builder.assert_called_once_with(state)
    assert "2026-09-30T09:20:00-04:00" in prompt
    assert "unverified statements in the debate do not establish" in prompt
