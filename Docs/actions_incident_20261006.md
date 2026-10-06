# 2026-10-06 hosted runner incident and PR #333 follow-up

## Evidence and root cause

All times below are KST. GitHub job annotations, job steps, and run attempts
were inspected directly; email delivery time is not treated as job start time.

| Run | Failed job | Evidence |
| --- | --- | --- |
| [37367005555](https://github.com/nornen0202/TradingAgents/actions/runs/37367005555) | `overlay_gate` | 05:00–05:15, zero steps, no assigned runner |
| [37356828248](https://github.com/nornen0202/TradingAgents/actions/runs/37356828248) | `deploy` | Analysis and Pages artifact build succeeded; 05:50–06:05 deployment never started |
| [37368588073](https://github.com/nornen0202/TradingAgents/actions/runs/37368588073) | notification `resolve` | Zero steps, no assigned runner |
| [37373759298](https://github.com/nornen0202/TradingAgents/actions/runs/37373759298) | notification send job | Zero steps, no assigned runner |
| [37374304637](https://github.com/nornen0202/TradingAgents/actions/runs/37374304637) | notification `resolve` | Zero steps, no assigned runner |

Every failed job above has the failure annotation:
`The job was not acquired by Runner of type hosted even after multiple attempts`.
This establishes a GitHub-hosted runner acquisition failure before application
code execution. It does not establish GitHub's underlying infrastructure cause
or a platform-wide outage. The Ubuntu image migration notice is informational,
not evidence that migration caused these failures. There is no evidence here of
a self-hosted Windows cancellation, Telegram transport error, or failed analysis
in the US run. Its `github-pages-final` artifact was still unexpired at inspection.

Later green runs are not sufficient recovery evidence: overlay `37428642801`
and daily `37404115605` completed only their gate and skipped the producer and
deployment jobs. Existing scheduled watchdogs dispatch target workflows, but do
not specifically recover notification delivery or reuse successful analysis by
retrying only its unstarted deployment job.

## Changes

- Add `Hosted Runner Recovery` on the completion of the three affected workflows,
  with a manual inspection/recovery entry point. It uses the Windows hosted pool
  so the recovery controller does not depend on Ubuntu allocation.
- Fetch the current run, current-attempt jobs, and paginated check annotations.
  Require same repository/main, an allowlisted workflow/job, no steps or assigned
  runner, and the exact acquisition-failure annotation for every failed job.
  Reject application failures, manual cancellations, mixed failures, untrusted
  sources, active runs, future/older-than-24-hour runs, and attempts >= 3.
- Recheck attempt/status immediately before requesting `rerun-failed-jobs`.
  Per-upstream concurrency serializes this controller; successful analysis jobs
  are retained. Existing market gates, Pages rollback guard, and notification
  ledger remain active. Recovery reports an explicit reason and request outcome.
  This is bounded best-effort recovery, not a guarantee of hosted runner capacity
  or repeated webhook delivery during an infrastructure outage.
- Accept both bare REST workflow paths and documented `@main`/`@refs/heads/main`
  suffixes before the allowlist lookup; a commit suffix must equal the validated
  run's head SHA. Reject other suffixes. The incident responses used bare paths,
  so both representations are covered by regression tests.
- PR [#333](https://github.com/nornen0202/TradingAgents/pull/333) was merged before
  its two P2 comments. Preserve the newest valid research quote by aware provider
  timestamp, including out-of-order completions and equivalent timezone offsets.
  Later unavailable/invalid responses retain the valid quote and record a bounded,
  sanitized latest-failure receipt and failure count. No raw provider error is saved.
- Snapshot and compare `codex_max_retries` for recovery. Missing old settings and
  changed budgets are rejected; matching budgets remain eligible. Do not amend
  historical manifests to fabricate compatibility.

The retry endpoint preserves successful jobs and reruns failed jobs and their
dependents, per [GitHub's rerun documentation](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/re-run-workflows-and-jobs).

## Verification and separate findings

Regression tests cover quote retention, reversed callback completion order,
timezone comparison, failure-to-success recovery, detached diagnostic copies,
missing/changed/matching retry budgets, and recovery eligibility, pagination,
dry run, source trust, mixed failures, and concurrent attempt changes.

A live read-only recovery inspection selected all five incident runs and rejected
KR analysis `37396519749` as `job_started_or_not_allowed`. Both KR runs
`37376948702` and `37396519749` separately ended with 29/30 successful analyses
and correctly failed required coverage. In the latter, ticker `105560.KS` reported
`PROVIDER_ERROR / CodexAppServerError / UNKNOWN` after 1,246 seconds. This is a
separate provider/model execution failure, not the hosted acquisition incident.
The logs also contain Yahoo symbol-coverage warnings, but those do not prove the
cause of that ticker's model error. Do not automatically replay these expensive
full analyses under the infrastructure retry policy or claim their coverage was
repaired by a green gate-only run.

Operational replay results are recorded in the follow-up PR and completion report.
