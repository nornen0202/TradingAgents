# Fresh inputs before KR/US investment reports

The report consumer previously read the newest completed archive without acquiring new market/account data. Its independent producer slots matched local Work but not the web schedules: the 13:00 KR task could read the 10:34 overlay while the next refresh was at 13:30. A US report starting at 23:30 could finish after a 23:00 observation's 30-minute expiry. A new mirror commit only republishes those observations; it does not renew them.

## Local scheduled reports

Use `python -m tradingagents.work prepare --surface kr --refresh-market` (or `us`), with the canonical archive and producer-state paths from the daily Work skill. The ordinary archive-only API remains available for diagnostics and non-market consumers.

The refresh checks exchange and official market calendars, acquires the same producer lock as the local automation lane, reuses completed research through `overlay_only`, and queries broker quotes and the account again. It never submits orders or reruns company research. Research/judge and report synthesis model settings remain Sol / xhigh.

Before preparing an event it requires the selected producer to be the new run, genuine non-future quote/account clocks from this invocation and less than ten minutes old, VALID account health, complete holdings/watchlist coverage, and resolved research less than 36 hours old. Minute-resolution quote clocks are allowed within the invocation's first minute. An expired cache, missing account, partial universe, failed overlay, unknown calendar, competing producer, or session ending during refresh cannot create or acknowledge a report event.

The fresh-report requirement is persisted in pending Work state. At publish, actual quote/account ages must remain below 30 minutes and every row must remain valid even when the draft has downgraded execution readiness. A failed publish leaves the event pending and the canonical published report unchanged. The writer must refresh/prepare again and rebind the draft, rather than extend timestamps or acknowledge the failed report.

## Web Scheduled tasks

Web tasks cannot refresh this computer's broker account. The local producer therefore adds KR 12:50/13:10 and US 23:20/23:40/00:00 KST overlays for the 13:00/23:30 web schedules. The independent publication lane still must finish. Existing session, DST, retry budget, and original research lineage guards remain in force. Overlay collection is deterministic and reuses research; these extra slots do not add full LLM research runs.

Web task instructions must fetch a newly discovered, commit-pinned mirror immediately before drafting and again before final publication. The same 10-minute start and 30-minute final input limits apply, with all row validity checks. A slot or successful mirror publication alone is never freshness proof. If fresh inputs cannot be obtained within a bounded wait, withhold current personalized quantities/weights. Return MARKET_CLOSED outside the regular session. In standard time the fixed 23:30 KST web slot is at the US open and can correctly be held until fresh inputs actually exist; never fake the session clock.

## Verification evidence

Unit tests exercise successful refresh/prepare and publish, invalid/cached/future data, expired publish, incomplete coverage, broker errors, producer contention, calendar veto, session end, preserved Sol/xhigh configuration, and web preparation/recheck slots across midnight. Actual after-hours runs can establish correct MARKET_CLOSED handling only. A live scheduled market-session report is required to establish real broker freshness, final report clocks, and publish/ACK/handoff success. Saved model settings alone do not prove a cloud run's actual model or token usage.
