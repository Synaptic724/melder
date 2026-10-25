# architecture_patch

## Metadata
- Patch ID: creations_store_slots_by_binding_2026_10_25
- Status: draft
- Owner: Mark
- Author: melder_3 (synaptic_python_developer)
- Created: 2026-10-25T10:55:14Z
- Updated: 2026-10-25T10:55:14Z
- Ticket: STORY-2026-10-25-creations_store_slots_by_binding (the owner's go, chat 2026-10-25 04:00 MDT, for the
  shelf/slot design he was shown at 03:58 MDT)

## Patch Scope and Non-Goals
- Objective: a Creations store files objects by store key, not by spell_id. A Spell's store key is
  `<spell_id>:<binding_hash>` (new `Spell.store_key`, fixed at construction), so each binding of one class has its own
  slot, disposal record and shape. The store also keeps one shelf per spell_id: the store keys it has filed under
  that spell_id, each with its shape (one object, or a `many` list), recorded when the slot is first filed.
  - Everything that files or reads ONE slot uses the store key: the emitted site plans, doors, solo templates and
    the opt-in specializer (the key bound as a constant where the spell_id was), the add and register verbs' callers,
    the slot guards, existing-object registration and `meld_existing_spell`.
  - Everything that acts on the SPELL walks its spell_id's shelf in the store the door selects today: purge (by
    spell_id or any selector), `has_live_creation` and `describe_live_creation_status`, and extract/restore
    (ownership transfer, contract invalidation, lesser upgrade). Counts come from what is stored and its recorded
    shape, never from the asking spell's existence; each slot is disposed with its own record.
  - A rebind under the same binding gets the same key and meets its slot (the 2026-10-03 rule stands). A rebind
    under another binding starts with an empty slot; the old binding's objects stay alive in their store until it
    ends and are disposed then with their own methods.
  - Managed pools stay keyed by spell_id. The creation cache moves to generation 25.
  - Fixes S1-S9 of the store probe (STORY-2026-10-25-creations_store_slots_by_binding, FACT note): wrong disposal
    methods (S1), a failed meld that loses its object (S2), the old list or object returned (S3-S5), purge's TypeError
    and miscount (S6, S7), probes that read the asking binding's shape (S8, S9).
- Non-goals: S3's binding-change verb and revalidation marks (STORY-2026-10-18-revalidate_on_binding_change, parked);
  teardown order per object across keys (Fix B, probe S10 and S11; not approved); reaching an object filed in a
  store the asking spell's existence does not select (an old existence's object in another store stays there and
  ends with that store); any change to how a spell_id or binding hash is computed, to lookup, to the doors' store
  selection or purge authority, or to managed pools; any disposal on `cleanup_spell` (the owner's rulings of
  2026-10-03 and 2026-10-14: Melder disposes nothing because a definition was removed).

## Changed-Components Matrix
| component | change_type | rationale | depends_on |
|---|---|---|---|
| Binding Pipeline - Spell (`src/melder/aether/spellbook/spell.py`) | modify | `Spell.store_key`, built after the binding manifest, kept after cleanup | none |
| Creations and SpellSpace (`creations.py`; docs of `conduit_creations.py`, `cluster_creations.py`) | modify | slots by store key; the shelf index; `register_slot`, `count_spell_creations`; purge and extract/restore over the shelf | Spell |
| SpellCompiler and Validation Pipeline (site plan, door compiler, specializer, generalized helpers, solo templates) | modify | bind the store key where a store slot was keyed by the spell_id; the no-disposal slotted publish calls `register_slot` | Spell, Creations |
| Spellbook Core - CachingSystem (`src/melder/utilities/caching_system/caching_system.py`) | modify | generation 25, "creation_store_slots_by_binding" | SpellCompiler |
| Meld Resolution Runtime (`conduit_meld.py`, `spellspace_meld.py`; docs of `meld.py`) | modify | the probes count the shelf; `meld_existing_spell` reads its binding's slot | Creations |
| Conduit Runtime (`src/melder/aether/conduit/conduit.py`) | modify | `_register_to_creations` files under `spell.store_key` (melder_1 holds conduit.py: its OK first) | Spell, Creations |

code_description_patch_creations_and_spellspace is required: noting a slot on its shelf has a lock-free caller (the
no-disposal publish), purge retires several slots under one build lock, and restore replaces a shelf; their order
and error semantics are the contract. Ownership transfer, contract invalidation and the lesser upgrade change no
code: they extract and restore by spell_id, which now moves the whole shelf.

## Interface and Boundary Deltas
- New: `Spell.store_key` (str, `f"{spell_id}:{binding_hash}"`; 129 characters for a SHA256 spell_id), a plain slot
  read like `spell_id`. No new public verb on Conduit, Spellbook or a Meld door.
- Creations (internal): `_creations`, `_disposable_creations` and `_slot_guards` are keyed by store key;
  `_managed_quantities` stays keyed by spell_id. New owned state `_slot_shapes` (store key -> True for a `many` list)
  and `_shelves` (spell_id -> the store keys filed under it, in first-filing order). New `register_slot(key, item)`
  (the publish the emitted code inlined as `store._creations[sid] = v`) and `count_spell_creations(spell_id)`.
  `add_creation`, `add_many_creations`, `register_many`, `get_creation` and `slot_guard` take a store key.
  `purge(spell, ...)` retires every slot on the shelf of `spell.spell_id`. `extract_spell_creations(spell_id)` returns
  the whole shelf, each row with its `"key"`; `restore_spell_creations(spell_id, rows)` replaces the target's shelf
  and installs each row under `row.get("key", spell_id)`.
