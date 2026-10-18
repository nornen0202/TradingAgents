"""Offline US demo transport tests. No broker access or real credentials."""
from datetime import datetime, timezone
import json

import pytest
import requests

from tradingagents.execution import kis_demo_us as module
from tradingagents.execution.kis_demo import DemoCredentials, DemoError, RequestPacer
from tools import check_kis_demo_us as probe


class Response:
    def __init__(self, payload, *, status=200, headers=None):
        self.payload, self.status_code, self.headers = payload, status, headers or {}

    def json(self):
        if isinstance(self.payload, Exception):
            raise self.payload
        return self.payload


class Session:
    def __init__(self, *responses):
        self.responses, self.calls = list(responses), []
        self.closed = False

    def request(self, method, url, **kwargs):
        self.calls.append((method, url, kwargs))
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response

    def close(self):
        self.closed = True


NOW = datetime.fromisoformat("2026-10-19T15:00:00+00:00")
CREDENTIALS = DemoCredentials("us-demo-fixture", "us-secret-fixture", "12345678", "01")


def client(*responses, now=NOW):
    session = Session(Response({"access_token": "fixture-token", "expires_in": 86400}), *responses)
    return module.KisDemoUSReadClient(CREDENTIALS, session=session,
        pacer=RequestPacer(interval=0), utcnow=lambda: now), session


def balance(rows=None, **changes):
    return {"rt_cd": "0", "output1": [] if rows is None else rows,
            "output2": {"tot_evlu_pfls_amt": "0"}, **changes}


def order(**changes):
    return {"ord_dt": "20261019", "dmst_ord_dt": "20261019", "thco_ord_tmd": "233000",
            "ovrs_excg_cd": "NASD", "pdno": "AAPL", **changes}


def test_dedicated_us_path_without_environment_or_domestic_fallback(monkeypatch, tmp_path):
    paths = []
    monkeypatch.setattr(module, "storage_path", lambda: tmp_path / "kis-demo.dpapi")
    monkeypatch.setattr(module, "load_demo_settings", lambda **kw: paths.append(kw["path"]) or {})
    monkeypatch.setenv("KIS_DEMO_APP_KEY", "domestic-fixture")
    monkeypatch.setenv("KIS_APP_KEY", "live-fixture")
    assert not any(module.configuration_status().values())
    with pytest.raises(DemoError):
        module.credentials_from_settings()
    assert paths == [tmp_path / "kis-demo-us.dpapi"] * 2


def test_us_balance_uses_official_vts_read_path_and_masks_repr():
    c, session = client(Response(balance()))
    assert c.balance("NASD")[0] == []
    assert session.calls[-1][0:2] == ("GET", module.DEMO_HOST + module.PREFIX + "inquire-balance")
    params = session.calls[-1][2]["params"]
    assert params["OVRS_EXCG_CD"] == "NASD" and params["TR_CRCY_CD"] == "USD"
    assert session.calls[-1][2]["headers"]["tr_id"] == "VTTS3012R"
    assert all(not call[2]["allow_redirects"] for call in session.calls)
    assert "fixture" not in repr(CREDENTIALS) and "12345678" not in repr(CREDENTIALS)


@pytest.mark.parametrize("method,path", [
    ("POST", module.PREFIX + "order"), ("POST", module.PREFIX + "order-rvsecncl"),
    ("GET", "/uapi/domestic-stock/v1/trading/inquire-balance"),
    ("GET", "https://openapi.koreainvestment.com:9443"),
    ("DELETE", module.PREFIX + "inquire-balance"),
])
def test_mutations_and_alternate_hosts_block_before_auth(method, path):
    c, session = client()
    with pytest.raises(DemoError):
        c._http(method, path)
    assert not session.calls


