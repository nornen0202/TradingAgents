import json
import tempfile
from pathlib import Path

from tradingagents.scheduled.config import SiteSettings
from tradingagents.scheduled.site import _run_phase_label, build_site


def _write_run(run_dir: Path, payload: dict) -> None:
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "run.json").write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def _manifest(
    run_id: str,
    *,
    started_at: str,
    market_session_phase: str,
    portfolio_status: str,
    total_tickers: int,
    degraded_count: int = 0,
    execution_data_quality: str = "REALTIME_EXECUTION_READY",
) -> dict:
    return {
        "version": 1,
        "run_id": run_id,
        "status": "success",
        "started_at": started_at,
        "market_session_phase": market_session_phase,
        "summary": {"total_tickers": total_tickers, "successful_tickers": total_tickers, "failed_tickers": 0},
        "settings": {"output_language": "Korean", "market": "US"},
        "execution": {
            "overlay_phase": {"name": "CHECKPOINT_14_35"},
            "degraded": [f"T{i}" for i in range(degraded_count)],
            "execution_data_quality": execution_data_quality,
            "market_data_quality_counts": {execution_data_quality: total_tickers},
        },
        "portfolio": (
            {"status": portfolio_status, "profile": "us_account"}
            if portfolio_status and portfolio_status != "disabled"
            else {"status": "disabled"}
        ),
        "tickers": [],
    }


def test_us_delayed_provider_cannot_be_in_session_execution_ready():
    manifest = _manifest(
        "20260417T180000_github-actions-overlay-us",
        started_at="2026-04-17T18:00:00+00:00",
        market_session_phase="regular_session",
        portfolio_status="success",
        total_tickers=16,
        execution_data_quality="DELAYED_ANALYSIS_ONLY",
    )

    assert _run_phase_label(manifest) == "delayed_analysis_only"
    assert _run_phase_label(manifest) != "in_session"


def test_homepage_representative_run_prefers_same_cohort():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        archive_dir = root / "archive"
        site_dir = root / "site"
        watchlist = _manifest(
            "20260418T010000_github-actions-overlay-us",
            started_at="2026-04-18T01:00:00+00:00",
            market_session_phase="regular_session",
            portfolio_status="disabled",
            total_tickers=8,
            degraded_count=0,
        )
        account_aware = _manifest(
            "20260418T020000_github-actions-overlay-us",
            started_at="2026-04-18T02:00:00+00:00",
            market_session_phase="delayed_analysis_only",
            portfolio_status="success",
            total_tickers=16,
            degraded_count=16,
            execution_data_quality="DELAYED_ANALYSIS_ONLY",
        )
        _write_run(archive_dir / "runs" / "2026" / watchlist["run_id"], watchlist)
        _write_run(archive_dir / "runs" / "2026" / account_aware["run_id"], account_aware)

        build_site(archive_dir, site_dir, SiteSettings(title="TA", subtitle="Daily"))
        html = (site_dir / "index.html").read_text(encoding="utf-8")

    assert account_aware["run_id"] in html
    assert html.index(account_aware["run_id"]) < html.index(watchlist["run_id"])
    assert "Delayed analysis only" in html


def test_post_close_overlay_not_labeled_in_session():
    manifest = _manifest(
        "20260418T055952_github-actions-overlay-us",
        started_at="2026-04-18T05:59:52+00:00",
        market_session_phase="post_close",
        portfolio_status="success",
        total_tickers=16,
    )

    assert _run_phase_label(manifest) == "post_close"
    assert _run_phase_label(manifest) != "in_session"
