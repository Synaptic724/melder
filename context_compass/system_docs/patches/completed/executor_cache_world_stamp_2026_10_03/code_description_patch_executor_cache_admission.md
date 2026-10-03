# Code description patch: executor-cache admission and staging

- Patch id: executor_cache_world_stamp_2026_10_03
- Files: `src/melder/utilities/caching_system/caching_system.py`,
  `src/melder/aether/spellbook/spellbook_creation_system.py`
- Owner: fable_0
- Created: 2026-10-03T20:43:11Z

<!-- BEGIN ENTRY: "Executor-cache admission: control flow and edge semantics" -->
## Control flow
1. `CachingSystem._build_empty_cache_data`: `world_stamp: ""`. `_normalize_loaded_cache_data`:
   `loaded.get("world_stamp", "")`, ValueError unless a str, carried into the returned envelope.
   `_write_current_cache_to_disk_locked`: writes the field. `world_stamp` property: the current value.
   `set_world_stamp(stamp)`: under the lock, store and return whether it changed. Generation 19.
2. `_build_conjure_cache_state`: when caching is enabled, `world_stamp = StructuralSnapshot.world_stamp(
   spellbook)` and `world_matches = caching_system.world_stamp == world_stamp`; otherwise "" and False.
   `is_full_hit = bool(live) and not missing and world_matches`; `is_mixed = bool(matched) and not
   is_full_hit`; `is_full_miss = not is_full_hit and not is_mixed`. Both values join the returned dict.
3. `_stage_spell_payloads_at_conjure_end`: after the remove-all and the sorted re-stage,
   `if caching_system.set_world_stamp(cache_state["world_stamp"]): spellbook._cache_emit_required = True`.

## Edge and error semantics
- An empty live set stays a full miss (unchanged), so a world of existing objects only never records a hit;
  its stamp is still recorded by the staging that runs on that path.
- A full hit with a matching stamp never reaches the setter; the bundle is untouched.
- A stamp mismatch with every payload matched is reported as mixed: the label the activation tail already
  routes to staging.

## Invariants / idempotency
- Staging is idempotent per world: the second conjure of an unchanged world full-hits and writes nothing.
- The setter is the only writer of the field; it runs after the payload writes of the same conjure.

## Explicit non-goals
- No per-spell stamp in the executor tier; no change to what is staged or loaded per spell.
<!-- END ENTRY: "Executor-cache admission: control flow and edge semantics" -->
