"""KIS VTS wire fixtures with generated keys, scopes, and zero network calls."""

import asyncio
import base64
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from decimal import Decimal
import json

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7
import pytest
from websockets.exceptions import ConnectionClosedError

from tradingagents.atomic_io import interprocess_file_lock
from tradingagents.execution.kis_vts_feed import (
    VtsFrameDecoder, VtsScope, run_event_feed, subscription_plan,
)

KR = VtsScope("KR", "local_fixture_kr", "0000000001")
US = VtsScope("US", "local_fixture_us", "0000000002")
NOW = datetime.fromisoformat("2026-07-01T10:00:05+09:00")
KEY = b"A" * 32
IV = b"B" * 16


def acknowledgement(tr, scope):
    return json.dumps({"header": {"tr_id": tr, "tr_key": scope.hts_id},
                       "body": {"rt_cd": "0", "output": {"key": KEY.decode(), "iv": IV.decode()}}})


def notice(tr, scope, number, *, account=None, original=""):
    width = 26 if scope.market == "KR" else 25
    fields = [scope.hts_id, scope.account if account is None else account, number, original] + [""] * (width - 4)
    pad = PKCS7(128).padder()
    plain = pad.update("^".join(fields).encode()) + pad.finalize()
    enc = Cipher(algorithms.AES(KEY), modes.CBC(IV)).encryptor()
    encrypted = base64.b64encode(enc.update(plain) + enc.finalize()).decode()
    return f"1|{tr}|001|{encrypted}"


def kr_quote(clock="100000", price="21000"):
    fields = [""] * 46
    fields[0], fields[1], fields[2], fields[33] = "009999", clock, price, "20260701"
    return "0|H0STCNT0|001|" + "^".join(fields)


def us_quote():
    fields = [""] * 26
    fields[0], fields[1], fields[6], fields[7], fields[11] = "DNASFIX", "FIX", "20260701", "100001", "125.50"
    return "0|HDFSCNT0|001|" + "^".join(fields)


def test_shared_subscription_budget_prioritizes_notices_orders_and_holdings():
    plan = subscription_plan((KR, US), active_orders=[("US", "DNASFIX")],
                             held=[("KR", "009999"), ("US", "DNASFIX")],
                             watchlist=[("KR", f"{i:06}") for i in range(100)])
    assert plan[:4] == (("H0STCNI9", KR.hts_id), ("H0GSCNI9", US.hts_id),
                        ("HDFSCNT0", "DNASFIX"), ("H0STCNT0", "009999"))
    assert len(plan) == 41
    with pytest.raises(ValueError, match="exceed"):
        subscription_plan((KR, US), held=[("KR", f"{i:06}") for i in range(40)])


@pytest.mark.parametrize(("market", "tr"), [("KR", "H0STCNI9"), ("US", "H0GSCNI9")])
def test_exact_notice_id_prefix_and_separate_rejected_and_accepted_receipts(market, tr):
    scope = VtsScope(market, "$fixture", "0000000001")
    assert subscription_plan((scope,)) == ((tr, "$fixture"),)
    with pytest.raises(ValueError, match="scope"):
        VtsScope(market, "fix$ture", scope.account)
    decoder = VtsFrameDecoder((scope,), subscription_plan((scope,)))
    denied = json.loads(acknowledgement(tr, scope))
    denied["body"] = {"rt_cd": "1", "msg1": "private broker data"}
    with pytest.raises(ValueError, match="not acknowledged"):
        decoder.control(json.dumps(denied), received_at=NOW)
    assert not decoder.notices_active
    denied_receipt = decoder.notice_controls[(tr, "1")]
    assert not denied_receipt.accepted
    assert denied_receipt.rt_cd == "1" and denied_receipt.received_at == NOW.isoformat()
    with pytest.raises(ValueError, match="Unexpected"):
        decoder.control(acknowledgement(tr, VtsScope(market, "fixture", scope.account)), received_at=NOW)
    assert len(decoder.notice_controls) == 1
    assert decoder.control(acknowledgement(tr, scope), received_at=NOW) is False
    assert decoder.notices_active and decoder.notice_controls[(tr, "0")].accepted
    assert all(value not in repr(decoder.notice_controls) for value in (scope.hts_id, scope.account, "private broker data"))


