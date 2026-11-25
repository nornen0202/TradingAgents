from __future__ import annotations

import requests

from .api_keys import get_api_key
from .config import get_config
from .vendor_exceptions import VendorConfigurationError, VendorTransientError


_KRX_API_BASE = "https://data-dbg.krx.co.kr"


def call_krx_open_api(api_path: str, params: dict[str, str] | None = None, *, timeout: float | None = None) -> dict:
    api_key = get_api_key("KRX_API_KEY")
    if not api_key:
        raise VendorConfigurationError("KRX Open API key is not configured.")

    try:
        response = requests.get(
            f"{_KRX_API_BASE.rstrip('/')}/{api_path.lstrip('/')}",
            params=params or {},
            headers={"AUTH_KEY": api_key},
            timeout=timeout if timeout is not None else float(get_config().get("vendor_timeout", 15)),
            allow_redirects=False,
        )
        response.raise_for_status()
        if response.status_code != 200:
            raise VendorTransientError(f"KRX Open API returned HTTP {response.status_code}")
    except requests.RequestException as exc:
        raise VendorTransientError(f"KRX Open API request failed: {exc}") from exc

    return response.json()
