# component_patch_creations

## Metadata
- Patch ID: remove_many_child_holder_ownership_2026_10_24
- Component: Creations store (`src/melder/aether/conduit/creations/creations.py`)
- Status: draft
- Owner: Mark (decision); melder_1 (executor)
- Created: 2026-10-24T20:06:55Z
- Updated: 2026-10-24T20:06:55Z

## Component Purpose and Boundary
- Current boundary: a store records live objects and their disposal values in three shapes - `(object, methods)`,
  `ManyDisposalBucket`, and since 0.2.8238 `HolderDisposalEntry` (a holder with the `many` children adopted into it).
- Target boundary: two shapes again - `(object, methods)` and `ManyDisposalBucket`.

## Before/After Behavior Summary
- Before: `adopt_children` moves a just-published holder's children out of their buckets into its record; whole-store
  disposal, `clear_all` and purge of the holder dispose the holder, then its children; extract/restore carry the
  children with the holder; a `many` purge or probe of the child's spell skips adopted children.
- After: no adoption; children stay in their spell's bucket in the store that recorded them; disposing a holder runs
  only its own methods; extract/restore move only the holder; the child spell's purge and probe see every child.

## Interface Deltas
- Inputs: `restore_spell_creations` rows carry no `children` key (a row with one is not produced any more).
- Outputs: `extract_spell_creations` unique rows carry no `children`; a holder without disposal methods extracts as
  non-disposable again.
- Error semantics: unchanged; disposal failures aggregate per method as before.

## State and Lifecycle Deltas
- Owned state changes: `_disposable_creations` holds tuples and buckets only.
- Lifecycle/cleanup changes: reverse-creation order within one store is unchanged; a child recorded in another
  store is disposed when that store ends.

## Failure Mode Deltas
- New failure mode: none in the store.
- Removed failure mode: none.
- Changed failure mode: a holder kept past the scope that recorded its child holds a disposed child (the owner's
  rule: the user's to handle).

## Dependency and Ordering Constraints
1. The emission change lands in the same change set (a miss would otherwise call the removed verb).
2. `_dispose_entry` keeps one dispatch for purge over the two shapes.

## Validation Expectations
- Test/validation item 1: purge of a holder runs only its methods; its children stay recorded until their store ends.
- Evidence target 1: integration and component runs, GIL off and on.

## Unknowns and Open Decisions
- UNKNOWN: none.
- DECISION_REQUEST: none.

## Context / Handoff Summary
- What changed: nothing yet.
- Remaining risks: tests or docs that still name the removed shapes; caught by a whole-tree search before landing.
- Next entrypoint: `Creations` class contract, `_dispose_disposable_registry`, `_dispose_entry`, extract/restore.
