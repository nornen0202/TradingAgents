from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from tradingagents.scheduled.account_site import PUBLIC_ACCOUNT_SCHEMA, build_public_account_site
from tradingagents.scheduled.config import load_scheduled_config
from tradingagents.scheduled.site import _render_index_page


def _manifest(archive: Path, *, market: str, run_id: str, account_id: str) -> dict:
    run_dir = archive / "runs" / "2026" / run_id
    private_dir = run_dir / "portfolio-private"
    private_dir.mkdir(parents=True)
    (private_dir / "account_snapshot.json").write_text(
        json.dumps(
            {
                "snapshot_id": f"20260813_kis_{account_id}",
                "account_id": account_id,
                "as_of": "2026-08-13T08:30:00+09:00",
                "snapshot_health": "VALID",
                "settled_cash_krw": 100_000,
                "available_cash_krw": 90_000,
                "buying_power_krw": 80_000,
                "total_equity_krw": 1_410_000,
                "pending_orders": [{"broker_order_id": "ODNO-SECRET"}],
                "positions": [
                    {
                        "broker_symbol": "NVDA" if market == "US" else "005930",
                        "canonical_ticker": "NVDA" if market == "US" else "005930.KS",
                        "display_name": "엔비디아" if market == "US" else "삼성전자",
                        "quantity": 6,
                        "available_qty": 5,
                        "avg_cost_krw": 200_000,
                        "market_price_krw": 220_000,
                        "market_value_krw": 1_320_000,
                        "unrealized_pnl_krw": 120_000,
                    }
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return {
        "_run_dir": str(run_dir),
        "run_id": run_id,
        "settings": {"market": market},
        "started_at": "2026-08-13T08:30:00+09:00",
    }


def test_public_account_site_separates_markets_and_excludes_identifiers(tmp_path: Path) -> None:
    archive = tmp_path / "archive"
    site = tmp_path / "site"
    manifests = [
        _manifest(archive, market="KR", run_id="20260813T083000_kr", account_id="12345678-01"),
        _manifest(archive, market="US", run_id="20260813T083000_us", account_id="87654321-01"),
    ]

    payload = build_public_account_site(
        site_dir=site,
        manifests=manifests,
        public_base_url="https://example.test/TradingAgents",
    )

    assert payload["schema"] == PUBLIC_ACCOUNT_SCHEMA
    assert payload["markets"]["kr"]["positions"][0]["ticker"] == "005930.KS"
    assert payload["markets"]["us"]["positions"][0]["ticker"] == "NVDA"
    assert payload["markets"]["us"]["positions"][0]["unrealized_return_pct"] == 10.0
    assert payload["markets"]["us"]["summary"]["total_market_value_krw"] == 1_320_000

    published = (site / "account" / "public.json").read_text(encoding="utf-8")
    html = (site / "account" / "index.html").read_text(encoding="utf-8")
    assert "12345678-01" not in published
    assert "87654321-01" not in published
    assert "ODNO-SECRET" not in published
    assert "snapshot_id" not in published
    assert "pending_orders" not in published
    assert "엔비디아" in html
    assert "삼성전자" in html
    assert "public.json" in html
    (site / "index.html").write_text('<a href="account/index.html">Account</a>', encoding="utf-8")

    subprocess.check_call(
        [
            sys.executable,
            ".github/scripts/verify_public_account_site.py",
            "--site-dir",
            str(site),
            "--require-markets",
            "all",
        ]
    )


def test_public_account_site_falls_back_to_older_valid_snapshot(tmp_path: Path) -> None:
    archive = tmp_path / "archive"
    invalid = _manifest(archive, market="KR", run_id="20260814T083000_kr", account_id="12345678-01")
    invalid_path = Path(invalid["_run_dir"]) / "portfolio-private" / "account_snapshot.json"
    payload = json.loads(invalid_path.read_text(encoding="utf-8"))
    payload["snapshot_health"] = "INVALID_SNAPSHOT"
    invalid_path.write_text(json.dumps(payload), encoding="utf-8")
    valid = _manifest(archive, market="KR", run_id="20260813T083000_kr", account_id="12345678-01")

    result = build_public_account_site(site_dir=tmp_path / "site", manifests=[invalid, valid])

    assert result["markets"]["kr"]["run_id"] == "20260813T083000_kr"
    assert result["markets"]["us"]["status"] == "unavailable"


def test_repository_daily_configs_explicitly_enable_public_account_snapshot() -> None:
    for path in (Path("config/scheduled_analysis.toml"), Path("config/scheduled_analysis_korea.toml")):
        config = load_scheduled_config(path)
        assert config.site.publish_account_snapshot is True

    workflow = Path(".github/workflows/daily-codex-analysis.yml").read_text(encoding="utf-8")
    assert "Verify public account snapshot page" in workflow
    assert ".github/scripts/verify_public_account_site.py" in workflow
    assert '"${{ needs.schedule_gate.outputs.profile }}"' in workflow


def test_homepage_links_to_public_account_page_when_enabled() -> None:
    from tradingagents.scheduled.config import SiteSettings

    html = _render_index_page([], SiteSettings(publish_account_snapshot=True))

    assert 'href="account/index.html"' in html
