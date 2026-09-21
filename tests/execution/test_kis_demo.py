import json

import pytest
import requests

from tradingagents.execution.kis_demo import (
    DemoCredentials,
    DemoError,
    DemoOrderJournal,
    KisDemoClient,
)
from tools.check_kis_demo import check


class Response:
    def __init__(self, payload, *, code=200, headers=None):
        self.payload, self.status_code, self.headers = payload, code, headers or {}

    def json(self):
        return self.payload


class Session:
    def __init__(self, *responses):
        self.responses, self.calls = list(responses), []

    def request(self, method, url, **kwargs):
        self.calls.append((method, url, kwargs))
        result = self.responses.pop(0)
        if isinstance(result, Exception):
            raise result
        return result

    def close(self):
        pass


def credentials(account="12345678"):
    return DemoCredentials("demo-key-test", "demo-secret-test", account, "01")


def client(*responses):
    s = Session(
        Response({"access_token": "token-test", "expires_in": 86400}), *responses
    )
    return KisDemoClient(credentials(), session=s), s


def args(**changes):
    return dict(
        intent_id="intent-1",
        ticker="005930",
        side="BUY",
        quantity=2,
        limit_price=70000,
        available_at="2026-09-21T10:00:00+09:00",
        valid_until="2026-09-21T10:02:00+09:00",
        now="2026-09-21T10:01:00+09:00",
        **changes,
    )


def ack():
    return Response(
        {"rt_cd": "0", "output": {"ODNO": "123", "KRX_FWDG_ORD_ORGNO": "001"}}
    )


def test_only_dedicated_demo_credentials_are_loaded(monkeypatch, tmp_path):
    from tradingagents.dataflows import api_keys

    p = tmp_path / "keys.json"
    p.write_text(json.dumps({"KIS_APP_KEY": "real", "KIS_APP_SECRET": "real"}))
    monkeypatch.setenv("TRADINGAGENTS_API_KEYS_PATH", str(p))
    for name in ("APP_KEY", "APP_SECRET", "ACCOUNT_NO", "PRODUCT_CODE"):
        monkeypatch.delenv("KIS_DEMO_" + name, raising=False)
        monkeypatch.delenv("KIS_VTS_" + name, raising=False)
    api_keys._load_documented_keys.cache_clear()
    assert check(connect=True)["status"] == "MISSING_DEMO_SETTINGS"
    with pytest.raises(DemoError):
        DemoCredentials.from_local_settings()
    p.write_text(
        json.dumps(
            {
                "KIS_DEMO_APP_KEY": "test",
                "KIS_DEMO_APP_SECRET": "test",
                "KIS_DEMO_ACCOUNT_NO": "12345678",
                "KIS_DEMO_PRODUCT_CODE": "01",
            }
        )
    )
    api_keys._load_documented_keys.cache_clear()
    assert DemoCredentials.from_local_settings().scope() == credentials().scope()
    assert "12345678" not in repr(DemoCredentials.from_local_settings())
    api_keys._load_documented_keys.cache_clear()


def test_ledger_ack_is_not_fill_and_restart_cannot_duplicate(tmp_path):
    c, s = client(ack())
    path = tmp_path / "journal.sqlite"
    journal = DemoOrderJournal(path, c)
    assert journal.submit(**args())["status"] == "ACKNOWLEDGED"
    journal.close()
    journal = DemoOrderJournal(path, c)
    assert journal.submit(**args())["status"] == "ACKNOWLEDGED"
    assert len(s.calls) == 2
    assert all(
        url.startswith("https://openapivts.koreainvestment.com:29443/")
        for _, url, _ in s.calls
    )
    assert s.calls[-1][2]["headers"]["tr_id"] == "VTTC0012U"
    assert s.calls[-1][2]["json"]["ORD_QTY"] == "2"
    assert all(not kw["allow_redirects"] for _, _, kw in s.calls)
    changed = args()
    changed["quantity"] = 3
    with pytest.raises(DemoError, match="different order"):
        journal.submit(**changed)
    journal.close()


