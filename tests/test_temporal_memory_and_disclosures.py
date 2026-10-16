"""Offline regressions for eligible memory retrieval and Korean filing dates."""

from copy import deepcopy
from datetime import timedelta
import json
from unittest.mock import Mock, patch

import pytest

from tradingagents.agents.managers.portfolio_manager import create_portfolio_manager
from tradingagents.agents.managers.research_manager import create_research_manager
from tradingagents.agents.researchers.bear_researcher import create_bear_researcher
from tradingagents.agents.researchers.bull_researcher import create_bull_researcher
from tradingagents.agents.trader.trader import create_trader
from tradingagents.agents.utils.memory import FinancialSituationMemory
from tradingagents.dataflows import alpha_vantage_fundamentals as av
from tradingagents.dataflows import opendart
from tradingagents.dataflows import y_finance
from tradingagents.dataflows.config import run_config
from tradingagents.dataflows.interface import route_to_vendor
from tradingagents.dataflows.vendor_exceptions import (
    VendorInputError,
    VendorMalformedResponseError,
    VendorTransientError,
)
from tradingagents.graph.reflection import Reflector


def test_future_and_undated_memories_cannot_change_historical_scores(tmp_path):
    memory = FinancialSituationMemory("temporal", {"memory_dir": str(tmp_path)})
    memory.add_situations([
        ("alpha beta market", "first", {"outcome_known_at": "2026-03-01"}),
        ("alpha earnings", "second", {"outcome_known_at": "2026-03-01"}),
        ("delta market", "third", {"outcome_known_at": "2026-03-01"}),
    ])
    expected = memory.get_memories("alpha market", n_matches=3, as_of="2026-03-02")
    memory.add_situations([
        ("alpha " * 20, "future", {"outcome_known_at": "2026-04-01"}),
        ("market " * 20, "undated"),
    ])
    loaded = FinancialSituationMemory("temporal", {"memory_dir": str(tmp_path)})
    assert loaded.get_memories("alpha market", n_matches=3, as_of="2026-03-02") == expected


def test_metadata_filters_also_apply_before_bm25_scoring():
    memory = FinancialSituationMemory("sectors")
    memory.add_situations([
        ("alpha beta", "first", {"sector": "semiconductors"}),
        ("alpha gamma", "second", {"sector": "semiconductors"}),
        ("market gamma", "third", {"sector": "semiconductors"}),
    ])
    expected = memory.get_memories("alpha", n_matches=3)
    memory.add_situations([("alpha " * 30, "unrelated", {"sector": "banks"})])
    assert memory.get_memories("alpha", n_matches=3, metadata_filters={"sector": "semiconductors"}) == expected


@pytest.mark.parametrize("metadata,eligible", [
    ({"outcome_known_at": "2026-03-01"}, True),
    ({"settlement_date": "2026-03-02"}, True),
    ({"outcome_known_at": "2026-03-01", "settlement_date": "2026-03-03"}, False),
    ({"outcome_known_at": "2026-03-03", "settlement_date": "2026-03-01"}, False),
    ({"outcome_known_at": "2026-03-01", "settlement_date": "invalid"}, False),
    ({"outcome_known_at": "2026-03-01", "trade_date": "2026-04-01"}, False),
    ({"outcome_known_at": "2026-03-01", "trade_date": None}, False),
    ({}, False),
])
def test_settlement_and_decision_dates_bound_memory(metadata, eligible):
    memory = FinancialSituationMemory("settlement")
    memory.add_situations([("earnings", "advice", metadata)])
    assert bool(memory.get_memories("earnings", as_of="2026-03-02")) is eligible


@pytest.mark.parametrize("factory,module", [
    (create_bull_researcher, None),
    (create_bear_researcher, None),
    (create_research_manager, "tradingagents.agents.managers.research_manager"),
    (create_portfolio_manager, "tradingagents.agents.managers.portfolio_manager"),
    (create_trader, "tradingagents.agents.trader.trader"),
])
def test_all_memory_consumers_use_their_own_research_cutoff(factory, module):
    memory = Mock()
    memory.get_memories.return_value = []
    state = {
        "company_of_interest": "AAPL", "analysis_date": "2026-03-02", "trade_date": "2026-02-27",
        "market_report": "market", "sentiment_report": "sentiment", "news_report": "news",
        "fundamentals_report": "fundamentals", "investment_plan": "plan", "trader_investment_plan": "trader plan",
        "investment_debate_state": {"count": 0, "history": ""},
        "risk_debate_state": {
            "history": "", "count": 0, "aggressive_history": "", "conservative_history": "",
            "neutral_history": "", "current_aggressive_response": "",
            "current_conservative_response": "", "current_neutral_response": "",
        },
    }
    if module:
        with patch(f"{module}.invoke_structured_decision_with_retry", return_value=(Mock(), "{}")):
            factory(Mock(), memory)(deepcopy(state))
    else:
        factory(Mock(), memory)(deepcopy(state))
    assert memory.get_memories.call_args.kwargs["as_of"] == state["analysis_date"]