@pytest.mark.parametrize(("scope", "tr"), [(KR, "H0STCNI9"), (US, "H0GSCNI9")])
def test_acknowledged_notice_is_scoped_and_never_claims_a_fill(scope, tr):
    decoder = VtsFrameDecoder((scope,), subscription_plan((scope,)))
    frame = notice(tr, scope, "000000047", original="000000031")
    with pytest.raises(ValueError, match="before scoped"):
        decoder.events(frame, NOW)
    assert decoder.control(acknowledgement(tr, scope)) is False
    assert decoder.events(notice(tr, scope, "000000047", account="0000000066"), NOW) == ()
    event, = decoder.events(frame, NOW)
    assert event.order_number == "000000047"
    assert event.original_order_number == "000000031"
    assert not hasattr(event, "filled")
    assert scope.hts_id not in repr(event) and scope.account not in repr(event)
    with pytest.raises(ValueError, match="frame type"):
        decoder.events(frame.replace(tr, tr[:-1] + "0"), NOW)


def test_native_quotes_validate_provider_clocks_and_currency():
    plan = subscription_plan((KR, US), held=[("KR", "009999"), ("US", "DNASFIX")])
    decoder = VtsFrameDecoder((KR, US), plan)
    kr, = decoder.events(kr_quote(), NOW)
    us, = decoder.events(us_quote(), NOW)
    assert (kr.currency, kr.native_price, kr.tradable) == ("KRW", Decimal("21000"), False)
    assert (us.currency, us.native_price, us.tradable) == ("USD", Decimal("125.50"), False)
    assert decoder.events(kr_quote(clock="100100"), NOW) == ()
    assert decoder.events(kr_quote(), NOW + timedelta(minutes=1)) == ()
    assert decoder.events(kr_quote(price="NaN"), NOW) == ()
    with pytest.raises(ValueError, match="record count"):
        decoder.events(kr_quote().replace("|001|", "|999|"), NOW)


@pytest.mark.parametrize("quote", [kr_quote(), us_quote()])
@pytest.mark.parametrize("bad_date", ["", "20260230", "bad-date", "20260702"])
def test_provider_dates_must_be_present_valid_and_nonfuture(quote, bad_date):
    plan = subscription_plan((KR, US), held=[("KR", "009999"), ("US", "DNASFIX")])
    decoder = VtsFrameDecoder((KR, US), plan)
    assert decoder.events(quote.replace("20260701", bad_date), NOW) == ()
    with pytest.raises(ValueError):
        decoder.events("", NOW)


def test_reconnect_resynchronizes_suppresses_duplicates_and_owns_one_socket(tmp_path):
    calls = []
    lock = tmp_path / "session.lock"
    tr = "H0STCNI9"
    hint = notice(tr, KR, "000000005")
    plan = subscription_plan((KR,), held=[("KR", "009999")])
    attempt = iter([
        [kr_quote(clock="100003"), acknowledgement(tr, KR), hint, kr_quote(clock="100003", price="21100"),
         json.dumps({"header": {"tr_id": "PINGPONG"}})],
        [acknowledgement(tr, KR), hint, kr_quote(clock="100002"),
         kr_quote(clock="100004"), notice(tr, KR, "000000006")],
    ])

    class Socket:
        async def send(self, payload):
            calls.append(("register", json.loads(payload)["body"]["input"]["tr_id"]))

        async def pong(self, payload):
            calls.append(("heartbeat", json.loads(payload)["header"]["tr_id"]))

        def __aiter__(self):
            async def messages():
                for item in next(attempt):
                    yield item
                raise ConnectionClosedError(None, None)
            return messages()

    @asynccontextmanager
    async def open_socket():
        calls.append(("connect", None))
        yield Socket()

    async def record(item):
        calls.append(item)

    async def token():
        return "local-fixture-approval"

    params = dict(open_vts=open_socket, approval=token,
                  resynchronize=lambda: record(("resync", None)),
                  on_hint=lambda event: record(("hint", event.order_number)),
                  on_quote=lambda event: record(("quote", event.source_at.second, int(event.native_price))),
                  sleep=lambda delay: record(("backoff", delay)),
                  clock=lambda: NOW, attempts=2)
    with interprocess_file_lock(lock, timeout=0):
        with pytest.raises(TimeoutError):
            asyncio.run(run_event_feed(lock, (KR,), plan, **params))
    assert not calls

    result = asyncio.run(run_event_feed(lock, (KR,), plan, **params))
    assert result.verified_notice_sessions == 2
    assert result.disconnects == result.delivered_order_hints == 2
    assert result.delivered_quotes == 3
    assert [item for item in calls if item[0] == "hint"] == [("hint", "000000005"), ("hint", "000000006")]
    assert [item for item in calls if item[0] == "quote"] == [("quote", 3, 21000), ("quote", 3, 21100), ("quote", 4, 21000)]
    assert [item for item in calls if item[0] in {"connect", "resync", "backoff"}] == [
        ("connect", None), ("resync", None), ("backoff", 1), ("connect", None), ("resync", None), ("resync", None),
    ]
    assert calls.index(("resync", None)) < calls.index(("quote", 3, 21000))
    assert ("heartbeat", "PINGPONG") in calls


