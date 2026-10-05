# Component patch: Spellbook Core (Binding and Conjure) - creation-cache admission

- Patch id: executor_cache_world_stamp_2026_10_03
- Owner: fable_0
- Created: 2026-10-03T20:43:11Z

<!-- BEGIN ENTRY: "Creation-cache admission: before and after" -->
## Before
`_build_conjure_cache_state` classifies on payload ids only: `live` = resolvable, non-existing-creation
spells; `full_hit = live and not (live - cached)`; `mixed = matched and missing`. The world a payload was
compiled in is not recorded in the envelope. An existing creation or a non-resolvable definition is in the
pool but never in `live`, so adding, removing or re-keying one leaves the classification a full hit:
phases 8-11 are skipped and each live spell's lazy manifest package is published; the stale plan runs at the
first meld (TypeError for a parameter the plan never resolved, or a plan naming a spell outside the world).
The structural tier already misses on that world (its rows carry the world stamp) and reruns phases 1-4.

## After
`CachingSystem` carries `world_stamp` in the envelope ("" in an empty store, optional on load, always
written); `_build_conjure_cache_state` computes `StructuralSnapshot.world_stamp(spellbook)` when caching is
enabled and sets `world_matches = (recorded == live)`; `full_hit = live and not missing and world_matches`;
`mixed = matched and not full_hit`; `full_miss` otherwise. The returned state carries both values.
`_stage_spell_payloads_at_conjure_end` (mixed and full miss only) records the live stamp after re-staging
every live spell and flags the conjure-end emit when the recorded value changed. The full-hit load, the
structural capture and the single emit are unchanged.

## State and failure deltas
- New envelope field; generation 19 retires bundles without it (version mismatch is the existing cold path).
- No new exception. A hand-made bundle without the field never full-hits.

## Dependency and ordering
- The stamp is read where the executor tier classifies, after `_prepare_spellbook_for_conjure` bound the
  frame configuration; it is written in the activation tail after staging and before the emit, on both the
  ordinary and the existing-conduit conjure routes (both call the same two helpers).

## Validation expectations
- Unit: all live ids cached + matching stamp -> full_hit; + mismatching stamp -> mixed (not full hit); no
  cached id + mismatching stamp -> full_miss; disabled unchanged; staging records the stamp and flags the emit
  when it changed; the envelope round-trips the stamp, loads "" when absent, rejects a non-string.
- Component (caching on, fresh fragment, own conduit name): world 1 Worker(service: Service) alone, meld
  raises UnresolvedInputError; world 2 bare existing Service + Worker, warm cache: the meld returns a Worker
  holding that service (red today: TypeError missing 'service'); world 3 Worker alone again: the meld raises
  UnresolvedInputError; world 4 = world 2 repeated: full hit, bundle bytes and mtime untouched.
- Integration: the surplus contract re-pinned - a removed spell reruns once, then the repeat full-hits.
<!-- END ENTRY: "Creation-cache admission: before and after" -->
