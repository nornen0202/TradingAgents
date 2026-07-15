from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from zoneinfo import ZoneInfo

from tradingagents.scheduled.runner import (
    _finalize_active_universe_coverage,
    _github_actions_source_receipt,
    _reconcile_fresh_portfolio_coverage,
    _resolve_run_ticker_universe,
    _select_daily_active_tickers,
    _strict_required_coverage_failed,
)
from tradingagents.scanner.prism_like_scanner import augment_universe_with_scanner


def _config(tmp_path: Path):
    return SimpleNamespace(
        run=SimpleNamespace(tickers=("AAPL", "MSFT", "NVDA", "AMD", "META")),
        portfolio=SimpleNamespace(enabled=True, profile_path=tmp_path / "profile.toml", profile_name="default"),
        storage=SimpleNamespace(archive_dir=tmp_path / "archive"),
    )


def test_active_universe_keeps_holdings_and_rotates_non_holdings(tmp_path: Path):
    config = _config(tmp_path)
    snapshot = SimpleNamespace(
        positions=(
            SimpleNamespace(canonical_ticker="NVDA"),
            SimpleNamespace(canonical_ticker="MSFT"),
        )
    )
    with (
        patch("tradingagents.scheduled.runner.load_portfolio_profile", return_value=SimpleNamespace()),
        patch("tradingagents.scheduled.runner.load_snapshot_for_profile", return_value=snapshot),
    ):
        first, first_omitted, first_meta = _select_daily_active_tickers(
            config=config,
            tickers=["AAPL", "MSFT", "NVDA", "AMD", "META"],
            started_at=datetime(2026, 7, 10, tzinfo=ZoneInfo("Asia/Seoul")),
            active_ticker_limit=3,
        )
        second, _second_omitted, _second_meta = _select_daily_active_tickers(
            config=config,
            tickers=["AAPL", "MSFT", "NVDA", "AMD", "META"],
            started_at=datetime(2026, 7, 11, tzinfo=ZoneInfo("Asia/Seoul")),
            active_ticker_limit=3,
        )

    assert first[:2] == ["MSFT", "NVDA"]
    assert second[:2] == ["MSFT", "NVDA"]
    assert first[2] != second[2]
    assert set(first) | set(first_omitted) == {"AAPL", "MSFT", "NVDA", "AMD", "META"}
    assert first_meta["mode"] == "holdings_first_watchlist_rotation"
    assert first_meta["holding_tickers"] == ["MSFT", "NVDA"]


def test_active_limit_expands_to_cover_every_holding(tmp_path: Path):
    config = _config(tmp_path)
    snapshot = SimpleNamespace(
        positions=tuple(SimpleNamespace(canonical_ticker=ticker) for ticker in ("AAPL", "MSFT", "NVDA", "AMD"))
    )
    with (
        patch("tradingagents.scheduled.runner.load_portfolio_profile", return_value=SimpleNamespace()),
        patch("tradingagents.scheduled.runner.load_snapshot_for_profile", return_value=snapshot),
    ):
        selected, _omitted, metadata = _select_daily_active_tickers(
            config=config,
            tickers=["AAPL", "MSFT", "NVDA", "AMD", "META"],
            started_at=datetime(2026, 7, 10, tzinfo=ZoneInfo("Asia/Seoul")),
            active_ticker_limit=3,
        )

    assert selected[:4] == ["AAPL", "MSFT", "NVDA", "AMD"]
    assert metadata["effective_limit"] == 4


def test_config_plus_account_merges_profile_watchlist_and_out_of_config_holdings(tmp_path: Path):
    config = _config(tmp_path)
    config.run.ticker_universe_mode = "config_plus_account"
    profile = SimpleNamespace(watch_tickers=("AAPL", "MSFT", "META"))
    snapshot = SimpleNamespace(
        positions=(
            SimpleNamespace(canonical_ticker="NVDA"),
            SimpleNamespace(canonical_ticker="SGOV"),
        )
    )
    with (
        patch("tradingagents.scheduled.runner.load_portfolio_profile", return_value=profile),
        patch("tradingagents.scheduled.runner.load_snapshot_for_profile", return_value=snapshot),
    ):
        universe = _resolve_run_ticker_universe(config)

    assert universe.tickers == ("AAPL", "MSFT", "NVDA", "AMD", "META", "SGOV")
    assert universe.profile_watch_tickers == ("AAPL", "MSFT", "META")
    assert universe.holding_tickers == ("NVDA", "SGOV")
    assert universe.account_snapshot_status == "loaded"


