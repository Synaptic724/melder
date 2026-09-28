# component_patch_meld_resolution_runtime

## Metadata
- Patch ID: meld_entry_cache_2026_09_27
- Component: Meld Resolution Runtime (and the `SpellSpace.meld` front door of Creations and SpellSpace)
- Status: draft
- Owner: user (implementation: fable_0)
- Created: 2026-09-27T21:39:56Z
- Updated: 2026-09-27T21:39:56Z

## Component Purpose and Boundary
- Current boundary: `Meld` owns one success-only warm registry, `_fast_meld_doors`, keyed by spell id and read
  by four readers (`ConduitMeld.meld`, `SpellSpaceMeld.meld`, `Conduit.meld`, `SpellSpace.meld`).
- Target boundary: `Meld` owns a second registry, `_fast_input_doors`, keyed by registered name or class, minted
  by the two door subclasses on the same success arms and read by the two public front doors only.

## Before/After Behavior Summary
- Before: `Conduit.meld("Name")` forwards `meld(None, spell_name="Name")` to the door; `Conduit.meld(spell=Cls)`
  forwards `meld(Cls)`. Both take the door's else-branch: `_input_resolution_cache` (name/class -> id, capped
  2048), `_spell_id_pool`, the validity gates, the creation-context lane, the builder. No entry is minted.
- After: the door's else-branch computes `fast_input_key` (= `spell_name` when `spell`, `spellframe`,
  `binding_name` are None and `type(spell_name) is str`; = `spell` when `spell_name`, `spellframe`,
  `binding_name` are None and `isinstance(spell, type)`) and on the two success arms writes
  `self._fast_input_doors[fast_input_key] = (target_spell, creation_context, door_epoch_at_entry,
  target_spell.user_created_object is not None)`. `Conduit.meld` and `SpellSpace.meld`, when `spellframe`,
  `binding_name` and `spell_id` are None, `spell` is not None and the world is automatic, read that registry,
  apply the id lane's ladder and arms and return on a hit; a miss or a failed guard continues to the door
  exactly as today, which re-mints on success.

## Interface Deltas
- Inputs: none. Outputs: none. Error semantics: none; a hit never raises what the slow lane would not raise
  (a constructor error propagates as today; an unhashable `spell` is a miss).

## State and Lifecycle Deltas
- Owned state changes: `Meld._fast_input_doors` (plain dict, per-op atomicity, last-write-wins on racing
  first builds, registry-bounded cardinality per invariant I3).
- Lifecycle/cleanup changes: deleted in `Meld.cleanup`; cleared by the upgrade route beside `_fast_meld_doors`
  and `_input_resolution_cache`.

## Failure Mode Deltas
- New failure mode: none. A cleaned spell or context makes the guard read raise AttributeError, which is a miss.
- Removed failure mode: none.
- Changed failure mode: none.

## Dependency and Ordering Constraints
1. The entry captures `door_epoch_at_entry` read BEFORE execution, as the id lane does, so a bump during the
   building meld makes the next hit miss.
2. Mint only when `creation_gate is None` (the existing arms already are), so dynamic worlds never mint.
3. The public front doors read the registry before delegating; the door subclasses never read it (a miss at
   the front door means the entry is absent or stale, so the door goes straight to the slow lane).

## Validation Expectations
- Unit (`tests/unit/melder/aether/conduit/`): mint by name and by class after one successful meld; hit returns
  the same object identity for a stored singleton and a fresh transient per call; guard misses on notch, hook
  attach, `_cleanup_creation_context`, `cleanup_spell` then rebind, `_spellbook_validation_required`; no mint in
  a dynamic world, with meld hooks, with list/tuple/empty-dict overrides, for an instance or lambda `spell`;
  the override dict arm; the existing-object arm; `SpellSpace.meld` mirror.
- Component (`tests/component/`): differential - by name, by class and by id return the same objects and the same
  errors across the composition shapes of `tests/experimentation/pgo_codegen_composition_experiment.py`.
- Evidence target: the suites on the VM (3.14t, `-X gil=0`); owner-run suites and gauntlet are the gate.

## Unknowns and Open Decisions
- UNKNOWN: none blocking; the VM numbers are directional.
- DECISION_REQUEST: notch timing (frozen window after the 0.2.82 cut).

## Context / Handoff Summary
- What changed: nothing yet (draft written before the src edits).
- Remaining risks: an untested remap path; the tests above cover every remap event found in source.
- Next entrypoint: `src/melder/aether/conduit/meld/meld.py` (slot), then the mints, then the read lanes.
