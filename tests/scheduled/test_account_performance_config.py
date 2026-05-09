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
