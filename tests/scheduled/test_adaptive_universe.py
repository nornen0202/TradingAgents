from dataclasses import replace
from datetime import datetime, timedelta, timezone
import json
from types import SimpleNamespace
from unittest.mock import patch

import pandas as pd
import pytest

from tradingagents.scheduled import adaptive_universe as au
from tradingagents.scheduled.config import UniverseSettings, _load_universe_settings, load_scheduled_config, with_overrides
from tradingagents.scheduled.runner import _select_daily_active_tickers, _finalize_active_universe_coverage, _strict_required_coverage_failed
from tradingagents.scheduled.site import _render_universe_selection_section

NOW = datetime(2026, 9, 10, 22, tzinfo=timezone.utc)


def setup(tmp_path, *, holdings=("HOLD",), market="US", **settings):
    config = SimpleNamespace(universe=replace(UniverseSettings(enabled=True), **settings),
        run=SimpleNamespace(market=market, run_mode="full", explicit_trade_date=None),
        storage=SimpleNamespace(archive_dir=tmp_path), portfolio=SimpleNamespace(profile_name="test"))
    universe = SimpleNamespace(holding_tickers=holdings, account_snapshot_status="loaded",
        account_snapshot_health="VALID", configured_tickers=(), mode="config_plus_account")
    return config, universe


def quote(ticker, *, sector="Technology", market="US", **values):
    return {"symbol": ticker, "currency": "KRW" if market == "KR" else "USD",
        "regularMarketTime": (NOW - timedelta(hours=2)).timestamp(), "regularMarketPrice": 100,
        "averageDailyVolume3Month": 1e9, "fiftyDayAverage": 95, "twoHundredDayAverage": 90,
        "regularMarketChangePercent": 2, "sector": sector, **values}


def select(config, universe, quotes, *, history=None, previous=None, tickers=None, cached=None, limit=0):
    return au.select_adaptive_universe(config=config, universe=universe, tickers=tickers or list(quotes),
        asof=NOW, requested_limit=limit, quotes=quotes, history_bundle=(history or {}, previous or [], cached or {}))


def test_account_holdings_are_mandatory_and_every_override_stays_under_30(tmp_path):
    config, universe = setup(tmp_path, holdings=("HOLD", "HELD"))
    quotes = {f"T{i}": quote(f"T{i}", sector=au.SECTORS[i % 11]) for i in range(70)}
    selected, omitted, receipt = select(config, universe, quotes, limit=100)
    assert selected[:2] == ["HOLD", "HELD"]
    assert len(selected) == len(set(selected)) == 30
    assert receipt["coverage"]["complete"] is True
    assert set(receipt["expected_watchlist_tickers"]) == set(selected[2:])
    assert len(omitted) == 42
    assert all(row["selection_reason"] for row in receipt["candidates"])
    report = au.render_selection_report(receipt)
    assert "보유 종목 필수 포함" in report
    assert "오늘 제외한 후보" in report
    assert "수익 확률" in report


@pytest.mark.parametrize("status", ["disabled", "watchlist_only", "snapshot_load_failed", "invalid_snapshot"])
def test_account_failure_cannot_silently_become_seed_only_analysis(tmp_path, status):
    config, universe = setup(tmp_path)
    universe.account_snapshot_status = status
    with patch.object(au, "research_quotes") as research, pytest.raises(RuntimeError, match="ACCOUNT_UNAVAILABLE"):
        au.select_adaptive_universe(config=config, universe=universe, tickers=[], asof=NOW)
    research.assert_not_called()


def test_over_30_holdings_fail_explicitly_without_dropping_one(tmp_path):
    config, universe = setup(tmp_path, holdings=tuple(f"H{i}" for i in range(31)))
    with pytest.raises(RuntimeError, match="HOLDINGS_EXCEED_CAP"):
        select(config, universe, {})


def test_small_smoke_limit_expands_only_for_holdings_and_never_excludes_them(tmp_path):
    config, universe = setup(tmp_path, holdings=("AAA", "BBB", "CCC", "DDD"))
    selected, _, _ = select(config, universe, {"NEW": quote("NEW")}, limit=3)
    assert selected == list(universe.holding_tickers)


def test_korean_aliases_share_one_slot_and_us_candidates_are_excluded(tmp_path):
    config, universe = setup(tmp_path, market="KR", holdings=("005930", "005930.KS"))
    quotes = {"KR:005930": quote("005930.KS", market="KR"), "NVDA": quote("NVDA"),
              "KR:000660": quote("000660.KS", market="KR")}
    selected, _, _ = select(config, universe, quotes, tickers=["005930.KS", "000660.KS", "NVDA"])
    assert selected == ["005930.KS", "000660.KS"]


