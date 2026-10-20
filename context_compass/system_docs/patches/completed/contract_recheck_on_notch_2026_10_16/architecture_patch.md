# Architecture patch: contract_recheck_on_notch_2026_10_16

## Metadata
- Patch ID: contract_recheck_on_notch_2026_10_16
- Status: active; the owner decided D1-D5 and approved the patch as a whole (2026-10-16); the build is under way on
  every file but conduit.py, which stays with melder_0's notch-target task until it hands it over (D3's lines)
- Owner: user (the story settled in chat, 2026-10-16); melder_1 (synaptic_python_developer) (patch)
- Ticket: TASK-2026-10-16-recheck_contract_consumers_when_provider_changes - rule 2 of the owner's 2026-10-15
  direction (rule 1 landed as 0.2.8247 in TASK-2026-10-15-make_meld_state_checks_follow_spell_state).
- Created: 2026-10-16T10:32:18Z
- Updated: 2026-10-16T12:57:39Z

## Objective
A SpellContract consumer - a spell with a `SpellContract(...)` default, built from a provider its Book borrows from
a linked conduit - is checked on every gated meld today. `Meld._ensure_lineage_resolvable` calls
`_check_contracts_and_force_revalidation`, which reads the consumer's signature, looks each contract key up in the
Book's active contracted maps and gates the conduit verdict, so phases 5-11 rerun on every such meld: 1470-1650 us a
warm meld against 1.8-2.0 us without it (probe, both GIL modes). That scan is also the only thing that makes a
consumer follow its lender's notch: no path that changes a borrower Book's active contracted copy marks the consumers
of that copy; removed alone, the consumer keeps getting the old version.

The owner's rule (2026-10-16): a satisfied contract needs no per-meld check; a change of the provider a consumer
resolves - a notch above all, because a notched version's `__init__` may differ - marks that consumer for a recheck;
its next meld re-validates the contract and rebuilds against the version now active, or fails with the error a first
meld would give; objects already built keep their provider (mark only). And (D2): "if the spell being notched is a
dependency for something else it should flag their spells for revalidation" - every spell that depends on the
notched one, in its Book or in another, by annotation or through a contract. Today a notch flags nothing downstream:
a dependent built before goes on building the old version, one never built fails with RuntimeError "many_only
manifest references unknown spell_id" (probe C1-C3); across Books, a contract consumer of a provider whose own
dependency was notched fails on every meld (probe S5, X1).

This patch:
1. the borrower Book's five contracted-map mutators mark the consumers of the changed copy's key `gated` +
   `contract_unvalidated` through `SpellSystemStates.mark_contract_dependents_dirty`;
2. the meld's per-meld scan is removed, so the gate's structural branch is the recheck;
3. a notch marks everything downstream of the notched lineage - registry edges and contract keys, transitively -
   and every contract-consumer mark walks on from the consumers it marks (D2);
4. wherever a plan is about to compile, the meld first refreshes the structure of every stale lineage the plan
   expands, so a dependent two hops from a notch compiles against its dependency's current structure (D2);
5. a lost provider is named in the meld's error (D1-B), and a notch back makes a parked version-anchored copy usable
   again with its consumers marked (D3).

## Non-goals
- No change to the compiler's contract handling (Phase 3 sockets and the contract index, Phase 4's presence check,
  Phases 8-9), to `SpellValidity` or `SpellState`, to the gate's two branches, to the meld doors, to RiskManager, to
  records, caches, spell ids or MutationResearch.
- Mark only: nothing is disposed, extracted or rebuilt when a provider or a dependency changes. Grant, uncontract,
  sever and remove-all keep the extraction `ConduitWard._invalidate_contract_consumers` already does, for the
  consumers only.
- Removal (`unregister_index`) and ownership transfer keep `compute_impact_closure` (registry edges only).
- Not a lent consumer's Book-local provider loss (a consumer lent to a second Book whose own link to the provider
  goes away): pre-existing, and the scan never closed it (D4: TASK-2026-10-16-investigate_lent_consumer_provider_loss).
