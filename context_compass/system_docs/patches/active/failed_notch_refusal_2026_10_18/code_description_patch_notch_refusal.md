# Code description patch: the notch entry's check and reversal (failed_notch_refusal_2026_10_18)

## Control flow
1. `_notch_spell(spell_index, spell, change_reason)`: `check_cleaned`; under the Book lock read the before-state -
   the index's active version, its `selected_spell_id`, `_lookup_spells.get(spell._key)` - then the frame claim
   (`get_lookup(spell._key)`) and whether SpellSystemStates tracks the index.
2. A notch to the active version returns at once (the seam's no-op) and journals nothing.
3. `_apply_notch(...)`: the switch and its publications, as today, minus the journal entry.
4. When the Book is conjured and the now-active `spell` has no Phase-4 result and no Phase-5 root blueprint:
   `_run_post_conjure_structural_phases([spell])`.
5. It passes, or was not needed: journal the promotion (`_record_research_promotion(before_active_id, spell_id)`)
   and return `spell`.
6. It raises SpellbookValidationError: build the refusal error first (its report renders from the Phase-4 result
   still on the spell), then `_revert_refused_notch`, then `SpellCompilerArtifact.reset_phase_artifacts()` on the
   refused version, then raise the refusal from the check's error.
7. It raises anything else: `_revert_refused_notch` and the reset, then re-raise it.

## Edge and error semantics
- The refusal line: "notch_spell refused: '<name>' (spell_id <id>) failed its structural check, so the notch did
  not happen; '<name>' (spell_id <id>) is still the active version of the index." With no outgoing version the tail
  reads "...; the index still has no active version.".
- Phase-4 results are transient elsewhere (nulled at conjure end); a refused version's are reset at once, so the next
  notch to it runs the check again instead of reading a verdict computed while it was active.
- A version that passes keeps its Phase 1-4 results, as at today's commit; the commit validator then skips it.

## Invariants and idempotency
- Inside the window nothing else runs against the Book, its conduits or the binding key (the seal), and no meld runs
  on the sealed conduits (the gate freeze), so the before-state cannot move between steps 1 and 6.
- A refused notch can be retried; it is checked, and refused again, until the version's world lets it pass.

## Explicit non-goals
- No rollback in the change-control machinery: a session rollback action runs after the orchestrator's failed
  commit has released the request's scope claims (`release_implicit_embargoes`), outside the seal.
- No check before the switch: parked, the incoming version is not in `_spell_id_pool`, from which Phase 3 takes its
  candidates, so the check would judge a world without it (SelfMade could not resolve to itself).
