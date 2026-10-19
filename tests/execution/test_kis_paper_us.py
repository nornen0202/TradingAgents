"""US mock execution fixtures; no broker network access or real credentials."""
from datetime import datetime, timedelta
import json
from urllib.parse import urlsplit

import pytest
import requests
from requests.adapters import HTTPAdapter

from tradingagents.execution.kis_demo import DemoCredentials, DemoError, RequestPacer
from tradingagents.execution.kis_demo_us import KisDemoUSClient, KisDemoUSReadClient
from tradingagents.execution.kis_paper_us import KisPaperUSBroker, USPaperOrderPolicy, read_paper_us_account

NOW = "2026-10-19T10:01:00-04:00"


class Response:
    def __init__(self, payload, code=200, headers=None):
        self.payload, self.status_code, self.headers = payload, code, headers or {}

    def json(self):
        return self.payload


class Session:
    def __init__(self, *responses):
        self.responses, self.calls = list(responses), []

    def request(self, method, url, **kwargs):
        self.calls.append((method, url, kwargs))
        response = self.responses.pop(0)
        if callable(response):
            response = response()
        if isinstance(response, Exception):
            raise response
        return response

    def close(self):
        pass


def ack(odno="123"):
    return Response({"rt_cd": "0", "output": {"ODNO": odno}})


def report(*, quantity=1, filled=0, remaining=1, **changes):
    return Response({"rt_cd": "0", "output": [{"odno": "123", "ord_dt": "20261019", "dmst_ord_dt": "20261019",
        "thco_ord_tmd": "230100", "pdno": "AAPL", "ovrs_excg_cd": "NASD", "tr_crcy_cd": "USD",
        "sll_buy_dvsn_cd": "02", "ft_ord_unpr3": "200.00", "ft_ord_qty": str(quantity),
        "ft_ccld_qty": str(filled), "nccs_qty": str(remaining), "prcs_stat_name": "접수", "rjct_rson": "", **changes}]})


def make(tmp_path, *responses, enabled=True, policy=None, account_no="12345678"):
    moment = [datetime.fromisoformat(NOW)]
    session = Session(Response({"access_token": "fixture-token", "expires_in": 86400}), *responses)
    client = KisDemoUSClient(DemoCredentials("fixture-key", "fixture-secret", account_no, "01"), session=session,
        pacer=RequestPacer(interval=0), utcnow=lambda: moment[0])
    broker = KisPaperUSBroker(tmp_path / "vts-us.sqlite", client, policy or USPaperOrderPolicy((("AAPL", "NASD"),)),
                            paper_enabled=enabled, clock=lambda: moment[0])
    return broker, client, session, moment


def order(broker, **changes):
    result = {"intent_id": "us-intent-1", "ticker": "AAPL", "exchange": "NASD", "side": "BUY", "quantity": 1, "limit_price": 200,
        "signal": {"signal_id": "signal:fixture-1", "ticker": "AAPL", "decision_now": "STARTER_NOW", "execution_ready": True,
            "available_at": "2026-10-19T10:00:50-04:00", "valid_until": "2026-10-19T10:02:30-04:00"},
        "quote": {"ticker": "AAPL", "exchange": "NASD", "provider": "kis", "currency": "USD", "session": "regular", "execution_ready": True,
            "instrument_type": "STOCK", "last_price": 200, "observed_at": "2026-10-19T10:00:55-04:00", "ingested_at": NOW},
        "account": {"environment": "demo", "market": "US", "currency": "USD", "account_scope": broker.client.credentials.scope(), "complete": True,
            "observed_at": NOW, "ingested_at": NOW, "nav_usd": 100_000, "cash_usd": 98_000,
            "positions": [{"ticker": "AAPL", "exchange": "NASD", "quantity": 10, "sellable_quantity": 10, "market_value_usd": 2000}],
            "cash_only_buying_power_usd": 90_000, "cash_only_buying_quantity": 450,
            "capacity_ticker": "AAPL", "capacity_exchange": "NASD", "capacity_limit_price": 200}}
    result.update(changes)
    return result


def test_explicit_opt_in_and_vts_only_exact_tr_mapping(tmp_path):
    b, c, s, _ = make(tmp_path, ack(), enabled=False)
    with pytest.raises(DemoError):
        b.submit(**order(b))
    assert not s.calls
    for method, endpoint, tr_id in (("POST", "order", "TTTT1002U"), ("POST", "order", "VTTT1006U"),
            ("POST", "daytime-order", "VTTT1002U"), ("GET", "../inquire-balance", "VTTS3012R")):
        with pytest.raises(DemoError):
            c.request(method, endpoint, tr_id, body=c._account())
    assert not s.calls
    b.close()