- Not `Conduit.validate_resolution`'s conduit-wide pass: it compiles without the catch-up, and a stale dependency
  there gives the visibility failure it gives today.
- No new lock; one new registry map (a binding key per lineage); no new read on a warm meld path - the catch-up runs
  only where a plan compiles.

## Changed components
| component | change | file owner |
| --- | --- | --- |
| Spellbook: `_add_contracted_spell`, `_deactivate_contracted_spell`, `_reactivate_contracted_spell`, `_remove_contracted_spell` (active branch), `_clear_contracted_spells_for_conduit`; new `_mark_contract_dependents_dirty` | after the Book lock, when conjured, mark the Book's consumers of the changed active copy's key | melder_1 (released by melder_0, 2026-10-16T12:33:09Z) |
| Spellbook: `bind`, `_apply_notch` (D2) | pass `binding_key=spell._key` to `register_index`; the notch marks everything downstream of the notched lineage; `_apply_notch`'s docstring and comment corrected | melder_1 (released by melder_0, 2026-10-16T12:33:09Z) |
| SpellSystemStates: `register_index`, new `mark_dependents_for_revalidation`, `mark_contract_dependents_dirty`, `unregister_index`, `cleanup` (D2) | a binding key per lineage; the downstream walk over registry edges and contract keys; every contract-consumer mark walks on | melder_1 |
| Meld: `_ensure_lineage_resolvable`, `_ensure_runtime_resolution_ready`; new `_refresh_stale_dependencies` and helpers | the per-meld scan removed with its two helpers and their imports; the catch-up before a plan compiles (D2); docstrings | melder_1 |
| SpellbookValidationError (D1-B) | a spell with no error but a gating Phase-4 warning shows that warning as its reason | melder_1 |
| ContractProviderPresenceStrategy (D1-B) | the SPELL_CONTRACT_MISSING_PROVIDER message gains its remedy; a snapshot walk | melder_1 |
| Conduit: `notch_spell`, new `_activate_borrowed_spell` (D3) | after the notch window, make every linked peer's parked copy of the incoming version active again | melder_1, once melder_0's TASK-2026-10-16-public_notch_target_for_staged_versions lands (it holds conduit.py) |
| ConduitWard: `_add_spell_to_contract` docstring, `_get_spell_contract_keys` comment | say what a version-anchored grant does on a notch; name the Phase 8 analyzer's signature read | melder_1 |
| tests; system docs, graph descriptors, release note | the scan's unit tests replaced; marking, walk, catch-up, recheck, report and reactivation tests; docs | melder_1 |

## Invariants
1. Marking. Every change of a conjured Book's active contracted copy - added, parked, reactivated, removed, cleared -
   marks the Book's consumers of that copy's key `gated` + `contract_unvalidated` (not transitively dirty), after
   the map change is published and after the Book lock is released. A change of a parked copy only
   (`_add_inactive_contracted_spell`, the parked branch of `_remove_contracted_spell`) marks nothing: no consumer
   resolves a parked copy. Before conjure nothing is marked: conjure runs phases 1-4 for every spell.
2. Coverage. Every path that changes an active contracted copy ends in those five mutators: a grant and its
   dependency copies, an index link and its member copies, a lender's notch on every linked peer
   (`Conduit._deactivate_borrowed_spell`, and with D3 `_activate_borrowed_spell`) and on index-link receivers
   (`ConduitWard._emit_index_notch`), an index member's removal and an index destroy (`_uncontract_member_spell`), an
   uncontract, a remove-all, a root's dependency fallout (`_remove_root_from_contracts`) and an ownership transfer
   (it drives the ward's grant and uncontract verbs). A sever pops whole buckets (`_detach_link_contract`) and
   already marks every consumer on both sides (`_invalidate_contract_consumers`).
3. Mark only. A mark changes state; it builds, disposes and extracts nothing. Objects already built keep their
   provider and dependencies; the next build of a marked spell's object uses the versions active at that meld.
4. Recheck. A marked lineage is `gated`, so the event raises the Book flag in every bucket holding it and the
   lineage's next meld enters the gate: the catch-up (11) first, then phases 1-4 for the spell (Phase 4's presence
   check for a consumer); a missing provider leaves the lineage `gated` and the meld raises the first meld's
   SpellbookValidationError; otherwise it becomes `valid`, the conduit verdict is gated (`structure_changed`) and
   phases 5-11 rebuild against the versions now active. The CreationContext is per spell, so one rebuild serves every
   conduit that melds the lineage.
