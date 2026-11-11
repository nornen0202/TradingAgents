# Report delivery incident — 2026-11-12

## Observed status (KST)

- KR Work report published at 2026-11-11 20:53:36; US at 2026-11-12 01:15:31.
- The local publisher recorded DELIVERY_VERIFIED at 2026-11-12 04:44:51. An independent call to `verify_live` confirmed the public snapshot and checked report/strategy bytes match the generated site.
- YouTube Work report remains dated 2026-11-07 09:31:34.
- The last Actions run is 42316210571 (2026-11-07 09:06:57). Both self-hosted runners are online.
- Workflow dispatch returns HTTP 422, `Actions has been disabled for this repository.` The public Actions UI explicitly says workflows on this fork are stopped due to the scale of Actions usage and a maintainer can re-enable them. Repository permissions still return `enabled: true`; reapplying that setting and enabling the notification workflow do not remove the fork-level block.
- Notification dispatch state contains 22 DISPATCH_FAILED events. These are not Telegram delivery receipts. The advisory admission from November 8 is DISPATCH_UNRESOLVED with HTTPError and no associated run.

## Fix

Notification dispatch recognizes the explicit repository-disabled rejection, preserves the event retry budget, records a credential-free blocked reason, and stops the batch. A persistent one-hour backoff avoids repeating the same failed dispatch for every event. Health remains pending; successful dispatch removes the block. Telegram receipts and publication validation remain required.

Advisory recovery distinguishes definitive HTTP 401/403/404/422 rejection from an ambiguous timeout or server error. A rejected request cannot retain permanent producer ownership; the existing per-window attempt budget, cooldown, and active-run checks still apply. Unknown requests continue to block duplicate work.

## Operational follow-up

The fork-level Actions block requires the maintainer re-enable control in GitHub's authenticated Actions page. Chrome was signed out during diagnosis. This is separate from the repository Actions permissions API.

After re-enablement, verify a real dispatch is accepted, reconcile the historical November 8 admission only after confirming no matching run exists, and recover the current YouTube collector. Reconcile latest KR/US notification events through the existing validated notifier and check SENT/message IDs. Do not erase all retry receipts or replay the entire historical outbox. Keep disabled trading/paper lanes unchanged; run-due is already producing current analysis.

Local regression tests cover explicit rejection, retained cooldown/budget, timeout/server ambiguity, notification backoff and recovery. No broker or order settings were changed.
