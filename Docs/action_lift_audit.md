# Action Lift Audit

Action Lift Audit checks whether a stock-level execution signal survived the move into the account-level portfolio report.

It separates four questions:

- Thesis: is the stock-level view constructive?
- Entry: is the stock actionable now or near a trigger?
- Size: is full-size allowed, or only a pilot?
- Account fit: did the account layer create an order or conditional plan?

## Artifacts

Each portfolio run writes the same payload to:

```text
portfolio-private/action_lift_audit.json
portfolio-private/portfolio_action_lift_audit.json
```

The payload is also embedded in `portfolio_report.json` and `decision_audit.json`.

## Entry Coverage

Audit entries are built over the union of:

- `PortfolioRecommendation.actions`
- scored `PortfolioCandidate` tickers

If a candidate is `ACTIONABLE_NOW` or `PILOT_READY` but no `PortfolioAction` exists, the audit creates a synthetic account row:

```text
account_action_now = NO_ACCOUNT_ACTION
account_action_if_triggered = WATCH
block_reasons includes CANDIDATE_ACTIONABLE_NOT_LIFTED
lift_status = ACTION_LIFT_FAILURE unless a legitimate hard block exists
```

## Order Visibility

The audit splits account visibility into:

- `proposed_now_exists`: a non-zero immediate delta exists.
- `conditional_order_exists`: a non-zero triggered delta exists, or the account action is a conditional buy plan such as `STARTER_IF_TRIGGERED`, `ADD_IF_TRIGGERED`, `STARTER_ON_PULLBACK`, or `CLOSE_CONFIRMED_STARTER_NEXT_DAY`.
- `proposed_order_exists`: either immediate or conditional visibility exists.

A valid conditional starter plan is not an action lift failure, even when there is no immediate order.

## Lift Status

Core account action enums are unchanged. The detailed labels below are audit/report statuses:

```text
ORDER_PROPOSED
BUDGET_BLOCKED
PILOT_VISIBLE_NO_ORDER
ACTION_LIFT_FAILURE
BUY_SIGNAL_RELABELED_AS_SELL_SIDE
PRISM_SOFT_BLOCK_PILOT_ALLOWED
HARD_BLOCKED
NOT_ACTIONABLE
```

## Hard Block Categories

`block_categories` keeps hard risk classes separate:

- `disclosure_hard_block`
- `market_warning_block`
- `data_quality_block`
- `account_concentration_block`
- `stop_distance_block`
- `budget_block`

Disclosure, market, data identity, account concentration, and stop-distance blocks prevent pilot visibility. Budget blocks remain visible as sizing diagnostics when the thesis is otherwise actionable.

## Scores

`opportunity_cost_score` is retained for backward compatibility as a 0-1 missed-opportunity score.

`opportunity_capture_score` is a 0-100 score derived from safe structured fields and text proxies:

- `fundamental_catalyst_score`
- `breakout_score`
- `volume_value_score`
- `sector_leadership_score`
- `liquidity_score`
- `source_confirmation_score`
- `missed_upside_risk_score`
- `valuation_risk_penalty`
- `account_concentration_penalty`
- `disclosure_risk_penalty`

The score is advisory and does not place orders.
