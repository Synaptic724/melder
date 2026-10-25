# code_description_patch_meld_resolution_runtime

## Metadata
- Patch ID: probe_and_purge_reach_every_version_2026_10_25
- Component: Meld Resolution Runtime - the spell_id discovery of purge and the live-creation probes
- Status: draft
- Owner: Mark
- Author: melder_1 (synaptic_python_developer)
- Created: 2026-10-25T03:03:37Z
- Updated: 2026-10-25T03:03:37Z

## Trigger Justification
- Concurrency: the new read runs on a cold path that races a notch moving the same version between the Book's
  maps, and it takes the Book lock; its ordering against the other Melder locks is the contract.
- Error semantics: the KeyError text must stay identical for a spell_id no visible version carries.

## Control-Flow Description (Pseudocode Level)
1. `Meld._resolve_probe_target(*, spell, spell_name, spellframe, binding_name)`:
   - `spell` is a str (a spell_id): return `_resolve_visible_version_by_id(spell)`.
   - otherwise: return `_resolve_spell(spell=..., spell_name=..., spellframe=..., binding_name=...)`, unchanged.
2. `Meld._resolve_visible_version_by_id(spell_id)`:
   - try `_resolve_spell_by_id(spell_id)` - the unchanged lock-free read of the active pool, the active versions
     and each lender's active copies - and return its Spell.
   - on its KeyError: `visible = self._spellbook._find_visible_version(spell_id)`; None re-raises that KeyError
     (the same object, so the same text); otherwise return `visible`.
3. `Spellbook._find_visible_version(spell_id)`: `check_cleaned()`; under `self._lock`: `_spells_by_id`, then
   `_inactive_spells`, then for each lender `_contracted_spells_by_id[lender]` and
   `_inactive_contracted_spells[lender]`; the first hit is returned, else None. The lock is released on return.
4. `Meld._resolve_purge_spell`: unchanged up to discovery (cleaned check, `purge_all` type check, instance to
   class, `purge_all=False` needs an instance); discovery is `_resolve_probe_target`.
5. `ConduitMeld.describe_live_creation_status` and `SpellSpaceMeld.describe_live_creation_status`: discovery is
   `_resolve_probe_target`; the spellspace-request refusal (conduit door) and the status builders are unchanged.
   `Meld.has_live_creation` calls `describe_live_creation_status`, so it follows.
6. `ConduitMeld._get_purge_creations`, `Existence.unique`: when `spell._owner_creations` is None, raise the R6
   RuntimeError before reading the store's owner id; every other branch unchanged.

## Edge/Error and Rollback Semantics
- A spell_id of no visible version: KeyError "[MELD] No spell found with spell_id: <id>", re-raised from the
  active read, so the text, type and message are the ones callers see today.
- A version moved by a notch while the lookup runs: under the Book lock it is in exactly one of the four maps, so
  the locked read finds it - before the move in its old map, after it in its new one.
- A version disposed while the lookup runs (`cleanup_spell`): found before `_dispose_spell` takes it out of the
  maps, missed after (KeyError); not ordered, as for an active version (F16).
- An ownership transfer between its flip and its migration: the moving versions can be in neither Book (KeyError),
  as with `find_spell_by_spell_id`; after it, the target sees them and the source does not (F20).
- A cleaned Book: RuntimeError from `check_cleaned`; a cleaned Meld refuses first (`_resolve_purge_spell`).
- No rollback: the lookup reads only.

## Invariants and Idempotency Expectations
- The active path costs what it costs today: one Python call frame more on the doors that build nothing (the
  helper), no lock, and the same reads in the same order; a try block costs nothing until it raises.
- Lock order: the Book lock is taken alone - the Meld holds no lock when it calls the lookup, and the lookup takes
  nothing under the Book lock; the store, slot and spell locks of purge come after it is released. No new edge
  among Melder's own locks.
- User code: a `unique` constructor runs under its spell's lock, and Book teardown and conjure take spell locks
  under the Book lock. A constructor that probes or purges a parked spell_id while another thread tears its Book
  down could wait on both - the documented rule already forbids that ("quiesce melds before cleanup"), and
  `notch_spell` (`Spellbook._get_owned_spell`) takes the Book lock the same way from the same call sites.
- Idempotent: probes read only; a second purge of a version returns 0 (the store's rule, unchanged).

## Explicit Non-Goals
- No change to `_resolve_spell`, `_resolve_spell_by_id` or any meld door, cache or fast door.
- No change to `Creations.purge`, store selection, purge authority or the status payloads.
- No change to the Rift rooms, the static viewer or the capability room's meld.

## Validation Focus Points
- The race (integration): never KeyError for a version a notch is moving, the GIL off and on, from the lender and
  from an index-link borrower.
- R4 and R5 (component): the KeyError for an unknown, a disposed and a foreign spell_id; the meld doors' KeyError
  for a parked version.
- R6 (component): the RuntimeError for a `unique` version with no owner store, parked and active.

## Context / Handoff Summary
- What changed: nothing yet.
- Remaining unknowns: none in the control flow.
- Next entrypoint: `Meld._resolve_visible_version_by_id`.