5. No per-meld contract work. A meld whose lineage and conduit verdict are `valid` and that owes no deferred pass
   reads no signature, looks nothing up, walks nothing and forces no rebuild, contract consumer or not.
6. One key. The mark uses the copy's key (`Spell._key`, the same as `Spellbook._make_spell_key`), the normalization
   of `SpellContract.canonical_key` that Phase 3's contract index records; the registry records the same key per
   lineage for the walk (every version of a lineage shares one binding signature).
7. Locks. Every mark runs after its caller releases the Book lock: registry lock -> state lock (released before the
   callback) -> RiskManager lock -> the Book flag's plain attribute write. Marks add edges only into the registry -
   from the owner's ward lock where `_emit_index_notch`, `_emit_index_destroy` and `_emit_index_member_removed` call
   the receiver's mutators, from a contract lock in `_remove_root_from_contracts`, and from the notch window - and
   nothing under the registry, state or RiskManager lock takes a ward, contract, conduit or Book lock, so no cycle.
8. Cost. One registry call per active-copy change and one walk per notch (cold paths). A warm meld of a contract
   consumer goes from about 1.5 ms to about 2 us; the first meld after a change pays the catch-up's refreshes, one
   structural and one 5-11 pass. While a marked lineage of a Book is pending, that Book's warm melds take the gate.
9. Errors. Every path keeps its error type except: a meld whose provider is gone raises the first meld's
   SpellbookValidationError instead of the scan's MeldExecutionError (both RuntimeError), and with D1-B its message
   names the contract; a dependent whose dependency's refreshed structure is broken or not valid raises
   SpellbookValidationError naming that dependency; a dependent whose dependency no longer resolves a parameter gets
   the first meld's UnresolvedInputError naming it, where it built the old version.
10. Downstream walk (D2). A notch marks every lineage downstream of the notched one: reached by a registry edge
    (frame-wide, so through borrowed spells too) - `gated` + `impacted_by_dependency`, transitively dirty; reached by
    a contract key (a consumer, in any Book, of the binding key of a lineage already reached, the notched one
    included) - `gated` + `contract_unvalidated`; and on from each. Every contract-consumer mark (invariant 1, the link
    commit hook, `_invalidate_contract_consumers`) walks on the same way from the consumers it marked. The walk visits
    each lineage once and marks no seed.
11. Catch-up (D2). Before a plan compiles in a meld - the gate when the spell may compile (its lineage or effective
    verdict not `valid`, or `resolution_required`), and the deferred lane when the spell owes it - every stale lineage
    (`gated` or `unknown`) the plan expands (topology targets by lineage, contract sockets through the active copy of
    the Book whose pass compiles) gets phases 1-4 with its owner Book under its rebuild window and spell lock, and its
    own plan reset (CreationContext, Phase 5+ artifacts, `resolution_required`, door epoch). A broken or still
    non-valid refresh raises SpellbookValidationError naming that lineage.
12. Catch-up locks. The walk holds no lock; a refresh holds one dependency's window and lock and releases them before
    the next; the dependent's own window and lock come after the catch-up. No nesting, no new lock-order edge.

## Interface deltas
- Removed (private): `Meld._check_contracts_and_force_revalidation`, `Meld._iter_spell_contract_defaults`.
- Added (private): `Spellbook._mark_contract_dependents_dirty(contract_keys)`; `Conduit._activate_borrowed_spell(
  spell_id)` (D3); `Meld._refresh_stale_dependencies(spell)` and its helpers (D2); the class constant
  `SpellbookValidationError.GATING_WARNING_CODES` beside `INTERNAL_CODES` (D1-B).
