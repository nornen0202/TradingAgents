import json
import tempfile
import unittest
from pathlib import Path

from tradingagents.scheduled.config import SiteSettings
from tradingagents.scheduled.site import build_site


class InvestorModeUiTests(unittest.TestCase):
    def test_default_ticker_page_hides_engineering_labels(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            archive_dir = root / "archive"
            site_dir = root / "site"
            run_dir = archive_dir / "runs" / "2026" / "20260416T091653_github-actions-kr"
            report_dir = run_dir / "tickers" / "005930.KS" / "report"
            report_dir.mkdir(parents=True)
            (report_dir / "complete_report.md").write_text("# 삼성전자\n투자자용 리포트", encoding="utf-8")
            ticker_dir = run_dir / "tickers" / "005930.KS"
            (ticker_dir / "analysis.json").write_text("{}", encoding="utf-8")
            (ticker_dir / "final_state.json").write_text("{}", encoding="utf-8")
            (run_dir / "run.json").write_text(
                json.dumps(
                    {
                        "version": 1,
                        "run_id": "20260416T091653_github-actions-kr",
                        "label": "github-actions-kr",
                        "status": "success",
                        "started_at": "2026-04-16T09:16:53+09:00",
                        "finished_at": "2026-04-16T09:30:00+09:00",
                        "timezone": "Asia/Seoul",
                        "settings": {"output_language": "Korean"},
                        "summary": {"total_tickers": 1, "successful_tickers": 1, "failed_tickers": 0},
                        "batch_metrics": {},
                        "warnings": [],
                        "portfolio": {"status": "disabled"},
                        "tickers": [
                            {
                                "ticker": "005930.KS",
                                "ticker_name": "삼성전자",
                                "status": "success",
                                "analysis_date": "2026-04-16",
                                "trade_date": "2026-04-15",
                                "decision": "HOLD",
                                "finished_at": "2026-04-16T09:30:00+09:00",
                                "duration_seconds": 1.0,
                                "metrics": {"llm_calls": 1, "tool_calls": 1, "tokens_in": 10, "tokens_out": 20},
                                "quality_flags": ["stale_market_data"],
                                "artifacts": {
                                    "analysis_json": "tickers/005930.KS/analysis.json",
                                    "report_markdown": "tickers/005930.KS/report/complete_report.md",
                                    "final_state_json": "tickers/005930.KS/final_state.json",
                                },
                            }
                        ],
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )

            build_site(archive_dir, site_dir, SiteSettings(title="KR", subtitle="Daily"))
            html = (site_dir / "runs" / "20260416T091653_github-actions-kr" / "005930.KS.html").read_text(
                encoding="utf-8"
            )

        hidden_labels = [
            "Decision source",
            "Analysis review",
            "Portfolio review",
            "Historical view",
            "Published At",
            "Data health",
            "Source status",
            "LLM calls",
            "Tool calls",
            "Token usage",
            "Vendor calls",
            "Fallback count",
            "Quality flags",
        ]
        for label in hidden_labels:
            self.assertNotIn(label, html)
        self.assertIn("오늘 할 일", html)
        self.assertIn("종가 확인 시 할 일", html)
        self.assertIn("고급 진단", html)

    def test_investor_mode_hides_engineering_fields_by_default(self):
        self.test_default_ticker_page_hides_engineering_labels()

    def test_investor_mode_hides_advanced_diagnostics_by_default(self):
        self.test_default_ticker_page_hides_engineering_labels()


if __name__ == "__main__":
    unittest.main()
