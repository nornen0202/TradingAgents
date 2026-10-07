from __future__ import annotations

from collections.abc import Mapping
from typing import Any


def get_setting(settings: Any, name: str, default: Any = None) -> Any:
    if isinstance(settings, Mapping):
        return settings.get(name, default)
    return getattr(settings, name, default)


def tier_provider(settings: Any, role: str) -> str:
    """Resolve a tier's provider while preserving the legacy shared setting."""
    return str(
        get_setting(settings, f"{role}_think_provider")
        or get_setting(settings, "llm_provider", "codex")
    ).strip().lower()


def tier_backend_url(settings: Any, role: str) -> str | None:
    """A custom endpoint belongs only to the provider it was configured for."""
    specific = get_setting(settings, f"{role}_think_backend_url")
    if specific:
        return specific
    shared_provider = str(get_setting(settings, "llm_provider", "codex")).strip().lower()
    if tier_provider(settings, role) == shared_provider:
        return get_setting(settings, "backend_url")
    return None


def codex_reasoning_effort(settings: Any, role: str) -> str:
    specific = get_setting(settings, f"codex_{role}_reasoning_effort")
    legacy = get_setting(settings, "codex_reasoning_effort", "medium")
    return str(specific or legacy or "medium").strip() or "medium"


def codex_client_kwargs(settings: Any, *, role: str) -> dict[str, Any]:
    return {
        "codex_binary": get_setting(settings, "codex_binary"),
        "codex_reasoning_effort": codex_reasoning_effort(settings, role),
        "codex_summary": get_setting(settings, "codex_summary", "none"),
        "codex_personality": get_setting(settings, "codex_personality", "none"),
        "codex_workspace_dir": get_setting(settings, "codex_workspace_dir"),
        "codex_request_timeout": get_setting(settings, "codex_request_timeout", 120.0),
        "codex_max_retries": get_setting(settings, "codex_max_retries", 2),
        "codex_cleanup_threads": get_setting(settings, "codex_cleanup_threads", True),
        "codex_preflight_mode": get_setting(
            settings, "codex_preflight_mode", "per_client"
        ),
        "codex_fallback_on_app_server_error": get_setting(
            settings, "codex_fallback_on_app_server_error", False
        ),
        "model_role": role,
    }
