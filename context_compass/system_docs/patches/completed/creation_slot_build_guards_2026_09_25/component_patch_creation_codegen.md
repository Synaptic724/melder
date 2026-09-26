# component_patch_creation_codegen

## Metadata
- Patch ID: creation_slot_build_guards_2026_09_25
- Component: Creation runtime doors and plan-step emitters (codegen_creation_system)
- Status: promoted to src_architecture and src_components 2026-09-25; archived
- Owner: user (implementation: melder_0)
- Created: 2026-09-25T22:50:59Z
- Updated: 2026-09-25T23:28:41Z

## Component Purpose and Boundary
- Current boundary: emits door and plan-step source that holds the target store's lock across the
  whole build for slotted non-unique existences.
- Target boundary: identical emitted shape, with the slot guard in place of the store lock.

## Before/After Behavior Summary
- Before: `with store._lock: recheck; build; register` for unique_per_conduit, unique_per_spell_space,
  lineage and cluster (doors and steps). Manifest steps write the dicts directly; manifest
  disposal-bearing many appends with no lock.
- After: `with store.slot_guard(spell_id): recheck; build; register` for those existences;
  registration always goes through `add_creation`/`add_many_creations` (self-locking). Unique
  branches are unchanged (Spell._lock, brief store touches). `many` is unchanged except the manifest
  many append now takes the store lock through `add_many_creations`.

## Interface Deltas
- Inputs/Outputs: unchanged executor signatures; `(instance, created)` hook contract unchanged.
- Error semantics: unchanged, except the cleaned-store publish error from Creations.

## State and Lifecycle Deltas
- None. Emitted executors hold no new state.

## Failure Mode Deltas
- Removed: deadlocks listed in the architecture patch.
- Removed: manifest many first-use bucket race.

## Dependency and Ordering Constraints
1. Requires Creations.slot_guard and self-locking publish (component_patch_creations.md).
2. Requires cache version 10 so no previously emitted executor is reused.

## Validation Expectations
- Every emitter path (generalized fresh + manifest/hydrated, overrides, many_only, solo via doors)
  exercised by existing suites; the regression file covers doors, nested steps and purge.

## Unknowns and Open Decisions
- UNKNOWN: none blocking.

## Context / Handoff Summary
- What changed: store lock -> slot guard at every build-once site.
- Remaining risks: an emitter site missed by the read pass (mitigation: grep after edit for any
  `_lock:` that spans a construct).
- Next entrypoint: the task PLAN note.
