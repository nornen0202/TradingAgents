import importlib.util
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location("runtime_constraints", Path(__file__).resolve().parents[1] / "tools/check_runtime_constraints.py")
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


def test_platform_markers_and_unused_extras_do_not_create_false_drift():
    result = audit.audit_constraints("""
    # Exported by uv
    numpy==2.4.6 ; python_full_version < '3.12'
    numpy==2.5.1 ; python_full_version >= '3.12'
    optional-translator==9.0
    typing_extensions==4.15.0
    """, installed={"numpy": "2.5.1", "typing-extensions": "4.15.0", "pytest": "9.0"},
       environment={"python_full_version": "3.14.3"})
    assert result["status"] == "ALIGNED" and result["matched_count"] == 2
    assert result["uninstalled_constraints"] == ["optional-translator"]
    assert result["dependency_completeness_verified"] is False


def test_actual_two_package_drift_is_reported_without_modifying_environment():
    installed = {"cryptography": "49.0.0", "soupsieve": "2.8.4"}
    result = audit.audit_constraints("cryptography==50.0.0\nsoupsieve==2.9", installed=installed)
    assert result["status"] == "DRIFT" and result["matched_count"] == 0
    assert result["mismatches"] == [
        {"package": "cryptography", "installed": "49.0.0", "locked": "50.0.0"},
        {"package": "soupsieve", "installed": "2.8.4", "locked": "2.9"},
    ]
    assert installed == {"cryptography": "49.0.0", "soupsieve": "2.8.4"}


def test_an_unrelated_or_empty_interpreter_cannot_report_alignment():
    result = audit.audit_constraints("cryptography==50.0.0", installed={"pytest": "9.0"})
    assert result["status"] == "UNVERIFIED" and result["matched_count"] == 0
    assert result["mismatches"] == []


@pytest.mark.parametrize("text", ["", "# empty", "x>=1", "x==1.*", "x @ https://example.invalid/x.whl",
                                  "x[extra]==1", "x==1\nx==2", "--index-url https://example.invalid"])
def test_non_frozen_or_ambiguous_inputs_are_rejected(text):
    with pytest.raises(ValueError):
        audit.audit_constraints(text, installed={})