def test_github_actions_source_receipt_is_exact_and_fails_closed(monkeypatch):
    values = {
        "GITHUB_RUN_ID": "12345",
        "GITHUB_RUN_ATTEMPT": "2",
        "GITHUB_REPOSITORY": "nornen0202/TradingAgents",
        "GITHUB_WORKFLOW": "Daily Codex Analysis",
        "GITHUB_SHA": "A" * 40,
    }
    for key, value in values.items():
        monkeypatch.setenv(key, value)

    assert _github_actions_source_receipt() == {
        "run_id": 12345,
        "run_attempt": 2,
        "repository": "nornen0202/TradingAgents",
        "workflow": "Daily Codex Analysis",
        "sha": "a" * 40,
    }

    monkeypatch.setenv("GITHUB_SHA", "not-a-commit")
    assert _github_actions_source_receipt() == {}


def test_watchlist_precedes_scanner_candidates_under_active_cap(tmp_path: Path):
    config = _config(tmp_path)
    config.run.ticker_universe_mode = "config_plus_account"
    profile = SimpleNamespace(watch_tickers=tuple(config.run.tickers))
    snapshot = SimpleNamespace(positions=(SimpleNamespace(canonical_ticker="NVDA"),))
    with (
        patch("tradingagents.scheduled.runner.load_portfolio_profile", return_value=profile),
        patch("tradingagents.scheduled.runner.load_snapshot_for_profile", return_value=snapshot),
    ):
        universe = _resolve_run_ticker_universe(config)

    selected, omitted, metadata = _select_daily_active_tickers(
        config=config,
        tickers=[*universe.tickers, "SCAN1", "SCAN2"],
        started_at=datetime(2026, 7, 10, tzinfo=ZoneInfo("Asia/Seoul")),
        active_ticker_limit=3,
        resolved_universe=universe,
    )

    assert selected[0] == "NVDA"
    assert len(selected) == 3
    assert set(selected[1:]) <= {"AAPL", "MSFT", "AMD", "META"}
    assert metadata["scanner_additions"] == []
    assert metadata["omitted_scanner_additions"] == ["SCAN1", "SCAN2"]
    assert {"SCAN1", "SCAN2"} <= set(omitted)


def test_no_cap_covers_alias_holding_watchlist_and_scanner(tmp_path: Path):
    config = _config(tmp_path)
    config.run.tickers = ("005930.KS", "000660.KS")
    config.run.ticker_universe_mode = "config_plus_account"
    profile = SimpleNamespace(watch_tickers=("005930.KS", "000660.KS", "035420.KS"))
    snapshot = SimpleNamespace(
        positions=(
            SimpleNamespace(canonical_ticker="005930"),
            SimpleNamespace(canonical_ticker="403870.KQ"),
        )
    )
    with (
        patch("tradingagents.scheduled.runner.load_portfolio_profile", return_value=profile),
        patch("tradingagents.scheduled.runner.load_snapshot_for_profile", return_value=snapshot),
    ):
        universe = _resolve_run_ticker_universe(config)

    selected, omitted, metadata = _select_daily_active_tickers(
        config=config,
        tickers=[*universe.tickers, "084670.KS"],
        started_at=datetime(2026, 7, 10, tzinfo=ZoneInfo("Asia/Seoul")),
        active_ticker_limit=0,
        resolved_universe=universe,
    )

    assert omitted == []
    assert set(selected) == {"005930.KS", "000660.KS", "035420.KS", "403870.KQ", "084670.KS"}
    assert selected[0] == "005930.KS"
    assert metadata["missing_holding_tickers"] == []
    assert metadata["missing_watchlist_tickers"] == []
    assert metadata["scanner_additions"] == ["084670.KS"]
    assert metadata["coverage"]["complete"] is True


