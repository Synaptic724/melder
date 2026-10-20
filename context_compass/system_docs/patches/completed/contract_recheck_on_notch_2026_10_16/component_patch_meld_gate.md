# Component patch: the meld gate's recheck and catch-up (contract_recheck_on_notch_2026_10_16)

## Metadata
- Patch ID: contract_recheck_on_notch_2026_10_16
- Component: Meld (`src/melder/aether/conduit/meld/meld.py`): `_ensure_lineage_resolvable`,
  `_ensure_runtime_resolution_ready`, `_check_contracts_and_force_revalidation`, `_iter_spell_contract_defaults`,
  `_force_resolution_revalidation`; new `_refresh_stale_dependencies` and its helpers
- Status: active; D1 (B) and D2 (fold in) decided by the owner (2026-10-16)
- Owner: user; melder_1 (synaptic_python_developer) (patch, and writer of this file)
- Created: 2026-10-16T10:32:18Z
- Updated: 2026-10-16T12:57:39Z

## Component purpose and boundary
- Current boundary: the meld-time validation gate, entered by `ConduitMeld.meld` and `SpellSpaceMeld.meld` only
  while the Book's validation-required flag is up. It has three steps: rerun phases 1-4 for an `unknown` or
  `gated` lineage; for every spell with a SpellContract default, scan the signature, look each contract key up in
  the Book's active contracted maps (MeldExecutionError on a miss) and gate the conduit verdict; rerun phases 5-11
  for an `unknown` or `gated` conduit verdict. The deferred lane (`_ensure_runtime_resolution_ready`, entered from
  the doors for a spell flagged `resolution_required`) runs 8-11 or the full 5-11 pass. Neither looks at the
  structure of the dependencies a plan expands: a resolution pass reads each dependency's topology as that
  dependency's own last Phase 3 registered it.
- Target boundary: two steps, preceded by a catch-up wherever a plan is about to compile. The structural step is
  the contract recheck: it runs because a provider change marked the consumer `gated` + `contract_unvalidated`
  (component_patch_borrower_contracted_maps.md), and Phase 4's ContractProviderPresenceStrategy is the presence
  check. The catch-up refreshes the structure of every stale lineage the plan expands - the dependencies a notch's
  walk marked (component_patch_dependent_walk.md) - before the plan compiles.

## Before / after: the scan
- Before: every gated meld of a contract consumer reads `inspect.signature(call_target,
  annotation_format=Format.FORWARDREF)`, makes one `_resolve_contracted_by_lookup_key` call per contract and gates
  the conduit verdict (`contract_unvalidated`), so phases 5-11 rerun every time: 1470-1650 us a warm meld.
- After: `_ensure_lineage_resolvable` keeps its structural branch and its resolution branch and drops the call
  between them. A consumer whose lineage and verdict are `valid` passes with the two state reads every spell pays.
  A marked consumer reruns phases 1-4: a present provider makes the lineage `valid`, the branch gates the conduit
  verdict (`structure_changed`, as today) and phases 5-11 rebuild against the provider now active; a missing one
  leaves it `gated` and the branch raises `SpellbookValidationError([spell])`, the first meld's error (with D1-B it
  names the contract).
- `_check_contracts_and_force_revalidation` and `_iter_spell_contract_defaults` are deleted; the Phase 8 analyzer
  and the Phase 9 processor keep their own `_iter_spell_contract_defaults`. `_resolve_contracted_by_lookup_key`
  stays (purge and lookups use it).
- `_force_resolution_revalidation`: code unchanged; its docstring stops naming contract callers (the structural
  branch is its only caller and passes `structure_changed`; the default stays).
- `_ensure_lineage_resolvable`'s docstring: the contract bullet becomes "a SpellContract consumer is rechecked by
  the structural step when a change of its provider has marked it; a satisfied contract costs nothing per meld", and
  a bullet describes the catch-up.