- Added (internal registry, D2): `SpellSystemStates.register_index(..., *, resolvable=None, binding_key=None)`;
  `SpellSystemStates.mark_dependents_for_revalidation(index_ids) -> Set[str]`; `mark_contract_dependents_dirty`
  walks on (its signature and return value unchanged).
- Public: no signature changes. Behaviour:
  - a consumer follows a lender's notch with one rebuild instead of a rebuild per meld;
  - a meld whose provider is gone raises SpellbookValidationError naming the parameter, the contract key and the
    remedy (release note, **Breaking** for code that catches MeldExecutionError there);
  - every spell that depends on a notched one rebuilds against the version now active at its next meld, or fails with
    the first meld's error - where it built the old version (release note, **Breaking** for code relying on that);
  - a contract consumer's dependents rebuild after a link, grant, uncontract or sever (a consumer compiled while its
    provider was missing was built with its SpellContract default object);
  - a version-anchored borrower gets its copy back when a notch back makes its version active again (D3).
- Persisted: none. No cache generation, record version or spell id moves.

## Migration order
This patch -> the owner's approval -> the mapping note in the ticket -> on a scratch copy of the tree: red tests ->
the melder_1 files (spell_system_states.py with the walk; meld.py with the scan's removal and the catch-up; the
error and the strategy; the ward's docstring and comment) -> spellbook.py (released by melder_0 at
2026-10-16T12:33:09Z: the five mutators, bind's and the notch's key, the notch's walk) -> green with the GIL off and
on -> the probes before and after -> the same diff in the real tree -> the suites again -> conduit.py (D3:
`_activate_borrowed_spell` and its call in `notch_spell`) once melder_0's
TASK-2026-10-16-public_notch_target_for_staged_versions lands and releases it - that task rebinds its resolved target to
`spell` and leaves the window and the fan-out lines as they are - with its tests and the suites once more ->
system docs, graph descriptors, release note, one notch above the current version -> closure -> rebuild.
The marking, the walk, the catch-up and the scan's removal land in one notch: the scan alone is what makes a consumer
follow today, and the walk without the catch-up strands a dependent two hops away.

## Rollback
Revert the notch's files. Nothing is persisted and no cache generation moves, so a revert restores today's behaviour
(the per-meld scan; no marking, no walk, no catch-up).

## Coverage matrix
| invariant | evidence |
| --- | --- |
| 1 | unit (each mutator, real SpellSystemStates): marks the key's consumers when conjured, nothing before conjure, nothing for a parked copy; the mark runs with the Book lock free |
| 2 | component, both GIL modes: index-link notch, notch back and repeat notch; grant and notch; index destroy; member removal; uncontract; remove-all; transfer with repoint; sever (unchanged) |
| 3 | component: a unique consumer keeps its object after a notch and builds the new version after a purge; a many consumer built before keeps its provider; a dependent's stored object keeps its dependency |
| 4 | component: after a notch the consumer is `gated` + `contract_unvalidated`, its next meld reruns 1-4 and 5-11 once, warm melds after it run neither; a lost provider raises the first meld's error; a notch to a version whose `__init__` cannot be resolved raises the first meld's UnresolvedInputError; a consumer lent to a second Book follows in both with one rebuild |
| 5 | unit: a `valid` consumer's gate pass makes no lookup, no walk and gates no verdict; component: warm melds count no 5-11 pass and no refresh |
| 6 | unit: a contract with a mixed-case binding name is marked by the provider copy's key; the registry's recorded key equals `Spell._key` |
| 7 | review of each mutator's lock span and the notch's call site; component: melds racing notches and index destroys, GIL off |
| 8 | the probes before and after (us per warm meld; passes and refreshes per change); the walk's time for a notch with many dependents |
| 9 | component: the lost-provider meld raises SpellbookValidationError naming the contract; a dependent of a broken refresh raises naming the dependency; the class-annotation case raises UnresolvedInputError naming the parameter |
| 10 | unit (real registry): chain and cross-Book walks, both flags, idempotency, a contract cycle, the key's lifecycle, the walk-on from `mark_contract_dependents_dirty` |
| 11 | component, both GIL modes: probe C1-C4 and X1 as regressions (a dependent follows warm, cold and P-first; across Books the dependent, the consumer and the lender's provider follow; the link regression) |
| 12 | unit with lock doubles: no lock across the walk, one dependency's window and lock per refresh, the dependent's taken after |

## Risks
- The scan's removal without the marking breaks follow (measured 2026-10-15), and the walk without the catch-up
  strands a dependent two hops away (probe "closure" mode): all land together.
- A Book's flag stays up while one of its marked lineages is pending - neither melded nor refreshed by a dependent's
  catch-up - so its warm melds take the gate meanwhile: about 15-16 us instead of 0.3-0.7 us (rule 1's measurement,
  0.2.8247). It comes down as they revalidate (the probe's chains end with the flag down). A Book that borrows copies
  it never resolves keeps its flag up for that reason already, before any notch (probe X1).
- The catch-up drains a stale dependency's index gate, as that dependency's own rebuild does: a constructor that melds
  a spell whose stale dependency it is itself building waits for itself and hits the 30 s drain timeout (the failure
  mode recorded for rebuild windows on 2026-09-26).
- A borrower's meld thread runs a lender's spell's phases 1-4 for the first time. They take no Book lock and read the
  owner Book's pool through a one-call copy; the registry keeps one topology per lineage, the one every Phase 8 reads.
- The notch's walk holds the registry lock for its whole closure, with one RiskManager callback per changed state
  (O(closure x Books) key lookups). A notch is a cold path; the time for a large fan-out is measured in the build.
- The walk also marks the consumers of an impacted key in Books that do not borrow that lineage; they are already
  `gated` for want of a provider, so the mark publishes nothing.
- Grant marks twice (the mutator, then `_invalidate_contract_consumers`); the second `set_validity` finds the lineage
  `gated` and publishes nothing.
- A mark that raises (a cleaned registry while its Book is live) propagates after the map change, as the collection
  mark in `_add_contracted_spell` already does.
- Pre-existing, unchanged: structural validity is per lineage, frame-wide, while contract presence is per Book, so
  a lineage melded through two Books holds the verdict of the last Book that reran Phase 4; and a consumer lent to a
  second Book keeps building the old provider there when only that Book loses its provider (probe L3, L4; D4).

## Ticket coverage
- Task: TASK-2026-10-16-recheck_contract_consumers_when_provider_changes (standalone).

## Unknowns and decisions
- UNKNOWN: none in the design; each claim is a source read or a probe run recorded in the ticket.
- Decided by the owner (chat 2026-10-16):
  - D1: B - SpellbookValidationError shows the gating SPELL_CONTRACT_MISSING_PROVIDER warning, with its remedy, as
    the spell's reason (component_patch_contract_presence_report.md);
  - D2: the dependency notch is part of rule 2 - a notch flags for revalidation every spell that depends on the
    notched one (component_patch_dependent_walk.md, component_patch_meld_gate.md);
  - D3: a notch back makes the borrower's parked copy of the incoming version usable again and marks its consumers;
    built objects are untouched (component_patch_notch_reactivation.md);
  - D4: a lent consumer's Book-local provider loss is investigated in its own task
    (TASK-2026-10-16-investigate_lent_consumer_provider_loss, backlog);
  - D5: the landing waits for melder_0: spellbook.py and transfer_of_ownership.py were released at 2026-10-16T12:33:09Z;
    conduit.py stays with melder_0's TASK-2026-10-16-public_notch_target_for_staged_versions until it lands, so
    D3's conduit.py lines come last.
- APPROVED by the owner (chat 2026-10-16): the patch as a whole and the migration order above; the build started on
  every file but conduit.py.

## Context / Handoff Summary
- What changed: the patch is written and carries the owner's decisions D1-D5; nothing in `src/` yet.
- What remains: the build (approved 2026-10-16; conduit.py after melder_0's HANDOFF).
- Next entrypoint: component_patch_borrower_contracted_maps.md, then component_patch_dependent_walk.md.
