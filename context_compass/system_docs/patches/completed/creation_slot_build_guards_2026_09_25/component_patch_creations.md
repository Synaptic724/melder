# component_patch_creations

## Metadata
- Patch ID: creation_slot_build_guards_2026_09_25
- Component: Creations and SpellSpace (Creations store)
- Status: promoted to src_architecture and src_components 2026-09-25; archived
- Owner: user (implementation: melder_0)
- Created: 2026-09-25T22:50:59Z
- Updated: 2026-09-25T23:28:41Z

## Component Purpose and Boundary
- Current boundary: scoped live-object registry; its RLock guards both dicts AND is borrowed by
  generated code as the build-once mutex across whole constructions.
- Target boundary: registry plus a per-slot build-guard table. The store lock guards only the dicts.

## Before/After Behavior Summary
- Before: `add_creation` relies on the caller's store lock; generated doors and steps hold the store
  lock across construction; purge of non-unique slots takes only the store lock.
- After: `slot_guard(spell_id)` returns one RLock per spell id (created on first use, kept until
  cleanup). `add_creation`/`add_many_creations` publish under the store lock and refuse a cleaned store.
  Purge of unique_per_conduit / unique_per_spell_space / lineage / cluster slots takes the slot guard
  first, so it waits for an in-flight build of that slot exactly as unique purge waits on Spell._lock.

## Interface Deltas
- Inputs: new `slot_guard(spell_id: str) -> RLock`.
- Outputs: unchanged.
- Error semantics: publishing into a cleaned store disposes the new object (when it declared disposal
  methods) and raises RuntimeError instead of writing into a retired registry.

## State and Lifecycle Deltas
- Owned state changes: `_slot_guards: Dict[str, RLock]`.
- Lifecycle/cleanup changes: cleanup deletes `_slot_guards`; `_lock` is retained as a documented
  tombstone so a racing publish can observe `_cleaned` under it.

## Failure Mode Deltas
- Removed failure mode: store-lock / Spell-lock deadlock (7 regression shapes).
- New failure mode: none intended; a build racing store cleanup now raises instead of returning an
  object that cleanup disposes.
- Changed failure mode: a build racing `clear_all`/`reset_for_pool` publishes into the fresh store.

## Dependency and Ordering Constraints
1. Lock order is slot guard (or Spell._lock) -> store lock; never the reverse.
2. The store lock is never held while calling user code or acquiring another lock.

## Validation Expectations
- Deadlock regression file: all shapes SAFE. Purge component tests pass. Pool tests pass.
- Evidence target: tests/integration/melder/multithreading/test_multithreading_meld_lock_order_deadlock.py

## Unknowns and Open Decisions
- UNKNOWN: none blocking.

## Context / Handoff Summary
- What changed: build-once exclusion moved to slot guards; publish self-locks.
- Remaining risks: none known beyond the reset-race behavior note.
- Next entrypoint: code_description_patch_creations.md.
