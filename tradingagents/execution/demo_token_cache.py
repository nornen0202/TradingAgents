"""Optional user-scoped DPAPI token reuse for scheduled VTS-only clients.

Only ciphertext reaches disk. Credential/market binding prevents cross-account
or KR/US key reuse, and a process lock serializes token issuance across ticks.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import tempfile

from tradingagents.atomic_io import interprocess_file_lock
from .demo_secrets import SecretStoreError, _crypt, storage_path
from .kis_demo import DemoNotSentError


def _instant(value):
    if isinstance(value, str):
        value = datetime.fromisoformat(value)
    if not isinstance(value, datetime) or value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("Aware token clock required")
    return value.astimezone(timezone.utc)


def _write(path, data):
    encrypted = _crypt(json.dumps(data).encode("utf-8"), decrypt=False)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix="vts-token-", suffix=".tmp", delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(encrypted)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def cache_demo_authentication(client, *, market, path=None):
    """Attach encrypted caching to a dedicated VTS client instance only.

    Linux/offline tests can inject a path and protect/unprotect implementation.
    Production outside Windows retains the original memory-only authentication.
    """
    from .kis_demo import KisDemoClient
    from .kis_demo_us import KisDemoUSReadClient
    if market not in {"KR", "US"} or not isinstance(client, (KisDemoClient, KisDemoUSReadClient)):
        raise DemoNotSentError("Dedicated VTS client and market required")
    if (market == "KR") != isinstance(client, KisDemoClient):
        raise DemoNotSentError("Token market and VTS client differ")
    if path is None and os.name != "nt":
        return client
    destination = Path(path) if path is not None else storage_path().with_name(f"kis-demo-{market.lower()}-token.dpapi")
    credentials = client.credentials
    binding = hashlib.sha256(json.dumps(["VTS", market, credentials.app_key, credentials.app_secret,
        credentials.account_no, credentials.product_code], separators=(",", ":")).encode()).hexdigest()
    authenticate = client.authenticate

    def cached_authenticate():
        try:
            now = _instant(client.utcnow())
            if client._token and now < _instant(client._expires):
                return
            with interprocess_file_lock(destination.with_suffix(".lock"), timeout=20):
                now = _instant(client.utcnow())
                try:
                    saved = json.loads(_crypt(destination.read_bytes(), decrypt=True))
                    issued, expires = _instant(saved["issued_at"]), _instant(saved["expires_at"])
                    token = saved["token"]
                    if (saved["binding"] == binding and issued <= now < expires
                            and 0 < (expires - issued).total_seconds() <= 86400
                            and isinstance(token, str) and token and len(token) <= 16384):
                        client._token, client._expires = token, expires
                        return
                except (OSError, ValueError, TypeError, KeyError, SecretStoreError):
                    pass  # An unreadable/expired cache never supplies authorization.
                authenticate()
                completed = _instant(client.utcnow())
                expires = _instant(client._expires)
                if completed < now or not client._token or not completed < expires:
                    raise DemoNotSentError("VTS token observation is invalid")
                _write(destination, {"binding": binding, "issued_at": now.isoformat(),
                    "expires_at": expires.isoformat(), "token": client._token})
        except (OSError, ValueError, TimeoutError, SecretStoreError):
            # Token issuance may have succeeded before protected persistence
            # failed. Do not let the next call bypass that failure via memory.
            client._token = None
            client._expires = datetime.min.replace(tzinfo=timezone.utc)
            raise DemoNotSentError("Protected VTS token cache is unavailable") from None

    client.authenticate = cached_authenticate
    return client
