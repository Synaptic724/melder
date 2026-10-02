# component_patch_creations_and_spellspace

## Metadata
- Patch ID: many_registration_trim_2026_10_01
- Component: Creations and SpellSpace
- Status: active
- Owner: user (agent fable_0)
- Created: 2026-10-01T01:08:13Z
- Updated: 2026-10-01T01:08:13Z

<!-- BEGIN ENTRY: "Creations: many registration and disposal shape" -->
## Component Purpose and Boundary
- Current boundary: `Creations` owns one scope's live registry (`_creations`) and its cleanup-only mirror
  (`_disposable_creations`); for a many key the mirror is a second list of `(object, methods)` tuples kept in
  step with the live list.
- Target boundary: unchanged ownership; for a many key the mirror is ONE `ManyDisposalBucket` whose `entries`
  IS the live list (aliased) and whose `methods` is the key's Spell-owned method list.

## Before/After Behavior Summary
- Before: `add_many_creations` -> `_append_many_locked` under `_lock`: cleaned check, live get, first-use list,
  isinstance, append; disposable get, first-use list, isinstance, append of a new tuple. ~204 ns standalone.
- After: `register_many(key, item, disposal_methods)` under `_lock`: cleaned check, one get, first use creates
  the list and the record, one append. ~104-111 ns standalone. `add_many_creations` keeps its signature, its
  non-list check and its no-disposal branch, and writes the same shape.
  EVIDENCE:
  - src/melder/aether/conduit/creations/creations.py:597-711
  - artifacts/many_registration_trim_20261001/vm_register_many_shapes_gil0_20261001.md:1-16

## Interface Deltas
- Inputs: `register_many(key: str, item: object, disposal_methods: List[str]) -> None` (new, internal, called
  by emitted plans and executors). Precondition: the key's Existence is `many` and declares disposal methods;
  `disposal_methods` is the Spell-owned list (identical for every registration of the key).
- Outputs: none; `get_creation` and the live bucket shape (`spell_id -> list[object]`) are unchanged.
- Error semantics: a cleaned store raises RuntimeError after running the object's methods (unchanged);
  `add_many_creations` raises ValueError on a non-list slot (unchanged) and on a disposal declaration that
  disagrees with the key's existing entries (new, fail-fast for the public verb); `restore_spell_creations`
  raises RuntimeError when the rows of one many key disagree on `disposable` (new).

## State and Lifecycle Deltas
- Owned state changes: `_disposable_creations[key]` for many keys holds a `ManyDisposalBucket` (a plain
  `__slots__` class in creations.py: `entries` borrowed from the live registry, `methods` borrowed from the
  Spell); no new field on `Creations`, `__slots__` unchanged.
- Lifecycle/cleanup changes: none in order or aggregation; `cleanup`/`clear_all` swap both maps as before and
  the detached record's `entries` keeps the objects alive until disposal ran.

## Failure Mode Deltas
- New failure mode: mixed disposal declarations for one many key are refused (ValueError on the public verb,
  RuntimeError on restore) instead of being carried as sparse metadata.
- Removed failure mode: none.
- Changed failure mode: none; the refusal after cleanup, the ExceptionGroup texts and the per-method errors
  are byte-identical.

## Dependency and Ordering Constraints
1. The store lands before the emitters (an emitted `register_many` needs the verb); both land in one change
   set with the generation bump.
2. `_detach_single_many_creation` needs no second search: removing the object from the live list removes it
   from the record, and the returned disposal entry is `(creation, record.methods)`.
3. `extract_spell_creations` rows keep `disposal_methods` per row (the record's list), so transfer and
   lesser-creations readers are untouched.

## Validation Expectations
- Test/validation item 1: unit - registration shape, first-use record, newest-first disposal with the key's
  methods, failure aggregation, purge all/single (order of the remainder, both keys removed when empty),
  extract/restore round trip (order and methods), mixed-declaration refusals, cleaned-store refusal.
- Evidence target 1: tests/unit/melder/aether/conduit/creations/ (new file plus the regression files).
<!-- END ENTRY: "Creations: many registration and disposal shape" -->

## Unknowns and Open Decisions
- UNKNOWN: none.
- DECISION_REQUEST: the hot verb carries no non-list check (impossible by construction: one Existence per
  Spell); the owner confirms or asks for the check (+10-15 ns).

## Context / Handoff Summary
- What changed: nothing yet; the edit is defined above.
- Remaining risks: a test that pinned the tuple shape of `_disposable_creations`; those files are listed in
  the task and change with the shape.
- Next entrypoint: the task's mapping note, then the owner's confirmation.
