import json
from pathlib import Path

from tradingagents.scheduled.config import SiteSettings
from tradingagents.scheduled.site import build_site


def test_portfolio_page_publishes_summary_image(tmp_path: Path):
    archive_dir = tmp_path / "archive"
    site_dir = tmp_path / "site"
    run_id = "20260426T013659_github-actions-us"
    run_dir = archive_dir / "runs" / "2026" / run_id
    private_dir = run_dir / "portfolio-private"
    private_dir.mkdir(parents=True)
    (private_dir / "portfolio_report.md").write_text("# Portfolio\n\nbody", encoding="utf-8")
    (private_dir / "summary_card.svg").write_text("<svg><text>summary image</text></svg>", encoding="utf-8")
    (private_dir / "status.json").write_text(
        json.dumps(
            {
                "status": "success",
                "profile": "us_kis_default",
                "snapshot_health": "VALID",
                "generated_at": "2026-04-26T01:40:00+00:00",
                "artifacts": {
                    "portfolio_report_md": "portfolio-private/portfolio_report.md",
                    "summary_card_svg": "portfolio-private/summary_card.svg",
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (run_dir / "run.json").write_text(
        json.dumps(
            {
                "version": 1,
                "run_id": run_id,
                "status": "success",
                "started_at": "2026-04-26T01:36:59+00:00",
                "finished_at": "2026-04-26T01:40:00+00:00",
                "summary": {"total_tickers": 1, "successful_tickers": 1, "failed_tickers": 0},
                "settings": {"output_language": "Korean", "market": "US", "summary_image_publish_to_site": True},
                "portfolio": {
                    "status": "success",
                    "profile": "us_kis_default",
                    "artifacts": {
                        "portfolio_report_md": "portfolio-private/portfolio_report.md",
                        "summary_card_svg": "portfolio-private/summary_card.svg",
                    },
                },
                "tickers": [],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    build_site(archive_dir, site_dir, SiteSettings(title="TA", subtitle="Daily"))

    portfolio_html = (site_dir / "runs" / run_id / "portfolio.html").read_text(encoding="utf-8")
    assert "요약 이미지" in portfolio_html
    assert "summary_card.svg" in portfolio_html
    assert (site_dir / "downloads" / run_id / "portfolio" / "summary_card.svg").exists()