@pytest.mark.parametrize("values", [
    {"regularMarketTime": (NOW + timedelta(days=1)).timestamp()},
    {"regularMarketTime": (NOW - timedelta(days=8)).timestamp()},
    {"regularMarketPrice": float("nan")}, {"regularMarketPrice": -1},
    {"averageDailyVolume3Month": 1}, {"currency": "EUR"},
    {"regularMarketChangePercent": 21},
])
def test_bad_optional_candidates_are_excluded_but_holdings_remain(tmp_path, values):
    config, universe = setup(tmp_path)
    selected, _, receipt = select(config, universe, {"BAD": quote("BAD", **values)})
    assert selected == ["HOLD"]
    assert receipt["underfilled"]
    assert receipt["candidates"][-1]["selection_reason"] == "failed_data_or_liquidity_gate"
    json.dumps(receipt, allow_nan=False)


def historical(ticker, rating="BUY", *, age=1):
    return {"ticker": ticker, "asof": (NOW - timedelta(days=age)).isoformat(), "rating": rating,
        "setup_quality": "COMPELLING", "entry_action": "WAIT", "risk_action": "HOLD",
        "quality_flags": [], "trigger_prices": [101]}


def test_history_changes_priority_without_relying_on_llm_confidence(tmp_path):
    config, universe = setup(tmp_path, max_tickers=2, exploration_slots=0)
    quotes = {t: quote(t) for t in ("WIN", "LOSE")}
    history = {"WIN": historical("WIN"), "LOSE": historical("LOSE", "SELL")}
    selected, _, receipt = select(config, universe, quotes, history=history)
    assert selected == ["HOLD", "WIN"]
    assert receipt["scores_are_profit_probabilities"] is False


def test_new_candidates_have_reserved_research_slots_and_daily_replacement_bound(tmp_path):
    config, universe = setup(tmp_path, max_tickers=10, max_new_nonholdings=3, exploration_slots=2)
    old = [f"OLD{i}" for i in range(9)]
    new = [f"NEW{i}" for i in range(20)]
    quotes = {t: quote(t, sector=au.SECTORS[i % 11]) for i, t in enumerate(old + new)}
    selected, _, receipt = select(config, universe, quotes, history={t: historical(t) for t in old}, previous=["HOLD", *old])
    added = set(selected) & set(new)
    assert 2 <= len(added) <= 3
    assert len(selected) == 10
    assert receipt["new_nonholding_count"] <= 3


def test_sector_limit_does_not_relax_to_fill_the_cap(tmp_path):
    config, universe = setup(tmp_path, max_per_sector=4)
    selected, _, receipt = select(config, universe, {f"T{i}": quote(f"T{i}") for i in range(20)})
    assert len(selected) == 5  # mandatory holding has unknown sector
    assert receipt["underfilled"]
    assert any(r["selection_reason"] == "sector_research_limit" for r in receipt["candidates"])


def test_cached_quotes_are_age_checked_and_marked(tmp_path):
    config, universe = setup(tmp_path)
    cached = {"GOOD": quote("GOOD"), "STALE": quote("STALE", regularMarketTime=(NOW-timedelta(days=10)).timestamp())}
    selected, _, receipt = select(config, universe, {}, cached=cached)
    assert selected == ["HOLD", "GOOD"]
    assert next(r for r in receipt["candidates"] if r["ticker"] == "GOOD")["quote"]["source"] == "archived_quote"


def test_selection_failure_is_strict_but_intentionally_omitted_seeds_are_not(tmp_path):
    config, universe = setup(tmp_path, max_tickers=2)
    selected, _, receipt = select(config, universe, {"AAA": quote("AAA"), "BBB": quote("BBB")})
    rows = [{"ticker": t, "status": "success"} for t in selected]
    good = _finalize_active_universe_coverage(metadata=receipt, expected_tickers=selected, ticker_summaries=rows)
    assert not _strict_required_coverage_failed({"active_universe": good})
    bad = _finalize_active_universe_coverage(metadata=receipt, expected_tickers=selected, ticker_summaries=rows[:-1])
    assert _strict_required_coverage_failed({"active_universe": bad})


def test_research_source_circuit_breaker_is_bounded():
    with patch.object(au.yf, "screen", side_effect=RuntimeError("private URL")) as screen, patch.object(au.yf, "download") as download:
        quotes, warnings = au.research_quotes(market="US", tickers=["AAPL"], max_candidates=160)
    assert quotes == {}
    assert screen.call_count == 3
    download.assert_not_called()
    assert "research_source_circuit_open" in warnings
    assert "private URL" not in str(warnings)


def test_price_refresh_uses_latest_bar_without_backfill():
    index = pd.date_range("2026-01-01", periods=210)
    frame = pd.DataFrame({("AAA", "Close"): [100.] * 209 + [float("nan")],
                          ("AAA", "Volume"): [1e7] * 210}, index=index)
    with patch.object(au.yf, "download", return_value=frame):
        quotes, warnings = au.refresh_seed_quotes(["AAA"], market="US")
    assert not quotes
    assert warnings == ["seed_price_unavailable:AAA"]


