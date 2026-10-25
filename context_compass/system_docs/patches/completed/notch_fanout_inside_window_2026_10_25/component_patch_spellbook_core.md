# component_patch_spellbook_core

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
- Spellbook Core _notch_spell.

## Before/After Behavior Summary
- Before: the guarded section ran `_check_notched_version` only. After: it also runs `after_switch()` when given; an error from either takes `_revert_refused_notch` (the index, lookup, claim, dependencies and topology restored) and propagates (a SpellbookValidationError wrapped as the refusal, as before).

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
