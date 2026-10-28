# Dependency security recovery — 2026-10-28

The repository audit found eight open dependency advisories: three for pypdf,
three for filelock, one for the SQLite checkpoint store and one for setuptools.
The recovery updates the lock and installation floors rather than dismissing
alerts or relying on a workstation's currently installed packages.

| Dependency | Recovery version | Relevant fix |
| --- | --- | --- |
| pypdf | 6.21.2 or later | Bound malformed cross-reference work and repeated missing-object lookups |
| langgraph-checkpoint-sqlite | 3.1.2 or later | Validate namespace labels before store dispatch |
| setuptools | 84.1.0 or later | Prevent Windows namespace-package path escape; apply to build and runtime requirements |
| filelock, Python 3.11+ | 4.2.4 in the lock, floor 4.2.1 | Fix Windows lock-file/SQLite side-file handling and soft-lock timeout behavior |
| filelock, Python 3.10 | 3.20.3 | Retain the last pre-affected version compatible with the legacy interpreter |

filelock 4.2.1 requires Python 3.11+. The three reported affected ranges start at
3.20.4 or 3.22.0 and end at 4.2.0. A version-qualified GitHub advisory lookup
returned those three advisories for the old locked 3.31.0, and none for 3.20.3 or
4.2.4. This is a check of published advisories at the audit time, not a guarantee
against undisclosed vulnerabilities. Keep the Python-version markers when
refreshing the lock; do not select an affected 3.x release for Python 3.10.

The lock is generated/exported with the repository's pinned uv 0.11.28 and all
extras. Export validation, `pip check`, PDF round-trip, exclusive file-lock and
SQLite checkpoint round-trip checks pass with the updated packages. The full
application suite and CI remain the merge gate. Dependency testing uses an
isolated target before updating the operational environment.

Sources: [filelock metadata](https://pypi.org/project/filelock/4.2.1/),
[setuptools metadata](https://pypi.org/project/setuptools/84.1.0/),
[filelock SQLite advisory](https://github.com/advisories/GHSA-v4x8-3wr5-3wq8),
[filelock timeout advisory](https://github.com/advisories/GHSA-567q-5qvw-pf92),
[filelock side-file advisory](https://github.com/advisories/GHSA-9vhv-jxww-xfm5),
[checkpoint advisory](https://github.com/advisories/GHSA-6hmw-9432-67qq),
[setuptools advisory](https://github.com/advisories/GHSA-xmj3-9gf7-h52w),
[pypdf release](https://github.com/py-pdf/pypdf/releases/tag/6.21.2).
