# component_patch_spell_compiler

## Metadata
- Patch ID: structural_snapshot_2026_09_26
- Component: SpellCompiler and Validation Pipeline (phase 3; the new structural snapshot seam); Spellbook
  Core (conjure pipeline in `SpellbookCreationSystem`); Creation cache envelope (`CachingSystem`); Binding
  Pipeline (`Spell.dependency_graph`)
- Status: draft
- Owner: fable_0 (cowork)
- Created: 2026-09-26T15:49:37Z
- Updated: 2026-09-26T16:39:37Z

## Component Purpose and Boundary
- Current boundary: `SpellbookCreationSystem.conjure` freezes the configuration, runs phases 1-4 over
  every spell through the scheduler (`run_structural_phases`, chunked units over `spellbook._spells`),
  classifies the executor cache from the live resolvable id set, runs phases 5-7 and (unless a full
  executor hit) 8-11, builds the conduit, and at conjure end loads cached creation contexts (full hit) or
  re-stages every executor payload (mixed/miss) before the single conjure-end emit
  (spellbook_creation_system.py:207-333, :875-1046). Phase 3 writes `update_dependencies`,
  `register_local_topology`, `artifact._resolution_frame` and `Spell._add_build_details` per spell;
  phase 4 writes the lineage verdict (compiler_phase_4.py:56-178). The envelope is one marshal dict with
  five stamps and `spell_payloads` (caching_system.py:151-168, :497-640).
- Target boundary: the same pipeline with a structural tier in front of the structural run: classify per
  spell, replay the hits, regenerate the misses through the unchanged phases, capture at conjure end. The
  envelope carries a second per-spell map. Phase 3 stops building a DAG object (C-C).

## Before/After Behavior Summary
- Before (phase 3): builds a `DirectedAcyclicWorkGraph` per spell with live Spell payloads (ULID, RLock,
  per-node containers, per-edge lock acquisitions, heap topological sort), stores it as
  `Spell.dependency_graph`; its only production reader is the resolution-frame presence strategy's
  `is None` warning; `Spell.dependencies`, the resolution frame and the registered topology carry the
  same information (candidates.md C-C; phase_03.md:38-80).
