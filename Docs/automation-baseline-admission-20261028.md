# Scheduled overlay admission incident, October 28, 2026

The local US overlay scheduler repeatedly launched workers while no eligible
completed full-research baseline existed. The workers correctly rejected the
October 21 baseline with `OVERLAY_BASELINE_STALE`. The scheduler nevertheless
spent an attempt and emitted a worker-failure notification for each new slot.

## Evidence

- US full run `20261028T175146_local-scheduler-us-full` failed after Codex returned
  `429 Too Many Requests`. Its existing circuit breaker stopped the remaining
  ticker work; the final cohort had zero successes and 30 failures/skips.
- The existing bounded retry started
  `20261028T185153_local-scheduler-us-full`. At the investigation checkpoint,
  all 30 ticker workers had succeeded, but the full manifest was still being
  finalized. A running attempt or individual ticker artifacts cannot authorize
  an overlay or establish report delivery.
- Overlay attempts `20261028T230258_local-scheduler-us-overlay_only`,
  `20261028T232338_local-scheduler-us-overlay_only` and
  `20261028T234149_local-scheduler-us-overlay_only` failed because the newest
  eligible completed full baseline was from October 21. Existing research and
  failure receipts were retained.
- The independent minute refresh already returned `WAITING_RESEARCH_BASELINE`
  for this condition. Scheduled checkpoints lacked that admission check.

## Repair

Scheduled overlays now use the same existing full-baseline selector before
admitting a worker. The selector checks the market, completion, coverage, age
and newer exchange sessions using the scheduler's explicit clock. The check
does not write a discovery cache. Missing, incomplete, stale or unverifiable
baselines cause a dependency wait without starting a worker, spending an
attempt or emitting a worker-failure notification. Read/parse failures return
`OVERLAY_BASELINE_UNVERIFIED` with only an error type.

The original slot key, accumulated attempts and cooldown still take priority.
Newly completed research can make an eligible slot due on the next tick. The
observed manifest is never pinned or passed to the worker: the execution path
still independently verifies its current universe, holdings and artifacts.
Full research, model selection, risk gates and trading permissions are unchanged.

## Verification and remaining production acceptance

Offline fixtures cover ready/empty archives, stale and future dates, missing or
invalid dates, too many newer sessions, wrong markets, incomplete/running/failed
cohorts, malformed manifests, KR admission, preservation of prior attempts and
resumption after successful research. Existing scheduler, checkpoint, clock,
cross-market, minute-refresh and advisory-recovery regressions are also run.

Adoption of this repair establishes correct admission, not successful new
research or publication. Verify the owned full run's terminal coverage and
subsequent overlay and exact report delivery separately. Do not reset retry
history, terminate that producer or manufacture a fresh report from old prices.
