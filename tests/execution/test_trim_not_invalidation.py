import json
from dataclasses import replace
from datetime import datetime, timedelta, timezone

import pytest

from tradingagents.execution.contract_builder import build_execution_contract, has_legacy_trim_invalidation
from tradingagents.execution.overlay import evaluate_execution_state
from tradingagents.schemas import IntradayMarketSnapshot


def _analysis_payload(levels, *, risk_action="NONE", risk_level=None):
    decision = {
        "rating": "HOLD", "portfolio_stance": "NEUTRAL", "entry_action": "WAIT",
        "setup_quality": "DEVELOPING", "confidence": 0.6, "time_horizon": "short",
        "entry_logic": "신규 진입은 별도 검증 후 재평가한다.",
        "exit_logic": "반등 감축과 종가 손절 조건을 구분한다.",
        "position_sizing": "반등에서는 보유의 25%만 감축한다.",
        "risk_limits": "보유 수량을 넘는 매도를 금지한다.",
        "catalysts": [], "invalidators": ["정규장 종가의 지지선 이탈을 확인한다."],
        "watchlist_triggers": [],
        "data_coverage": {"company_news_count": 1, "disclosures_count": 1,
                          "social_source": "unavailable", "macro_items_count": 0},
        "execution_levels": {"levels": levels, "vwap_required": False},
        "risk_action": risk_action,
        "risk_action_reason": "반등 저항 도달 시 보유 일부만 위험 축소한다.",
        "risk_action_level": risk_level,
    }
    return {
        "decision": json.dumps(decision, ensure_ascii=False),
        "finished_at": "2026-10-22T08:00:00+09:00", "trade_date": "2026-10-21",
    }


def _contract(levels, **kwargs):
    return build_execution_contract(ticker="278470.KS", analysis_payload=_analysis_payload(levels, **kwargs))


def _market(price):
    return IntradayMarketSnapshot(
        ticker="278470.KS", asof="2026-10-22T10:45:00+09:00",
        provider="yfinance_intraday", interval="5m", last_price=price,
        session_vwap=price, day_high=price + 100, day_low=price - 100,
        volume=1000, avg20_daily_volume=1000, relative_volume=1,
        market_session="regular",
    )


@pytest.mark.parametrize("price,expected_action", [(319000, "NONE"), (333000, "REDUCE_NOW")])
def test_rebound_trim_does_not_become_a_downside_exit(price, expected_action):
    trim = {"label": "반등 저항 감축", "level_type": "TRIM", "price": 331500,
            "low": 331500, "high": 339000, "confirmation": "intraday",
            "source_text": "반등 저항 도달 시 보유 25%만 감축한다."}
    contract = _contract([
        {"label": "선행 돌파 실패", "level_type": "INVALIDATION", "price": 326000,
         "confirmation": "two_bar"},
        trim,
        {"label": "전술분 종가 손절", "level_type": "STOP_LOSS", "price": 307000,
         "confirmation": "close"},
    ], risk_action="REDUCE_RISK", risk_level=trim)
    assert "fallback_contract" not in contract.reason_codes
    update = evaluate_execution_state(
        contract, _market(price), now=datetime.fromisoformat("2026-10-22T10:45:00+09:00"),
        max_data_age_seconds=120,
    )
    assert update.decision_now.value == expected_action
    assert "intraday_invalidation_breached" not in update.reason_codes
    assert contract.invalid_if_intraday_below is None
    assert contract.invalid_if_close_below == 307000


@pytest.mark.parametrize("confirmation", ["intraday", "close"])
def test_trim_level_cannot_hide_the_actual_stop_with_the_same_confirmation(confirmation):
    contract = _contract([
        {"label": "반등 감축", "level_type": "TRIM", "price": 331500,
         "confirmation": confirmation},
        {"label": "손절", "level_type": "STOP_LOSS", "price": 307000,
         "confirmation": confirmation},
    ])
    assert "fallback_contract" not in contract.reason_codes
    assert getattr(contract, "invalid_if_" + confirmation + "_below") == 307000


