# Automation resilience review — 2026-10-29

## Scope and acceptance

A verified report publication does not establish current research availability,
execution eligibility or notification delivery. Review these independently using
canonical manifests, actual completion clocks, exact public bytes, and Telegram
result receipts. A queued dispatch, successful connectivity check, closed market,
or historical disabled task result is not an analysis completion or trading approval.

The earlier delivery recovery verified 67 public files: 17 daily analyses and 19
Work reports dated October 22 onward. US recovery
`20261029T124921_manual-us-failed-recovery` completed 30/30, reusing 27 immutable
research results and analyzing the three failed names. The original US session
spent three scheduled attempts and one manual recovery: its cumulative limit of
four remains exhausted. The original failures and timestamps remain unchanged.

## Findings and repairs

| Finding | Repair | Acceptance evidence |
| --- | --- | --- |
| A completed manual US repair was excluded by the production-label filter | Verify its canonical completed attempt, failed parent chain, frozen cohort, exact settings, original artifact hashes, and new research clocks before admission | Offline corruption/clock/cohort cases; actual US manifest verified without modification |
| Recovery completion could renew the apparent age of copied research | Age and exchange-session limits use the oldest carried research start | Original source clocks survive recovery; stale recovered cohorts remain ineligible |
| Missing/future completion clocks could qualify as full baselines | Require explicit success and aware ordered start/completion clocks at the read cutoff | Missing, malformed, naive, reversed and future completion fixtures |
| The older US retry was admitted before the newer KR daily window | Order by original window, hold older full research while the newer market lacks completion, and retain active-market safety checks | KR-first and US-still-open tests, with unchanged attempt keys |
| A missed daily window disappeared from due work | Explicit same-day `research-kis --catch-up-market kr/us` through the normal lane lock, preflight, attempt counter and strict worker | Original window key, actual current start, no orders, exhausted-budget and invalid-window tests |
| One damaged historical manifest or outbox receipt could block unrelated notifications | Isolate invalid records, preserve them, and write bounded diagnostics by stage/surface/event | Healthy events dispatch once despite corrupt neighbors; exception contents excluded |
| Advisory lookup stopped at the first 100 workflow runs | Bounded complete pagination, preserving unique successful producer provenance | Producer on page two admitted; truncated/repeated/ambiguous history rejected |
| A terminated build could retain the old local DELIVERY_VERIFIED marker | Write BUILDING before touching the local tree, and rebuild incomplete generations even with unchanged inputs | Exception and process-interrupt tests; the public branch remains the previous verified generation until push |
| Account-history reads and recovery hashing serialized removable-volume I/O | Bounded four-worker reads with deterministic ordering and every source/date/hash check preserved | Parallel barrier test, tie behavior, unreadable snapshots and existing privacy/date checks |
| New security advisories affected LangGraph and the Python 3.10 filelock exception | Merge dependency PR 484; require Python 3.11+, filelock 4.2.1+, langgraph 1.2.14+, SDK 0.4.6+ (locked 0.4.10) | Frozen lock export; application tests with staged new dependencies; CI gate |

## Operational recovery procedure

Use the installed immutable-source launcher. Ordinary task schedules must not
include catch-up flags. For a confirmed missed same-day KR window, between
10:15 and 17:45 KST, use `-Command research-kis -CatchUpMarket kr`.
For the preceding US session, the supported catch-up interval is after 08:00
and before 17:45 KST. `-DryRun` uses a separate log and spends no attempt.
An active research owner wins the lock; never terminate it to force this command.
The wrapper records catch-up output in a separate log so normal minute/five-minute
checks cannot fail on its open log handle. Prior-day missing production remains
MISSED; do not backdate a new run or rewrite historical reports as timely results.

Check `notifications/health` alongside dispatch/result receipts. CHECKED means
reconciliation ran, not that a message was delivered. AdvisoryProducerNotVerified
means the published collection has no unique successful publish-enabled producer;
never manufacture a successful owner from a failed workflow or a no-work retry.
The October 29 PRISM collection succeeded, but its owning workflow failed later.
Its public report was recovered; that does not authorize a false success receipt.

### Verified publication recovery after a successful collection

The remaining PRISM notice exposed a separate recovery gap. The original
collection step succeeded, and the sole failed step was the publish-enabled
merged-site build. A later local publication recovered the exact source, but
the original workflow correctly remained failed. A skipped collection in a
later successful no-op cannot replace that owner.

