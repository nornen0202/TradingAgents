import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tradingagents.dataflows.institutional import (
    CAP_ESTIMATES,
    build_public_equity_intelligence,
    build_public_equity_intelligence_artifacts,
    provider_catalog,
    route_to_institutional_provider,
)
from tradingagents.scheduled.runner import execute_scheduled_run, load_scheduled_config


class _FakeStatsHandler:
    def get_stats(self):
        return {
            "llm_calls": 3,
            "tool_calls": 2,
            "tokens_in": 400,
            "tokens_out": 300,
            "tokens_available": True,
        }


class _FakeGraph:
    def __init__(self, selected_analysts, debug=False, config=None, callbacks=None):
        self.selected_analysts = selected_analysts
        self.debug = debug
        self.config = config or {}
        self.callbacks = callbacks or []

    def propagate(self, ticker, trade_date, analysis_date=None):
        decision = json.dumps(
            {
                "rating": "HOLD",
                "portfolio_stance": "BULLISH",
                "entry_action": "WAIT",
                "setup_quality": "DEVELOPING",
                "confidence": 0.61,
                "time_horizon": "medium",
                "entry_logic": "wait for confirmation",
                "exit_logic": "break thesis on guidance cut",
                "position_sizing": "starter only",
                "risk_limits": "1R",
                "catalysts": ["earnings revision"],
                "invalidators": ["guidance cut"],
                "watchlist_triggers": ["breakout confirmation"],
                "data_coverage": {
                    "company_news_count": 2,
                    "disclosures_count": 1,
                    "social_source": "news-derived",
                    "macro_items_count": 1,
                },
            },
            ensure_ascii=False,
        )
        final_state = {
            "company_of_interest": ticker,
            "instrument_profile": {"display_name": ticker},
            "trade_date": trade_date,
            "analysis_date": analysis_date or trade_date,
            "market_report": f"## Market\n{ticker} market setup",
            "sentiment_report": f"## Sentiment\n{ticker} sentiment",
            "news_report": f"## News\n{ticker} news",
            "fundamentals_report": f"## Fundamentals\n{ticker} fundamentals",
            "investment_debate_state": {
                "bull_history": "bull",
                "bear_history": "bear",
                "history": "debate",
                "current_response": "",
                "judge_decision": "manager",
            },
            "trader_investment_plan": "trader plan",
            "investment_plan": "investment plan",
            "risk_debate_state": {
                "aggressive_history": "aggressive",
                "conservative_history": "conservative",
                "neutral_history": "neutral",
                "history": "risk debate",
                "judge_decision": "final decision",
            },
            "final_trade_decision": decision,
        }
        return final_state, decision


