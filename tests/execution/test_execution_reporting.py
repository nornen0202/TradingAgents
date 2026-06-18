from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import patch

from tradingagents.execution.reporting import render_execution_update_markdown
from tradingagents.schemas import (
    ActionIfTriggered,
    BreakoutConfirmation,
    DecisionNow,
    DecisionState,
    ExecutionContract,
    ExecutionUpdate,
    LevelBasis,
    PrimarySetup,
    ThesisState,
)


def test_blank_execution_summary_model_uses_deterministic_text_without_llm():
    contract = ExecutionContract(
        ticker="AAPL",
        analysis_asof="2026-05-29T09:00:00-04:00",
        market_data_asof="2026-05-29",
        level_basis=LevelBasis.DAILY_CLOSE,
        thesis_state=ThesisState.CONSTRUCTIVE,
        primary_setup=PrimarySetup.BREAKOUT_CONFIRMATION,
        portfolio_stance="BULLISH",
        entry_action_base="WAIT",
        setup_quality="COMPELLING",
        confidence=0.8,
        action_if_triggered=ActionIfTriggered.STARTER,
        breakout_level=100.0,
        breakout_confirmation=BreakoutConfirmation.INTRADAY_ABOVE,
        min_relative_volume=1.0,
    )
    update = ExecutionUpdate(
        ticker="AAPL",
        analysis_asof="2026-05-29T09:00:00-04:00",
        execution_asof="2026-05-29T10:00:00-04:00",
        market_data_asof="2026-05-29T10:00:00-04:00",
        source={"provider": "fixture"},
        last_price=101.0,
        session_vwap=100.0,
        day_high=102.0,
        day_low=99.0,
        intraday_volume=1000,
        avg20_daily_volume=1000.0,
        relative_volume=1.2,
        price_state="above_breakout",
        volume_state="confirmed",
        event_state="none",
        decision_state=DecisionState.ACTIONABLE_NOW,
        decision_now=DecisionNow.STARTER_NOW,
        decision_if_triggered=ActionIfTriggered.STARTER,
        trigger_status={"breakout": True},
        changed_fields=(),
        reason_codes=("pilot_ready",),
        staleness_seconds=0,
        data_health="ok",
        refresh_checkpoint="10:00",
    )
    llm_settings = SimpleNamespace(provider="codex")

    with patch("tradingagents.execution.reporting.create_llm_client") as create_client:
        markdown = render_execution_update_markdown(
            contract,
            update,
            llm_settings=llm_settings,
            llm_model=None,
        )

    create_client.assert_not_called()
    assert "## Explanation" in markdown
    assert "State: `ACTIONABLE_NOW` / Now: `STARTER_NOW`." in markdown
    assert "Reasons: pilot_ready." in markdown


def test_codex_fallback_marker_uses_deterministic_execution_summary():
    contract = ExecutionContract(
        ticker="AAPL",
        analysis_asof="2026-05-29T09:00:00-04:00",
        market_data_asof="2026-05-29",
        level_basis=LevelBasis.DAILY_CLOSE,
        thesis_state=ThesisState.CONSTRUCTIVE,
        primary_setup=PrimarySetup.BREAKOUT_CONFIRMATION,
        portfolio_stance="BULLISH",
        entry_action_base="WAIT",
        setup_quality="COMPELLING",
        confidence=0.8,
        action_if_triggered=ActionIfTriggered.STARTER,
        breakout_level=100.0,
        breakout_confirmation=BreakoutConfirmation.INTRADAY_ABOVE,
        min_relative_volume=1.0,
    )
    update = ExecutionUpdate(
        ticker="AAPL",
        analysis_asof="2026-05-29T09:00:00-04:00",
        execution_asof="2026-05-29T10:00:00-04:00",
        market_data_asof="2026-05-29T10:00:00-04:00",
        source={"provider": "fixture"},
        last_price=101.0,
        session_vwap=100.0,
        day_high=102.0,
        day_low=99.0,
        intraday_volume=1000,
        avg20_daily_volume=1000.0,
        relative_volume=1.2,
        price_state="above_breakout",
        volume_state="confirmed",
        event_state="none",
        decision_state=DecisionState.ACTIONABLE_NOW,
        decision_now=DecisionNow.STARTER_NOW,
        decision_if_triggered=ActionIfTriggered.STARTER,
        trigger_status={"breakout": True},
        changed_fields=(),
        reason_codes=("pilot_ready",),
        staleness_seconds=0,
        data_health="ok",
        refresh_checkpoint="10:00",
    )
    llm_settings = SimpleNamespace(
        provider="codex",
        codex_fallback_on_app_server_error=True,
    )
    fallback_llm = SimpleNamespace(
        invoke=lambda _prompt: SimpleNamespace(
            content="TRADINGAGENTS_CODEX_FALLBACK_RESPONSE\nprovider timeout"
        )
    )

    with patch("tradingagents.execution.reporting.create_llm_client") as create_client:
        create_client.return_value.get_llm.return_value = fallback_llm
        markdown = render_execution_update_markdown(
            contract,
            update,
            llm_settings=llm_settings,
            llm_model="gpt-5.5",
        )

    assert "TRADINGAGENTS_CODEX_FALLBACK_RESPONSE" not in markdown
    assert "State: `ACTIONABLE_NOW` / Now: `STARTER_NOW`." in markdown
