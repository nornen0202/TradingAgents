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

### Current local backend and Telegram delivery

Since October 10, `TRADINGAGENTS_AUTOMATION_BACKEND=local` gives the existing
`LocalAutomation-run-due` and `LocalAutomation-publish` tasks production and
publication ownership. The cloud watchdog and core cloud writers are intentionally
disabled. Do not re-enable or dispatch them solely because their last run is old;
check the actual local task, manifest and receipt instead. The older cloud recovery
instructions below apply when GitHub owns production or a real admitted cloud
writer needs recovery.

The October 12 investigation confirmed that KR research completed at 09:40 with
30/30 tickers, while no local producer invoked Telegram. Cloud `workflow_run`
notifications cannot observe local Python completion. The notification workflow's
cloud guard had already been repaired, but that did not create a local event bridge.

The local producer now records safe terminal failures, including preflight
exceptions, and the publication lane reconciles `notifications/events` into the
existing `tradingagents-mobile-notifications.yml` workflow using an exact outbox
hash. The trusted main job on the Pages runner validates canonical completion and
live publication before using the existing deployment Telegram secrets. No bot
credential is copied into local configuration or an outbox. Daily completion is
backfilled only within 24 hours; historical overlays are not replayed. New overlays
after bridge activation retain completion notices. Work ACK/handoff success remains
silent and never substitutes for a producer completion notice.

On October 19, pre-report quote/account refreshes superseded the scheduled
overlays in the verified public strategy, but their `pre-report-kr-overlay`
producer label was excluded from the local notification bridge. Only the morning
full research notice was sent. The bridge now recognizes the exact
`pre-report-{kr,us}-overlay` labels with `run_mode=overlay_only`, both when queuing
and in the trusted sender. Successful canonical coverage, exact published
producer identity and finish time, the publication lane lock, live byte
verification, retry limits and Telegram deduplication still apply. The message
describes quote/account refresh completion, never new full research. Older
superseded refreshes are not replayed, and Work ACK/handoff remains silent.

YouTube and PRISM still collect through GitHub, but their `deploy` jobs are
intentionally skipped with the local backend. Their successful build alone does
not prove delivery. The local publisher now queues a separate advisory completion
only for a canonical successful run completed within 24 hours, after matching one
trusted main-branch GitHub run and exact attempt. The successful collection step
must contain the canonical start/finish times, and the Pages snapshot step must
also succeed. Gate-only runs, YouTube `publish=false`, failures, native cloud
deployments and superseded cloud deployments cannot create these local notices.

Before sending, the existing trusted Telegram workflow rechecks that attempt and
the immutable manifest hash. Under the publication lane lock it checks the
published input packet's source run, completion time and recomputed source hash,
then compares its bytes with the actual live Pages packet in addition to the
existing site verification. The notice describes external material processing and
publication; it does not claim a new investment analysis or Work report. Work ACK
and handoff remain silent. Rebuilding a packet or retrying a tick cannot create a
second completion event for the same immutable advisory run.

On October 16, backup YouTube schedules recollected after successful local-backend
runs because the shared gate required `youtube_coverage`, which depends on the
deliberately skipped cloud deployment. Both schedule and runner-acquisition gates
now receive the repository backend setting. With local ownership, a successful
default-universe run covers collection only when its actual verification, merged
site rebuild and snapshot-stamp steps all succeeded. Gate-only no-ops, custom
sources, `publish=false` and failed runs do not establish this coverage. Cloud
ownership still requires the existing end-to-end coverage marker. This prevents
another collection; it does not prove live publication or notification, which
must still be verified independently through the local publisher and receipts.

The same check found PRISM's successful `08:07:41.117583` completion excluded by
GitHub's `08:07:41` step boundary, leaving its completion notice unqueued. Recovery
and notification admission now share one precision-aware containment check: a
whole-second GitHub end contains observations before the next second; fractional
GitHub ends retain their exact bound. Manifest timestamps, hashes and execution
validity are unchanged. Wrong attempts, reversed intervals, the next second,
ambiguous producers and missing canonical evidence still fail closed. Resume the
existing publication/notification lane after deployment; do not recollect PRISM
or repeat its Work acknowledgement to recover this notice.

