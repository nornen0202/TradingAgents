import json
from datetime import date, timedelta
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration, LLMResult

from cli.stats_handler import StatsCallbackHandler
from tradingagents.dataflows import alpha_vantage_news
from tradingagents.dataflows.vendor_exceptions import VendorMalformedResponseError
from tradingagents.llm_clients.codex_app_server import CodexStructuredOutputError
from tradingagents.llm_clients.factory import create_llm_client
from tradingagents.scheduled import runner
from tradingagents.scheduled.config import load_scheduled_config


def test_large_insider_history_returns_recent_whole_records_and_coverage(monkeypatch):
    rows = [{"transaction_date": (date(2026, 9, 22) - timedelta(days=i)).isoformat(),
             "ticker": "AAPL", "executive": "Example officer", "shares": "123.45", "share_price": "329.40"}
            for i in range(7154)]
    fetch = Mock(return_value=json.dumps({"data": list(reversed(rows))}))
    monkeypatch.setattr(alpha_vantage_news, "_make_api_request", fetch)
    text = alpha_vantage_news.get_insider_transactions("AAPL")
    result = json.loads(text)
    assert result["data"] == rows[:100]
    assert len(text) < 120_000
    assert result["_coverage"]["omitted_row_count"] == 7054
    assert result["_coverage"]["truncated"] is True
    assert result["_coverage"]["point_in_time_verified"] is False
    assert "not complete historical activity" in result["_coverage"]["scope"]
    fetch.assert_called_once_with("INSIDER_TRANSACTIONS", {"symbol": "AAPL"})


def test_insider_budget_keeps_json_records_and_counts_omitted_rows():
    rows = [{"transaction_date": "2026-09-22", "detail": "x" * 500} for _ in range(10)]
    result = json.loads(alpha_vantage_news._bounded_insider_response({"data": rows}, max_chars=1800))
    assert 0 < len(result["data"]) < len(rows)
    assert result["data"] == rows[:len(result["data"])]
    assert result["_coverage"]["returned_row_count"] + result["_coverage"]["omitted_row_count"] == 10


@pytest.mark.parametrize("raw", ["not json", {}, {"data": [{"transaction_date": "unknown"}]}])
def test_malformed_insider_payload_does_not_look_like_collected_evidence(raw):
    with pytest.raises(VendorMalformedResponseError):
        alpha_vantage_news._bounded_insider_response(raw)


def test_oversized_prompt_fails_before_provider_and_never_becomes_fallback():
    session = Mock()
    llm = create_llm_client("codex", "gpt-6-sol", codex_binary="C:/fake/codex",
                            codex_workspace_dir="C:/tmp/test-workspace", codex_max_retries=0,
                            codex_fallback_on_app_server_error=True,
                            session_factory=lambda **kwargs: session,
                            preflight_runner=lambda **kwargs: None).get_llm()
    with pytest.raises(CodexStructuredOutputError, match="input budget"):
        llm.invoke("x" * 1_000_001)
    session.invoke.assert_not_called()


def test_fallback_callback_survives_localized_text_and_cleared_messages(tmp_path, monkeypatch):
    stats = StatsCallbackHandler()
    stats.on_llm_end(LLMResult(generations=[[ChatGeneration(message=AIMessage(
        content="번역된 대체 응답", response_metadata={"codex_fallback": True}))]]))
    assert stats.get_stats()["llm_fallback_calls"] == 1
    config_path = tmp_path / "test.toml"
    config_path.write_text('[run]\ntickers=["AAPL"]\n[storage]\narchive_dir="./archive"\nsite_dir="./site"\n', encoding="utf-8")
    config = load_scheduled_config(config_path)
    graph = SimpleNamespace(propagate=lambda *args, **kwargs: ({"messages": []}, "HOLD"), close=lambda: None)
    monkeypatch.setattr(runner, "TradingAgentsGraph", lambda *args, **kwargs: graph)
    monkeypatch.setattr(runner, "StatsCallbackHandler", lambda: stats)
    monkeypatch.setattr(runner, "resolve_instrument", lambda ticker: SimpleNamespace(display_name="Apple"))
    result = runner._run_single_ticker(config=config, ticker="AAPL", run_dir=tmp_path / "run",
                                       engine_results_dir=tmp_path / "engine", trade_date_override="2026-09-29")
    assert result["status"] == "failed" and result["decision"] is None
    assert "full analysis is incomplete" in result["error"]
    assert result["metrics"]["llm_fallback_calls"] == 1
    assert not (tmp_path / "run/tickers/AAPL/analysis.json").exists()


@pytest.mark.parametrize("path", ["config/scheduled_analysis.toml", "config/scheduled_analysis_korea.toml"])
def test_official_full_profiles_require_actual_model_responses(path):
    assert load_scheduled_config(path).llm.codex_fallback_on_app_server_error is False
