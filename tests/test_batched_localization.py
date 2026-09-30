from __future__ import annotations

import json
from types import SimpleNamespace

import pytest

from tradingagents.agents.utils import agent_utils
from tradingagents.graph import trading_graph
from tradingagents.schemas import parse_structured_decision


@pytest.fixture(autouse=True)
def korean_llm_backend(monkeypatch):
    monkeypatch.setattr(agent_utils, "get_output_language", lambda: "Korean")
    monkeypatch.setattr(trading_graph, "get_output_language", lambda: "Korean")
    monkeypatch.setattr(agent_utils, "get_translation_settings",
                        lambda: SimpleNamespace(backend="llm", allow_llm_fallback=True))


class Translator:
    def __init__(self):
        self.calls = []

    def invoke(self, messages):
        self.calls.append(messages)
        fields = json.loads(messages[-1][1])
        return SimpleNamespace(content=json.dumps({key: "확인할 조건: " + value for key, value in fields.items()}))


def test_many_fields_use_one_call_and_preserve_each_numeric_contract():
    llm = Translator()
    fields = {f"condition.{index}": f"Confirm a close >= {100 + index}.50 with volume 1.2x." for index in range(30)}
    result = agent_utils.rewrite_fields_in_output_language(llm, fields)
    assert len(llm.calls) == 1
    assert set(result) == set(fields)
    for key, original in fields.items():
        assert result[key] == "확인할 조건: " + original


def test_already_korean_fields_do_not_call_model():
    llm = Translator()
    fields = {"entry": "거래량 증가와 함께 100원 위 종가를 확인한다."}
    assert agent_utils.rewrite_fields_in_output_language(llm, fields) == fields
    assert not llm.calls


def test_unavailable_local_backend_uses_one_batched_fallback(monkeypatch):
    monkeypatch.setattr(agent_utils, "get_translation_settings",
                        lambda: SimpleNamespace(backend="nllb_ct2", allow_llm_fallback=True))
    probes = []
    def unavailable(*args):
        probes.append(args)
        raise agent_utils.TranslationBackendError("model unavailable")
    monkeypatch.setattr(agent_utils, "translate_with_backend", unavailable)
    llm = Translator()
    fields = {f"condition.{i}": f"Confirm above {100 + i}." for i in range(30)}
    result = agent_utils.rewrite_fields_in_output_language(llm, fields)
    assert len(probes) == 1
    assert len(llm.calls) == 1
    assert set(result) == set(fields)


def test_disabled_fallback_never_calls_model(monkeypatch):
    monkeypatch.setattr(agent_utils, "get_translation_settings",
                        lambda: SimpleNamespace(backend="nllb_ct2", allow_llm_fallback=False))
    monkeypatch.setattr(agent_utils, "translate_with_backend", lambda *args: "잘못된 가격 101")
    llm = Translator()
    fields = {"entry": "Price 100."}
    assert agent_utils.rewrite_fields_in_output_language(llm, fields) == fields
    assert not llm.calls


@pytest.mark.parametrize("bad", ["Confirm >= 101.", "Confirm <= 100.", "", None])
def test_bad_price_direction_or_type_is_rejected_even_after_fallback(bad, caplog):
    class InvalidTranslator:
        calls = 0
        def invoke(self, messages):
            self.calls += 1
            return SimpleNamespace(content=json.dumps({"entry": bad}) if self.calls == 1 else bad)
    llm = InvalidTranslator()
    original = {"entry": "Confirm >= 100."}
    assert agent_utils.rewrite_fields_in_output_language(llm, original) == original
    assert llm.calls == 2
    if bad not in (None, ""):
        assert "Rejected invalid financial translation" in caplog.text


def test_malformed_batch_falls_back_without_cross_assigning_fields():
    class MalformedTranslator:
        calls = 0
        def invoke(self, messages):
            self.calls += 1
            content = '{"other":"wrong"}' if self.calls == 1 else "재확인 조건: " + messages[-1][1]
            return SimpleNamespace(content=content)
    llm = MalformedTranslator()
    fields = {"entry": "Confirm above 100.", "exit": "Reduce below 90."}
    result = agent_utils.rewrite_fields_in_output_language(llm, fields)
    assert llm.calls == 3
    assert result == {key: "재확인 조건: " + value for key, value in fields.items()}


def test_graph_excludes_machine_fields_from_translation_and_preserves_lists():
    decision = {
        "rating": "HOLD", "portfolio_stance": "BULLISH", "entry_action": "WAIT",
        "conditional_entry_action": "STARTER", "conditional_entry_valid_until": "2026-10-02T16:00:00-04:00",
        "execution_levels": {"levels": [{"level_type": "BREAKOUT", "price": 100, "confirmation": "close"}]},
        "setup_quality": "DEVELOPING", "confidence": .62, "time_horizon": "medium",
        "entry_logic": "Confirm above 100.", "exit_logic": "Reduce below 90.",
        "position_sizing": "Limit risk to 0.5%.", "risk_limits": "Do not chase above 110.",
        "catalysts": ["Earnings growth of 20%.", "Official filing confirmation."],
        "invalidators": ["Close below 90."], "watchlist_triggers": ["Volume exceeds 1.2x."],
        "data_coverage": {"company_news_count": 3, "disclosures_count": 0,
                          "social_source": "news_derived", "macro_items_count": 1},
    }
    raw = json.dumps(decision)
    llm = Translator()
    graph = trading_graph.TradingAgentsGraph.__new__(trading_graph.TradingAgentsGraph)
    graph.output_thinking_llm = llm
    localized = graph._localize_final_state({"trader_investment_plan": raw, "final_trade_decision": raw})
    before = parse_structured_decision(raw).to_dict()
    after = json.loads(localized["trader_investment_plan"])
    narratives = {"entry_logic", "exit_logic", "position_sizing", "risk_limits",
                  "catalysts", "invalidators", "watchlist_triggers"}
    assert {k: v for k, v in before.items() if k not in narratives} == {
        k: v for k, v in after.items() if k not in narratives
    }
    assert len(llm.calls) == 1
    assert "rating" not in json.loads(llm.calls[0][-1][1])
    assert after["catalysts"] == ["확인할 조건: " + item for item in before["catalysts"]]
    assert localized["final_trade_decision"] == raw


def test_localization_numeric_validation_handles_korean_spacing():
    assert agent_utils._valid_field_translation("Growth 16.4%, profit 26.6%.", "성장률16.4%, 영업이익26.6%.")
    assert agent_utils._valid_field_translation("Price $2,203.95.", "가격 2203.95달러.")
    assert not agent_utils._valid_field_translation("Loss -0.5%.", "손실 0.5%.")
    assert agent_utils._valid_field_translation("September 29 close, October 2 expiry.", "9월 29일 종가, 10월 2일 만료.")
    assert agent_utils._valid_field_translation("Price on 2026-09-29.", "2026년 9월 29일 가격.")
    assert not agent_utils._valid_field_translation("September 29 close.", "9월 30일 종가.")