def test_watchlist_only_broker_fallback_is_not_complete_account_coverage(tmp_path: Path):
    config = _config(tmp_path)
    config.run.ticker_universe_mode = "config_plus_account"
    profile = SimpleNamespace(watch_tickers=tuple(config.run.tickers))
    snapshot = SimpleNamespace(
        positions=tuple(),
        snapshot_health="WATCHLIST_ONLY",
        cash_diagnostics={"source": "kis_snapshot_unavailable"},
        warnings=("KIS account snapshot unavailable; generated a watchlist-only snapshot.",),
    )
    with (
        patch("tradingagents.scheduled.runner.load_portfolio_profile", return_value=profile),
        patch("tradingagents.scheduled.runner.load_snapshot_for_profile", return_value=snapshot),
    ):
        universe = _resolve_run_ticker_universe(config)

    selected, omitted, metadata = _select_daily_active_tickers(
        config=config,
        tickers=list(universe.tickers),
        started_at=datetime(2026, 7, 10, tzinfo=ZoneInfo("Asia/Seoul")),
        active_ticker_limit=0,
        resolved_universe=universe,
    )

    assert set(selected) == set(config.run.tickers)
    assert omitted == []
    assert universe.holding_tickers == tuple()
    assert universe.account_snapshot_status == "snapshot_unavailable"
    assert universe.account_snapshot_health == "WATCHLIST_ONLY"
    assert any("account_snapshot_degraded" in warning for warning in universe.warnings)
    assert metadata["coverage"]["complete"] is False


def test_final_coverage_detects_missing_overlay_summary_by_identity():
    metadata = {
        "mode": "full_required_coverage",
        "coverage": {"complete": True},
    }

    finalized = _finalize_active_universe_coverage(
        metadata=metadata,
        expected_tickers=["005930.KS", "000660.KS", "035420.KS"],
        ticker_summaries=[
            {"ticker": "005930", "status": "success"},
            {"ticker": "000660.KS", "status": "success"},
        ],
    )

    assert finalized["missing_analysis_tickers"] == ["035420.KS"]
    assert finalized["coverage"]["selection_complete"] is True
    assert finalized["coverage"]["analysis_complete"] is False
    assert finalized["coverage"]["complete"] is False
    assert _strict_required_coverage_failed({"active_universe": finalized}) is True


def test_final_coverage_accepts_successful_alias_equivalent_summaries():
    metadata = {
        "mode": "full_required_coverage",
        "coverage": {"complete": True},
    }

    finalized = _finalize_active_universe_coverage(
        metadata=metadata,
        expected_tickers=["005930.KS", "000660.KS"],
        ticker_summaries=[
            {"ticker": "005930", "status": "success"},
            {"ticker": "000660.KS", "status": "success"},
        ],
    )

    assert finalized["missing_analysis_tickers"] == []
    assert finalized["coverage"]["analysis_complete"] is True
    assert finalized["coverage"]["complete"] is True
    assert _strict_required_coverage_failed({"active_universe": finalized}) is False


def test_strict_coverage_ignores_intentional_smoke_rotation():
    manifest = {
        "active_universe": {
            "mode": "holdings_first_watchlist_rotation",
            "coverage": {"complete": False},
        }
    }

    assert _strict_required_coverage_failed(manifest) is False


def test_scanner_alias_does_not_consume_new_ticker_quota():
    scanner_result = SimpleNamespace(
        candidates=(
            SimpleNamespace(ticker="005930"),
            SimpleNamespace(ticker="000660.KS"),
        )
    )

    augmented = augment_universe_with_scanner(
        ["005930.KS"],
        scanner_result,
        max_new_tickers=1,
    )

    assert augmented == ["005930.KS", "000660.KS"]