class InstitutionalIntelligenceTests(unittest.TestCase):
    def test_provider_catalog_includes_public_and_paid_vendors(self):
        catalog = {item["id"]: item for item in provider_catalog()}
        self.assertIn("yfinance", catalog)
        self.assertIn("daloopa", catalog)
        self.assertIn("factset", catalog)
        self.assertEqual(catalog["yfinance"]["access"], "free")
        self.assertEqual(catalog["factset"]["access"], "paid")

    def test_imported_vendor_payload_enriches_evidence_and_earnings_pack(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            data_dir = Path(tmpdir)
            vendor_dir = data_dir / "daloopa" / "NVDA"
            vendor_dir.mkdir(parents=True)
            (vendor_dir / "financials.json").write_text(
                json.dumps(
                    {
                        "source_refs": [
                            {
                                "provider": "daloopa",
                                "title": "NVDA model export",
                                "document_type": "vendor_export",
                                "confidence": 0.9,
                            }
                        ],
                        "evidence_ledger": [
                            {
                                "claim": "Data center revenue accelerated.",
                                "direction": "support",
                                "metric": "data_center_revenue",
                                "period": "latest_quarter",
                                "quality": 0.9,
                                "source_refs": [
                                    {
                                        "provider": "daloopa",
                                        "title": "NVDA KPI export",
                                        "confidence": 0.9,
                                    }
                                ],
                            }
                        ],
                        "earnings_event_pack": {
                            "status": "available_imported",
                            "transcript_available": True,
                            "transcript_highlights": ["Management raised demand commentary."],
                            "consensus_delta": {"eps": "beat"},
                        },
                        "estimate_revision_direction": "positive",
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            final_state = {
                "fundamentals_report": "fundamentals text",
                "final_trade_decision": '{"rating":"HOLD"}',
            }
            tool_events = [
                {"method": "get_fundamentals", "vendor": "yfinance", "status": "success", "fallback": False}
            ]
            with patch.dict("os.environ", {"TRADINGAGENTS_INSTITUTIONAL_DATA_DIR": str(data_dir)}, clear=False):
                payload = build_public_equity_intelligence(
                    ticker="NVDA",
                    curr_date="2026-06-08",
                    final_state=final_state,
                    tool_events=tool_events,
                )

            self.assertEqual(payload["source_cohort"], "public_plus_institutional_imports")
            self.assertTrue(payload["earnings_event_pack"]["transcript_available"])
            self.assertEqual(payload["coverage"]["estimate_revision_direction"], "positive")
            self.assertGreater(payload["source_quality_score"], 0.3)

    def test_route_to_institutional_provider_prefers_imports_without_live_credentials(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            data_dir = Path(tmpdir)
            vendor_dir = data_dir / "factset" / "MSFT"
            vendor_dir.mkdir(parents=True)
            (vendor_dir / "estimates.json").write_text(
                json.dumps({"estimate_revision_direction": "neutral"}, ensure_ascii=False),
                encoding="utf-8",
            )
            with patch.dict("os.environ", {"TRADINGAGENTS_INSTITUTIONAL_DATA_DIR": str(data_dir)}, clear=False):
                payload = route_to_institutional_provider(CAP_ESTIMATES, "MSFT", "2026-06-08")

            self.assertEqual(payload["status"], "success")
            self.assertEqual(payload["mode"], "imported")
            self.assertEqual(payload["provider"]["id"], "factset")

    def test_artifact_builder_emits_required_sidecars(self):
        outputs = build_public_equity_intelligence_artifacts(
            ticker="AAPL",
            curr_date="2026-06-08",
            final_state={"fundamentals_report": "fundamentals", "final_trade_decision": '{"rating":"HOLD"}'},
            tool_events=[{"method": "get_fundamentals", "vendor": "yfinance", "status": "success", "fallback": False}],
        )
        self.assertIn("summary", outputs)
        self.assertIn("source_quality", outputs)
        self.assertIn("evidence_ledger", outputs)
        self.assertIn("earnings_event_pack", outputs)
        self.assertIn("thesis_tracker", outputs)

    def test_scheduled_run_writes_public_equity_intelligence_artifacts(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            archive_dir = root / "archive"
            site_dir = root / "site"
            config_path = root / "scheduled.toml"
            config_path.write_text(
                f"""
[run]
tickers = ["AAPL"]
continue_on_ticker_error = true
report_polisher_enabled = false

[llm]
provider = "codex"
quick_model = "gpt-5.5"
deep_model = "gpt-5.5"
output_model = "gpt-5.5"

[storage]
archive_dir = "{archive_dir.as_posix()}"
site_dir = "{site_dir.as_posix()}"

[portfolio]
enabled = false

[portfolio_performance]
enabled = false
""",
                encoding="utf-8",
            )
            config = load_scheduled_config(config_path)
            with (
                patch("tradingagents.scheduled.runner.TradingAgentsGraph", _FakeGraph),
                patch("tradingagents.scheduled.runner.StatsCallbackHandler", _FakeStatsHandler),
                patch("tradingagents.scheduled.runner.resolve_trade_date", return_value="2026-06-08"),
            ):
                manifest = execute_scheduled_run(config, run_label="institutional-test")

            ticker_summary = manifest["tickers"][0]
            artifacts = ticker_summary["artifacts"]
            self.assertIn("public_equity_intelligence_json", artifacts)
            self.assertIn("source_quality_json", artifacts)
            self.assertIn("evidence_ledger_json", artifacts)
            self.assertIn("earnings_event_pack_json", artifacts)
            self.assertIn("thesis_tracker_json", artifacts)
            run_dir = archive_dir / "runs" / manifest["started_at"][:4] / manifest["run_id"]
            self.assertTrue((run_dir / artifacts["public_equity_intelligence_json"]).exists())
            ticker_page = site_dir / "runs" / manifest["run_id"] / "AAPL.html"
            self.assertIn("원천/증거 상태", ticker_page.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
