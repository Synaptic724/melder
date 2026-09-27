# code_description_patch_structural_hydrator

## Metadata
- Patch ID: structural_snapshot_2026_09_26
- Component: SpellCompiler structural snapshot seam (capture, classification, hydrate) inside the
  `SpellbookCreationSystem.conjure` pipeline
- Status: draft
- Owner: fable_0 (cowork)
- Created: 2026-09-26T15:49:37Z
- Updated: 2026-09-26T18:12:10Z

## Control Flow
1. (LANDED 2026-09-26) `conjure` resolves the conduit name and calls `_prepare_spellbook_for_conjure`, which
   after the configuration freeze/bind calls `_build_structural_cache_state` (`disabled` without a conduit
   name, with the opt-in warning report, or with caching off; else) `classify(spellbook, caching_system)`, which builds
   `world_stamp = StructuralSnapshot.world_stamp(spellbook)` (sha256 over sorted pool ids, the posture
   name and the sorted borrowed spell ids) and, for every spell in `spellbook._spells`, the live key
   `StructuralSnapshot.structural_key(spell)` (`{"format", "spell_id", "annotation_refs"}` from the
   bind-time requirements); a spell is HIT when
   `caching_system.get_structural_payload(spell_id)` decodes, `payload_well_formed(payload, spell_id)`,
   `payload["key"] == live key`, `payload["world_stamp"] == world_stamp` and `payload["replayable"]`;
   otherwise MISS. Result: `{"structural_path": "full_hit" | "partial" | "miss" | "disabled",
   "world_stamp", "hits": {spell_id: payload}, "misses": set}`. Caching disabled or an empty structural
   map -> `disabled`/`miss` (today's run, step 6).
2. (LANDED) Path `full_hit`: `_hydrate_structural_tier_for_conjure` -> `hydrate_full_hit(spellbook, hits)`
   runs steps 3 and 4 per spell in sorted id order (a missing payload raises KeyError before any write);
   the structural scheduler run is NOT executed and no broken check runs (rows exist only for spells that
   passed it). A replay failure is logged (`_hydrate_structural_tier_for_conjure`, documented best-effort)
   and the phases run live (step 6). Continue at step 7.
3. (LANDED) Replay of one spell (in this order, all through existing surfaces):
   a. `spell_system_states.update_dependencies(spell.spell_index, phase3.dependency_ids)` (creates the
      lineage state if missing, diffs, reverse edges, marks gated + dirty - the same call phase 3 makes);
   b. `spell_system_states.register_local_topology(spell.spell_index, SpellLocalTopology(spell_id,
      sockets))` with descriptors rebuilt from the socket rows (enum names -> members);
   c. (path `partial` only, where phase 4 runs live and its presence strategy reads the frame)
      `artifact._resolution_frame = SpellResolutionFrame(spell_id, ordered)` with
      `ordered = sorted(set(phase3.dependency_ids) - {spell_id}) + [spell_id]` (derived, not stored);
   d. `spell._add_build_details(dependencies=list(dict.fromkeys(phase3.dependency_ids)))` (sets
      `Spell.dependencies`, invalidates the creation context - the cached context is loaded later at
      activation as today);
   e. Nexus publication when `spellbook._nexus_publish_enabled`.
4. (LANDED) Verdict replay (full hit only), per spell: `state = get_by_index_id(spell.spell_index.id)`
   (None raises RuntimeError: states exist from bind); `state.clear_dirty(now)` (one timestamp per
   hydrate); `state.set_validity(valid, validation_passed, flags_to_remove=[contract_unvalidated])` or
   `set_validity(gated, contract_unvalidated, flags_to_add=[contract_unvalidated])` from
   `phase4.validity`. No artifact write: `_is_broken` is already False on a fresh artifact and the phase-4
   result object is not recreated (phase 6 tests key presence only; the post-pass reset leaves `None`
   today).
5. Path `partial` (DESIGN ONLY - pending the owner's decision; today a partial classification runs step 6):
   run the fused phases 1-2 for EVERY spell (chunked units as today); step 3 (with 3c) for every hit;
   phase 3 for the miss set only (chunked units over the subset; hard barriers kept); phase 4 for EVERY
   spell (live verdicts; no step 4); broken check as today.
6. (LANDED) Path `miss`/`partial`/`disabled`: `run_structural_phases` unchanged.
7. Executor classification, phases 5-7, 8-11 (or the full-hit skip), conduit build and activation: unchanged.
8. Capture at conjure end (LANDED 2026-09-26; `_activate_conjured_conduit` ->
   `_capture_structural_payloads_at_conjure_end` ->
   `StructuralSnapshot.capture_at_conjure_end(spellbook, caching_system)`, after the executor staging and
   before the conjure-end emit, on every cache path): for EVERY owned spell (sorted id order) build
   `{"key", "world_stamp", "replayable", "phase3", "phase4"}` from DURABLE state - `Spell.dependencies`,
   the socket descriptors of the registered topology (no edge rows, they are a socket projection; no
   ordered frame, it is derived), the lineage state (`validity` name, `contract_unvalidated` flag) and the
   bind-time requirements (key) - never from the phase artifacts, which `cleanup_phase_artifacts_after_resolution`
   has already reset; `replayable` is `pool_replayable(spellbook)` (one verdict per conjure). Then
   `caching_system.upsert_structural_payload(spell_id, payload)` (False when the bytes are unchanged); a spell
   with caching disabled or without a buildable payload (no key, no index, no state, no topology, or a
   logged build failure) has its payload removed; ids not in `_spells` are removed;
   `spellbook._cache_emit_required = True` only when anything changed. The existing emit writes the file.

## Edge / Error Semantics
- A payload that fails to decode, lacks a key, or has a schema the reader does not recognize is a MISS for
  that spell and is overwritten at capture; it never raises into conjure.
- A registry helper raising during step 3 propagates out of `hydrate_full_hit` as it would from phase 3;
  the creation system logs it and runs the structural phases live for the whole book (documented
  best-effort), so conjure completes with cold-path state; the capture at conjure end then refreshes the
  rows.
- Post-conjure binds are unaffected: `run_post_conjure_structural_phases` runs 1-4 for the new spells only,
  as today; their payloads are captured on the NEXT conjure of a process, never mid-run.
- A spell with `replayable: false` is a MISS on every conjure until a later capture records true (the rule
  is a property of the pool, so it flips only when the pool's `__eq__` situation changes).
- `transfer_spell_ownership` drops the source's structural payload (its lineage is dirtied per conduit).
- Restore: every book conjures through the public path; the snapshot keys on spell ids and rows carry no
  index ULID, so a restored world with fresh ULIDs still hits when the pool projection is unchanged.

## Invariants / Idempotency
- Step 3 is idempotent under a following live phase 3 for the same spell (phase 3 rewrites every write),
  which is what makes a mid-hydrate fallback to the full run safe.
- Capture is pure over (`Spell.dependencies`, registry state, bind-time requirements, pool eq-safety, world
  inputs); two captures of the same state produce byte-equal payloads, and the second rewrites nothing.
- The executor tier never reads structural payloads and the structural tier never reads executor
  payloads; the only shared surface is the envelope file and its emit.

## Explicit Non-Goals
- No rows for phases 1-2 (borrowed at conjure; never persisted), none for 5-7.
- No replay of the phase-4 result object, diagnostics or timestamps.
- No change to how post-conjure binds, local recompiles or the JIT 8-11 path run.
- No per-parameter `==` re-verification in v1 (recorded as the refinement that would lift the
  book-wide `replayable: false` when the candidate index is disabled).
