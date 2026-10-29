# Automation recovery and publication failures, 2026-10-29

## Observed failures

- The October 28 18:51 US full run finished 29 successful ticker workers and one
  failed DELL worker, then remained in optional postprocessing until its original
  12-hour parent timeout. No terminal `run.json` was saved. The existing selector
  could not reuse the 29 successes and started a third full attempt at 06:57 KST.
- Work US prepare PID 49400, started at 03:10 KST, was still inside Python's
  `tempfile._mkstemp_inner` at 09:27. The Windows implementation can repeatedly
  swallow PermissionError when `os.access` reports writable, including actual
  access-policy denial. No successful new report delivery was established.
- PRISM Actions run 40789927596 completed collection but failed rebuilding the
  merged site with MemoryError in immutable research `_read`. It allocated the
  64 MiB maximum even for small files. The archive contained 1,319 manifests,
  approximately 1,206 MiB of JSON, and the local publisher used about 2.3 GiB.
- The current US third attempt also rejected CVX malformed provider OHLCV. This
  remains a real data-quality failure; the repair does not accept invalid bars.

## Changes

Partial full research now immediately publishes its terminal partial manifest
and attempt, preserving original successful artifacts for existing failed-only
recovery. News, portfolio, performance, execution and delivery cannot prevent
that checkpoint. Existing lineage, model, date, coverage and retry-budget checks
remain authoritative. Fully successful and portfolio-only runs retain normal
postprocessing.

Atomic JSON temporary creation now uses exclusive unique sibling names, retries
only genuine name collisions with a finite bound, and propagates permissions or
disk errors immediately. Existing bounded Windows replacement retries remain.
No ACLs or execution permissions are widened.

Immutable evidence reads allocate the already-validated file size plus one byte,
preserving size/change/digest verification. Site discovery shares equal research
subtrees within its read-only build with a bounded index; source files and report
values are unchanged.

## Acceptance

Offline tests cover partial and skipped research in parallel/sequential modes,
multi-hop recovery, permission/disk denial, collisions, evidence growth/shrink,
and equal-vs-different research rendering. Live delivery must still be verified
against the exact new event/report/publication; an older DELIVERY_VERIFIED receipt
or successful notification is not evidence that the missing US report arrived.
