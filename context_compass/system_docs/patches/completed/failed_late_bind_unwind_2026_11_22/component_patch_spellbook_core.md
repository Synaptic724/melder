# component_patch_spellbook_core

## Metadata
- Patch ID: failed_late_bind_unwind_2026_11_22
- Component: Spellbook Core - `Spellbook.bind`, `Spellbook.bind_inactive`, the bind window (`end_transaction`,
  `_clear_bind_transaction_state`), the Book flag setter and the new unwind
- Status: implemented at 0.2.8316; merged
- Owner: Mark (accountable); melder_0 (synaptic_python_developer)
- Created: 2026-11-23T10:14:18Z
- Updated: 2026-11-23T11:20:00Z

## Component Purpose and Boundary
- Current boundary: a post-conjure bind publishes the spell into the Book maps, then registers its lineage and its
  RiskManager entry; the window's end clears the pending collections only when the commit succeeds; nothing undoes a
  refused window.
- Target boundary: a post-conjure bind pins the Book flag up and registers its lineage marked as being late-bound
  before the Book maps publish the spell; the window keeps the bookkeeping the unwind needs; the window end clears the
  marks, drops the pin and refreshes the flag, committed or not; `_unwind_refused_bind_window` undoes a refused window.

## Before/After Behavior Summary
- Before: after a refused late bind the spell stays in the Book maps, the frame registries, SpellSystemStates, the
  RiskManager and the Nexus record; a second bind of it raises the spell-id collision.
- After: after a refused late bind none of those hold it; a second bind gets the same refusal, and binds once its cause
  is fixed. A good window-mate is unwound too (the window is the transaction) and binds again. A `bind_inactive`
  window-mate is disposed as a parked version. An existing object bound in the window leaves its store slot and is not
  disposed. A managed pool the bind composed is discarded and cleaned.
- Unchanged: a bind before conjure; a committed late bind; an in-window abort (its spells stay, their marks clear).

## Interface Deltas
- `_set_spellbook_validation_required(required)`: writes `required or <a late bind is open>`.
- `_unwind_refused_bind_window(refusal) -> None` (internal, called by the manager's abort hook).
- `_end_bind_window() -> None` (internal, the outermost window end).
- Window bookkeeping (internal slots): `_pending_late_bind_spell_ids` (list), `_pending_inactive_spells` (list of
  `(Spell, throwaway index id)`), `_pending_composed_pool_ids` (set), `_pending_registered_slot_keys` (set).

## State and Lifecycle Deltas
- The four bookkeeping slots follow `_pending_structural_spells`: initialized in `__init__`, reset by
  `_prepare_bind_transaction_state`, cleared by `_clear_bind_transaction_state`, removed at cleanup.
- `bind`: `register_index` moves before the Book maps publish (for every bind); after conjure it passes
  `late_bind_thread_id`, and the spell id joins `_pending_late_bind_spell_ids` before that call, which pins the flag.

## Failure Mode Deltas
- Removed: the registration a refused late bind left behind, and the spell-id collision on its retry.
- New: none for callers; a failed unwind step is logged at ERROR and named in a note on the refusal.

## Dependency and Ordering Constraints
1. Pin, then mark (`register_index`), then publish (the Book maps under the Book lock).
2. The unwind runs on the committing thread with the claims held: collect the announce keys, undo each active spell
   newest first, dispose the parked mates newest first, re-gate the watchers, clear the bookkeeping.
3. The window end runs in a `finally` around the mediator end, after the commit or its failure.

## Validation Expectations
- A refused lone late bind leaves nothing registered; its retry is refused again, not as a collision; fixed, it binds.
- A window with a good mate and a refused spell: both removed; the good mate binds and melds again.
- An existing object, a managed spell and a `bind_inactive` mate in a refused window: removed as above.
- A Book the unwind empties still sees later bind ids (the frame's spell-id set link survives).
- An in-window abort unwinds nothing and leaves no mark.
- The flag is up while a late bind is open and is recomputed at the window end.
