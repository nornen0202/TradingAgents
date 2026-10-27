from types import SimpleNamespace

import pytest

from tradingagents.scheduled import runner


@pytest.mark.parametrize("attempts,blocked", [(1, False), (2, False), (3, True), (4, True)])
def test_exhausted_codex_http_retries_use_existing_circuit_threshold(attempts, blocked):
    config = SimpleNamespace(run=SimpleNamespace(codex_circuit_breaker_enabled=True,
        fatal_error_patterns=(), max_consecutive_codex_failures=3))
    summary = {"status": "failed", "error": "exceeded retry limit, last status: 429 Too Many Requests",
               "failure_diagnostics": {"exception_class": "CodexAppServerError"}}
    assert runner._is_codex_failure_summary(summary)
    assert bool(runner._circuit_breaker_reason(config=config, summary=summary,
                consecutive_codex_failures=attempts)) is blocked


@pytest.mark.parametrize("exception", ["HTTPError", "DataVendorError", "", None])
def test_vendor_rate_limits_do_not_open_codex_circuit(exception):
    summary = {"error": "429 Too Many Requests", "failure_diagnostics": {"exception_class": exception}}
    assert not runner._is_codex_failure_summary(summary)
