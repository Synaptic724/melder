# component_patch_spellcompiler_site_plans

## Metadata
- Patch ID: nested_slot_guard_2026_09_26
- Component: SpellCompiler and Validation Pipeline (site-plan lowering and runtime)
- Status: draft
- Owner: user (implementation: melder_2)
- Created: 2026-09-26T21:48:30Z

## Before/After Behavior
- Before: every shared site's miss, the root's included, builds its children, then takes its slot guard (the
  Spell lock for unique with the hint), rechecks, constructs and publishes. When a route door calls the normal
  plan it already holds the root's guard, so the root miss re-enters it.
- After: in the normal plan emitted for a door route of "unique_per_conduit" or "spellspace" whose root has the
  matching existence, the root miss builds its children, rechecks, constructs and publishes without a "with"
  block; it relies on the door's guard. Every other site, every override plan, and every other root keep their
  guard. The generalized hydrator passes its manifest route key; the many_only hydrator passes none (all-many
  roots take no guard).

## Interface Deltas
- SitePlanLowering.emit(..., normal_mode=False, door_route_key=None)
- SitePlanEmission(..., normal_mode=False, door_route_key=None)
- SitePlanOverrideRuntime(..., door_route_key=None); only _compile_normal_plan reads it.

## State / Failure Deltas
- None observable. The RLock's recursion depth during the root's construction is 1 instead of 2.
- Store cleaned during a door-called build (a caller contract violation): today the plan fails with
  AttributeError at its root guard read; after, it fails with AttributeError at its root recheck read. Both are
  before the root is constructed; a cleanup during the root's own construction behaves as before.

## Dependency / Ordering
- melder_0 owns these files (NOTICE M2-8). The door compiler and creations.py are not changed.

## Validation Expectations
- Unit (new file): door-held root takes no guard while its children still take theirs; lineage, cluster and
  unique roots and a runtime without a route key keep the root guard; override plans keep it; the root recheck
  returns an instance published during a child's construction.
- Integration (new file): N threads first-meld one unique_per_conduit root on one conduit and one
  unique_per_spell_space root in one shared SpellSpace: one construction, one instance; a created hook fires
  exactly once; a nested same-thread override meld of the root is returned by the outer meld.
- Suites: spellbook, conduit, multithreading (lock-order deadlock), purge, specialization on 3.14t and GIL.

## Documentation Deltas (on promotion)
- src_components: Creations and SpellSpace ("Slot build guards"), Meld Resolution Runtime (Concurrency),
  SpellCompiler and Validation Pipeline (Normal plan, Emission).
- src_architecture: Operational Invariants ("Creation build locks"), Sequence: Meld Resolution step 4,
  Context / Handoff Summary.
