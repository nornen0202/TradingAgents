from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
from zoneinfo import ZoneInfo

from tradingagents.scheduled.runner import _select_daily_active_tickers


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
    assert first_meta["mode"] == "holdings_first_rotating_coverage"
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
