from datetime import datetime, timedelta

import pytest

from tradingagents.scheduled.runner import _microstructure_publication_metadata

NOW = datetime.fromisoformat("2026-10-23T01:00:00+09:00")


@pytest.mark.parametrize("stamp,live", [(None, False), ("", False), ("bad", False),
    ("2026-10-23T01:00:00", False), ((NOW+timedelta(microseconds=1)).isoformat(), False),
    ((NOW-timedelta(seconds=120)).isoformat(), False),
    ((NOW-timedelta(seconds=119.999)).isoformat(), True), (NOW.isoformat(), True),
    ("2026-10-22T16:00:00+00:00", True)])
def test_publication_uses_aware_original_clock_and_exclusive_expiry(stamp, live):
    row = _microstructure_publication_metadata(market_data_asof=stamp, market_session="regular",
        execution_data_quality="REALTIME", published_in_run_id="fixture", microstructure_source_run_id="fixture",
        analysis_source_run_id="original", generated_in_current_run=True, backfilled_from_run_id=None,
        published_at=NOW, max_data_age_seconds=120)
    assert (row["execution_eligibility"] == "LIVE_EXECUTION_READY") is live
    assert row["artifact_asof"] == stamp
    if stamp in {None, "", "bad", "2026-10-23T01:00:00", (NOW+timedelta(microseconds=1)).isoformat()}:
        assert row["artifact_age_seconds_at_publish"] is None
