"""Read-only installed-version audit against an explicit frozen uv export.

This does not install packages, prove imports work, or require unused extras.
Run pip check as a separate dependency-completeness check before adoption.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from importlib import metadata
import hashlib
import json
from pathlib import Path
import platform

from packaging.requirements import Requirement
from packaging.utils import canonicalize_name


def audit_constraints(text, *, installed, environment=None):
    observed = {canonicalize_name(name): version for name, version in installed.items()}
    expected = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        requirement = Requirement(line)
        pins = list(requirement.specifier)
        if (requirement.url or requirement.extras or len(pins) != 1
                or pins[0].operator != "==" or "*" in pins[0].version):
            raise ValueError("Only exact frozen package constraints are supported")
        if requirement.marker and not requirement.marker.evaluate(environment):
            continue
        name, version = canonicalize_name(requirement.name), pins[0].version
        if name in expected and expected[name] != version:
            raise ValueError("Conflicting applicable frozen package versions")
        expected[name] = version
    if not expected:
        raise ValueError("No applicable frozen package constraints")
    mismatches = [{"package": name, "installed": observed[name], "locked": version}
                  for name, version in sorted(expected.items())
                  if name in observed and observed[name] != version]
    matched = sorted(name for name, version in expected.items() if observed.get(name) == version)
    uninstalled = sorted(expected.keys() - observed.keys())
    status = "DRIFT" if mismatches else "ALIGNED" if matched else "UNVERIFIED"
    return {"status": status, "scope": "INSTALLED_PACKAGES_IN_FROZEN_EXPORT",
            "matched_count": len(matched), "mismatches": mismatches,
            "uninstalled_constraints": uninstalled, "dependency_completeness_verified": False}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--constraints", type=Path, required=True)
    args = parser.parse_args(argv)
    installed = {distribution.metadata["Name"]: distribution.version
                 for distribution in metadata.distributions() if distribution.metadata["Name"]}
    raw = args.constraints.read_bytes()
    result = audit_constraints(raw.decode("utf-8-sig"), installed=installed)
    result["observed_at"] = datetime.now(timezone.utc).isoformat()
    result["constraints_sha256"] = hashlib.sha256(raw).hexdigest()
    result["python_version"] = platform.python_version()
    result["application_version"] = metadata.version("tradingagents")
    print(json.dumps(result, sort_keys=True))
    return 0 if result["status"] == "ALIGNED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
