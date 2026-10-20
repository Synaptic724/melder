# Code-description patch: marking, the downstream walk and the recheck (contract_recheck_on_notch_2026_10_16)

## Metadata
- Patch ID: contract_recheck_on_notch_2026_10_16
- Components: the Spellbook's contracted-map mutators and `_apply_notch`, SpellSystemStates' marks and walk,
  Conduit.notch_spell's fan-out, Meld's gate and catch-up, ContractProviderPresenceStrategy, SpellbookValidationError
- Status: active; the owner decided D1-D5 (2026-10-16)
- Owner: user; melder_1 (synaptic_python_developer) (patch)
- Created: 2026-10-16T10:32:18Z
- Updated: 2026-10-16T12:57:39Z

## Trigger justification
Ordering and concurrency: marks are issued by mutators that callers run under ward and contract locks and by the
notch inside its window; a notch's fan-out parks and activates in separate steps that a meld can fall between; the
recheck runs Phase 4 over maps the same change may still be writing; and the catch-up runs another lineage's phases
before a plan compiles, under that lineage's window and lock. Error semantics also change for a lost provider and for
a dependent of a changed dependency.

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
   write) - and the lineage joins the dirty set. Still under the registry lock, the walk (below) runs from those
   consumers. The call returns the consumers only.
5. The staged-key refresh and the copy's RiskManager registration or unregistration, as today.

The walk, `mark_dependents_for_revalidation(seeds)`, under the registry lock (re-entrant):
1. A worklist from the seeds; a visited set holds the seeds.
2. For each lineage taken: its `direct_dependents` are edge-reached; when `_binding_key_by_index` holds its key K',
   the consumer lineages recorded under K' in every Book's contract index are contract-reached. Unvisited ones join
   the worklist.
3. When the worklist is empty, each reached lineage except the seeds is marked: edge-reached
   `mark_transitively_dirty()`, contract-reached rule 2's `set_validity(...contract_unvalidated...)`, both when
   reached both ways; each joins the dirty set and publishes to RiskManager when its validity changed.

A notch in Book L of lineage D (`old` -> `new`):
1. Inside the notch window, `_apply_notch`: park `old`, promote `new`, repoint the index and the frame signature,
   then (Book lock released) `register_index(..., resolvable=new.resolvable, binding_key=new._key)` - D `gated` -
   and `mark_dependents_for_revalidation((D,))`: everything downstream of D is marked, in every Book.
2. The commit, as today (phases 1-4 for a promoted member never compiled).
3. After the window, the fan-out: `_deactivate_borrowed_spell(old)` -> each linked peer parks its copy of `old` ->
   mark of D's key; with D3 `_activate_borrowed_spell(new)` -> each linked peer reactivates a parked copy of `new` ->
   mark; `_emit_index_notch(index, old, new)` under L's ward lock -> each index-link receiver parks `old` (a no-op
   now) and makes `new` active -> mark. Every mark walks on. The first mark of a lineage publishes; the later ones
   find it `gated` and publish nothing.

A meld of spell S through conduit C after any of these (C's Book flag is up when S or anything C holds is marked):
1. `_ensure_lineage_resolvable(S)`: S may compile (its lineage or effective verdict is not `valid`, or it carries
   `resolution_required`), so the catch-up runs first, with no lock held:
   - walk S's plan: S's topology in the registry; NORMAL socket targets mapped to their lineage's current version
     and looked up in the pool of S's Book; SPELL_CONTRACT keys resolved in S's Book's active contracted maps; each
     spell once; a refreshed one through its new topology;
   - for each stale dependency X (`gated` or `unknown`): enter X's rebuild window, take X's lock, re-check; phases
     1-4 with X's owner Book; broken -> X `invalid`, SpellbookValidationError([X]); not `valid` ->
     SpellbookValidationError([X]); `valid` -> X's CreationContext cleaned, Phase 5+ artifacts cleared,
     `resolution_required`, door epoch bumped; release X's lock and window.
2. Structural branch for S, as today: under S's rebuild window and lock, phases 1-4 against C's Book; Phase 4's
   presence check for a consumer; broken -> `invalid` and SpellbookValidationError; not `valid` ->
   SpellbookValidationError (D1-B names a lost contract); `valid` -> `_force_resolution_revalidation(structure_changed)`
   gates C's verdict.
3. Resolution branch (S not `resolution_required`): C's verdict is `gated`, so phases 5-11 rerun for C; Phase 5's
   scope and Phase 8's occurrences read current topologies; Phase 11 compiles the plan and the context (per spell) is
   republished; C's verdict becomes `valid`.
4. Execution builds S over the versions now active. No contract scan anywhere on this path.
5. A meld of S through another conduit afterwards finds the lineage and its own verdict `valid` and uses the
   republished context: one 5-11 pass per change serves every conduit (probe L1).
6. A refreshed dependency X melded directly later, in any conduit: its door finds `resolution_required`, the deferred
   lane runs the catch-up for X's own plan, then X's full target pass (no Phase 5 root), and X builds over the
   versions now active.

## Edge and error semantics
- Notch, notch back, repeat notch of a provider: every hop marks; the first meld after a hop runs phases 1-4 and 5-11
  once; warm melds after it run neither (probe S1).
- Notch of a dependency (Q -> P -> D, one Book or across Books): P and Q are marked; Q's first meld refreshes P with
  one catch-up, then reruns its own 1-4 and 5-11 and builds the new D; Q's next melds take the fast door; P's own meld
  then runs its full pass (probe C1-C3, X1 "catchup").
- A notch to a version the dependency's annotation no longer selects (a class annotation and a subclass, under the
  kind rule): the refresh leaves the dependency `valid` with an UNRESOLVED_INPUT socket, and the dependent's meld
  raises the first meld's UnresolvedInputError naming the parameter (probe C4) - today it built the old version.
