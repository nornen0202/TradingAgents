import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tradingagents.agents.utils.agent_utils import rewrite_in_output_language
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.reporting import save_report_bundle
from tradingagents.translation import _prepare_transformers_runtime, should_skip_translation


class ReportLocalizationTests(unittest.TestCase):
    def test_save_report_bundle_formats_structured_decision_without_raw_json_details(self):
        structured_decision = """
<details>
<summary>원본 구조화 JSON 보기</summary>
{"rating":"NO_TRADE","portfolio_stance":"BULLISH","entry_action":"WAIT","setup_quality":"DEVELOPING","confidence":0.66,"time_horizon":"medium","entry_logic":"breakout after confirmation","exit_logic":"support break","position_sizing":"starter","risk_limits":"1R","catalysts":["earnings revision"],"invalidators":["support break"],"watchlist_triggers":["breakout confirmation"],"data_coverage":{"company_news_count":5,"disclosures_count":1,"social_source":"dedicated","macro_items_count":3}}
</details>
        """.strip()
        final_state = {
            "analysis_date": "2026-04-06",
            "trade_date": "2026-04-02",
            "market_report": "시장 보고서 본문",
            "sentiment_report": "소셜 보고서 본문",
            "news_report": "뉴스 보고서 본문",
            "fundamentals_report": "펀더멘털 보고서 본문",
            "investment_debate_state": {
                "bull_history": "강세 의견",
                "bear_history": "약세 의견",
                "judge_decision": structured_decision,
            },
            "trader_investment_plan": "트레이딩 계획",
            "risk_debate_state": {
                "aggressive_history": "공격형 의견",
                "conservative_history": "보수형 의견",
                "neutral_history": "중립 의견",
                "judge_decision": structured_decision,
            },
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            report_path = save_report_bundle(
                final_state,
                "GOOGL",
                Path(tmpdir),
                language="Korean",
            )
            report_text = report_path.read_text(encoding="utf-8")

        self.assertNotIn("원본 구조화 JSON 보기", report_text)
        self.assertIn("포트폴리오 stance", report_text)
        self.assertIn("엔트리 액션", report_text)
        self.assertIn("Decision scope", report_text)
        self.assertIn("breakout after confirmation", report_text)

    def test_save_report_bundle_uses_korean_labels(self):
        final_state = {
            "analysis_date": "2026-04-06",
            "trade_date": "2026-04-02",
            "market_report": "시장 보고서 본문",
            "sentiment_report": "소셜 보고서 본문",
            "news_report": "뉴스 보고서 본문",
            "fundamentals_report": "펀더멘털 보고서 본문",
            "investment_debate_state": {
                "bull_history": "강세 의견",
                "bear_history": "약세 의견",
                "judge_decision": "리서치 매니저 판단",
            },
            "trader_investment_plan": "트레이딩 계획",
            "risk_debate_state": {
                "aggressive_history": "공격형 의견",
                "conservative_history": "보수형 의견",
                "neutral_history": "중립 의견",
                "judge_decision": "포트폴리오 최종 판단",
            },
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            report_path = save_report_bundle(
                final_state,
                "GOOGL",
                Path(tmpdir),
                language="Korean",
            )
            report_text = report_path.read_text(encoding="utf-8")

        self.assertIn("트레이딩 분석 리포트", report_text)
        self.assertIn("생성 시각", report_text)
        self.assertIn("분석 기준일: 2026-04-06", report_text)
        self.assertIn("시장 데이터 기준일: 2026-04-02", report_text)
        self.assertIn("I. 애널리스트 팀 리포트", report_text)
        self.assertIn("V. 포트폴리오 매니저 최종 판단", report_text)
        self.assertIn("시장 애널리스트", report_text)

    def test_save_report_bundle_preserves_buy_rating_in_public_report(self):
        structured_decision = (
            '{"rating":"BUY","portfolio_stance":"BULLISH","entry_action":"STARTER",'
            '"setup_quality":"COMPELLING","confidence":0.82,"time_horizon":"short",'
            '"entry_logic":"confirmed breakout","exit_logic":"lose breakout level",'
            '"position_sizing":"starter","risk_limits":"1R","catalysts":["earnings beat"],'
            '"invalidators":["failed breakout"],"watchlist_triggers":["volume expansion"],'
            '"data_coverage":{"company_news_count":4,"disclosures_count":1,'
            '"social_source":"dedicated","macro_items_count":2}}'
        )
        final_state = {
            "analysis_date": "2026-04-06",
            "trade_date": "2026-04-02",
            "market_report": "시장 보고서 본문",
            "sentiment_report": "소셜 보고서 본문",
            "news_report": "뉴스 보고서 본문",
            "fundamentals_report": "펀더멘털 보고서 본문",
            "investment_debate_state": {
                "bull_history": "강세 의견",
                "bear_history": "약세 의견",
                "judge_decision": structured_decision,
            },
            "trader_investment_plan": "트레이딩 계획",
            "risk_debate_state": {
                "aggressive_history": "공격형 의견",
                "conservative_history": "보수형 의견",
                "neutral_history": "중립 의견",
                "judge_decision": structured_decision,
            },
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            report_path = save_report_bundle(
                final_state,
                "GOOGL",
                Path(tmpdir),
                language="English",
            )
            report_text = report_path.read_text(encoding="utf-8")

        self.assertIn("Legacy rating: `BUY`", report_text)
        self.assertIn("Decision scope", report_text)

    def test_localize_final_state_rewrites_only_report_fields(self):
        graph = TradingAgentsGraph.__new__(TradingAgentsGraph)
        graph.quick_thinking_llm = object()
        final_state = {
            "market_report": "market",
            "sentiment_report": "social",
            "news_report": "news",
            "fundamentals_report": "fundamentals",
            "investment_plan": "investment plan",
            "trader_investment_plan": "trader plan",
            "final_trade_decision": "final decision",
            "investment_debate_state": {
                "bull_history": "bull",
                "bear_history": "bear",
                "history": "debate history",
                "current_response": "latest debate",
                "judge_decision": "manager decision",
            },
            "risk_debate_state": {
                "aggressive_history": "aggressive",
                "conservative_history": "conservative",
                "neutral_history": "neutral",
                "history": "risk history",
                "current_aggressive_response": "aggr latest",
                "current_conservative_response": "cons latest",
                "current_neutral_response": "neutral latest",
                "judge_decision": "portfolio decision",
            },
        }

        with (
            patch("tradingagents.graph.trading_graph.get_output_language", return_value="Korean"),
            patch(
                "tradingagents.graph.trading_graph.rewrite_in_output_language",
                side_effect=lambda llm, content, content_type="report": f"KO::{content_type}::{content}",
            ),
        ):
            localized = graph._localize_final_state(final_state)

        self.assertEqual(localized["market_report"], "KO::market analyst report::market")
        self.assertEqual(localized["trader_investment_plan"], "KO::trader plan::trader plan")
        self.assertEqual(localized["investment_plan"], "investment plan")
        self.assertEqual(localized["final_trade_decision"], "final decision")
        self.assertEqual(
            localized["investment_debate_state"]["judge_decision"],
            "KO::research manager decision::manager decision",
        )
        self.assertEqual(localized["investment_debate_state"]["history"], "debate history")
        self.assertEqual(localized["risk_debate_state"]["current_neutral_response"], "neutral latest")

    def test_localize_final_state_rejects_unexpected_script_noise(self):
        graph = TradingAgentsGraph.__new__(TradingAgentsGraph)
        graph.quick_thinking_llm = object()
        final_state = {
            "market_report": "market",
            "sentiment_report": "social",
            "news_report": "news",
            "fundamentals_report": "fundamentals",
            "investment_plan": "investment plan",
            "trader_investment_plan": "trader plan",
            "final_trade_decision": "final decision",
            "investment_debate_state": {
                "bull_history": "bull",
                "bear_history": "bear",
                "history": "debate history",
                "current_response": "latest debate",
                "judge_decision": "manager decision",
            },
            "risk_debate_state": {
                "aggressive_history": "aggressive",
                "conservative_history": "conservative",
                "neutral_history": "neutral",
                "history": "risk history",
                "current_aggressive_response": "aggr latest",
                "current_conservative_response": "cons latest",
                "current_neutral_response": "neutral latest",
                "judge_decision": "portfolio decision",
            },
        }

        with (
            patch("tradingagents.graph.trading_graph.get_output_language", return_value="Korean"),
            patch(
                "tradingagents.graph.trading_graph.rewrite_in_output_language",
                side_effect=lambda llm, content, content_type="report": f"KRW فوق::{content}",
            ),
        ):
            localized = graph._localize_final_state(final_state)

        self.assertEqual(localized["market_report"], "market")
        self.assertEqual(localized["risk_debate_state"]["judge_decision"], "portfolio decision")

    def test_skip_translation_for_already_korean_text(self):
        self.assertTrue(should_skip_translation("시장 보고서 본문입니다.\n매수 의견 유지.", "Korean"))
        self.assertFalse(should_skip_translation("## Market\nKeep buy rating.", "Korean"))

        with (
            patch("tradingagents.agents.utils.agent_utils.get_output_language", return_value="Korean"),
            patch("tradingagents.agents.utils.agent_utils.translate_with_backend") as translate_mock,
        ):
            localized = rewrite_in_output_language(object(), "시장 보고서 본문입니다.\n매수 의견 유지.")

        self.assertEqual(localized, "시장 보고서 본문입니다.\n매수 의견 유지.")
        translate_mock.assert_not_called()


    def test_prepare_transformers_runtime_suppresses_advisory_warning(self):
        with patch.dict("os.environ", {}, clear=True):
            _prepare_transformers_runtime()
            self.assertEqual(os.environ.get("TRANSFORMERS_NO_ADVISORY_WARNINGS"), "1")

    def test_llm_rewrite_prompt_warns_against_holiday_inference(self):
        class _FakeLlm:
            def __init__(self):
                self.messages = None

            def invoke(self, messages):
                self.messages = messages
                return type("Reply", (), {"content": "재작성 결과"})()

        llm = _FakeLlm()
        with (
            patch("tradingagents.agents.utils.agent_utils.get_output_language", return_value="Korean"),
            patch(
                "tradingagents.agents.utils.agent_utils.get_translation_settings",
                return_value=type("Settings", (), {"backend": "llm", "allow_llm_fallback": True})(),
            ),
        ):
            localized = rewrite_in_output_language(llm, "Market report body.")

        self.assertEqual(localized, "재작성 결과")
        self.assertIn("Do not infer that a date is a market holiday", llm.messages[0][1])


if __name__ == "__main__":
    unittest.main()
