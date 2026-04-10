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
            self.assertTrue((private_dir / "portfolio_report.json").exists())
            self.assertTrue((private_dir / "portfolio_report.md").exists())
            self.assertTrue((private_dir / "proposed_orders.json").exists())
            self.assertTrue((private_dir / "decision_audit.json").exists())

            report_payload = json.loads((private_dir / "portfolio_report.json").read_text(encoding="utf-8"))
            self.assertEqual(report_payload["snapshot_id"], "20260410T073000_manual_test")
            self.assertEqual(report_payload["market_regime"], "constructive_but_selective")
            self.assertGreaterEqual(len(report_payload["actions"]), 2)

            published_portfolio_dir = site_dir / "downloads" / manifest["run_id"] / "portfolio"
            self.assertTrue((published_portfolio_dir / "portfolio_report.md").exists())
            self.assertTrue((published_portfolio_dir / "portfolio_report.json").exists())


if __name__ == "__main__":
    unittest.main()
