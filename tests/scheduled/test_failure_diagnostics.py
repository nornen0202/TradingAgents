import json
import subprocess

import pytest
from requests import exceptions as request_errors

from tradingagents.llm_clients.codex_app_server import (
    CodexAppServerAuthError,
    CodexAppServerBinaryError,
    CodexAppServerError,
    CodexAppServerTimeoutError,
    CodexModelUnavailableError,
    CodexStructuredOutputError,
)
from tradingagents.scheduled.failure_diagnostics import (
    failure_diagnostics,
    format_failure_diagnostics,
    sanitize_failure_diagnostics,
)


_SENSITIVE_SENTINEL = "synthetic-private-account-and-prompt-contents"
_UNKNOWN = {"failure_category": "UNKNOWN_ERROR", "exception_class": "OtherError", "retryability": "UNKNOWN"}


@pytest.mark.parametrize("exception,category,class_name,retryability", [
    (CodexAppServerAuthError(_SENSITIVE_SENTINEL), "AUTHENTICATION_ERROR", "CodexAppServerAuthError", "NON_RETRYABLE"),
    (CodexAppServerBinaryError(_SENSITIVE_SENTINEL), "RUNTIME_CONFIGURATION_ERROR", "CodexAppServerBinaryError", "NON_RETRYABLE"),
    (CodexModelUnavailableError(_SENSITIVE_SENTINEL), "MODEL_UNAVAILABLE", "CodexModelUnavailableError", "NON_RETRYABLE"),
    (CodexStructuredOutputError(_SENSITIVE_SENTINEL), "STRUCTURED_OUTPUT_ERROR", "CodexStructuredOutputError", "UNKNOWN"),
    (CodexAppServerTimeoutError(_SENSITIVE_SENTINEL), "PROVIDER_TIMEOUT", "CodexAppServerTimeoutError", "RETRYABLE"),
    (CodexAppServerError("Timed out waiting for turn " + _SENSITIVE_SENTINEL), "PROVIDER_ERROR", "CodexAppServerError", "UNKNOWN"),
    (request_errors.SSLError(_SENSITIVE_SENTINEL), "TLS_ERROR", "requests.SSLError", "NON_RETRYABLE"),
    (request_errors.InvalidURL(_SENSITIVE_SENTINEL), "REQUEST_CONFIGURATION_ERROR", "requests.InvalidURL", "NON_RETRYABLE"),
    (request_errors.ReadTimeout(_SENSITIVE_SENTINEL), "REQUEST_TIMEOUT", "requests.Timeout", "RETRYABLE"),
    (request_errors.ConnectTimeout(_SENSITIVE_SENTINEL), "REQUEST_TIMEOUT", "requests.Timeout", "RETRYABLE"),
    (request_errors.ConnectionError(_SENSITIVE_SENTINEL), "TRANSPORT_ERROR", "requests.ConnectionError", "RETRYABLE"),
    (request_errors.HTTPError(_SENSITIVE_SENTINEL), "HTTP_ERROR", "requests.HTTPError", "UNKNOWN"),
    (request_errors.RequestException(_SENSITIVE_SENTINEL), "REQUEST_ERROR", "requests.RequestException", "UNKNOWN"),
    (subprocess.TimeoutExpired(_SENSITIVE_SENTINEL, 1, output=_SENSITIVE_SENTINEL, stderr=_SENSITIVE_SENTINEL), "PROCESS_TIMEOUT", "TimeoutExpired", "RETRYABLE"),
    (subprocess.CalledProcessError(1, _SENSITIVE_SENTINEL, stderr=_SENSITIVE_SENTINEL), "PROCESS_ERROR", "CalledProcessError", "UNKNOWN"),
    (PermissionError(_SENSITIVE_SENTINEL), "PERMISSION_ERROR", "PermissionError", "NON_RETRYABLE"),
    (FileNotFoundError(_SENSITIVE_SENTINEL), "MISSING_RESOURCE", "FileNotFoundError", "NON_RETRYABLE"),
    (TimeoutError(_SENSITIVE_SENTINEL), "TIMEOUT", "TimeoutError", "RETRYABLE"),
    (ConnectionRefusedError(_SENSITIVE_SENTINEL), "TRANSPORT_ERROR", "ConnectionError", "RETRYABLE"),
    (TypeError(_SENSITIVE_SENTINEL), "TYPE_ERROR", "TypeError", "NON_RETRYABLE"),
    (KeyError(_SENSITIVE_SENTINEL), "MISSING_FIELD", "KeyError", "UNKNOWN"),
    (ValueError(_SENSITIVE_SENTINEL), "VALUE_ERROR", "ValueError", "UNKNOWN"),
    (json.JSONDecodeError(_SENSITIVE_SENTINEL, _SENSITIVE_SENTINEL, 0), "JSON_FORMAT_ERROR", "JSONDecodeError", "UNKNOWN"),
])
def test_typed_diagnostics_are_allowlisted_and_do_not_publish_message(exception, category, class_name, retryability):
    result = failure_diagnostics(exception)
    assert result == {"failure_category": category, "exception_class": class_name, "retryability": retryability}
    assert sanitize_failure_diagnostics(result) == result
    rendered = format_failure_diagnostics(result)
    assert _SENSITIVE_SENTINEL not in rendered
    assert "\n" not in rendered