@pytest.mark.parametrize("kind", ["INVALIDATION", "STOP_LOSS"])
def test_explicit_intraday_downside_protection_still_exits(kind):
    contract = _contract([
        {"label": "장중 하방 방어", "level_type": kind, "price": 307000,
         "confirmation": "intraday"},
    ])
    update = evaluate_execution_state(
        contract, _market(306000), now=datetime.fromisoformat("2026-10-22T10:45:00+09:00"),
        max_data_age_seconds=120,
    )
    assert contract.invalid_if_intraday_below == 307000
    assert update.decision_now.value == "EXIT_NOW"
    assert "intraday_invalidation_breached" in update.reason_codes


@pytest.mark.parametrize("legacy", [True, False])
def test_overlay_rebuilds_only_affected_cached_contract_without_research_or_clock_edits(tmp_path, legacy):
    from tradingagents.scheduled.config import load_scheduled_config
    from tradingagents.scheduled.runner import _bootstrap_overlay_inputs_from_latest_run

    payload = _analysis_payload([
        {"label": "반등 감축", "level_type": "TRIM", "price": 331500,
         "confirmation": "intraday"},
        {"label": "종가 손절", "level_type": "STOP_LOSS", "price": 307000,
         "confirmation": "close"},
    ])
    cached = build_execution_contract(ticker="278470.KS", analysis_payload=payload).to_dict()
    if legacy:
        cached["invalid_if_intraday_below"] = 331500
    assert has_legacy_trim_invalidation(cached) == legacy
    archive = tmp_path / "archive"
    source = archive / "runs" / "2026" / "source-full"
    ticker_dir = source / "tickers" / "278470.KS"
    ticker_dir.mkdir(parents=True)
    analysis_text = json.dumps(payload, ensure_ascii=False)
    contract_text = json.dumps(cached, ensure_ascii=False)
    (ticker_dir / "analysis.json").write_text(analysis_text, encoding="utf-8")
    (ticker_dir / "execution_contract.json").write_text(contract_text, encoding="utf-8")
    manifest = {
        "run_id": "source-full", "status": "success",
        "started_at": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat(),
        "settings": {"run_mode": "full", "market": "KR"},
        "summary": {"total_tickers": 1, "successful_tickers": 1, "failed_tickers": 0},
        "tickers": [{"ticker": "278470.KS", "status": "success", "decision": payload["decision"],
                     "artifacts": {"analysis_json": "tickers/278470.KS/analysis.json",
                                   "execution_contract_json": "tickers/278470.KS/execution_contract.json"}}],
    }
    (source / "run.json").write_text(json.dumps(manifest), encoding="utf-8")
    (archive / "latest-run.json").write_text(json.dumps(manifest), encoding="utf-8")
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        '[run]\nmarket="KR"\ntickers=["278470.KS"]\nrun_mode="overlay_only"\n'
        f'[storage]\narchive_dir="{archive.as_posix()}"\nsite_dir="{(tmp_path / "site").as_posix()}"\n'
        '[execution]\nenabled=true\n', encoding="utf-8",
    )
    config = load_scheduled_config(config_path)
    config = replace(config, execution=replace(config.execution, execution_lightweight_refresh=True))
    destination = archive / "runs" / "2026" / "new-overlay"
    summaries, source_id = _bootstrap_overlay_inputs_from_latest_run(
        config=config, run_dir=destination, tickers=["278470.KS"],
    )
    rebuilt_path = destination / summaries[0]["artifacts"]["execution_contract_json"]
    rebuilt = json.loads(rebuilt_path.read_text(encoding="utf-8"))
    assert source_id == "source-full"
    assert rebuilt["invalid_if_intraday_below"] is None
    assert rebuilt["invalid_if_close_below"] == 307000
    assert rebuilt["analysis_asof"] == cached["analysis_asof"]
    assert rebuilt["market_data_asof"] == cached["market_data_asof"]
    assert summaries[0]["metrics"]["llm_calls"] == 0
    assert (ticker_dir / "analysis.json").read_text(encoding="utf-8") == analysis_text
    assert (ticker_dir / "execution_contract.json").read_text(encoding="utf-8") == contract_text
    assert (destination / summaries[0]["artifacts"]["analysis_json"]).read_text(encoding="utf-8") == analysis_text
    if not legacy:
        assert rebuilt_path.read_text(encoding="utf-8") == contract_text
