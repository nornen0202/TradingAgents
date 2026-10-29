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

## Remaining acceptance work and limits

At review start, KR had no full production on October 28/29; the last was
October 27. The new same-day recovery must finish and publish before KR research
recovery is complete. Code tests alone cannot close that incident. End-of-session
or stale-input execution blocks remain valid until a real current observation.

The last full publisher took about 37 minutes. Parallel reads remove confirmed
serialization, but the full generation still needs measurement after deployment.
Storage and process checks are observations, not guarantees against disconnects,
power loss, upstream outages or future vulnerabilities. Keep protected-volume
headroom, original retry limits, exact configured model roles, as-of validation,
private/public separation and existing order permissions intact.

The local scheduled tasks use the existing interactive account. They require a
logged-in host; the Codex operations schedule additionally requires the desktop
app running. AC/DC automatic sleep was disabled at inspection. No login policy,
privilege, real-order permission, disabled legacy schedule, original data or
backup retention rule was changed as part of this review.
