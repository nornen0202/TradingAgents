"""User-scoped Windows DPAPI storage for a dedicated KIS demo credential bundle."""

from __future__ import annotations

import ctypes
from ctypes import wintypes
import json
import os
from pathlib import Path
import re
import tempfile

DEMO_KEYS = (
    "KIS_DEMO_APP_KEY",
    "KIS_DEMO_APP_SECRET",
    "KIS_DEMO_ACCOUNT_NO",
    "KIS_DEMO_PRODUCT_CODE",
)


class SecretStoreError(RuntimeError):
    """Never include secret values or OS exception payloads in user-facing errors."""


def storage_path():
    base = os.getenv("LOCALAPPDATA")
    if not base:
        raise SecretStoreError("Windows user storage is unavailable")
    return Path(base) / "TradingAgents" / "kis-demo.dpapi"


def credential_bundle(app_key: str, app_secret: str, account: str):
    """Three user inputs: two keys and the full 8+2 digit demo account."""
    if not re.fullmatch(r"[0-9]{8}[- ]?[0-9]{2}", account.strip()):
        raise SecretStoreError(
            "Enter the complete demo account: 8 digits plus 2 product digits"
        )
    number = account.strip().replace("-", "").replace(" ", "")
    values = (app_key.strip(), app_secret.strip(), number[:8], number[8:])
    if any(
        not v
        or any(c.isspace() for c in v)
        or v.upper() in {"TODO", "CHANGEME", "YOUR_KEY"}
        for v in values
    ):
        raise SecretStoreError("Three complete demo inputs are required")
    return dict(zip(DEMO_KEYS, values))


def _validate(bundle):
    if (
        not isinstance(bundle, dict)
        or set(bundle) != set(DEMO_KEYS)
        or any(not isinstance(v, str) for v in bundle.values())
    ):
        raise SecretStoreError("Invalid demo credential bundle")
    return credential_bundle(
        bundle[DEMO_KEYS[0]],
        bundle[DEMO_KEYS[1]],
        bundle[DEMO_KEYS[2]] + bundle[DEMO_KEYS[3]],
    )


def _crypt(data: bytes, *, decrypt: bool):
    if os.name != "nt":
        raise SecretStoreError(
            "Secure setup requires Windows; use dedicated environment settings elsewhere"
        )

    class Blob(ctypes.Structure):
        _fields_ = [("size", wintypes.DWORD), ("data", ctypes.POINTER(ctypes.c_ubyte))]

    buffer = ctypes.create_string_buffer(data)
    source = Blob(len(data), ctypes.cast(buffer, ctypes.POINTER(ctypes.c_ubyte)))
    result = Blob()
    crypt = ctypes.WinDLL("crypt32", use_last_error=True)
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.LocalFree.argtypes = [ctypes.c_void_p]
    kernel.LocalFree.restype = ctypes.c_void_p
    function = crypt.CryptUnprotectData if decrypt else crypt.CryptProtectData
    function.argtypes = [
        ctypes.POINTER(Blob),
        ctypes.c_void_p,
        ctypes.POINTER(Blob),
        ctypes.c_void_p,
        ctypes.c_void_p,
        wintypes.DWORD,
        ctypes.POINTER(Blob),
    ]
    function.restype = wintypes.BOOL
    # CRYPTPROTECT_UI_FORBIDDEN, deliberately NOT CRYPTPROTECT_LOCAL_MACHINE.
    if not function(
        ctypes.byref(source), None, None, None, None, 1, ctypes.byref(result)
    ):
        raise SecretStoreError(
            "Windows could not protect or unlock demo settings for this user"
        )
    try:
        return ctypes.string_at(result.data, result.size)
    finally:
        kernel.LocalFree(ctypes.cast(result.data, ctypes.c_void_p))


def save_demo_settings(bundle, *, path: Path | None = None):
    clean = _validate(bundle)
    encrypted = _crypt(json.dumps(clean).encode("utf-8"), decrypt=False)
    destination = path or storage_path()
    destination.parent.mkdir(parents=True, exist_ok=True)
    temp = None
    try:
        with tempfile.NamedTemporaryFile(
            dir=destination.parent, prefix="kis-demo-", suffix=".tmp", delete=False
        ) as handle:
            temp = Path(handle.name)
            handle.write(encrypted)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, destination)
    except OSError:
        raise SecretStoreError("Could not save protected demo settings") from None
    finally:
        if temp and temp.exists():
            temp.unlink()


def load_demo_settings(*, path: Path | None = None):
    if path is None and (os.name != "nt" or not os.getenv("LOCALAPPDATA")):
        return {}
    source = path or storage_path()
    if not source.exists():
        return {}
    try:
        return _validate(json.loads(_crypt(source.read_bytes(), decrypt=True)))
    except (OSError, UnicodeError, ValueError):
        raise SecretStoreError(
            "Stored demo settings cannot be read; register them again"
        ) from None
