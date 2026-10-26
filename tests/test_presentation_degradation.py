from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from tradingagents.agents.utils import agent_utils
from tradingagents.graph import trading_graph
from tradingagents.graph.signal_processing import SignalProcessor
from tradingagents.llm_clients.codex_app_server import (
    CodexAppServerError, CodexAppServerAuthError, CodexAppServerBinaryError,
    CodexAppServerStorageError, CodexAppServerTimeoutError,
    CodexModelUnavailableError, CodexStructuredOutputError,
)
from tradingagents.schemas import StructuredDecisionValidationError, parse_structured_decision


@pytest.fixture(autouse=True)
def korean_llm_backend(monkeypatch):
    monkeypatch.setattr(agent_utils, "get_output_language", lambda: "Korean")
    monkeypatch.setattr(trading_graph, "get_output_language", lambda: "Korean")
    monkeypatch.setattr(agent_utils, "get_translation_settings",
                        lambda: SimpleNamespace(backend="llm", allow_llm_fallback=True))


def decision_text():
    return json.dumps({
        "rating": "HOLD", "portfolio_stance": "BULLISH", "entry_action": "WAIT",
        "conditional_entry_action": "STARTER", "conditional_entry_valid_until": "2026-10-26T14:30:00+09:00",
        "risk_action": "HOLD", "setup_quality": "DEVELOPING", "confidence": .62,
        "time_horizon": "medium", "entry_logic": "Confirm above 100.25.",
        "exit_logic": "Reduce below 90.5.", "position_sizing": "Risk 0.5%.",
        "risk_limits": "Do not chase above 110.", "catalysts": ["Growth 20%."],
        "invalidators": ["Close below 90.5."], "watchlist_triggers": ["Volume above 1.2x."],
        "execution_levels": {"levels": [{"level_type": "BREAKOUT", "price": 100.25,
                                         "confirmation": "close", "volume": 1.2}]},
    }, ensure_ascii=False)


def full_state(*, already_korean=False):
    narrative = "시장 보고서 본문입니다." if already_korean else "Market source 100.25."
    raw = decision_text()
    return {
        "company_of_interest": "278470.KS", "trade_date": "2026-10-23", "analysis_date": "2026-10-26",
        "source_revision": "original-immutable-source", "approved_at": "2026-10-26T04:45:00+09:00",
        "market_data_asof": "2026-10-23T15:30:00+09:00",
        "market_report": narrative, "sentiment_report": narrative,
        "news_report": narrative, "fundamentals_report": narrative,
        "investment_plan": raw, "trader_investment_plan": raw, "final_trade_decision": raw,
        "investment_debate_state": {"bull_history": narrative, "bear_history": narrative,
                                    "judge_decision": raw, "history": "original history"},
        "risk_debate_state": {"aggressive_history": narrative, "conservative_history": narrative,
                              "neutral_history": narrative, "judge_decision": raw,
                              "history": "original risk history"},
    }


def graph_with_llm(llm):
    graph = trading_graph.TradingAgentsGraph.__new__(trading_graph.TradingAgentsGraph)
    graph.output_thinking_llm = llm
    graph.quick_thinking_llm = llm
    return graph


@pytest.mark.parametrize("error_type", [CodexAppServerError, CodexAppServerAuthError,
    CodexAppServerBinaryError, CodexAppServerStorageError, CodexAppServerTimeoutError,
    CodexModelUnavailableError, CodexStructuredOutputError])
@pytest.mark.parametrize("structured_failure", [False, True])
def test_known_presentation_failure_preserves_original_and_skips_remaining_calls(error_type, structured_failure):
    llm = Mock()
    llm.invoke.side_effect = error_type("initialize sqlite failed; private-account secret-response")
    graph = graph_with_llm(llm)
    original = full_state(already_korean=structured_failure)
    before = deepcopy(original)
    localized = graph._localize_final_state(original)
    assert original == before and localized == before
    assert llm.invoke.call_count == 1
    assert localized["final_trade_decision"] == before["final_trade_decision"]
    assert parse_structured_decision(localized["final_trade_decision"]).to_dict() == parse_structured_decision(before["final_trade_decision"]).to_dict()
    metadata = graph.presentation_diagnostics
    assert metadata["status"] == "DEGRADED"
    assert metadata["language_completion"] == "INCOMPLETE_PRESERVED_ORIGINAL"
    assert metadata["reason_code"] == "CODEX_APP_SERVER_PRESENTATION_ERROR"
    fields = metadata["original_preserved_fields"]
    assert fields[0]["field"] == ("trader_investment_plan" if structured_failure else "market_report")
    assert fields[0]["disposition"] == "PROVIDER_ERROR"
    assert fields[0]["original_text_sha256"] == hashlib.sha256(before[fields[0]["field"]].encode()).hexdigest()
    assert len(fields) == (8 if structured_failure else 12)
    assert all(row["disposition"] == "SKIPPED_AFTER_PROVIDER_ERROR" for row in fields[1:])
    assert "secret-response" not in json.dumps(metadata) and "private-account" not in json.dumps(metadata)
    assert metadata["financial_action_fields_modified"] is False and metadata["execution_authorized"] is False


