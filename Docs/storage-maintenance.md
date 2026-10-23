# Local storage maintenance

The existing `StorageMaintenance` Windows task can also offload closed Codex
documents, archive completed TradingAgents worker homes, retain crash diagnostics,
and prune the uv cache. These behaviors are opt-in through a local
`storage-policy.json` beside the installed scripts. The installer preserves that
machine-specific file and installs both Python helpers.

Start from `tools/storage-policy.example.json`, fill in local paths and the volume
serials reported by `Win32_LogicalDisk`, and enable it only after a dry run. Point
`python_executable` at a stable Python 3.10+ installation. Protect backup and
destination directories so that only the operating user and SYSTEM can access
worker homes, which may contain credentials. The optional `private_sid` field
applies that ACL to newly created destinations on Windows.

Run the existing maintenance script without `-Apply` to preview all policies.
The configured external volumes must match before the extended policy runs;
missing drives fail closed instead of creating replacement storage on C:.

Documents older than seven days are candidates only after 48 hours without file
writes. Running processes are checked by command line, executable path, and
accessible Windows current directory. Existing junctions are not traversed.
Partially offloaded date folders retain their existing links and consider only
remaining ordinary chat folders. Closed date folders are copied to the configured
destination, independently archived, and verified with SHA-256 before the old path
becomes a junction. The staged C: original is removed only after the destination,
backup, and original are all verified. Interrupted prepared transactions are
resumed from their journal.

Worker cleanup requires a matching canonical `run.json` with `status=success`
and a finish timestamp. It retains the latest two successful runs and all runs
younger than seven days; recent writes and active processes prevent cleanup.
Unknown, failed, or running workers are retained. A verified backup is kept before
an eligible completed worker is removed. No automatic backup expiration is used.

Crash dumps retain the latest two and anything younger than seven days. Older
dumps are hash-verified in backup storage before removal. uv pruning uses uv's own
locking with a short lock timeout, never a forced directory deletion. Existing
archive and self-hosted runner retention remains in place. A low C: free-space
warning is written to task output below the configured threshold.

Set `preserve_canonical_archive=true` when canonical research history is still
referenced by provenance, approvals, or ledgers. The PowerShell task then retains
`archive/runs`, `archive/youtube-archive/runs`, and `prism-telegram-archive/runs`
regardless of age. This preservation flag is independent of the Python helper's
`enabled` switch. It does not
move those directories or weaken any application path boundary. Other retention
categories keep their existing rules. Configure this guard before a maintenance
run; malformed local policy JSON fails before cleanup begins.

The optional `relocations` list registers `{id, source, destination}` directory
aliases created by a verified migration. Each source must remain a junction to
the exact destination. A mismatch is reported without repairing or deleting
either path, and the helper returns exit code 2 before any retention starts.
The wrapper runs mount and alias preflight before its own cleanup as well.
`critical_free_bytes` also
returns code 2 below its threshold; `warning_free_bytes` remains informational.
The wrapper propagates a failure so existing scheduled-task monitoring can see
the condition. Omit `critical_free_bytes` to retain warning-only behavior.
The example uses 12GiB critical and 30GiB warning; these maintenance alerts do not
change trading, order, research, or retry limits.

For an initial migration, `maintain_codex_storage.py --config ... --apply` leaves
the staged originals intact. Run Codex and local automation checks, write a JSON
receipt containing `codex_ok`, `tradingagents_ok`, and a numeric `verified_at`
timestamp newer than the prepared transactions, then rerun with
`--apply --finalize-receipt ...`. Preserve the receipt, operation journals,
manifests, and backups for recovery. This workflow never moves the main Codex
authentication, configuration, session database, or active TradingAgents source
checkout.
