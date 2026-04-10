from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path


_DOC_ENV_MAP = {
    "ALPHA_VANTAGE_API_KEY": "Alpha Vantage",
    "KIS_APP_KEY": "KIS Developers App Key",
    "KIS_APP_SECRET": "KIS Developers App Secret",
    "KIS_ACCOUNT_NO": "KIS Account Number",
    "KIS_PRODUCT_CODE": "KIS Product Code",
    "NAVER_CLIENT_ID": "Naver.Client ID",
    "NAVER_CLIENT_SECRET": "Naver.Client Secret",
    "OPENDART_API_KEY": "OpenDart",
}

_ENV_ALIASES = {
    "ALPHA_VANTAGE_API_KEY": ("ALPHA_VANTAGE_API_KEY", "ALPHA_VANTAGE_KEY"),
    "KIS_APP_KEY": ("KIS_APP_KEY", "KIS_Developers_APP_KEY"),
    "KIS_APP_SECRET": ("KIS_APP_SECRET", "KIS_Developers_APP_SECRET"),
    "KIS_ACCOUNT_NO": ("KIS_ACCOUNT_NO", "KIS_Developers_ACCOUNT_NO"),
    "KIS_PRODUCT_CODE": ("KIS_PRODUCT_CODE", "KIS_Developers_PRODUCT_CODE"),
    "NAVER_CLIENT_ID": ("NAVER_CLIENT_ID", "NAVER_API_CLIENT_ID"),
    "NAVER_CLIENT_SECRET": ("NAVER_CLIENT_SECRET", "NAVER_API_CLIENT_SECRET"),
    "OPENDART_API_KEY": ("OPENDART_API_KEY", "OPEN_DART_API_KEY", "OPENDART_KEY"),
}

_PLACEHOLDER_VALUES = {
    "[REDACTED]",
    "<REDACTED>",
    "REDACTED",
    "[YOUR_KEY]",
    "<YOUR_KEY>",
    "YOUR_KEY",
    "CHANGEME",
    "CHANGE_ME",
    "TODO",
    "TBD",
}


def _get_api_keys_doc_path() -> Path:
    return Path(__file__).resolve().parents[2] / "Docs" / "list_api_keys.md"


def _get_api_keys_json_path() -> Path:
    configured = _normalize_key_value(os.getenv("TRADINGAGENTS_API_KEYS_PATH"))
    if configured:
        return Path(configured).expanduser()
    return Path(__file__).resolve().parents[2] / "config" / "api_keys.json"


def _normalize_key_value(value: str | None) -> str | None:
    if value is None:
        return None

    normalized = value.strip()
    if not normalized:
        return None

    if (
        len(normalized) >= 2
        and normalized[0] == normalized[-1]
        and normalized[0] in {'"', "'"}
    ):
        normalized = normalized[1:-1].strip()

    if "\\n" in normalized and "\n" not in normalized:
        normalized = normalized.replace("\\n", "")

    normalized = normalized.strip()
    if normalized.upper() in _PLACEHOLDER_VALUES:
        return None
    return normalized or None


def _normalize_file_value(value: object) -> str | None:
    if value is None or isinstance(value, (dict, list)):
        return None
    return _normalize_key_value(str(value))


def _load_json_keys(path: Path) -> dict[str, str]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return {}

    if not isinstance(payload, dict):
        return {}

    parsed: dict[str, str] = {}
    for env_name, aliases in _ENV_ALIASES.items():
        candidates = (env_name, *aliases, env_name.lower(), *(alias.lower() for alias in aliases))
        for candidate in candidates:
            if candidate not in payload:
                continue
            normalized = _normalize_file_value(payload.get(candidate))
            if normalized:
                parsed[env_name] = normalized
                break
    return parsed


def _load_legacy_markdown_keys(path: Path) -> dict[str, str]:
    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return {}

    parsed: dict[str, str] = {}
    current_section = None

    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        if line.startswith("Alpha Vantage:"):
            _, value = line.split(":", 1)
            normalized = _normalize_key_value(value)
            if normalized:
                parsed["ALPHA_VANTAGE_API_KEY"] = normalized
            current_section = None
            continue

        if line.startswith("OpenDart:"):
            _, value = line.split(":", 1)
            normalized = _normalize_key_value(value)
            if normalized:
                parsed["OPENDART_API_KEY"] = normalized
            current_section = None
            continue

        if line.endswith(":") and not line.startswith("-"):
            current_section = line[:-1].strip()
            continue

        if line.startswith("-") and ":" in line and current_section == "Naver":
            key, value = line[1:].split(":", 1)
            normalized_key = key.strip().lower()
            normalized_value = _normalize_key_value(value)
            if not normalized_value:
                continue
            if normalized_key == "client id":
                parsed["NAVER_CLIENT_ID"] = normalized_value
            elif normalized_key == "client secret":
                parsed["NAVER_CLIENT_SECRET"] = normalized_value
            continue

    return parsed


def _load_key_file(path: Path) -> dict[str, str]:
    if path.suffix.lower() == ".json":
        return _load_json_keys(path)
    return _load_legacy_markdown_keys(path)


@lru_cache(maxsize=1)
def _load_documented_keys() -> dict[str, str]:
    json_path = _get_api_keys_json_path()
    if json_path.exists():
        parsed = _load_key_file(json_path)
        if parsed:
            return parsed

    legacy_path = _get_api_keys_doc_path()
    if legacy_path.exists():
        return _load_legacy_markdown_keys(legacy_path)

    return {}


def get_api_key(env_name: str) -> str | None:
    for candidate in _ENV_ALIASES.get(env_name, (env_name,)):
        normalized = _normalize_key_value(os.getenv(candidate))
        if normalized:
            return normalized

    documented = _normalize_key_value(_load_documented_keys().get(env_name))
    if documented:
        return documented

    return None
