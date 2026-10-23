"""Public metadata boundary and point-in-time projection; no external API."""
from copy import deepcopy
from datetime import datetime, timezone
from unittest.mock import Mock

import pytest

from tradingagents.portfolio.kis import KisClient, PortfolioConfigurationError
from tradingagents.portfolio.security_metadata import collect_security_metadata, security_metadata_candidate


PATH = "/uapi/overseas-price/v1/quotations/search-info"
ASOF = datetime(2026, 10, 23, 1, tzinfo=timezone.utc)


def snapshot():
    return {
        "schema": "kis.current-security-metadata/v1", "provider": "KIS", "environment": "real",
        "symbol": "GEV", "exchange": "NYS", "product_type": "513",
        "collection_started_at": "2026-10-23T00:00:00+00:00",
        "available_at": "2026-10-23T00:00:01+00:00",
        "payload": {"rt_cd": "0", "output": {
            "istt_usge_isin_cd": "US36828A1016", "lstg_dt": "20240402",
            "tr_crcy_cd": "USD", "ovrs_excg_cd": "NYS",
            "ovrs_now_pric1": "999", "last_rcvg_dtime": "20240402000000",
        }},
    }


def client(environment="real"):
    session = Mock()
    response = Mock(status_code=200, headers={})
    response.json.return_value = snapshot()["payload"]
    session.request.return_value = response
    token = Mock(status_code=200)
    token.json.return_value = {"access_token": "test", "expires_in": 86400}
    session.post.return_value = token
    return KisClient(app_key="test", app_secret="test", environment=environment,
                     session=session, token_file_cache_enabled=False), session


def test_explicit_public_real_reader_preserves_fixed_request_and_clock():
    reader, session = client()
    before = datetime.now(timezone.utc)
    result = collect_security_metadata(reader, "GEV", exchange="NYS")
    after = datetime.now(timezone.utc)
    assert before <= datetime.fromisoformat(result["collection_started_at"]) <= after
    assert before <= datetime.fromisoformat(result["available_at"]) <= after
    request = session.request.call_args.kwargs
    assert request["method"] == "GET"
    assert request["url"] == "https://openapi.koreainvestment.com:9443" + PATH
    assert request["params"] == {"PRDT_TYPE_CD": "513", "PDNO": "GEV"}
    assert request["headers"]["tr_id"] == "CTPF1702R"
    assert request["allow_redirects"] is False


@pytest.mark.parametrize("environment,params,tr_cont", [
    ("demo", {"PRDT_TYPE_CD": "513", "PDNO": "GEV"}, ""),
    ("real", None, ""), ("real", {}, ""),
    ("real", {"PRDT_TYPE_CD": "513", "PDNO": "gev"}, ""),
    ("real", {"PRDT_TYPE_CD": "513", "PDNO": "GEV", "CANO": "123"}, ""),
    ("real", {"PRDT_TYPE_CD": "999", "PDNO": "GEV"}, ""),
    ("real", {"PRDT_TYPE_CD": "513", "PDNO": "GEV"}, "N"),
    ("real", {"PRDT_TYPE_CD": "513", "PDNO": "GEV?x=1"}, ""),
])
def test_bad_request_never_authenticates(environment, params, tr_cont):
    reader, session = client(environment)
    with pytest.raises(PortfolioConfigurationError):
        reader.request_json(method="GET", path=PATH, tr_id="CTPF1702R", params=params, tr_cont=tr_cont)
    session.post.assert_not_called()
    session.request.assert_not_called()


def test_demo_collection_and_unknown_market_never_authenticate():
    reader, session = client("demo")
    with pytest.raises(PortfolioConfigurationError):
        collect_security_metadata(reader, "GEV", exchange="NYS")
    with pytest.raises(PortfolioConfigurationError):
        reader.overseas_product_info_raw("GEV", exchange="OTC")
    session.post.assert_not_called()
    session.request.assert_not_called()


def test_candidate_is_not_historical_authorization_or_quote():
    original = snapshot()
    result = security_metadata_candidate(original, analysis_as_of=ASOF)
    assert result["isin"] == "US36828A1016"
    assert not result["issuer_binding_verified"]
    assert not result["first_regular_listing_verified"]
    assert not result["historical_identity_verified"]
    assert not result["price_history_shortening_authorized"]
    assert "ovrs_now_pric1" not in result and "last_rcvg_dtime" not in result
    assert original == snapshot()


@pytest.mark.parametrize("key,value", [
    ("available_at", None), ("available_at", ""), ("available_at", "bad"),
    ("available_at", "2026-10-23T00:00:01"),
    ("available_at", "2026-10-24T00:00:00+00:00"),
    ("collection_started_at", "2026-10-23T02:00:00+00:00"),
    ("collection_started_at", None), ("environment", "demo"),
    ("exchange", "OTC"), ("product_type", "512"), ("symbol", "GEV?x"),
])
def test_envelope_missing_invalid_future_is_rejected(key, value):
    item = snapshot()
    item[key] = value
    with pytest.raises(ValueError):
        security_metadata_candidate(item, analysis_as_of=ASOF)


@pytest.mark.parametrize("key,value", [
    ("lstg_dt", "20261024"), ("lstg_dt", None), ("lstg_dt", "20240230"),
    ("lstg_dt", "2024-04-02"), ("istt_usge_isin_cd", "US36828A1010"),
    ("istt_usge_isin_cd", None), ("istt_usge_isin_cd", "bad"),
    ("ovrs_excg_cd", ""), ("ovrs_excg_cd", None), ("tr_crcy_cd", "EUR"),
])
def test_missing_future_bad_date_and_identity_are_rejected(key, value):
    item = snapshot()
    item["payload"]["output"][key] = value
    with pytest.raises(ValueError):
        security_metadata_candidate(item, analysis_as_of=ASOF)


@pytest.mark.parametrize("payload", [{}, {"rt_cd": "1"}, {"rt_cd": "0", "output": {}},
                                    {"rt_cd": "0", "output": []},
                                    {"rt_cd": "0", "output": [snapshot()["payload"]["output"]]}])
def test_empty_error_ambiguous_response_rejected(payload):
    item = deepcopy(snapshot())
    item["payload"] = payload
    with pytest.raises(ValueError):
        security_metadata_candidate(item, analysis_as_of=ASOF)


def test_cutoff_is_required_aware_and_no_backdating_from_listing_date():
    with pytest.raises(ValueError):
        security_metadata_candidate(snapshot(), analysis_as_of=ASOF.replace(tzinfo=None))
    with pytest.raises(ValueError):
        security_metadata_candidate(snapshot(), analysis_as_of=datetime(2024, 4, 2, tzinfo=timezone.utc))
    at_collection = datetime.fromisoformat(snapshot()["available_at"])
    assert security_metadata_candidate(snapshot(), analysis_as_of=at_collection)["isin"]