- After (phase 3, C-C; LANDED 2026-09-26): `_build_local_frame_dag` returns `(ordered_node_ids,
  dependency_spell_ids)` without DagNodes - the order is the sorted distinct dependency ids then the root
  (the star DAG's topological law), a self-dependency raises ValueError before any registry write, and the
  edge rows are not stored because they are a projection of the topology sockets; `Spell.dependency_graph`
  is a documented `None` tombstone (cleanup cascade removed, slot kept for shape);
  `Spell._add_build_details(dependencies)` has no `dag` parameter; the presence strategy checks the frame
  only (MISSING_DEPENDENCY_GRAPH retired); every other write of phase 3 is unchanged.
- Before (conjure, structural): phases 1-4 run for every spell on every conjure, including a full
  executor hit (structural wall 3.885ms of the 6.158ms phases 1-7 wall at 29 spells, owner-run
  2026-09-26).
- After (conjure, structural): `_build_structural_cache_state` runs first (needs only the caching system,
  built from the resolved conduit name as today, and the pool). Path (a) full structural hit: replay for
  every spell, no structural scheduler run, broken check as today. Path (b) partial: phases 1-2 for every
  spell (one fused chunked phase, borrowed requirements), replay phase-3 rows for hits, phase 3 for the
  miss subset (`_build_per_spell_phase_units` over the subset), phase 4 for every spell. Path (c) miss or
  caching disabled: today's run. Everything from the executor classification onward is unchanged.
- Before (envelope): `spell_payloads` only; a non-full executor hit removes and re-stages every executor
  payload (`_stage_spell_payloads_at_conjure_end`).
- After (envelope): `structural_payloads` beside it; at conjure end every spell whose phase 3 ran live is
  re-captured, hit spells keep their payload, dead ids are removed, and the same conjure-end emit writes
  both maps; generation 15.
- Before (replay surface): none.
- After (replay surface): the snapshot module's hydrate performs, per hit spell and in this order,
  `spell_system_states.update_dependencies(spell.spell_index, dependency_ids)`,
  `register_local_topology(spell.spell_index, SpellLocalTopology(spell_id, sockets))`,
  `artifact._resolution_frame = SpellResolutionFrame(spell_id, ordered_node_ids)`,
  `spell._add_build_details(dependencies=dependency_ids)` (invalidates the creation context, as
  today), Nexus publication when enabled; on path (a) additionally `state.clear_dirty(time.time())` and
  `state.set_validity(...)` with the recorded verdict and flags, and `artifact._is_broken = False`. On path
  (b) phase 4 runs live for every spell instead of replaying verdicts.

## Interface Deltas
- Inputs: `SpellbookCreationSystem.conjure` unchanged for callers; `run_structural_phases` gains an
  optional spell subset and a phase selection (1-2 only / 3 only / 4 only) used by the partial path;
  `CachingSystem` gains the four structural methods; the snapshot module exposes
  `build_structural_payload(spell, artifact, registry, world_stamp, replayable)`,
  `structural_key(spell)`, `world_stamp(spellbook)`, `classify(spellbook, caching_system)` and
  `hydrate(spellbook, payloads, replay_verdicts: bool)`.
- Outputs: unchanged public API; the envelope gains one key; `Spell.dependency_graph` returns `None`.
- Error semantics: a structural payload that fails to decode or validate is a MISS for that spell (the
  spell regenerates; the payload is rewritten at conjure end); a corrupt envelope is a cold cache as today.
  A registry helper raising during replay propagates (it would raise for phase 3 too). Nothing new is
  raised into `conjure` by the capture step: capture failures are logged and leave the spell without a
  payload.

## State and Lifecycle Deltas
- Owned state changes: `CachingSystem._cache_data["structural_payloads"]` (bytes per spell; cleaned with
  the store); `Spell.dependency_graph` tombstone; no new registry state, no new Spell slot.
- Lifecycle/cleanup changes: none; the snapshot module is stateless (slot-only static helpers), the
  descriptor rows are rebuilt into a fresh `SpellLocalTopology` per hydrate and owned by the registry as
  today.

## Failure Mode Deltas
- New failure mode: a stale structural payload replayed because the world stamp missed a relevant input.
  Guard: the stamp covers every input the survey found phases 3-4 read from the world (pool ids, posture,
  contracted keys) plus the per-spell annotation refs; the D5 parity suite is the detector.
- Removed failure mode: none on the cold path.
- Changed failure mode: a spell that regenerates on a partial hit costs phases 1-4 as today; a full hit
  that fails mid-hydrate falls back to path (c) for the whole book (the registry writes of a completed
  spell are idempotent under a following live run, because phase 3 rewrites them).

## Dependency and Ordering Constraints
1. C-C lands first (rows exist; the DAG reader is gone) - `compiler_phase_3.py`, `spell.py`, one strategy,
   nine test files. LANDED 2026-09-26 (worktree suites green; owner-run pending).
2. The envelope change and generation 15 are sequenced after melder_0's generation 14 commit; NOTICE before
   touching `caching_system.py`, `spellbook_creation_system.py` or `spellbook.py` (melder_0's S3 lane
   edits the cache path).
3. Capture before hydrate; hydrate before parity; measurement last.
4. The breakdown harness gains a caching-enabled cycle (benchmarks/ edit) only with owner approval.

## Validation Expectations
- Test/validation item 1: row builders (unit) - deterministic bytes for the same pass, values only.
- Test/validation item 2: envelope (unit) - round trip, generation gate, transfer drops the structural
  payload.
- Test/validation item 3: conjure paths (component) - full hit runs no structural phase unit and yields
  registry state equal to the cold pass; partial hit runs phases 1-2 and 4 for all and phase 3 for the
  misses only; identical verdicts.
- Test/validation item 4: D5 parity list and restore parity (component).
- Evidence target: owner-run compiler and component suites; breakdown harness before/after. "Not run."

## Unknowns and Open Decisions
- Profile requirements presence per spell kind (hit-rate question, not correctness).
- Whether `SpellResolutionFrame` and `SpellLocalTopology` constructors accept the row tuples directly or
  need a small builder (read at the capture task).

## Context / Handoff Summary
- What changed: design only. Next entrypoint: C-C task after owner review.
