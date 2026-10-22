from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from threading import Barrier, Event
from unittest.mock import Mock

import pytest

from tradingagents.dataflows.intraday.ranking_batch import (
    ObservedRankingResponse, RankingBatch, ranking_batch_context, read_market_ranking,
)
from tradingagents.portfolio.kis import KisClient


NOW = datetime(2026, 10, 22, 14, 30, tzinfo=timezone.utc)
RESPONSE = ({"rt_cd": "0", "output2": [
    {"symb": "AAPL", "published_at": "2026-10-22T14:29:00+00:00", "nested": {"value": 1}},
    {"symb": "MSFT", "rank": "2"},
]}, {"Date": "Thu, 22 Oct 2026 14:30:00 GMT"})
REQUEST = {"method": "GET", "path": "/uapi/overseas-stock/v1/ranking/volume-power",
           "tr_id": "HHDFS76280000", "tr_cont": "",
           "params": {"EXCD": "NAS", "NDAY": "0", "VOL_RANG": "0", "AUTH": "", "KEYB": ""}}


def client(**kwargs):
    result = KisClient(app_key=kwargs.pop("app_key", "fixture-key"),
                       app_secret=kwargs.pop("app_secret", "fixture-secret"), **kwargs)
    result.request_json = Mock(side_effect=lambda **kw: deepcopy(RESPONSE))
    return result


def test_thirty_independent_clients_share_one_original_response_and_first_observation():
    times = iter([NOW, NOW + timedelta(seconds=1), *[NOW + timedelta(seconds=50)] * 30])
    batch = RankingBatch(clock=lambda: next(times))
    clients = [client() for _ in range(30)]
    with ranking_batch_context(batch):
        responses = [item.overseas_volume_power(exchange="NAS") for item in clients]
    assert sum(item.request_json.call_count for item in clients) == 1
    assert len({id(item.session) for item in clients}) == 30
    assert len({id(item._token_thread_lock) for item in clients}) == 30
    assert all(response == RESPONSE for response in responses)
    assert all(response.observed_at == (NOW + timedelta(seconds=1)).isoformat() for response in responses)
    responses[0][0]["output2"][0]["nested"]["value"] = 999
    responses[0][1]["Date"] = "changed"
    assert responses[1] == RESPONSE
    assert clients[0].request_json.call_args.kwargs == REQUEST
    batch.close()


@pytest.mark.parametrize("kwargs", [
    {"exchange": "NYS"}, {"nday": "1"}, {"volume_range": "1"},
    {"auth": "different"}, {"keyb": "next-page"}, {"tr_cont": "N"},
])
def test_complete_request_parameters_have_distinct_keys(kwargs):
    item = client()
    batch = RankingBatch(clock=lambda: NOW)
    with ranking_batch_context(batch):
        item.overseas_volume_power(exchange="NAS")
        item.overseas_volume_power(**{"exchange": "NAS", **kwargs})
        item.overseas_volume_power(**{"exchange": "NAS", **kwargs})
    assert item.request_json.call_count == 2


@pytest.mark.parametrize("scope", [
    {"app_key": "different"}, {"app_secret": "different"}, {"environment": "demo"},
    {"app_key": "fixture", "app_secret": "key:fixture-secret"},
])
def test_credentials_and_environment_are_isolated(scope):
    first, second = client(), client(**scope)
    with ranking_batch_context(RankingBatch(clock=lambda: NOW)):
        first.overseas_volume_power(exchange="NAS")
        second.overseas_volume_power(exchange="NAS")
    assert first.request_json.call_count == second.request_json.call_count == 1


def test_invalid_host_is_revalidated_on_cache_hit():
    item = client()
    with ranking_batch_context(RankingBatch(clock=lambda: NOW)):
        item.overseas_volume_power(exchange="NAS")
        item.base_url = "https://untrusted.invalid"
        with pytest.raises(ValueError):
            item.overseas_volume_power(exchange="NAS")
    assert item.request_json.call_count == 1


@pytest.mark.parametrize("change", [{"path": "/other"}, {"tr_id": "OTHER"},
                                    {"method": "POST"}, {"body": {"x": 1}}])
def test_other_requests_never_share(change):
    item = client()
    with ranking_batch_context(RankingBatch(clock=lambda: NOW)):
        for _ in range(2):
            read_market_ranking(item, **{**REQUEST, **change})
    assert item.request_json.call_count == 2


