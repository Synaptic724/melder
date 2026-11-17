# component_patch_crystal_analysis

## Metadata
- Patch ID: crystal_world_reuse_2026_11_17
- Component: crystal_analysis (`CrystalAnalyzer`, `ModuleAnswerCache`, `CrystalAnalysisResult`,
  `SitePackageCustodyStrategy`)
- Ticket: https://github.com/Synaptic724/melder/issues/331
- Status: implemented at 0.2.8305; merged into the canonical system docs
- Owner: Mark (accountable); melder_0 (synaptic_python_developer)
- Created: 2026-11-17T11:00:00Z
- Updated: 2026-11-17T11:15:23Z

## Component Purpose and Boundary
Unchanged boundary: the analyzer walks a spell module's world at bind time and hands the crystal a result. This
patch lets it hand over a copy of a world it already walked, and makes the walk that remains cheaper.

## Before/After Behavior Summary
- Before (0.2.8304): every bind walked its world (about 150 modules for MelderOps): one stat per own-source module,
  a fact replay per module, a custody lookup per import edge, a leaf record per edge (about 870 records a bind),
  list scans per record, and the load-order finalize.
- After: a bind whose root world is unchanged copies the kept result (lookups only: no walk, no stat for loaded
  modules, no finalize). A walk that runs checks loaded modules by object and spec, records each leaf once, and
  finds membership in sets.

## Interface Deltas
- `ModuleAnswerCache`: `lookup_module_facts`/`store_module_facts` take an optional stat pair (None for a loaded
  module, whose spec is kept instead); new `lookup_world`/`store_world` and a `_MAX_WORLDS` bound.
- `CrystalAnalysisResult.load_described_payload(payload)`; membership sets beside the target lists.
- `SitePackageCustodyStrategy.site_root_signature()`.

## State and Lifecycle Deltas
- New class-level world map (LRU, 128 worlds); the analyzer gains a per-pass map of file guards for modules read
  without an object, emptied with the other per-pass answers.
- The result gains three set fields, created at init and deleted at cleanup.

## Failure Mode Deltas
- A world that cannot be validated cheaply (see the architecture invariants) is simply not kept or not reused.

## Dependency and Ordering Constraints
- The world is collected before the per-pass answers are emptied, and kept only after finalize, from the finished
  result's `describe()`.

## Validation Expectations
- A second bind of a spell from the same module walks nothing and records the same payload; a reload, a re-import,
  an edit of a module not imported, a change of `sys.path` and a change of a site root each force a walk.
- An edit of a loaded module without a reload keeps the earlier analysis (the new residual), until a reload.
- Leaf dedupe and the payload load give exactly the fresh payload.

## Unknowns and Open Decisions
- none

## Context / Handoff Summary
Implemented at 0.2.8305.
