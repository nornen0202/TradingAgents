from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from tradingagents.youtube.config import load_youtube_config
from tradingagents.youtube.verifier import (
    YouTubeLLMClients,
    _close_role_llms,
    _create_role_llms,
)


def test_youtube_config_routes_stages_across_gpt_5_6_family():
    settings = load_youtube_config("config/youtube_daily.toml").llm

    assert settings.quick_model == "gpt-5.6-terra"
    assert settings.deep_model == "gpt-5.6-sol"
    assert settings.output_model == "gpt-5.6-luna"
    assert settings.codex_quick_reasoning_effort == "low"
    assert settings.codex_deep_reasoning_effort == "medium"
    assert settings.codex_output_reasoning_effort == "low"


def test_youtube_config_accepts_workflow_resolved_role_models(monkeypatch):
    monkeypatch.setenv("TRADINGAGENTS_YOUTUBE_QUICK_MODEL", "gpt-5.4-mini")
    monkeypatch.setenv("TRADINGAGENTS_YOUTUBE_DEEP_MODEL", "gpt-5.5")
    monkeypatch.setenv("TRADINGAGENTS_YOUTUBE_OUTPUT_MODEL", "gpt-5.4-mini")

    settings = load_youtube_config("config/youtube_daily.toml").llm

    assert settings.quick_model == "gpt-5.4-mini"
    assert settings.deep_model == "gpt-5.5"
    assert settings.output_model == "gpt-5.4-mini"


def test_youtube_role_clients_receive_stage_model_effort_and_telemetry_role():
    settings = load_youtube_config("config/youtube_daily.toml").llm
    calls = []

    def fake_create_llm_client(*, provider, model, **kwargs):
        calls.append((provider, model, kwargs))
        return SimpleNamespace(get_llm=lambda: object())

    with patch(
        "tradingagents.youtube.verifier.create_llm_client",
        side_effect=fake_create_llm_client,
    ):
        clients = _create_role_llms(settings)

    assert clients.quick is not None
    assert clients.judge is not None
    assert clients.writer is not None
    assert [
        (model, kwargs["codex_reasoning_effort"], kwargs["model_role"])
        for _, model, kwargs in calls
    ] == [
        ("gpt-5.6-terra", "low", "quick"),
        ("gpt-5.6-sol", "medium", "judge"),
        ("gpt-5.6-luna", "low", "writer"),
    ]


def test_youtube_role_clients_are_closed_once_after_each_video():
    class Closable:
        def __init__(self):
            self.close_calls = 0

        def close(self):
            self.close_calls += 1

    quick = Closable()
    judge = Closable()
    shared_writer = judge

    _close_role_llms(YouTubeLLMClients(quick=quick, judge=judge, writer=shared_writer))

    assert quick.close_calls == 1
    assert judge.close_calls == 1


def test_youtube_workflow_preflights_and_exports_every_role_model():
    workflow = Path(".github/workflows/daily-youtube-reports.yml").read_text(
        encoding="utf-8"
    )

    assert 'TRADINGAGENTS_CODEX_ALLOW_MODEL_FALLBACK: "0"' in workflow
    assert 'TRADINGAGENTS_CODEX_PREFLIGHT_ALLOW_MODEL_FALLBACK: "1"' in workflow
    assert 'model="gpt-5.6-sol"' in workflow
    assert 'model="gpt-5.6-terra"' in workflow
    assert 'model="gpt-5.6-luna"' in workflow
    assert 'codex_preflight_fallback_models("judge")' in workflow
    assert 'codex_preflight_fallback_models("quick")' in workflow
    assert 'codex_preflight_fallback_models("writer")' in workflow
    assert "TRADINGAGENTS_CODEX_PREFLIGHT_OK=1" in workflow
    assert "TRADINGAGENTS_YOUTUBE_DEEP_MODEL=" in workflow
    assert "TRADINGAGENTS_YOUTUBE_QUICK_MODEL=" in workflow
    assert "TRADINGAGENTS_YOUTUBE_OUTPUT_MODEL=" in workflow