def test_unknown_identity_and_direct_calls_preserve_original_response_contract():
    item = client()
    for _ in range(2):
        assert type(item.overseas_volume_power(exchange="NAS")) is tuple
    del item.app_key
    with ranking_batch_context(RankingBatch(clock=lambda: NOW)):
        for _ in range(2):
            assert type(item.overseas_volume_power(exchange="NAS")) is tuple
    assert item.request_json.call_count == 4


def test_next_batch_and_context_cleanup_require_new_reads():
    item = client()
    for _ in range(2):
        batch = RankingBatch(clock=lambda: NOW)
        with ranking_batch_context(batch):
            assert isinstance(item.overseas_volume_power(exchange="NAS"), ObservedRankingResponse)
        batch.close()
    assert type(item.overseas_volume_power(exchange="NAS")) is tuple
    assert item.request_json.call_count == 3


@pytest.mark.parametrize("bad", [None, {}, ({}, {}), ({"output2": []}, {}),
    ({"rt_cd": "1", "output2": [{"symb": "AAPL"}]}, {}),
    ({"output2": [{"unknown": "x"}]}, {}), ({"output2": [None]}, {}),
    ({"output2": [{"symb": "AAPL"}]}, None)])
def test_empty_and_malformed_responses_are_not_memoized(bad):
    item = client()
    item.request_json.side_effect = [deepcopy(bad), deepcopy(RESPONSE)]
    with ranking_batch_context(RankingBatch(clock=lambda: NOW)):
        assert item.overseas_volume_power(exchange="NAS") == bad
        assert item.overseas_volume_power(exchange="NAS") == RESPONSE
        assert item.overseas_volume_power(exchange="NAS") == RESPONSE
    assert item.request_json.call_count == 2


def test_failure_is_removed_and_original_request_can_retry():
    item = client()
    item.request_json.side_effect = [RuntimeError("temporary"), deepcopy(RESPONSE)]
    with ranking_batch_context(RankingBatch(clock=lambda: NOW)):
        with pytest.raises(RuntimeError, match="temporary"):
            item.overseas_volume_power(exchange="NAS")
        item.overseas_volume_power(exchange="NAS")
        item.overseas_volume_power(exchange="NAS")
    assert item.request_json.call_count == 2


def test_successful_owner_uses_original_broker_retry_without_authentication_changes(monkeypatch):
    from tradingagents.portfolio import kis
    retry = Mock(status_code=500, headers={})
    retry.json.return_value = {"rt_cd": "1", "msg_cd": "TEMPORARY"}
    success = Mock(status_code=200, headers={})
    success.json.return_value = deepcopy(RESPONSE[0])
    session = Mock()
    session.request.side_effect = [retry, success]
    item = KisClient(app_key="fixture", app_secret="fixture", session=session)
    item.ensure_access_token = Mock(return_value="fixture-token")
    item.issue_access_token = Mock(side_effect=AssertionError("no auth refresh expected"))
    sleep = Mock()
    monkeypatch.setattr(kis, "_sleep_before_kis_retry", sleep)
    monkeypatch.setenv("KIS_API_MAX_RETRIES", "3")
    with ranking_batch_context(RankingBatch(clock=lambda: NOW)):
        assert item.overseas_volume_power(exchange="NAS")[0] == RESPONSE[0]
        assert item.overseas_volume_power(exchange="NAS")[0] == RESPONSE[0]
    assert session.request.call_count == 2
    assert item.ensure_access_token.call_count == 2
    item.issue_access_token.assert_not_called()
    sleep.assert_called_once()
    assert all(call.kwargs["timeout"] == item.timeout_seconds for call in session.request.call_args_list)


def test_concurrent_singleflight_preserves_independent_clients():
    batch = RankingBatch(clock=lambda: NOW)
    gate, release, entered = Barrier(5), Event(), Event()
    clients = [client() for _ in range(4)]
    def request(**kwargs):
        entered.set()
        assert release.wait(5)
        return deepcopy(RESPONSE)
    for item in clients:
        item.request_json.side_effect = request
    def fetch(item):
        with ranking_batch_context(batch):
            gate.wait()
            return item.overseas_volume_power(exchange="NAS")
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = [pool.submit(fetch, item) for item in clients]
        gate.wait()
        assert entered.wait(5)
        release.set()
        responses = [future.result(timeout=5) for future in futures]
    assert sum(item.request_json.call_count for item in clients) == 1
    assert all(response == RESPONSE and response.observed_at == NOW.isoformat() for response in responses)


