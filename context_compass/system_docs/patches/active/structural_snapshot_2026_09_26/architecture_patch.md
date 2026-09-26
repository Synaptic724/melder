# architecture_patch

## Metadata
- Patch ID: structural_snapshot_2026_09_26
- Status: draft
- Owner: fable_0 (cowork)
- Created: 2026-09-26T15:49:37Z
- Updated: 2026-09-26T17:26:53Z

## Patch Scope and Non-Goals
- Objective (epic I-1, owner-selected 2026-09-26; design settled the same day): a conjure whose creation
  cache holds a valid STRUCTURAL payload for every spell replays the results of phases 3-4 as value rows
  and skips the structural scheduler run; a conjure whose cache covers only some spells replays those and
  regenerates the rest through the normal phase code; phases 5-7 are untouched and run on the hydrated
  registry state exactly as they run on a cold one. The unit of caching, replay and regeneration is the
  SPELL, mirroring the existing per-spell executor payloads.
- Non-goals: no rows for phases 5-7 (blueprints, path registry, system index, per-conduit validity, the
  component-of map stay live); no index ULID ever enters a row; no change to phases 8-11, the executor
  payloads, the meld hot path, `Creations`, the crystallizer restore engine or the change-control
  dirty-root loop (the doc wording for that loop is a separate authorized correction); no phase is
  reimplemented - the snapshot only replays rows through the registry's own write helpers.

## Changed-Components Matrix
| component | change_type | rationale | depends_on |
|---|---|---|---|
| SpellCompiler and Validation Pipeline (phase 3) | modify (LANDED 2026-09-26, task C-C) | C-C: `_build_local_frame_dag` returns `(ordered_node_ids, dependency_spell_ids)` without materializing a `DirectedAcyclicWorkGraph` (order = sorted distinct dependency ids + root; a self-resolution is recorded like any other dependency and Phase 4 reports it as SELF_DEPENDENCY); `Spell.dependency_graph` is a documented None tombstone; `_add_build_details(dependencies)`; the presence strategy checks the frame only (MISSING_DEPENDENCY_GRAPH retired) | none |
| SpellCompiler and Validation Pipeline (new structural snapshot seam) | add (capture LANDED 2026-09-26, task 3: `structural_snapshot/structural_snapshot.py`, `StructuralSnapshot`) | one module beside the phases owns capture (rows from DURABLE state at conjure end) and hydrate (registry replay + artifact/Spell writes) plus the per-spell key, world stamp and pool replayability verdict | C-C (rows) |
| Spellbook Core (conjure pipeline, `SpellbookCreationSystem`) | modify (capture LANDED 2026-09-26: `_capture_structural_payloads_at_conjure_end`) | structural classification and hydrate happen BEFORE the structural run; the structural run takes a spell subset; phase 4 runs for all spells whenever any phase 3 ran live; capture at conjure end after the executor staging, on every cache path | snapshot seam |
| Creation cache envelope (`CachingSystem`) | modify (LANDED 2026-09-26, task 3) | top-level `structural_payloads` map (spell_id -> nested-marshal bytes) with has/get/upsert(-> changed)/remove, `structural_payloads` view and `cached_structural_spell_ids`; generation 14 -> 15 (`structural_snapshot_rows`); transfer drops the structural payload | none |
| Binding Pipeline (`Spell`) | modify | `dependency_graph` tombstone (C-C); one hydrate entry that sets `dependencies` and invalidates the creation context without a DAG | C-C |
| DevOps Control Plane (`SpellSystemStates`, `SpellSystemState`) | none | replay uses the existing `update_dependencies`, `register_local_topology`, `clear_dirty` and `set_validity` exactly as phases 3-4 call them; no new API | - |

