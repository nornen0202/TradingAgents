import os
from pathlib import Path

import pytest

from tradingagents.execution.demo_secrets import (
    SecretStoreError,
    credential_bundle,
    load_demo_settings,
    save_demo_settings,
)
from tradingagents.execution.kis_demo import DemoCredentials
from tools.setup_kis_demo import save_and_check


def test_complete_account_is_split_without_guessing_product():
    bundle = credential_bundle("demo-key", "demo-secret", "12345678-01")
    assert bundle["KIS_DEMO_ACCOUNT_NO"] == "12345678"
    assert bundle["KIS_DEMO_PRODUCT_CODE"] == "01"
    for number in ("12345678", "bad12345678-01", "12345678-1"):
        with pytest.raises(SecretStoreError):
            credential_bundle("demo-key", "demo-secret", number)


@pytest.mark.skipif(os.name != "nt", reason="Windows user-scoped DPAPI")
def test_dpapi_roundtrip_tamper_and_loader_precedence(monkeypatch, tmp_path):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    bundle = credential_bundle("demo-key-test", "demo-secret-test", "12345678-01")
    save_demo_settings(bundle)
    path = tmp_path / "TradingAgents" / "kis-demo.dpapi"
    assert b"demo-secret-test" not in path.read_bytes()
    assert b"12345678" not in path.read_bytes()
    assert load_demo_settings() == bundle
    monkeypatch.setenv("KIS_DEMO_ACCOUNT_NO", "87654321")
    assert DemoCredentials.from_local_settings().account_no == "12345678"
    path.write_bytes(b"broken encrypted file")
    with pytest.raises(SecretStoreError):
        DemoCredentials.from_local_settings()


@pytest.mark.skipif(os.name != "nt", reason="Windows user-scoped DPAPI")
def test_registration_saves_and_runs_readonly_probe(monkeypatch, tmp_path):
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    import tools.setup_kis_demo as setup

    calls = []

    def read_only(**kwargs):
        calls.append(kwargs)
        return {"status": "READ_CONNECTION_VERIFIED", "orders_submitted": 0}

    monkeypatch.setattr(setup, "check", read_only)
    assert (
        save_and_check("demo-key", "demo-secret", "12345678-01")["orders_submitted"]
        == 0
    )
    assert calls == [{"connect": True}]
    report = Path(tmp_path, "TradingAgents", "kis-demo-readiness.json").read_text()
    assert "demo-secret" not in report and "12345678" not in report
