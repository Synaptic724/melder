# Component patch: Spellbook Core - the creation cache keys on the binding hash (spell_identity_is_the_code_2026_10_18)

## Metadata
- Patch ID: spell_identity_is_the_code_2026_10_18
- Component: Spellbook Core (Binding and Conjure) - its creation cache: `StructuralSnapshot.PAYLOAD_FORMAT`,
  `structural_key`, `world_stamp` and `payload_well_formed`
  (`src/melder/aether/spellbook/spell_compiler/structural_snapshot/structural_snapshot.py`);
  `CachingSystem.CACHE_VERSION_HISTORY` and the class docstring (`src/melder/utilities/caching_system/caching_system.py`);
  the docstring and comment of `SpellbookCreationSystem._build_conjure_cache_state`
  (`src/melder/aether/spellbook/spellbook_creation_system.py`); the generalized family's comment and docstring
  that trust the spell_id to cover the binding (`generalized_manifest_no_overrides_compiler.py`,
  `generalized_manifest.py`, under `src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/generalized/`)
- Story: STORY-2026-10-18-binding_manifest_hash (S2), landing with STORY-2026-10-18-spell_id_hashes_the_object_code
  (S1)
- Status: approved - the owner's word to land S1 with S2's cache keys (chat 2026-10-18; the epic's DECISION note
  of 2026-10-18T15:01:53Z) and his confirmation of the "conduit manifest" reading (DECISION note of
  2026-10-18T14:14:10Z)
- Owner: user; melder_0 (synaptic_python_developer)
- Created: 2026-10-18T15:40:03Z
- Updated: 2026-10-18T16:32:46Z

## Component Purpose and Boundary
- Current boundary, read whole on 0.2.8255: one `.meldercache` bundle per root conduit holds two tiers, both keyed
  by spell_id.
  - Structural tier: one payload per owned spell, keyed `{format, spell_id, annotation_refs}` and carrying the
    world stamp, a SHA256 over the sorted pool ids, the frame posture and the sorted borrowed ids. A conjure
    replays phases 3-4 when every owned spell's payload carries its live key, the live stamp and a replayable
    verdict, and captures fresh payloads at its end on every cache path (`StructuralSnapshot.structural_key`,
    `world_stamp`, `classify`, `capture_at_conjure_end`).
  - Executor tier: one manifest package per payload-eligible spell. A conjure skips phases 8-11 and loads every
    context from its package when every live id is cached and the envelope's recorded stamp equals the live one;
    any other conjure compiles, removes every package, restages every live spell and records the stamp
    (`SpellbookCreationSystem._build_conjure_cache_state`, `_load_cached_creation_contexts_for_conjure`,
    `_stage_spell_payloads_at_conjure_end`). A meld stages a package only for an id the bundle lacks
    (`Spellbook._emit_spell_cache`).
  - Both rest on the spell_id covering the binding. The key's docstring says "the spell id already covers the
    spell's own signature, names, existence and resolvability", and the generalized family stamps each step's
    existence and disposal flag into the rows a cached plan is emitted from, trusting that "disposal facts
    compose into the spell fingerprint".
- Target boundary: the same tiers and rules with each spell's binding hash beside its spell_id. The structural key
  gains `binding_hash`, and the world stamp hashes every pool id and every borrowed id with its spell's binding
  hash. One stamp feeds both tiers, so a binding changed under one spell_id - existence, disposal names, address,
  spellframe, resolvable or managed settings - misses both tiers for the Book, as a changed spell_id does today.

## Before/After Behavior Summary
- Without this patch, S1 would let a stale plan through: `Greeter` cached as `unique`, then bound as `many` in the
  next process, keeps one spell_id and one pool, so both tiers would hit and its consumers would replay plans
  emitted for a `unique` provider.
- With it, that world's stamp differs, so both tiers miss once, recompile and restage; a repeat world is a
  byte-identical full hit as today, and worlds whose bindings did not change hit exactly as today.

## Interface Deltas
- Inputs: none new. `StructuralSnapshot.world_stamp(spellbook)` and `structural_key(spell)` keep their signatures
  and read `Spell.binding_hash` (component_patch_binding_pipeline.md, S2 section).
- Outputs: the structural key is `{"format": 2, "spell_id", "binding_hash", "annotation_refs"}` (`PAYLOAD_FORMAT`
  1 -> 2, checked by `payload_well_formed`); the stamp's lines are `pool:<id>=<binding_hash>,...` (sorted by id),
  `posture:<name>` and `borrowed:<id>=<binding_hash>,...` (sorted); the envelope format is unchanged.
- `CachingSystem.CACHE_VERSION_HISTORY` gains 23: "binding_manifest_keys"; a generation-22 bundle is cold once.
- Error semantics: unchanged - a malformed or older payload is a miss, an older bundle a cold cache.

## State and Lifecycle Deltas
- Owned state changes: none. Both values are computed from the Book's Spells at classification and capture, as
  the stamp is today; `Spell.binding_hash` is computed once at bind.
- Lifecycle/cleanup changes: none.

## Failure Mode Deltas
- New failure mode: none. Removed: the stale replay S1 alone would allow (above).
- Changed: none visible. A binding change changed the spell_id and missed both tiers; it now keeps the spell_id
  and still misses both.
- Residual, unchanged (RISK, low): a package staged at a meld for an id the bundle lacked - possible only after
  that spell's conjure-end staging failed, which is logged - is replayed by a later full hit of the stamped world
  even when the spell was rebound in between; the restaging that follows any miss replaces it.

## Dependency and Ordering Constraints
1. Needs `Spell.binding_hash` (component_patch_binding_pipeline.md, S2 section), so it waits for spell.py
   (back from melder_1 after S9 lands as 0.2.8256; M1-37).
2. Lands with S1 in one pass: the cache never sees S1's spell_id without the binding hash (architecture patch,
   invariant 7).
3. The generation bump is in the same change set as the key and stamp change.

## Validation Expectations
- Unit: the key carries the binding hash and `payload_well_formed` refuses format 1; the stamp moves when one pool
  spell's binding hash moves (existence, disposal names, resolvable, managed settings) and when a borrowed
  spell's does, and is byte-identical for one world across two processes and with the GIL off and on.
- Integration: bind a class as `unique`, conjure and emit; a fresh Aether binds it as `many` (one spell_id) and
  conjures - the structural path is a miss, the executor path mixed, and the consumer builds a new provider per
  meld; the same world twice is a full hit on both tiers.
- `CachingSystem`: a generation-22 bundle loads cold.
- The existing structural-snapshot and executor-cache suites pass, the format assertions moved to 2.

## Unknowns and Open Decisions
- UNKNOWN: none in the code paths read.
- RISK (low): the residual under Failure Mode Deltas; closing it needs a per-package record of the world it was
  staged in, which no reachable path but a logged staging failure exercises.

## Context / Handoff Summary
- What changed: nothing in `src/`.
- Remaining risks: the residual above.
- Next entrypoint:
  `src/melder/aether/spellbook/spell_compiler/structural_snapshot/structural_snapshot.py:StructuralSnapshot.world_stamp`.
