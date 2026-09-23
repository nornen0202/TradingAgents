import json

import pytest

from tradingagents.scheduled import site
from tradingagents.scheduled.config import SiteSettings


def test_corrupt_archive_does_not_hide_valid_reports(tmp_path):
    runs = tmp_path / "runs"
    for run_id, content in [
        ("valid", json.dumps({"run_id": "valid", "started_at": "2026-09-22", "status": "success", "settings": {}})),
        ("partial-write", "{"),
        ("invalid-shape", "[]"),
        ("mismatched-id", json.dumps({"run_id": "../escape", "started_at": "2026-09-22", "status": "success", "settings": {}})),
    ]:
        path = runs / run_id / "run.json"
        path.parent.mkdir(parents=True)
        path.write_text(content, encoding="utf-8")
    with pytest.warns(RuntimeWarning):
        manifests = site._load_run_manifests(tmp_path)
    assert [item["run_id"] for item in manifests] == ["valid"]


def test_homepage_does_not_parse_private_portfolio_files(tmp_path, monkeypatch):
    run_dir = tmp_path / "run"
    private = run_dir / "portfolio-private"
    private.mkdir(parents=True)
    (private / "status.json").write_text("{", encoding="utf-8")
    manifest = {"run_id": "run", "started_at": "2026-09-22", "status": "success",
                "settings": {}, "_run_dir": str(run_dir), "tickers": []}
    def forbidden(*args, **kwargs):
        raise AssertionError("Homepage must not load private account payloads")
    monkeypatch.setattr(site, "_load_portfolio_summary", forbidden)
    page = site._render_index_page([manifest], SiteSettings())
    assert "strategy.html" in page
    assert 'aria-label="주요 메뉴"' in page


def test_corrupt_portfolio_status_degrades_to_empty_summary(tmp_path):
    private = tmp_path / "portfolio-private"
    private.mkdir()
    (private / "status.json").write_text("{", encoding="utf-8")
    with pytest.warns(RuntimeWarning, match="portfolio status"):
        assert site._load_portfolio_summary(tmp_path) == {}