def test_unknown_presentation_exception_still_propagates():
    graph = graph_with_llm(Mock(invoke=Mock(side_effect=ValueError("unknown failure"))))
    with pytest.raises(ValueError, match="unknown failure"):
        graph._localize_final_state(full_state())
    assert graph.presentation_diagnostics["status"] == "STARTED"


def test_successful_prefix_is_not_reported_as_complete_when_later_backend_fails():
    llm = Mock()
    llm.invoke.side_effect = [SimpleNamespace(content="번역문: Market source 100.25."),
                              CodexAppServerError("initialize failed private detail")]
    graph = graph_with_llm(llm)
    original = full_state()
    localized = graph._localize_final_state(original)
    assert localized["market_report"] != original["market_report"]
    assert localized["sentiment_report"] == original["sentiment_report"]
    assert localized["trader_investment_plan"] == original["trader_investment_plan"]
    assert localized["final_trade_decision"] == original["final_trade_decision"]
    assert llm.invoke.call_count == 2
    assert graph.presentation_diagnostics["status"] == "DEGRADED"
    assert graph.presentation_diagnostics["language_completion"] == "INCOMPLETE_PRESERVED_ORIGINAL"
    assert graph.presentation_diagnostics["original_preserved_fields"][0]["field"] == "sentiment_report"
    assert len(graph.presentation_diagnostics["original_preserved_fields"]) == 11


def test_english_skip_returns_same_object_without_calling_translation(monkeypatch):
    monkeypatch.setattr(trading_graph, "get_output_language", lambda: "English")
    llm = Mock()
    graph = graph_with_llm(llm)
    original = full_state()
    assert graph._localize_final_state(original) is original
    llm.invoke.assert_not_called()
    assert graph.presentation_diagnostics["status"] == "NOT_REQUIRED"


def test_normal_translation_keeps_machine_fields_and_original_clocks():
    def translate(messages):
        text = messages[-1][1]
        try:
            fields = json.loads(text)
        except ValueError:
            return SimpleNamespace(content="번역문: " + text)
        return SimpleNamespace(content=json.dumps({key: "번역문: " + value for key, value in fields.items()}))
    llm = Mock(invoke=Mock(side_effect=translate))
    graph = graph_with_llm(llm)
    original = full_state()
    localized = graph._localize_final_state(original)
    assert graph.presentation_diagnostics["status"] == "PROCESSED"
    assert graph.presentation_diagnostics["language_completion"] == "NOT_INDEPENDENTLY_VERIFIED"
    assert graph.presentation_diagnostics["original_preserved_fields"] == []
    assert localized["market_report"] != original["market_report"]
    assert localized["final_trade_decision"] == original["final_trade_decision"]
    assert {k: localized[k] for k in ("source_revision", "approved_at", "market_data_asof")} == {
        k: original[k] for k in ("source_revision", "approved_at", "market_data_asof")}
    narratives = {"entry_logic", "exit_logic", "position_sizing", "risk_limits", "catalysts", "invalidators", "watchlist_triggers"}
    before = parse_structured_decision(original["trader_investment_plan"]).to_dict()
    after = json.loads(localized["trader_investment_plan"])
    assert {k: v for k, v in before.items() if k not in narratives} == {k: v for k, v in after.items() if k not in narratives}
    assert llm.invoke.call_count == 12  # Existing per-report/batched-decision translation count.


@pytest.mark.parametrize("core_error", [CodexAppServerError("financial node error"),
                                       StructuredDecisionValidationError("invalid financial decision")])
