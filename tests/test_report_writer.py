import json
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from tradingagents.portfolio.account_models import AccountSnapshot, PortfolioAction, PortfolioRecommendation
from tradingagents.report_writer import polish_portfolio_report_markdown, polish_ticker_report


class _FakeLLM:
    def __init__(self, payload):
        self.payload = payload

    def invoke(self, prompt):
        self.prompt = prompt
        return SimpleNamespace(content=json.dumps(self.payload, ensure_ascii=False))


def _llm_settings():
    return SimpleNamespace(
        provider="codex",
        output_model="gpt-5.4",
        deep_model="gpt-5.4",
        quick_model="gpt-5.4",
        codex_reasoning_effort="medium",
        codex_summary="none",
        codex_personality="none",
        codex_request_timeout=30.0,
        codex_max_retries=1,
        codex_cleanup_threads=True,
        codex_workspace_dir=None,
        codex_binary=None,
    )


def _structured_decision():
    return json.dumps(
        {
            "rating": "NO_TRADE",
            "portfolio_stance": "BULLISH",
            "entry_action": "STARTER",
            "setup_quality": "DEVELOPING",
            "confidence": 0.68,
            "time_horizon": "medium",
            "entry_logic": "support confirmation near 182",
            "exit_logic": "close below the 200-day average",
            "position_sizing": "start with one third of target size",
            "risk_limits": "keep risk below 1R",
            "catalysts": ["MACD turned positive", "price above key averages"],
            "invalidators": ["200-day average breakdown"],
            "watchlist_triggers": ["support holds with volume"],
            "data_coverage": {
                "company_news_count": 5,
                "disclosures_count": 1,
                "social_source": "dedicated",
                "macro_items_count": 3,
            },
        },
        ensure_ascii=False,
    )


class ReportWriterTests(unittest.TestCase):
    def test_ticker_writer_adds_summary_without_mutating_decision(self):
        final_state = {
            "company_of_interest": "NVDA",
            "market_report": "NVDA price is above the 10/50/200-day averages.",
            "trader_investment_plan": "Start small after support confirmation.",
            "risk_debate_state": {"judge_decision": _structured_decision()},
            "final_trade_decision": _structured_decision(),
        }
        writer_payload = {
            "headline_action": "초기 진입 가능",
            "one_sentence_summary": "강세 논지는 유효하지만 확인형 진입이 적절합니다.",
            "why_now": ["주가가 주요 이동평균을 상회", "MACD가 양전환"],
            "how_to_execute": "목표 비중의 1/3만 먼저 진입합니다.",
            "add_if": "182 부근 지지 확인 후 추가합니다.",
            "cut_if": "200일선 하회 종가가 나오면 축소합니다.",
            "key_risks": ["지지선 이탈"],
            "watch_next": ["거래량 동반 돌파"],
            "confidence_text": "보통 이상",
            "data_caveat_text": "자료 상태 정상",
        }

        with patch("tradingagents.report_writer._create_writer_llm", return_value=_FakeLLM(writer_payload)):
            polished_state, metadata = polish_ticker_report(
                final_state,
                ticker="NVDA",
                language="Korean",
                llm_settings=_llm_settings(),
            )

        self.assertEqual(metadata["status"], "success")
        self.assertEqual(polished_state["final_trade_decision"], final_state["final_trade_decision"])
        self.assertIn("## 투자자 요약", polished_state["investor_summary_report"])
        self.assertIn("초기 진입 가능", polished_state["investor_summary_report"])
        self.assertNotIn("RULE_ONLY", polished_state["investor_summary_report"])

    def test_ticker_writer_falls_back_to_template_when_llm_unavailable(self):
        final_state = {"final_trade_decision": _structured_decision()}

        polished_state, metadata = polish_ticker_report(
            final_state,
            ticker="NVDA",
            language="Korean",
            llm_settings=None,
        )

        self.assertEqual(metadata["status"], "fallback")
        self.assertIn("## 투자자 요약", polished_state["investor_summary_report"])
        self.assertIn("소액/분할 진입 후보", polished_state["investor_summary_report"])

    def test_portfolio_writer_inserts_summary_after_title(self):
        snapshot = AccountSnapshot(
            snapshot_id="snapshot-1",
            as_of="2026-04-12T09:00:00+09:00",
            broker="watchlist",
            account_id="watchlist",
            currency="KRW",
            settled_cash_krw=0,
            available_cash_krw=0,
            buying_power_krw=0,
            total_equity_krw=0,
            snapshot_health="WATCHLIST_ONLY",
        )
        action = PortfolioAction(
            canonical_ticker="NVDA",
            display_name="NVIDIA",
            priority=1,
            confidence=0.68,
            action_now="WATCH",
            delta_krw_now=0,
            target_weight_now=0.0,
            action_if_triggered="STARTER_IF_TRIGGERED",
            delta_krw_if_triggered=500000,
            target_weight_if_triggered=0.1,
            trigger_conditions=("support confirmation",),
            rationale="강세 논지는 유효하지만 확인이 필요합니다.",
            data_health={},
        )
        recommendation = PortfolioRecommendation(
            snapshot_id="snapshot-1",
            report_date="2026-04-12",
            account_value_krw=0,
            recommended_cash_after_now_krw=0,
            recommended_cash_after_triggered_krw=0,
            market_regime="constructive_but_selective",
            actions=(action,),
            portfolio_risks=("실계좌 스냅샷 없음",),
            data_health_summary={},
        )
        writer_payload = {
            "headline_action": "워치리스트 모드",
            "one_sentence_summary": "즉시 주문 없이 NVDA 조건을 우선 관찰합니다.",
            "why_now": ["강세 논지는 유효"],
            "how_to_execute": "계좌 연결 전에는 주문하지 않습니다.",
            "add_if": "지지 확인 시 소액 진입을 검토합니다.",
            "cut_if": "조건이 깨지면 관찰에서 제외합니다.",
            "key_risks": ["실계좌 정보 없음"],
            "watch_next": ["NVDA 지지 확인"],
            "confidence_text": "보통",
            "data_caveat_text": "관심종목 기준입니다.",
        }

        with patch("tradingagents.report_writer._create_writer_llm", return_value=_FakeLLM(writer_payload)):
            markdown, metadata = polish_portfolio_report_markdown(
                "# TradingAgents 포트폴리오 워치리스트 리포트\n\n## 핵심 요약\n\n- 조건부 후보 1개",
                snapshot=snapshot,
                recommendation=recommendation,
                language="Korean",
                llm_settings=_llm_settings(),
            )

        self.assertEqual(metadata["status"], "success")
        self.assertLess(markdown.index("## 투자자 요약"), markdown.index("## 핵심 요약"))
        self.assertIn("워치리스트 모드", markdown)
        self.assertNotIn("RULE_ONLY", markdown)


if __name__ == "__main__":
    unittest.main()
