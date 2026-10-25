# architecture_patch

## Metadata
- Patch ID: notch_fanout_inside_window_2026_10_25
- Status: active
- Owner: Mark
- Author: melder_0 (synaptic_python_developer)
- Created: 2026-10-25T14:01:58Z
- Updated: 2026-10-25T14:01:58Z
- Ticket: TASK-2026-10-16-order_inflight_borrower_melds_against_notch_fanout, parent
  EPIC-2026-10-25-notch_fanout_inflight_melds

## Patch Scope and Non-Goals
- Objective: a borrower meld racing a lender's `notch_spell` ends in the outgoing or the incoming version (or the clean
  refusal), never a consumer built against no provider or an internal RuntimeError. Design 2 (the owner, 2026-10-25):
  the borrower fan-out (`_deactivate_borrowed_spell`, `_activate_borrowed_spell`, `ConduitWard._emit_index_notch`) runs
  inside the notch's transaction window, while the borrowers' CreationGates are quiesced, instead of after
  `end_transaction(success=True)`. A fan-out error undoes the whole notch (the owner's "1").
- Non-goals: the four failure sites themselves (design 1); in-Book notches (no race); sever/uncontract (0.2.8227).

## Changed-Components Matrix
| component | change |
| --- | --- |
| Conduit (notch_spell) | fan-out passed as an `after_switch` hook; inverse fan-out on failure; transaction ends after |
| Spellbook Core (_notch_spell) | `after_switch` hook runs after `_check_notched_version`, inside the guarded section whose error takes `_revert_refused_notch` |
| ConduitWard | `_emit_index_notch` comment: a notch now runs it inside its window |

## Interface and Boundary Deltas
- `Spellbook._notch_spell(..., after_switch: Optional[Callable[[], None]] = None)` (internal).
- `Conduit._undo_borrower_fan_out(spell_index, outgoing_id, incoming_id)` (internal).
- No public signature changes. A fan-out error now propagates with the notch undone (was: the notch stood).

## Cross-Component Invariants
- While a lender's notch fans out to its borrowers, every sealed lineage's CreationGate is parked: no borrower meld is
  in flight between the park and the reactivation.
- A notch either stands with every borrower moved, or leaves the lender index, the borrowers' contracted members and
  the contracts' selected ids as they were.
- Lock order is unchanged: `_notch_spell` holds no Book lock at the hook; the ward emission keeps ward -> contract ->
  borrower Book (sever's order).

## Migration and Rollout Order
1. Spellbook hook. 2. Conduit: hook + inverse + transaction end. 3. Ward comment. 4. Tests, docs, notch, rebuild.

## Rollback Strategy
- Revert the three edits; nothing persisted or cached changes.

## Validation Expectations and Evidence Plan
- Red: a borrower meld issued during the fan-out completes before the notch ends (today); a fan-out error leaves the
  lender switched (today). Green: the meld parks until the notch ends and gets the incoming version; the error undoes
  the notch. Race: test `-k racing` and probe_rule2_race_rate.py show none of the four failure kinds, GIL off.

## Ticket Coverage Map
- Plan steps 1-5 of the task's PLAN note; lock audit in its FACT note.

## Unknowns and Decision Requests
- UNKNOWN: none. DECISION: design 2 and the reversal (the owner, 2026-10-25).

## Context / Handoff Summary
The notch's borrower fan-out moves inside its frozen window, with an undo on failure.