On October 17, the independent run-due reconciler saw a newly rebuilt YouTube
packet while the previous publication receipt was still `DELIVERY_VERIFIED`.
It queued a notice before the publisher recorded `PAGES_PENDING`, and the sender
correctly refused the unverified delivery. Advisory admission now shares the
publisher lock across receipt, packet and producer checks. A busy publisher
defers only new advisory admission; existing failures and queued notices still
reconcile. The publisher passes its existing lock ownership without reentering
the non-reentrant lock. Actual live verification, immutable identities and the
three-attempt/15-minute retry contract remain required. Resume a failed notice
through the existing reconciler after its cooldown; do not reset its receipt,
recollect the source or repeat the Work ACK.

The outbox retains the existing three-attempt budget, 15-minute dispatch cooldown,
active-workflow ownership check and atomic Telegram delivery ledger. A broken
collector or GitHub read cannot block unrelated queued failures or the other
collector. For a missed advisory notice, inspect `notifications/events`, the exact
GitHub attempt, live `work/v1/<surface>/latest.json`, and finally the matching
`notifications/results` receipt. `DISPATCH_ACCEPTED` is not `SENT`. Native failure
notifications continue through the original workflow; do not replay them through
the advisory completion lane or dispatch the producer again merely to send a notice.

On October 18, PRISM successfully collected five messages with zero ticker-level
signals. The producer's informational `telegram_no_ticker_level_signals_found`
warning was incorrectly rejected by both recovery and notification admission.
Those lanes now share a completion check that accepts only that exact single
warning, positive message count and zero signal count. Unknown, mixed or
inconsistent warnings still require diagnosis. Collection status, immutable source
hash, exact producer attempt, publication lock and live packet checks remain
required. Resume the existing notification lane after deploying this repair;
do not recollect messages or repeat Work ACK to deliver a zero-signal notice.

Completion text distinguishes full investment research from an overlay's quote
and account refresh. A verified strategy data publication does not establish a
new Work briefing or a newly completed full analysis; overlay notices explicitly
say that they reuse existing research.

On October 20, a Pages build took 101 seconds, beyond the publisher's bounded
90-second propagation wait. New completed overlays then replaced the pending
generation before its delivery receipt was finalized. The publisher now resumes
the exact committed snapshot and its report/strategy contents before rebuilding
for newer inputs. A partial local build cannot qualify for that resume, and live
byte verification remains mandatory. Market notification admission shares the
publication lock, as advisory admission already does. Pending publication defers
success dispatches without spending attempts; independent failures still dispatch.
An already queued overlay superseded by a canonically completed, newer overlay
in the verified live strategy returns `NOOP/SUPERSEDED_BY_VERIFIED_PUBLICATION`.
This is a policy skip, never `SENT`. Missing, failed, incomplete, future or unbound
successors cannot establish it; full research and existing delivery receipts are
preserved. Resume only the existing bounded notification lane after deployment.

The installed PowerShell launcher also records failures before Python is invoked,
including a missing analysis runtime or failed source fetch/snapshot preparation.
It writes the same credential-free, hash-bound outbox with stage `launcher`,
preserving the first observation for each error category and KST day. It reserves
one bootstrap dispatch under the Python reconciler's shared byte-range lock. The
normal reconciler owns the remaining cumulative retry budget after recovery; the
launcher never repeats that bootstrap attempt or duplicates Python-owned failures.
The trusted notification workflow probes the analysis interpreter with an isolated,
stdlib-only process before loading credentials. If it is absent, cannot launch,
fails the probe, or exceeds ten seconds, the workflow sets up its own pinned Python,
so reporting that failure does not require fixing the analysis runtime first.

This does not detect a powered-off PC, a task that never launches, or failure to
load the installed launcher/helper itself. If durable storage is unavailable or
GitHub rejects the bootstrap while Python remains unavailable, delivery remains
blocked and needs the independent operator. Preserve the failed/unknown dispatch
receipt; do not label it sent or reset its budget. Installing this repair requires
updating both launcher scripts; fetching a source snapshot alone does not update
the installed PowerShell entrypoint. Do not reinstall schedules or interrupt an
active worker to update the files. The existing installer accepts
`-UpdateScriptsOnly` to atomically replace the helper and entrypoint without
changing tasks, enabled markers, or active workers.

