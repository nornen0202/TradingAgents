from __future__ import annotations

import importlib.util
import json
from pathlib import Path


def _load_verifier():
    path = Path(__file__).resolve().parents[1] / ".github" / "scripts" / "verify_account_performance_site.py"
    spec = importlib.util.spec_from_file_location("verify_account_performance_site", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write_feed(site_dir: Path, runs: list[dict[str, object]]) -> None:
    site_dir.mkdir(parents=True, exist_ok=True)
    (site_dir / "feed.json").write_text(json.dumps({"runs": runs}), encoding="utf-8")


def test_select_run_ignores_newer_unpublished_history(tmp_path: Path) -> None:
    verifier = _load_verifier()
    site_dir = tmp_path / "site"
    published_id = "20260716T010000_github-actions-portfolio-kr"
    published_url = f"runs/{published_id}/index.html"
    (site_dir / published_url).parent.mkdir(parents=True)
    (site_dir / published_url).write_text("published", encoding="utf-8")
    _write_feed(
        site_dir,
        [
            {
                "run_id": "20260716T020000_unpublished",
                "label": "github-actions-portfolio-kr",
                "started_at": "2026-07-16T02:00:00+09:00",
                "settings": {"market": "KR", "run_mode": "portfolio_only"},
                "published_to_site": False,
                "run_url": None,
            },
            {
                "run_id": published_id,
                "label": "github-actions-portfolio-kr",
                "started_at": "2026-07-16T01:00:00+09:00",
                "settings": {"market": "KR", "run_mode": "portfolio_only"},
                "published_to_site": True,
                "run_url": published_url,
            },
        ],
    )

    selected = verifier._select_run(
        site_dir=site_dir,
        market="kr",
        run_label="github-actions-portfolio-kr",
    )

    assert selected["run_id"] == published_id


def test_select_run_rejects_feed_entry_without_published_file(tmp_path: Path) -> None:
    verifier = _load_verifier()
    site_dir = tmp_path / "site"
    _write_feed(
        site_dir,
        [
            {
                "run_id": "20260716T010000_missing",
                "label": "github-actions-portfolio-us",
                "started_at": "2026-07-16T01:00:00+09:00",
                "settings": {"market": "US", "run_mode": "portfolio_only"},
                "published_to_site": True,
                "run_url": "runs/20260716T010000_missing/index.html",
            }
        ],
    )

    try:
        verifier._select_run(
            site_dir=site_dir,
            market="us",
            run_label="github-actions-portfolio-us",
        )
    except AssertionError as exc:
        assert "No portfolio_only US run found" in str(exc)
    else:  # pragma: no cover - defensive test failure branch
        raise AssertionError("Verifier selected an unpublished/missing run page.")