@pytest.mark.parametrize("endpoint,tr_id", [
    ("inquire-balance", "TTTS3012R"), ("inquire-ccnl", "TTTS3035R"),
    ("order", "VTTT1002U"), ("../inquire-balance", "VTTS3012R"),
])
def test_endpoint_and_transaction_pair_allowlist(endpoint, tr_id):
    c, session = client()
    with pytest.raises(DemoError):
        c.request(endpoint, tr_id, params=c._account())
    assert not session.calls


def test_account_scope_mismatch_has_no_auth_or_read():
    c, session = client()
    with pytest.raises(DemoError):
        c.request("inquire-balance", "VTTS3012R", params={"CANO": "87654321", "ACNT_PRDT_CD": "01"})
    assert not session.calls


@pytest.mark.parametrize("exchange", ["NAS", "", "SEHK", "ALL", None])
def test_invalid_exchange_is_rejected_before_network(exchange):
    c, session = client()
    with pytest.raises(DemoError):
        c.balance(exchange)
    assert not session.calls


def test_pagination_complete_uses_fk200_nk200_and_n_header():
    c, session = client(
        Response(balance([{"ovrs_pdno": "AAPL"}], ctx_area_fk200="a", ctx_area_nk200="b"), headers={"tr_cont": "F"}),
        Response(balance([{"ovrs_pdno": "MSFT"}]), headers={"tr_cont": "D"}),
    )
    assert len(c.balance("NASD")[0]) == 2
    call = session.calls[-1][2]
    assert call["params"]["CTX_AREA_FK200"] == "a" and call["params"]["CTX_AREA_NK200"] == "b"
    assert call["headers"]["tr_cont"] == "N"


@pytest.mark.parametrize("changes,headers", [
    ({"ctx_area_fk200": "", "ctx_area_nk200": ""}, {"tr_cont": "M"}),
    ({"ctx_area_fk200": None, "ctx_area_nk200": "x"}, {"tr_cont": "F"}),
    ({}, {"tr_cont": "UNKNOWN"}),
])
def test_incomplete_or_unknown_pagination_fails(changes, headers):
    c, _ = client(Response(balance(**changes), headers=headers))
    with pytest.raises(DemoError):
        c.balance("NASD")


def test_repeated_pagination_cursor_fails_without_inventing_completion():
    response = Response(balance(ctx_area_fk200="a", ctx_area_nk200="b"), headers={"tr_cont": "M"})
    c, _ = client(response, response)
    with pytest.raises(DemoError, match="pagination incomplete"):
        c.balance("NASD")


@pytest.mark.parametrize("payload", [
    {}, {"rt_cd": "1", "output1": [], "output2": {}},
    balance(output1=None), balance(output1={}), balance(output1=[None]),
    balance(output2=None), balance(output2=[]), balance(output2={}), balance(output2=[0]),
])
def test_missing_or_malformed_balance_is_never_an_empty_account(payload):
    c, _ = client(Response(payload))
    with pytest.raises(DemoError):
        c.balance("NASD")


@pytest.mark.parametrize("response", [
    Response({}, status=302), Response({}, status=500), Response([]),
    Response(ValueError("private broker error")), requests.Timeout("private key in exception"),
])
def test_transport_errors_are_sanitized_and_never_retried(response):
    c, session = client(response)
    with pytest.raises(DemoError) as error:
        c.balance("NASD")
    assert "private" not in str(error.value)
    assert len(session.calls) == 2


def test_retry_enabled_adapter_is_rejected_before_network():
    session = requests.Session()
    session.mount("https://", requests.adapters.HTTPAdapter(max_retries=1))
    with pytest.raises(DemoError):
        module.KisDemoUSReadClient(CREDENTIALS, session=session)
    session.close()


@pytest.mark.parametrize("trade_date", [None, "", "2026-10-19", "20260230", "20261020", "20261301"])
def test_missing_invalid_future_dates_are_rejected_locally(trade_date):
    c, session = client()
    with pytest.raises(DemoError):
        c.orders(trade_date)
    assert not session.calls


