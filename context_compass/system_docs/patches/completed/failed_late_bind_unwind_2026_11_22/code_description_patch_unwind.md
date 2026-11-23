# code_description_patch_unwind

## Metadata
- Patch ID: failed_late_bind_unwind_2026_11_22
- Component: `Spellbook._unwind_refused_bind_window`, `Spellbook._end_bind_window`, the late-bind marking in
  `Spellbook.bind`, and `ChangeControlManager._default_abort_hook`
- Status: implemented at 0.2.8316; merged
- Owner: Mark (accountable); melder_0 (synaptic_python_developer)
- Created: 2026-11-23T10:14:18Z
- Updated: 2026-11-23T11:20:00Z

## Control Flow Commitments
- `Spellbook.bind`, after conjure: right after the address claim, append the spell id to
  `_pending_late_bind_spell_ids` and raise the flag (the pin), then `register_index(..., late_bind_thread_id=<this
  thread>)`, then publish the Book maps. Before conjure `register_index` runs at the same point without the mark.
- `ChangeControlManager._dispatch_commit_validator`: when the structural validator raises for a bind request, record
  the refusal under the request id, then re-raise.
- The orchestrator's commit failure calls the abort hook with the claims held. `_default_abort_hook` pops the
  request's refusal; with none it returns (an in-window abort, or another request). Otherwise it resolves the
  Spellbook as the validator does and calls `_unwind_refused_bind_window(refusal)`; an unresolvable Spellbook adds a
  note to the refusal.
- `_unwind_refused_bind_window(refusal)`:
  1. Snapshot, under the Book lock, the window's active late-bound spells (the pending structural spells whose ids
     are marked) and its parked mates.
  2. Collect the announce keys while they are live: each spell's frame key and `CompilerPhase3._hidden_type_key`.
  3. Each active spell, newest first: `unregister_index` (its impact closure flags the edge dependents; the mark goes
     with it), the RiskManager unregister, the crystal removals when recording, the Book map pops under the Book lock,
     `_unregister_owned_spell_id` (id maps and the Nexus record), `Aether._remove_single_spell_index`,
     `release_lookup_by_spell_id`, `Creations.forget_slot` for a slot this window filed, the discard and cleanup of a
     managed pool this window composed, `unregister_spell_index_gate` and the gate's cleanup, then the Spell and its
     index cleaned.
  4. Each parked mate, newest first: `_dispose_spell` (the parked branch), the discard of a pool its stamp composed,
     and the unregister and cleanup of the gate its throwaway index registered.
  5. `mark_collection_dependents_dirty` with the announce keys, then the bookkeeping cleared.
  6. A note on the refusal naming the spells removed, and one per step that failed.
- `Spellbook.end_transaction`, bind branch: the mediator end runs in a `try`; in its `finally`, when no bind session
  remains for the identity, `_end_bind_window` runs: clear the marks still registered, clear the bookkeeping (the pin
  drops with it), and refresh the Book flag through `RiskManager.refresh_spellbook_flag`.

## Edge and Error Semantics
- Each unwind step runs in its own best-effort `try` (documented cleanup behaviour): its failure is logged at ERROR
  with the spell and the step, recorded for the note, and the next step runs.
- The refusal keeps its type and text; the orchestrator re-raises it after the hook.
- A refusal raised before any late bind was marked (a window opened before conjure) unwinds nothing: the validator
  returns early for an unconjured Book, so nothing is recorded.

## Invariants and Idempotency
- The unwind touches only what this window registered: the spells in its bookkeeping, a slot it filed, a pool it
  composed, the gates its stamps registered.
- `_end_bind_window` is safe after the unwind: the marks and bookkeeping it clears are already gone.

## Explicit Non-Goals
- No unwind for an in-window abort, a failing dirty marker or a failing general commit hook or validator.
- No undo of forward-only records (bind callbacks, the research journal, crystal tap rows, fact stamps) or of objects
  melds built during the window.
