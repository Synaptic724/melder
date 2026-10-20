# Code-description patch: the flag's write and the Book flag's distillation (meld_state_gate_2026_10_15)

## Metadata
- Patch ID: meld_state_gate_2026_10_15
- Components: SpellSystemStates.register_index, SpellSystemStates.non_resolvable_index_ids, RiskManager
- Status: active
- Owner: user; melder_1 (synaptic_python_developer) (patch)
- Created: 2026-10-15T21:00:00Z
- Updated: 2026-10-15T22:32:34Z

## Trigger justification
Ordering and concurrency: the flag must be in place before the gated event that `register_index` publishes, and the
reader runs inside callbacks that the registry fires under its own lock.

## Control flow
`register_index(spell_index, owner_spellbook_id=None, *, resolvable=None)`:
1. Refuse a capability that is neither None nor a bool (TypeError). Read the index id and selected id (RuntimeError
   when no selection, as before).
2. Registry lock: find the state; when absent create it (selection kept: False), else note whether its current id is
   the selected id (selection kept) and update it. Refresh the spell-id index; retire the verdicts held for the
   selected id; record the owner Book (all as before).
3. Still under the registry lock, write the capability (`update_flags`, state lock inside): False -> add
   `non_resolvable`; True -> remove; None -> remove unless the selection was kept. No publication; note whether
   the flag set changed and whether the validity is already `gated`. Then put the lineage in or out of the
   published set (`_publish_non_resolvable_membership_locked`, reading the flag back with `has_flag`): the set is
   replaced whole, never mutated, and nothing is replaced when the membership already matches.
4. `mark_structural_change(register_or_rebind)`: the state goes gated; when its validity changed, the RiskManager
   callback `on_structural_validity_change(index_id, gated)` runs, still inside the registry lock, outside the state
   lock. Add to the dirty set (as before).
5. When step 3 changed the flag and the validity was already `gated` (step 4 published nothing), call
   `state._republish_validity()`: the same callback with the current validity, under the registry lock and
   contained like step 4's, so every bucket holding the lineage refreshes with the new flag.

`RiskManager._refresh_spellbook_flag(conduit_id)`:
1. Manager lock: the conduit's bucket; none or no Book -> return. Both sets empty -> required False, no snapshot.
   Otherwise snapshot their union. Release the lock.
2. `_has_unexcluded_risk(snapshot)`: `not snapshot <= states.non_resolvable_index_ids` - one subset test, no lock;
   a `spell:` key or a removed lineage is never in the set, so it counts. All flagged -> False.
3. `spellbook._set_spellbook_validation_required(required)` outside every lock (failures swallowed, as before).

`RiskManager.register_conduit`: unregister, create the bucket, `_register_spell_risk` for each visible spell, then one
refresh. `register_spell`: `_register_spell_risk`, then one refresh when it registered something.

## Edge and error semantics
- A notch to a resolvable=False version: step 3 adds the flag, step 4's event refreshes every conduit that holds the
  lineage and none of them counts it any more; the owner's `register_spell` that follows does the same.
- A notch back to a resolvable version: step 3 removes the flag before step 4, so the event's refresh counts the
  lineage again, with the resolution risk the sets kept while it was flagged (a reactivated borrowed copy is never
  re-registered, so nothing else would restore it). After a repeat notch the lineage is still `gated` then (a
  notch commit runs phases 1-4 only for a member never compiled), so step 4 publishes nothing and step 5 is that
  refresh.
- A transfer: the flip registers a fresh state with the capability; the rollback re-registers with it; the disable
  step's registration of a missing state is unflagged until the flip.
- A removed lineage: `unregister_index` takes it out of the set when it pops the state, before it fires `cleaned`,
  so the lineage counts until `unregister_spell` drops it - unchanged.
- A refresh racing a registration reads the set from before or after it; the refresh that the registration's event
  runs reads the new one, because the set is replaced before the event publishes. A refresh racing the registry's
  cleanup finds the empty tombstone set, or the cleaned-registry RuntimeError, never a missing attribute.
- Callers that pass no capability: nothing is ever flagged and every refresh answers as before.

## Invariants and idempotency
- The flag is present iff the last registration that supplied a capability said False and the selection has not
  changed since.
- Registering again with the same capability changes nothing on the flag and publishes nothing extra;
  `update_flags` is idempotent.
- The risk sets after any sequence of calls are the sets today's code produces for the same sequence.
- The published set equals the registered lineages whose state carries the flag at every release of the registry
  lock.
- Lock order stays registry -> state and never manager -> registry; no new lock.

## Explicit non-goals
- No change to validity, verdicts, meld doors, the gate, the contract check, Nexus, records or caches.
- No fix for the pre-existing ordering race between two refreshes.

## Validation focus points
- The gated event sees the new flag and the new set (a recording manager's callback reads `index_has_flag` and
  `non_resolvable_index_ids`).
- Notch False -> True on a borrower whose copy is reactivated: the borrower's flag rises, also when the lineage was
  already `gated` (step 5).
- GIL off: melds racing notches both ways never build a definition and never skip the gate for an unvalidated
  resolvable version.

## Context / Handoff Summary
- What changed: written before any edit; step 5 added 2026-10-15T21:20:19Z (found while writing the risk tests); the
  published set added 2026-10-15T22:12:54Z (the per-key probe's cost grew with the definition count).
- Remaining unknowns: none.
- Next entrypoint: the mapping note in the ticket, then the scratch-tree build.
