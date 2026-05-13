from pathlib import Path

from tradingagents.scheduled.config import _load_portfolio_performance_settings


def test_min_coverage_ratio_zero_is_preserved(tmp_path: Path):
    settings = _load_portfolio_performance_settings({"min_coverage_ratio": 0.0}, base_dir=tmp_path)

    assert settings.min_coverage_ratio == 0.0


def test_min_coverage_ratio_missing_defaults_to_point_eight(tmp_path: Path):
    settings = _load_portfolio_performance_settings({}, base_dir=tmp_path)

    assert settings.min_coverage_ratio == 0.8


def test_min_coverage_ratio_is_clamped(tmp_path: Path):
    high = _load_portfolio_performance_settings({"min_coverage_ratio": 1.2}, base_dir=tmp_path)
    low = _load_portfolio_performance_settings({"min_coverage_ratio": -0.5}, base_dir=tmp_path)

    assert high.min_coverage_ratio == 1.0
    assert low.min_coverage_ratio == 0.0


def test_broker_performance_settings_are_loaded(tmp_path: Path):
    settings = _load_portfolio_performance_settings(
        {
            "broker_return_baseline_path": "broker.json",
            "broker_period_start": "2026-04-13",
            "broker_period_end": "2026-05-12",
            "prefer_broker_reported_performance": False,
            "show_snapshot_performance_when_unreconciled": True,
        },
        base_dir=tmp_path,
    )

    assert settings.broker_return_baseline_path == tmp_path / "broker.json"
    assert settings.broker_period_start == "2026-04-13"
    assert settings.broker_period_end == "2026-05-12"
    assert settings.prefer_broker_reported_performance is False
    assert settings.show_snapshot_performance_when_unreconciled is True