## Interface and Boundary Deltas
- Boundary delta 1 (placement): the `.melc` envelope gains `structural_payloads: {spell_id: bytes}` beside
  `spell_payloads`. Every spell in `spellbook._spells` may carry a structural payload (phases 1-4 run for
  every spell), whereas executor payloads exist only for resolvable, non-existing-creation spells; the two
  maps therefore stay separate and the executor classification (`_build_conjure_cache_state`, live
  resolvable ids vs `cached_spell_ids`) is byte-for-byte unchanged. Payloads are stored as nested-marshal
  bytes (GC-untracked, the envelope's rule). `CachingSystem` gains `upsert_structural_payload`,
  `get_structural_payload`, `remove_structural_payload`, `cached_structural_spell_ids`;
  `_build_empty_cache_data`, `_normalize_loaded_cache_data` and `_write_current_cache_to_disk_locked`
  carry the new key; `transfer_spell_payload_to` removes the structural payload from the source and
  copies nothing (a transferred spell is dirtied per conduit and must regenerate). `CACHE_VERSION_HISTORY`
  gains `15: "structural_snapshot_rows"`; version-14 bundles cold-reset once. Coordinate the number with
  melder_0 (14 is theirs, uncommitted on the device tree at authoring time).
- Interface delta 2 (structural payload schema, marshal-safe values only):
  (LANDED shape, `StructuralSnapshot.PAYLOAD_FORMAT` 1)
  `{"key": {"format": 1, "spell_id": str, "annotation_refs": [(module, qualname), ...] sorted},
    "world_stamp": str,
    "replayable": bool,
    "phase3": {"dependency_ids": [str, ...],
               "sockets": [(param_name, position, socket_kind_name, is_collection, is_optional,
                            target_spell_ids, dependency_key, contract_key, referenced_spell_ids,
                            parameter_kind), ...]},
    "phase4": {"validity": <SpellValidity name>, "contract_unvalidated": bool}}`.
  Sockets are the `SpellSocketDescriptor` fields (all strings, ints, bools, enum names and tuples of
  strings). There is no separate edge list: the retired per-spell DAG was a star (every dependency ->
  root, every edge NORMAL, first parameter name kept per dependency), so its rows are a projection of
  the sockets (`target_spell_ids` x `param_name`). The ordered frame is NOT stored either: it is the
  sorted distinct dependency ids (without the spell) followed by the spell id, the law phase 3 applies
  (landed with C-C, 2026-09-26). No `is_broken`/`issue_codes` rows: capture runs at conjure end, past the
  broken-spell check. No index ULID, no object, no repr.
- Interface delta 3 (keys): per-spell tier = the spell id plus the sorted (module, qualname) refs of the
  phase-1 annotation types, read from the bind-time profile requirements (level 0) at both capture and
  hit; a spell whose profile carries no requirements is a structural miss. Per-conduit tier = the WORLD
  STAMP: sha256 over the sorted spell ids of `spellbook._spell_id_pool`, the frame posture name
  (`system_state.name`, empty without a frame configuration) and the sorted spell ids of the borrowed
  spells in `spellbook._contracted_spells`; recorded in every payload and compared at hit.
  Envelope stamps (generation, release, Python tag, frame, conduit) stay as today.
- Interface delta 4 (replayability): a POOL property computed at capture (`StructuralSnapshot.pool_replayable`):
  false when any pool spell's bound object or spellframe fails `CompilerPhase3._eq_safe_object` (the rule
  that disables the phase-3 candidate index and falls back to `==` scans a name cannot reproduce); every
  payload of that book carries the same verdict. A payload
  with `replayable: false` is stored (its phase-4 rows still describe the pass) but never replayed; the
  spell regenerates through the normal phases. There is no book-level refusal.
- Interface delta 5 (conjure order): `SpellbookCreationSystem.conjure` classifies the structural tier
  BEFORE `run_structural_phases`: for every spell in `_spells` the payload exists, its key equals the
  live key, its world stamp equals the live stamp and it is replayable -> HIT, else MISS. Three paths:
  (a) every spell hits: replay phase-3 rows and phase-4 verdict rows for all, skip the structural
  scheduler run, keep the broken-spell check (trivially clean); (b) some hit: run phases 1-2 for EVERY
  spell (borrowed from the bind profile, pure), replay phase-3 rows for the hits, run phase 3 for the
  misses as a chunked subset run, run phase 4 for EVERY spell live; (c) none or caching disabled: today's
  run. The executor classification follows, unchanged.
- Interface delta 6 (capture; LANDED 2026-09-26): at conjure end, on every cache path (executor full hit
  included), after the ownership wiring and the executor staging, `StructuralSnapshot.capture_at_conjure_end`
  builds a payload for EVERY owned spell from DURABLE state - `Spell.dependencies`, the registered
  `SpellLocalTopology`, the lineage state (validity + `contract_unvalidated`) and the bind-time profile
  requirements - because the per-spell phase artifacts are already reset by `cleanup_phase_artifacts_after_resolution`
  before activation. Identical bytes are not rewritten (`upsert_structural_payload` reports the change), so an
  unchanged world leaves the bundle file untouched; a spell with caching disabled or without a buildable payload
  has its stale payload removed; ids no longer owned are removed; `_cache_emit_required` is set only when
  something changed and the existing conjure-end emit writes both maps.

## Cross-Component Invariants
- Invariant 1 (parity): after a hydrate, `SpellSystemStates` holds the same direct dependencies, reverse
  `dependents`, local topologies (field by field), validity verdict and flags for every replayed spell as
  the cold pass that produced the rows; the D5 invalidation table (bind, rebind, notch, index destroy,
  spell cleanup, link/unlink, contract add/remove, transfer) yields the same verdicts after a hydrated
  conjure as after a cold one. Gated (`contract_unvalidated`) verdicts replay verbatim.
- Invariant 2 (no phase reimplementation): a spell is either replayed from rows or run through the
  unchanged phase code; the snapshot module contains no matching, no validation and no graph logic.
- Invariant 3 (rows are values): every persisted value is `None`, bool, int, str or a tuple/list of those;
  no index ULID, no object, no repr text of an object.
- Invariant 4 (capture-on-clean): payloads are captured only at conjure end, which a conjure reaches only
  past the broken-spell check; no `is_broken` row exists.
- Invariant 5 (executor tier independence): the 8-11 classification and load path are untouched; a
  structural miss never forces an executor miss and an executor miss never forces a structural miss.