def test_timeout_is_unknown_and_freezes_further_writes(tmp_path):
    c, s = client(requests.Timeout("sensitive-response"))
    journal = DemoOrderJournal(tmp_path / "journal.sqlite", c)
    assert journal.submit(**args())["status"] == "UNKNOWN"
    assert journal.submit(**args())["status"] == "UNKNOWN"
    newer = args()
    newer["intent_id"] = "intent-2"
    with pytest.raises(DemoError, match="ambiguous"):
        journal.submit(**newer)
    assert len(s.calls) == 2
    assert journal.reconcile(intent_id="intent-1", trade_date="20260921")[
        "requires_manual_reconciliation"
    ]
    journal.close()


def test_reconcile_partial_fill_then_cancel_is_not_assumed_filled(tmp_path):
    partial = Response(
        {
            "rt_cd": "0",
            "output1": [
                {
                    "odno": "123",
                    "ord_qty": "2",
                    "tot_ccld_qty": "1",
                    "rmn_qty": "1",
                    "cncl_yn": "N",
                }
            ],
        }
    )
    c, s = client(ack(), partial, partial, ack())
    journal = DemoOrderJournal(tmp_path / "journal.sqlite", c)
    journal.submit(**args())
    assert (
        journal.reconcile(intent_id="intent-1", trade_date="20260921")["status"]
        == "PARTIAL"
    )
    result = journal.cancel(
        intent_id="intent-1", trade_date="20260921", now=args()["now"]
    )
    assert result["status"] == "ACKNOWLEDGED"
    assert s.calls[-1][2]["json"]["ORD_QTY"] == "1"
    assert s.calls[-1][2]["headers"]["tr_id"] == "VTTC0013U"
    journal.close()


def test_paginated_orders_are_complete_and_loops_fail_closed():
    page = Response(
        {
            "rt_cd": "0",
            "output1": [{"odno": "1"}],
            "ctx_area_fk100": "a",
            "ctx_area_nk100": "b",
        },
        headers={"tr_cont": "M"},
    )
    c, s = client(page, Response({"rt_cd": "0", "output1": [{"odno": "2"}]}))
    assert len(c.orders("20260921")) == 2
    assert s.calls[-1][2]["headers"]["tr_cont"] == "N"
    c, _ = client(page, page)
    with pytest.raises(DemoError, match="pagination incomplete"):
        c.orders("20260921")


def test_real_transaction_id_and_cross_account_journal_rejected(tmp_path):
    c, s = client()
    with pytest.raises(DemoError, match="allowlist"):
        c.request("POST", "order-cash", "TTTC0012U", body=c._account())
    assert not s.calls
    p = tmp_path / "journal.sqlite"
    DemoOrderJournal(p, c).close()
    with pytest.raises(DemoError, match="another demo account"):
        DemoOrderJournal(p, KisDemoClient(credentials("87654321")))


def test_redirect_and_missing_read_rows_do_not_become_valid_accounts():
    c, _ = client(Response({}, code=302))
    with pytest.raises(DemoError, match="HTTP status 302"):
        c.balance()
    c, _ = client(Response({"rt_cd": "0"}))
    with pytest.raises(DemoError, match="missing rows"):
        c.balance()


def test_expired_intent_never_reaches_auth_or_order_endpoint(tmp_path):
    c, s = client()
    journal = DemoOrderJournal(tmp_path / "journal.sqlite", c)
    expired = args()
    expired["now"] = expired["valid_until"]
    with pytest.raises(DemoError, match="expired"):
        journal.submit(**expired)
    assert not s.calls
    journal.close()


@pytest.mark.parametrize(
    "payload,status",
    [
        ({"rt_cd": "1", "msg1": "private reason"}, "REJECTED"),
        ({"rt_cd": "0"}, "UNKNOWN"),
        ({"rt_cd": "0", "output": ["malformed"]}, "UNKNOWN"),
    ],
)
def test_rejected_and_ambiguous_receipts_never_become_fills(tmp_path, payload, status):
    c, s = client(Response(payload))
    journal = DemoOrderJournal(tmp_path / "journal.sqlite", c)
    assert journal.submit(**args()) == {"status": status}
    assert (
        "private reason"
        not in journal.db.execute("SELECT response FROM requests").fetchone()[0]
    )
    with pytest.raises(DemoError, match="date differs"):
        journal.reconcile(intent_id="intent-1", trade_date="20260922")
    assert len(s.calls) == 2
    journal.close()