`notifications/dispatches` records bounded attempts (three, fifteen-minute cooldown)
and active workflow ownership. `DISPATCH_ACCEPTED` is pending. Only a corresponding
`notifications/results` Telegram `SENT`/deduplicated `NOOP` receipt establishes
delivery. The existing atomic Telegram ledger preserves partial cursors and failure
incident cooldown. A successful workflow missing its local receipt requires
diagnosis rather than blind retransmission. Failed notification transport does not
terminate healthy research. A PC/network outage still requires the independent
observer; it cannot send from an offline host.

The October 19 US evening refreshes exposed a publication-confirmation gap:
Pages deployed successfully, but the immediate post-push check still saw the
previous snapshot. The next publication tick rebuilt another completed overlay
before verifying that delivery, leaving Work handoffs and completion notices
pending through successive successful deployments. The publisher now checks the
same immutable site up to seven times, fifteen seconds apart (at most ninety
seconds of propagation waits), under its existing publication lock. Each check
still requires the exact live snapshot, report and strategy bytes. It pushes and
mirrors only once, then completes exact handoffs and notification reconciliation
only after verification. Exhaustion retains `PAGES_PENDING`; verification errors
retain the existing failure path and cumulative notification retry limits. Never
repeat research or a Work ACK to repair this stage. The observed Pages deployment
took about sixty-five seconds; a sixty-second window would still miss it.

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

The local US overlay lane delays the early 22:40 cloud slot until the first
configured New York execution checkpoint (currently 10:00: 23:00 KST in daylight
saving time, 00:00 KST in standard time). The former cloud start targeted a later
deployment; a fast local run could finish before any checkpoint and incorrectly
suppress a refresh before the 23:10 Work briefing. Before the checkpoint, local
ticks report `AWAITING_EXECUTION_CHECKPOINT` without launching work or spending
an attempt. A successful earlier snapshot does not cover the aligned window.
The original slot identity and cumulative retry budget stay intact; only a
successful pre-checkpoint attempt bypasses cooldown for its first real refresh.
Failed attempts keep their cooldown and limits. Market calendar holds remain
unchanged. During standard time the 23:10 Work slot is before the US open;
retain its pre-open limitations rather than
inventing live execution readiness. Research completion and publication never
override stale quotes or execution gates.

The local KR lane refreshes at 10:30, 13:30 and 14:30 KST, ten minutes before
the corresponding Work briefings. The legacy cloud slots (10:05, 12:00, 13:20)
could finish quickly enough that their thirty-minute observations expired before
Work prepared a report; the last slot also left 14:40 without a fresh cohort.
Only local due-target clocks change. The official market calendar, configured
execution checkpoints, frozen research universe, per-slot attempt budgets and
source validity remain enforced. An earlier successful snapshot does not cover
the later pre-briefing window. Historical receipts retain their original slots.
Long collection or rendering can still exhaust validity; keep live recheck
requirements when that happens rather than extending timestamps.

The later local US refreshes run at 01:00 and 03:00 KST before Work at 01:10
and 03:10. The former 00:40/02:10 clocks could leave thirty-minute quotes
expired while the US market was still open: the October 15 03:12 report used
02:10–02:15 KST observations. The cloud clocks remain unchanged, as do the
first US slot's New York checkpoint alignment, session/calendar checks,
per-slot retry limits and immutable observations. A successful earlier refresh
does not cover a later Work-aligned slot. KR and US Work prompts also require
the actual intended briefing time and a completed producer before prepare,
so an early app wakeup cannot freeze the previous cohort. Long-running
producers retain ownership and all stale-execution gates remain enforced.

## Recovery decisions

### A normalized decision fails price-range validation at final signal extraction

The October 15 KR run `20261015T055359_local-scheduler-kr-full` rejected
`010140.KS` at final signal extraction: normalized bounds `[19, 19160]`
contradicted the literal `19,160~19,570원` range. Its error artifact did not retain
the original LLM response, so do not infer its original bound types. A regression
reproduces this validation escape with string or partially populated bounds:
raw validation skips them, normalization creates numeric bounds, and a subsequent
parse rejects them. Validate the normalized representation inside the original
parser as well, so the existing bounded decision repair handles that failure.
Keep the literal-price guard and retry limit; never repair the stored prices by
guessing or relax the execution gate.

