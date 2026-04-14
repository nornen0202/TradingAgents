import json
from pathlib import Path

from tradingagents.execution.selective_rerun import collect_event_signals, find_selective_rerun_targets


class _State:
    def __init__(self, value: str):
        self.value = value


class _Update:
    def __init__(self, state: str):
        self.decision_state = _State(state)


class _Guard:
    requires_post_event_rerun = True


class _Contract:
    def __init__(self):
        self.event_guard = _Guard()


def test_collect_event_signals_detects_keywords(tmp_path: Path):
    run_dir = tmp_path
    ticker_dir = run_dir / "tickers" / "TSM"
    ticker_dir.mkdir(parents=True)
    analysis_path = ticker_dir / "analysis.json"
    analysis_path.write_text(
        json.dumps({"decision": "Earnings soon and guidance update expected"}, ensure_ascii=False),
        encoding="utf-8",
    )
    summaries = [
        {
            "ticker": "TSM",
            "status": "success",
            "artifacts": {"analysis_json": "tickers/TSM/analysis.json"},
        }
    ]

    import tradingagents.execution.selective_rerun as module

    original = module._fetch_fresh_headlines
    module._fetch_fresh_headlines = lambda _ticker: ""
    try:
        signals = collect_event_signals(run_dir=run_dir, ticker_summaries=summaries)
    finally:
        module._fetch_fresh_headlines = original

    assert signals["TSM"] == ["earnings", "guidance"]


def test_find_selective_rerun_targets_uses_event_and_invalidation():
    targets = find_selective_rerun_targets(
        contracts={"TSM": _Contract()},
        updates={"TSM": _Update("INVALIDATED")},
        event_signals={"TSM": ["earnings"]},
    )

    assert "TSM" in targets
    assert "overlay_invalidated" in targets["TSM"]
    assert "event:earnings" in targets["TSM"]
    assert "post_event_guard_rerun" in targets["TSM"]
