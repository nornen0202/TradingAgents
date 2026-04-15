from datetime import datetime

from tradingagents.scheduled.runner import _select_due_checkpoints
from tradingagents.scheduled.site import _execution_badge_label


def test_preopen_phase_when_no_checkpoint_due():
    selected, phase = _select_due_checkpoints(
        now_kst=datetime(2026, 4, 15, 22, 10),
        checkpoints=["22:35", "22:50", "23:30"],
    )
    assert selected == []
    assert phase == "PRE_OPEN"


def test_preopen_badge_label_for_unrefreshed_snapshot():
    assert _execution_badge_label({"ticker": "AAPL", "status": "success"}) == "PRE_OPEN SNAPSHOT"