@pytest.mark.parametrize("left,right,expected", [
    ("0000000123", "123", True), ("123", "0000000123", True),
    ("0000000123", "124", False), ("0000000000", "0", False),
    ("+123", "123", False), ("123 ", "123", False), ("123.0", "123", False),
    ("00000000123", "123", False), ("１２３", "123", False),
    (123, "123", False), (None, "123", False), ("", "", False),
])
def test_order_identity_only_normalizes_decimal_zero_padding(left, right, expected):
    from tradingagents.execution.kis_paper_us import _same_order_number
    assert _same_order_number(left, right) is expected


def test_original_padded_ack_reconciles_without_rewrite_or_resubmit(tmp_path):
    b, c, session, _ = make(tmp_path, ack("0000000123"), report())
    try:
        b.submit(**order(b))
        original = b.db.execute("SELECT response FROM requests WHERE id='us-intent-1'").fetchone()[0]
        b.journal._block("us-intent-1", "unverified_paper_reconciliation")
        result = b.reconcile(intent_id="us-intent-1")
        assert result["status"] == "OPEN" and result["remaining_qty"] == 1
        assert b.db.execute("SELECT response FROM requests WHERE id='us-intent-1'").fetchone()[0] == original
        assert b.db.execute("SELECT COUNT(*) FROM reconciliation_issues").fetchone()[0] == 0
        assert sum(method == "POST" and url.endswith('/order') for method, url, _ in session.calls) == 1
    finally:
        b.close()


@pytest.mark.parametrize("change", ["duplicate", "different", "wrong_terms", "future"])
def test_padded_ack_does_not_bypass_unique_original_evidence(tmp_path, change):
    response = report()
    if change == "duplicate": response.payload['output'].append({**response.payload['output'][0], 'odno': '0000000123'})
    if change == "different": response.payload['output'][0]['odno'] = '124'
    if change == "wrong_terms": response.payload['output'][0]['pdno'] = 'MSFT'
    if change == "future": response.payload['output'][0]['thco_ord_tmd'] = '230101'
    b, c, session, _ = make(tmp_path, ack("0000000123"), response)
    try:
        b.submit(**order(b))
        with pytest.raises(DemoError):
            b.reconcile(intent_id='us-intent-1')
        assert b.db.execute("SELECT COUNT(*) FROM reconciliation_issues").fetchone()[0] == 1
    finally:
        b.close()


def test_ack_is_not_fill_and_retry_after_restart_does_not_write(tmp_path):
    b, c, s, _ = make(tmp_path, ack())
    args = order(b)
    first = b.submit(**args)
    assert first["status"] == "ACKNOWLEDGED" and first["live_orders_enabled"] is False
    sent = s.calls[-1]
    assert urlsplit(sent[1]).netloc == "openapivts.koreainvestment.com:29443"
    assert sent[2]["headers"]["tr_id"] == "VTTT1002U"
    assert sent[2]["json"]["OVRS_ORD_UNPR"] == "200.00" and not sent[2]["allow_redirects"]
    assert b.db.execute("SELECT count(*) FROM lifecycle_events WHERE kind='FILL'").fetchone()[0] == 0
    b.close()
    b, _, s, _ = make(tmp_path)
    assert b.submit(**args)["duplicate"] is True
    assert not s.calls
    with pytest.raises(DemoError):
        b.submit(**{**args, "quantity": 2})
    b.close()


def test_lost_response_is_unknown_and_blocks_new_order_across_restart(tmp_path):
    b, _, _, _ = make(tmp_path, requests.Timeout())
    args = order(b)
    assert b.submit(**args)["status"] == "UNKNOWN"
    b.close()
    b, _, s, _ = make(tmp_path)
    assert b.submit(**args)["status"] == "UNKNOWN"
    with pytest.raises(DemoError):
        b.submit(**{**args, "intent_id": "second"})
    assert not s.calls
    b.close()


