import json
import tempfile
from pathlib import Path

from tradingagents.scheduled.config import SiteSettings
from tradingagents.scheduled.site import build_site


def _write_run(archive_dir: Path, payload: dict) -> None:
    run_dir = archive_dir / "runs" / "2026" / payload["run_id"]
    run_dir.mkdir(parents=True, exist_ok=True)
    for ticker in payload.get("tickers", []):
        ticker_dir = run_dir / "tickers" / ticker["ticker"]
        ticker_dir.mkdir(parents=True, exist_ok=True)
        (ticker_dir / "analysis.json").write_text("{}", encoding="utf-8")
        (ticker_dir / "final_state.json").write_text("{}", encoding="utf-8")
    (run_dir / "run.json").write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def _decision(trigger: str) -> str:
    return json.dumps(
        {
            "rating": "NO_TRADE",
            "portfolio_stance": "BULLISH",
            "entry_action": "WAIT",
            "setup_quality": "DEVELOPING",
            "confidence": 0.7,
            "time_horizon": "medium",
            "entry_logic": "조건 확인",
            "exit_logic": "이탈시 관찰",
            "position_sizing": "분할",
            "risk_limits": "손절",
            "watchlist_triggers": [trigger],
            "catalysts": [],
            "invalidators": [],
            "data_coverage": {
                "company_news_count": 3,
                "disclosures_count": 1,
                "social_source": "dedicated",
                "macro_items_count": 1,
            },
        },
        ensure_ascii=False,
    )


def test_run_timeline_and_ticker_delta_cards():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        archive = root / "archive"
        site = root / "site"

        run1 = {
            "version": 1,
            "run_id": "20260417T041713_github-actions-overlay-us",
            "status": "success",
            "started_at": "2026-04-17T04:17:13+00:00",
            "finished_at": "2026-04-17T04:18:00+00:00",
            "settings": {"output_language": "Korean", "market": "us"},
            "summary": {"total_tickers": 1, "successful_tickers": 1, "failed_tickers": 0},
            "portfolio": {"status": "disabled"},
            "tickers": [
                {
                    "ticker": "NVDA",
                    "ticker_name": "NVIDIA",
                    "status": "success",
                    "analysis_date": "2026-04-17",
                    "trade_date": "2026-04-17",
                    "decision": _decision("종가 260 상회"),
                    "artifacts": {
                        "analysis_json": "tickers/NVDA/analysis.json",
                        "final_state_json": "tickers/NVDA/final_state.json",
                    },
                    "execution_update": {"decision_state": "WAIT"},
                }
            ],
            "execution": {"overlay_phase": {"name": "CHECKPOINT_13_17"}, "degraded": []},
        }
        run2 = {
            "version": 1,
            "run_id": "20260417T044622_github-actions-overlay-us",
            "status": "success",
            "started_at": "2026-04-17T04:46:22+00:00",
            "finished_at": "2026-04-17T04:47:00+00:00",
            "settings": {"output_language": "Korean", "market": "us"},
            "summary": {"total_tickers": 1, "successful_tickers": 1, "failed_tickers": 0},
            "portfolio": {"status": "disabled"},
            "tickers": [
                {
                    "ticker": "NVDA",
                    "ticker_name": "NVIDIA",
                    "status": "success",
                    "analysis_date": "2026-04-17",
                    "trade_date": "2026-04-17",
                    "decision": _decision("종가 266.43 상회"),
                    "artifacts": {
                        "analysis_json": "tickers/NVDA/analysis.json",
                        "final_state_json": "tickers/NVDA/final_state.json",
                    },
                    "execution_update": {"decision_state": "ACTIONABLE_NOW"},
                }
            ],
            "execution": {"overlay_phase": {"name": "CHECKPOINT_13_46"}, "degraded": []},
        }
        _write_run(archive, run1)
        _write_run(archive, run2)

        build_site(archive, site, SiteSettings(title="TA", subtitle="Daily"))
        run_html = (site / "runs" / run2["run_id"] / "index.html").read_text(encoding="utf-8")
        ticker_html = (site / "runs" / run2["run_id"] / "NVDA.html").read_text(encoding="utf-8")

    assert "동일 세션 timeline" in run_html
    assert run1["run_id"] in run_html
    assert run2["run_id"] in run_html
    assert "직전 run 대비 종목 변화" in ticker_html
    assert "Today 변화" in ticker_html
