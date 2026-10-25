# component_patch_creations_and_spellspace

## Metadata
- Patch ID: creations_store_slots_by_binding_2026_10_25
- Component: Creations and SpellSpace (`src/melder/aether/conduit/creations/creations.py`; docstrings of
  `conduit_creations.py` and `cluster_creations.py`)
- Status: draft
- Owner: Mark
- Author: melder_3 (synaptic_python_developer)
- Created: 2026-10-25T10:55:14Z
- Updated: 2026-10-25T10:55:14Z

## Component Purpose and Boundary
- Current boundary: one `Creations` is the live-object store of one scope. It files every object, disposal record,
  slot guard and managed pool by spell_id; a slot's shape is read from the Spell that asks (`purge`, the doors'
  probes) or from the stored value (`extract_spell_creations` tests `isinstance(value, list)`). Meld selects the
  store; the store neither discovers scopes nor authorizes callers.
- Target boundary: the same store, filing objects, records and slot guards by store key (`Spell.store_key`), with a
  per-spell_id shelf of the keys it has filed and each key's shape. Store selection and authority stay with Meld;
  the managed pools stay keyed by spell_id.

## Before/After Behavior Summary
- Before: two bindings of one class (a rebind after `cleanup_spell` keeps the spell_id since 0.2.8257) share one
  entry. `register_many` appends a new binding's objects under the first registration's disposal list (S1) or onto
  an old slotted object (S2: AttributeError after the object is built; or that object's own `append`); a slotted
  read returns the old list or object (S3-S5); `purge` takes the shape from the asking spell (S6 TypeError, S7 count
  1 for 2 objects); a probe reads the asking binding's shape (S8, S9).
- After: each binding files under its own key, so its slot, record and shape are its own; the objects of a removed
  binding stay in their slot until the store ends and are disposed with their own record. `purge`,
  `count_spell_creations` and `extract_spell_creations` walk the spell_id's shelf and read each slot's recorded
  shape. A binding filed again under the same key (a same-binding rebind) meets its slot.

## Interface Deltas
- Inputs: `add_creation(key, ...)`, `add_many_creations(key, ...)`, `register_many(key, ...)`, `get_creation(key)`,
  `slot_guard(key)` take a store key; their parameter is renamed `key` where it was `spell_id`. `purge(spell, ...)`
  reads `spell.spell_id` (its shelf) and `spell.store_key` (its build guard); `extract_spell_creations(spell_id)`
  and `restore_spell_creations(spell_id, rows)` keep their signatures.
- New: `register_slot(key, item) -> None` - publish one slotted object without disposal methods; the caller holds the
  slot's build lock and has rechecked the slot (the emitted plans' contract), so it checks neither duplicates nor
  `_cleaned`, as the inline store it replaces did not. `count_spell_creations(spell_id) -> int` - the objects every
  binding of the spell_id holds in this store: a `many` slot's length plus one per other slot whose value is not
  None.
- Outputs: purge's count is every object detached from the shelf (each `many` slot's length, one per other slot).
  Extract rows gain `"key"` (the store key of the slot the row came from); managed rows do not.
- Error semantics: removed - the AttributeError of `register_many` onto an old slotted object (a key names one
  binding, so one shape) and purge's TypeError. Kept - the ValueErrors of `add_creation` (a key already filed) and
  `add_many_creations` (a non-list slot; a disposal declaration that disagrees with the key's entries), the
  RuntimeErrors of a cleaned store and of restore's shape checks; an ExceptionGroup gathers every disposal failure of
  a purge across all its slots.

## State and Lifecycle Deltas
- Owned state changes: `_slot_shapes: Dict[str, bool]` (store key -> True for a `many` list slot) and
  `_shelves: Dict[str, List[str]]` (spell_id -> store keys, in first-filing order). Both are written only under the
  store lock, when a key is first filed or a filing finds the other shape (a test or legacy key reused), and never
  shrink: they survive `clear_all`, `reset_for_pool` and `reset_for_pool_unlocked`, bounded by the keys ever filed
  here, like `_slot_guards`.
- Lifecycle/cleanup changes: `cleanup` deletes `_slot_shapes` and `_shelves` with the other live fields; teardown and
  the reusable clears keep walking `_disposable_creations` newest first, which now holds one record per binding.
  `restore_spell_creations` first drops, undisposed, every slot on the target's shelf (and the bare spell_id key),
  as it dropped the spell_id's entry before, then installs the rows.

## Failure Mode Deltas
- New failure mode: none. A key filed by a direct write to `_creations` (tests only) is on no shelf, so purge, the
  count and extract do not see it; every src writer goes through a noting verb.
- Removed failure mode: S1-S9 of the store probe.
- Changed failure mode: a single-object purge searches every slot on the shelf, so it retires an old binding's
  object too; slots of other bindings are detached without their build lock (only a removed definition builds
  them), so an old build still in flight publishes after the purge and stays, like any later registration.

## Dependency and Ordering Constraints
1. `Spell.store_key` lands first; every emitter and caller passes it where it passed the spell_id.
2. The shelf entry is written before the slot's first value, so no reader meets a live slot that is off its shelf.
3. A many slot's record and bucket are created in one critical section, as today; noting precedes both.
4. Managed rows of extract/restore keep the spell_id; only object rows carry keys.

## Validation Expectations
- Unit (new module `tests/unit/melder/aether/conduit/creations/test_creations_store_slots.py`): every writer notes
  its key and shape (both `add_creation` branches, `register_slot`, `register_many`, `add_many_creations`, restore);
  `count_spell_creations` over several slots (None and an empty bucket count 0); purge across slots - the count, each
  record's methods, newest slot first, a single object found in any slot; extract rows with keys and restore under
  them, replacing the target shelf; a row without a key; a key without ':'; shelves kept across `clear_all` and
  `reset_for_pool`, gone at `cleanup`.
- Component: S1-S7 through public melds, purge and teardown (the story's module).
- Existing tests that read the store by spell_id move to the store key.

## Unknowns and Open Decisions
- UNKNOWN: none.
- DECISION_REQUEST: none.

## Context / Handoff Summary
- What changed: the store contract above, drafted from creations.py on 0.2.8270.
- Remaining risks: a writer left on the bare spell_id files a slot its spell's shelf does not list; the grep at
  closure checks that no src writer is left.
- Next entrypoint: code_description_patch_creations_and_spellspace.md.