@pytest.mark.parametrize("group,key,value", [
    ("quote", "currency", "KRW"), ("quote", "exchange", "NYSE"), ("quote", "provider", "yahoo"),
    ("quote", "observed_at", None), ("quote", "observed_at", "2026-10-19T10:02:00-04:00"),
    ("quote", "observed_at", "2026-10-19T09:59:00-04:00"), ("quote", "ingested_at", "invalid"),
    ("quote", "session", "afterhours"), ("quote", "execution_ready", False),
    ("account", "environment", "real"), ("account", "currency", "KRW"), ("account", "market", "KR"),
    ("account", "account_scope", "other"), ("account", "complete", False),
    ("account", "cash_only_buying_quantity", 0), ("account", "cash_usd", 0),
    ("account", "capacity_exchange", "NYSE"), ("signal", "execution_ready", False),
    ("signal", "decision_now", "WATCH"), ("signal", "valid_until", "2026-10-19T10:01:00-04:00"),
])
def test_bad_evidence_blocks_before_network(tmp_path, group, key, value):
    b, _, s, _ = make(tmp_path)
    args = order(b)
    args[group][key] = value
    with pytest.raises(DemoError):
        b.submit(**args)
    assert not s.calls
    b.close()


@pytest.mark.parametrize("changes", [{"ticker": "005930"}, {"exchange": "SEHK"}, {"quantity": 1.5}, {"quantity": True},
    {"limit_price": 0.99}, {"limit_price": 200.001}, {"limit_price": float("nan")}, {"quantity": 3}, {"limit_price": 210}, {"side": "SHORT"}])
def test_invalid_terms_and_risk_limits(tmp_path, changes):
    b, _, s, _ = make(tmp_path)
    with pytest.raises(DemoError):
        b.submit(**order(b, **changes))
    assert not s.calls
    b.close()


def test_regular_session_and_late_transport_deadline(tmp_path):
    b, c, s, moment = make(tmp_path, ack())
    moment[0] = datetime.fromisoformat("2026-10-18T10:01:00-04:00")
    with pytest.raises(DemoError):
        b.submit(**order(b))
    assert not s.calls
    moment[0] = datetime.fromisoformat(NOW)
    class SlowPacer:
        def wait(self):
            moment[0] += timedelta(minutes=2)
    c.pacer = SlowPacer()
    assert b.submit(**order(b))["status"] == "NOT_SENT"
    assert all(not url.endswith("/order") for _, url, _ in s.calls)
    b.close()


def test_reducing_sell_uses_explicit_demo_sell_id_and_sellable_reservations(tmp_path):
    b, _, s, _ = make(tmp_path, ack())
    args = order(b, side="SELL")
    args["signal"]["decision_now"] = "REDUCE_NOW"
    args["account"]["cash_usd"] = 0
    args["account"]["cash_only_buying_quantity"] = 0
    assert b.submit(**args)["status"] == "ACKNOWLEDGED"
    assert s.calls[-1][2]["headers"]["tr_id"] == "VTTT1001U"
    args["intent_id"] = "second"
    args["account"]["positions"][0]["sellable_quantity"] = 1
    with pytest.raises(DemoError):
        b.submit(**args)
    b.close()


def test_partial_fill_cancel_ack_and_later_cancel_evidence(tmp_path):
    b, _, s, _ = make(tmp_path, ack(), report(quantity=2, filled=1), report(quantity=2, filled=1), ack("cancel-1"),
                    report(quantity=2, filled=1, remaining=0, prcs_stat_name="취소완료"))
    b.submit(**order(b, quantity=2))
    observed = b.reconcile(intent_id="us-intent-1")
    assert observed["status"] == "PARTIAL" and observed["cumulative_observation_only"] is True
    cancelled = b.cancel(intent_id="us-intent-1")
    assert cancelled["status"] == "ACKNOWLEDGED" and cancelled["cancellation_confirmed"] is False
    assert s.calls[-1][2]["headers"]["tr_id"] == "VTTT1004U"
    assert s.calls[-1][2]["json"]["ORD_QTY"] == "1"
    assert b.reconcile(intent_id="us-intent-1")["status"] == "CANCELLED"
    assert b.db.execute("SELECT count(*) FROM lifecycle_events WHERE kind='FILL'").fetchone()[0] == 0
    assert b.db.execute("SELECT count(*) FROM lifecycle_events WHERE kind='CANCEL'").fetchone()[0] == 1
    b.close()


def test_cancel_race_reports_fill_not_cancel(tmp_path):
    b, _, s, _ = make(tmp_path, ack(), report(filled=1, remaining=0))
    b.submit(**order(b))
    with pytest.raises(DemoError):
        b.cancel(intent_id="us-intent-1")
    assert b.db.execute("SELECT status FROM order_state").fetchone()[0] == "FILLED"
    assert not any(url.endswith("/order-rvsecncl") for _, url, _ in s.calls)
    b.close()


