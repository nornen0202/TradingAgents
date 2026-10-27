# Local storage and automation recovery — 2026-10-28

## Confirmed causes

- C: had about 2.9 GiB free at investigation start. The local producer requires
  4 GiB on **each** resolved archive, state and LLM workspace volume.
- Earlier work moved the LLM workspace to G:, but left the canonical archive
  (48.924 GiB / 896,468 files) and repository runtime (4.618 GiB / 148,753 files)
  on C:. The October 23 online archive copy was explicitly incomplete; it was
  never an accepted migration. Cache cleanup temporarily freed space but did
  not relocate the growing outputs.
- Storage maintenance correctly returned failure after cleanup still left C:
  below its 12 GiB critical reserve. A failure log alone did not repair capacity.
- Infrastructure admission failures consumed research attempts even though no
  LLM research started, so freeing space alone could leave that slot exhausted.
- The October 26 US full run had 4 successful and 26 failed tickers. The failed
  rows recorded `CodexAppServerError` with exhausted HTTP 429 retries. That generic
  message did not activate the existing provider circuit. The canonical US Work
  report was last published on October 22; a successful publication of old files
  must not be described as a new US analysis.
- D: reported Windows disk event 51 and NTFS event 140 (device unavailable while
  flushing). It is excluded from this project's migration destinations. This
  hardware/connection fault is separate from C: capacity and requires host repair.

## Code changes

- Storage exceptions identify the resolved failing path and measured reserve.
- A known storage admission failure queues the existing deduplicated notification
  and defers production without spending a research attempt. It does not reset
  historical receipts, extend model retries, bypass data gates or alter orders.
- Repeated, identified Codex HTTP 429 failures use the configured consecutive
  failure threshold. A data vendor's HTTP 429 does not open the LLM circuit.
- The launcher accepts `-RuntimeRoot`, routes child temporary files to that
  volume, and derives the PRISM archive from the archive's parent directory.
  Existing installations remain compatible with their original paths.
- `tools/verify_storage_copy.py` verifies complete inventories, SHA-256 content,
  stable source/destination metadata and SQLite integrity before cutover. SQLite
  checks use private clones including WAL, so verification cannot alter the
  original shared-memory files. Reparse entries, extra files and mismatches fail
  verification. It never deletes a source or destination.
- Scheduler and notification unit tests no longer depend on the host's real C:
  free space; dedicated reserve and admission tests still exercise failure.
- Operations documentation reflects the actual local scheduler and independent
  six-times-daily Codex maintenance schedule instead of the obsolete heartbeat.

## Operational verification

The migration audit directory is `H:\TradingAgentsAudit\20261028`. Keep its
receipts and task exports for recovery; they are local operational evidence,
not files for public Pages. Runtime content verification covered 148,753 files
and 4,958,053,694 bytes with no mismatches. The four current KR/US strategy and
validation SQLite ledgers passed `quick_check` after runtime cutover. The
existing enabled flags, allocations and `real_orders_enabled=false` were retained.

The runtime now resides at `H:\TradingAgentsRuntime\runtime`, with the original
`C:\Projects\TradingAgents\.runtime` path retained as a junction. Archive
cutover and post-recovery production must be checked against their final audit
receipts; neither a staged copy nor an LLM preflight proves report delivery.

Exact configured-model preflight succeeded. The mobile layout, strategy
interactions, report reading/navigation and archive chart/replay browser
regressions passed. Full-suite results and final migration/production receipts
are recorded in the audit directory.

## Pull request reconciliation

PRs #325 (`urllib3 2.8.0`), #335 (`multidict 6.9.1`) and #336
(`langgraph-sdk 0.4.4`) were already superseded: each target package's complete
lock entry was identical on `fork/main`, including distributions and hashes.
They were closed as redundant rather than reapplying old lockfile changes.

## Recovery rules

1. Pause relevant writers and preserve task definitions before filesystem work.
2. Copy without deleting the source, verify content and database consistency,
   quarantine any stale destination-only files, and then verify again.
3. Retain original paths as verified aliases and preserve an independent original
   backup. Never convert an unverified staged copy into the canonical archive.
4. Resume the existing tasks and check resolved volumes, current run metadata,
   actual publication lineage and notification receipts independently.
5. Preserve missed sessions and old failed attempts. A repaired disk or model
   preflight is not a retroactive successful analysis. During a closed US session,
   do not manufacture a current actionable Work report from old prices.
