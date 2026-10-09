# Actions-independent analysis and report publication

## Verified incident

On October 9–10, 2026 KST, workflow dispatch returned HTTP 422 with
`Actions has been disabled for this repository`, although the repository
permissions API reported `enabled: true` and both registered runners were online.
The existing Windows overlay tasks only requested GitHub workflows: they did
not execute analysis when GitHub rejected dispatch. A hosted gate, deployment,
or recovery workflow cannot repair a repository-wide invocation block.

A concurrent operational recovery re-enabled Actions in the signed-in GitHub
UI. US full run [37977141414](https://github.com/nornen0202/TradingAgents/actions/runs/37977141414)
then entered `analyze_us`. Preserve that admitted producer; do not launch a
duplicate local analysis or terminate it to migrate. The precise GitHub usage
threshold and the individual workflows' contribution to the restriction have
not been established. The permissions API alone is not an invocation probe.
GitHub documents a separate [GitHub-controlled disabled state](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository).

## Independent production and durable publication

`tradingagents.local_automation` has two Windows scheduled tasks, both checked
every five minutes and at logon, with separate OS locks:

- `run-due`: reuses the existing exchange-calendar windows, including Friday's
  US session after Korean midnight; checks complete same-market research in
  the local archive, and runs the configured full/overlay CLI directly.
  Required ticker coverage, exact model preflight, strict errors, existing
  per-ticker budgets, and bounded session retry counts remain enforced.
- `publish`: watches completed manifests and canonical Work reports independently
  of producer success. Rebuilds the existing public site, verifies exact Work
  hashes and mobile lineage, guards against rollback at both the live site and
  publishing branch, and pushes generated public output to `fork/gh-pages`
  without force. The public AI mirror uses the same validated local public
  files and does not wait for the Pages CDN or an Actions event.

Successful research suppresses duplicate analysis even if publication failed.
Publication retains a durable pending receipt and retries delivery separately.
A Git push or accepted handoff is not a delivery receipt: the publisher checks
the live snapshot marker plus exact strategy and KR/US Work-report bytes before
recording `DELIVERY_VERIFIED`. Work handoff queues an exact local publication
when the local backend is installed or the specific Actions-disabled error is
returned; it does not claim that the report is externally available.

The launcher exports tracked `fork/main` into an immutable revision directory;
it does not reset the user's checkout or borrow either runner's workspace.
Credentials remain at the existing local key path and in the GitHub CLI keyring.
No private archive, account database, key file, or Telegram session is committed
to the public output branch. Source extraction is serialized between lanes.

## Installation and ownership transition

After merging the code, set repository variable
`TRADINGAGENTS_AUTOMATION_BACKEND=local`, then run:

```powershell
tools/install_local_automation.ps1
```

The current user must be signed in, with the existing `.venv`, local API keys,
Codex authentication, and GitHub CLI authorization available. These are local
Windows tasks, not ChatGPT heartbeat automations. They run when this computer
is on and the configured user session is available.

The first task ticks inspect **all** active trusted main-branch writer runs,
including queued/waiting writers. They wait for those writers to finish and
persist `actions-drained.json`; they do not cancel them. They do not wait on
stale jobless queue metadata older than the
[24-hour self-hosted queue window](https://docs.github.com/en/actions/reference/runners/self-hosted-runners).
This exemption requires a trusted main run still marked queued and a fresh jobs
response with exactly zero jobs; running work or even one queued job is preserved.
Subsequent production does not query Actions. The cloud daily/overlay gates and Work publisher yield
to the local authority variable, and other report-addon workflows retain their
collectors while their Pages deploy jobs yield to the single local publisher.
YouTube/PRISM collection itself remains a separate workflow capability.

The installer records and disables the old `IntradayOverlay-*` Windows dispatch
tasks for this repository: the local scheduler uses exchange-calendar checkpoints and
does not need repeated cloud dispatch. Disable the cloud scheduled watchdog
and daily/overlay workflow schedules after the admitted run has drained to
avoid continuing to create empty skipped runs. Keep runner registrations.

Keep `tradingagents-mobile-notifications.yml` enabled. It owns neither production
nor Pages and must still inspect admitted cloud runs and YouTube/PRISM collectors.
Its existing provenance, terminal-deployment, deduplication and silent Work-handoff
checks remain authoritative. Local ownership alone is not a reason to mute these
notifications. A missed cloud notice can be recovered with one exact upstream
run/attempt dispatch after verifying that no matching notification is active.
The local producer/publisher does not yet emit Telegram notifications; its Pages
delivery receipt must not be reported as a Telegram `SENT` receipt.

After the drain, the first publisher saves the old Pages settings in local
`previous-pages.json` and changes Pages to `legacy`, source `gh-pages:/`.
The output includes `.nojekyll`. GitHub explicitly supports
[direct branch deployment with Actions disabled](https://docs.github.com/en/pages/getting-started-with-github-pages/about-github-pages-and-jekyll).
The existing `https://nornen0202.github.io/TradingAgents` address is preserved.
Git hosting and Pages service availability are still required; this removes
Actions invocation, hosted runner acquisition, and Actions artifact storage
from the analysis/publication path, not every external dependency.

Local diagnostic files are under `.runtime/local-automation`: lane logs,
attempt receipts, `publication.json`, source revisions, and rollback settings.
`PAGES_PENDING` means publication has not yet been verified externally. A stale
input remains stale after a new publication; the existing execution/data
freshness guards continue to fail closed.

## Returning ownership to Actions

Stop and disable both `LocalAutomation-*` tasks and wait for any active local
producer/publication to finish. Remove `.runtime/local-automation/enabled.json`
and `actions-drained.json`, clear the repository backend variable, restore
Pages `build_type=workflow` using the recorded settings, and re-enable the
previously disabled daily/overlay/watchdog workflows. Confirm one successful
producer and exact public delivery before treating the transition as complete.
Never run both publishers or two same-session full producers during transition.