def test_close_unblocks_inflight_and_prevents_late_repopulation():
    batch, item, entered, release = RankingBatch(clock=lambda: NOW), client(), Event(), Event()
    def request(**kwargs):
        entered.set()
        assert release.wait(5)
        return deepcopy(RESPONSE)
    item.request_json.side_effect = request
    with ThreadPoolExecutor(max_workers=2) as pool:
        owner = pool.submit(batch.read, item, REQUEST)
        assert entered.wait(5)
        follower = pool.submit(batch.read, client(), REQUEST)
        batch.close()
        release.set()
        for future in (owner, follower):
            with pytest.raises(ValueError, match="closed"):
                future.result(timeout=5)
    assert not batch._reads
    with pytest.raises(ValueError, match="closed"):
        batch.read(item, REQUEST)
    assert item.request_json.call_count == 1
    del item.app_key
    with pytest.raises(ValueError, match="closed"):
        batch.read(item, REQUEST)
    assert item.request_json.call_count == 1


@pytest.mark.parametrize("invalid", [None, "bad", "2026-10-22", datetime(2026, 10, 22)])
def test_missing_malformed_naive_observation_is_not_saved(invalid):
    current = [NOW]
    batch, item = RankingBatch(clock=lambda: current[0]), client()
    current[0] = invalid
    with pytest.raises(ValueError, match="aware"):
        batch.read(item, REQUEST)
    current[0] = NOW
    assert batch.read(item, REQUEST) == RESPONSE
    assert item.request_json.call_count == 2


def test_future_observation_and_regression_are_rejected_without_retention():
    clocks = iter([NOW, NOW + timedelta(seconds=1), NOW, NOW, NOW])
    batch, item = RankingBatch(clock=lambda: next(clocks)), client()
    with pytest.raises(ValueError, match="future"):
        batch.read(item, REQUEST)
    assert batch.read(item, REQUEST).observed_at == NOW.isoformat()
    assert item.request_json.call_count == 2
    regressed = RankingBatch(clock=lambda: NOW)
    regressed._clock = lambda: NOW - timedelta(seconds=1)
    with pytest.raises(ValueError, match="regressed"):
        regressed.read(item, REQUEST)
    assert not regressed._reads


def test_parameter_input_and_returned_nested_values_are_copy_isolated():
    request, item = deepcopy(REQUEST), client()
    def fetch(**kwargs):
        kwargs["params"]["EXCD"] = "MUTATED"
        return RESPONSE
    item.request_json.side_effect = fetch
    batch = RankingBatch(clock=lambda: NOW)
    response = batch.read(item, request)
    assert request == REQUEST
    response[0]["output2"][0]["nested"]["value"] = 999
    assert batch.read(item, request) == RESPONSE
    assert RESPONSE[0]["output2"][0]["nested"]["value"] == 1
    assert item.request_json.call_count == 1


def test_real_runner_scopes_shared_reads_to_each_checkpoint(monkeypatch, tmp_path):
    from tradingagents.scheduled import runner
    from tradingagents.scheduled.config import load_scheduled_config
    config_file = tmp_path / "config.toml"
    config_file.write_text('[run]\ntickers=["AAPL", "MSFT"]\nmarket="US"\n'
                           '[execution]\nenabled=true\ncheckpoint_timezone="America/New_York"\n')
    config = load_scheduled_config(config_file)
    rows, clients = [], []
    for ticker in ("AAPL", "MSFT"):
        path = tmp_path / ticker / "execution_contract.json"
        path.parent.mkdir()
        path.write_text("{}")
        rows.append({"ticker": ticker, "status": "success", "artifacts": {
            "execution_contract_json": path.relative_to(tmp_path).as_posix()}})
    def fetch(ticker, **kwargs):
        item = client()
        clients.append(item)
        return item.overseas_volume_power(exchange="NAS")
    monkeypatch.setattr(runner, "fetch_intraday_market_snapshot", fetch)
    for checkpoint in ("10:30", "10:31"):
        result = runner._fetch_overlay_market_snapshots(config=config, ticker_summaries=rows,
            run_dir=tmp_path, checkpoint_label=checkpoint)
        assert all(isinstance(value, ObservedRankingResponse) for value in result.values())
    assert len(clients) == 4
    assert sum(item.request_json.call_count for item in clients) == 2
    assert type(clients[0].overseas_volume_power(exchange="NAS")) is tuple
    assert sum(item.request_json.call_count for item in clients) == 3
