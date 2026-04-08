from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path


_DOC_ENV_MAP = {
    "ALPHA_VANTAGE_API_KEY": "Alpha Vantage",
    "NAVER_CLIENT_ID": "Naver.Client ID",
    "NAVER_CLIENT_SECRET": "Naver.Client Secret",
    "OPENDART_API_KEY": "OpenDart",
}

_ENV_ALIASES = {
    "ALPHA_VANTAGE_API_KEY": ("ALPHA_VANTAGE_API_KEY", "ALPHA_VANTAGE_KEY"),
    "NAVER_CLIENT_ID": ("NAVER_CLIENT_ID", "NAVER_API_CLIENT_ID"),
    "NAVER_CLIENT_SECRET": ("NAVER_CLIENT_SECRET", "NAVER_API_CLIENT_SECRET"),
    "OPENDART_API_KEY": ("OPENDART_API_KEY", "OPEN_DART_API_KEY", "OPENDART_KEY"),
}


def _get_api_keys_doc_path() -> Path:
    return Path(__file__).resolve().parents[2] / "Docs" / "list_api_keys.md"


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
    return normalized or None


@lru_cache(maxsize=1)
def _load_documented_keys() -> dict[str, str]:
    path = _get_api_keys_doc_path()
    if not path.exists():
        return {}

    content = path.read_text(encoding="utf-8")
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


def get_api_key(env_name: str) -> str | None:
    for candidate in _ENV_ALIASES.get(env_name, (env_name,)):
        normalized = _normalize_key_value(os.getenv(candidate))
        if normalized:
            return normalized

    documented = _normalize_key_value(_load_documented_keys().get(env_name))
    if documented:
        return documented

    return None
