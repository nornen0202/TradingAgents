import json

from tradingagents.agents.utils.decision_retry import invoke_structured_decision_with_retry


def _valid_decision() -> str:
    return json.dumps(
        {
            "rating": "HOLD",
            "portfolio_stance": "NEUTRAL",
            "entry_action": "WAIT",
            "setup_quality": "DEVELOPING",
            "confidence": 0.6,
            "time_horizon": "medium",
            "entry_logic": "Wait for confirmation above resistance.",
            "exit_logic": "Exit if support fails.",
            "position_sizing": "Keep size modest until confirmation.",
            "risk_limits": "Use defined support as invalidation.",
            "catalysts": ["Earnings follow-through"],
            "invalidators": ["Support break"],
            "watchlist_triggers": ["Breakout on volume"],
            "data_coverage": {
                "company_news_count": 0,
                "disclosures_count": 0,
                "social_source": "unavailable",
                "macro_items_count": 0,
            },
        }
    )


class _Response:
    def __init__(self, content: str):
        self.content = content


class _RepairingLLM:
    def __init__(self):
        self.calls = []
        self.responses = [
            _Response('{"rating":"HOLD"}'),
            _Response(_valid_decision()),
        ]

    def invoke(self, prompt):
        self.calls.append(prompt)
        return self.responses.pop(0)


def test_structured_decision_retry_repairs_missing_required_fields_for_message_prompts():
    llm = _RepairingLLM()

    response, decision_json = invoke_structured_decision_with_retry(
        llm,
        [{"role": "system", "content": "Return a decision."}],
        context="trader execution plan",
    )

    parsed = json.loads(decision_json)
    assert response.content == _valid_decision()
    assert parsed["rating"] == "HOLD"
    assert len(llm.calls) == 2
    assert llm.calls[1][-2]["role"] == "assistant"
    assert llm.calls[1][-2]["content"] == '{"rating":"HOLD"}'
    assert "missing required fields" in llm.calls[1][-1]["content"].lower()
    assert "return only json" in llm.calls[1][-1]["content"].lower()


def test_structured_decision_retry_allows_two_repairs_by_default():
    llm = _RepairingLLM()
    llm.responses = [
        _Response('{"rating":"HOLD"}'),
        _Response('{"rating":"HOLD","confidence":0.5}'),
        _Response(_valid_decision()),
    ]

    _response, decision_json = invoke_structured_decision_with_retry(
        llm,
        [{"role": "system", "content": "Return a decision."}],
        context="trader execution plan",
    )

    parsed = json.loads(decision_json)
    assert parsed["rating"] == "HOLD"
    assert len(llm.calls) == 3
    assert '"portfolio_stance"' in llm.calls[1][-1]["content"]
    assert '"entry_logic"' in llm.calls[2][-1]["content"]


def test_structured_decision_retry_allows_three_repairs_by_default():
    llm = _RepairingLLM()
    llm.responses = [
        _Response('{"rating":"HOLD"}'),
        _Response('{"rating":"HOLD","confidence":0.5}'),
        _Response('{"rating":"HOLD","confidence":0.5,"time_horizon":"medium"}'),
        _Response(_valid_decision()),
    ]

    _response, decision_json = invoke_structured_decision_with_retry(
        llm,
        [{"role": "system", "content": "Return a decision."}],
        context="portfolio manager final decision",
    )

    parsed = json.loads(decision_json)
    assert parsed["rating"] == "HOLD"
    assert len(llm.calls) == 4


def test_structured_decision_retry_returns_safe_fallback_for_codex_provider_marker():
    class FallbackLLM:
        def invoke(self, prompt):
            return _Response(
                "TRADINGAGENTS_CODEX_FALLBACK_RESPONSE\n"
                "Codex app-server did not return a response before timeout."
            )

    _response, decision_json = invoke_structured_decision_with_retry(
        FallbackLLM(),
        [{"role": "system", "content": "Return a decision."}],
        context="portfolio manager final decision",
    )

    parsed = json.loads(decision_json)
    assert parsed["rating"] == "NO_TRADE"
    assert parsed["entry_action"] == "WAIT"
    assert "CODEX_PROVIDER_UNAVAILABLE" in parsed["risk_action_reason_codes"]


def test_structured_decision_retry_returns_safe_fallback_after_exhausted_repairs():
    class InvalidLLM:
        def __init__(self):
            self.calls = 0

        def invoke(self, prompt):
            self.calls += 1
            return _Response('{"rating":"HOLD"}')

    llm = InvalidLLM()
    _response, decision_json = invoke_structured_decision_with_retry(
        llm,
        [{"role": "system", "content": "Return a decision."}],
        context="research manager investment plan",
        max_retries=1,
    )

    parsed = json.loads(decision_json)
    assert parsed["rating"] == "NO_TRADE"
    assert llm.calls == 2
