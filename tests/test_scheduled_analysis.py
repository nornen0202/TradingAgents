import json
import tempfile
import unittest
from datetime import date
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import tradingagents.scheduled.runner as scheduled_runner
from tradingagents.scheduled.runner import execute_scheduled_run, load_scheduled_config, main, resolve_trade_date


class _FakeStatsHandler:
    def get_stats(self):
        return {
            "llm_calls": 12,
            "tool_calls": 7,
            "tokens_in": 1024,
            "tokens_out": 2048,
        }


class _ZeroToolStatsHandler:
    def get_stats(self):
        return {
            "llm_calls": 5,
            "tool_calls": 0,
            "tokens_in": 100,
            "tokens_out": 200,
        }


class _FakeTradingAgentsGraph:
    def __init__(self, selected_analysts, debug=False, config=None, callbacks=None):
        self.selected_analysts = selected_analysts
        self.debug = debug
        self.config = config or {}
        self.callbacks = callbacks or []

    def propagate(self, ticker, trade_date, analysis_date=None):
        if ticker == "FAIL":
            raise RuntimeError("synthetic failure")

        final_state = {
            "company_of_interest": ticker,
            "instrument_profile": {"display_name": "NVIDIA Corporation"},
            "trade_date": trade_date,
            "analysis_date": analysis_date or trade_date,
            "market_report": f"## Market\n{ticker} market analysis",
            "sentiment_report": f"## Sentiment\n{ticker} sentiment analysis",
            "news_report": f"## News\n{ticker} news analysis",
            "fundamentals_report": f"## Fundamentals\n{ticker} fundamentals analysis",
            "investment_debate_state": {
                "bull_history": f"{ticker} bull case",
                "bear_history": f"{ticker} bear case",
                "history": "debate transcript",
                "current_response": "",
                "judge_decision": f"{ticker} research manager decision",
            },
            "trader_investment_plan": f"{ticker} trading plan",
            "investment_plan": f"{ticker} investment plan",
            "risk_debate_state": {
                "aggressive_history": f"{ticker} aggressive case",
                "conservative_history": f"{ticker} conservative case",
                "neutral_history": f"{ticker} neutral case",
                "history": "risk transcript",
                "judge_decision": f"{ticker} final portfolio decision",
            },
            "final_trade_decision": f"{ticker} final trade decision",
        }
        return final_state, "BUY"


class _FakeWorkerProcess:
    def __init__(self, returncode=0, *, running=False):
        self.returncode = None if running else returncode
        self._returncode = returncode
        self.pid = 12345
        self.terminated = False

    def poll(self):
        return self.returncode

    def kill(self):
        self.terminated = True
        self.returncode = -9

    def wait(self, timeout=None):
        if self.returncode is None:
            self.returncode = self._returncode
        return self.returncode


