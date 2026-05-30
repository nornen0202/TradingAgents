from __future__ import annotations

from pathlib import Path

from tradingagents.scheduled.config import SiteSettings
from tradingagents.scheduled.site import _render_run_page


def test_run_page_explains_when_no_microstructure_checkpoint_was_due(tmp_path: Path):
    manifest = {
        "_run_dir": str(tmp_path),
        "run_id": "run",
        "status": "success",
        "started_at": "2026-05-30T16:26:18+09:00",
        "settings": {"output_language": "Korean"},
        "summary": {"successful_tickers": 1, "failed_tickers": 0},
        "execution": {
            "artifacts": {},
            "overlay_phase": {"selected_checkpoints": []},
            "notes": ["No execution checkpoint is due yet; this run is a pre-open snapshot."],
        },
        "tickers": [],
    }

    html = _render_run_page(manifest, SiteSettings())

    assert "장중 실행 컨텍스트" in html
    assert "microstructure 파일이 새로 생성되지 않았습니다" in html
    assert "No execution checkpoint is due yet" in html
