from types import SimpleNamespace
from unittest.mock import Mock
import json

import pytest

from tradingagents.agents.utils.decision_provenance import DecisionProvenanceSession
from tradingagents.agents.utils.decision_retry import invoke_structured_decision_with_retry


@pytest.mark.parametrize("failure", [False, True])
def test_new_analysis_or_error_persists_trace_after_scope_reset(tmp_path, monkeypatch, failure):
    from tradingagents.scheduled import runner
    from tradingagents.scheduled.config import load_scheduled_config
    path = tmp_path / "config.toml"
    path.write_text('[run]\ntickers=["AAPL"]\nmarket="US"\n[storage]\n'
                    f'archive_dir="{(tmp_path / "archive").as_posix()}"\nsite_dir="{(tmp_path / "site").as_posix()}"\n')
    config = load_scheduled_config(path)
    raw = json.dumps({"rating": "HOLD", "portfolio_stance": "BULLISH", "entry_action": "WAIT",
                      "setup_quality": "DEVELOPING", "confidence": .6, "time_horizon": "medium",
                      "entry_logic": "Wait.", "exit_logic": "Support.", "position_sizing": "No new allocation.",
                      "risk_limits": "Keep limits.", "catalysts": [], "invalidators": []})
    llm = Mock()
    llm.invoke.return_value = SimpleNamespace(content=raw)

    def propagate(*a, **kw):
        _, normalized = invoke_structured_decision_with_retry(llm, "fixture", context="portfolio manager final decision")
        if failure:
            raise RuntimeError("fixture graph failure")
        return {"company_of_interest":"AAPL", "final_trade_decision": normalized, "messages": []}, "HOLD"

    graph = SimpleNamespace(propagate=propagate, close=Mock())
    monkeypatch.setattr(runner, "TradingAgentsGraph", lambda *a, **kw: graph)
    monkeypatch.setattr(runner, "polish_ticker_report", lambda state, **kw: (state, {}))
    monkeypatch.setattr(runner, "save_report_bundle", lambda state, ticker, directory, **kw: directory / "report.md")
    monkeypatch.setattr(runner, "build_public_equity_intelligence_artifacts", Mock(side_effect=ValueError("fixture")))
    monkeypatch.setattr(runner, "build_execution_contract", Mock(side_effect=ValueError("fixture")))
    monkeypatch.setattr("tradingagents.charting.report.build_review", Mock(side_effect=ValueError("fixture")))
    outer = DecisionProvenanceSession("OTHER")
    with outer.capture():
        result = runner._run_single_ticker(config=config, ticker="AAPL", run_dir=tmp_path / "run",
                                          engine_results_dir=tmp_path / "engine", trade_date_override="2026-10-23")
        assert outer.receipt()["events"] == []
    artifact = tmp_path / "run/tickers/AAPL" / ("error.json" if failure else "analysis.json")
    payload = json.loads(artifact.read_text())
    receipt = payload["decision_provenance"]
    assert result["status"] == ("failed" if failure else "success")
    assert receipt["ticker"] == "AAPL" and receipt["status"] == "RECORDED"
    assert receipt["events"][0]["defaulted_fields"] == ["conditional_entry_action", "conditional_entry_valid_until"]
    assert llm.invoke.call_count == 1 and graph.close.call_count == 1
    if not failure:
        assert receipt["selected_binding"]["selected_machine_projection_matches"] is True
        assert receipt["selected_binding"]["selected_post_localization_text_sha256"]
