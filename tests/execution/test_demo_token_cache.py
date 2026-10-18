from datetime import datetime, timedelta, timezone
import json

import pytest

from tradingagents.execution import demo_token_cache as cache
from tradingagents.execution.kis_demo import DemoCredentials, DemoNotSentError, KisDemoClient
from tradingagents.execution.kis_demo_us import KisDemoUSReadClient


NOW = datetime(2026, 10, 19, 0, 5, tzinfo=timezone.utc)


@pytest.fixture
def protect(monkeypatch):
    # Deterministic stand-in proves plaintext never reaches the file boundary.
    monkeypatch.setattr(cache, "_crypt", lambda data, decrypt: bytes(x ^ 173 for x in data))


def client(calls, *, now=NOW, market="KR", key="demo-key"):
    cls = KisDemoClient if market == "KR" else KisDemoUSReadClient
    result = cls(DemoCredentials(key, "demo-secret", "12345678", "01"), utcnow=lambda: now)
    def auth():
        calls.append(market)
        result._token, result._expires = "fixture-token-private", now + timedelta(hours=12)
    result.authenticate = auth
    return result


def test_protected_token_reused_after_process_restart(tmp_path, protect):
    calls = []
    path = tmp_path / "token.dpapi"
    first = cache.cache_demo_authentication(client(calls), market="KR", path=path)
    first.authenticate()
    assert b"fixture-token-private" not in path.read_bytes()
    second = cache.cache_demo_authentication(client(calls, now=NOW + timedelta(minutes=1)), market="KR", path=path)
    second.authenticate()
    assert calls == ["KR"]
    assert second._token == first._token


@pytest.mark.parametrize("change", ["key", "market", "expired", "future", "malformed", "invalid_expiry"])
def test_invalid_or_other_scope_cache_cannot_authorize(tmp_path, protect, change):
    calls = []
    path = tmp_path / "token.dpapi"
    cache.cache_demo_authentication(client(calls), market="KR", path=path).authenticate()
    data = json.loads(cache._crypt(path.read_bytes(), decrypt=True))
    market, key, now = "KR", "demo-key", NOW
    if change == "key": key = "other-key"
    elif change == "market": market = "US"
    elif change == "expired": now += timedelta(days=1)
    elif change == "future": data["issued_at"] = (NOW + timedelta(minutes=5)).isoformat()
    elif change == "malformed": data = []
    else: data["expires_at"] = "undated"
    path.write_bytes(cache._crypt(json.dumps(data).encode(), decrypt=False))
    cache.cache_demo_authentication(client(calls, market=market, key=key, now=now), market=market, path=path).authenticate()
    assert len(calls) == 2


def test_cache_does_not_accept_non_demo_or_market_mismatch(tmp_path, protect):
    with pytest.raises(DemoNotSentError):
        cache.cache_demo_authentication(object(), market="KR", path=tmp_path / "token")
    with pytest.raises(DemoNotSentError):
        cache.cache_demo_authentication(client([]), market="US", path=tmp_path / "token")


def test_protection_failure_stops_before_request_and_does_not_expose_token(tmp_path, monkeypatch):
    def fail(*args, **kwargs):
        raise cache.SecretStoreError("private failure text")
    monkeypatch.setattr(cache, "_crypt", fail)
    secured = cache.cache_demo_authentication(client([]), market="KR", path=tmp_path / "token")
    for _ in range(2):
        with pytest.raises(DemoNotSentError, match="Protected VTS token cache is unavailable") as error:
            secured.authenticate()
        assert "private" not in str(error.value)
        assert secured._token is None
        assert secured._expires < NOW
    assert not (tmp_path / "token").exists()
