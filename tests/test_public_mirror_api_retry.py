import importlib.util
import io
from urllib.error import HTTPError, URLError

import pytest


spec = importlib.util.spec_from_file_location("mirror_retry", ".github/scripts/publish_ai_context.py")
mirror = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mirror)


def test_transient_tree_creation_failure_replays_exact_payload(monkeypatch):
    monkeypatch.setenv("GH_TOKEN", "test-token")
    requests, delays = [], []
    def open_request(request, timeout):
        requests.append((request.method, request.data))
        if len(requests) == 1:
            raise HTTPError(request.full_url, 500, "unavailable", {}, None)
        return io.BytesIO(b'{"sha":"tree"}')
    monkeypatch.setattr(mirror, "urlopen", open_request)
    monkeypatch.setattr(mirror.time, "sleep", delays.append)
    assert mirror.api("/git/trees", "POST", {"tree": []}) == {"sha": "tree"}
    assert requests[0] == requests[1] and delays == [1]


@pytest.mark.parametrize("code", [401, 403, 404, 409, 422])
def test_permission_and_conflict_failures_are_not_retried(monkeypatch, code):
    monkeypatch.setenv("GH_TOKEN", "test-token")
    def fail(request, timeout):
        raise HTTPError(request.full_url, code, "failure", {}, None)
    monkeypatch.setattr(mirror, "urlopen", fail)
    monkeypatch.setattr(mirror.time, "sleep", lambda _: pytest.fail("must not retry"))
    with pytest.raises(HTTPError):
        mirror.api("/git/refs/heads/public-context", "PATCH", {"sha": "new", "force": False})


@pytest.mark.parametrize("error", [URLError("offline"), TimeoutError(), HTTPError("url", 503, "failure", {}, None)])
def test_retries_are_bounded_and_failure_is_reported(monkeypatch, error):
    monkeypatch.setenv("GH_TOKEN", "test-token")
    requests, delays = [], []
    def fail(request, timeout):
        requests.append(request)
        raise error
    monkeypatch.setattr(mirror, "urlopen", fail)
    monkeypatch.setattr(mirror.time, "sleep", delays.append)
    with pytest.raises(type(error)):
        mirror.api("/git/trees", "POST", {"tree": []})
    assert len(requests) == 4 and delays == [1, 3, 7]