def decision():
    return {"rating": "BUY", "confidence": 0.7, "time_horizon": "medium", "entry_logic": "Confirm",
        "exit_logic": "Invalidation", "position_sizing": "Bounded", "risk_limits": "No leverage",
        "catalysts": ["earnings"], "invalidators": ["support"]}


def test_history_ignores_future_other_market_overlay_and_unvalidated_runs(tmp_path):
    for name, market, mode, offset, valid in [("good", "US", "full", -1, True),
            ("future", "US", "full", 1, True), ("kr", "KR", "full", -1, True),
            ("overlay", "US", "overlay_only", -1, True), ("invalid", "US", "full", -1, False)]:
        path = tmp_path / "runs" / "2026" / name / "run.json"
        path.parent.mkdir(parents=True)
        path.write_text(json.dumps({"run_id": name, "finished_at": (NOW+timedelta(days=offset)).isoformat(),
            "status": "success", "settings": {"market": market, "run_mode": mode},
            "tickers": [{"ticker": name.upper(), "status": "success", "decision": decision(),
                          "quality_flags": [] if valid else ["decision_unvalidated"]}]}), encoding="utf-8")
    history, _, _ = au.read_history(tmp_path, market="US", asof=NOW, days=30)
    assert set(history) == {"GOOD"}


def test_overlay_never_reranks_the_frozen_daily_universe(tmp_path):
    config, universe = setup(tmp_path)
    config.run.run_mode = "overlay_only"
    universe.tickers = ("HOLD", "AAA")
    universe.configured_tickers = ("AAA",)
    universe.profile_watch_tickers = ()
    with patch.object(au, "select_adaptive_universe", side_effect=AssertionError("must not rerank")):
        selected, _, _ = _select_daily_active_tickers(config=config, tickers=["HOLD", "AAA"],
            started_at=NOW, active_ticker_limit=0, resolved_universe=universe)
    assert selected == ["HOLD", "AAA"]


def test_runner_dispatches_full_runs_to_adaptive_selection(tmp_path):
    config, universe = setup(tmp_path)
    with patch.object(au, "research_quotes", return_value=({"AAA": quote("AAA")}, [])), patch.object(au, "read_history", return_value=({}, [], {})):
        selected, _, receipt = _select_daily_active_tickers(config=config, tickers=["AAA"],
            started_at=NOW, active_ticker_limit=30, resolved_universe=universe)
    assert selected == ["HOLD", "AAA"]
    assert receipt["mode"] == "adaptive_required_coverage"


def test_public_seed_holding_stays_public_but_account_only_holding_stays_private(tmp_path):
    config, universe = setup(tmp_path, holdings=("PUBLIC", "PRIVATE"))
    universe.configured_tickers = ("PUBLIC", "AAA")
    _, _, receipt = select(config, universe, {"AAA": quote("AAA")})
    assert set(receipt["expected_watchlist_tickers"]) == {"PUBLIC", "AAA"}
    assert set(receipt["watchlist_tickers"]) == {"AAA"}


def test_account_only_override_cannot_add_optional_names(tmp_path):
    config, universe = setup(tmp_path)
    universe.mode = "account_only"
    selected, _, _ = select(config, universe, {"AAA": quote("AAA")})
    assert selected == ["HOLD"]


def test_wrong_market_account_fails_without_silently_dropping_holdings(tmp_path):
    config, universe = setup(tmp_path, holdings=("005930.KS",))
    with pytest.raises(RuntimeError, match="MARKET_MISMATCH"):
        select(config, universe, {})


@pytest.mark.parametrize("raw", [{"max_tickers": 31}, {"max_candidates": 10}, {"quote_max_age_days": 20},
                                {"exploration_slots": 10, "max_new_nonholdings": 2}, {"min_daily_value_usd": float("nan")}])
def test_invalid_policy_is_rejected(raw):
    with pytest.raises(ValueError):
        _load_universe_settings(raw)


def test_both_production_configs_enable_the_cap_and_overrides_keep_policy():
    for name in ("scheduled_analysis.toml", "scheduled_analysis_korea.toml"):
        config = load_scheduled_config(f"config/{name}")
        assert config.universe.enabled and config.universe.max_tickers == 30
        assert config.run.daily_active_ticker_limit == 30
        assert with_overrides(config, daily_active_ticker_limit=100).universe.max_tickers == 30


def test_public_selection_section_escapes_labels_and_explains_research_only(tmp_path):
    config, universe = setup(tmp_path)
    _, _, receipt = select(config, universe, {"AAA": quote("AAA")})
    manifest = {"active_universe": receipt}
    with patch("tradingagents.scheduled.site._public_ticker_summaries", return_value=[{"ticker": "AAA"}]):
        html = _render_universe_selection_section(manifest)
    assert "매수 추천이나 수익 확률이 아닙니다" in html
    assert "새로운 기회 조사" in html
    assert "HOLD" not in html
