from unittest.mock import Mock

import pytest

from tradingagents.llm_clients import openai_client


@pytest.mark.parametrize("provider,endpoint,key_env,key", [
    ("ollama", "http://localhost:11434/v1", None, "ollama"),
    ("openrouter", "https://openrouter.ai/api/v1", "OPENROUTER_API_KEY", "router-test"),
    ("xai", "https://api.x.ai/v1", "XAI_API_KEY", "xai-test"),
])
def test_custom_endpoint_overrides_provider_default_without_changing_auth(monkeypatch, provider, endpoint, key_env, key):
    if key_env:
        monkeypatch.setenv(key_env, key)
    constructor = Mock()
    monkeypatch.setattr(openai_client, "NormalizedChatOpenAI", constructor)
    monkeypatch.setattr(openai_client.OpenAIClient, "warn_if_unknown_model", lambda _: None)
    openai_client.OpenAIClient(model="test-model", provider=provider).get_llm()
    assert constructor.call_args.kwargs["base_url"] == endpoint
    assert constructor.call_args.kwargs["api_key"] == key
    openai_client.OpenAIClient(model="test-model", provider=provider, base_url="https://private-proxy.example/v1").get_llm()
    assert constructor.call_args.kwargs["base_url"] == "https://private-proxy.example/v1"
    assert constructor.call_args.kwargs["api_key"] == key
