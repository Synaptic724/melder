# architecture_patch

## Metadata
- Patch ID: creation_slot_build_guards_2026_09_25
- Status: promoted to src_architecture and src_components 2026-09-25; archived
- Owner: user (implementation: melder_0)
- Created: 2026-09-25T22:50:59Z
- Updated: 2026-09-25T23:28:41Z

## Patch Scope and Non-Goals
- Objective: remove the store-lock / Spell-lock deadlock between concurrent first resolutions (and
  purge) by giving build-once exclusion its own per-slot lock, so no thread ever holds a Creations
  store lock while waiting on another lock or running user code.
- Non-goals: moving `unique` off `Spell._lock`; the joint-alpha override optimization; changing which
  store an Existence routes to; restricting what users may compose; hook standardization.

## Changed-Components Matrix
| component | change_type | rationale | depends_on |
|---|---|---|---|
| Creations and SpellSpace (Creations store) | modify | owns slot guards, leaf publish, guarded purge | none |
| Meld Resolution Runtime (creation runtime doors) | modify | door build-once uses the slot guard | Creations |
| SpellCompiler codegen creation emitters | modify | plan steps use slot guards; register self-locks | Creations |
| CachingSystem | modify | version 10 rejects executors emitted with the old locking | none |

## Interface and Boundary Deltas
- Internal only. `Creations.slot_guard(spell_id) -> RLock` is new. `add_creation` and
  `add_many_creations` now take the store lock themselves and refuse a cleaned store.
- No public API change. Observable change: different slots in one store may now build in parallel
  (today the whole store serializes). Same-slot requesters still wait and still get one object.

## Cross-Component Invariants
- Slot: one (store, spell_id) pair whose Existence promises at most one object. Every slot has exactly
  one build lock: `unique` -> `Spell._lock` (a unique spell has one slot, its owner store); every
  other slotted Existence -> `store.slot_guard(spell_id)`. `many` has no slot and no guard.
- Store lock (`Creations._lock`) is a LEAF: held only around dict reads/writes (publish, many append,
  detach, swap). Never held while acquiring another lock, never around user code.
- Build locks are acquired consumer before provider along the dependency graph, which has no cycles,
  so no wait cycle can form. A wait cycle would require a circular dependency (rejected by validation;
  infinite recursion even on one thread).
- Warm path unchanged: an unlocked `dict.get` hit returns before any lock.

## Migration and Rollout Order
1. Creations: guard table, self-locking publish with cleaned check, guarded purge, cleanup tombstone.
2. Door compiler: 8 slotted route sites.
3. Plan-step emitters (generalized, many_only, manifest).
4. Cache version 10.
5. Regression tests flip; schema test table.

## Rollback Strategy
- Rollback trigger: a correctness regression in the existing suites or a measured cold-path cost the
  owner rejects.
- Rollback steps: revert the listed files; cache version 10 bundles are then rejected by version-9
  readers and rebuilt cold.
- Post-rollback verification: deadlock regression file returns to 7 strict xfails.

## Validation Expectations and Evidence Plan
- The 7 former DEADLOCK_CASES pass as SAFE on 3.14.7t and 3.14.7 GIL; the 4 SAFE cases still pass;
  new case unique -> many -> unique_per_conduit passes.
- Relevant existing suites pass (creations, meld, purge, spellspace, cluster, lineage, caching,
  multithreading) on 3.14.7t.
- Before/after benchmark of warm meld and cold build cycles (lesser per-request, spellspace cycle).
- Evidence: task MEASURE notes; artifacts/creation_slot_build_guards_20260925/.

## Ticket Coverage Map
- Epic: EPIC-2026-09-24-override-execution-performance
- Story: STORY-2026-09-25-verify-override-writer-and-contract
- Tasks: TASK-2026-09-25-implement-creation-slot-build-guards

## Unknowns and Decision Requests
- UNKNOWN: whether moving `unique` onto the store guard table is worth it (out of scope).
- Behavior note for owner review: a scope reset (`clear_all`) that races an in-flight build no longer
  waits for it; the finished object publishes into the reset store instead of being disposed with it.

## Context / Handoff Summary
- What changed: build-once exclusion moves from the store lock to per-slot guards.
- What remains: canonical doc merge after owner acceptance.
- Next entrypoint: component_patch_creations.md.
