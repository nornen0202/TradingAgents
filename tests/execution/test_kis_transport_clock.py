"""A wall-clock rollback must not turn expired evidence into an eligible write."""
from datetime import datetime, timedelta, timezone

import pytest

from tradingagents.execution.kis_demo import DemoCredentials, DemoError, DemoOrderJournal, KisDemoClient, RequestPacer
from tradingagents.execution.kis_demo_us import KisDemoUSClient


@pytest.fixture(params=["KR", "US"])
def setup_transport(tmp_path, request):
    now = datetime(2026, 10, 19, 14, 0, tzinfo=timezone.utc)
    moment, calls, behavior = [now], [], [None]
    class Session:
        def request(self, method, url, **kwargs):
            calls.append((method, url, kwargs))
            if behavior[0]:
                behavior[0]()
            class Response:
                status_code = 200
                headers = {}
                def json(self):
                    return {"rt_cd": "0", "output": {"ODNO": "123"}}
            return Response()
        def close(self):
            pass
    cls = KisDemoClient if request.param == "KR" else KisDemoUSClient
    client = cls(DemoCredentials("fixture-key", "fixture-secret", "12345678", "01"),
                 session=Session(), pacer=RequestPacer(interval=0), utcnow=lambda: moment[0])
    client._token, client._expires = "fixture-token", now + timedelta(hours=1)
    journal = DemoOrderJournal(tmp_path / "orders.sqlite", client)
    body = {**client._account(), "PDNO": "AAPL", "ORD_QTY": "1", "OVRS_EXCG_CD": "NASD",
            "ORD_SVR_DVSN_CD": "0", "ORD_DVSN": "00", "OVRS_ORD_UNPR": "200.00"}
    endpoint, tr_id = ("order-cash", "VTTC0012U") if request.param == "KR" else ("order", "VTTT1002U")
    def submit():
        return journal._write_once("intent-1", endpoint, tr_id, body, now.isoformat(), deadline=(now + timedelta(seconds=90)).isoformat())
    yield client, journal, moment, calls, behavior, submit, now
    journal.close()


def test_clock_regresses_since_intent_validation_is_not_sent(setup_transport):
    _, _, moment, calls, _, submit, _ = setup_transport
    moment[0] -= timedelta(seconds=1)
    assert submit()["status"] == "NOT_SENT"
    assert not calls


def test_clock_regresses_during_authentication_is_not_sent(setup_transport):
    client, _, moment, calls, _, submit, _ = setup_transport
    def authenticate():
        moment[0] -= timedelta(seconds=1)
    client.authenticate = authenticate
    assert submit()["status"] == "NOT_SENT"
    assert not calls


def test_clock_regresses_during_pacing_is_not_sent(setup_transport):
    client, _, moment, calls, _, submit, _ = setup_transport
    def wait():
        moment[0] -= timedelta(seconds=1)
    client.pacer.wait = wait
    assert submit()["status"] == "NOT_SENT"
    assert not calls


def test_clock_regresses_after_post_is_unknown_and_not_resent(setup_transport):
    _, _, moment, calls, behavior, submit, now = setup_transport
    behavior[0] = lambda: moment.__setitem__(0, now - timedelta(seconds=1))
    assert submit()["status"] == "UNKNOWN"
    moment[0] = now
    assert submit()["status"] == "UNKNOWN"
    assert len(calls) == 1


def test_clock_becomes_naive_after_post_is_unknown(setup_transport):
    _, _, moment, calls, behavior, submit, now = setup_transport
    behavior[0] = lambda: moment.__setitem__(0, now.replace(tzinfo=None))
    assert submit()["status"] == "UNKNOWN"
    assert len(calls) == 1


def test_readback_regression_is_rejected(setup_transport):
    client, _, moment, calls, behavior, _, now = setup_transport
    behavior[0] = lambda: moment.__setitem__(0, now - timedelta(seconds=1))
    with pytest.raises(DemoError, match="regressed"):
        if isinstance(client, KisDemoUSClient):
            client.balance("NASD")
        else:
            client.balance()
    assert len(calls) == 1
