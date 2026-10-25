# code_description_patch_creations_and_spellspace

## Metadata
- Patch ID: creations_store_slots_by_binding_2026_10_25
- Component: Creations and SpellSpace (`src/melder/aether/conduit/creations/creations.py`)
- Status: draft
- Owner: Mark
- Author: melder_3 (synaptic_python_developer)
- Created: 2026-10-25T10:55:14Z
- Updated: 2026-10-25T10:55:14Z

## Trigger Justification
- Concurrency: the shelf is written from a lock-free caller (the no-disposal publish, `add_creation`'s first branch
  and `register_slot`) and from callers that already hold the store lock (`register_many`, `_append_many_locked`,
  restore); readers run beside them on free-threaded 3.14t.
- Multi-branch semantics: purge retires several slots under one build lock, for a whole spell or for one object, and
  aggregates their disposal; restore replaces a shelf before it installs rows.

## Control-Flow Description (Pseudocode Level)
1. Noting (`_note_slot(key, is_many)`, takes the store lock, re-entrant):
   - if the store is cleaned, return (the caller's write then fails or is dropped exactly as today);
   - if the key has no recorded shape: its shelf id is the text before the key's last ':' (the whole key when it has
     none); append the key to that shelf, creating the shelf;
   - record the key's shape (`_slot_shapes[key] = is_many`).
   Callers test first, without the lock: `_slot_shapes.get(key) is not <shape>`; only a key's first filing in the
   store (or a reused test key of the other shape) takes the noting path.
2. Writers note BEFORE they write the slot's first value:
   - `add_creation`, no disposal (lock-free): cleaned check, duplicate check, note(False), one dict store;
   - `add_creation`, with disposal (store lock): cleaned check, duplicate check, note(False), both registries;
   - `register_slot(key, item)` (lock-free, the emitted publish): note(False), one dict store;
   - `register_many` (store lock, explicit acquire/release): on the key's first registration in this store - the
     bucket absent - note(True), then the bucket and its record; every later call is today's dict read and append;
   - `_append_many_locked` (store lock): note(True) when it creates the bucket;
   - `restore_spell_creations` (store lock): note each installed key with its row's shape.
3. `count_spell_creations(spell_id)` (store lock, reads only): for each key on the shelf, read the slot; skip an
   absent slot and a value that is None; add a `many` slot's length or one.
4. `purge(spell, purge_all, creation)`:
   - cleaned check; a single purge needs a creation; a managed spell returns 0 (unchanged);
   - take the asking definition's build lock: `unique` -> `spell._lock`; `many` -> none; any other existence ->
     `slot_guard(spell.store_key)`;
   - under the store lock (`_detach_purge_entries(spell_id, ...)`), cleaned check again, then walk the shelf of
     `spell.spell_id` newest-filed key first:
     - whole purge: for each live slot pop the value and its record; count the slot's length (`many`) or one; keep
       every popped value and record;
     - single purge: the first slot that holds `creation` by identity - a `many` bucket searched entry by entry
       (`_detach_single_many_creation`), any other slot compared with `is` - gives up that one object and its record
       (a `many` record pairs it with the key's methods); nothing else moves;
   - release both locks; dispose each detached record with `_dispose_entry` in detach order; keep the detached values
     alive until then; raise one ExceptionGroup of every failure, else return the count.
5. `extract_spell_creations(spell_id)` (store lock): pop the managed pool row first (unchanged); then for each key on
   the shelf in first-filing order: a `many` slot gives one row per object (its record's methods on each when the key
   is disposal-bearing) and pops both maps; any other slot whose value is not None and not a dict (today's skip)
   gives one row and pops both maps; every object row carries `"key": key`. Unregister the pool after the lock.
6. `restore_spell_creations(spell_id, rows)` (store lock): drop every slot on the shelf (and the bare spell_id key)
   from both maps, undisposed; then for each row: a managed row as today; an object row goes under
   `row.get("key", spell_id)` with today's shape checks, noted before its first write. Pool registration and the
   replaced pool's cleanup after the lock, as today.
7. `cleanup()`: detach as today; delete `_slot_shapes` and `_shelves` with the other live fields.

## Edge/Error and Rollback Semantics
- A key noted and then never written (a failed build) stays on its shelf as an empty entry; readers skip it.
- A clear between a note and its write: the index survives, the write lands in one generation or the other, and the
  key stays indexed either way.
- `cleanup()` between a note and its write: noting returns early when it sees `_cleaned`; the write is refused, dropped
  with the detached map, or fails on the retired store's missing field, as today.
- Purge has no rollback: values are popped under the store lock and disposed after it; a disposal failure does not
  put a value back (unchanged).
- Restore that raises on a malformed row leaves the shelf dropped and the earlier rows installed (unchanged: today it
  dropped the spell_id's entry before the rows).

## Invariants and Idempotency Expectations
- Every key present in `_creations` was noted before it was first written there by a src writer.
- A key's recorded shape matches what it holds whenever it holds something.
- Noting is idempotent: a second note of a key with its shape changes nothing and takes no lock.
- Purge of a spell with nothing live returns 0 and changes nothing; a second whole purge returns 0.
- The store lock stays a leaf: noting, the count, purge's detach, extract and restore take no other lock under it.

## Explicit Non-Goals
- No shelf for managed pools (they stay one per spell_id in `_managed_quantities`).
- No per-object teardown order across keys (Fix B).
- No shrinking of the shelf index during a store's life.
- No reverse lookup from an object to its key.

## Validation Focus Points
- The first-filing race: many threads publishing different keys of one spell_id into one store - every key on the
  shelf once (the GIL off).
- A probe beside a publish: the count is consistent at each step (never negative, never a key twice).
- Purge across a `many`, a `unique` and a `unique_per_conduit` slot of one spell_id: one count, one ExceptionGroup,
  every method run.
- Warm paths unchanged: `register_many`'s second call and a slotted hit run no noting code (benchmark).
- Restore replacing a shelf: target slots of every binding dropped, rows installed under their keys.

## Context / Handoff Summary
- What changed: the store's control flow for keys and shelves.
- Remaining unknowns: none.
- Next entrypoint: the red tests (architecture_patch.md, Migration and Rollout Order step 2).
