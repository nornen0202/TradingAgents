from collections import Counter
from datetime import datetime, timezone
import json

import pandas as pd

from tradingagents.eval.archive_backtest import run_archive_backtest


def _run(archive, clock, label, rows, *, recovery=False, mode="full"):
    run_id = f"20261112T{clock}_{label}"
    folder = archive / "runs" / "2026" / run_id
    folder.mkdir(parents=True)
    payload = {"run_id": run_id, "status": "partial_failure", "settings": {"market": "US", "run_mode": mode},
               "started_at": "2026-11-12T10:00:00Z", "finished_at": "2026-11-12T14:00:00Z", "tickers": rows}
    if recovery:
        payload["research_recovery"] = {"source_run_id": "first"}
    (folder / "run.json").write_text(json.dumps(payload), encoding="utf-8")


def test_archive_cli_evidence_keeps_new_retry_judgments_and_uses_public_clock(tmp_path):
    archive = tmp_path / "archive"
    original = {"ticker": "AAPL", "trade_date": "2026-11-11", "analysis_date": "2026-11-12", "status": "success",
                "started_at": "2026-11-12T10:00:00Z", "finished_at": "2026-11-12T12:00:00Z",
                "decision": {"rating": "BUY", "entry_action": "WAIT", "conditional_entry_action": "ADD"}}
    _run(archive, "100000", "full", [original])
    duplicate = {**original, "research_reuse": {"source_run_id": "first"}}
    retry = {**original, "ticker": "MSFT", "decision": {"rating": "BUY", "entry_action": "STARTER"}}
    _run(archive, "110000", "retry", [duplicate, retry], recovery=True)
    _run(archive, "120000", "overlay_only", [original], mode="overlay_only")
    requested = Counter()

    def fetch(symbol, start, end):
        requested[symbol] += 1
        # Premarket completion on the 12th is eligible for the 12th open.
        return pd.DataFrame({"Open": [100, 101], "Close": [100, 110 if symbol != "SPY" else 105]},
                            index=pd.to_datetime(["2026-11-12", "2026-11-13"]))

    path, result = run_archive_backtest(
        archive, "2026-11-12", "2026-11-12", tmp_path, holding=1, fee_bps=10,
        as_of=datetime(2026, 11, 16, tzinfo=timezone.utc), run_id="fixture", fetch=fetch)
    assert path.is_file()
    assert result["manifest"]["archive_inventory"]["오버레이 실행"] == 1
    assert result["manifest"]["archive_inventory"]["재시도에서 복사·재발행된 행"] == 1
    assert result["direction"]["scored"] == 2
    assert result["new_exposure"]["statuses"] == {"NO_NEW_EXPOSURE": 1, "SCORED": 1}
    assert all(row["direction"]["entry_session"] == "2026-11-12" for row in result["records"])
    assert requested == {"AAPL": 1, "MSFT": 1, "SPY": 1}
    _, replayed = run_archive_backtest(
        archive, "2026-11-12", "2026-11-12", tmp_path, holding=1, fee_bps=10,
        as_of=datetime(2026, 11, 16, tzinfo=timezone.utc), run_id="reproduced",
        price_snapshot=path.with_name("price-inputs.json"))
    assert result == replayed
