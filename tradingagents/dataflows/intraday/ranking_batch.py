"""Share successful US ranking reads only within one execution checkpoint.

The response observation is acquisition time, never an exchange event clock.
Clients, sessions, authentication and their ordinary request retries stay local
to each caller. Nothing here caches quotes, accounts, orders or later batches.
"""
from __future__ import annotations

from collections.abc import Mapping
from concurrent.futures import Future
from contextlib import contextmanager
from contextvars import ContextVar
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import hmac
import json
import os
from threading import Lock


_CURRENT: ContextVar[RankingBatch | None] = ContextVar("market_ranking_batch", default=None)
_PATH = "/uapi/overseas-stock/v1/ranking/volume-power"
_TR = "HHDFS76280000"


def _instant(value):
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("Ranking observation requires an aware clock")
    return value.astimezone(timezone.utc)


class ObservedRankingResponse(tuple):
    """Keep the existing (JSON, headers) contract and separate acquisition time."""

    def __new__(cls, response, observed_at):
        result = super().__new__(cls, response)
        result.observed_at = observed_at
        return result


def _shareable(response):
    if not isinstance(response, tuple) or len(response) != 2:
        return False
    payload, headers = response
    if not isinstance(payload, dict) or not isinstance(headers, Mapping):
        return False
    if str(payload.get("rt_cd", "0")) not in {"0", ""}:
        return False
    rows = payload.get("output2") or payload.get("output")
    if isinstance(rows, dict):
        rows = [rows]
    return bool(isinstance(rows, list) and rows and all(
        isinstance(row, dict) and isinstance(
            row.get("symb") or row.get("SYMB") or row.get("ovrs_pdno"), str)
        and str(row.get("symb") or row.get("SYMB") or row.get("ovrs_pdno")).strip()
        for row in rows))


class RankingBatch:
    def __init__(self, *, clock=None):
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._started = _instant(self._clock())
        self._salt = os.urandom(32)
        self._lock = Lock()
        self._reads = {}
        self._closed = False

    def _key(self, client, request):
        if (request.get("method") != "GET" or request.get("path") != _PATH
                or request.get("tr_id") != _TR or request.get("body") is not None):
            return None
        # Validate the configured host on every lookup, including cache hits.
        validate = getattr(client, "_validated_base_url", None)
        if not callable(validate):
            return None
        base = validate()
        identity = [getattr(client, "environment", None), base,
                    getattr(client, "app_key", None), getattr(client, "app_secret", None)]
        if not all(isinstance(item, str) and item for item in identity):
            return None
        scope = hmac.new(self._salt, json.dumps(identity).encode(), hashlib.sha256).digest()
        return scope, json.dumps(request, sort_keys=True, allow_nan=False)

    def read(self, client, request):
        with self._lock:
            if self._closed:
                raise ValueError("Ranking batch is closed")
        # Both the key and the actual request use this isolated parameter set.
        request = deepcopy(request)
        key = self._key(client, request)
        if key is None:
            return client.request_json(**request)
        with self._lock:
            if self._closed:
                raise ValueError("Ranking batch is closed")
            future = self._reads.get(key)
            owner = future is None
            if owner:
                future = Future()
                self._reads[key] = future
        if owner:
            try:
                response = client.request_json(**request)
                observed = _instant(self._clock())
                if observed < self._started:
                    raise ValueError("Ranking observation clock regressed")
                valid = _shareable(response)
                saved = deepcopy(response), observed if valid else None
                with self._lock:
                    if self._closed:
                        raise ValueError("Ranking batch is closed")
                    if not valid:
                        self._reads.pop(key, None)
                    future.set_result(saved)
            except BaseException as exc:
                with self._lock:
                    if self._reads.get(key) is future:
                        self._reads.pop(key, None)
                    if not future.done():
                        future.set_exception(exc)
                raise
        response, observed = future.result()
        now = _instant(self._clock())
        with self._lock:
            if self._closed:
                raise ValueError("Ranking batch is closed")
            if now < self._started or observed is not None and observed > now:
                if self._reads.get(key) is future:
                    self._reads.pop(key, None)
                raise ValueError("Ranking observation is in the future")
        response = deepcopy(response)
        return ObservedRankingResponse(response, observed.isoformat()) if observed is not None else response

    def close(self):
        with self._lock:
            self._closed = True
            for future in self._reads.values():
                if not future.done():
                    future.set_exception(ValueError("Ranking batch is closed"))
            self._reads.clear()


@contextmanager
def ranking_batch_context(batch):
    token = _CURRENT.set(batch)
    try:
        yield
    finally:
        _CURRENT.reset(token)


def read_market_ranking(client, **request):
    batch = _CURRENT.get()
    return client.request_json(**request) if batch is None else batch.read(client, request)
