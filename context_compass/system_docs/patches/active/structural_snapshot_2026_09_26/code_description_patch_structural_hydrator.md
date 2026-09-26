# code_description_patch_structural_hydrator

## Metadata
- Patch ID: structural_snapshot_2026_09_26
- Component: SpellCompiler structural snapshot seam (capture, classification, hydrate) inside the
  `SpellbookCreationSystem.conjure` pipeline
- Status: draft
- Owner: fable_0 (cowork)
- Created: 2026-09-26T15:49:37Z
- Updated: 2026-09-26T15:49:37Z

## Control Flow
1. `conjure` (after configuration freeze, before any phase): `classify(spellbook, caching_system)` builds
   `world_stamp = sha256(sorted pool ids + system_state + sorted contracted keys)` and, for every spell in
   `spellbook._spells`, computes the live key `(spell_id, sorted annotation refs from
   spell.profile.resolution_profile.requirements)`; a spell is HIT when
   `caching_system.get_structural_payload(spell_id)` decodes, `payload["key"] == live key`,
   `payload["world_stamp"] == world_stamp` and `payload["replayable"]`; otherwise MISS. Result:
   `{"path": "full_hit" | "partial" | "miss" | "disabled", "hits": {spell_id: payload}, "misses": set}`.
   Caching disabled or an empty structural map -> `disabled`/`miss` (today's run, step 6).
2. Path `full_hit`: `hydrate(spellbook, hits, replay_verdicts=True)` runs step 3 for every spell, then
   step 4; the structural scheduler run is NOT executed; `_collect_broken_spells` runs as today (all
   false); continue at step 7.
3. Replay of one spell (in this order, all through existing surfaces):
   a. `spell_system_states.update_dependencies(spell.spell_index, phase3.dependency_ids)` (creates the
      lineage state if missing, diffs, reverse edges, marks gated + dirty - the same call phase 3 makes);
   b. `spell_system_states.register_local_topology(spell.spell_index, SpellLocalTopology(spell_id,
      sockets))` with descriptors rebuilt from the socket rows (enum names -> members);
   c. `artifact._resolution_frame = SpellResolutionFrame(spell_id, phase3.ordered_node_ids)`;
   d. `spell._add_build_details(dag=None, dependencies=phase3.dependency_ids)` (sets `Spell.dependencies`,
      invalidates the creation context - the cached context is loaded later at activation as today);
   e. Nexus publication when `spellbook._nexus_publish_enabled`.
4. Verdict replay (full hit only), per spell: `state = get_by_index_id(spell.spell_index.id)`;
   `state.clear_dirty(time.time())`; `state.set_validity(valid, validation_passed,
   flags_to_remove=[contract_unvalidated])` or `set_validity(gated, contract_unvalidated,
   flags_to_add=[contract_unvalidated])` from `phase4.validity`; `artifact._is_broken = False`. The
   phase-4 result object is not recreated (phase 6 tests key presence only; the post-pass reset leaves
   `None` today).
5. Path `partial`: run the fused phases 1-2 for EVERY spell (chunked units as today); step 3 for every
   hit; phase 3 for the miss set only (chunked units over the subset; hard barriers kept); phase 4 for
   EVERY spell (live verdicts; no step 4); broken check as today.
6. Path `miss`/`disabled`: `run_structural_phases` unchanged.
7. Executor classification, phases 5-7, 8-11 (or the full-hit skip), conduit build and activation: unchanged.
8. Capture at conjure end (inside `_activate_conjured_conduit`, before the conjure-end emit): for every
   spell whose phase 3 ran live in this conjure (`misses`, or all spells on paths miss/disabled), build
   `{"key", "world_stamp", "replayable", "phase3", "phase4"}` from the artifact (`_resolution_frame`,
   the socket descriptors of the registered topology, the C-C edge rows), the lineage state (`validity`,
   `contract_unvalidated` flag; `is_broken` is false by construction) and the pass verdict
   (`replayable` false when the pass ran with the phase-3 candidate index disabled), and
   `caching_system.upsert_structural_payload(spell_id, payload)`; remove structural payloads whose ids
   are not in `_spells`; set `spellbook._cache_emit_required` when anything changed. The existing emit
   writes the file.

## Edge / Error Semantics
- A payload that fails to decode, lacks a key, or has a schema the reader does not recognize is a MISS for
  that spell and is overwritten at capture; it never raises into conjure.
- A registry helper raising during step 3 propagates exactly as it would from phase 3 (contract violation,
  not a cache condition); the cache file is not rewritten for that conjure.
- Post-conjure binds are unaffected: `run_post_conjure_structural_phases` runs 1-4 for the new spells only,
  as today; their payloads are captured on the NEXT conjure of a process, never mid-run.
- A spell with `replayable: false` is a MISS on every conjure until a later capture records true (the rule
  is a property of the pass, so it flips only when the pool's `__eq__` situation changes).
- `transfer_spell_ownership` drops the source's structural payload (its lineage is dirtied per conduit).
- Restore: every book conjures through the public path; the snapshot keys on spell ids and rows carry no
  index ULID, so a restored world with fresh ULIDs still hits when the pool projection is unchanged.

## Invariants / Idempotency
- Step 3 is idempotent under a following live phase 3 for the same spell (phase 3 rewrites every write),
  which is what makes a mid-hydrate fallback to the full run safe.
- Capture is pure over (artifact, registry state, pass verdict); two captures of the same pass produce
  byte-equal payloads.
- The executor tier never reads structural payloads and the structural tier never reads executor
  payloads; the only shared surface is the envelope file and its emit.

## Explicit Non-Goals
- No rows for phases 1-2 (borrowed at conjure; never persisted), none for 5-7.
- No replay of the phase-4 result object, diagnostics or timestamps.
- No change to how post-conjure binds, local recompiles or the JIT 8-11 path run.
- No per-parameter `==` re-verification in v1 (recorded as the refinement that would lift the
  book-wide `replayable: false` when the candidate index is disabled).