def test_financial_graph_errors_are_not_presentation_degradation(core_error):
    graph = graph_with_llm(Mock())
    graph.debug = False
    graph.prepare_run = Mock(return_value=({}, {}))
    graph.invoke_run = Mock(side_effect=core_error)
    graph._localize_final_state = Mock()
    with pytest.raises(type(core_error)):
        graph._propagate("278470.KS", "2026-10-23", analysis_date="2026-10-26")
    graph._localize_final_state.assert_not_called()


def test_invalid_final_financial_schema_remains_fatal_before_localization():
    graph = graph_with_llm(Mock())
    graph.debug = False
    graph.prepare_run = Mock(return_value=({}, {}))
    graph.invoke_run = Mock(return_value={"final_trade_decision": "invalid schema"})
    graph.signal_processor = SignalProcessor()
    graph._localize_final_state = Mock()
    with pytest.raises(StructuredDecisionValidationError):
        graph._propagate("278470.KS", "2026-10-23", analysis_date="2026-10-26")
    graph._localize_final_state.assert_not_called()


@pytest.mark.parametrize("financial_fallback", [False, True])
def test_runner_persists_new_presentation_metadata_without_relaxing_fallback_gate(tmp_path, monkeypatch, financial_fallback):
    from tradingagents.scheduled import runner
    from tradingagents.scheduled.config import load_scheduled_config
    path = tmp_path / "config.toml"
    path.write_text('[run]\ntickers=["AAPL"]\nmarket="US"\n[storage]\n'
                    f'archive_dir="{(tmp_path / "archive").as_posix()}"\nsite_dir="{(tmp_path / "site").as_posix()}"\n')
    config = load_scheduled_config(path)
    llm = Mock(invoke=Mock(side_effect=CodexAppServerStorageError("sqlite init private value")))
    graph = graph_with_llm(llm)
    original = full_state()
    graph.propagate = lambda *a, **kw: (graph._localize_final_state(original), "HOLD")
    graph.close = Mock()
    monkeypatch.setattr(runner, "TradingAgentsGraph", lambda *a, **kw: graph)
    stats = runner.StatsCallbackHandler()
    stats.get_stats = Mock(return_value={"llm_calls": 0, "tool_calls": 0, "tokens_in": 0,
                                       "tokens_out": 0, "llm_fallback_calls": int(financial_fallback)})
    monkeypatch.setattr(runner, "StatsCallbackHandler", lambda: stats)
    monkeypatch.setattr(runner, "polish_ticker_report", lambda state, **kw: (state, {}))
    monkeypatch.setattr(runner, "save_report_bundle", lambda state, ticker, directory, **kw: directory / "report.md")
    monkeypatch.setattr(runner, "build_public_equity_intelligence_artifacts", Mock(side_effect=ValueError("fixture")))
    monkeypatch.setattr(runner, "build_execution_contract", Mock(side_effect=ValueError("fixture")))
    monkeypatch.setattr("tradingagents.charting.report.build_review", Mock(side_effect=ValueError("fixture")))
    result = runner._run_single_ticker(config=config, ticker="AAPL", run_dir=tmp_path / "run",
                                      engine_results_dir=tmp_path / "engine", trade_date_override="2026-10-23")
    artifact = tmp_path / "run/tickers/AAPL" / ("error.json" if financial_fallback else "analysis.json")
    payload = json.loads(artifact.read_text())
    assert result["status"] == ("failed" if financial_fallback else "success")
    assert payload["presentation_diagnostics"] == graph.presentation_diagnostics
    assert payload["presentation_diagnostics"]["status"] == "DEGRADED"
    assert llm.invoke.call_count == 1 and graph.close.call_count == 1
    if financial_fallback:
        assert "LLM fallback" in payload["error"]
    else:
        assert payload["decision"] == original["final_trade_decision"]
        assert payload["metrics"]["llm_fallback_calls"] == 0
    metadata_copy = runner._presentation_diagnostics(graph)
    metadata_copy["original_preserved_fields"].clear()
    assert graph.presentation_diagnostics["original_preserved_fields"]


def degraded_receipt():
    graph = graph_with_llm(Mock(invoke=Mock(side_effect=CodexAppServerError("private-error"))))
    graph._localize_final_state(full_state())
    return graph.presentation_diagnostics