Leave healthy ticker workers running. After the producer finishes, inspect its
immutable manifest and recover only failed tickers with a compatible source,
reusing successful research. A code fix or a partially completed run alone does
not establish full coverage, publication, or delivery.

The local scheduler now passes its newest terminal partial cohort from the same
market/production window to `--resume-from-run`. The existing runner validates
exact research settings, loaded account, selected coverage and successful
artifacts before reuse. An incompatible source fails closed within the existing
cumulative attempt budget; it does not silently become another full analysis.

### Failed holding analysis makes an intact selection appear incomplete

The October 15 partial KR source completed 29/30 ticker analyses. Fresh portfolio
reconciliation also marked selection incomplete because the failed ticker was a
holding, although all thirty rows were selected and retained. This blocked the
07:58 failed-only retry before research started. Preserve that failed attempt and
its cooldown; it still counts toward the market/session budget.

Recovery may derive a selection view only when a verified fresh account receipt
shows that every reported holding gap is a failed/skipped row, and the original
`universe_selection.json` proves complete selection with exactly matching mode,
required holdings/watchlist, ordered selected tickers and count. Bind its hash
alongside the terminal manifest, and recheck both before copying successful
artifacts. Missing proof, real selection gaps, changed holdings or settings,
unverified accounts and modified artifacts still fail closed. Do not edit the
partial source or mark its analysis complete. The new cohort must retry the
failed ticker and recompute complete coverage before publication.

### Local storage exhaustion after completed ticker research

On October 14, all thirty KR ticker workers completed, but postprocessing failed
with `ENOSPC` before a final manifest was published. A subsequent auth-file copy
also failed with `ENOSPC` and was reported as `CodexAppServerAuthError`; this did
not establish an expired login. Isolated per-ticker plugin caches had accumulated
about 14 GB in the local scratch workspace. Auth seeding now replaces a complete
temporary file atomically and reports full storage as `CodexAppServerStorageError`.
Local production checks the same 4 GiB output reserve used by the Windows lane.

The installed launcher accepts `codex_workspace_dir` in
`.runtime/local-automation/runtime-settings.json`, using the existing
`TRADINGAGENTS_CODEX_WORKSPACE_DIR` override. This changes future scratch output;
it does not move canonical archives or existing workspaces. Keep the scratch root
private to the Windows user. Do not delete or move a workspace after an approval
rejection. NTFS compression can preserve inactive files while recovering space.

For a terminal failed full attempt with every ticker successfully archived, use
`--finalize-from-run` with `--finalization-source-config` pointing to its original
immutable Git configuration. The loader verifies that config against Git, checks
the frozen universe/current holdings, exact models, all research artifacts and
hashes, and runs no ticker graph. It writes a new cohort with explicit research
reuse provenance and original research/quote timestamps. The interrupted source,
its failed attempt and missing/corrupt final outputs remain intact. Hold the
existing `run-due.lock` throughout operator finalization to exclude a scheduled
full rerun. Verify the new manifest, publication, report handoff and Telegram
receipt independently; recovered postprocessing is not newly generated research.

### KIS calendar and account token coordination

