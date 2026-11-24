from collections import Counter
from datetime import datetime, timezone
import json

import pandas as pd

from tradingagents.eval.archive_backtest import run_archive_backtest


def _run(archive, clock, label, rows, *, recovery=False, mode="full"):
    run_id = f"20241114T{clock}_{label}"
    folder = archive / "runs" / "2024" / run_id
    folder.mkdir(parents=True)
    payload = {"run_id": run_id, "status": "partial_failure", "settings": {"market": "US", "run_mode": mode},
               "started_at": "2024-11-14T10:00:00Z", "finished_at": "2024-11-14T14:00:00Z", "tickers": rows}
    if recovery:
        payload["research_recovery"] = {"source_run_id": "first"}
    (folder / "run.json").write_text(json.dumps(payload), encoding="utf-8")


def test_archive_cli_evidence_keeps_new_retry_judgments_and_uses_public_clock(tmp_path):
    archive = tmp_path / "archive"
    original = {"ticker": "AAPL", "trade_date": "2024-11-13", "analysis_date": "2024-11-14", "status": "success",
                "started_at": "2024-11-14T10:00:00Z", "finished_at": "2024-11-14T12:00:00Z",
                "decision": {"rating": "BUY", "entry_action": "WAIT", "conditional_entry_action": "ADD"}}
    _run(archive, "100000", "full", [original])
    duplicate = {**original, "research_reuse": {"source_run_id": "first"}}
    retry = {**original, "ticker": "MSFT", "decision": {"rating": "BUY", "entry_action": "STARTER"}}
    _run(archive, "110000", "retry", [duplicate, retry], recovery=True)
    _run(archive, "120000", "overlay_only", [original], mode="overlay_only")
    requested = Counter()

    def fetch(symbol, start, end):
        requested[symbol] += 1
        # Premarket completion on the 14th is eligible for the 14th open.
        return pd.DataFrame({"Open": [100, 101], "Close": [100, 110 if symbol != "SPY" else 105]},
                            index=pd.to_datetime(["2024-11-14", "2024-11-15"]))

    path, result = run_archive_backtest(
        archive, "2024-10-14", "2024-11-14", tmp_path, holding=1, fee_bps=10,
        as_of=datetime(2024, 11, 18, tzinfo=timezone.utc), run_id="fixture", fetch=fetch)
    assert path.is_file()
    assert result["manifest"]["archive_inventory"]["오버레이 실행"] == 1
    assert result["manifest"]["archive_inventory"]["재시도에서 복사·재발행된 행"] == 1
    assert result["direction"]["scored"] == 2
    assert result["new_exposure"]["statuses"] == {"NO_NEW_EXPOSURE": 1, "SCORED": 1}
    assert all(group["direction"]["target"] == 0 for group in result["archive_groups"] if group["month"] == "2024-10")
    assert all(row["direction"]["entry_session"] == "2024-11-14" for row in result["records"])
    assert requested == {"AAPL": 1, "MSFT": 1, "SPY": 1}
    _, replayed = run_archive_backtest(
        archive, "2024-10-14", "2024-11-14", tmp_path, holding=1, fee_bps=10,
        as_of=datetime(2024, 11, 18, tzinfo=timezone.utc), run_id="reproduced",
        price_snapshot=path.with_name("price-inputs.json"))
    assert result == replayed