- Invariant 6 (phase-4 completeness): whenever any spell's phase 3 runs live, phase 4 runs live for every
  spell over a full artifact set (phases 1-2 executed for all), because the binding-resolution-cycle
  strategy skips pool spells without phase-1 rows and would otherwise see a smaller graph.
- Invariant 7 (post-hit state equals post-pass state): after a full structural hit no phase 1-4 artifacts
  exist on the spells, which is the state every cold conjure leaves behind after its post-pass reset;
  phases 5-7 read registry state only, and the JIT 8-11 path already re-reflects when phase-1 rows are
  absent.

## Migration and Rollout Order
1. C-C: phase 3 without the DAG object (rows-only helper, tombstone, presence strategy repointed); compiler
   suites green owner-run; the breakdown harness `local_frame` row before/after.
2. Capture: snapshot module (rows, key, stamp, verdict), envelope map, generation 15, conjure-end staging;
   unit tests for row builders and the envelope; component test that a cold conjure writes payloads for
   every spell. LANDED 2026-09-26 (worktree suites green; owner-run pending); component tests also pin
   that a repeat world leaves the bundle bytes and mtime untouched and that an eq-risky pool marks every
   payload non-replayable (tests/component/melder/spellbook/test_spellbook_component_structural_snapshot_capture.py).
3. Hydrate: structural classification, the three conjure paths, subset structural run, phase-4-for-all rule;
   component tests: full hit skips the structural run and leaves identical registry state; partial hit.
4. Parity: the D5 table as a test list (cold vs hydrated verdicts); restore parity (fresh index ULIDs,
   snapshot still hits); the two-process key test.
5. Measurement: breakdown harness at workers=1 before/after (the 2026-09-26 baseline: 1-4 wall 3.885ms,
   5-7 2.273ms at 29 spells); gauntlet parity.
6. Promotion into `src_components.md` (SpellCompiler entry, Spellbook Core conjure pipeline, Binding
   Pipeline, CachingSystem) and `src_architecture.md` (conjure sequence, invariants); indexes regenerated.

## Rollback Strategy
- Rollback trigger: any parity test failure that cannot be traced to a row-builder bug; a compiler suite
  regression; a gauntlet parity failure.
- Rollback steps: revert the conjure reorder (the structural run returns to the head of the pipeline),
  drop the envelope key and the generation bump (a cold reset), delete the snapshot module. C-C is
  independently revertible (restore the DAG build and the strategy's read).
- Post-rollback verification: compiler suites green owner-run; the breakdown harness matches the baseline.

## Validation Expectations and Evidence Plan
- Validation item 1 (unit; LANDED): row builders are deterministic and ULID-free; key and world stamp
  composition; replayability verdict; envelope round trip of `structural_payloads`; generation gate
  (tests/unit/melder/spellbook/spell_compiler/structural_snapshot/test_structural_snapshot.py, 25 tests;
  tests/unit/melder/utilities/test_caching_system.py +5; schema history pin 15).
- Validation item 2 (component): cold conjure -> capture -> fresh process -> full hit: no structural
  phase unit runs (scheduler phase names asserted), registry state equal field by field, first meld
  behaves as after a cold conjure; partial hit after one new bind: phases 1-2 for all, phase 3 for the
  new spell only, phase 4 for all, identical verdicts.
- Validation item 3 (parity): one test per D5 row comparing cold and hydrated verdicts; restore parity.
- Validation item 4 (measurement, owner-run): breakdown harness at workers=1 with a caching-enabled
  variant of the cycle (a benchmarks/ edit, owner-approved), gauntlet parity.
- Evidence source: owner-run `python -m pytest -q tests/unit/melder/spellbook/spell_compiler
  tests/component/melder/spellbook`; "Not run." until reported.

## Ticket Coverage Map
- Epic: tickets/epics/2026-08-03_comptime_ir_phase_pipeline_epic.md
- Story: tickets/stories/2026-09-26_structural_snapshot_story.md
- Tasks: tickets/tasks/2026-09-26_author_structural_snapshot_patch_docs_task.md (this patch); C-C,
  capture, hydrate, parity and measurement tasks opened under the story in that order.

## Unknowns and Decision Requests
- DECIDED (owner, 2026-09-26): 1-4 only, per spell, beside the executor payload; no refusal (per-spell
  regeneration through the normal phases); annotation refs in the key; the CCM loop question is moot.
- UNKNOWN: whether the bind-time profile requirements exist for every spell kind (proven for class spells
  by the phase-1 identity guard; callables and existing creations to verify at the capture task) - a spell
  without them is a structural miss, so correctness does not depend on the answer, only the hit rate.
- RESOLVED (C-C, 2026-09-26): no Nexus or crystallizer reader consumed `Spell.dependency_graph`; the only
  production reader was the presence strategy (retired warning); nine test files moved to the rows.

## Context / Handoff Summary
- What changed: C-C (task 2) and capture (task 3) landed under `src/` as described in the LANDED rows;
  the hydrate design (deltas 5 and the classification) is still design-only.
- Next entrypoint: the hydrate task (structural classification before `run_structural_phases`).