- Notch to a version whose `__init__` cannot be resolved: the contract is present, so Phase 4 passes; the
  construction raises the UnresolvedInputError a first meld of that version raises (probe S3).
- Provider gone (index destroy, an anchored copy parked, uncontract, remove-all): Phase 4's warning keeps the
  lineage `gated`; SpellbookValidationError, the first meld's error, naming the contract (D1-B; probe S4). When the
  consumer is a dependency of the melded spell, the catch-up raises it naming the consumer.
- A meld that falls between a notch's park and its activation finds the consumer `gated` with no provider and raises
  SpellbookValidationError; the activation marks it again and the next meld follows. In the same window today the
  scan raised MeldExecutionError.
- A notch racing a dependent's compile: the compile may record a visibility failure (its verdict `invalid`); the
  notch's walk has marked the dependent's lineage `gated`, so its next meld reruns 1-4, gates the verdict again and
  recompiles.
- A meld already executing when a mark lands finishes over what it read: mark only.
- A stored `unique`, `unique_per_conduit` or slotted object keeps its provider and dependencies; after a purge the
  next meld builds over the new versions (probe S6). A `many` object built before keeps them too.
- Before conjure nothing is marked. A non-resolvable consumer is marked like any other; its meld is refused before
  the gate as today, and rule 1 keeps its lineage out of the Book flag.
- Grant: the mutator marks, then `_invalidate_contract_consumers` marks again (and extracts the consumers' objects,
  as today); the second mark publishes nothing, and the walk extracts nothing.
- A registry cleaned while its Book is live: the mark raises after the map change, as the collection mark does; the
  walk returns an empty set on a cleaned registry.
- Out of scope, unchanged: a lent consumer whose relaying Book alone loses the provider (D4, probe L3 and L4);
  `Conduit.validate_resolution`'s conduit-wide pass, which runs no catch-up.

## Invariants and idempotency
- Marking is idempotent: a second mark of a `gated` lineage changes nothing and publishes nothing; the walk visits
  each lineage once and terminates on cycles.
- A refresh is idempotent: it re-checks staleness under the dependency's window and lock, so two dependents melded
  at once refresh a shared dependency once.
- One 5-11 pass per change per lineage, at its first meld after the change; a refresh per stale dependency per
  change, at the first compile that expands it.
- No warm meld path reads anything new; the gate's catch-up runs only when the spell may compile.
- Lock order: the caller's ward or contract lock or the notch window (when it holds one) -> registry -> state, then
  RiskManager under the registry lock; the Book lock is released before every mark. The catch-up holds no lock while
  it walks, then one dependency's window and lock at a time, before the melded spell's own. Nothing under the
  registry, state or RiskManager lock takes a ward, contract, conduit or Book lock, so the new edges close no cycle.

## Explicit non-goals
- No disposal, extraction or rebuild at a provider or dependency change; no change to grant, uncontract, sever or
  remove-all's extraction of consumer objects.
- No change to the compiler's contract handling, the gate's branches, the meld doors, RiskManager, records, caches.
- Removal and ownership transfer keep their edge-only closure.
- Not a lent consumer's Book-local provider loss (D4) and not the conduit-wide pass.

## Validation focus points
- Every mark is issued with the Book lock free (a registry double that asserts it).
- A notch's fan-out: the consumer is `gated` after the park and still `gated` after the activation, one publication.
- The walk: chain, cross-Book and walk-on cases on a real registry; no seed marked; one publication per change.
- The catch-up: owner Book used; window before lock; no lock across the walk; plan reset fields; raises naming the
  dependency.
- GIL off: melds racing notches back and forth and index destroys never raise from Phase 4's walk, never deadlock,
  and after the racing stops the next meld builds over the active versions.
- Cost: a warm consumer meld at about 2 us with no scan; per change, one 5-11 pass per lineage and one refresh per
  stale dependency (probe counters); the walk's time for a notch with many dependents.

## Context / Handoff Summary
- What changed: written before any edit; the downstream walk and the catch-up added for D2 (2026-10-16T12:22:44Z).
- Remaining unknowns: none; the owner decided D1-D5 (architecture_patch.md).
- Next entrypoint: the mapping note in the ticket (approved by the owner on 2026-10-16).
