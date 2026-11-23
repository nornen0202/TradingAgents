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
    fields[0], fields[1], fields[5], fields[6], fields[11] = "DNASFIX", "FIX", "20260701", "100001", "125.50"
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


def test_reconnect_resynchronizes_suppresses_duplicates_and_owns_one_socket(tmp_path):
    calls = []
    lock = tmp_path / "session.lock"
    tr = "H0STCNI9"
    hint = notice(tr, KR, "000000005")
    plan = subscription_plan((KR,), held=[("KR", "009999")])
    attempt = iter([
        [acknowledgement(tr, KR), hint, kr_quote(clock="100003"),
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
                raise OSError("synthetic disconnect")
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
                  on_quote=lambda event: record(("quote", event.source_at.second)),
                  sleep=lambda delay: record(("backoff", delay)),
                  clock=lambda: NOW, attempts=2)
    with interprocess_file_lock(lock, timeout=0):
        with pytest.raises(TimeoutError):
            asyncio.run(run_event_feed(lock, (KR,), plan, **params))
    assert not calls

    result = asyncio.run(run_event_feed(lock, (KR,), plan, **params))
    assert result.disconnects == result.delivered_order_hints == result.delivered_quotes == 2
    assert [item for item in calls if item[0] == "hint"] == [("hint", "000000005"), ("hint", "000000006")]
    assert [item for item in calls if item[0] == "quote"] == [("quote", 3), ("quote", 4)]
    assert [item for item in calls if item[0] in {"connect", "resync", "backoff"}] == [
        ("resync", None), ("connect", None), ("backoff", 1), ("resync", None), ("connect", None), ("resync", None),
    ]
    assert ("heartbeat", "PINGPONG") in calls