On October 15, KR production stopped before ticker research with
`ADAPTIVE_ACCOUNT_UNAVAILABLE` after the account token endpoint returned HTTP 403.
The official calendar had just issued an independent token, while the account
client's stored token had entered its twenty-minute refresh window. The original
403 response body was not retained. A read-only account probe at 05:00 recovered
all thirteen holdings. The same calendar-then-account ordering reproduces a second
token request and HTTP 403 under the broker's documented
[one-token-issue-per-minute limit](https://github.com/koreainvestment/open-trading-api#5-%EB%AC%B8%EC%A0%9C-%ED%95%B4%EA%B2%B0-%EA%B0%80%EC%9D%B4%EB%93%9C).

The calendar now obtains its token through the existing real KIS client's shared
refresh lock and atomic private cache. Its official holiday GET and same-day
calendar cache remain separate from token storage; no token enters a calendar
receipt. A failed refresh, lock or token-cache write keeps the session gate
closed. Do not force token issuance, bypass mandatory holdings coverage, reset
the original attempt count or shorten its cooldown. Verify a current read-only
account snapshot, then let the existing scheduler resume within its remaining
budget. Before that worker starts, classify production recovery separately from
the merged preventive repair; a successful account probe is not a completed
daily analysis.

### Windows readers temporarily blocking archive replacement

The October 16 01:00 US overlay archived a successful 30/30 manifest, then failed
while replacing `latest-run.json` with Windows error 5. A reader holding the file
without delete sharing reproduces this exact failure. The immutable run remained
valid and the publication archive fallback delivered the current Work report;
the failed attempt and its failure notification remain historical evidence.

The shared atomic JSON writer now retries only the replacement operation for
native Windows errors 5, 32 and 33: seven attempts with at most 2.55 seconds of
backoff. It reuses the same complete, flushed temporary file under the caller's
existing lock. Other write failures and persistent denials still fail closed;
it never deletes the destination, changes ACLs, rewrites observations, or reruns
research. A completed immutable manifest can advance a lagging discovery pointer
through the existing idempotent publication function, which refuses to replace
a newer run or an unverifiable/corrupt pointer. Do not change the failed attempt
to success or replay its notification. Verify exact Work/Pages/mobile lineage
and the existing success notification independently.

### Korean session VWAP source consistency

The October 14 pre-open audit reproduced an invalid KR VWAP: a domestic quote
had zero cumulative volume/value, so the old fallback summed minute bars'
`acml_tr_pbmn` (cumulative traded value) and divided by `cntg_vol` (interval
volume). These field meanings are documented in the
[official KIS example](https://github.com/koreainvestment/open-trading-api/blob/main/examples_llm/domestic_stock/inquire_time_itemchartprice/chk_inquire_time_itemchartprice.py).
The resulting price was far outside the observed trading range.

KR session VWAP now requires paired cumulative totals and a valid daily range
from the same domestic price response. Missing totals or an inconsistent value
produce `session_vwap=null`, an explicit missing reason and analysis-only data
quality. A rolling minute window, including previous-day bars, cannot replace
session VWAP. Neither publication nor this change refreshes the quote timestamp.
Historical artifacts stay intact; inspect whether the original research excluded
the bad observation before deciding on recovery. A healthy immutable producer is
not restarted to apply a data-collection fix; later scheduled quote refreshes use
the new source snapshot and still require their normal session and risk checks.

### Korean daily history provider gaps

The local scheduler enables `TRADINGAGENTS_KIS_RESEARCH_FALLBACK_ENABLED=1`
(an explicit `0` disables it). When Yahoo's requested KR daily bar is missing
or invalid, the existing read-only KIS daily chart client supplies a complete
independent series. Stock-data tools, indicator history and stale trade-date
preflight use the same fallback. The exact completed session must have a real
valid bar; a calendar date alone cannot release the freshness guard.

KIS history uses KRX adjusted prices (`FID_ORG_ADJ_PRC=0`), as documented in the
[official KIS example](https://github.com/koreainvestment/open-trading-api/blob/main/examples_llm/domestic_stock/inquire_daily_itemchartprice/inquire_daily_itemchartprice.py).
Requests paginate backwards at most twenty times, validate every requested
OHLCV row, and exclude future rows. The tool includes source, observation time
and requested end date. Its five-minute process cache is separate from Yahoo's
disk cache; the series are never spliced. Missing credentials or broker data
cannot fabricate a completed bar. Retry and market-session budgets are unchanged.

On October 13, Yahoo returned null OHLC for October 12 across the KR cohort;
Alpha Vantage's fallback hit its subscription/rate limit. The four KR production
attempts were exhausted. Broker reads independently verified the missing October
12 history, while a bounded read-only check verified October 13 Yahoo bars for
all thirty requested tickers. The closed October 13 session remains missed;
provider recovery and a reference report do not count as new completed analysis.

### Require an outcome, not another observation

The heartbeat is an operator, not an audit-only task. For each open incident,
finish the run with one of these outcomes and concrete evidence:

- `REPAIRED`: the original symptom is absent and the intended result is verified.
- `IN_PROGRESS`: an actual run/worker is progressing; record its ID, last progress,
  remaining verification and next check. An accepted dispatch alone is not progress.
- `BLOCKED_EXTERNAL`: name the exact external control, evidence, responsible
  party, supported unblock action and the observation that will permit recovery.
- `HEALTHY`: the relevant production and delivery obligations are satisfied.

Use these as incident outcomes, not as the Codex Goal API's status. Unchanged
timestamps, repeated API reads and new snapshots are not repair progress. Two
consecutive checks without progress require a different diagnostic or a concrete
external handoff in that run; do not merely roll `next_check_at` forward. This
does not reset retry limits or require changes without evidence. Continue
independent authorized repairs while one action is blocked. After a documented
external handoff, check only its clearance signal until it changes; do not repeat
the full archive/report audit hourly. Recheck affected delivery obligations when
their deadlines change or when the blocker clears.

For a newly blocked or materially worsened incident, report impact, exact action
already attempted, blocker and next owner/action. Preserve the outstanding action
even if duplicate alerts are suppressed; never equate `DONT_NOTIFY` with resolved
or "no action needed". Notify on repair, new impact or newly required user action.

### Repository invocation block: inspect the actual control

`actions/permissions.enabled=true`, active workflow definitions and online runners
do not prove that GitHub permits repository execution. When annotations say
`repository invocation blocked` or dispatch returns `Actions has been disabled
for this repository`, inspect the repository's Actions page with an authorized
signed-in browser, in addition to the API. A signed-out page can expose the
reason but omit the maintainer's repair control. If the browser is unavailable,
try the supported available browser surface; do not label this a support-only
incident without inspecting the accessible control.

On 2026-10-10, the signed-in page explicitly said GitHub had disabled workflows
on this fork because of Actions usage, and offered a maintainer re-enable button.
The normal repository permissions API still returned enabled. The authorized
operator used that official control and observed `Actions Enabled.`; no token,
repository permission or environment protection was changed. This is a supported
restoration path when the displayed reason and user authorization permit it,
not permission to bypass an account/security restriction or accept new terms.
Escalate those cases with the exact screen and required action.

After clearance, check active ownership and launch one bounded existing watchdog
run. Verify its jobs, then recover only still-required production/delivery stages
using current-session and exact-report evidence. Do not replay every missed
schedule, re-ACK a report, or call yesterday's research today's analysis. A missed
session can remain `MISSED` even after infrastructure and reference delivery are
restored. Record those outcomes separately.

Usage-related disablement also requires reviewing native probes, local dispatches,
watchdog retries and downstream fan-out. Attribute counts before changing cadence;
the banner establishes the usage-related disablement but does not identify a
specific threshold or offending workflow. Reduce proven redundant work while
preserving market deadlines and failure notifications. Do not repeatedly re-enable
and flood the same workflows as a substitute for that review.

### Keep approval failures scoped to the rejected action

A Codex automatic approval rejection and a GitHub execution restriction are
different incidents. Capture the rejected action and actual reason; if the only
reason is `blocked by policy`, say so rather than inventing a cause. Do not retry
the same prohibited effect through another tool or disable approval protections.
Continue unrelated permitted diagnostics and repairs. If durable receipt writing
is blocked, report the last persisted time and include the new evidence in the
chat; do not claim it was saved or let stale state override current evidence.
Request only the specific missing approval if it is necessary to proceed.

The current topology has an independent Codex observer, but its recovery dispatch
still depends on GitHub Actions. Moving the same dispatch to a local timer does
not remove that dependency. A future availability redesign should separate the
calendar/lease-driven producer from GitHub transport, reuse the same validated
entrypoints, and maintain one writer with immutable execution/delivery receipts.
Keep repository CI and deployment on their existing paths until an independently
authorized and tested replacement exists. Such a redesign is not activated by
this runbook and must never serve as a workaround for an explicit policy denial.

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
Daily/Overlay/YouTube/PRISM producers can miss their `workflow_run` notification and
mirror: GitHub suppresses events caused by `GITHUB_TOKEN`, while explicit
`workflow_dispatch` is exempt ([GitHub event rules](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow)).

After a three-minute completion grace, the reconciler uses paginated run history
and exact upstream ID/attempt markers to dispatch only missing followups. It
preserves active ownership, rechecks immediately before dispatch, waits fifteen
minutes before retries, and counts all followup runs and reruns toward a three-attempt
budget per upstream. Gate-only producers are ignored; mirrors require successful
deployment. The existing notifier still verifies the upstream and deduplicates
Telegram sends. The existing mirror still verifies public content hashes.

PRISM has a daily 07:35 KST collection schedule, including weekends and market
holidays. The watchdog recovers missing runs from 07:50 until 17:00 KST, yielding
to active KR/US analysis, overlays, and YouTube publication. The recovery extends
the six-hour lookback by the actual scheduling delay so the original collection
interval remains included, keeps the 80-message cap, and leaves the configured
authentication mode unchanged. Existing active-run ownership and per-cause retry
limits apply. Successful collection and deployment, not yesterday's Work ACK or
an empty current event window, establish completion. PRISM recovery provenance
also enables the bounded downstream notification/mirror reconciler.
If the collection/build succeeded but deployment failed, the watchdog preserves
that source and leaves delivery to Pages recovery and the operator; it does not
start another collection to repair deployment.

The rollout starts with producer runs created at or after 2026-10-07 15:59 UTC;
earlier incidents were manually delivered before the provenance markers existed.
Recovery looks back 24 hours. Older or budget-exhausted incidents require this
operator's evidence-based repair, not another unbounded retry. A successful
followup workflow is only coverage for dispatch deduplication: operations must
still verify `SENT`/policy `SKIPPED` and actual mirror/Pages contents.

Public AI mirrors use a unique cache key on every Pages read, including both
manifest reads. A stable manifest with a stale child file is retried as a whole
snapshot, at most three attempts with two- and five-second backoffs. Hash, byte
count, generation, allowlist and non-rollback checks remain mandatory. A green
`already at this or a newer snapshot` log still needs the current branch manifest
and live Pages manifest compared; its log includes both generation timestamps.
On October 8, a stable-URL read first failed integrity, then a later successful
workflow left the mirror at the prior generation. Bounded workflow retries
restored it; cache-bypassing reads prevent reuse of that cached response. Exact
CDN propagation behavior was not established by the logs.

Transient download HTTP 429/500/502/503/504, connection errors and timeouts share
that same three-attempt whole-snapshot budget. Partial downloads are discarded;
permanent HTTP failures propagate immediately. A 503 during the October 9 US
Work handoff exposed that transport errors previously bypassed this retry loop.

For Daily analysis, an unidentified native scheduled run that is still queued
with no jobs and was created before the target production window does not cover
that new window. An October 8 check reproduced an earlier US-era queue blocking
KR recovery this way. The old run is left intact. Any run with jobs, an explicit
matching profile, a current/missing creation time, or a manual trigger retains
the conservative active-ownership guard. A queued coverage result never proves
analysis completion; verify the local manifest and heartbeat separately.

An overlay gate that skipped before its research dependency completed does not
cover a later check with that completed baseline. The watchdog compares the
successful gate's completion time with the successful dependency job times and
reconsiders the overlay only when that ordering is proven. Unknown timestamps,
active owners and normal no-work results stay protected. An obsolete skip neither
consumes nor clears the existing failure budget. October 8's 23:10 overlay was
held until the US analysis completed at 23:12, but previously suppressed recovery
for the rest of the 22:40 checkpoint window.

For Work publication, read and apply
[the repository Work skill](../.agents/skills/tradingagents-daily-investment-work/SKILL.md).
Keep its canonical local runtime directory even when code repairs use a worktree.
Use `prepare -> compose Markdown + structured JSON -> publish -> ACK -> handoff`.
Respect `NOOP`, `RESUME`, busy and regression results. Do not manually clear or
overwrite pending state. An existing pending event can belong to an active
scheduled writer; check before resuming it. Preserve thesis, required rows,
receipt binding and execution gates. Do not re-ACK to repair a deployment.

The local portfolio overlay can reference an exact repeated thesis condition by
`thesis_ref`, a JSON Pointer into the same ticker's complete strategy-table thesis.
Resolve these references when composing the report; retain unique portfolio
conditions as well. This lossless representation keeps the packet's existing
600,000-character limit and all rows, research, sizing and execution gates. It
repairs the October 8 US packet overflow caused by repeated long research plans.

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

## Local recovery of advisory schedules

The local `run-due` lane recovers only the existing YouTube and PRISM Actions
collectors when no core worker is due on that tick. Core research and overlays
always run first, without an advisory API dependency. A tick that starts core
work returns after that worker; recovery reevaluates on the next tick using the
current calendar. The existing `run-due.lock` protects this local admission,
including a worker already running an older immutable revision. Advisory runs
keep their native independent workspaces and archives and do not hold that lock
for their remote lifetime: a three-hour YouTube run must not delay the 10:05 KR
overlay or the 10:40 Work publication. Native collector schedules are unchanged.

Recovery reuses watchdog windows, inputs, active blockers and consecutive-failure
budgets, dispatches at most one advisory per tick on `main`, and marks it
`local_watchdog`. It additionally checks live advisory ownership without a
creation-date filter, so an active rerun of an old run is still protected.
PRISM retains the watchdog's delayed six-hour lookback and 80-message cap.
The local path does not enable any disabled core workflow.

Under the local state directory, `advisory-recovery/admission.json` is written
before dispatch, together with `advisory-recovery/attempts/<session-hash>.json`.
The latter enforces at least 60 minutes between attempts and at most two local
dispatches per target/session; the existing native plus watchdog failure budget
can stop recovery sooner. An accepted request is not delivery. A timeout, lost
response or not-yet-visible run leaves the admission unresolved across ticks and
sessions. No timer alone authorizes a second dispatch: one matching, terminal
run must first resolve it. Ambiguous, corrupt or truncated evidence fails closed.
For `ADVISORY_DISPATCH_UNRESOLVED`, the operator must inspect the saved workflow,
request time and prior run IDs, identify the exact new run or prove rejection,
and preserve that evidence before a targeted repair; do not clear receipts to
reset the budget.

Coverage requires the real successful collection step, a uniquely matching
canonical completed manifest inside that step's time interval, and the successful
publication stamp/build. A local skipped cloud deploy is expected; a green
runtime gate without collection is not coverage and does not reset failure
history. A completed collection with missing canonical evidence or an incomplete
publication is diagnosed without launching that research again. These checks
are separate from live Pages and Telegram verification. Only matching canonical
run-name timestamps are read, so unrelated damaged archives stay untouched.
If an old GitHub run is retried successfully today, its original creation date
can put it outside history queries. Current-window canonical completion with
default source coverage then produces `CANONICAL_COMPLETE_PRODUCER_UNRESOLVED`
and prevents recollection until the exact producer attempt is verified.

Advisory diagnostics never become core-analysis failures. Fixed reason codes
distinguish authentication/API availability, truncated history, invalid receipts,
missing/incomplete canonical production and completed collection awaiting
publication repair. Per-target source/receipt errors do not starve the other
collector; unresolved admission and unknown active ownership remain shared
barriers. Continue the normal publication/notification lane and verify actual
manifest, Pages, Work handoff and `SENT` or policy `SKIPPED` independently.

The October 14 incident showed missing YouTube native probes and the 07:35 PRISM
run while other Actions executed successfully. The confirmed repair is closing
the local-backend watchdog coverage gap; the internal cause of GitHub not
creating those native runs was not established.

## Notification contention with native publication

The native publisher holds `publish.lock` through building, pushing and live
Pages propagation verification. Market and advisory notification consumers wait
up to five minutes for that lane, within the notification job's ten-minute
limit. Once acquired, they read the publication receipt and exact source/packet
again and verify the actual live bytes while still locked. A pending receipt,
superseded source, live mismatch or exhausted lock wait never permits a send.
Advisory queue admission remains nonblocking; the owning publisher can admit it
after verification. Dispatch acceptance remains distinct from `SENT`.

On October 20, notification run `39355639293` exhausted its previous 30-second
wait at 10:51:16 KST; the publisher verified delivery at 10:51:18 KST. The
`PermissionError` nested inside that lock timeout described contention, not
missing user permissions. Do not reset receipts or reanalyse successful
research for this failure. Check active ownership, exact current source and
the cumulative retry budget before a targeted notification retry.

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
