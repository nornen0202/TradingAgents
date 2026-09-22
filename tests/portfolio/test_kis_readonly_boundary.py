"""No broker access: enforce the real-account reader's network boundary."""

from types import SimpleNamespace
from unittest.mock import Mock, patch

import pytest

from tradingagents.portfolio.account_models import AccountConstraints
from tradingagents.portfolio.kis import (
    DEMO_BASE_URL,
    REAL_BASE_URL,
    KisApiError,
    KisClient,
    PortfolioConfigurationError,
    _extract_cash_snapshot,
)


BALANCE = "/uapi/domestic-stock/v1/trading/inquire-balance"


def client_for(environment="real"):
    session = Mock()
    response = Mock(status_code=200, headers={})
    response.json.return_value = {"rt_cd": "0", "output": []}
    session.request.return_value = response
    token = Mock(status_code=200)
    token.json.return_value = {"access_token": "test-token", "expires_in": 86400}
    session.post.return_value = token
    client = KisClient(
        app_key="test-key",
        app_secret="test-secret",
        environment=environment,
        session=session,
        token_file_cache_enabled=False,
    )
    return client, session


@pytest.mark.parametrize("method,path,tr_id,body", [
    ("POST", "/uapi/domestic-stock/v1/trading/order-cash", "TTTC0012U", {}),
    ("POST", "/uapi/domestic-stock/v1/trading/order-rvsecncl", "TTTC0013U", {}),
    ("GET", "/uapi/domestic-stock/v1/trading/order-cash", "TTTC0012U", None),
    ("DELETE", BALANCE, "TTTC8434R", None),
    ("POST", BALANCE, "TTTC8434R", None),
    ("GET", BALANCE, "TTTC0012U", None),
    ("GET", BALANCE, "VTTC8434R", None),
    ("GET", BALANCE, "TTTC8434R", {}),
    ("GET", BALANCE + "?redirect=1", "TTTC8434R", None),
    ("GET", "https://other.invalid/", "TTTC8434R", None),
    ("GET", "/oauth2/tokenP", "TTTC8434R", None),
    ("GET", "/uapi/domestic-stock/v1/trading/unknown", "TTTC8434R", None),
])
def test_forbidden_requests_fail_before_authentication(method, path, tr_id, body):
    client, session = client_for()
    with pytest.raises(PortfolioConfigurationError, match="read-only"):
        client.request_json(method=method, path=path, tr_id=tr_id, body=body)
    session.post.assert_not_called()
    session.request.assert_not_called()


@pytest.mark.parametrize("environment", ["", "paper", "REAL", "real ", "production", None])
def test_invalid_environment_never_falls_back_to_real(environment):
    with pytest.raises(PortfolioConfigurationError, match="environment"):
        client_for(environment)
    with patch("tradingagents.portfolio.kis.get_api_key") as key:
        with pytest.raises(PortfolioConfigurationError, match="environment"):
            KisClient.from_api_keys(environment=environment)
        key.assert_not_called()


@pytest.mark.parametrize("environment,path,tr_id", [
    ("real", BALANCE, "TTTC8434R"),
    ("demo", BALANCE, "VTTC8434R"),
    ("real", "/uapi/domestic-stock/v1/quotations/inquire-price", "FHKST01010100"),
    ("real", "/uapi/overseas-stock/v1/trading/inquire-present-balance", "CTRP6504R"),
    ("real", "/uapi/overseas-stock/v1/trading/inquire-period-profit", "TTTS3039R"),
    ("real", "/uapi/domestic-stock/v1/trading/inquire-daily-ccld", "CTSC9215R"),
    ("real", "/uapi/domestic-stock/v1/trading/period-rights", "CTRGA011R"),
    ("real", "/uapi/overseas-price/v1/quotations/dailyprice", "HHDFS76240000"),
])
def test_quote_account_and_performance_reads_keep_fixed_host(environment, path, tr_id):
    client, session = client_for(environment)
    payload, _ = client.request_json(method="GET", path=path, tr_id=tr_id)
    assert payload["rt_cd"] == "0"
    host = DEMO_BASE_URL if environment == "demo" else REAL_BASE_URL
    assert session.request.call_args.kwargs["url"] == host + path
    assert session.request.call_args.kwargs["allow_redirects"] is False
    assert session.post.call_args.args[0] == host + "/oauth2/tokenP"
    assert session.post.call_args.kwargs["allow_redirects"] is False


def test_demo_cannot_use_real_credentials_or_real_account_tr_id():
    with patch("tradingagents.portfolio.kis.get_api_key") as key:
        key.side_effect = lambda name: {"KIS_APP_KEY": "real", "KIS_APP_SECRET": "real"}.get(name)
        with pytest.raises(PortfolioConfigurationError, match="KIS_DEMO"):
            KisClient.from_api_keys(environment="demo")
        assert {call.args[0] for call in key.call_args_list} == {
            "KIS_DEMO_APP_KEY", "KIS_DEMO_APP_SECRET"
        }
    client, session = client_for("demo")
    with pytest.raises(PortfolioConfigurationError):
        client.request_json(method="GET", path=BALANCE, tr_id="TTTC8434R")
    session.post.assert_not_called()
    session.request.assert_not_called()


def test_demo_factory_uses_dedicated_keys():
    with patch("tradingagents.portfolio.kis.get_api_key") as key:
        key.side_effect = lambda name: {
            "KIS_DEMO_APP_KEY": "demo-key", "KIS_DEMO_APP_SECRET": "demo-secret"
        }.get(name)
        client = KisClient.from_api_keys(environment="demo")
    assert client.app_key == "demo-key"
    assert client.app_secret == "demo-secret"
    assert client.base_url == DEMO_BASE_URL


