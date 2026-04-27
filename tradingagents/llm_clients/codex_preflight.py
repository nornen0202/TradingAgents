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


@dataclass(slots=True)
class CodexPreflightResult:
    account: dict
    models: list[str]
    requested_model: str
    resolved_model: str
    fallback_used: bool = False


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
        resolved_model = _resolve_model(model, models=models, fallback_models=fallback_models)
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
