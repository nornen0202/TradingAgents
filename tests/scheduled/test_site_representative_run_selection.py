from tradingagents.scheduled.site import _run_category, _select_representative_run


def _manifest(
    run_id: str,
    *,
    started_at: str,
    total: int,
    successful: int,
    failed: int,
    portfolio_status: str = "success",
    market: str = "US",
) -> dict:
    return {
        "run_id": run_id,
        "status": "success" if failed == 0 else "partial_failure",
        "started_at": started_at,
        "market_session_phase": "regular_session",
        "settings": {"market": market},
        "summary": {"total_tickers": total, "successful_tickers": successful, "failed_tickers": failed},
        "execution": {
            "overlay_phase": {"name": "REGULAR_SESSION"},
            "execution_data_quality": "REALTIME_EXECUTION_READY",
            "market_data_quality_counts": {"REALTIME_EXECUTION_READY": total},
            "degraded": [],
        },
        "portfolio": {
            "status": portfolio_status,
            "profile": "account",
            "artifacts": {"portfolio_report_json": "portfolio-private/portfolio_report.json"},
        },
        "tickers": [],
    }


def test_representative_run_excludes_high_failure_rate():
    stale_partial = _manifest(
        "20260430T201627_github-actions-us",
        started_at="2026-04-30T20:16:27+00:00",
        total=31,
        successful=18,
        failed=13,
    )
    successful = _manifest(
        "20260509T061435_github-actions-us",
        started_at="2026-05-09T06:14:35+00:00",
        total=31,
        successful=31,
        failed=0,
    )

    selected = _select_representative_run([stale_partial, successful])

    assert selected is successful
    assert _run_category(stale_partial) == "TECHNICAL_ARCHIVE"


def test_representative_run_prefers_recent_successful_account_report():
    older = _manifest(
        "20260508T061435_github-actions-us",
        started_at="2026-05-08T06:14:35+00:00",
        total=31,
        successful=31,
        failed=0,
    )
    newer = _manifest(
        "20260509T061435_github-actions-us",
        started_at="2026-05-09T06:14:35+00:00",
        total=31,
        successful=31,
        failed=0,
    )

    selected = _select_representative_run([newer, older])

    assert selected is newer