class ScheduledAnalysisTests(unittest.TestCase):
    def test_load_scheduled_config_enables_report_polisher_by_default(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            config_path = root / "scheduled_analysis.toml"
            config_path.write_text(
                """
[run]
tickers = ["NVDA"]

[storage]
archive_dir = "./archive"
site_dir = "./site"
""",
                encoding="utf-8",
            )

            config = load_scheduled_config(config_path)

            self.assertTrue(config.run.report_polisher_enabled)
            self.assertTrue(config.portfolio.report_polisher_enabled)
            self.assertEqual(config.run.ticker_universe_mode, "config_only")
            self.assertFalse(config.run.parallel_ticker_execution)
            self.assertEqual(config.run.max_parallel_tickers, 1)
            self.assertEqual(config.run.per_ticker_timeout_minutes, 0.0)
            self.assertFalse(config.run.codex_circuit_breaker_enabled)

    def test_load_scheduled_config_rejects_invalid_ticker_universe_mode(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            config_path = root / "scheduled_analysis.toml"
            config_path.write_text(
                """
[run]
tickers = ["NVDA"]
ticker_universe_mode = "invalid_mode"

[storage]
archive_dir = "./archive"
site_dir = "./site"
""",
                encoding="utf-8",
            )

            with self.assertRaises(ValueError):
                load_scheduled_config(config_path)

    def test_resolve_trade_date_falls_back_when_yfinance_latest_lookup_is_transient(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            config_path = root / "scheduled_analysis.toml"
            config_path.write_text(
                """
[run]
tickers = ["NVDA"]
trade_date_mode = "latest_available"
latest_market_data_lookback_days = 14
timezone = "Asia/Seoul"

[storage]
archive_dir = "./archive"
site_dir = "./site"
""",
                encoding="utf-8",
            )
            config = load_scheduled_config(config_path)

            with (
                patch(
                    "tradingagents.scheduled.runner._fetch_recent_trade_date_history",
                    side_effect=TypeError("'NoneType' object is not subscriptable"),
                ),
                patch("tradingagents.scheduled.runner._previous_business_day", return_value=date(2026, 4, 15)),
            ):
                trade_date = resolve_trade_date("NVDA", config)

        self.assertEqual(trade_date, "2026-04-15")

    def test_execute_scheduled_run_archives_outputs_and_builds_site(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            config_path = root / "scheduled_analysis.toml"
            archive_dir = root / "archive"
            site_dir = root / "site"
            config_path.write_text(
                f"""
[run]
tickers = ["NVDA", "FAIL"]
analysts = ["market", "social", "news", "fundamentals"]
output_language = "Korean"
trade_date_mode = "latest_available"
timezone = "Asia/Seoul"
continue_on_ticker_error = true
report_polisher_enabled = false

[llm]
provider = "codex"
quick_model = "gpt-5.5"
deep_model = "gpt-5.5"
codex_reasoning_effort = "medium"

[translation]
backend = "nllb_ct2"
model = "nllb-200-distilled-600m"
allow_llm_fallback = true

[storage]
archive_dir = "{archive_dir.as_posix()}"
site_dir = "{site_dir.as_posix()}"

[site]
title = "Daily Reports"
subtitle = "Automated"

[ticker_names]
NVDA = "NVIDIA Override"
""",
                encoding="utf-8",
            )

            config = load_scheduled_config(config_path)
            with (
                patch("tradingagents.scheduled.runner.TradingAgentsGraph", _FakeTradingAgentsGraph),
                patch("tradingagents.scheduled.runner.StatsCallbackHandler", _FakeStatsHandler),
                patch("tradingagents.scheduled.runner.resolve_trade_date", return_value="2026-04-04"),
            ):
                manifest = execute_scheduled_run(config, run_label="test")

            self.assertEqual(manifest["status"], "partial_failure")
            self.assertEqual(manifest["summary"]["successful_tickers"], 1)
            self.assertEqual(manifest["summary"]["failed_tickers"], 1)
            self.assertEqual(manifest["settings"]["provider"], "codex")
            self.assertEqual(manifest["settings"]["deep_model"], "gpt-5.5")
            self.assertEqual(manifest["settings"]["quick_model"], "gpt-5.5")
            self.assertEqual(manifest["settings"]["translation_backend"], "nllb_ct2")
            self.assertEqual(manifest["settings"]["translation_model"], "nllb-200-distilled-600m")
            self.assertEqual(manifest["tickers"][0]["analysis_date"], manifest["started_at"][:10])

            run_dir = archive_dir / "runs" / manifest["started_at"][:4] / manifest["run_id"]
            self.assertTrue((run_dir / "run.json").exists())
            self.assertTrue((run_dir / "tickers" / "NVDA" / "report" / "complete_report.md").exists())
            self.assertTrue((run_dir / "tickers" / "FAIL" / "error.json").exists())

            index_html = (site_dir / "index.html").read_text(encoding="utf-8")
            run_html = (site_dir / "runs" / manifest["run_id"] / "index.html").read_text(encoding="utf-8")
            ticker_html = (site_dir / "runs" / manifest["run_id"] / "NVDA.html").read_text(encoding="utf-8")

            self.assertIn("Daily Reports", index_html)
            self.assertIn("partial failure", index_html)
            self.assertNotIn("overlay health", index_html)
            self.assertNotIn("judge health", index_html)
            self.assertNotIn("data coverage", index_html)
            self.assertNotIn("freshness", index_html)
            self.assertNotIn("identity integrity", index_html)
            self.assertNotIn("고급 진단", index_html)
            self.assertIn("NVDA", run_html)
            self.assertIn("NVIDIA Override (NVDA)", run_html)
            self.assertIn("Report", ticker_html)
            self.assertIn("기준 시각", ticker_html)
            self.assertIn("<strong>투자판단</strong><span>매수</span>", ticker_html)
            self.assertIn("<strong>오늘 할 일</strong>", ticker_html)
            self.assertNotIn("Decision scope", ticker_html)
            self.assertNotIn("Setup quality", ticker_html)
            self.assertNotIn("LLM calls", ticker_html)
            self.assertNotIn("Token usage", ticker_html)
            self.assertNotIn("Fallback count", ticker_html)
            self.assertIn("NVIDIA Override (NVDA)", ticker_html)
            self.assertNotIn("Quality flags", ticker_html)
            self.assertTrue((site_dir / "downloads" / manifest["run_id"] / "NVDA" / "complete_report.md").exists())

    def test_execute_scheduled_run_can_skip_site_build(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            config_path = root / "scheduled_analysis.toml"
            archive_dir = root / "archive"
            site_dir = root / "site"
            config_path.write_text(
                f"""
[run]
tickers = ["NVDA"]
analysts = ["market"]
timezone = "Asia/Seoul"
report_polisher_enabled = false

[storage]
archive_dir = "{archive_dir.as_posix()}"
site_dir = "{site_dir.as_posix()}"
""",
                encoding="utf-8",
            )

            config = load_scheduled_config(config_path)
            with (
                patch("tradingagents.scheduled.runner.TradingAgentsGraph", _FakeTradingAgentsGraph),
                patch("tradingagents.scheduled.runner.StatsCallbackHandler", _FakeStatsHandler),
                patch("tradingagents.scheduled.runner.resolve_trade_date", return_value="2026-04-04"),
                patch("tradingagents.scheduled.runner.build_site") as build_site_mock,
            ):
                manifest = execute_scheduled_run(config, run_label="skip-site", skip_site_build=True)

            self.assertEqual(manifest["status"], "success")
            self.assertTrue((archive_dir / "latest-run.json").exists())
            self.assertFalse((site_dir / "index.html").exists())
            build_site_mock.assert_not_called()

    def test_execute_scheduled_run_stops_before_time_budget_exhaustion(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            config_path = root / "scheduled_analysis.toml"
            archive_dir = root / "archive"
            site_dir = root / "site"
            config_path.write_text(
                f"""
[run]
tickers = ["NVDA", "AAPL", "MSFT"]
timezone = "Asia/Seoul"
continue_on_ticker_error = true
max_runtime_minutes = 20
min_remaining_minutes_for_next_ticker = 10

[storage]
archive_dir = "{archive_dir.as_posix()}"
site_dir = "{site_dir.as_posix()}"
""",
                encoding="utf-8",
            )
            config = load_scheduled_config(config_path)
            success_summary = {
                "ticker": "NVDA",
                "ticker_name": "NVIDIA Corporation",
                "status": "success",
                "analysis_date": "2026-04-05",
                "trade_date": "2026-04-04",
                "decision": "BUY",
                "started_at": "2026-04-05T09:13:00+09:00",
                "finished_at": "2026-04-05T09:20:00+09:00",
                "duration_seconds": 420.0,
                "metrics": {"llm_calls": 1, "tool_calls": 1, "tokens_in": 1, "tokens_out": 1},
                "artifacts": {},
            }
            with (
                patch("tradingagents.scheduled.runner.perf_counter", side_effect=[0.0, 0.0, 900.0]),
                patch("tradingagents.scheduled.runner.resolve_trade_date", return_value="2026-04-04"),
                patch("tradingagents.scheduled.runner._run_single_ticker", return_value=success_summary) as run_single,
            ):
                manifest = execute_scheduled_run(config, run_label="budget")

            self.assertEqual(run_single.call_count, 1)
            self.assertEqual(manifest["status"], "partial_failure")
            self.assertEqual(manifest["summary"]["total_tickers"], 3)
            self.assertEqual(manifest["summary"]["successful_tickers"], 1)
            self.assertEqual(manifest["summary"]["failed_tickers"], 2)
            self.assertEqual(manifest["summary"]["skipped_tickers"], 2)
            self.assertEqual([item["ticker"] for item in manifest["tickers"][1:]], ["AAPL", "MSFT"])
            self.assertTrue(all(item["status"] == "skipped" for item in manifest["tickers"][1:]))
            self.assertTrue(any("run_time_budget_exhausted" in item for item in manifest["warnings"]))
            run_dir = archive_dir / "runs" / manifest["started_at"][:4] / manifest["run_id"]
            self.assertTrue((run_dir / "run.json").exists())
            self.assertTrue((site_dir / "index.html").exists())

    def test_load_scheduled_config_parses_parallel_and_circuit_breaker_settings(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            config_path = root / "scheduled_analysis.toml"
            config_path.write_text(
                """
[run]
tickers = ["NVDA"]
parallel_ticker_execution = true
max_parallel_tickers = 2
per_ticker_timeout_minutes = 30
codex_circuit_breaker_enabled = true
max_consecutive_codex_failures = 3
fatal_error_patterns = ["usage limit", "model unavailable"]
daily_active_ticker_limit = 4
analysis_mode = "smoke"

[llm]
codex_preflight_mode = "workflow_once"
codex_fallback_on_app_server_error = true

[storage]
archive_dir = "./archive"
site_dir = "./site"
""",
                encoding="utf-8",
            )

            config = load_scheduled_config(config_path)

            self.assertTrue(config.run.parallel_ticker_execution)
            self.assertEqual(config.run.max_parallel_tickers, 2)
            self.assertEqual(config.run.per_ticker_timeout_minutes, 30)
            self.assertTrue(config.run.codex_circuit_breaker_enabled)
            self.assertEqual(config.run.max_consecutive_codex_failures, 3)
            self.assertEqual(config.run.fatal_error_patterns, ("usage limit", "model unavailable"))
            self.assertEqual(config.run.daily_active_ticker_limit, 4)
            self.assertEqual(config.run.analysis_mode, "smoke")
            self.assertEqual(config.llm.codex_preflight_mode, "workflow_once")
            self.assertTrue(config.llm.codex_fallback_on_app_server_error)

    def test_execute_scheduled_run_records_parallel_manifest_state(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            config_path = root / "scheduled_analysis.toml"
            archive_dir = root / "archive"
            site_dir = root / "site"
            config_path.write_text(
                f"""
[run]
tickers = ["NVDA", "AAPL"]
parallel_ticker_execution = true
max_parallel_tickers = 2
continue_on_ticker_error = true

[storage]
archive_dir = "{archive_dir.as_posix()}"
site_dir = "{site_dir.as_posix()}"
""",
                encoding="utf-8",
            )
            config = load_scheduled_config(config_path)
            summary = {
                "ticker": "NVDA",
                "ticker_name": "NVIDIA",
                "status": "success",
                "analysis_date": "2026-04-05",
                "trade_date": "2026-04-04",
                "decision": "BUY",
                "started_at": "2026-04-05T09:13:00+09:00",
                "finished_at": "2026-04-05T09:14:00+09:00",
                "duration_seconds": 60.0,
                "metrics": {"llm_calls": 1, "tool_calls": 1, "tokens_in": 1, "tokens_out": 1},
                "artifacts": {},
                "worker": {"mode": "subprocess", "elapsed_seconds": 60.0},
            }
            parallel_summary = {
                "enabled": True,
                "requested": True,
                "mode": "subprocess",
                "max_parallel_tickers": 2,
                "per_ticker_timeout_minutes": 0.0,
            }
            circuit = {"enabled": False, "triggered": False, "reason": None, "skipped_tickers": []}
            with (
                patch("tradingagents.scheduled.runner.resolve_trade_date", return_value="2026-04-04"),
                patch(
                    "tradingagents.scheduled.runner._run_parallel_tickers",
                    return_value=([summary, {**summary, "ticker": "AAPL", "ticker_name": "Apple"}], parallel_summary, circuit, []),
                ) as run_parallel,
            ):
                manifest = execute_scheduled_run(config, run_label="parallel")

            self.assertEqual(run_parallel.call_count, 1)
            self.assertTrue(manifest["parallel_ticker_execution"]["enabled"])
            self.assertEqual(manifest["parallel_ticker_execution"]["max_parallel_tickers"], 2)
            self.assertFalse(manifest["circuit_breaker"]["triggered"])
            self.assertEqual([item["ticker"] for item in manifest["tickers"]], ["NVDA", "AAPL"])

    def test_parallel_ticker_scheduler_starts_two_workers_and_preserves_manifest_order(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            config_path = root / "scheduled_analysis.toml"
            archive_dir = root / "archive"
            site_dir = root / "site"
            run_dir = archive_dir / "runs" / "2026" / "test"
            config_path.write_text(
                f"""
[run]
tickers = ["A", "B", "C"]
parallel_ticker_execution = true
max_parallel_tickers = 2
continue_on_ticker_error = true

[storage]
archive_dir = "{archive_dir.as_posix()}"
site_dir = "{site_dir.as_posix()}"
""",
                encoding="utf-8",
            )
            config = load_scheduled_config(config_path)
            started: list[str] = []

            def fake_start(**kwargs):
                ticker = kwargs["ticker"]
                index = kwargs["index"]
                started.append(ticker)
                summary_path = run_dir / "summaries" / f"{index}.json"
                stdout_path = run_dir / "logs" / f"{index}.out"
                stderr_path = run_dir / "logs" / f"{index}.err"
                summary_path.parent.mkdir(parents=True, exist_ok=True)
                stdout_path.parent.mkdir(parents=True, exist_ok=True)
                summary_path.write_text(
                    json.dumps(
                        {
                            "ticker": ticker,
                            "ticker_name": ticker,
                            "status": "success",
                            "analysis_date": "2026-04-05",
                            "trade_date": "2026-04-04",
                            "decision": "BUY",
                            "started_at": "2026-04-05T09:13:00+09:00",
                            "finished_at": "2026-04-05T09:14:00+09:00",
                            "duration_seconds": 60.0,
                            "metrics": {"llm_calls": 1, "tool_calls": 1, "tokens_in": 1, "tokens_out": 1},
                            "artifacts": {},
                        }
                    ),
                    encoding="utf-8",
                )
                return {
                    "ticker": ticker,
                    "index": index,
                    "process": _FakeWorkerProcess(),
                    "summary_path": summary_path,
                    "stdout_path": stdout_path,
                    "stderr_path": stderr_path,
                    "stdout_handle": stdout_path.open("w", encoding="utf-8"),
                    "stderr_handle": stderr_path.open("w", encoding="utf-8"),
                    "started_perf": 0.0,
                    "started_at": "2026-04-05T09:13:00+09:00",
                }

            with patch("tradingagents.scheduled.runner._start_ticker_worker", side_effect=fake_start):
                summaries, parallel, circuit, warnings = scheduled_runner._run_parallel_tickers(
                    config=config,
                    run_tickers=["A", "B", "C"],
                    run_dir=run_dir,
                    engine_results_dir=run_dir / "engine-results",
                    trade_date_override="2026-04-04",
                    timer_start=0.0,
                    max_runtime_seconds=None,
                    min_remaining_seconds=0.0,
                )

            self.assertEqual(started[:2], ["A", "B"])
            self.assertEqual([item["ticker"] for item in summaries], ["A", "B", "C"])
            self.assertTrue(parallel["enabled"])
            self.assertFalse(circuit["triggered"])
            self.assertEqual(warnings, [])

    def test_parallel_ticker_scheduler_opens_circuit_breaker_on_fatal_codex_error(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            config_path = root / "scheduled_analysis.toml"
            archive_dir = root / "archive"
            site_dir = root / "site"
            run_dir = archive_dir / "runs" / "2026" / "test"
            config_path.write_text(
                f"""
[run]
tickers = ["A", "B", "C"]
parallel_ticker_execution = true
max_parallel_tickers = 2
continue_on_ticker_error = true
codex_circuit_breaker_enabled = true
fatal_error_patterns = ["usage limit", "model unavailable"]

[storage]
archive_dir = "{archive_dir.as_posix()}"
site_dir = "{site_dir.as_posix()}"
""",
                encoding="utf-8",
            )
            config = load_scheduled_config(config_path)

            def fake_start(**kwargs):
                ticker = kwargs["ticker"]
                index = kwargs["index"]
                summary_path = run_dir / "summaries" / f"{index}.json"
                stdout_path = run_dir / "logs" / f"{index}.out"
                stderr_path = run_dir / "logs" / f"{index}.err"
                summary_path.parent.mkdir(parents=True, exist_ok=True)
                stdout_path.parent.mkdir(parents=True, exist_ok=True)
                status = "failed" if ticker == "A" else "success"
                error = "You've hit your usage limit." if ticker == "A" else ""
                summary_path.write_text(
                    json.dumps(
                        {
                            "ticker": ticker,
                            "ticker_name": ticker,
                            "status": status,
                            "analysis_date": "2026-04-05",
                            "trade_date": "2026-04-04",
                            "decision": None if status == "failed" else "BUY",
                            "error": error,
                            "started_at": "2026-04-05T09:13:00+09:00",
                            "finished_at": "2026-04-05T09:14:00+09:00",
                            "duration_seconds": 60.0,
                            "metrics": {"llm_calls": 0, "tool_calls": 0, "tokens_in": 0, "tokens_out": 0},
                            "artifacts": {},
                        }
                    ),
                    encoding="utf-8",
                )
                return {
                    "ticker": ticker,
                    "index": index,
                    "process": _FakeWorkerProcess(),
                    "summary_path": summary_path,
                    "stdout_path": stdout_path,
                    "stderr_path": stderr_path,
                    "stdout_handle": stdout_path.open("w", encoding="utf-8"),
                    "stderr_handle": stderr_path.open("w", encoding="utf-8"),
                    "started_perf": 0.0,
                    "started_at": "2026-04-05T09:13:00+09:00",
                }

            with patch("tradingagents.scheduled.runner._start_ticker_worker", side_effect=fake_start):
                summaries, _parallel, circuit, warnings = scheduled_runner._run_parallel_tickers(
                    config=config,
                    run_tickers=["A", "B", "C"],
                    run_dir=run_dir,
                    engine_results_dir=run_dir / "engine-results",
                    trade_date_override="2026-04-04",
                    timer_start=0.0,
                    max_runtime_seconds=None,
                    min_remaining_seconds=0.0,
                )

            self.assertTrue(circuit["triggered"])
            self.assertIn("fatal_pattern:usage limit", circuit["reason"])
            self.assertEqual(summaries[0]["status"], "failed")
            self.assertTrue(all(item["status"] == "skipped" for item in summaries[1:]))
            self.assertTrue(any("codex_circuit_breaker_opened" in item for item in warnings))

    def test_parallel_ticker_scheduler_continues_after_transient_codex_timeouts(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            config_path = root / "scheduled_analysis.toml"
            archive_dir = root / "archive"
            site_dir = root / "site"
            run_dir = archive_dir / "runs" / "2026" / "test"
            config_path.write_text(
                f"""
[run]
tickers = ["A", "B", "C", "D"]
parallel_ticker_execution = true
max_parallel_tickers = 2
continue_on_ticker_error = true
codex_circuit_breaker_enabled = true
max_consecutive_codex_failures = 3
fatal_error_patterns = ["usage limit", "model unavailable"]

[storage]
archive_dir = "{archive_dir.as_posix()}"
site_dir = "{site_dir.as_posix()}"
""",
                encoding="utf-8",
            )
            config = load_scheduled_config(config_path)
            started: list[str] = []

            def fake_start(**kwargs):
                ticker = kwargs["ticker"]
                index = kwargs["index"]
                started.append(ticker)
                summary_path = run_dir / "summaries" / f"{index}.json"
                stdout_path = run_dir / "logs" / f"{index}.out"
                stderr_path = run_dir / "logs" / f"{index}.err"
                summary_path.parent.mkdir(parents=True, exist_ok=True)
                stdout_path.parent.mkdir(parents=True, exist_ok=True)
                summary_path.write_text(
                    json.dumps(
                        {
                            "ticker": ticker,
                            "ticker_name": ticker,
                            "status": "failed",
                            "analysis_date": "2026-04-05",
                            "trade_date": None,
                            "decision": None,
                            "error": "Timed out waiting for Codex app-server after 170s.",
                            "started_at": "2026-04-05T09:13:00+09:00",
                            "finished_at": "2026-04-05T09:14:00+09:00",
                            "duration_seconds": 60.0,
                            "metrics": {"llm_calls": 0, "tool_calls": 0, "tokens_in": 0, "tokens_out": 0},
                            "artifacts": {},
                        }
                    ),
                    encoding="utf-8",
                )
                return {
                    "ticker": ticker,
                    "index": index,
                    "process": _FakeWorkerProcess(returncode=1),
                    "summary_path": summary_path,
                    "stdout_path": stdout_path,
                    "stderr_path": stderr_path,
                    "stdout_handle": stdout_path.open("w", encoding="utf-8"),
                    "stderr_handle": stderr_path.open("w", encoding="utf-8"),
                    "started_perf": 0.0,
                    "started_at": "2026-04-05T09:13:00+09:00",
                }

            with patch("tradingagents.scheduled.runner._start_ticker_worker", side_effect=fake_start):
                summaries, _parallel, circuit, warnings = scheduled_runner._run_parallel_tickers(
                    config=config,
                    run_tickers=["A", "B", "C", "D"],
                    run_dir=run_dir,
                    engine_results_dir=run_dir / "engine-results",
                    trade_date_override="2026-04-04",
                    timer_start=0.0,
                    max_runtime_seconds=None,
                    min_remaining_seconds=0.0,
                )

            self.assertEqual(started, ["A", "B", "C", "D"])
            self.assertFalse(circuit["triggered"])
            self.assertTrue(all(item["status"] == "failed" for item in summaries))
            self.assertFalse(any("codex_circuit_breaker_opened" in item for item in warnings))

    def test_parallel_ticker_scheduler_marks_worker_timeout(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            config_path = root / "scheduled_analysis.toml"
            archive_dir = root / "archive"
            site_dir = root / "site"
            run_dir = archive_dir / "runs" / "2026" / "test"
            config_path.write_text(
                f"""
[run]
tickers = ["A"]
parallel_ticker_execution = true
max_parallel_tickers = 2
per_ticker_timeout_minutes = 1
continue_on_ticker_error = true

[storage]
archive_dir = "{archive_dir.as_posix()}"
site_dir = "{site_dir.as_posix()}"
""",
                encoding="utf-8",
            )
            config = load_scheduled_config(config_path)

            def fake_start(**kwargs):
                index = kwargs["index"]
                stdout_path = run_dir / "logs" / f"{index}.out"
                stderr_path = run_dir / "logs" / f"{index}.err"
                stdout_path.parent.mkdir(parents=True, exist_ok=True)
                return {
                    "ticker": kwargs["ticker"],
                    "index": index,
                    "process": _FakeWorkerProcess(running=True),
                    "summary_path": run_dir / "summaries" / f"{index}.json",
                    "stdout_path": stdout_path,
                    "stderr_path": stderr_path,
                    "stdout_handle": stdout_path.open("w", encoding="utf-8"),
                    "stderr_handle": stderr_path.open("w", encoding="utf-8"),
                    "started_perf": 0.0,
                    "started_at": "2026-04-05T09:13:00+09:00",
                }

            with (
                patch("tradingagents.scheduled.runner._start_ticker_worker", side_effect=fake_start),
                patch("tradingagents.scheduled.runner.perf_counter", return_value=120.0),
            ):
                summaries, _parallel, _circuit, _warnings = scheduled_runner._run_parallel_tickers(
                    config=config,
                    run_tickers=["A"],
                    run_dir=run_dir,
                    engine_results_dir=run_dir / "engine-results",
                    trade_date_override="2026-04-04",
                    timer_start=0.0,
                    max_runtime_seconds=None,
                    min_remaining_seconds=0.0,
                )

            self.assertEqual(summaries[0]["status"], "failed")
            self.assertIn("per_ticker_timeout", summaries[0]["error"])

    def test_parallel_ticker_scheduler_terminates_running_workers_at_runtime_budget(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            config_path = root / "scheduled_analysis.toml"
            archive_dir = root / "archive"
            site_dir = root / "site"
            run_dir = archive_dir / "runs" / "2026" / "test"
            config_path.write_text(
                f"""
[run]
tickers = ["A"]
parallel_ticker_execution = true
max_parallel_tickers = 1
continue_on_ticker_error = true

[storage]
archive_dir = "{archive_dir.as_posix()}"
site_dir = "{site_dir.as_posix()}"
""",
                encoding="utf-8",
            )
            config = load_scheduled_config(config_path)
            process = _FakeWorkerProcess(running=True)

            def fake_start(**kwargs):
                index = kwargs["index"]
                stdout_path = run_dir / "logs" / f"{index}.out"
                stderr_path = run_dir / "logs" / f"{index}.err"
                stdout_path.parent.mkdir(parents=True, exist_ok=True)
                return {
                    "ticker": kwargs["ticker"],
                    "index": index,
                    "process": process,
                    "summary_path": run_dir / "summaries" / f"{index}.json",
                    "stdout_path": stdout_path,
                    "stderr_path": stderr_path,
                    "stdout_handle": stdout_path.open("w", encoding="utf-8"),
                    "stderr_handle": stderr_path.open("w", encoding="utf-8"),
                    "started_perf": 0.0,
                    "started_at": "2026-04-05T09:13:00+09:00",
                }

            perf_values = [0.0]

            def fake_perf_counter():
                if perf_values:
                    return perf_values.pop(0)
                return 120.0

            with (
                patch("tradingagents.scheduled.runner._start_ticker_worker", side_effect=fake_start),
                patch(
                    "tradingagents.scheduled.runner._terminate_worker_process",
                    side_effect=lambda proc: proc.kill(),
                ) as terminate_worker,
                patch("tradingagents.scheduled.runner.perf_counter", side_effect=fake_perf_counter),
            ):
                summaries, _parallel, _circuit, warnings = scheduled_runner._run_parallel_tickers(
                    config=config,
                    run_tickers=["A"],
                    run_dir=run_dir,
                    engine_results_dir=run_dir / "engine-results",
                    trade_date_override="2026-04-04",
                    timer_start=0.0,
                    max_runtime_seconds=60.0,
                    min_remaining_seconds=30.0,
                )

            terminate_worker.assert_called_once_with(process)
            self.assertTrue(process.terminated)
            self.assertEqual(summaries[0]["status"], "failed")
            self.assertIn("run_time_budget_exhausted", summaries[0]["error"])
            self.assertTrue(summaries[0]["worker"]["budget_exhausted"])
            self.assertTrue(any("run_time_budget_exhausted" in item for item in warnings))

    def test_post_processing_budget_guard_skips_optional_work_when_runtime_is_low(self):
        warnings: list[str] = []

        with patch("tradingagents.scheduled.runner.perf_counter", return_value=95.0):
            available = scheduled_runner._post_processing_budget_available(
                stage="performance",
                max_runtime_seconds=100.0,
                timer_start=0.0,
                min_required_seconds=10.0,
                warnings=warnings,
            )

        self.assertFalse(available)
        self.assertEqual(
            warnings,
            ["post_processing_budget_exhausted:stage=performance:remaining_seconds=5:min_required_seconds=10"],
        )

    def test_post_processing_budget_guard_allows_optional_work_when_runtime_is_available(self):
        warnings: list[str] = []

        with patch("tradingagents.scheduled.runner.perf_counter", return_value=80.0):
            available = scheduled_runner._post_processing_budget_available(
                stage="portfolio",
                max_runtime_seconds=100.0,
                timer_start=0.0,
                min_required_seconds=10.0,
                warnings=warnings,
            )

        self.assertTrue(available)
        self.assertEqual(warnings, [])

    def test_parallel_ticker_execution_is_disabled_when_continue_on_error_is_false(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            config_path = root / "scheduled_analysis.toml"
            archive_dir = root / "archive"
            site_dir = root / "site"
            config_path.write_text(
                f"""
[run]
tickers = ["A", "B"]
parallel_ticker_execution = true
max_parallel_tickers = 2
continue_on_ticker_error = false

[storage]
archive_dir = "{archive_dir.as_posix()}"
site_dir = "{site_dir.as_posix()}"
""",
                encoding="utf-8",
            )
            config = load_scheduled_config(config_path)

            self.assertFalse(scheduled_runner._should_run_tickers_in_parallel(config=config, ticker_count=2))

    def test_circuit_breaker_ignores_consecutive_transient_codex_timeouts(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            config_path = root / "scheduled_analysis.toml"
            config_path.write_text(
                """
[run]
tickers = ["A"]
codex_circuit_breaker_enabled = true
max_consecutive_codex_failures = 3
""",
                encoding="utf-8",
            )
            config = load_scheduled_config(config_path)
            summary = {"status": "failed", "error": "Timed out waiting for Codex app-server after 170s"}

            reason = scheduled_runner._circuit_breaker_reason(
                config=config,
                summary=summary,
                consecutive_codex_failures=3,
            )

            self.assertIsNone(reason)
            self.assertFalse(scheduled_runner._is_codex_failure_summary(summary))

    def test_codex_parallel_worker_count_is_capped(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            config_path = root / "scheduled_analysis.toml"
            config_path.write_text(
                """
[run]
tickers = ["A", "B", "C", "D", "E"]
parallel_ticker_execution = true
max_parallel_tickers = 5

[llm]
provider = "codex"
""",
                encoding="utf-8",
            )
            config = load_scheduled_config(config_path)

            with patch.dict("os.environ", {"TRADINGAGENTS_CODEX_MAX_PARALLEL_TICKERS_CAP": ""}, clear=False):
                effective, warning = scheduled_runner._effective_parallel_worker_count(
                    config=config,
                    ticker_count=5,
                )

            self.assertEqual(effective, 3)
            self.assertEqual(warning, "codex_parallel_ticker_cap_applied:requested=5:cap=3:effective=3")

    def test_main_site_only_rebuilds_from_existing_archive(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            archive_dir = root / "archive"
            site_dir = root / "site"
            run_dir = archive_dir / "runs" / "2026" / "20260405T091300_seed"
            ticker_dir = run_dir / "tickers" / "NVDA" / "report"
            ticker_dir.mkdir(parents=True, exist_ok=True)
            (ticker_dir / "complete_report.md").write_text("# Test report", encoding="utf-8")
            analysis_dir = run_dir / "tickers" / "NVDA"
            (analysis_dir / "analysis.json").write_text("{}", encoding="utf-8")
            (analysis_dir / "final_state.json").write_text("{}", encoding="utf-8")
            private_dir = run_dir / "portfolio-private"
            private_dir.mkdir(parents=True, exist_ok=True)
            (private_dir / "portfolio_report.md").write_text("# Portfolio report", encoding="utf-8")
            (private_dir / "portfolio_report.json").write_text("{}", encoding="utf-8")
            (private_dir / "status.json").write_text(
                json.dumps(
                    {
                        "status": "success",
                        "profile": "kr_kis_default",
                        "generated_at": "2026-04-05T09:21:00+09:00",
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            (run_dir / "run.json").write_text(
                json.dumps(
                    {
                        "version": 1,
                        "run_id": "20260405T091300_seed",
                        "label": "seed",
                        "status": "success",
                        "started_at": "2026-04-05T09:13:00+09:00",
                        "finished_at": "2026-04-05T09:20:00+09:00",
                        "timezone": "Asia/Seoul",
                        "settings": {
                            "provider": "codex",
                            "quick_model": "gpt-5.5",
                            "deep_model": "gpt-5.5",
                            "codex_reasoning_effort": "medium",
                            "output_language": "Korean",
                            "translation_backend": "nllb_ct2",
                            "translation_model": "nllb-200-distilled-600m",
                            "analysts": ["market", "social", "news", "fundamentals"],
                            "trade_date_mode": "latest_available",
                            "max_debate_rounds": 1,
                            "max_risk_discuss_rounds": 1,
                        },
                        "summary": {
                            "total_tickers": 1,
                            "successful_tickers": 1,
                            "failed_tickers": 0,
                        },
                        "tickers": [
                            {
                                "ticker": "NVDA",
                                "ticker_name": "NVIDIA Corporation",
                                "status": "success",
                                "analysis_date": "2026-04-05",
                                "trade_date": "2026-04-04",
                                "decision": "BUY",
                                "started_at": "2026-04-05T09:13:00+09:00",
                                "finished_at": "2026-04-05T09:20:00+09:00",
                                "duration_seconds": 420.0,
                                "metrics": {
                                    "llm_calls": 10,
                                    "tool_calls": 7,
                                    "tokens_in": 1000,
                                    "tokens_out": 2000,
                                },
                                "artifacts": {
                                    "analysis_json": "tickers/NVDA/analysis.json",
                                    "report_markdown": "tickers/NVDA/report/complete_report.md",
                                    "final_state_json": "tickers/NVDA/final_state.json",
                                    "graph_log_json": None,
                                },
                            }
                        ],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            config_path = root / "scheduled_analysis.toml"
            config_path.write_text(
                f"""
[run]
tickers = ["NVDA"]

[storage]
archive_dir = "{archive_dir.as_posix()}"
site_dir = "{site_dir.as_posix()}"
""",
                encoding="utf-8",
            )

            exit_code = main(["--config", str(config_path), "--site-only"])

            self.assertEqual(exit_code, 0)
            self.assertTrue((site_dir / "index.html").exists())

    def test_main_applies_parallel_cli_overrides(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            config_path = root / "scheduled_analysis.toml"
            archive_dir = root / "archive"
            site_dir = root / "site"
            config_path.write_text(
                f"""
[run]
tickers = ["NVDA", "AAPL", "MSFT"]

[storage]
archive_dir = "{archive_dir.as_posix()}"
site_dir = "{site_dir.as_posix()}"
""",
                encoding="utf-8",
            )
            captured = {}

            def fake_execute(config, *, run_label, skip_site_build=False):
                captured["config"] = config
                captured["skip_site_build"] = skip_site_build
                return {
                    "run_id": "test",
                    "status": "success",
                    "summary": {"successful_tickers": 0, "failed_tickers": 0},
                }

            with patch("tradingagents.scheduled.runner.execute_scheduled_run", side_effect=fake_execute):
                exit_code = main(
                    [
                        "--config",
                        str(config_path),
                        "--analysis-mode",
                        "smoke",
                        "--max-parallel-tickers",
                        "2",
                        "--per-ticker-timeout-minutes",
                        "15",
                        "--daily-active-ticker-limit",
                        "3",
                    ]
                )

            self.assertEqual(exit_code, 0)
            config = captured["config"]
            self.assertEqual(config.run.analysis_mode, "smoke")
            self.assertEqual(config.run.max_parallel_tickers, 2)
            self.assertEqual(config.run.per_ticker_timeout_minutes, 15)
            self.assertEqual(config.run.daily_active_ticker_limit, 3)
            self.assertFalse(captured["skip_site_build"])

    def test_execute_scheduled_run_supports_account_only_ticker_universe_mode(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            config_path = root / "scheduled_analysis.toml"
            archive_dir = root / "archive"
            site_dir = root / "site"
            config_path.write_text(
                f"""
[run]
tickers = ["NVDA"]
ticker_universe_mode = "account_only"
analysts = ["market", "social", "news", "fundamentals"]
output_language = "Korean"
trade_date_mode = "latest_available"
timezone = "Asia/Seoul"
continue_on_ticker_error = true
report_polisher_enabled = false

[llm]
provider = "codex"
quick_model = "gpt-5.5"
deep_model = "gpt-5.5"

[storage]
archive_dir = "{archive_dir.as_posix()}"
site_dir = "{site_dir.as_posix()}"

[portfolio]
enabled = true
profile_path = "portfolio_profiles.toml"
profile_name = "kr_kis_default"
""",
                encoding="utf-8",
            )

            config = load_scheduled_config(config_path)
            fake_snapshot = SimpleNamespace(
                positions=(
                    SimpleNamespace(canonical_ticker="005930.KS"),
                    SimpleNamespace(canonical_ticker="000660.KS"),
                )
            )
            with (
                patch("tradingagents.scheduled.runner.load_portfolio_profile"),
                patch("tradingagents.scheduled.runner.load_snapshot_for_profile", return_value=fake_snapshot),
                patch("tradingagents.scheduled.runner.run_portfolio_pipeline", return_value={"status": "disabled"}),
                patch("tradingagents.scheduled.runner.TradingAgentsGraph", _FakeTradingAgentsGraph),
                patch("tradingagents.scheduled.runner.StatsCallbackHandler", _FakeStatsHandler),
                patch("tradingagents.scheduled.runner.resolve_trade_date", return_value="2026-04-04"),
            ):
                manifest = execute_scheduled_run(config, run_label="account-only")

            analyzed = [item["ticker"] for item in manifest["tickers"]]
            self.assertEqual(sorted(analyzed), ["000660.KS", "005930.KS"])

    def test_execute_scheduled_run_marks_quality_flag_when_no_tool_calls(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            config_path = root / "scheduled_analysis.toml"
            archive_dir = root / "archive"
            site_dir = root / "site"
            config_path.write_text(
                f"""
[run]
tickers = ["NVDA"]
continue_on_ticker_error = true
report_polisher_enabled = false

[llm]
provider = "codex"
quick_model = "gpt-5.5"
deep_model = "gpt-5.5"

[storage]
archive_dir = "{archive_dir.as_posix()}"
site_dir = "{site_dir.as_posix()}"
""",
                encoding="utf-8",
            )
            config = load_scheduled_config(config_path)
            with (
                patch("tradingagents.scheduled.runner.TradingAgentsGraph", _FakeTradingAgentsGraph),
                patch("tradingagents.scheduled.runner.StatsCallbackHandler", _ZeroToolStatsHandler),
                patch("tradingagents.scheduled.runner.resolve_trade_date", return_value="2026-04-04"),
            ):
                manifest = execute_scheduled_run(config, run_label="quality")

            ticker_summary = manifest["tickers"][0]
            self.assertIn("no_tool_calls_detected", ticker_summary.get("quality_flags", []))


if __name__ == "__main__":
    unittest.main()
