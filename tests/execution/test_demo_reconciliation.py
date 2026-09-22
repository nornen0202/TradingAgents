import pytest
import requests

from test_kis_demo import args, client, ack, Response
from tradingagents.execution.kis_demo import DemoError, DemoOrderJournal, RequestPacer


def report(*, filled=1, remaining=1, **changes):
    return Response(
        {
            "rt_cd": "0",
            "output1": [
                {
                    "odno": "123",
                    "ord_qty": "2",
                    "tot_ccld_qty": str(filled),
                    "rmn_qty": str(remaining),
                    "cncl_yn": "N",
                    "pdno": "005930",
                    "sll_buy_dvsn_cd": "02",
                    "ord_unpr": "70000",
                    **changes,
                }
            ],
        }
    )


@pytest.mark.parametrize(
    "change",
    [
        {"pdno": "000660"},
        {"sll_buy_dvsn_cd": "01"},
        {"ord_qty": "3"},
        {"ord_unpr": "71000"},
    ],
)
def test_broker_terms_must_match_persisted_intent(tmp_path, change):
    c, _ = client(ack(), report(**change))
    j = DemoOrderJournal(tmp_path / "journal.sqlite", c)
    try:
        j.submit(**args())
        with pytest.raises(DemoError, match="invalid fill"):
            j.reconcile(intent_id="intent-1", trade_date="20260921")
        other = {**args(), "intent_id": "intent-2"}
        with pytest.raises(DemoError, match="ambiguous"):
            j.submit(**other)
        body = j.db.execute("SELECT body FROM intents").fetchone()[0]
        assert "12345678" not in body and "app" not in body.lower()
    finally:
        j.close()


def test_duplicate_observations_do_not_add_fills_and_regression_blocks(tmp_path):
    c, _ = client(ack(), report(), report(), report(filled=0, remaining=2))
    path = tmp_path / "journal.sqlite"
    j = DemoOrderJournal(path, c)
    j.submit(**args())
    j.reconcile(intent_id="intent-1", trade_date="20260921")
    j.close()
    j = DemoOrderJournal(path, c)
    try:
        j.reconcile(intent_id="intent-1", trade_date="20260921")
        assert j.db.execute("SELECT filled FROM order_state").fetchone()[0] == 1
        with pytest.raises(DemoError, match="regressed"):
            j.reconcile(intent_id="intent-1", trade_date="20260921")
        assert j.db.execute("SELECT filled FROM order_state").fetchone()[0] == 1
        assert (
            j.db.execute("SELECT count(*) FROM reconciliation_issues").fetchone()[0]
            == 1
        )
    finally:
        j.close()


def test_unknown_new_order_does_not_prevent_cancelling_known_order(tmp_path):
    c, s = client(ack(), requests.Timeout(), report(), ack())
    j = DemoOrderJournal(tmp_path / "journal.sqlite", c)
    try:
        j.submit(**args())
        assert j.submit(**{**args(), "intent_id": "intent-2"})["status"] == "UNKNOWN"
        assert (
            j.cancel(intent_id="intent-1", trade_date="20260921", now=args()["now"])[
                "status"
            ]
            == "ACKNOWLEDGED"
        )
        calls = len(s.calls)
        # A second cancellation returns the persisted receipt, even without a fresh order query.
        assert (
            j.cancel(intent_id="intent-1", trade_date="20260921", now=args()["now"])[
                "status"
            ]
            == "ACKNOWLEDGED"
        )
        assert len(s.calls) == calls
        with pytest.raises(DemoError, match="ambiguous"):
            j.submit(**{**args(), "intent_id": "intent-3"})
    finally:
        j.close()


def test_throttle_spacing_and_expiry_rechecked_before_network(tmp_path):
    clock = [0.0]

    def advance(seconds):
        clock[0] += seconds

    pacer = RequestPacer(clock=lambda: clock[0], sleep=advance)
    pacer.wait()
    pacer.wait()
    pacer.wait()
    assert clock[0] == pytest.approx(2.2)
    c, s = client(ack())
    from datetime import datetime

    c.utcnow = lambda: datetime.fromisoformat(args()["valid_until"])
    j = DemoOrderJournal(tmp_path / "journal.sqlite", c)
    try:
        assert j.submit(**args())["status"] == "UNKNOWN"
        assert len(s.calls) == 1  # Authentication only, no order POST after expiry.
    finally:
        j.close()


def test_missing_order_blocks_until_verified_again_and_terminal_state_cannot_reopen(
    tmp_path,
):
    c, _ = client(
        ack(),
        Response({"rt_cd": "0", "output1": []}),
        report(filled=2, remaining=0),
        report(),
    )
    j = DemoOrderJournal(tmp_path / "journal.sqlite", c)
    try:
        j.submit(**args())
        assert (
            j.reconcile(intent_id="intent-1", trade_date="20260921")["status"]
            == "UNRESOLVED"
        )
        assert (
            j.db.execute("SELECT count(*) FROM reconciliation_issues").fetchone()[0]
            == 1
        )
        assert (
            j.reconcile(intent_id="intent-1", trade_date="20260921")["status"]
            == "FILLED"
        )
        assert (
            j.db.execute("SELECT count(*) FROM reconciliation_issues").fetchone()[0]
            == 0
        )
        with pytest.raises(DemoError, match="regressed"):
            j.reconcile(intent_id="intent-1", trade_date="20260921")
        assert j.db.execute("SELECT status FROM order_state").fetchone()[0] == "FILLED"
    finally:
        j.close()
