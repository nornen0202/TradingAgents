import json
from datetime import datetime, timedelta

from tradingagents.scheduled import runner
from tradingagents.scheduled.config import load_scheduled_config


def test_completion_clock_includes_portfolio_work_across_midnight(monkeypatch, tmp_path):
    instant = datetime.fromisoformat("2026-09-30T23:40:00+09:00")

    class Clock(datetime):
        @classmethod
        def now(cls, tz=None):
            return instant.astimezone(tz) if tz else instant.replace(tzinfo=None)

    def portfolio_pipeline(**kwargs):
        nonlocal instant
        assert kwargs["manifest"]["ticker_phase_finished_at"] == instant.isoformat()
        instant += timedelta(minutes=30)
        return {"status": "success"}

    config_path = tmp_path / "scheduled.toml"
    config_path.write_text(
        '[run]\ntickers=["AAPL"]\nrun_mode="portfolio_only"\ntimezone="Asia/Seoul"\n'
        '[storage]\narchive_dir="./archive"\nsite_dir="./site"\n'
        '[portfolio]\nenabled=true\nprofile_path="./profile.toml"\nprofile_name="test"\n',
        encoding="utf-8",
    )
    monkeypatch.setattr(runner, "datetime", Clock)
    monkeypatch.setattr(runner, "run_portfolio_pipeline", portfolio_pipeline)
    config = load_scheduled_config(config_path)
    manifest = runner.execute_scheduled_run(config, run_label="clock-test", skip_site_build=True)
    assert manifest["ticker_phase_finished_at"] == "2026-09-30T23:40:00+09:00"
    assert manifest["finished_at"] == "2026-10-01T00:10:00+09:00"
    assert manifest["duration_seconds"] == 1800
    assert manifest["postprocessing_duration_seconds"] == 1800
    saved = json.loads((config.storage.archive_dir / "latest-run.json").read_text(encoding="utf-8"))
    archived = json.loads((config.storage.archive_dir / "runs/2026" / manifest["run_id"] / "run.json").read_text(encoding="utf-8"))
    assert saved["finished_at"] == archived["finished_at"] == manifest["finished_at"]