def test_unknown_type_name_and_timeout_looking_message_are_not_inferred():
    private_named_type = type(_SENSITIVE_SENTINEL, (RuntimeError,), {})
    assert failure_diagnostics(private_named_type("Timed out; token=" + _SENSITIVE_SENTINEL)) == _UNKNOWN


def test_classifier_does_not_read_any_exception_attribute_or_string():
    class UnreadableError(RuntimeError):
        def __getattribute__(self, _name):
            raise AssertionError("No exception attributes may be read")

        def __str__(self):
            raise AssertionError("Exception string must not be read")

        def __repr__(self):
            raise AssertionError("Exception repr must not be read")

    assert failure_diagnostics(UnreadableError()) == _UNKNOWN


def test_known_subclass_is_classified_without_reading_response_or_args():
    class UnreadableHttpError(request_errors.HTTPError):
        def __getattribute__(self, _name):
            raise AssertionError("No exception attributes may be read")

        def __str__(self):
            raise AssertionError("Exception string must not be read")

    # RequestException.__init__ accesses response; construct before enabling the
    # adversarial subclass so this test concerns the diagnostic function alone.
    exception = request_errors.HTTPError(_SENSITIVE_SENTINEL)
    exception.__class__ = UnreadableHttpError
    assert failure_diagnostics(exception) == {
        "failure_category": "HTTP_ERROR", "exception_class": "requests.HTTPError", "retryability": "UNKNOWN",
    }


@pytest.mark.parametrize("payload", [
    None,
    "error=" + _SENSITIVE_SENTINEL,
    {"error": "TimeoutError: " + _SENSITIVE_SENTINEL},
    {"failure_category": "TIMEOUT\n" + _SENSITIVE_SENTINEL, "exception_class": "TimeoutError", "retryability": "RETRYABLE"},
    {"failure_category": "AUTHENTICATION_ERROR", "exception_class": "TimeoutError", "retryability": "RETRYABLE"},
    {"failure_category": "TIMEOUT", "exception_class": _SENSITIVE_SENTINEL, "retryability": "RETRYABLE"},
    {"failure_category": "TIMEOUT", "exception_class": "TimeoutError", "retryability": ["RETRYABLE"]},
])
def test_untrusted_or_legacy_worker_summaries_fail_closed(payload):
    assert sanitize_failure_diagnostics(payload) == _UNKNOWN
    assert _SENSITIVE_SENTINEL not in format_failure_diagnostics(payload)


def test_projection_ignores_extra_private_fields_and_rejects_mapping_subclasses():
    payload = {**failure_diagnostics(TimeoutError()), "error": _SENSITIVE_SENTINEL, "response": _SENSITIVE_SENTINEL}
    assert set(sanitize_failure_diagnostics(payload)) == {"failure_category", "exception_class", "retryability"}
    assert _SENSITIVE_SENTINEL not in format_failure_diagnostics(payload)

    class UnreadableDict(dict):
        def get(self, *_args):
            raise AssertionError("Do not inspect non-JSON mappings")

    assert sanitize_failure_diagnostics(UnreadableDict(payload)) == _UNKNOWN
