from tradingagents.schemas import ActionIfTriggered, ExecutionContract, LevelBasis, PrimarySetup, ThesisState


def test_execution_contract_to_dict_required_fields():
    contract = ExecutionContract(
        ticker="TSM",
        analysis_asof="2026-04-13T20:05:12+09:00",
        market_data_asof="2026-04-10T16:00:00-04:00",
        level_basis=LevelBasis.DAILY_CLOSE,
        thesis_state=ThesisState.CONSTRUCTIVE,
        primary_setup=PrimarySetup.WATCH_ONLY,
        portfolio_stance="BULLISH",
        entry_action_base="WAIT",
        setup_quality="DEVELOPING",
        confidence=0.7,
        action_if_triggered=ActionIfTriggered.NONE,
    )
    payload = contract.to_dict()
    assert payload["ticker"] == "TSM"
    assert payload["level_basis"] == "daily_close"
    assert payload["action_if_triggered"] == "NONE"