@pytest.mark.parametrize("changes", [{"ord_dt": "20261020"}, {"dmst_ord_dt": ""}, {"thco_ord_tmd": "230200"},
    {"thco_ord_tmd": "225900"}, {"ft_ord_unpr3": "201"}, {"tr_crcy_cd": "KRW"}, {"ft_ccld_qty": "2"},
    {"ft_ccld_qty": "bad"}, {"nccs_qty": "-1"}, {"pdno": "MSFT"}, {"ovrs_excg_cd": "NYSE"}])
def test_report_missing_future_invalid_and_mismatched_data_blocks_new_orders(tmp_path, changes):
    b, _, _, _ = make(tmp_path, ack(), report(**changes))
    b.submit(**order(b))
    with pytest.raises(DemoError):
        b.reconcile(intent_id="us-intent-1")
    assert b.db.execute("SELECT count(*) FROM reconciliation_issues").fetchone()[0] == 1
    with pytest.raises(DemoError):
        b.submit(**order(b, intent_id="second"))
    b.close()


def test_filled_state_cannot_regress(tmp_path):
    b, _, _, _ = make(tmp_path, ack(), report(filled=1, remaining=0), report())
    b.submit(**order(b))
    assert b.reconcile(intent_id="us-intent-1")["status"] == "FILLED"
    with pytest.raises(DemoError):
        b.reconcile(intent_id="us-intent-1")
    assert b.db.execute("SELECT status FROM order_state").fetchone()[0] == "FILLED"
    b.close()


def test_empty_report_and_zero_remainder_do_not_invent_fills_or_cancels(tmp_path):
    b, _, _, _ = make(tmp_path, ack(), Response({"rt_cd": "0", "output": []}), report(remaining=0, prcs_stat_name="완료"))
    b.submit(**order(b))
    with pytest.raises(DemoError):
        b.reconcile(intent_id="us-intent-1")
    assert b.reconcile(intent_id="us-intent-1")["status"] == "UNRESOLVED"
    assert b.db.execute("SELECT count(*) FROM order_state").fetchone()[0] == 0
    b.close()


def test_observation_is_known_only_after_response(tmp_path):
    b, _, s, moment = make(tmp_path, ack())
    b.submit(**order(b))
    def response():
        moment[0] += timedelta(seconds=3)
        return report(filled=1, remaining=0)
    s.responses.append(response)
    result = b.reconcile(intent_id="us-intent-1")
    assert datetime.fromisoformat(result["observed_at"]) == moment[0]
    assert result["settlement_known"] is False and result["fill_time_known"] is False
    b.close()


def test_complete_us_account_uses_usd_only_capacity(tmp_path):
    balances = [Response({"rt_cd": "0", "output1": [], "output2": {"tot_evlu_pfls_amt": "0"}}) for _ in range(3)]
    cap = Response({"rt_cd": "0", "output": {"tr_crcy_cd": "USD", "ord_psbl_frcr_amt": "1000", "ovrs_ord_psbl_amt": "900",
                   "ord_psbl_qty": "4", "echm_af_ord_psbl_amt": "999999"}})
    b, c, s, moment = make(tmp_path, *balances, cap)
    result = read_paper_us_account(c, ticker="AAPL", exchange="NASD", limit_price=200, clock=lambda: moment[0])
    assert result["cash_only_buying_power_usd"] == 900 and result["nav_usd"] == 1000
    assert result["cash_only_buying_quantity"] == 4 and result["positions"] == []
    assert s.calls[-1][2]["headers"]["tr_id"] == "VTTS3007R"
    assert s.calls[-1][2]["params"]["OVRS_ORD_UNPR"] == "200.00"
    b.close()


@pytest.mark.parametrize("field,value", [("tr_crcy_cd", "KRW"), ("ord_psbl_frcr_amt", ""), ("ord_psbl_qty", "1.5")])
def test_malformed_us_capacity_blocks(tmp_path, field, value):
    cap = {"tr_crcy_cd": "USD", "ord_psbl_frcr_amt": "1000", "ovrs_ord_psbl_amt": "900", "ord_psbl_qty": "4"}
    cap[field] = value
    balances = [Response({"rt_cd": "0", "output1": [], "output2": {"total": "0"}}) for _ in range(3)]
    b, c, _, moment = make(tmp_path, *balances, Response({"rt_cd": "0", "output": cap}))
    with pytest.raises(DemoError):
        read_paper_us_account(c, ticker="AAPL", exchange="NASD", limit_price=200, clock=lambda: moment[0])
    b.close()


