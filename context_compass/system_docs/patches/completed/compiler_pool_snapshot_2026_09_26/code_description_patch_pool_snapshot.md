# code_description_patch_pool_snapshot

## Metadata
- Patch ID: compiler_pool_snapshot_2026_09_26
- Component: SpellCompiler and Validation Pipeline
- Status: draft
- Created: 2026-09-26T21:20:00Z

## Control Flow
- Phase 5 (both entrypoints): build the adjacency snapshot; `spell_lookup = spellbook._spell_id_pool.copy()`;
  visible = ids in `spell_lookup` whose spell is resolvable and whose id is in `snapshot.all_spell_ids`;
  every later lookup in the pass reads `spell_lookup`.
- Phase 6 frame-wide: `spell_lookup = spellbook._spell_id_pool.copy()` once; stages 1-3 and the strategies
  receive it.
- Phase 3 `_iter_all_spells`: iterate `spellbook._spell_id_pool.copy().values()`.
- Phase-4 strategies and the Phase-8 walk: iterate `<pool>.copy().items()` at the loop.

## Edge / Error Semantics
- No new raise. A pass started before a bind finishes does not see that spell; the bind stages it and gates
  the lineage, so the next meld revalidates with it (unchanged mechanism).
- The Phase-5 change-control revalidator keeps reading the live pool by id (a lookup, not an iteration).

## Invariants / Idempotency
- A copy is a shallow dict; spells are the same objects. Taking it has no side effect, so reruns behave
  identically. Cost is one O(pool) copy per iterating site, the same order as the iteration it replaces.

## Non-goals
- No snapshot of SpellSystemStates (the adjacency builder already reads it under its lock).
- No change to conjure-time sweeps or the Nexus publisher.
