"""Allowlisted, message-free worker failure diagnostics for public logs.

Never serialize an exception or inspect its message, args, response, traceback,
stderr, cause, or credential-bearing attributes. A retry classification is only
an operational hint for existing bounded/read-only retry policy, not permission
to retry, change authentication/model settings, or skip data-quality gates.
"""

from __future__ import annotations

import json
import subprocess
from typing import Any

from requests import exceptions as request_errors

from tradingagents.llm_clients.codex_app_server import (
    CodexAppServerAuthError,
    CodexAppServerBinaryError,
    CodexAppServerError,
    CodexModelUnavailableError,
    CodexStructuredOutputError,
)


_FIELDS = ("failure_category", "exception_class", "retryability")
_UNKNOWN = ("UNKNOWN_ERROR", "OtherError", "UNKNOWN")

# The emitted class name is a constant, never type(exc).__name__. More specific
# classes must precede their parents. Unknown provider errors stay unknown rather
# than being guessed from free-form messages (including timeout-looking text).
_RULES: tuple[tuple[type[BaseException], tuple[str, str, str]], ...] = (
    (CodexAppServerAuthError, ("AUTHENTICATION_ERROR", "CodexAppServerAuthError", "NON_RETRYABLE")),
    (CodexAppServerBinaryError, ("RUNTIME_CONFIGURATION_ERROR", "CodexAppServerBinaryError", "NON_RETRYABLE")),
    (CodexModelUnavailableError, ("MODEL_UNAVAILABLE", "CodexModelUnavailableError", "NON_RETRYABLE")),
    (CodexStructuredOutputError, ("STRUCTURED_OUTPUT_ERROR", "CodexStructuredOutputError", "UNKNOWN")),
    (CodexAppServerError, ("PROVIDER_ERROR", "CodexAppServerError", "UNKNOWN")),
    (request_errors.SSLError, ("TLS_ERROR", "requests.SSLError", "NON_RETRYABLE")),
    (request_errors.InvalidURL, ("REQUEST_CONFIGURATION_ERROR", "requests.InvalidURL", "NON_RETRYABLE")),
    (request_errors.InvalidSchema, ("REQUEST_CONFIGURATION_ERROR", "requests.InvalidSchema", "NON_RETRYABLE")),
    (request_errors.MissingSchema, ("REQUEST_CONFIGURATION_ERROR", "requests.MissingSchema", "NON_RETRYABLE")),
    (request_errors.Timeout, ("REQUEST_TIMEOUT", "requests.Timeout", "RETRYABLE")),
    (request_errors.ConnectionError, ("TRANSPORT_ERROR", "requests.ConnectionError", "RETRYABLE")),
    (request_errors.HTTPError, ("HTTP_ERROR", "requests.HTTPError", "UNKNOWN")),
    (json.JSONDecodeError, ("JSON_FORMAT_ERROR", "JSONDecodeError", "UNKNOWN")),
    (request_errors.RequestException, ("REQUEST_ERROR", "requests.RequestException", "UNKNOWN")),
    (subprocess.TimeoutExpired, ("PROCESS_TIMEOUT", "TimeoutExpired", "RETRYABLE")),
    (subprocess.CalledProcessError, ("PROCESS_ERROR", "CalledProcessError", "UNKNOWN")),
    (PermissionError, ("PERMISSION_ERROR", "PermissionError", "NON_RETRYABLE")),
    (FileNotFoundError, ("MISSING_RESOURCE", "FileNotFoundError", "NON_RETRYABLE")),
    (TimeoutError, ("TIMEOUT", "TimeoutError", "RETRYABLE")),
    (ConnectionError, ("TRANSPORT_ERROR", "ConnectionError", "RETRYABLE")),
    (TypeError, ("TYPE_ERROR", "TypeError", "NON_RETRYABLE")),
    (KeyError, ("MISSING_FIELD", "KeyError", "UNKNOWN")),
    (ValueError, ("VALUE_ERROR", "ValueError", "UNKNOWN")),
)
_ALLOWED = frozenset([_UNKNOWN, *(diagnostic for _, diagnostic in _RULES)])


def failure_diagnostics(exc: BaseException) -> dict[str, str]:
    """Classify only by inheritance; do not read attributes from ``exc``."""
    exception_type = type(exc)
    for expected_type, diagnostic in _RULES:
        if issubclass(exception_type, expected_type):
            return dict(zip(_FIELDS, diagnostic))
    return dict(zip(_FIELDS, _UNKNOWN))


def sanitize_failure_diagnostics(payload: Any) -> dict[str, str]:
    """Project a decoded worker summary onto a known, consistent field triple.

    Unknown/legacy summaries are intentionally not classified from their ``error``
    text. Reject newlines, arbitrary class names and mismatched enum combinations.
    """
    if type(payload) is not dict:
        return dict(zip(_FIELDS, _UNKNOWN))
    values = tuple(payload.get(field) for field in _FIELDS)
    if all(type(value) is str for value in values) and values in _ALLOWED:
        return dict(zip(_FIELDS, values))
    return dict(zip(_FIELDS, _UNKNOWN))


def format_failure_diagnostics(payload: Any) -> str:
    """Return only allowlisted fields suitable for a single public log line."""
    diagnostic = sanitize_failure_diagnostics(payload)
    return " ".join(f"{field}={diagnostic[field]}" for field in _FIELDS)
