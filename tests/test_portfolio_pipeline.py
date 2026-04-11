import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tradingagents.scheduled.runner import execute_scheduled_run, load_scheduled_config


class _FakeStatsHandler:
    def get_stats(self):
        return {
            "llm_calls": 8,
            "tool_calls": 6,
            "tokens_in": 1200,
            "tokens_out": 900,
            "tokens_available": True,
        }


def _structured_decision_payload(rating: str, stance: str, entry_action: str, setup_quality: str, confidence: float) -> str:
    return json.dumps(
        {
            "rating": rating,
            "portfolio_stance": stance,
            "entry_action": entry_action,
            "setup_quality": setup_quality,
            "confidence": confidence,
            "time_horizon": "medium",
            "entry_logic": "structured entry logic",
            "exit_logic": "structured exit logic",
            "position_sizing": "starter size",
            "risk_limits": "1R",
            "catalysts": ["earnings revision"],
            "invalidators": ["support breakdown"],
            "watchlist_triggers": ["breakout confirmation"],
            "data_coverage": {
                "company_news_count": 5,
                "disclosures_count": 1,
                "social_source": "dedicated",
                "macro_items_count": 3,
            },
        },
        ensure_ascii=False,
    )


class _FakeStructuredDecisionGraph:
    def __init__(self, selected_analysts, debug=False, config=None, callbacks=None):
        self.selected_analysts = selected_analysts
        self.debug = debug
        self.config = config or {}
        self.callbacks = callbacks or []

    def propagate(self, ticker, trade_date, analysis_date=None):
        if ticker == "000660.KS":
            decision = _structured_decision_payload("NO_TRADE", "BULLISH", "WAIT", "DEVELOPING", 0.66)
        else:
            decision = _structured_decision_payload("HOLD", "BULLISH", "WAIT", "DEVELOPING", 0.61)

        final_state = {
            "company_of_interest": ticker,
            "instrument_profile": {"display_name": ticker},
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
            "final_trade_decision": decision,
        }
        return final_state, decision