def test_local_probe_reports_approval_separately_from_missing_hts(tmp_path, monkeypatch):
    from tools import check_kis_vts_feed as probe
    from tradingagents.execution.kis_demo import DemoCredentials

    creds = DemoCredentials("fixture-key", "fixture-secret", "12345678", "01")
    monkeypatch.setattr(probe, "get_api_key", lambda name: None)
    monkeypatch.setattr(DemoCredentials, "from_local_settings", classmethod(lambda cls: creds))
    monkeypatch.setattr(probe, "credentials_from_settings", lambda: creds)
    monkeypatch.setattr(probe.KisDemoClient, "websocket_approval", lambda client: "fixture-token")
    assert probe.check(tmp_path / "strategy")["status"] == "MISSING_DEMO_HTS_ID"
    result = probe.check(tmp_path / "strategy", connect_to_broker=True)
    assert result["status"] == "MISSING_DEMO_HTS_ID" and result["approval_verified"] is True
    assert result["orders_submitted"] == 0 and result["real_orders_enabled"] is False
    assert "fixture-token" not in str(result) and "12345678" not in str(result)


@pytest.mark.parametrize("reconnect", [False, True])
def test_local_probe_keeps_independent_app_approvals_and_subscriptions_scoped(tmp_path, monkeypatch, reconnect):
    from tools import check_kis_vts_feed as probe
    from tradingagents.execution.kis_demo import DemoCredentials

    kr = DemoCredentials("fixture-kr-key", "fixture-kr-secret", "12345678", "01")
    us = DemoCredentials("fixture-us-key", "fixture-us-secret", "12345678", "01")
    approval_attempts, subscriptions = [], []
    monkeypatch.setattr(probe, "get_api_key", lambda name: "fixture-hts")
    monkeypatch.setattr(DemoCredentials, "from_local_settings", classmethod(lambda cls: kr))
    monkeypatch.setattr(probe, "credentials_from_settings", lambda: us)

    def broker_approval(client):
        approval_attempts.append(client.credentials)
        return "fixture-token-" + client.credentials.app_key

    async def read_feed(clients, hts_ids, *, approval, **_):
        assert len(clients) == 1
        market, client = next(iter(clients.items()))
        assert approval == "fixture-token-" + client.credentials.app_key
        assert hts_ids[market] == "fixture-hts"
        subscriptions.append((market, client.credentials))
        return {"verified_notice_sessions": 1, "rest_order_inquiries": {market: 2}}

    monkeypatch.setattr(probe.KisDemoClient, "websocket_approval", broker_approval)
    monkeypatch.setattr(probe, "_read_feed", read_feed)
    result = probe.check(tmp_path / "strategy", connect_to_broker=True, verify_reconnect=reconnect)
    assert result["status"] == "SUBSCRIPTIONS_VERIFIED"
    assert result["approval_verified_by_market"] == {"KR": True, "US": True}
    count = 2 if reconnect else 1
    assert approval_attempts == [kr, us] and subscriptions == [("KR", kr)] * count + [("US", us)] * count
    assert all(secret not in str(result) for secret in (kr.app_key, us.app_key, kr.account_no, "fixture-token"))