def test_modified_host_is_rejected_before_authentication():
    client, session = client_for()
    client.base_url = "https://other.invalid"
    with pytest.raises(PortfolioConfigurationError, match="host"):
        client.request_json(method="GET", path=BALANCE, tr_id="TTTC8434R")
    with pytest.raises(PortfolioConfigurationError, match="host"):
        client.issue_access_token(force=True)
    session.post.assert_not_called()
    session.request.assert_not_called()


@pytest.mark.parametrize("redirect_at", ["token", "read"])
def test_redirect_response_is_not_a_success_or_followed(redirect_at):
    client, session = client_for()
    if redirect_at == "token":
        session.post.return_value.status_code = 302
    else:
        session.request.return_value.status_code = 307
    with pytest.raises(KisApiError, match="redirect"):
        client.request_json(method="GET", path=BALANCE, tr_id="TTTC8434R")
    assert session.post.call_count == 1
    assert session.request.call_count == (0 if redirect_at == "token" else 1)


def cash_snapshot(summary, positions=2_000_000, market="kr"):
    profile = SimpleNamespace(market_scope=market, constraints=AccountConstraints())
    return _extract_cash_snapshot(
        summary_payload=summary, positions_market_value=positions, profile=profile
    )


def test_explicit_zero_cash_and_buying_power_stay_zero():
    snapshot = cash_snapshot({"dnca_tot_amt": "500000", "ord_psbl_cash": "0", "buy_psbl_amt": "0"})
    assert snapshot["settled_cash_krw"] == 500_000
    assert snapshot["available_cash_krw"] == 0
    assert snapshot["buying_power_krw"] == 0
    assert snapshot["snapshot_health"] == "CAPITAL_CONSTRAINED"


@pytest.mark.parametrize("reported", ["0", "-500000", "1500000"])
def test_reported_equity_not_inflated_by_holdings_or_credit(reported):
    snapshot = cash_snapshot({
        "dnca_tot_amt": "500000", "ord_psbl_cash": "300000", "buy_psbl_amt": "9000000",
        "nass_amt": reported,
    })
    assert snapshot["total_equity_krw"] == int(reported)
    assert snapshot["cash_diagnostics"]["selected_fields"]["total_equity"] == "nass_amt"


def test_missing_cash_fields_keep_deposit_fallback():
    snapshot = cash_snapshot({"dnca_tot_amt": "500000"})
    assert snapshot["available_cash_krw"] == 500_000
    assert snapshot["buying_power_krw"] == 500_000


def test_missing_equity_falls_back_without_counting_buying_power_as_equity():
    snapshot = cash_snapshot({"dnca_tot_amt": "500000", "buy_psbl_amt": "9000000"})
    assert snapshot["buying_power_krw"] == 9_000_000
    assert snapshot["total_equity_krw"] == 2_500_000
    assert any("fell back" in warning for warning in snapshot["warnings"])


def test_domestic_stock_valuation_cannot_override_total_equity():
    snapshot = cash_snapshot({
        "dnca_tot_amt": "500000", "evlu_amt_smtl_amt": "2000000", "tot_evlu_amt": "2500000",
    })
    assert snapshot["total_equity_krw"] == 2_500_000
    assert snapshot["cash_diagnostics"]["selected_fields"]["total_equity"] == "tot_evlu_amt"


def test_overseas_foreign_component_cannot_override_won_net_assets():
    snapshot = cash_snapshot({"frcr_evlu_tota": "77589", "nass_amt": "26000000"}, market="us")
    assert snapshot["total_equity_krw"] == 26_000_000
    selected = snapshot["cash_diagnostics"]["selected_fields"]
    assert selected["total_equity"] == "nass_amt"
    assert "frcr_evlu_tota" not in selected["total_equity_candidates"]


@pytest.mark.parametrize("market,field", [
    ("kr", "evlu_amt_smtl_amt"), ("us", "frcr_evlu_tota"),
])
def test_component_valuation_alone_retains_fallback_diagnostic(market, field):
    snapshot = cash_snapshot({field: "77589", "dnca_tot_amt": "500000"}, market=market)
    assert snapshot["total_equity_krw"] == 2_500_000
    assert snapshot["cash_diagnostics"]["selected_fields"]["total_equity"] is None
    assert snapshot["cash_diagnostics"]["selected_fields"]["total_equity_candidates"] == {}
    assert snapshot["cash_diagnostics"]["parsed_numeric_fields"][field] == 77_589
    assert any("trusted total-equity" in warning for warning in snapshot["warnings"])


@pytest.mark.parametrize("market,field", [("kr", "nass_amt"), ("us", "tot_asst_amt")])
@pytest.mark.parametrize("reported", ["0", "-500000"])
def test_market_specific_authoritative_zero_or_negative_is_preserved(market, field, reported):
    snapshot = cash_snapshot({field: reported, "tot_evlu_amt": "2500000"}, market=market)
    assert snapshot["total_equity_krw"] == int(reported)
    assert snapshot["cash_diagnostics"]["selected_fields"]["total_equity"] == field


@pytest.mark.parametrize("invalid", [float("inf"), float("-inf"), float("nan"), "1e9999", True])
def test_invalid_numeric_equity_falls_back_without_overflow(invalid):
    snapshot = cash_snapshot({"nass_amt": invalid, "dnca_tot_amt": "500000"})
    assert snapshot["total_equity_krw"] == 2_500_000
    assert snapshot["cash_diagnostics"]["selected_fields"]["total_equity"] is None
