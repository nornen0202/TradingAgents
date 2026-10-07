# Proactive automation operations

The operator is responsible for the complete path from a due analysis to a
verified report. A successful GitHub gate, Work ACK, or accepted dispatch alone
does not prove that the user received the current strategy.

## Active schedule and ownership

On 2026-10-07, the Codex app registered the active thread heartbeat
`tradingagents`, **TradingAgents 능동 장애 점검·복구**, every hour at minute 55 in
Asia/Seoul. It returns to the incident-recovery conversation, retaining its
context. The app's Scheduled entry is authoritative; this file does not register
a schedule. The existing KR, US, YouTube and PRISM production automations remain
the primary report writers. The heartbeat repairs omissions after checking for
an active writer, rather than starting a second writer.

The GitHub Scheduled Actions Watchdog remains the first recovery layer, scheduled
every 15 minutes. The independent Codex heartbeat also checks whether that
watchdog ran. On the first check each KST day, review the last 24 hours for
recurring causes and implement supported preventive repairs.

This setup uses local files and requires the PC to be online with the desktop
app running. GitHub's hosted watchdog can continue independently, but cannot
repair an offline PC. A cloud Dot is an optional future coordinator, not an
activated dependency of this setup. Dots also need an online connected computer
for these local archives. See the official
[scheduled tasks](https://learn.chatgpt.com/docs/automations) and
[Dots](https://learn.chatgpt.com/docs/dots) documentation.

## Each check

1. Read `AGENTS.md` and the previous local operations receipt. Record the actual
   timezone-aware current time. Use `nornen0202/TradingAgents` and remote `fork`.
   Fetch fresh GitHub data; do not rely on a previous conversation's run status.
2. Inspect the latest watchdog, daily analysis, overlay, Work Pages refresh,
   mobile notification, public mirror, YouTube and PRISM runs. Inspect actual
   jobs, relevant steps and annotations for failures or apparent no-work runs.
   Query workflow-specific runs, with a created-time filter and pagination when
   needed, so a busy notification stream cannot hide an older producer.
3. Check both repository runners and the local service/worker state. The main
   runner uses `self-hosted, Windows, X64, codex`; the auxiliary Pages runner has
   only `tradingagents-pages`. Never operate on another repository's runner.
4. Read canonical sanitized archives under `C:/TradingAgentsData/archive` and
   `C:/TradingAgentsData/prism-telegram-archive`. Discover run manifests beneath
   the archive's date hierarchy; use their real schema and source lineage. Check
   latest attempt separately from latest completed analysis, heartbeat progress,
   holdings/watchlist coverage, failures, account observation, quote observation
   and research trade date. Never use automation memory or public Pages as a
   substitute for the private source packet.
5. Inspect canonical `.runtime/chatgpt-work` state, the exact acknowledged report,
   pending work and handoff receipts. Summarize selected fields rather than
   dumping event histories, portfolio data or secret-bearing logs. Read source
   health for YouTube/PRISM independently of their Work acknowledgement.
6. Compare the local KR/US acknowledged event and report hash with live
   `work/v1/<surface>/report/latest.json`, and check its lineage and full required
   ticker coverage in `mobile/strategy.json`. The base URL is
   `https://nornen0202.github.io/TradingAgents/`. Confirm the matching Pages job
   completed. For Telegram, inspect the matching notification receipt/log for
   `SENT`, or the exact documented reason for `SKIPPED`. Successful Work handoffs
   are intentionally silent; silence for that event is not a failed send.

Use the current workflow and market calendar as the schedule authority. At setup,
KR full-analysis probes begin at 04:35 KST and aim to finish by 10:00; its first
Work briefing is scheduled for 10:40, then 13:40 and 14:40. US analysis begins at
17:50 KST, aiming for 22:30, with Work at 23:10, 01:10 and 03:10. Resolve the US
session date across KST midnight and DST with the existing calendar. Weekends,
official holidays, healthy in-progress jobs and closed-market expiry are not by
themselves incidents. Publication time never refreshes the inputs. A recovered
producer finishing after the last Work slot still needs its report published.

## Recovery decisions

| Evidence | Action | Completion evidence |
| --- | --- | --- |
| Watchdog has not started for over 60 minutes and none is active | Dispatch `scheduled-actions-watchdog.yml` once on `main`, with `dry_run=false`; record its run ID and inspect its output | Actual watchdog completion and the due target's run ID or a justified covered/held result |
| Watchdog is active but making no progress | Inspect its jobs and lock holder; do not enqueue another copy | Progress resumes or an explicit unresolved blocker is recorded |
| Due producer absent | Prefer the existing watchdog's calendar, dependency, active-job and retry-budget checks | Real producer job starts and local heartbeat advances |
| Partial analysis with failed tickers | Validate strict failed-only compatibility, then dispatch daily analysis with the real local `resume_from_run` archive ID | All required tickers succeed; successful source research is reused |
| Successful build blocked by an unstarted Pages lease | Use `.github/scripts/recover_stalled_pages.py` through the watchdog, with all its existing protection checks | Lease released and the intended report actually deployed |
| Verified hosted allocation failure | Use `hosted-runner-recovery.yml` / `recover_hosted_runner.py` | Failed jobs rerun without repeating successful analysis |
| Local runner offline or duplicate session | Inspect the owning service and use the service-aware keepalive; act only on a verified idle duplicate belonging to this repo | GitHub runner online and the intended job progresses |
| Producer completed but Work is absent, older or interrupted | Check active surface ownership, then follow the repository Work skill locally | Exact report published, ACKed, handed off and verified live |
| ACK exists but Pages delivery failed | Inspect the existing dispatch; retry its failed deployment, or use exact `handoff --force` only after proving the original is inactive/failed | Live event/hash matches the current canonical report |
| Current quote/account data unusable | Use an existing permitted read-only refresh path when due; retain all execution gates | Actual observation times, coverage and correct readiness; otherwise explicit `NEEDS_LIVE_RECHECK` |
| Repeated code defect with evidence | Isolated worktree, minimal fix and regression checks; commit, push `fork`, open PR, pass required CI and merge | Tests pass and the production symptom is rechecked |

The watchdog also runs `recover_missing_followups.py`. Completed watchdog-dispatched
Daily/Overlay/YouTube producers can miss their `workflow_run` notification and
mirror: GitHub suppresses events caused by `GITHUB_TOKEN`, while explicit
`workflow_dispatch` is exempt ([GitHub event rules](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow)).

After a three-minute completion grace, the reconciler uses paginated run history
and exact upstream ID/attempt markers to dispatch only missing followups. It
preserves active ownership, rechecks immediately before dispatch, waits fifteen
minutes before retries, and counts all followup runs and reruns toward a three-attempt
budget per upstream. Gate-only producers are ignored; mirrors require successful
deployment. The existing notifier still verifies the upstream and deduplicates
Telegram sends. The existing mirror still verifies public content hashes.

The rollout starts with producer runs created at or after 2026-10-07 15:59 UTC;
earlier incidents were manually delivered before the provenance markers existed.
Recovery looks back 24 hours. Older or budget-exhausted incidents require this
operator's evidence-based repair, not another unbounded retry. A successful
followup workflow is only coverage for dispatch deduplication: operations must
still verify `SENT`/policy `SKIPPED` and actual mirror/Pages contents.

For Daily analysis, an unidentified native scheduled run that is still queued
with no jobs and was created before the target production window does not cover
that new window. An October 8 check reproduced an earlier US-era queue blocking
KR recovery this way. The old run is left intact. Any run with jobs, an explicit
matching profile, a current/missing creation time, or a manual trigger retains
the conservative active-ownership guard. A queued coverage result never proves
analysis completion; verify the local manifest and heartbeat separately.

For Work publication, read and apply
[the repository Work skill](../.agents/skills/tradingagents-daily-investment-work/SKILL.md).
Keep its canonical local runtime directory even when code repairs use a worktree.
Use `prepare -> compose Markdown + structured JSON -> publish -> ACK -> handoff`.
Respect `NOOP`, `RESUME`, busy and regression results. Do not manually clear or
overwrite pending state. An existing pending event can belong to an active
scheduled writer; check before resuming it. Preserve thesis, required rows,
receipt binding and execution gates. Do not re-ACK to repair a deployment.

All retries count toward the existing incident budget, including native,
watchdog and manual attempts. A new heartbeat must not reset that budget. Group
the same profile/stage/diagnostic and unchanged code into one incident; a changed
run ID or a new check time is not a new cause. If the budget is exhausted, diagnose
and fix the cause instead of dispatching another identical attempt. Never amend
historical manifests to pass compatibility, bypass environment protection, stop
an active worker, force-push, weaken market/account/risk gates or place orders.

When a default model changes during an active producer, failed-only recovery
preflight selects the original terminal source's model roles. Ordinary production
keeps the new defaults. The recovery runner still requires exact research settings,
a current loaded account and intact successful artifacts; model pinning does not
relax those checks or change the global configuration. An unavailable original
model or unsupported role pairing fails closed before research starts.

Do not keep a foreground turn waiting for hours of analysis. After confirming
progress, record the active run, remaining checks and next scheduled check; the
heartbeat continues from that record. This is `IN_PROGRESS`, not a verified
recovery. Use waits of at most 60 seconds while actively checking.

## Durable receipts and reporting

Store credential-free operations evidence in the canonical main checkout:

- `.runtime/automation-operations/latest.json`: latest check, atomically replaced.
- `.runtime/automation-operations/YYYY-MM-DD/<timestamp>.json`: immutable checks.
- `.runtime/automation-operations/incidents.jsonl`: append-only incident changes.

Record schema version, observed time, automation ID, overall status, incident
fingerprint, first/last observation, affected session/profile, evidence run IDs,
attempts, repair action, expected result, next check and unresolved blocker.
Include actual report event/hash and separate dispatch/deployment/live-content
verification fields. Do not set `external_delivery_verified` from dispatch
acceptance. Leave inaccessible evidence `UNKNOWN`; never guess a healthy state.
Keep corrupt receipts for diagnosis rather than silently resetting them.

Report the impact, confirmed cause, performed repair, verified result and any
remaining action in Korean. For a healthy check, keep the result short. Preserve
normal failure notifications; do not mute them to make the system appear healthy.
Use the repository's existing notification pipeline for external delivery.
Do not send messages to unrelated chats or people. Ask the user only when a real
missing permission, login or decision prevents the authorized repair.

## Initial live exercise, 2026-10-07

The first check found the latest scheduled watchdog at 15:10 KST, although it is
configured every 15 minutes. By 18:56 there was no US producer in that session's
window. This is observed scheduling delay, not proof of a GitHub-wide outage.
Manual watchdog [37604015126](https://github.com/nornen0202/TradingAgents/actions/runs/37604015126)
completed, returned `no_active_lease`, and dispatched the missing US analysis as
[37604062164](https://github.com/nornen0202/TradingAgents/actions/runs/37604062164).
Its analysis was still running at setup; completion and delivery require later
verification. The heartbeat's local receipt carries this outstanding check.

Earlier incident details and transport/runner repairs are in
[the October 7 incident record](actions_incident_20261007.md).