The notification path now admits this specific recovery only with the original
trusted main workflow and exact attempt, one successful collection containing
the canonical clocks, exactly one failed merged-site build, a skipped snapshot
and native deployment, no other failed/cancelled steps or jobs, and a verified
local publication after the failed stage. The sender rechecks canonical hashes,
the local owner, current publication lock, and exact live packet/site bytes.
Collection failures, unknown failures, publish-disabled runs, ambiguous owners,
future or missing clocks, changed originals, and pending publication remain
ineligible. The message explicitly describes publication recovery and the
receipt preserves the upstream failure. It uses the original advisory event
identity and existing retry budget; no source is recollected or relabeled.

Live observation also found the minute producer reading about 736 MB while
scanning notification history and holding the publication lock for over a
minute. The scan now reads at most four originals concurrently, preserves
every validation and a fixed cutoff, and queues results serially in original
order. Durable diagnostics record scan count and duration. Tests verify the
concurrency bound, serial outbox writes, corrupt-neighbor isolation, and
duplicate suppression even after a newer publication of the same source.
The live four-reader probe still took 45.1 seconds for 1,321 manifests under
concurrent production. Completion discovery therefore belongs exclusively to
the publication lane, which runs it even for an unchanged verified generation.
The minute producer dispatches existing events and failures without rereading
the historical archive or discovering advisory producers. This keeps completion
recovery active without delaying fresh observation production.

### Operational acceptance recorded during the review

- PR 494 merged as `fae53db7acd95506f96fdd116e24e754afa7218d`.
  Final CI 40831831947 passed 6,484 tests and 131 subtests (one platform skip),
  mobile/report/chart checks and CodeQL. Production and installed launcher
  hashes were adopted at 16:10 KST; untracked user work was preserved.
- The live Python environment now has LangGraph 1.2.14, SDK 0.4.10 and filelock
  4.2.4. Imports and dependency checks passed; open Dependabot alerts became zero.
- US recovery notification event
  `68a3015618a53a3c51ca84d209867c1ebef41d47472c703535939916137729c2`
  was SENT once by successful workflow 40833908824, message 825, verified at
  16:13:19 KST. The original research attempt budget remains exhausted.
- KR recovery `20261029T161248_local-scheduler-kr-full` started at 16:12:48 KST
  against the original October 29 04:30 window, attempt one of four, after a
  successful dry run. Its completion and delivery remain pending.
- The operational latest ledger was an October 9 CP949 document. Exact original
  bytes and a strictly decoded, equality-checked copy were preserved. Current
  review records now use atomic UTF-8 JSON. The existing operations automation
  prompt was updated without changing its schedule, model or effort.

## Remaining acceptance work and limits

### KR failures observed during the real catch-up

The original October 29 KR catch-up exposed two distinct data failures before
completion. Its healthy workers continue on immutable source `fae53db7`; original
failures, attempt counters and successful research clocks are preserved.

