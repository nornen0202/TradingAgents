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
  and defers full or selective research without spending a research attempt. It does not reset
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
- Windows Python and PowerShell file locks no longer write an initial byte
  before acquiring the lock. A deterministic regression reproduced the old
  empty-file race and confirmed that contention now follows the bounded timeout.
- Institutional evidence requires an explicit cutoff and verifiable publication
  or observation clocks. Future, missing and malformed dates are excluded before
  evidence selection and quality calculations, including nested source records.
- Chart catalog invalidation compares manifest content digests, so a change with
  the same file size and timestamp cannot silently reuse stale catalog content.
- Site discovery reads the supported flat and year/run manifest layouts without
  descending into ticker artifacts. Both methods found the same 1,258 manifests
  in the frozen archive; enumeration measured 59.2 seconds before and 0.029
  seconds after. This measures enumeration, not complete site generation.
- Storage failure alerts now explain unavailable drives and the 4 GiB admission
  reserve in Korean. Fixed text preserves the outbox's exclusion of private paths
  and raw diagnostics; event identity, deduplication and retry limits are unchanged.
- Site rendering shares the existing verified-manifest cache across tickers in
  one run, then discards it before the next run. Every owner analysis, artifact
  digest and source clock is still verified. Regression tests compare complete
  HTML, reject changed owner evidence, and reject a source beyond the next run's
  earlier cutoff. No process-global or cross-run evidence cache is introduced.
- Scheduler discovery retains canonical order and reads/parses every original,
  including malformed older JSON, using at most four parallel projected reads.
  Submission and parse memory are bounded by four files; there is no historical
  cutoff shortcut or persistent cache. A live read-only comparison of 1,264
  identical paths produced the same view digest in 23.5 seconds with four
  readers versus 40.7 seconds serially. This is a loaded-host discovery probe,
  not an end-to-end freshness guarantee. Idle or delegated research ticks defer
  discovery until a target actually needs archive evidence, avoiding a second
  unnecessary full scan alongside the minute producer.
- The exchange-calendar wrapper retains at most the two default KR/US calendars
  per factory and actual day. Upstream retains only the last range per exchange,
  so explicit history windows previously evicted the default session calendar
  and triggered repeated construction during quote refresh. Explicit ranges,
  official daily closure checks, exception propagation and freshness gates are
  unchanged. Offline tests cover range/default alternation, day and factory
  changes, failed construction and serialized concurrency.
- Work attempt discovery checks for an existing attempt receipt before reading
  a legacy manifest, and only reconciles a full result for a RUNNING attempt.
  Terminal attempts and minute overlays no longer cause redundant expanded
  manifest reads. Legacy-run selection and interrupted-run handling are retained.
  Work source-clock discovery overlaps two reads while retaining the existing
  three-manifest memory bound, producer-clock ordering and selected-source
  reread/consistency checks.
  YouTube/PRISM manifest discovery reads the supported flat and year/run layouts,
  avoiding recursive transcript/evidence traversal and nested manifest impostors.

## Code and dependency acceptance

PRs #470, #471, #472, #473, #474, #475 and #476 were merged into `fork/main`
after their required checks. The final Windows CI runs for #472, #475 and #476
each passed 6,290 tests and 131 subtests, with one skip, plus all four browser
regressions and CodeQL. CI run IDs are 40613867218, 40613898111 and 40618058948.
The local Python 3.14 dependency probe also passed the full application suite.

The operational virtual environment now uses pypdf 6.21.2, langgraph-checkpoint
4.3.1, langgraph-checkpoint-sqlite 3.1.2, filelock 4.2.4 and setuptools 84.1.0.
`pip check`, PDF round-trip, exclusive lock and SQLite checkpoint round-trip
checks passed after installation. A live response through `create_llm_client`
using the configured `gpt-6.1-sol` model passed with zero retries and no model
fallback. These checks do not prove completion of a new market analysis.

GitHub reported zero open Dependabot alerts after the dependency merges. See
`dependency-security-recovery-20261028.md` for the advisory scope and Python 3.10
compatibility rule. Do not reintroduce affected versions through a lock refresh.

## Operational verification