@pytest.mark.parametrize("change", [
    lambda d: d.update(private_owner="private-owner"),
    lambda d: d.update(reason_code="private-error"),
    lambda d: d.update(status="private-status"),
    lambda d: d.update(schema="private-schema"),
    lambda d: d.update(financial_action_fields_modified=0),
    lambda d: d.update(execution_authorized=True),
    lambda d: d["original_preserved_fields"][0].update(private_cost=999),
    lambda d: d["original_preserved_fields"][0].update(field="private-owner"),
    lambda d: d["original_preserved_fields"][0].update(disposition="private-error"),
    lambda d: d["original_preserved_fields"][0].update(original_text_sha256="private-original"),
    lambda d: d["original_preserved_fields"].append(d["original_preserved_fields"][0]),
])
def test_runner_diagnostics_rejects_unknown_keys_values_and_nonboolean_authority(change):
    from tradingagents.scheduled.runner import _presentation_diagnostics
    diagnostics = degraded_receipt()
    change(diagnostics)
    receipt = _presentation_diagnostics(SimpleNamespace(presentation_diagnostics=diagnostics))
    assert receipt["status"] == "UNVERIFIED"
    assert "private-" not in json.dumps(receipt) and "private_cost" not in json.dumps(receipt)
    assert receipt["original_preserved_fields"] == []


def test_runner_diagnostic_getter_failure_never_masks_original_error():
    from tradingagents.scheduled.runner import _presentation_diagnostics
    class BrokenGraph:
        @property
        def presentation_diagnostics(self):
            raise RuntimeError("private getter failure")
    original = ValueError("original financial failure")
    with pytest.raises(ValueError, match="original financial failure") as caught:
        try:
            raise original
        except ValueError:
            receipt = _presentation_diagnostics(BrokenGraph())
            assert receipt["status"] == "UNVERIFIED"
            assert "private" not in json.dumps(receipt)
            raise
    assert caught.value is original
    assert _presentation_diagnostics(None)["status"] == "NOT_RECORDED"


def report_bytes(directory):
    return {path.relative_to(directory).as_posix(): path.read_bytes()
            for path in directory.rglob("*") if path.is_file()}


@pytest.mark.parametrize("diagnostics", [None, {
    "schema": "tradingagents.presentation-diagnostics/v1", "status": "PROCESSED"}])
def test_legacy_none_and_normal_report_bytes_are_unchanged(tmp_path, diagnostics):
    from tradingagents.reporting import save_report_bundle
    state = {"market_report": "Original market report 100.25.", "analysis_date": "2026-10-26", "trade_date": "2026-10-23"}
    generated = datetime(2026, 10, 26, 8, 30, tzinfo=timezone.utc)
    save_report_bundle(state, "AAPL", tmp_path / "original", generated_at=generated)
    save_report_bundle(state, "AAPL", tmp_path / "explicit", generated_at=generated,
                       presentation_diagnostics=diagnostics)
    assert report_bytes(tmp_path / "original") == report_bytes(tmp_path / "explicit")


@pytest.mark.parametrize("html", [False, True])
def test_degraded_report_adds_only_static_complete_report_notice(tmp_path, html):
    from tradingagents.reporting import save_report_bundle
    state = {"market_report": "Original market report 100.25.", "analysis_date": "2026-10-26", "trade_date": "2026-10-23"}
    before = deepcopy(state)
    generated = datetime(2026, 10, 26, 8, 30, tzinfo=timezone.utc)
    save_report_bundle(state, "AAPL", tmp_path / "original", generated_at=generated, html=html)
    diagnostics = degraded_receipt()
    diagnostics["private_owner"] = "private-owner"
    diagnostics["private_cost"] = 999
    save_report_bundle(state, "AAPL", tmp_path / "degraded", generated_at=generated, html=html,
                       presentation_diagnostics=diagnostics)
    notice = "언어 변환 미완료(DEGRADED): 변환되지 않은 원문을 보존했습니다. 금융 판단·가격·승인 조건은 변경하지 않았습니다."
    assert state == before
    original, degraded = report_bytes(tmp_path / "original"), report_bytes(tmp_path / "degraded")
    assert set(original) == set(degraded)
    for name, content in degraded.items():
        text = content.decode()
        assert "private-owner" not in text and "private_cost" not in text
        if name in {"complete_report.md", "complete_report.html"}:
            assert notice in text and text.count(notice) == 1
            assert "Original market report 100.25." in text
        else:
            assert content == original[name]