- Imports: `from annotationlib import Format` and the `SpellContract` import leave meld.py (no other use);
  `inspect` stays (`_resolve_purge_spell` uses it).
- Comment: `ConduitWard._get_spell_contract_keys` says its signature read "Mirrors Meld._iter_spell_contract_defaults";
  it will name the Phase 8 analyzer's copy instead (the comment is updated, not removed).

## Before / after: the catch-up (D2)
- Before: a dependent two hops from a notch (Q -> P -> notched D) compiled P's stale topology: the lookup of D's
  parked version missed, the pass recorded a visibility failure that set Q and P `invalid` for the conduit, and the
  gate's resolution branch raises on an `invalid` verdict without rerunning, so Q stayed refused even after P was
  rebuilt (probe "closure" mode). Today, without the walk, Q kept building the old D.
- After: new private `Meld._refresh_stale_dependencies(spell)`, called
  - at the top of `_ensure_lineage_resolvable` when the spell may compile: its lineage is not `valid`, its effective
    conduit verdict (`_get_resolution_validity`) is not `valid`, or it carries `resolution_required`;
  - at the top of `_ensure_runtime_resolution_ready` when it carries `resolution_required`;
  in both places before the spell's own rebuild window and spell lock, with no lock held.
- The walk mirrors what the spell's resolution pass expands (Phase 5's scope, Phase 8's occurrences), starting from
  the spell's local topology in the registry (`get_local_topology_by_id`):
  - a NORMAL socket's target version ids, each mapped to its lineage's current version
    (`get_by_spell_id(target).current_spell_id`) and looked up in the pool of the Book whose pass compiles the plan
    (`spell._spellbook._spell_id_pool`; owned and contracted spells);
  - a SPELL_CONTRACT socket's key, resolved in that Book's active contracted maps as Phase 8 does
    (`_lookup_contracted_spells` then `_contracted_spells`), through one-call snapshots;
  - OVERRIDE_REQUIRED, UNRESOLVED_INPUT and AMBIGUOUS_INPUT sockets have no targets and are not followed.
  Each spell is visited once; a refreshed dependency is walked through its refreshed topology.
- A lineage is stale when its validity is `gated` or `unknown`; `invalid`, `disabled` and `cleaned` are left to the
  pass as today. A stale dependency is refreshed under its own rebuild window (dynamic ownership) and its spell lock,
  re-checked stale inside them (another meld may have refreshed it), with phases 1-4 against its owner Book
  (`dependency._spellbook`, the Book that compiled it):
  - broken -> its lineage `invalid` and `SpellbookValidationError([dependency])`, as the structural branch does;
  - not `valid` -> `SpellbookValidationError([dependency])` (a lost contract of the dependency is named, D1-B);
  - `valid` -> its own plan is reset, because it was compiled against the old structure: CreationContext cleaned,
    Phase 5+ artifacts cleared (`SpellCompilerSystem.clear_phase5_artifacts`), `resolution_complete=False`,
    `resolution_required=True`, door epoch bumped. Its next own meld, in any conduit, runs its full target pass
    (`_requires_own_target_pass`: no Phase 5 root) instead of serving the old plan.
- Then the gate continues for the spell itself as before.

## Interface deltas
- Inputs and outputs: none public. Removed (private): the two scan methods. Added (private):
  `_refresh_stale_dependencies(spell)`, `_iter_planned_dependencies(spell)`, `_refresh_dependency_structure(spell)`,
  `_may_compile(spell)`.