class PortfolioPipelineTests(unittest.TestCase):
    def test_execute_scheduled_run_generates_private_portfolio_artifacts(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            archive_dir = root / "archive"
            site_dir = root / "site"
            manual_snapshot_path = root / "manual_snapshot.json"
            profile_path = root / "portfolio_profiles.toml"
            config_path = root / "scheduled_analysis.toml"

            manual_snapshot_path.write_text(
                json.dumps(
                    {
                        "snapshot_id": "20260410T073000_manual_test",
                        "as_of": "2026-04-10T07:30:00+09:00",
                        "broker": "manual",
                        "account_id": "manual-test",
                        "currency": "KRW",
                        "settled_cash_krw": 3000000,
                        "available_cash_krw": 3000000,
                        "buying_power_krw": 3000000,
                        "positions": [
                            {
                                "broker_symbol": "000660",
                                "canonical_ticker": "000660.KS",
                                "display_name": "SK하이닉스",
                                "sector": "Semiconductors",
                                "quantity": 10,
                                "available_qty": 10,
                                "avg_cost_krw": 180000,
                                "market_price_krw": 200000,
                                "market_value_krw": 2000000,
                                "unrealized_pnl_krw": 200000,
                            }
                        ],
                        "constraints": {
                            "min_cash_buffer_krw": 2500000,
                            "min_trade_krw": 100000,
                            "max_single_name_weight": 0.35,
                            "max_sector_weight": 0.50,
                            "max_daily_turnover_ratio": 0.30,
                            "max_order_count_per_day": 5,
                            "respect_existing_weights_softly": True,
                        },
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            profile_path.write_text(
                f"""
[profiles.manual_test]
enabled = true
broker = "manual"
broker_environment = "real"
read_only = true
manual_snapshot_path = "{manual_snapshot_path.as_posix()}"
private_output_dirname = "portfolio-private"
watch_tickers = ["000660.KS", "005930.KS"]
trigger_budget_krw = 500000
min_cash_buffer_krw = 2500000
min_trade_krw = 100000
max_single_name_weight = 0.35
max_sector_weight = 0.50
max_daily_turnover_ratio = 0.30
max_order_count_per_day = 5
respect_existing_weights_softly = true
continue_on_error = false
""",
                encoding="utf-8",
            )

            config_path.write_text(
                f"""
[run]
tickers = ["000660.KS", "005930.KS"]
continue_on_ticker_error = true

[llm]
provider = "codex"
quick_model = "gpt-5.4-mini"
deep_model = "gpt-5.4"
output_model = "gpt-5.4"

[storage]
archive_dir = "{archive_dir.as_posix()}"
site_dir = "{site_dir.as_posix()}"

[portfolio]
enabled = true
profile_path = "{profile_path.as_posix()}"
profile_name = "manual_test"
continue_on_error = false
""",
                encoding="utf-8",
            )

            config = load_scheduled_config(config_path)
            with (
                patch("tradingagents.scheduled.runner.TradingAgentsGraph", _FakeStructuredDecisionGraph),
                patch("tradingagents.scheduled.runner.StatsCallbackHandler", _FakeStatsHandler),
                patch("tradingagents.scheduled.runner.resolve_trade_date", return_value="2026-04-09"),
            ):
                manifest = execute_scheduled_run(config, run_label="portfolio-test")

            run_dir = archive_dir / "runs" / manifest["started_at"][:4] / manifest["run_id"]
            private_dir = run_dir / "portfolio-private"
            self.assertEqual((manifest.get("portfolio") or {}).get("status"), "success")
            self.assertTrue((private_dir / "status.json").exists())
            self.assertTrue((private_dir / "account_snapshot.json").exists())
            self.assertTrue((private_dir / "portfolio_candidates.json").exists())
            self.assertTrue((private_dir / "portfolio_semantic_verdicts.json").exists())
            self.assertTrue((private_dir / "portfolio_report.json").exists())
            self.assertTrue((private_dir / "portfolio_report.md").exists())
            self.assertTrue((private_dir / "portfolio_action_judge.json").exists())
            self.assertTrue((private_dir / "proposed_orders.json").exists())
            self.assertTrue((private_dir / "decision_audit.json").exists())

            report_payload = json.loads((private_dir / "portfolio_report.json").read_text(encoding="utf-8"))
            audit_payload = json.loads((private_dir / "decision_audit.json").read_text(encoding="utf-8"))
            report_markdown = (private_dir / "portfolio_report.md").read_text(encoding="utf-8")
            public_portfolio_page = (site_dir / "runs" / manifest["run_id"] / "portfolio.html").read_text(encoding="utf-8")
            self.assertEqual(report_payload["snapshot_id"], "20260410T073000_manual_test")
            self.assertEqual(report_payload["market_regime"], "constructive_but_selective")
            self.assertGreaterEqual(len(report_payload["actions"]), 2)
            self.assertEqual(audit_payload["snapshot_health"], "VALID")
            self.assertIn("판단 경로", report_markdown)
            self.assertIn("Rendered account report", public_portfolio_page)
            self.assertIn("TradingAgents 계좌 운용 리포트", public_portfolio_page)

    def test_execute_scheduled_run_applies_portfolio_llm_judges_when_enabled(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            archive_dir = root / "archive"
            site_dir = root / "site"
            manual_snapshot_path = root / "manual_snapshot.json"
            profile_path = root / "portfolio_profiles.toml"
            config_path = root / "scheduled_analysis.toml"

            manual_snapshot_path.write_text(
                json.dumps(
                    {
                        "snapshot_id": "20260410T073000_manual_test",
                        "as_of": "2026-04-10T07:30:00+09:00",
                        "broker": "manual",
                        "account_id": "manual-test",
                        "currency": "KRW",
                        "settled_cash_krw": 3000000,
                        "available_cash_krw": 3000000,
                        "buying_power_krw": 3000000,
                        "positions": [
                            {
                                "broker_symbol": "000660",
                                "canonical_ticker": "000660.KS",
                                "display_name": "SK하이닉스",
                                "sector": "Semiconductors",
                                "quantity": 10,
                                "available_qty": 10,
                                "avg_cost_krw": 180000,
                                "market_price_krw": 200000,
                                "market_value_krw": 2000000,
                                "unrealized_pnl_krw": 200000,
                            }
                        ],
                        "constraints": {
                            "min_cash_buffer_krw": 2500000,
                            "min_trade_krw": 100000,
                            "max_single_name_weight": 0.35,
                            "max_sector_weight": 0.50,
                            "max_daily_turnover_ratio": 0.30,
                            "max_order_count_per_day": 5,
                            "respect_existing_weights_softly": True,
                        },
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            profile_path.write_text(
                f"""
[profiles.manual_test]
enabled = true
broker = "manual"
broker_environment = "real"
read_only = true
manual_snapshot_path = "{manual_snapshot_path.as_posix()}"
private_output_dirname = "portfolio-private"
watch_tickers = ["000660.KS", "005930.KS"]
trigger_budget_krw = 500000
min_cash_buffer_krw = 2500000
min_trade_krw = 100000
max_single_name_weight = 0.35
max_sector_weight = 0.50
max_daily_turnover_ratio = 0.30
max_order_count_per_day = 5
respect_existing_weights_softly = true
continue_on_error = false
""",
                encoding="utf-8",
            )

            config_path.write_text(
                f"""
[run]
tickers = ["000660.KS", "005930.KS"]
continue_on_ticker_error = true

[llm]
provider = "codex"
quick_model = "gpt-5.4-mini"
deep_model = "gpt-5.4"
output_model = "gpt-5.4"

[storage]
archive_dir = "{archive_dir.as_posix()}"
site_dir = "{site_dir.as_posix()}"

[portfolio]
enabled = true
profile_path = "{profile_path.as_posix()}"
profile_name = "manual_test"
continue_on_error = false
semantic_judge_enabled = true
action_judge_enabled = true
action_judge_top_n = 2
""",
                encoding="utf-8",
            )

            config = load_scheduled_config(config_path)
            with (
                patch("tradingagents.scheduled.runner.TradingAgentsGraph", _FakeStructuredDecisionGraph),
                patch("tradingagents.scheduled.runner.StatsCallbackHandler", _FakeStatsHandler),
                patch("tradingagents.scheduled.runner.resolve_trade_date", return_value="2026-04-09"),
                patch("tradingagents.portfolio.semantic_judge._create_semantic_llm", return_value=object()),
                patch(
                    "tradingagents.portfolio.semantic_judge._invoke_semantic_llm",
                    side_effect=[
                        {
                            "thesis_strength": 0.84,
                            "timing_readiness": 0.46,
                            "trigger_type": "breakout_confirmation",
                            "trigger_horizon": "days_to_weeks",
                            "trigger_quality": 0.79,
                            "thesis_state": "constructive_but_not_confirmed",
                            "semantic_summary": "논지는 강하지만 타이밍 확인 전이라 조건부 증액이 적절합니다.",
                            "counter_evidence": ["즉시 추격 매수 근거 부족"],
                            "reason_codes": ["bullish_thesis_intact", "timing_not_confirmed"],
                            "review_required": False,
                        },
                        {
                            "thesis_strength": 0.72,
                            "timing_readiness": 0.41,
                            "trigger_type": "watch_only",
                            "trigger_horizon": "days_to_weeks",
                            "trigger_quality": 0.65,
                            "thesis_state": "constructive_but_not_confirmed",
                            "semantic_summary": "보유 전환보다 관찰 우선이 적절합니다.",
                            "counter_evidence": [],
                            "reason_codes": ["conditional_trigger_preferred"],
                            "review_required": False,
                        },
                    ],
                ),
                patch("tradingagents.portfolio.action_judge._create_action_llm", return_value=object()),
                patch(
                    "tradingagents.portfolio.action_judge._invoke_action_llm",
                    return_value={
                        "priority_order": ["000660.KS", "005930.KS"],
                        "reason_by_ticker": {
                            "000660.KS": {
                                "summary": "반도체 내 우선순위가 가장 높아 1순위 유지가 적절합니다.",
                                "reason_codes": ["semiconductor_priority"],
                                "review_required": False,
                            }
                        },
                        "portfolio_note": "반도체 익스포저는 높지만 현 시점에서는 SK하이닉스가 상대 우위입니다.",
                    },
                ),
            ):
                manifest = execute_scheduled_run(config, run_label="portfolio-judge-test")

            run_dir = archive_dir / "runs" / manifest["started_at"][:4] / manifest["run_id"]
            private_dir = run_dir / "portfolio-private"
            report_payload = json.loads((private_dir / "portfolio_report.json").read_text(encoding="utf-8"))
            semantic_payload = json.loads((private_dir / "portfolio_semantic_verdicts.json").read_text(encoding="utf-8"))
            action_payload = json.loads((private_dir / "portfolio_action_judge.json").read_text(encoding="utf-8"))
            public_portfolio_page = (site_dir / "runs" / manifest["run_id"] / "portfolio.html").read_text(encoding="utf-8")

            self.assertEqual(action_payload["status"], "success")
            self.assertGreaterEqual(len(semantic_payload["verdicts"]), 2)
            self.assertEqual(report_payload["actions"][0]["decision_source"], "RULE+DEEP+CODEX")
            self.assertIn("semiconductor_priority", report_payload["actions"][0]["reason_codes"])
            self.assertIn("Account report", public_portfolio_page)

            published_portfolio_dir = site_dir / "downloads" / manifest["run_id"] / "portfolio"
            self.assertTrue((published_portfolio_dir / "portfolio_report.md").exists())
            self.assertTrue((published_portfolio_dir / "portfolio_report.json").exists())

    def test_execute_scheduled_run_marks_watchlist_only_for_empty_underfunded_snapshot(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            archive_dir = root / "archive"
            site_dir = root / "site"
            manual_snapshot_path = root / "manual_snapshot.json"
            profile_path = root / "portfolio_profiles.toml"
            config_path = root / "scheduled_analysis.toml"

            manual_snapshot_path.write_text(
                json.dumps(
                    {
                        "snapshot_id": "20260410T073000_manual_watchlist",
                        "as_of": "2026-04-10T07:30:00+09:00",
                        "broker": "manual",
                        "account_id": "manual-watchlist",
                        "currency": "KRW",
                        "settled_cash_krw": 2,
                        "available_cash_krw": 2,
                        "buying_power_krw": 2,
                        "total_equity_krw": 2,
                        "snapshot_health": "WATCHLIST_ONLY",
                        "positions": [],
                        "constraints": {
                            "min_cash_buffer_krw": 2500000,
                            "min_trade_krw": 100000,
                            "max_single_name_weight": 0.35,
                            "max_sector_weight": 0.50,
                            "max_daily_turnover_ratio": 0.30,
                            "max_order_count_per_day": 5,
                            "respect_existing_weights_softly": True,
                        },
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            profile_path.write_text(
                f"""
[profiles.manual_watchlist]
enabled = true
broker = "manual"
broker_environment = "real"
read_only = true
manual_snapshot_path = "{manual_snapshot_path.as_posix()}"
private_output_dirname = "portfolio-private"
watch_tickers = ["000660.KS"]
trigger_budget_krw = 500000
min_cash_buffer_krw = 2500000
min_trade_krw = 100000
max_single_name_weight = 0.35
max_sector_weight = 0.50
max_daily_turnover_ratio = 0.30
max_order_count_per_day = 5
respect_existing_weights_softly = true
continue_on_error = false
""",
                encoding="utf-8",
            )

            config_path.write_text(
                f"""
[run]
tickers = ["000660.KS"]
continue_on_ticker_error = true

[llm]
provider = "codex"
quick_model = "gpt-5.4-mini"
deep_model = "gpt-5.4"
output_model = "gpt-5.4"

[storage]
archive_dir = "{archive_dir.as_posix()}"
site_dir = "{site_dir.as_posix()}"

[portfolio]
enabled = true
profile_path = "{profile_path.as_posix()}"
profile_name = "manual_watchlist"
continue_on_error = false
""",
                encoding="utf-8",
            )

            config = load_scheduled_config(config_path)
            with (
                patch("tradingagents.scheduled.runner.TradingAgentsGraph", _FakeStructuredDecisionGraph),
                patch("tradingagents.scheduled.runner.StatsCallbackHandler", _FakeStatsHandler),
                patch("tradingagents.scheduled.runner.resolve_trade_date", return_value="2026-04-09"),
            ):
                manifest = execute_scheduled_run(config, run_label="portfolio-watchlist-test")

            self.assertEqual((manifest.get("portfolio") or {}).get("status"), "watchlist_only")

    def test_execute_scheduled_run_generates_watchlist_only_profile_report(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            archive_dir = root / "archive"
            site_dir = root / "site"
            profile_path = root / "portfolio_profiles.toml"
            config_path = root / "scheduled_analysis.toml"

            profile_path.write_text(
                """
[profiles.us_watchlist]
enabled = true
broker = "watchlist"
broker_environment = "real"
read_only = true
private_output_dirname = "portfolio-private"
watch_tickers = ["AAPL"]
trigger_budget_krw = 0
min_cash_buffer_krw = 0
min_trade_krw = 100000
max_single_name_weight = 0.35
max_sector_weight = 0.50
max_daily_turnover_ratio = 0.30
max_order_count_per_day = 5
respect_existing_weights_softly = true
continue_on_error = false
""",
                encoding="utf-8",
            )

            config_path.write_text(
                f"""
[run]
tickers = ["AAPL"]
continue_on_ticker_error = true

[llm]
provider = "codex"
quick_model = "gpt-5.4-mini"
deep_model = "gpt-5.4"
output_model = "gpt-5.4"

[storage]
archive_dir = "{archive_dir.as_posix()}"
site_dir = "{site_dir.as_posix()}"

[portfolio]
enabled = true
profile_path = "{profile_path.as_posix()}"
profile_name = "us_watchlist"
continue_on_error = false
""",
                encoding="utf-8",
            )

            config = load_scheduled_config(config_path)
            with (
                patch("tradingagents.scheduled.runner.TradingAgentsGraph", _FakeStructuredDecisionGraph),
                patch("tradingagents.scheduled.runner.StatsCallbackHandler", _FakeStatsHandler),
                patch("tradingagents.scheduled.runner.resolve_trade_date", return_value="2026-04-09"),
            ):
                manifest = execute_scheduled_run(config, run_label="portfolio-us-watchlist-test")

            run_dir = archive_dir / "runs" / manifest["started_at"][:4] / manifest["run_id"]
            private_dir = run_dir / "portfolio-private"
            status_payload = json.loads((private_dir / "status.json").read_text(encoding="utf-8"))
            snapshot_payload = json.loads((private_dir / "account_snapshot.json").read_text(encoding="utf-8"))
            public_portfolio_page = (site_dir / "runs" / manifest["run_id"] / "portfolio.html").read_text(encoding="utf-8")

            self.assertEqual(status_payload["status"], "watchlist_only")
            self.assertEqual(snapshot_payload["snapshot_health"], "WATCHLIST_ONLY")
            self.assertIn("Rendered account report", public_portfolio_page)


if __name__ == "__main__":
    unittest.main()