The migration audit directory is `H:\TradingAgentsAudit\20261028`. Keep its
receipts and task exports for recovery; they are local operational evidence,
not files for public Pages. Runtime content verification covered 148,753 files
and 4,958,053,694 bytes with no mismatches. The four current KR/US strategy and
validation SQLite ledgers passed `quick_check` after runtime cutover. The
existing enabled flags, allocations and `real_orders_enabled=false` were retained.

The runtime now resides at `H:\TradingAgentsRuntime\runtime`, with the original
`C:\Projects\TradingAgents\.runtime` path retained as a junction. At 11:41 KST,
the main archive was switched to `G:\TradingAgentsData\archive` after a complete
SHA-256 and stable-inventory verification of 897,496 files / 52,543,145,845 bytes.
`C:\TradingAgentsData\archive` remains its junction. PRISM's sanitized archive
uses the same arrangement at `G:\TradingAgentsData\prism-telegram-archive`;
its 640 files / 5,205,083 bytes and independent L: backup passed verification.

After cutover, KR and US owned research references were successfully read through
the original aliases. Isolated write, atomic replacement, cross-process lock and
probe cleanup checks passed on both the archive and runtime volumes. Original
runtime files are preserved at `G:\TradingAgentsBackups\runtime-original-20261028`.
The main archive original backup destination is
`L:\TradingAgentsBackups\archive-original-20261028`; acceptance of that move
requires `archive-original-backup-result.json` plus the final backup inventory
in the audit directory. The preservation worker must not be duplicated while
its recorded process is still active. Originals include NTFS-compressed files,
so logical archive bytes are not the same as reclaimed C: disk allocation.

The original backup move finished at 13:01:56 KST with zero failed or mismatched
files. At 13:08:52 the independent inventory accepted all 897,496 files /
52,543,145,845 bytes, found no source files remaining on C:, and passed four
SQLite checks on private clones. C: had 37,673,783,296 free bytes (35.1 GiB).
The G: canonical copy had already passed complete content hashing; L: acceptance
combines successful preservation, the empty source, exact inventory totals and
database checks. It is not a second complete hash pass over L:.

The cutover guard found one historical GitHub request, run 37655538332 from
October 7, whose API status remains `queued` despite zero jobs. Normal cancel
reported it completed; force-cancel returned HTTP 409, saying it had never been
queued. Its legacy workflow remains disabled and its history was preserved.
Only this exact, unchanged, never-admitted request was excluded from the
one-off writer check after rechecking those facts. Other queued or active writers
still block cutover. This matches the production scheduler's existing distinction
between an expired unstarted request and a real writer.

Post-recovery production must be checked against actual current receipts;
neither a copied archive nor a successful model response proves report delivery.

At 12:07 KST all eight original Windows tasks were enabled again, including
StorageMaintenance. The seven producer task definitions retained their original
actions, triggers and principals. Maintenance now explicitly selects
`C:\TradingAgentsMaintenance\tradingagents-storage-policy.json`, a project-only
policy covering the three migrated aliases and verified G:/H:/L: volume IDs.
Its PowerShell wrapper and Python policy dry-runs passed without deleting files.
The 30 GiB warning / 12 GiB critical C: reserves remain separate from the 4 GiB
per-volume producer admission requirement.

The eight Codex app automations are ACTIVE with their original models, reasoning
efforts, schedules, working directories and execution destinations. YouTube and
PRISM collector workflows are enabled. Obsolete cloud producers and the four
superseded October 23 migration tasks remain disabled. The existing monitor now
references the accepted migration receipts and the pending US delivery checks.

The first restored KR overlay, `20261028T120810_local-scheduler-kr-overlay_only`,
completed at 12:11:24 KST with 30 successes / zero failures on revision b107fcc8.
Its production-time decision gate passed, and subsequent minute freshness runs
completed. This reused existing research; it is not a new full analysis or a
promise that an expired quote is still executable.

At 12:22 KST the actual US `prepare --refresh-market` command returned
`MARKET_CLOSED` with no event creation or orders. A new US report is therefore
still pending the scheduled full analysis and report workflow. The restored
schedule includes the 17:50 KST full run and 23:10 / 01:10 / 03:10 KST Work reports.
The monitor must verify coverage, freshness, publish, acknowledgement and exact
external bytes; it must not infer delivery from a successful model probe or old
`DELIVERY_VERIFIED` receipt. At this checkpoint the resumed publisher was still
building, so October 27's receipt was not accepted as recovery evidence.

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