def test_fresh_snapshot_replaces_sold_holding_and_accepts_new_analyzed_holding():
    metadata = {
        "mode": "full_required_coverage",
        "ticker_universe_mode": "config_plus_account",
        "holding_tickers": ["005930.KS", "SOLD"],
        "expected_holding_tickers": ["005930.KS", "SOLD"],
        "missing_holding_tickers": [],
        "missing_watchlist_tickers": [],
        "coverage": {
            "selection_complete": True,
            "analysis_complete": True,
            "complete": True,
        },
    }
    portfolio_status = {
        "private_coverage_snapshot": {
            "snapshot_id": "fresh-1",
            "as_of": "2026-07-16T15:20:00+09:00",
            "snapshot_health": "VALID",
            "holding_set_complete": True,
            "canonical_holding_tickers": ["005930", "NEW"],
        }
    }

    reconciled = _reconcile_fresh_portfolio_coverage(
        metadata=metadata,
        portfolio_status=portfolio_status,
        ticker_summaries=[
            {"ticker": "005930.KS", "status": "success"},
            {"ticker": "NEW", "status": "success"},
        ],
    )

    assert reconciled["expected_holding_tickers"] == ["005930", "NEW"]
    assert reconciled["holding_tickers"] == ["005930", "NEW"]
    assert reconciled["missing_holding_tickers"] == []
    assert reconciled["fresh_snapshot_drift"]["added_holding_tickers"] == ["NEW"]
    assert reconciled["fresh_snapshot_drift"]["removed_holding_tickers"] == ["SOLD"]
    assert reconciled["coverage"]["fresh_snapshot_complete"] is True
    assert reconciled["coverage"]["complete"] is True
    assert _strict_required_coverage_failed({"active_universe": reconciled}) is False


def test_fresh_snapshot_new_unanalyzed_holding_fails_required_coverage():
    metadata = {
        "mode": "full_required_coverage",
        "ticker_universe_mode": "account_only",
        "holding_tickers": ["KEEP"],
        "expected_holding_tickers": ["KEEP"],
        "missing_holding_tickers": [],
        "missing_watchlist_tickers": [],
        "coverage": {
            "selection_complete": True,
            "analysis_complete": True,
            "complete": True,
        },
    }
    portfolio_status = {
        "private_coverage_snapshot": {
            "snapshot_id": "fresh-2",
            "as_of": "2026-07-16T15:21:00+09:00",
            "snapshot_health": "VALID",
            "holding_set_complete": True,
            "canonical_holding_tickers": ["KEEP", "NEW"],
        }
    }

    reconciled = _reconcile_fresh_portfolio_coverage(
        metadata=metadata,
        portfolio_status=portfolio_status,
        ticker_summaries=[{"ticker": "KEEP", "status": "success"}],
    )

    assert reconciled["expected_holding_tickers"] == ["KEEP", "NEW"]
    assert reconciled["holding_tickers"] == ["KEEP"]
    assert reconciled["missing_holding_tickers"] == ["NEW"]
    assert reconciled["coverage"]["holding_missing_count"] == 1
    assert reconciled["coverage"]["selection_complete"] is False
    assert reconciled["coverage"]["complete"] is False
    assert _strict_required_coverage_failed({"active_universe": reconciled}) is True


def test_unavailable_fresh_snapshot_preserves_opening_holdings_and_fails_closed():
    metadata = {
        "mode": "full_required_coverage",
        "ticker_universe_mode": "config_plus_account",
        "holding_tickers": ["KEEP"],
        "expected_holding_tickers": ["KEEP"],
        "missing_holding_tickers": [],
        "missing_watchlist_tickers": [],
        "coverage": {
            "selection_complete": True,
            "analysis_complete": True,
            "complete": True,
        },
    }

    reconciled = _reconcile_fresh_portfolio_coverage(
        metadata=metadata,
        portfolio_status={
            "private_coverage_snapshot": {
                "snapshot_id": "fallback-1",
                "as_of": "2026-07-16T15:22:00+09:00",
                "snapshot_health": "WATCHLIST_ONLY",
                "holding_set_complete": False,
                "canonical_holding_tickers": [],
            }
        },
        ticker_summaries=[{"ticker": "KEEP", "status": "success"}],
    )

    assert reconciled["expected_holding_tickers"] == ["KEEP"]
    assert reconciled["holding_tickers"] == ["KEEP"]
    assert reconciled["account_snapshot_status"] == "fresh_snapshot_unavailable"
    assert reconciled["fresh_snapshot_drift"]["status"] == "UNAVAILABLE"
    assert reconciled["coverage"]["fresh_snapshot_complete"] is False
    assert reconciled["coverage"]["complete"] is False
    assert _strict_required_coverage_failed({"active_universe": reconciled}) is True
