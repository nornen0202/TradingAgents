"""Bounded read-only handoff from an already-running execution producer."""
from datetime import timedelta
import json
import time

from tradingagents.charting.bars import instant
from .source_diagnostics import diagnose_source


def await_completed_source(archive, state_root, market, source, *, clock, selector,
                           sleep=time.sleep, monotonic=time.monotonic):
    """Wait at most 15 seconds for a current producer, never renew old evidence."""
    if source is None:
        return source, None
    now = instant(clock())
    diagnostics = diagnose_source(source, now, include_proposals=False)
    rows, fresh = diagnostics.get('strategy_rows', 0), diagnostics.get('fresh_rows', 0)
    if not rows or fresh == rows:
        return source, None
    receipt_path = state_root / 'execution-refresh' / f'{market.lower()}.json'

    def current_producer(at):
        try:
            receipt = json.loads(receipt_path.read_text(encoding='utf-8-sig'))
            started = instant(receipt.get('started_at'))
            return (receipt.get('status') == 'STARTED' and receipt.get('real_orders_enabled') is False
                and str(receipt.get('market', '')).lower() == market.lower()
                and receipt.get('previous_source_run_id') == source.name
                and started is not None and timedelta(0) <= at - started < timedelta(seconds=120))
        except (OSError, ValueError, TypeError, AttributeError):
            return False

    if not current_producer(now):
        return source, None
    began = monotonic()
    evidence = {'prior_source_run_id': source.name, 'prior_fresh_rows': fresh,
                'prior_strategy_rows': rows, 'max_wait_seconds': 15,
                'outcome': 'NO_NEW_COMPLETED_SOURCE'}
    selected = source
    while monotonic() - began < 15:
        at = instant(clock())
        if at is None or at < now:
            raise ValueError('SOURCE_HANDOFF_CLOCK_REGRESSED')
        latest = selector(archive, market.lower(), at)
        if latest is not None and latest != source:
            selected = latest
            evidence['outcome'] = 'NEW_COMPLETED_SOURCE'
            evidence['new_source_run_id'] = latest.name
            break
        if not current_producer(at):
            break
        remaining = 15 - (monotonic() - began)
        if remaining <= 0:
            break
        sleep(min(1, remaining))
    evidence['waited_seconds'] = round(monotonic() - began, 3)
    return selected, evidence