@pytest.mark.parametrize("known,analysis", [
    ("2026-03-01", None), ("2026-03-02", None),
    ("2026-03-03", "2026-03-03"), ("invalid", None),
])
def test_reflection_rejects_invalid_outcomes_before_llm_or_memory(known, analysis):
    llm, memory = Mock(), Mock()
    state = {"trade_date": "2026-03-02", "outcome_known_at": known, "analysis_date": analysis}
    with pytest.raises(ValueError):
        Reflector(llm).reflect_bull_researcher(state, 0.1, memory)
    llm.invoke.assert_not_called()
    memory.add_situations.assert_not_called()


def test_reflection_preserves_settlement_bound():
    assert Reflector._outcome_metadata({
        "company_of_interest": "AAPL", "trade_date": "2026-03-02",
        "outcome_known_at": "2026-03-03", "settlement_date": "2026-03-05",
    }) == {
        "symbol": "AAPL", "trade_date": "2026-03-02",
        "outcome_known_at": "2026-03-03", "settlement_date": "2026-03-05",
    }


def fetch_dart(payload):
    response = Mock()
    response.json.return_value = payload
    with (
        patch.object(opendart, "_resolve_corp_code", return_value=("00126380", "005930")),
        patch.object(opendart, "_get_opendart_key", return_value="fixture-key"),
        patch.object(opendart.requests, "get", return_value=response),
    ):
        return opendart.fetch_disclosures_opendart("005930.KS", "2026-03-01", "2026-03-02")


def test_opendart_filters_unknown_malformed_and_out_of_window_filings():
    items = fetch_dart({"status": "000", "list": [
        {"report_nm": "first day", "rcept_dt": "20260301"},
        {"report_nm": "last day", "rcept_dt": "20260302"},
        {"report_nm": "future", "rcept_dt": "20260303"},
        {"report_nm": "old", "rcept_dt": "20260228"},
        {"report_nm": "undated"}, {"rcept_dt": "invalid"}, {"rcept_dt": "202631"}, None,
    ]})
    assert [item.title for item in items] == ["005930: first day", "005930: last day"]
    assert all(item.published_at.utcoffset() == timedelta(hours=9) for item in items)


def test_opendart_request_limit_is_unavailable_rather_than_no_disclosures():
    with pytest.raises(VendorTransientError, match="020"):
        fetch_dart({"status": "020"})
    assert fetch_dart({"status": "013"}) == []


@pytest.mark.parametrize("payload", [[], None, {"status": "000", "list": {}}])
def test_opendart_malformed_response_is_not_success(payload):
    with pytest.raises(VendorMalformedResponseError):
        fetch_dart(payload)


@pytest.mark.parametrize("method", [
    "get_stock_data", "get_news", "get_company_news", "get_disclosures", "get_social_sentiment",
])
def test_reversed_date_windows_never_reach_a_vendor(method):
    vendor = Mock(return_value="unusable")
    with (
        run_config({"analysis_as_of": "2026-03-02", "tool_vendors": {method: "yfinance"}}),
        patch.dict("tradingagents.dataflows.interface.VENDOR_METHODS", {method: {"yfinance": vendor}}),
        pytest.raises(VendorInputError, match="start_date"),
    ):
        route_to_vendor(method, "AAPL", "2026-03-02", "2026-03-01")
    vendor.assert_not_called()


def test_av_rejects_publication_before_its_fiscal_period():
    with patch.object(av, "get_config", return_value={"point_in_time_strict": True}):
        result = av._filter_reports_by_date(json.dumps({"annualReports": [
            {"fiscalDateEnding": "2025-12-31", "reportedDate": "2025-01-01"},
            {"fiscalDateEnding": "2025-12-31", "reportedDate": "2026-02-01"},
        ]}), "2026-03-01")
    assert json.loads(result)["annualReports"] == [
        {"fiscalDateEnding": "2025-12-31", "reportedDate": "2026-02-01"},
    ]


@pytest.mark.parametrize("function", [
    y_finance.get_fundamentals, y_finance.get_balance_sheet,
    y_finance.get_income_statement, y_finance.get_cashflow,
])
def test_yahoo_snapshots_remain_withheld_historically(function):
    with patch.object(y_finance.yf, "Ticker") as ticker:
        result = function("AAPL", curr_date="2020-01-01")
    assert "historical" in result.lower()
    ticker.assert_not_called()
