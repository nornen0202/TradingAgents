from types import SimpleNamespace
from unittest.mock import patch

from tradingagents.llm_clients.codex_chat_model import CodexChatModel
from tradingagents.llm_clients.role_config import codex_client_kwargs
from tradingagents.portfolio.action_judge import _create_action_llm
from tradingagents.portfolio.semantic_judge import _create_semantic_llm


def _settings() -> SimpleNamespace:
    return SimpleNamespace(
        provider="codex",
        quick_model="gpt-5.6-terra",
        deep_model="gpt-5.6-sol",
        output_model="gpt-5.6-luna",
        writer_model="gpt-5.6-luna",
        judge_model="gpt-5.6-sol",
        codex_reasoning_effort="medium",
        codex_quick_reasoning_effort="low",
        codex_deep_reasoning_effort="medium",
        codex_output_reasoning_effort="low",
        codex_writer_reasoning_effort="low",
        codex_judge_reasoning_effort="medium",
        codex_execution_summary_reasoning_effort="low",
        codex_summary="none",
        codex_personality="none",
        codex_workspace_dir=None,
        codex_binary=None,
        codex_request_timeout=30.0,
        codex_max_retries=1,
        codex_cleanup_threads=True,
        codex_preflight_mode="per_client",
        codex_fallback_on_app_server_error=False,
    )


def test_codex_client_kwargs_select_role_effort_and_tag():
    kwargs = codex_client_kwargs(_settings(), role="writer")

    assert kwargs["codex_reasoning_effort"] == "low"
    assert kwargs["model_role"] == "writer"


def test_action_judge_uses_sol_with_judge_effort():
    with patch(
        "tradingagents.portfolio.action_judge.create_llm_client"
    ) as create_client:
        create_client.return_value.get_llm.return_value = object()

        _create_action_llm(_settings())

    assert create_client.call_args.kwargs["model"] == "gpt-5.6-sol"
    assert create_client.call_args.kwargs["codex_reasoning_effort"] == "medium"
    assert create_client.call_args.kwargs["model_role"] == "judge"


def test_semantic_judge_uses_sol_with_judge_effort():
    with patch(
        "tradingagents.portfolio.semantic_judge.create_llm_client"
    ) as create_client:
        create_client.return_value.get_llm.return_value = object()

        _create_semantic_llm(_settings())

    assert create_client.call_args.kwargs["model"] == "gpt-5.6-sol"
    assert create_client.call_args.kwargs["codex_reasoning_effort"] == "medium"
    assert create_client.call_args.kwargs["model_role"] == "judge"


def test_codex_fallback_order_preserves_role_cost_class(monkeypatch):
    captured: dict[str, tuple[str, ...]] = {}

    def preflight_runner(**kwargs):
        captured[kwargs["model"]] = tuple(kwargs["fallback_models"])
        return SimpleNamespace(resolved_model=kwargs["model"])

    monkeypatch.setenv("TRADINGAGENTS_CODEX_ALLOW_MODEL_FALLBACK", "1")
    for role, model in (("deep", "gpt-5.6-sol"), ("writer", "gpt-5.6-luna")):
        llm = CodexChatModel(
            model=model,
            model_role=role,
            codex_binary="C:/fake/codex.exe",
            codex_workspace_dir="C:/tmp/codex-workspace",
            preflight_runner=preflight_runner,
        )
        llm.preflight()

    assert captured["gpt-5.6-sol"][0] == "gpt-5.5"
    assert captured["gpt-5.6-luna"][0] == "gpt-5.4-mini"
