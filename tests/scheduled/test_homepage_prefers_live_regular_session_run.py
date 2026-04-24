import json
from pathlib import Path

from tradingagents.dataflows.intraday_market import DELAYED_ANALYSIS_ONLY, REALTIME_EXECUTION_READY
from tradingagents.scheduled.config import SiteSettings
from tradingagents.scheduled.site import build_site


def _write_run(run_dir: Path, payload: dict) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "run.json").write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def test_homepage_prefers_live_regular_session_run(tmp_path: Path):
    archive_dir = tmp_path / "archive"
    site_dir = tmp_path / "site"

    regular_live = {
        "version": 1,
        "run_id": "20260424T013000_live-kr",
        "status": "success",
        "started_at": "2026-04-24T01:30:00+00:00",
        "summary": {"total_tickers": 10, "successful_tickers": 10, "failed_tickers": 0},
        "settings": {"output_language": "Korean", "market": "KR"},
        "market_session_phase": "regular_session",
        "execution": {"execution_data_quality": REALTIME_EXECUTION_READY, "overlay_phase": {"name": "CHECKPOINT_10_30"}},
        "portfolio": {"status": "disabled"},
        "tickers": [],
    }
    pre_open = {
        "version": 1,
        "run_id": "20260424T000500_preopen-kr",
        "status": "success",
        "started_at": "2026-04-24T00:05:00+00:00",
        "summary": {"total_tickers": 10, "successful_tickers": 10, "failed_tickers": 0},
        "settings": {"output_language": "Korean", "market": "KR"},
        "market_session_phase": "pre_open",
        "execution": {"execution_data_quality": REALTIME_EXECUTION_READY, "overlay_phase": {"name": "PRE_OPEN"}},
        "portfolio": {"status": "disabled"},
        "tickers": [],
    }
    delayed = {
        "version": 1,
        "run_id": "20260424T060000_delayed-kr",
        "status": "success",
        "started_at": "2026-04-24T06:00:00+00:00",
        "summary": {"total_tickers": 10, "successful_tickers": 10, "failed_tickers": 0},
        "settings": {"output_language": "Korean", "market": "KR"},
        "market_session_phase": "regular_session",
        "execution": {"execution_data_quality": DELAYED_ANALYSIS_ONLY, "overlay_phase": {"name": "CHECKPOINT_15_00"}},
        "portfolio": {"status": "disabled"},
        "tickers": [],
    }

    _write_run(archive_dir / "runs" / "2026" / regular_live["run_id"], regular_live)
    _write_run(archive_dir / "runs" / "2026" / pre_open["run_id"], pre_open)
    _write_run(archive_dir / "runs" / "2026" / delayed["run_id"], delayed)

    build_site(archive_dir, site_dir, SiteSettings(title="TA", subtitle="Daily"))
    html = (site_dir / "index.html").read_text(encoding="utf-8")

    assert regular_live["run_id"] in html
    assert "Latest technical run" in html or "가장 최근 기술 run" in html