- `179880.KQ` (Melcon): Yahoo omitted the first regular session, October 15,
  2026. The [KRX new-listing notice](https://kind.krx.co.kr/external/2026/10/13/000679/20261013001545/70760.htm)
  and [separate trading-reference notice](https://kind.krx.co.kr/external/2026/10/14/000511/20261014000808/72100.htm)
  bind that date to common-stock ISIN `KR7179880000`. A current public KIS master
  independently binds the same identity. There are only ten real sessions through
  October 28: even after correcting the missing first bar, longer indicators
  remain unavailable.
- `443670.KQ` (SPSoft): Yahoo omitted September 19, 2025. The
  [KRX SPAC-dissolution new-listing notice](https://kind.krx.co.kr/external/2024/02/13/001310/20240213003429/70980.htm)
  and [separate trading-reference notice](https://kind.krx.co.kr/external/2024/02/14/001266/20240214003127/70718.htm)
  establish a **new operating-company security**, ISIN `KR7443670005`, first
  trading February 15, 2024. This is an explicit reviewed event; neither an
  ordinary SPAC reverse merger nor predecessor IBKS 19 prices are admitted.
- Prechecking the eight not-yet-started tickers found the same unverified history
  boundary for `419050.KQ` (Samkee Energy Solutions, originally Samkee EV).
  The [original KRX listing](https://kind.krx.co.kr/external/2023/02/01/000811/20230201002370/70760.htm)
  binds ISIN `KR7419050000` to February 3, 2023; a
  [separate first-session reference](https://kind.krx.co.kr/external/2023/02/02/000412/20230202001250/70793.htm)
  corroborates the day. The [exchange rename notice](https://kind.krx.co.kr/external/2025/04/15/000602/20250415001572/70765.htm)
  explains the current master name without replacing security identity. Its
  actual review clock is October 29 08:54 UTC. Read-only corrected validation at
  17:55 KST verified all 909 required sessions in ten KIS calls. The other seven
  remaining tickers passed actual price and six-indicator input checks.

The reviewed-event registry stores the original source hashes and actual October
29 08:34 UTC collection clocks. It cannot qualify earlier historical analyses.
Admission still requires the exact current master, an aware evidence cutoff, and
every KRX regular session since the verified first listing within the original
requested window. Recovery replaces the entire series from one adjusted-price
provider; it never patches individual Yahoo bars with another provider's values.
Future and unverifiable dates remain excluded; missing regular sessions fail.

The analyst Tool now returns explicit `UNAVAILABLE`, null value and no execution
authorization for insufficient/unverifiable indicator history. The failed vendor
request remains failed in its original telemetry. A later valid short indicator
cannot clear the missing long-indicator evidence or new-entry execution gate.
This allows an honest limited-history report without terminating the whole
company analysis. Unrelated integrity/runtime exceptions still propagate.
Public diagnostics classify typed indicator-history, invalid-data and exhausted
provider errors without inspecting private exception text or changing retry
permissions.

Read-only live validation at 17:44 KST returned ten Melcon and 656 SPSoft bars
through October 28, complete over their exact required sessions, in one and seven
bounded KIS calls respectively. It used an isolated cache and sent no orders.
Offline validation passed 300 history/evidence cases and 89 related vendor,
diagnostic, analyst and deterministic risk cases (five overlap). These include
empty, future, missing and malformed dates, predecessor/identity mismatches,
pre-review clocks and the mixed available/unavailable indicator gate. Full CI and
actual failed-only research completion/delivery are separate acceptance steps.

### Additional deployment and publication observations

- PR 495 merged as `be4de8e4`; CI 40836158926 passed 6,519 tests and 131 subtests,
  plus browser/CodeQL checks. The PRISM recovery notice was actually SENT once
  by workflow 40838184663, message 826, at 16:52 KST. Its original owning workflow
  remains failed. US message 825 remains SENT once.
- A complete publisher exercise returned zero at 17:17:53 KST. Total elapsed time
  was 22 minutes 29 seconds; the core Pages build took 18 minutes 27 seconds.
  Publication `cd5c2010a0112f453c49a66e85318388207ddf8e` was DELIVERY_VERIFIED at
  17:16:53 KST with a verified public mirror. All 67 selected public files were
  checked against committed bytes. Repeated publication did not resend either
  existing notification.
- PR 496 merged as `e352f211` and was adopted at 17:38 KST after all PR checks
  passed. Repository Work contracts now match the user's already approved saved
  model efforts and schedules; the installed settings were not changed. Declared
  model configuration is not represented as runtime observation.
- Runtime comparison found two remaining installed-version drifts: cryptography
  49.0.0 versus locked 50.0.0, and soupsieve 2.8.4 versus 2.9. Correct versions were
  staged and their encryption/selector smoke checks passed. Live installation
  awaits a safe idle interval; healthy research must not load mixed dependencies.

At review start, KR had no full production on October 28/29; the last was
October 27. The new same-day recovery must finish and publish before KR research
recovery is complete. Code tests alone cannot close that incident. End-of-session
or stale-input execution blocks remain valid until a real current observation.

The completed publication exercise above measures the deployed parallel-reader
path. Future builds can still vary with archive size and storage/network load.
Storage and process checks are observations, not guarantees against disconnects,
power loss, upstream outages or future vulnerabilities. Keep protected-volume
headroom, original retry limits, exact configured model roles, as-of validation,
private/public separation and existing order permissions intact.

The local scheduled tasks use the existing interactive account. They require a
logged-in host; the Codex operations schedule additionally requires the desktop
app running. AC/DC automatic sleep was disabled at inspection. No login policy,
privilege, real-order permission, disabled legacy schedule, original data or
backup retention rule was changed as part of this review.
