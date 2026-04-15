from tradingagents.scheduled.config import _default_execution_checkpoints_kst


def test_us_default_checkpoints_are_three_kst_times():
    checkpoints = _default_execution_checkpoints_kst("US")
    assert len(checkpoints) == 3
    assert all(len(value) == 5 and value[2] == ":" for value in checkpoints)


def test_kr_default_checkpoints_match_operational_profile():
    assert _default_execution_checkpoints_kst("KR") == ("09:20", "12:00", "15:40")