def test_policy_immutable_account_scoped_and_no_http_retries(tmp_path):
    b, _, _, _ = make(tmp_path)
    b.close()
    with pytest.raises(DemoError):
        make(tmp_path, policy=USPaperOrderPolicy((("AAPL", "NASD"),), max_order_usd=400))
    with pytest.raises(DemoError):
        make(tmp_path, account_no="87654321")
    session = requests.Session()
    session.mount("https://", HTTPAdapter(max_retries=1))
    with pytest.raises(DemoError):
        KisDemoUSClient(DemoCredentials("key", "secret", "12345678", "01"), session=session)
    session.close()


def test_read_only_client_remains_incapable_of_write(tmp_path):
    c = KisDemoUSReadClient(DemoCredentials("key", "secret", "12345678", "01"), session=Session())
    with pytest.raises(DemoError):
        c._http("POST", "/uapi/overseas-stock/v1/trading/order")
    with pytest.raises(DemoError):
        KisPaperUSBroker(tmp_path / "journal.sqlite", c, USPaperOrderPolicy((("AAPL", "NASD"),)), paper_enabled=True)


def test_cli_write_requires_opt_in_before_credentials_or_network(tmp_path, capsys, monkeypatch):
    from tools import kis_paper_us as cli
    monkeypatch.setattr(cli, "credentials_from_settings", lambda: pytest.fail("must not load settings"))
    result = cli.main(["submit", "--journal", str(tmp_path / "j.sqlite"), "--policy", str(tmp_path / "absent.json"),
                       "--input", str(tmp_path / "absent-order.json")])
    assert result == 2 and json.loads(capsys.readouterr().out)["live_orders_enabled"] is False


