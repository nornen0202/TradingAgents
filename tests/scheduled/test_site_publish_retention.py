import json
from pathlib import Path

from tradingagents.scheduled.config import SiteSettings
from tradingagents.scheduled.site import build_site


def _manifest(run_id: str, *, started_at: str, successful: int, failed: int) -> dict:
    total = successful + failed
    return {
        "version": 1,
        "run_id": run_id,
        "status": "success" if failed == 0 else "partial_failure",
        "started_at": started_at,
        "summary": {
            "total_tickers": total,
            "successful_tickers": successful,
            "failed_tickers": failed,
        },
        "settings": {"output_language": "Korean", "market": "US", "run_mode": "full"},
        "market_session_phase": "regular_session",
        "execution": {
            "execution_data_quality": "REALTIME_EXECUTION_READY",
            "overlay_phase": {"name": "REGULAR_SESSION"},
            "market_data_quality_counts": {"REALTIME_EXECUTION_READY": total},
            "degraded": [],
        },
        "portfolio": {
            "status": "success",
            "profile": "account",
            "artifacts": {
                "portfolio_report_md": "portfolio-private/portfolio_report.md",
                "portfolio_report_json": "portfolio-private/portfolio_report.json",
            },
        },
        "tickers": [
            {
                "ticker": "AAPL",
                "status": "success",
                "analysis_date": "2026-06-17",
                "trade_date": "2026-06-17",
                "decision": {"action": "HOLD", "confidence": 0.5},
                "artifacts": {
                    "report_markdown": "tickers/AAPL/report/complete_report.md",
                },
            }
        ],
    }


def _write_run(archive_dir: Path, manifest: dict) -> Path:
    run_dir = archive_dir / "runs" / manifest["started_at"][:4] / manifest["run_id"]
    report_dir = run_dir / "tickers" / "AAPL" / "report"
    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / "complete_report.md").write_text(f"# {manifest['run_id']}\n", encoding="utf-8")

    private_dir = run_dir / "portfolio-private"
    private_dir.mkdir(parents=True, exist_ok=True)
    (private_dir / "status.json").write_text(
        json.dumps({"status": "success", "profile": "account"}),
        encoding="utf-8",
    )
    (private_dir / "portfolio_report.md").write_text("portfolio report\n", encoding="utf-8")
    (private_dir / "portfolio_report.json").write_text(
        json.dumps({"data_health_summary": {"sell_side_distribution": {"TAKE_PROFIT": 1}}}),
        encoding="utf-8",
    )

    (run_dir / "run.json").write_text(json.dumps(manifest, ensure_ascii=False), encoding="utf-8")
    return run_dir


def test_site_limits_published_runs_but_keeps_latest_daily_and_representative(tmp_path: Path):
    archive_dir = tmp_path / "archive"
    site_dir = tmp_path / "site"
    latest_partial = _manifest(
        "20260617T205857_github-actions-us",
        started_at="2026-06-17T20:58:57+09:00",
        successful=25,
        failed=13,
    )
    representative = _manifest(
        "20260616T140000_github-actions-us",
        started_at="2026-06-16T14:00:00+00:00",
        successful=38,
        failed=0,
    )
    older = _manifest(
        "20260501T010000_github-actions-us",
        started_at="2026-05-01T01:00:00+09:00",
        successful=38,
        failed=0,
    )

    for manifest in (latest_partial, representative, older):
        _write_run(archive_dir, manifest)

    build_site(
        archive_dir,
        site_dir,
        SiteSettings(title="TA", subtitle="Daily", max_runs_on_homepage=1, max_published_runs=1),
    )

    index_html = (site_dir / "index.html").read_text(encoding="utf-8")
    feed = json.loads((site_dir / "feed.json").read_text(encoding="utf-8"))
    feed_by_run = {item["run_id"]: item for item in feed["runs"]}

    assert "Latest daily analysis" in index_html
    assert latest_partial["run_id"] in index_html
    assert "3 archived run(s) / 2 published on Pages" in index_html
    assert (site_dir / "runs" / latest_partial["run_id"] / "index.html").exists()
    assert (site_dir / "runs" / representative["run_id"] / "index.html").exists()
    assert not (site_dir / "runs" / older["run_id"] / "index.html").exists()
    assert not (site_dir / "downloads" / older["run_id"] / "AAPL" / "complete_report.md").exists()
    assert feed_by_run[latest_partial["run_id"]]["published_to_site"] is True
    assert feed_by_run[representative["run_id"]]["published_to_site"] is True
    assert feed_by_run[older["run_id"]]["published_to_site"] is False
