from unittest.mock import patch

from tradingagents.llm_clients.google_client import GoogleClient


def test_gemini_requests_have_a_default_deadline():
    with patch("tradingagents.llm_clients.google_client.NormalizedChatGoogleGenerativeAI") as model:
        GoogleClient("gemini-2.5-flash").get_llm()
    assert model.call_args.kwargs["timeout"] == 600.0


def test_gemini_request_deadline_can_be_overridden():
    with patch("tradingagents.llm_clients.google_client.NormalizedChatGoogleGenerativeAI") as model:
        GoogleClient("gemini-2.5-flash", timeout=45.0).get_llm()
    assert model.call_args.kwargs["timeout"] == 45.0
