import json
from pathlib import Path
from unittest.mock import patch

from tradingagents.live.context_delta import build_live_context_delta, render_report_vs_live_delta_markdown
from tradingagents.schemas import (
    ActionIfTriggered,
    BreakoutConfirmation,
    ExecutionContract,
    LevelBasis,
    PrimarySetup,
    SessionVWAPPreference,
    ThesisState,
)


def test_report_vs_live_delta_artifact(tmp_path: Path):
    contract = ExecutionContract(
        ticker="278470.KS",
        analysis_asof="2026-04-23T08:00:00+09:00",
        market_data_asof="2026-04-22",
        level_basis=LevelBasis.DAILY_CLOSE,
        thesis_state=ThesisState.CONSTRUCTIVE,
        primary_setup=PrimarySetup.BREAKOUT_CONFIRMATION,
        portfolio_stance="BULLISH",
        entry_action_base="WAIT",
        setup_quality="DEVELOPING",
        confidence=0.8,
        action_if_triggered=ActionIfTriggered.STARTER,
        breakout_level=439500,
        breakout_confirmation=BreakoutConfirmation.INTRADAY_ABOVE,
        min_relative_volume=1.1,
        session_vwap_preference=SessionVWAPPreference.ABOVE,
    )
    (tmp_path / "execution_contract.json").write_text(
        json.dumps(contract.to_dict(), ensure_ascii=False),
        encoding="utf-8",
    )

    manifest = {
        "run_id": "20260423T075140_github-actions-kr",
        "started_at": "2026-04-23T10:30:00+09:00",
        "settings": {"market": "KR"},
        "tickers": [
            {
                "ticker": "278470.KS",
                "decision": json.dumps(
                    {
                        "rating": "HOLD",
                        "portfolio_stance": "BULLISH",
                        "entry_action": "WAIT",
                        "setup_quality": "DEVELOPING",
                        "confidence": 0.8,
                        "time_horizon": "short",
                        "entry_logic": "watch",
                        "exit_logic": "trim",
                        "position_sizing": "starter",
                        "risk_limits": "1R",
                        "catalysts": [],
                        "invalidators": [],
                        "watchlist_triggers": [],
                        "data_coverage": {
                            "company_news_count": 1,
                            "disclosures_count": 0,
                            "social_source": "dedicated",
                            "macro_items_count": 1,
                        },
                    },
                    ensure_ascii=False,
                ),
                "execution_update": {
                    "execution_asof": "2026-04-23T10:30:00+09:00",
                    "last_price": 439500,
                    "day_high": 440000,
                    "day_low": 425000,
                    "session_vwap": 435000,
                    "relative_volume": 1.15,
                    "decision_state": "ACTIONABLE_NOW",
                    "execution_timing_state": "PILOT_READY",
                    "reason_codes": ["pilot_ready"],
                    "source": {"execution_data_quality": "REALTIME_EXECUTION_READY"},
                },
                "artifacts": {"execution_contract_json": "execution_contract.json"},
            }
        ],
    }

    with patch("tradingagents.live.context_delta.build_news_delta", return_value=["earnings_estimate_upgraded"]):
        artifact = build_live_context_delta(run_dir=tmp_path, manifest=manifest)

    assert artifact is not None
    assert artifact["ticker_deltas"][0]["live_action"] == "PILOT_CANDIDATE"
    assert "PRICE_ABOVE_TRIGGER" in artifact["ticker_deltas"][0]["reason_codes"]
    assert artifact["portfolio_delta"]["changed_since_base"] is True

    markdown = render_report_vs_live_delta_markdown(artifact)
    assert "리포트 원판 vs 최신 장중 재분석" in markdown
    assert "278470.KS" in json.dumps(artifact, ensure_ascii=False)
