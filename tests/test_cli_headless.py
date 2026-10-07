from types import SimpleNamespace
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from cli.main import app, run_analysis
from cli.selections import unattended_selections
from tests.test_cli_unicode_logging import _DummyLive, _FakeTradingAgentsGraph


DEFAULTS = {
    "llm_provider": "codex", "quick_think_llm": "quick", "deep_think_llm": "deep",
    "output_think_llm": "output", "max_debate_rounds": 2, "max_risk_discuss_rounds": 3,
    "output_language": "Korean", "codex_reasoning_effort": "medium",
}


def test_flags_resolve_defaults_without_changing_them():
    result = unattended_selections({"ticker": " 005930.ks ", "date": "2026-04-05", "analysts": "news,sentiment,news"}, DEFAULTS)
    assert result["ticker"] == "005930.KS"
    assert [item.value for item in result["analysts"]] == ["social", "news"]
    assert result["output_language"] == "Korean"
    assert result["config_overrides"]["max_risk_discuss_rounds"] == 3
    assert result["config_overrides"]["output_think_llm"] == "output"


@pytest.mark.parametrize("ticker", ["../AAPL", "AAPL/../../etc", "C:\\tmp", "NUL", "CON.txt", "[red]AAPL", "AAPL\x1b", ".", "AAPL."])
def test_rejects_unsafe_ticker_before_any_side_effect(ticker):
    with pytest.raises(ValueError, match="ticker"):
        unattended_selections({"ticker": ticker, "date": "2026-04-05"}, DEFAULTS)


@pytest.mark.parametrize("date", [None, "2026-4-5", "2026-02-30", "9999-01-01"])
def test_rejects_invalid_dates(date):
    with pytest.raises(ValueError, match="date"):
        unattended_selections({"ticker": "AAPL", "date": date}, DEFAULTS)


def test_changing_provider_requires_corresponding_models():
    with pytest.raises(ValueError, match="quick-model"):
        unattended_selections({"ticker": "AAPL", "date": "2026-04-05", "provider": "openai"}, DEFAULTS)
    with pytest.raises(ValueError, match="deep-model"):
        unattended_selections({"ticker": "AAPL", "date": "2026-04-05", "deep_provider": "anthropic"}, DEFAULTS)


@pytest.mark.parametrize("ticker", ["^GSPC", "0700.HK", "TOO_LONG_FOR_THE_RESOLVER"])
def test_unsupported_tickers_fail_before_graph_construction(ticker):
    with patch("cli.main.run_analysis") as run:
        result = CliRunner().invoke(app, ["analyze", "--ticker", ticker, "--date", "2026-04-05"])
    assert result.exit_code != 0
    run.assert_not_called()


def test_bare_korean_code_is_canonicalized_before_file_paths():
    result = unattended_selections({"ticker": "005930", "date": "2026-04-05"}, DEFAULTS)
    assert result["ticker"] == "005930.KS"


def test_cli_passes_explicit_flags_without_prompts():
    with patch("cli.main.run_analysis") as run, patch("cli.main.DEFAULT_CONFIG", DEFAULTS):
        result = CliRunner().invoke(app, ["analyze", "--ticker", "AAPL", "--date", "2026-04-05", "--analysts", "market", "--no-show", "--no-html", "--parallel-analysts"])
    assert result.exit_code == 0, result.output
    assert run.call_args.kwargs["html"] is False
    assert run.call_args.kwargs["show"] is False
    assert run.call_args.kwargs["selections"]["config_overrides"]["parallel_analysts"] is True


def test_cli_incomplete_flags_fail_without_launching_graph():
    with patch("cli.main.run_analysis") as run:
        result = CliRunner().invoke(app, ["analyze", "--ticker", "AAPL"])
    assert result.exit_code != 0
    run.assert_not_called()


def test_repeated_unattended_runs_save_html_without_prompting_or_cross_run_logs(tmp_path):
    with (
        patch("cli.main.DEFAULT_CONFIG", {**DEFAULTS, "results_dir": str(tmp_path)}),
        patch("cli.main.TradingAgentsGraph", _FakeTradingAgentsGraph),
        patch("cli.main.StatsCallbackHandler", return_value=SimpleNamespace()),
        patch("cli.main.Live", _DummyLive), patch("cli.main.create_layout", return_value=object()),
        patch("cli.main.update_display"), patch("cli.main.update_analyst_statuses"),
        patch("cli.main.classify_message_type", return_value=("Agent", "한글")),
        patch("cli.main.typer.prompt", side_effect=AssertionError("Unexpected prompt")),
        patch("cli.main.get_user_selections", side_effect=AssertionError("Unexpected selections")),
        patch("cli.main.console.print"),
    ):
        for ticker in ("AAPL", "NVDA"):
            selections = unattended_selections({"ticker": ticker, "date": "2026-04-05", "analysts": "market"}, DEFAULTS)
            run_analysis(selections=selections)
    first_log = (tmp_path / "AAPL" / "2026-04-05" / "message_tool.log").read_text(encoding="utf-8")
    assert "Selected ticker: NVDA" not in first_log
    assert (tmp_path / "NVDA" / "2026-04-05" / "reports" / "complete_report.html").exists()
    assert (tmp_path / "AAPL" / "2026-04-05" / "reports" / "run_settings.json").exists()


@pytest.mark.parametrize("failure", [None, "stream", "save"])
def test_graph_context_closes_on_success_stream_error_and_save_error(tmp_path, failure):
    closed = []

    def fail(*args, **kwargs):
        raise RuntimeError(f"{failure} failed")

    class Graph(_FakeTradingAgentsGraph):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            if failure == "stream":
                self.graph.stream = fail

        def __exit__(self, *args):
            closed.append(True)

    with (
        patch("cli.main.DEFAULT_CONFIG", {**DEFAULTS, "results_dir": str(tmp_path)}),
        patch("cli.main.TradingAgentsGraph", Graph),
        patch("cli.main.StatsCallbackHandler", return_value=SimpleNamespace()),
        patch("cli.main.Live", _DummyLive), patch("cli.main.create_layout", return_value=object()),
        patch("cli.main.update_display"), patch("cli.main.update_analyst_statuses"),
        patch("cli.main.classify_message_type", return_value=("Agent", "한글")),
        patch("cli.main.console.print"),
        patch("cli.main.save_report_to_disk", side_effect=fail if failure == "save" else None, return_value=tmp_path / "complete_report.md"),
    ):
        selections = unattended_selections({"ticker": "AAPL", "date": "2026-04-05", "analysts": "market"}, DEFAULTS)
        if failure:
            with pytest.raises(RuntimeError, match=f"{failure} failed"):
                run_analysis(selections=selections)
        else:
            run_analysis(selections=selections)
    assert closed == [True]
