# Opportunity Capture Sleeve

The opportunity capture sleeve is a read-only sizing diagnostic for strong stock-level opportunities that may be too risky for a full position.

It does not place live orders. TradingAgents remains read-only and only writes portfolio reports plus proposed order artifacts.

## Profile Fields

Values are percent units:

```toml
opportunity_capture_enabled = true
opportunity_capture_sleeve_nav_pct = 7.5
opportunity_capture_per_pilot_nav_pct = 1.0
opportunity_capture_max_loss_nav_pct = 0.3
max_pilot_stop_distance_pct = 12.0
soft_prism_conflict_allows_pilot = true
```

## Budget Function

`tradingagents.portfolio.opportunity_sleeve.compute_opportunity_pilot_budget()` returns:

```text
pilot_budget_krw
max_loss_krw
sleeve_total_krw
sizing_blocked
block_reasons
budget_reason
```

Inputs:

```text
nav_krw
available_cash_krw
min_cash_buffer_krw
stop_distance_pct
profile
```

The pilot budget is capped by:

- total sleeve NAV cap
- per-pilot NAV cap
- cash available after the minimum cash buffer
- max-loss cap divided by stop distance
- minimum trade size
- max pilot stop distance

If the sleeve is disabled, the function returns disabled diagnostics without blocking Action Lift Audit visibility.

## Audit Fields

Action Lift Audit entries include:

```text
pilot_budget_krw
max_loss_krw
sleeve_total_krw
stop_distance_pct
sizing_blocked
sizing_reason
```

These fields explain why a pilot may be visible but not converted into a live-size order.
