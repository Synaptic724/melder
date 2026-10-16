# Code-description patch: marking a consumer and its recheck (contract_recheck_on_notch_2026_10_16)

## Metadata
- Patch ID: contract_recheck_on_notch_2026_10_16
- Components: the Spellbook's contracted-map mutators, Conduit.notch_spell's fan-out, Meld's gate,
  ContractProviderPresenceStrategy, SpellbookValidationError
- Status: active
- Owner: user; melder_1 (synaptic_python_developer) (patch)
- Created: 2026-10-16T10:32:18Z
- Updated: 2026-10-16T10:32:18Z

## Trigger justification
Ordering and concurrency: the mark is issued by mutators that callers run under ward and contract locks, a notch's
fan-out parks and activates in separate steps that a meld can fall between, and the recheck runs Phase 4 over maps
that the same change may still be writing. Error semantics also change for a lost provider.

## Control flow
A change of an active contracted copy in Book B (any of the five mutators):
1. Under B's lock: change the maps, as today; compute the copy's key K (already computed where the mutator needs it)
   and read `B._conjured`.
2. Release B's lock.
3. `_add_contracted_spell` only: the collection mark of the frame key, as today.
4. When conjured: `B._mark_contract_dependents_dirty({K})` -> `SpellSystemStates.mark_contract_dependents_dirty(
   spellbook_id=B._id, contract_keys={K})`: under the registry lock, every consumer lineage recorded under (B, K) gets
   `set_validity(gated, contract_unvalidated, flags_to_add=[contract_unvalidated], transitively_dirty=False)` - the
   state lock is taken and released, then, when the validity changed, `RiskManager.on_structural_validity_change`
   marks the lineage risky in every conduit bucket that holds it and raises those Books' flags (a plain attribute
   write) - and the lineage joins the dirty set.
5. The staged-key refresh and the copy's RiskManager registration or unregistration, as today.

A lender's notch on conduit L, after its transaction ends, when the active member changed (old -> new):
1. `_deactivate_borrowed_spell(old)`: each linked peer's Book parks its copy of old -> mark of K.
2. With D3, `_activate_borrowed_spell(new)`: each linked peer's Book reactivates a parked copy of new -> mark of K.
3. `_emit_index_notch(index, old, new)` under L's ward lock: each index-link receiver parks old (now a no-op) and
   makes new active (`_ensure_contracted_active`: reactivate or add; a no-op after step 2) -> mark of K.
The first mark of a consumer publishes; the later ones find it `gated` and publish nothing.

The consumer's next meld through conduit C (C's Book flag is up):
1. `_ensure_lineage_resolvable`, structural branch: the lineage is `gated`, so under the rebuild window (dynamic)
   and the spell lock phases 1-4 rerun for this spell against C's Book. Phase 4's presence check finds the provider
   (the lineage becomes `valid`, `contract_unvalidated` removed) or not (it stays `gated`).
2. Broken -> `invalid` and SpellbookValidationError; still not `valid` -> SpellbookValidationError (with D1-B it
   names the contract); `valid` -> `_force_resolution_revalidation(structure_changed)` gates C's verdict.
3. Resolution branch: C's verdict is `gated`, so phases 5-11 rerun for C; Phase 8 resolves K to the active copy's
   spell id, Phase 11 compiles the plan and the context (per spell) is republished; C's verdict becomes `valid`.
4. Execution builds the consumer over the provider now active. No contract scan anywhere on this path.
5. A meld of the lineage through another conduit afterwards finds the lineage and its own verdict `valid` and uses
   the republished context: one 5-11 pass per change serves every conduit (probe L1).

## Edge and error semantics
- Notch, notch back, repeat notch: every hop marks; the first meld after a hop runs phases 1-4 and 5-11 once; warm
  melds after it run neither (probe S1).
- Notch to a version whose `__init__` cannot be resolved: the contract is present, so Phase 4 passes; the
  construction raises the UnresolvedInputError a first meld of that version raises (probe S3).
- Provider gone (index destroy, an anchored copy parked, uncontract, remove-all): Phase 4's warning keeps the
  lineage `gated`; SpellbookValidationError, the first meld's error (probe S4; D1 decides its message).
- A meld that falls between a notch's park (step 1) and its activation (step 2 or 3) finds the consumer `gated` with
  no provider and raises SpellbookValidationError; the activation marks it again and the next meld follows. In the
  same window today the scan raised MeldExecutionError.
- A meld already executing when the mark lands finishes over the provider it read: mark only.
- A stored `unique`, `unique_per_conduit` or slotted consumer keeps its object and its provider; after a purge the
  next meld builds over the new version (probe S6). A `many` consumer built before keeps its provider.
- Before conjure nothing is marked. A non-resolvable consumer is marked like any other; its meld is refused before
  the gate as today, and rule 1 keeps its lineage out of the Book flag.
- Grant: the mutator marks, then `_invalidate_contract_consumers` marks again (and extracts, as today); the second
  mark publishes nothing.
- A registry cleaned while its Book is live: the mark raises after the map change, as the collection mark does.
- Out of rule 2, unchanged: a provider's dependency notch (D2); a lent consumer whose relaying Book alone loses the
  provider (D4, probe L3 and L4).

## Invariants and idempotency
- Marking is idempotent: a second mark of a `gated` lineage changes nothing and publishes nothing.
- One 5-11 pass per provider change per consumer lineage, at its first meld after the change.
- No meld path reads anything new; the gate reads the same two states as today.
- Lock order: the caller's ward or contract lock (when it holds one) -> registry -> state, then RiskManager under
  the registry lock; the Book lock is released before the mark. Nothing under the registry, state or RiskManager
  lock takes a ward, contract, conduit or Book lock, so the new edges close no cycle.

## Explicit non-goals
- No disposal, extraction or rebuild at a provider change; no change to grant, uncontract, sever or remove-all's
  extraction.
- No change to the compiler's contract handling, the gate's branches, the meld doors, RiskManager, records, caches.
- Not the provider's dependencies (D2) and not a lent consumer's Book-local provider loss (D4).

## Validation focus points
- The mark is issued with the Book lock free (a registry double that asserts it).
- A notch's fan-out: the consumer is `gated` after step 1 and still `gated` after steps 2-3, one publication.
- GIL off: melds racing notches back and forth and index destroys never raise from Phase 4's walk, never deadlock,
  and after the racing stops the next meld builds over the active version.
- Cost: a warm consumer meld at about 2 us with no scan; one 5-11 pass per change (probe counters).

## Context / Handoff Summary
- What changed: written before any edit.
- Remaining unknowns: none; decisions D1-D5 are the owner's (architecture_patch.md).
- Next entrypoint: the mapping note in the ticket, after the owner's approval.