- Meld doors (no signature change): `describe_live_creation_status`'s `creation_count` and `is_live`, and therefore
  `has_live_creation`, count every binding's objects on the shelf in the store the door selects;
  `meld_existing_spell` returns the asking binding's object or raises "not live", as a meld would build anew.
- Errors removed: the AttributeError of a meld after a slotted spell was rebound as `many` (S2) and purge's TypeError
  (S6). No error added.
- Cache: generation 25; every older bundle is cold once (a release change already cold-starts it, generation 9).

## Cross-Component Invariants
- One store key, one binding, one shape: a key is fixed by its Spell's binding (existence and disposal order among
  it), so two bindings never share a slot and a slot never changes shape. A key without ':' (test and legacy keys)
  is its own shelf.
- Every live slot is on its spell_id's shelf: the shelf entry is written under the store lock before the slot's
  first value, and kept for the store's life - across `clear_all` and `reset_for_pool`, like the slot guards; only
  `cleanup` removes it. A reader filters the shelf by what `_creations` holds now.
- A meld reads and writes only its own binding's slot, through a key bound as a constant; no warm meld reads a
  shelf, and a warm `many` registration does no shelf work.
- Operations on a spell see every slot on its shelf in the selected store and count what each slot holds: a list's
  length for a `many` slot, one for any other stored value (purge), or one for a value that is not None (the probes,
  as today).
- Each slot is disposed with its own record at teardown, a reusable clear and purge; a slot's `many` objects
  newest first.
- No new lock and no new lock-order edge: noting runs under the store lock, a leaf, and takes nothing under it;
  purge takes the asking definition's build lock (`Spell._lock`, the slot guard of its store key, or none for
  `many`) then the store lock, as today.

## Migration and Rollout Order
1. These patch docs, linked from the story; the mapping note (patch section -> code -> test).
2. Red tests on 0.2.8270: a component module for S1-S9 and the contracts around them, unit tests for the shelf and
   the store key, emitter tests for the bound keys; the task module's four strict xfails.
3. `Spell.store_key`; Creations; the emitters; the Meld probes and `meld_existing_spell`; `conduit.py` on
   melder_1's OK; generation 25 after melder_1's 24.
4. The tests that read a store by spell_id moved to the store key; the red tests green; the task module's markers
   removed; the unit, component and integration suites the GIL off and on; the warm-meld benchmark.
5. src_architecture, src_components, the graph's descriptors and assembly, the tests pair, their indexes; the
   running release note; the next free notch.
6. Closure; the rebuild last.

## Rollback Strategy
- Rollback trigger: the owner redirects, a warm meld measures slower beyond noise, or a suite cannot go green without
  weakening a contract above.
- Rollback steps: revert the source, the tests and the docs. Stores are in memory and bundles of generation 25 are
  cold to older code by the release change, so nothing persisted needs migrating back.
- Post-rollback verification: the suites green on the reverted tree, the GIL off and on.

## Validation Expectations and Evidence Plan
- `tests/component/melder/aether/conduit/test_conduit_component_store_slots_by_binding.py`: S1-S9 with their new
  answers, the same-binding slot (2026-10-03), `meld_existing_spell` and the fast meld door after a rebind, an
  ownership transfer moving every binding's objects; and
  `test_conduit_component_rebind_while_old_objects_are_alive.py` with its markers removed.
- Unit: the shelf (noting from every writer, counts, purge across slots, extract/restore rows and replacement,
  legacy keys, kept across clears, gone at cleanup); `Spell.store_key`; the emitters bind store keys.
- The unit, component and integration suites, `-X gil=0` and `-X gil=1`.
- Warm-meld benchmark on 0.2.8270 and on the fix: `unique`, `unique_per_conduit`, a disposal-bearing `many`, and a
  spellspace cycle that builds a `unique_per_spell_space` object each time.
- Evidence: the runs in artifacts/creations_store_slots_20261025/, cited from the story's Notes.

## Ticket Coverage Map
- Epic: none (standalone; it lands S3's store requirement)
- Story: STORY-2026-10-25-creations_store_slots_by_binding
- Tasks: none (a story-level lane). TASK-2026-10-25-rebind_while_old_objects_are_alive_tests (closed) gave the first
  red tests.

## Unknowns and Decision Requests
- UNKNOWN: none blocking. The benchmark's numbers are measured at step 4.
- Consequence of the approved design, stated for the owner: while a class rebound under another binding has not
  built yet and the old binding's object is alive in the store, `has_live_creation` answers True (it counts the
  spell) and `meld_existing_spell` raises "not live" (it answers for the binding a meld would build). And an existing
  object bound again under another binding while its first filing is alive is filed under both keys and disposed
  with both lists at the store's end (today the second filing fails with a logged ValueError); see
  component_patch_conduit_runtime.md.
- DECISION_REQUEST: none. Fix B waits for the owner's word.

## Context / Handoff Summary
- What changed: the patch, drafted from the code on 0.2.8270 (the working tree).
- What remains: steps 2-6 of Migration and Rollout Order.
- Next entrypoint: component_patch_creations_and_spellspace.md and code_description_patch_creations_and_spellspace.md.