def test_rejects_common_notice_value_for_a_different_overseas_account(tmp_path, monkeypatch):
    from tools import check_kis_vts_feed as probe
    from tradingagents.execution.kis_demo import DemoCredentials

    kr = DemoCredentials("fixture-kr-key", "fixture-kr-secret", "12345678", "01")
    us = DemoCredentials("fixture-us-key", "fixture-us-secret", "12345679", "01")
    monkeypatch.setattr(DemoCredentials, "from_local_settings", classmethod(lambda cls: kr))
    monkeypatch.setattr(probe, "credentials_from_settings", lambda: us)
    monkeypatch.setattr(probe, "get_api_key", lambda name: "$fixture" if name == "KIS_DEMO_HTS_ID" else None)
    result = probe.check(tmp_path / "strategy", connect_to_broker=True)
    assert result["status"] == "US_DEMO_HTS_ID_REQUIRED_FOR_SEPARATE_ACCOUNT"
    assert "approval_verified_by_market" not in result


def test_probe_records_only_subscription_tr_and_result_code(tmp_path, monkeypatch):
    from tools import check_kis_vts_feed as probe

    class Socket:
        async def send(self, _payload):
            pass

        def __aiter__(self):
            async def messages():
                yield acknowledgement("H0STCNI9", KR)
                yield acknowledgement("H0GSCNI9", US)
            return messages()

    @asynccontextmanager
    async def socket(*args, **kwargs):
        yield Socket()

    class Client:
        def __init__(self, scope):
            from tradingagents.execution.kis_demo import DemoCredentials
            self.credentials = DemoCredentials("test", "test", scope.account[:8], scope.account[8:])

        def orders(self, _date):
            return []

    monkeypatch.setattr(probe, "_FixedHostConnection", socket)
    result = asyncio.run(probe._read_feed({"KR": Client(KR), "US": Client(US)},
                         {scope.market: scope.hts_id for scope in (KR, US)}, state=tmp_path,
                         approval="fixture-approval-only", attempts=1))
    assert [(receipt["tr_id"], receipt["rt_cd"]) for receipt in result["notice_acknowledgements"]] == [
        ("H0STCNI9", "0"), ("H0GSCNI9", "0"),
    ]
    assert all(receipt["accepted"] and datetime.fromisoformat(receipt["received_at"]).utcoffset() is not None
               for receipt in result["notice_acknowledgements"])
    assert result["sockets_connected"] == 1 and result["stopped"] == "PROBE_COMPLETED"
    assert result["disconnects"] == 0 and result["rest_order_inquiries"] == {"KR": 1, "US": 1}
    assert all(value not in str(result) for value in (KR.hts_id, US.account, KEY.decode(), IV.decode(), "fixture-approval-only"))


@pytest.mark.parametrize("failure", ["handshake", "no_ack_before_deadline"])
def test_local_probe_writes_masked_failure_without_holding_broker_lane(tmp_path, monkeypatch, failure):
    from tools import check_kis_vts_feed as probe
    from tradingagents.execution.kis_demo import DemoCredentials
    from websockets.exceptions import InvalidHandshake

    creds = DemoCredentials("fixture-key", "fixture-secret", "12345678", "01")
    monkeypatch.setattr(probe, "get_api_key", lambda name: "fixture-hts")
    monkeypatch.setattr(DemoCredentials, "from_local_settings", classmethod(lambda cls: creds))
    monkeypatch.setattr(probe, "credentials_from_settings", lambda: creds)
    monkeypatch.setattr(probe.KisDemoClient, "websocket_approval", lambda client: "fixture-token")
    monkeypatch.setattr(probe, "_ATTEMPT_SECONDS", .01)

    @asynccontextmanager
    async def socket(*args, **kwargs):
        if failure == "handshake":
            raise InvalidHandshake("private error material")
        await asyncio.sleep(100)
        yield

    monkeypatch.setattr(probe, "_FixedHostConnection", socket)
    state, output = tmp_path / "strategy", tmp_path / "result.json"
    monkeypatch.setattr("sys.argv", ["probe", "--state-dir", str(state), "--output", str(output), "--connect"])
    assert probe.main() == 2
    result = json.loads(output.read_bytes())
    assert result["status"] == "VTS_FEED_UNVERIFIED" and result["approval_verified"] is True
    assert "private error material" not in str(result)
    with interprocess_file_lock(state / "strategy.lock", timeout=0):
        pass