def test_empty_order_response_is_valid_and_filters_follow_mock_contract():
    c, session = client(Response({"rt_cd": "0", "output": []}))
    assert c.orders("20261019") == []
    params = session.calls[-1][2]["params"]
    assert all(params[key] == "" for key in ("PDNO", "OVRS_EXCG_CD", "ORD_DT", "ORD_GNO_BRNO", "ODNO"))
    assert params["SLL_BUY_DVSN"] == "00" and params["CCLD_NCCS_DVSN"] == "00"
    assert session.calls[-1][2]["headers"]["tr_id"] == "VTTS3035R"


def test_order_date_and_independent_domestic_clock_validated_locally():
    c, _ = client(Response({"rt_cd": "0", "output": [order()]}))
    assert len(c.orders("20261019")) == 1


@pytest.mark.parametrize("changes", [
    {"ord_dt": "20261020"}, {"ord_dt": "20261018"}, {"ord_dt": ""},
    {"ord_dt": "20260230"}, {"dmst_ord_dt": ""}, {"dmst_ord_dt": "20260230"},
    {"thco_ord_tmd": ""}, {"thco_ord_tmd": "250000"}, {"dmst_ord_dt": "20261020", "thco_ord_tmd": "010000"},
    {"dmst_ord_dt": "20261020", "thco_ord_tmd": "000001"},
    {"ovrs_excg_cd": "SEHK"}, {"ovrs_excg_cd": ""},
])
def test_unknown_out_of_range_or_future_orders_never_count_as_verified(changes):
    c, _ = client(Response({"rt_cd": "0", "output": [order(**changes)]}))
    with pytest.raises(DemoError):
        c.orders("20261019")


def test_naive_clock_is_rejected():
    c, session = client(now=datetime(2026, 10, 19))
    with pytest.raises(DemoError):
        c.orders("20261019")
    assert not session.calls


def test_offline_readiness_never_instantiates_client(monkeypatch):
    monkeypatch.setattr(probe, "configuration_status", lambda: {"key": True})
    monkeypatch.setattr(probe, "KisDemoUSReadClient", lambda *_: pytest.fail("network prohibited"))
    assert probe.check()["status"] == "READY_TO_PROBE"


def test_probe_only_outputs_masked_counts_and_completion_receipt(monkeypatch):
    class FakeClient:
        def __init__(self, _):
            self.closed = False

        def balance(self, exchange):
            return [{"secret": "never-export", "account": "12345678"}], {"cash": 100000}

        def orders(self, _):
            return []

        def close(self):
            self.closed = True

    monkeypatch.setattr(probe, "configuration_status", lambda: {"key": True})
    monkeypatch.setattr(probe, "credentials_from_settings", lambda: CREDENTIALS)
    monkeypatch.setattr(probe, "KisDemoUSReadClient", FakeClient)
    before = datetime.now(timezone.utc)
    result = probe.check(connect=True)
    assert result["status"] == "READ_CONNECTION_VERIFIED"
    assert datetime.fromisoformat(result["checked_at"]) >= before
    assert result["position_rows_by_exchange"] == dict.fromkeys(module.EXCHANGES, 1)
    assert not result["paper_order_connection_verified"]
    assert result["orders_submitted"] == 0 and not result["live_orders_enabled"]
    assert result["market"] == "US" and result["mode"] == "KIS_DEMO"
    encoded = json.dumps(result)
    assert "never-export" not in encoded and "12345678" not in encoded and "100000" not in encoded


def test_probe_failure_is_masked(monkeypatch):
    monkeypatch.setattr(probe, "configuration_status", lambda: {"key": True})
    monkeypatch.setattr(probe, "credentials_from_settings", lambda: (_ for _ in ()).throw(DemoError("private value")))
    result = probe.check(connect=True)
    assert result["status"] == "CONNECTION_UNVERIFIED"
    assert "private" not in json.dumps(result)
