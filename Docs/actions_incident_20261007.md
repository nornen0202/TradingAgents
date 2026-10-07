# 2026-10-07 missing KR analysis and stalled Pages deployment

## Verified cause and operational recovery

- US overlay [37485104962](https://github.com/nornen0202/TradingAgents/actions/runs/37485104962)
  completed refresh/build at 00:16 KST, but `deploy_overlay` remained `waiting`
  with zero steps and no assigned runner for more than 14 hours. GitHub's
  concurrency API identified that job as the holder of `tradingagents-pages-deploy`.
  Its pending environment had no reviewers or wait timer; the environment's
  only protection rule restricted deployments to `main`.
- The 08:12 KST KR probe [37545239889](https://github.com/nornen0202/TradingAgents/actions/runs/37545239889)
  explicitly skipped because that US deployment was waiting. Subsequent green
  KR runs likewise completed the gate without producing today's analysis.
- Work KR synthesis did run at 10:42 and 13:40 KST, but consumed the previous
  partial analysis: 29/30 succeeded, with KB Financial `105560.KS` failed. Its
  quotes and account observations were from October 6. Today's publication did
  not make those inputs current.
- KR handoff [37572642166](https://github.com/nornen0202/TradingAgents/actions/runs/37572642166)
  built successfully, then queued behind the stalled lease. Two earlier handoffs
  were cancelled as the shared concurrency group replaced its single pending job.
- Normal cancellation did not release the stalled run. A force cancellation
  released the lease; KR handoff 37572642166 then deployed successfully. The
  environment protection settings were not changed or bypassed.
- Today's complete KR producer was explicitly restarted as
  [37577525782](https://github.com/nornen0202/TradingAgents/actions/runs/37577525782).
  Starting that run is not a completion or delivery receipt.

Separate failures: US producer 37439146717 has the exact annotation that its
self-hosted runner lost communication with GitHub. Public mirror 37478112090
failed with HTTP 500 while creating a Git tree. Local service listener logs also
show repeated `A session for this runner already exists` conflicts: a service
listener and a current-user listener were running for the same registration.
These facts do not establish the underlying cause of the earlier communication
loss or a GitHub-wide outage.

## Repair

- Before ordinary watchdog dispatch, inspect the live Pages concurrency holder.
  Recover only an allowlisted main-branch deployment that has not started, has
  waited at least 45 minutes (at most 24 hours), has successful upstream jobs,
  and is waiting without an approval, timer, or custom environment rule. Recheck
  the lease and rules immediately before cancellation. If a newer snapshot is
  queued, let it proceed. Otherwise retry only failed jobs, retaining successful
  analysis/builds, with at most three run attempts. Snapshot rollback and Work
  lineage validation still apply.
- Queue shared Pages deployments instead of replacing the previous pending
  deployment. GitHub's `queue: max` allows up to 100 waiting jobs. See the
  [official concurrency documentation](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency).
- Treat running/starting runner services as owning startup even when the
  current user cannot read their listener process path. Use a per-runner-root
  keepalive mutex so the separate Pages runner has its own lock.
- Retry identical public mirror API requests on transient HTTP/connection
  failures, bounded to four attempts. Authentication, permissions, validation,
  and conflicting ref updates still fail explicitly; force pushes remain off.

## Verification

Focused tests cover the incident's stalled lease, successor preservation,
failed-job-only retry, attempt limits, dry run, protection rules, clock bounds,
concurrent job starts, queue wiring, a real PowerShell execution with an
invisible service listener, identical API replay, and permanent/error exhaustion.
Existing scheduler, hosted recovery, and public snapshot integrity tests passed.
A live dry-run returned `no_active_lease` after operational recovery.
