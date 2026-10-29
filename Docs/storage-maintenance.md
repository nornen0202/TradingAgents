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


## Isolated policy domains and current completion reuse (2026-10-29)

A policy may contain `domains`. Each domain retains the existing volume/alias,
quiet-period, process, backup and verification checks. Mutation roots must not
be duplicated or overlap across domains. Use `observe_only: true` for alias-only
cache and Repair checks; those domains must not replay another domain's journal.
The shared wrapper runs once. A degraded preflight returns 3 only when the shared
volumes/capacity passed; the wrapper then continues and the final aggregate returns
failure if any domain is blocked. Shared failures block every mutation.

`capacity_checks` records the actual resolved path, bytes and measurement time;
unavailable measurements are null. `health_receipt` is written only with `--apply`
and includes deltas, consecutive failures and a changed alert signature. Delivery
remains explicitly unverified until the existing monitor observes a receipt. Dry
run/preflight does not write that receipt or the PowerShell error log. D hardware
errors are never repaired, formatted, scanned or hidden by this helper.

The host policy keeps one TradingAgents worker owner, one Codex documents/dump/uv
owner, five cache aliases and one Repair alias. Retention (7 days, latest 2, 48-hour
quiet window; wrapper 7/14/30 days) and canonical archive preservation are unchanged.
The installed policy and scheduler XML are backed up before deployment; new tasks
or schedule changes are unnecessary.

When Work preparation finds the producer writer lock busy, it may consume an
already completed immutable result only if the manifest identity, success state,
original start/finish clocks, current market session, complete coverage, research
lineage and account/quote freshness all validate. Runtime.prepare pins the same
run and rechecks clocks under its state lock. Missing, stale, running or replaced
results remain BUSY without event allocation. This path performs no producer,
order or duplicate consumer handoff, and it does not extend any TTL.

Use `--health-only --apply` to persist current domain/capacity health without
starting retention I/O. This receipt is labelled health-only, never cleanup success.
The wrapper records its cleanup summary before propagating a degraded final exit.

## Long backup runs and truthful task status

The October 29 run exceeded the installed two-hour limit while verifying a second
41,583-file worker backup. Task Scheduler ended its hidden launcher at 18:30 KST
with result `0x41306`, while its PowerShell/Python children continued working.
The first backup had already finalized; the second remained in its verified
`prepared` journal phase. A scheduler end was therefore not cleanup completion.
Keep the surviving owner and journals intact; do not launch a competing cleanup.

The installer now uses `PT0S` so that the scheduler waits for the guarded worker's
real result. This is the documented [no execution time limit](https://learn.microsoft.com/en-us/windows/win32/taskschd/tasksettings-executiontimelimit)
setting. Daily timing, `IgnoreNew`, the maintenance mutex, retention and backup
validation remain in force. Python output streams into the maintenance log while
the process runs, with its original nonzero exit propagated after the summary.
Inspect process ownership, current journal phase, file I/O and log progress before
diagnosing a long run. Absence of new copy messages during a hash-verification
stage is not by itself evidence of a hang. An unrelated blocked storage domain
must still produce a failed aggregate result.

Read-only checks later distinguished a false Repair-path alarm from a missing
drive: D: retained its configured NTFS volume identity and about 602.5 GB free.
The alias and intended destination had the same nonzero volume/file identifiers,
but Windows final-path resolution returned error 433 for both. For this specific
error only, alias health may use those exact directory identities. Missing paths,
zero/unknown IDs, different targets, changed volumes and other errors still fail.
Capacity may use the existing directory directly after the same identity check;
the receipt retains error 433 and a null resolved path instead of claiming a
canonical path was resolved. This observes metadata only and does not modify,
repair, relocate or delete the unrelated project.