- Error semantics:
  - a meld of a consumer whose provider is gone raises SpellbookValidationError from the structural branch where the
    scan raised MeldExecutionError ("SpellContract could not be resolved. Missing contracted provider for key
    (frame_key=..., binding_key=...) on param ..."); a first meld with no provider already raised
    SpellbookValidationError; both are RuntimeError. A failing contracted lookup is no longer wrapped.
  - a meld of a dependent raises SpellbookValidationError naming a dependency whose refreshed structure is broken or
    not valid, where it recorded a visibility failure naming a parked version id and stayed refused;
  - a dependency whose refreshed structure no longer resolves a parameter (the kind rule does not select the new
    version for its annotation) gives the dependent the first meld's UnresolvedInputError naming that parameter, where
    the dependent silently built the old version (probe C4).

## State and lifecycle deltas
- The gate reads the same states and writes the same verdicts. The catch-up writes what a dependency's own meld
  writes when it reruns phases 1-4, plus the plan reset `flag_dependencies_without_own_plan` already uses
  (`resolution_required`, door epoch) and the artifacts' Phase 5+ clear.

## Failure mode deltas
- Removed: the per-meld signature read, lookup and rebuild of every contract consumer.
- Removed: a dependent two hops from a notch stays refused, or keeps building the old version (probe C1-C3, X1).
- Changed: the lost-provider error type, as above.

## Dependency and ordering constraints
1. The scan's removal lands with the Book marking in one notch; alone it stops consumers following their provider
   (measured 2026-10-15).
2. The catch-up lands with the dependent walk: without the walk nothing downstream is marked, so nothing compiles
   and the catch-up never runs; without the catch-up the walk strands a dependent two hops away.
3. The structural branch's `_force_resolution_revalidation(structure_changed)` stays: it is what rebuilds a spell
   whose structure revalidated after a mark.
4. Locks: the walk holds no lock (registry reads take and release the registry lock; Book maps are read through
   one-call snapshots). A refresh takes one dependency's rebuild window, then its spell lock, as that dependency's own
   meld does, and releases both before the next; the dependent's window and lock are taken only after the catch-up.
   So the catch-up nests no lock in another and adds no lock-order edge. Phases 1-4 take no Book lock (the gate runs
   them without one today) and read a Book's pool through a one-call copy (src_architecture, "Compiler pool reads").
5. A borrowed dependency is refreshed with its owner Book - the first time a borrower's meld thread runs a lender's
   spell's phases. Its structure is its owner's: the owner's conjure compiled it, and Phase 8 of every borrower reads
   the one topology the registry keeps per lineage.

## Validation expectations
- Unit (`tests/unit/melder/aether/conduit/meld/test_meld.py`): the three scan tests and the two
  `_iter_spell_contract_defaults` tests are replaced by: a `valid` contract consumer passes the gate with no
  contracted lookup and no verdict write; a `gated` consumer that Phase 4 validates gates its verdict with
  `structure_changed` and reruns resolution once; a `gated` consumer still `gated` after Phase 4 raises
  SpellbookValidationError and no MeldExecutionError.
- Unit (catch-up, doubles for the compiler system): a `gated` dependency is refreshed with its owner Book under its
  window and lock and its plan is reset (context cleaned, Phase 5+ cleared, `resolution_required`, door epoch); a
  `valid` one is not touched; a broken one raises SpellbookValidationError([dependency]) and goes `invalid`; one still
  `gated` raises naming it; no walk for a spell that will not compile; the walk holds no lock and a refresh holds only
  its dependency's window and lock (lock doubles); a contract socket follows the Book's active copy; a refreshed
  dependency is walked through its new topology.
- Integration: the first-meld tests that expect SpellbookValidationError for a missing provider stay green
  (`test_conduit_integration_spell_contract_variants.py`); new ones meld after a notch, an index destroy and an
  uncontract and assert follow or the first meld's error; the D2 regressions of component_patch_dependent_walk.md.
- The probes: a warm borrower contract consumer at about 2 us, no scan, one 5-11 pass per provider change; the chain
  follows with one refresh and one 5-11 pass, and the next melds take the fast door.

## Unknowns and open decisions
- UNKNOWN: none.
- Decided: D1 (B), D2 (fold in). Approved by the owner on 2026-10-16.

## Context / Handoff Summary
- What changed: written before any edit; the catch-up added for D2 (2026-10-16T12:22:44Z).
- Remaining risks: see the architecture patch.
- Next entrypoint: component_patch_contract_presence_report.md.
