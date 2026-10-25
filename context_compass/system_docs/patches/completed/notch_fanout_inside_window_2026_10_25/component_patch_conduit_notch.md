# component_patch_conduit_notch

## Metadata
- Patch ID: notch_fanout_inside_window_2026_10_25
- Status: active
- Owner: Mark
- Author: melder_0 (synaptic_python_developer)
- Created: 2026-10-25T14:01:58Z
- Updated: 2026-10-25T14:01:58Z
- Ticket: TASK-2026-10-16-order_inflight_borrower_melds_against_notch_fanout, parent
  EPIC-2026-10-25-notch_fanout_inflight_melds

## Component Purpose and Boundary
- Conduit notch_spell.

## Before/After Behavior Summary
- Before: the fan-out ran after the transaction ended, with the borrowers' gates open. After: it runs as the `after_switch` hook inside `_notch_spell`; on any exception from `_notch_spell` after the hook started, `_undo_borrower_fan_out` emits the index notch back, deactivates the incoming and reactivates the outgoing member on every peer, then the transaction ends failed and the error propagates.

## Interface Deltas
- See architecture_patch.

## State and Lifecycle Deltas
- None.

## Failure Mode Deltas
- A fan-out error undoes the notch; an undo failure raises RuntimeError naming the index (a Melder bug).

## Dependency and Ordering Constraints
- The Book reversal precedes the inverse ward emission (it reads the lender's active member).

## Validation Expectations
- The two red-first tests and the race test/probe.

## Unknowns and Open Decisions
- UNKNOWN: none.

## Context / Handoff Summary
- Design 2.
