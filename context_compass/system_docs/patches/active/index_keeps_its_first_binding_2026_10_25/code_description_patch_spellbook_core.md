# code_description_patch_spellbook_core

## Metadata
- Patch ID: index_keeps_its_first_binding_2026_10_25
- Component: Spellbook Core (Binding and Conjure)
- Status: draft
- Owner: Mark
- Author: melder_1 (synaptic_python_developer)
- Created: 2026-10-25T09:13:34Z
- Updated: 2026-10-25T09:13:34Z

## Trigger Justification
- A policy gate moves ahead of registration (`bind_inactive`), and the notch's claim move becomes a compare-and-set
  that decides a refusal inside the held window; the order of the steps and their error semantics are the contract.

## Control-Flow Description (Pseudocode Level)
1. `bind_inactive(...)`, inside its bind window:
   1. `new_spell = self._bind.bind(...)` - the version and its fresh index (`SpellIndex.for_binding`).
   2. The spell_id collision check, as today.
   3. NEW: `spell_index.check_cleaned()`; then `if spell_index.selected_spell_id not in self._spell_ids`: log, raise
      RuntimeError "bind_inactive: target index <id> is not owned by this spellbook; stage a version only onto an
      index this Spellbook owns (call bind_inactive through the conduit of the Spellbook that owns the index)."
   4. NEW: `spell_index.check_admits(new_spell, verb="bind_inactive")` - after ownership: for another Book's index
      the binding is moot.
   5. `_add_hooks_to_spell`, the posture check, registration, the owner stamp, `_apply_add_to_index`, the crystals, the
      research entry and the post hooks, as today.
   6. Any raise before registration starts retires the unpublished Spell and its fresh index (the existing handler).
2. `_apply_add_to_index(spell, target_index)`: owned; parked; the same index returns; the target owned; NEW
   `target_index.check_admits(spell, verb="add_to_spell_index")`; the move, as today.
3. `_apply_notch(spell_index, spell, change_reason)`, under the Book lock:
   1. `outgoing = self._spells.get(spell_index)`; `outgoing is spell` returns (the no-op), as today.
   2. NEW: `previous = self._aetheric_frame.get_lookup(spell._key)`.
   3. NEW: `holder = self._aetheric_frame.repoint_lookup(spell._key, new_id, from_spell_id=<outgoing.spell_id, or
      None when the index has no active version>)`.
   4. NEW: `holder is not None`: log; raise RuntimeError (the refusal text below). Nothing has moved.
   5. `try`: park `outgoing` and clean its creation context, promote `spell`, as today. `except`: put the claim back -
      `release_lookup_by_spell_id(new_id)` when `previous` is None, else `repoint_lookup(spell._key, previous,
      from_spell_id=new_id)` - and re-raise.
   6. `spell_index.update(new_id)`; the index crystal; REMOVED: `update_lookup(spell._key, new_id)`.
   7. After the lock, as today: `register_index`, the downstream marks, the RiskManager, Nexus, `invalidate_spell`, the
      gated verdicts.
4. `_revert_refused_notch(...)`: with a restored version, `_apply_notch(restored, mutation_rolled_back)` (its step 3
   moves the claim from the refused version back to the restored one), the dependencies and the topology put back;
   REMOVED: the `refused._key != restored._key` branch. With none, `_revert_refused_activation` and
   `_restore_binding_key`, as today.
5. `_apply_remove_from_index(spell, source_index)`: the checks, then `new_index = SpellIndex.for_binding(spell_id,
   spellframe=spell.spellframe, spell_name=spell.spell_name, binding_name=spell.binding_name)`; the rest as today.

## Edge/Error and Rollback Semantics
- The refusal text, holder in this Book (`self._spells_by_id.get(holder)` is a Spell): "notch_spell refused: the
  address of SpellIndex <id> - <its binding> - is held by spell_id '<holder>' ('<holder name>'), the active version
  of another index of this Spellbook, so the notch did not happen and nothing moved. A version split off with
  remove_from_spell_index goes active only once its address is free: move it back into that index with
  add_to_spell_index and notch there, or dispose that index's versions with cleanup_spell first."
- Holder elsewhere: "... is held by spell_id '<holder>', an active spell of another Spellbook of this frame, so the
  notch did not happen and nothing moved. There is one active spell per address per frame: notch once that spell is
  disposed, or bind this class as a new spell at another address."
- `<its binding>` is the incoming version's binding, which is its index's.
- The no-op notch to the active version returns before the claim is read.
- An index with no active version (one `remove_from_spell_index` minted) passes `from_spell_id=None`: a free address
  is claimed, a held one refused.
- The refusal raises from the seam, before `_notch_spell`'s `try`: no reversal runs; `Conduit.notch_spell` ends the
  transaction as failed (its gates reopen) and runs no fan-out.
- The put-back in step 3.5 covers a park or promotion that raises (a Melder bug the Conduit's target checks make
  unreachable from public calls); the index then ends as that path ends today, with the claim where it was.

## Invariants and Idempotency Expectations
- After a notch that stands, the address's claim names the incoming version; after a refusal it names what it named.
- A notch back moves the claim back by the same compare-and-set; repeating a notch is a no-op.
- `bind_inactive` and `add_to_spell_index` refused leave the Book, the index and the frame as they were; a retry with
  the index's binding succeeds.

## Explicit Non-Goals
- No check of the incoming version's parked status before the park
  (TASK-2026-10-16-notch_seam_checks_incoming_before_parking, backlog).
- No change to the borrower fan-out, the structural check of 0.2.8262 or the transaction strategies.

## Validation Focus Points
- C7 compiled and never compiled: RuntimeError naming English's spell_id; English selected, claimed and meldable by
  address; French's index with no active version.
- Cross-Book: RuntimeError naming Spanish's spell_id; Spanish keeps the claim; French stays parked.
- The split version goes active once its address is free; the notch keeps the index's address and a notch back
  returns the claim.
- The foreign-index staging registers nothing; a retry on the Book's own index succeeds.

## Context / Handoff Summary
- What changed: the control flow of the way-in checks and of the notch's claim move.
- Remaining unknowns: none.
- Next entrypoint: `Spellbook._apply_notch`.
