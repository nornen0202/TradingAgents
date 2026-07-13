from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .codex_app_server import (
    CodexAppServerAuthError,
    CodexAppServerBinaryError,
    CodexAppServerSession,
    CodexModelUnavailableError,
)
from .codex_binary import codex_binary_error_message, resolve_codex_binary


QUALITY_FALLBACK_MODELS = (
    "gpt-5.5",
    "gpt-5.4",
    "gpt-5.3-codex",
    "gpt-5.3-codex-spark",
    "gpt-5.2-codex",
    "gpt-5.2",
    "gpt-5.4-mini",
)

EFFICIENCY_FALLBACK_MODELS = (
    "gpt-5.4-mini",
    "gpt-5.4",
    "gpt-5.5",
)

_QUALITY_ROLES = {"deep", "judge", "youtube_verify"}
_FALSE_VALUES = {"0", "false", "no", "off"}


@dataclass(slots=True)
class CodexPreflightResult:
    account: dict
    models: list[str]
    requested_model: str
    resolved_model: str
    fallback_used: bool = False


def codex_preflight_fallback_models(
    role: str,
    *,
    allow_fallback: str | bool | None = None,
) -> tuple[str, ...]:
    """Return deployment-time fallbacks independently from runtime fail-fast policy.

    ``TRADINGAGENTS_CODEX_ALLOW_MODEL_FALLBACK`` controls per-client runtime
    behavior after a workflow has selected an exact model. Workflow preflight
    must not reuse that flag, otherwise a newly preferred model can prevent the
    workflow from selecting an already-supported compatibility model.
    """

    if allow_fallback is None:
        import os

        allow_fallback = os.getenv(
            "TRADINGAGENTS_CODEX_PREFLIGHT_ALLOW_MODEL_FALLBACK",
            "1",
        )
    if isinstance(allow_fallback, str):
        enabled = allow_fallback.strip().lower() not in _FALSE_VALUES
    else:
        enabled = bool(allow_fallback)
    if not enabled:
        return ()
    normalized_role = str(role or "").strip().lower()
    if normalized_role in _QUALITY_ROLES:
        return QUALITY_FALLBACK_MODELS
    return EFFICIENCY_FALLBACK_MODELS


def run_codex_preflight(
    *,
    codex_binary: str | None,
    model: str,
    request_timeout: float,
    workspace_dir: str,
    cleanup_threads: bool,
    fallback_models: list[str] | tuple[str, ...] | None = None,
    session_factory: Callable[..., CodexAppServerSession] = CodexAppServerSession,
) -> CodexPreflightResult:
    binary = resolve_codex_binary(codex_binary)
    if not binary and codex_binary and session_factory is not CodexAppServerSession:
        binary = codex_binary
    if not binary:
        raise CodexAppServerBinaryError(codex_binary_error_message(codex_binary))

    session = session_factory(
        codex_binary=binary,
        request_timeout=request_timeout,
        workspace_dir=workspace_dir,
        cleanup_threads=cleanup_threads,
    )

    try:
        session.start()
        account_payload = session.account_read()
        account = account_payload.get("account")
        if not account:
            raise CodexAppServerAuthError(
                "Codex authentication is not available for TradingAgents. "
                "Run `codex login` or `codex login --device-auth`, then retry."
            )

        models_payload = session.model_list(include_hidden=True)
        models = _collect_model_names(models_payload)
        resolved_model = _resolve_model(
            model, models=models, fallback_models=fallback_models
        )
        if not resolved_model:
            preview = ", ".join(models[:8]) if models else "no models reported"
            fallback_text = ""
            if fallback_models:
                fallback_text = f" Fallback candidates were: {', '.join(str(item) for item in fallback_models)}."
            raise CodexModelUnavailableError(
                f"Codex model '{model}' is not available from `model/list`. Available models: {preview}.{fallback_text}"
            )

        return CodexPreflightResult(
            account=account,
            models=models,
            requested_model=model,
            resolved_model=resolved_model,
            fallback_used=resolved_model != model,
        )
    finally:
        session.close()


def _collect_model_names(payload: dict) -> list[str]:
    names: list[str] = []
    for entry in payload.get("data", []) or []:
        if not isinstance(entry, dict):
            continue
        for key in ("model", "id"):
            value = entry.get(key)
            if isinstance(value, str) and value not in names:
                names.append(value)
    return names


def _resolve_model(
    model: str,
    *,
    models: list[str],
    fallback_models: list[str] | tuple[str, ...] | None,
) -> str | None:
    requested = str(model or "").strip()
    if requested in models:
        return requested

    for candidate in fallback_models or ():
        normalized = str(candidate or "").strip()
        if normalized and normalized in models:
            return normalized
    return None