def test_capacity_cli_is_read_only_and_masks_amounts(capsys, monkeypatch):
    from tools import kis_paper_us as cli
    class Client:
        def close(self):
            pass
    monkeypatch.setattr(cli, "credentials_from_settings", lambda: object())
    monkeypatch.setattr(cli, "KisDemoUSClient", lambda credentials: Client())
    monkeypatch.setattr(cli, "read_paper_us_account", lambda *a, **kw: {
        "positions": [], "complete": True, "cash_only_buying_power_usd": 987654, "cash_only_buying_quantity": 10})
    assert cli.main(["capacity", "--ticker", "AAPL", "--exchange", "NASD", "--limit-price", "200"]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["status"] == "USD_CAPACITY_VERIFIED" and result["orders_submitted"] == 0
    assert "987654" not in str(result) and result["paper_order_connection_verified"] is False


def test_lost_cancel_response_blocks_new_writes_and_never_resends(tmp_path):
    b, _, s, _ = make(tmp_path, ack(), report(), requests.Timeout())
    args = order(b)
    b.submit(**args)
    assert b.cancel(intent_id=args["intent_id"])["status"] == "UNKNOWN"
    calls = len(s.calls)
    assert b.cancel(intent_id=args["intent_id"])["status"] == "UNKNOWN"
    assert len(s.calls) == calls
    with pytest.raises(DemoError):
        b.submit(**{**args, "intent_id": "second"})
    b.close()


@pytest.mark.parametrize("padded", [False, True])
@pytest.mark.parametrize("label", ["완료", ""])
def test_cancel_child_must_prove_link_and_completion(tmp_path, padded, label):
    child = {**report().payload["output"][0], "odno": "456", "orgn_odno": "123", "rvse_cncl_dvsn": "02",
             "prcs_stat_name": label, "nccs_qty": "0"}
    final = report(remaining=0)
    final.payload["output"].append(child)
    b, _, _, _ = make(tmp_path, ack("0000000123" if padded else "123"), report(),
                       ack("0000000456" if padded else "456"), final)
    b.submit(**order(b))
    b.cancel(intent_id="us-intent-1")
    assert b.reconcile(intent_id="us-intent-1")["status"] == "CANCELLED"
    b.close()


@pytest.mark.parametrize("changes", [
    {"nccs_qty": "1"}, {"ft_ccld_qty": "1"}, {"ft_ord_qty": "2"},
    {"orgn_odno": "124"}, {"rvse_cncl_dvsn": "01"}, {"sll_buy_dvsn_cd": "01"},
    {"rjct_rson": "REJECTED"}, {"prcs_stat_name": "접수"}, {"prcs_stat_name": None},
    {"ft_ord_qty": ""}, {"nccs_qty": None}, {"thco_ord_tmd": "230059"},
])
def test_blank_cancel_label_needs_complete_matching_broker_quantity_proof(tmp_path, changes):
    child = {**report().payload["output"][0], "odno": "456", "orgn_odno": "123", "rvse_cncl_dvsn": "02",
             "prcs_stat_name": "", "nccs_qty": "0", **changes}
    final = report(remaining=0)
    final.payload["output"].append(child)
    b, _, _, _ = make(tmp_path, ack("0000000123"), report(), ack("0000000456"), final)
    try:
        b.submit(**order(b))
        b.cancel(intent_id="us-intent-1")
        try:
            result = b.reconcile(intent_id="us-intent-1")
        except DemoError:
            pass
        else:
            assert result["status"] == "UNRESOLVED"
        assert b.db.execute("SELECT COUNT(*) FROM reconciliation_issues").fetchone()[0] == 1
    finally:
        b.close()


def test_pending_buy_reservations_and_daily_limit(tmp_path):
    b, _, _, _ = make(tmp_path, ack(), policy=USPaperOrderPolicy((("AAPL", "NASD"),), max_daily_buy_usd=300))
    args = order(b)
    b.submit(**args)
    with pytest.raises(DemoError, match="Daily"):
        b.submit(**{**args, "intent_id": "second"})
    b.close()


def test_unfilled_cash_reservation_is_not_available_again(tmp_path):
    b, _, _, _ = make(tmp_path, ack())
    args = order(b)
    args["account"]["cash_usd"] = 350
    b.submit(**args)
    with pytest.raises(DemoError, match="reserved cash"):
        b.submit(**{**args, "intent_id": "second"})
    b.close()


@pytest.mark.parametrize("changes", [{"tr_crcy_cd": "KRW"}, {"ovrs_excg_cd": "NYSE"},
    {"ord_psbl_qty": "2"}, {"ovrs_cblc_qty": "1.5"}, {"loan_type_cd": "01"}])
def test_account_positions_require_whole_cash_usd_same_venue(tmp_path, changes):
    row = {"ovrs_pdno": "AAPL", "ovrs_excg_cd": "NASD", "tr_crcy_cd": "USD", "ovrs_cblc_qty": "1",
           "ord_psbl_qty": "1", "ovrs_stck_evlu_amt": "200", "loan_type_cd": "00", **changes}
    b, c, _, moment = make(tmp_path, Response({"rt_cd": "0", "output1": [row], "output2": {"total": "0"}}))
    with pytest.raises(DemoError):
        read_paper_us_account(c, ticker="AAPL", exchange="NASD", limit_price=200, clock=lambda: moment[0])
    b.close()


def test_ny_session_date_survives_korean_midnight(tmp_path):
    b, _, s, moment = make(tmp_path, ack(), report(dmst_ord_dt="20261020", thco_ord_tmd="040100"))
    moment[0] = datetime.fromisoformat("2026-10-19T15:01:00-04:00")
    args = order(b)
    args["signal"].update(available_at=moment[0].isoformat(), valid_until=(moment[0] + timedelta(seconds=90)).isoformat())
    args["quote"].update(observed_at=moment[0].isoformat(), ingested_at=moment[0].isoformat())
    args["account"].update(observed_at=moment[0].isoformat(), ingested_at=moment[0].isoformat())
    b.submit(**args)
    assert b.reconcile(intent_id="us-intent-1")["status"] == "OPEN"
    assert s.calls[-1][2]["params"]["ORD_STRT_DT"] == "20261019"
    b.close()


def test_future_cancel_child_is_not_evidence(tmp_path):
    child = {**report().payload["output"][0], "odno": "456", "orgn_odno": "123", "rvse_cncl_dvsn": "02",
             "prcs_stat_name": "완료", "nccs_qty": "0", "thco_ord_tmd": "230200"}
    final = report(remaining=0)
    final.payload["output"].append(child)
    b, _, _, _ = make(tmp_path, ack(), report(), ack("456"), final)
    b.submit(**order(b))
    b.cancel(intent_id="us-intent-1")
    with pytest.raises(DemoError):
        b.reconcile(intent_id="us-intent-1")
    assert b.db.execute("SELECT status FROM order_state").fetchone()[0] == "OPEN"
    b.close()
