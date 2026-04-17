import json
import tempfile
from pathlib import Path

from tradingagents.scheduled.config import SiteSettings
from tradingagents.scheduled.site import build_site


def _write_run(run_dir: Path, payload: dict) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "run.json").write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def test_homepage_prefers_latest_useful_run_over_latest_stale_run():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        archive_dir = root / "archive"
        site_dir = root / "site"

        useful = {
            "version": 1,
            "run_id": "20260417T044622_github-actions-overlay-us",
            "status": "success",
            "started_at": "2026-04-17T04:46:22+00:00",
            "summary": {"total_tickers": 20, "successful_tickers": 20, "failed_tickers": 0},
            "settings": {"output_language": "Korean"},
            "execution": {"overlay_phase": {"name": "CHECKPOINT_13_40"}, "degraded": ["TSLA"]},
            "portfolio": {"status": "disabled"},
            "tickers": [],
        }
        stale = {
            "version": 1,
            "run_id": "20260417T060132_github-actions-overlay-us",
            "status": "success",
            "started_at": "2026-04-17T06:01:32+00:00",
            "summary": {"total_tickers": 20, "successful_tickers": 20, "failed_tickers": 0},
            "settings": {"output_language": "Korean"},
            "execution": {"overlay_phase": {"name": "CHECKPOINT_15_20"}, "degraded": [f"T{i}" for i in range(20)]},
            "portfolio": {"status": "disabled"},
            "tickers": [],
        }
        _write_run(archive_dir / "runs" / "2026" / useful["run_id"], useful)
        _write_run(archive_dir / "runs" / "2026" / stale["run_id"], stale)

        build_site(archive_dir, site_dir, SiteSettings(title="TA", subtitle="Daily"))
        html = (site_dir / "index.html").read_text(encoding="utf-8")

    assert "Open 대표 투자 run" in html
    assert useful["run_id"] in html
    assert "가장 최근 기술 run" in html
    assert stale["run_id"] in html
