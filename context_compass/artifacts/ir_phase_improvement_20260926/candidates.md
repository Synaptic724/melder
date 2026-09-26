# Improvement candidates for the conjure pipeline (phases 1-11), ranked per regime

Recorded 2026-09-26 by fable_0 (STORY-2026-09-26-phase-pipeline-improvement-plan, task 2, steps R1-R2).
Status: COMPLETE. Fact base: `cost_model.md` (this directory) and the survey records under
`artifacts/ir_phase_survey_20260925/`; new source reads this session are named in the evidence cells. Every
candidate carries the eight fields the story requires plus a lane-collision flag. Expected effects are
MEASURED only where a MEASURE row in cost_model.md section 3 backs them; otherwise they are COUNTED
(allocations, passes, locks removed) and the magnitude is "unmeasured". Nothing was run: "Not run."

Two invariants that bound every ranking below:
- A Spellbook conjures ONE root conduit for its lifetime (src_architecture.md, Operational Invariants,
  `_conjured` flag). "Warm conjure" therefore means a NEW book in a new process hitting the `.melc` cache,
  never a second conjure of the same book: on a warm conjure the phase objects and registry rows do not
  exist yet, so every "skip if unchanged" memo below the creation cache is structurally unable to hit.
  The only ways to remove 1-7 work on the warm path are to do less per spell or to hydrate rows (C-G).
- Hot paths and the meld door belong to another agent (epic Decision Log 2026-09-25); no candidate here
  reaches `conduit/meld/**`, `Creations` or the scope-cycle door.

## Candidates

### C-A. Stop the dead pool-sized signature in phase 8 (hoist the pass-invariant hash; check None first)
- Mechanism: per root, `analyze` builds `fast_key` and `input_signature` by hashing the root's rows PLUS
  the pool-wide spell rows, topology rows and contracted rows (one pool-sized pickle + sha256 per root),
  then tests the skip condition whose LAST clause is `_occurrence_graph_analysis is not None`; phase 5's
  attach nulls that slot on every pass and no other module reads the two slots, so on every conjure the
  hash is computed and discarded (O(spells^2) per cold conjure). Fix: (1) test the None clause first and
  skip the compare; (2) hash the pass-invariant rows ONCE per pass into `analysis_pass_cache` and combine
  the per-root rows with that digest, so the stored key stays a deterministic function of the same inputs.
- Evidence: spell_occurrence_graph_analyzer_strategy.py:118-253, :267-372, :374-508; compiler_phase_5.py:
  182-216; spell_compiler_artifact.py:304-324; grep (no external reader); cost_model.md section 2 (phase 8).
- Regime: cold conjure and mixed hits (8-11 run); JIT 8-11 batches. Not warm (8-11 skipped).
- Expected effect: removes N x (pool-sized pickle + sha256) per cold conjure; magnitude unmeasured
  (June: plan_group ~14.2ms busy for 29 roots; the signature share is not separated).
- Scope: one strategy file, ~30 lines; the pass-cache key set gains one entry.
- Risk: LOW. The key must remain deterministic across processes (ties to C-H); no behaviour change.
- IR alignment: positive - a signature over value rows is exactly the IR-hash the epic wants; hoisting
  the pool digest is the L2/L3 "world snapshot hash" in embryo.
- Measurement: `profile_phase_scheduler_breakdown.py` plan_group busy at workers=1 before/after; a unit
  test that two processes produce equal signatures for the same book (C-H).
- Collision: phase 8 is inside updater_1's review-stage override proposals (`override_occurrence_slicing`)
  and melder_0's override design; coordinate the file before editing (NOTICE to updater_1 and melder_0).

### C-B. Fuse phases 5-7 into one foundation unit and drop phase 7's duplicate change-control rebuild
- Mechanism: the resolution run registers `root_blueprints`, `system_validation` and `change_control` as
  three single-unit phases: three latches, three control->worker->control handoffs, three `factory()`
  calls per conjure and per local recompile. Phase 7 then rebuilds the CCM component-of map that phase 5
  already rebuilt this conjure (clearing dirty state a second time), builds two throwaway
  `CompilerPhase5()` instances, and calls `set_revalidator` whose guard is already True. Fix: one phase
  whose single unit runs 5 -> 6 -> 7 sequentially (order preserved inside the unit; 6 needs 5's outputs),
  and phase 7 reduced to the revalidator guard (or folded into phase 5's tail). Mirror the `*_local`
  variants.
- Evidence: resolution_driver.md:17-27 (`_register_conduit_resolution_phases` :1743-1786);
  phase_07.md:15-22, :29-44; phase_05.md:50-60; compiler_phase_7.py:111-185 (via phase_07.md);
  phase_scheduler.py:758-906.
- Regime: every conjure (cold and warm) and every meld-time local recompile.
- Expected effect: MEASURED scheduler handoff is ~0.3ms over 6 barriers (profiled dump), so -2 barriers
  is ~0.1ms per conjure; -1 CCM rebuild and -2 object constructions per conjure (unmeasured, small). The
  larger value is structural: one foundation unit is the one hydrate unit C-G needs.
- Scope: `spellbook_creation_system.py` registration (driver, outside `spell_compiler/**`) and
  `phases/compiler_phase_7.py`; component map entries for phases 5-7 and the conjure flow.
- Risk: LOW. Fail-fast semantics are unchanged (a raise inside the fused unit reports once); cancellation
  is checked at unit start (phase 7 carries no cancel token today).
- IR alignment: positive - matches the epic's "link (5-6) then emit-and-wire (11 absorbing 7)" reading.
- Measurement: breakdown harness rows for the fused phase vs the three; `tests/` for change-control
  wiring (the dirty-root suite, 11 files) stay green (owner-run).
- Collision: `spellbook_creation_system.py` may be under edit by melder_0 (missing_dependency_sockets,
  step 3 "conjure INFO report"); verify with `git diff` before the patch and split hunks.

### C-C. Stop materializing the phase-3 DAG object; keep the id rows
- Mechanism: phase 3 builds a `DirectedAcyclicWorkGraph` per spell per conjure (ULID mint, RLock, two
  dicts; per node two sets + list + two dicts; per edge three re-entrant lock acquisitions and four
  container writes; a heap-based topological sort) with live Spell payloads, and stores it as
  `Spell.dependency_graph`. Its only production reader is the phase-4 presence strategy's `is None`
  warning; `Spell.dependencies` (ids), the `SpellResolutionFrame` (ordered ids) and the registered
  `SpellLocalTopology` carry the same information, and phase 5 re-derives the closure from registry rows.
  Fix: compute `ordered_node_ids` and `dependency_spell_ids` from the resolved sockets without DagNodes
  (or through a rows-only helper); point the presence strategy at the frame or the ids.
- Evidence: phase_03.md:24-32, :41-49; dag_node.py:45-83, :159-198; directed_acyclic_work_graph.py:56-68,
  :122-221, :255-296; resolution_frame_presence_strategy.py:90-103; grep `dependency_graph` (src: one
  reader; tests: 8 files, 49 hits); cost_model.md section 3 (phase 3 5.07ms/29 profiled, DAG share
  unmeasured).
- Regime: every conjure (phase 3 runs on cold and warm), post-conjure binds, local recompiles.
- Expected effect: per spell per conjure removes one ULID, one RLock, ~5 containers per node, three lock
  acquisitions per edge and the sort; phase 3 is the largest structural phase in the profiled dump
  (`_build_local_frame_dag` 4.37ms/29), DAG share unmeasured.
- Scope: `compiler_phase_3.py` (`_build_local_frame_dag`), `spell.py` (`dependency_graph` slot and
  cleanup), one validation strategy, eight test files; component map (Spell owns_state, phase 3 entry).
- Risk: MEDIUM. `Spell.dependency_graph` is a documented owned field (src_graph payload) and a test
  surface; keeping the attribute as `None` (documented tombstone) preserves shape, but tests that walk the
  DAG must move to the rows. Nexus publication reads: UNKNOWN (grep shows none under `nexus/`).
- IR alignment: strong - the L2 graph becomes rows (ids, param, socket kind) instead of an object graph.
- Measurement: breakdown harness `local_frame` wall at workers=1; `tests/component/.../dag/` and
  `test_spell.py` (owner-run).
- Collision: none known; phase 3 is not in the override lanes.

### C-D. Content-keyed phase-5 attach (skip the 8-11 invalidation when the blueprint rows are unchanged)
- Mechanism: every phase-5 attach nulls the occurrence analysis, codegen outputs and creation context of
  each owned spell. Because a book conjures once, this only matters on the meld-time local recompile
  paths, where the local attach publishes to the target only and the target did change.
- Evidence: compiler_phase_5.py:182-216 (via phase_05.md:35-48); src_architecture.md `_conjured`
  invariant; structural_driver.md:48-56.
- Regime: local recompile only.
- Expected effect: none on cold or warm conjure; local paths: the target is invalidated by design.
- Scope / Risk / IR alignment / Measurement: not worth a patch; recorded so the idea is not re-proposed.
- Collision: n/a. VERDICT: DROP.

### C-E. Capture the phase-2 symbolic graph at bind (level 0) and borrow it like phase 1
- Mechanism: phase 1 already borrows its rows from the bind-time profile (`_requirements_borrowed`);
  phase 2 is a pure function of those rows plus `selected_spell_id`, yet rebuilds one graph, one edge per
  parameter and one RLock each on every conjure; the resolution profile reserves `SpellSymbolicNode/Edge/
  Graph` placeholders for exactly this. Fix: build the edge rows at bind (value-only: param, position,
  di_shape, optional, collection, contract key, type refs), store them on the profile, and let phase 2
  attach a borrowed graph the post-pass reset does not clean.
- Evidence: phase_02.md:49-52; phase_01.md (borrow path compiler_phase_1.py:167-207;
  resolution_profile.py:11-402); driver.md (capture_phase2_5 rows); structural_driver.md:24-27 (reset
  spares borrowed requirements).
- Regime: every conjure (cold and warm) and post-conjure binds.
- Expected effect: removes phase 2's per-conjure allocations (profiled 0.46ms/29; small) and moves the
  cost to bind, once per spell version. The value is that it is the first IR row family in production.
- Scope: `compiler_phase_2.py`, `profiles/resolution_profile.py`, the bind-time profile completion,
  `spell_compiler_artifact.py` reset; tests for the borrow.
- Risk: LOW-MEDIUM. `target_annotation` is a live type today; the borrowed graph may keep the object
  until the IR type-ref scheme lands (STORY-2), so this is a memo first and a port second.
- IR alignment: strongest of the small candidates (level 0 grows from facts to the L1/L2 rows).
- Measurement: breakdown harness `requirements_symbolic` wall; bind cost in
  `profile_bind_conjure_cycle.py` (bind rises, conjure falls).
- Collision: none known.

### C-F. Gate-then-clear churn on the lineage registry every conjure
- Mechanism: phase 3 marks every compiled spell's lineage `dependencies_changed` + dirty, phase 4 clears
  it and writes validity, phase 6 writes per-conduit validity with RiskManager fan-out per changed id
  (202 `set_validity` calls, 0.45ms profiled). On a first conjure the states are new, so the gate is the
  correct initial state; the churn is real only on post-conjure binds and local recompiles.
- Evidence: phase_03.md:41-49; phase_04.md (writes); phase_06.md:44-58; cost_model.md section 3.
- Regime: post-conjure bind and local recompile.
- Expected effect: small (sub-millisecond, profiled); unmeasured unprofiled.
- Scope: `spell_system_states.update_dependencies` (mark only on a non-empty diff) - outside
  `spell_compiler/**` (DevOps control plane).
- Risk: MEDIUM: the gate is what the meld door reads; changing when it flips touches invalidation
  semantics (invalidation.md D5). IR alignment: neutral. Measurement: dirty-root and validity suites.
- Collision: none known. VERDICT: PARK (low value, semantic risk).

### C-G. Structural snapshot: hash -> hydrate phases 1-7 on a full cache hit (the epic's I-1)
- Mechanism: per summary.md D1-D6: capture registry rows (1-4), blueprint + path registry rows and
  per-conduit validity rows (5-7) from a pass that ended valid and clean, keyed per spell on the spell id
  and per conduit on (visible ids, owned ids, posture, contracted keys); on a full hit hydrate by
  registry replay, blueprint rebuild, one revalidator registration and the Spell flags, then the
  existing 8-11 cache load.
- Evidence: summary.md (D2 table, D3, D4, D5, D6); resolution_driver.md:46-66; cache_seam.md.
- Regime: warm conjure and restore (scales with the number of books).
- Expected effect: removes the 1-7 compute on a full hit: ~20ms of the 44ms profiled conjure, bounded
  above by the 6.1ms unprofiled warm conjure (June); the exact unprofiled share is unmeasured. Adds a
  capture cost on misses and a hydrate cost on hits (both unmeasured).
- Scope: LARGE - patch docs (architecture, SpellCompiler component, hydrator control flow), capture and
  hydrate code, envelope generation bump or sidecar, invalidation parity tests, restore parity tests.
- Risk: MEDIUM-HIGH: registry replay correctness (two validity tiers, reverse indexes, RiskManager
  bursts), identity-bearing frames (custom `__eq__`), index ULIDs in rows, the moving-module spell id.
- IR alignment: it IS the epic's memoization story and the Mojo hydration seam.
- Measurement: `profile_bind_conjure_cycle.py` warm conjure and warm setup; gauntlet setup line;
  invalidation parity = the D5 table as a test list.
- Collision: envelope generation bump touches `caching_system.py` (updater_0's release-guard work,
  closed) and the door compiler lineage (melder_0, cache v10/v11): coordinate the generation number.
- Prerequisites: C-H; the four STORY-2 rulings (frames, envelope vs sidecar, module fingerprint,
  CCM loop as API).

### C-H. Determinism test plus one serializer for the signature path (the epic's I-0)
- Mechanism: `serialize_codegen_signature_part` pickles raw sets in iteration order (hash-seed dependent
  for str), `freeze_phase11_schema_value` falls back to `repr` for user contract payloads (process-local
  addresses), and `CodegenCreationSchemaHelpers` duplicates the serializer/hash/freeze/row builders under
  an alias. Fix: one serializer that sorts sets and refuses or canonicalizes non-primitive payloads; a
  test that two interpreter processes produce equal executor and occurrence signatures for the same book.
- Evidence: driver.md (hashing hazards; shared_compiler_executions.py:60-137, :414-424, :1045-1052;
  codegen_creation_schema_helpers.py:1-60, :300-345).
- Regime: all (cache correctness); every signature-based skip (C-A, C-G) stands on it.
- Expected effect: no speed change; prevents per-process cache misses and false hits.
- Scope: two modules under `spell_compiler/**` plus tests; small.
- Risk: LOW (behaviour-preserving for deterministic inputs; changes the signature bytes, so one cache
  generation bump or a documented cold reset).
- IR alignment: strong (the IR hash must be deterministic by definition).
- Measurement: the two-process determinism test; cache hit rate across processes in
  `profile_bind_conjure_cycle.py`.
- Collision: `shared_compiler_executions.py` carries melder_0 content hunks at :875-1263 (sockets lane);
  the serializer at :60-137 is outside them, but the file will merge - sequence after melder_0 lands.

### C-I. Per-run object churn: validators, strategy lists, throwaway compiler systems
- Mechanism: each scheduler run builds a `SpellCompilerSystem` (compiler + validator with 13 strategies),
  a third one is built only to reset artifacts, phase 6 builds 23 strategy objects per run, phase 7 two
  `CompilerPhase5()` helpers. Fix: keep strategy instances on the owning builder (stateless per their
  contracts - UNKNOWN for the 11 + 22 unread strategies) and reset artifacts without a compiler system.
- Evidence: structural_driver.md:17-32, :36-40; phase_06.md:21-31; phase_07.md:15-22.
- Regime: every conjure and every local recompile.
- Expected effect: `cleanup_phase_artifacts_after_resolution` 0.41ms profiled; the rest unmeasured, small.
- Scope: driver and two phase modules. Risk: LOW-MEDIUM (strategy statelessness must be verified for
  33 unread files). IR alignment: neutral. Measurement: breakdown harness whole-conjure wall.
- Collision: none known. VERDICT: fold into whichever tranche touches those files; not standalone.

### C-J. Cost-aware plan_group chunking (longest-processing-time assignment by blueprint size)
- Mechanism: `plan_group` chunks are contiguous equal-count splits of `_spells` order over heterogeneous
  per-root cost (RequestRoot ~2.3ms vs ~0.1ms leaves, June); `PLAN_GROUP_CHUNK_MULTIPLIER=2` recovered
  part of the skew. The phase-5 blueprint's `ordered_node_ids` length is known before the plan_group
  factory runs, so roots can be ordered by closure size and dealt round-robin (LPT) into `workers*2`
  chunks.
- Evidence: tickets/tasks/completed/2026-06-12_phase_scheduler_v2_persistent_pool_task.md:197-232;
  structural_driver.md:17-32 (`_chunk_spells` :2483-2509, `_build_chunked_phase_units` :2550-2617);
  phase_05.md (blueprint per owned spell before 8-11).
- Regime: cold conjure at workers > 1 only.
- Expected effect: HYPOTHESIS: at workers=5 wall 4.42ms (mult 2) vs a 2.84ms busy floor -> up to ~1.5ms
  (~35%) of plan wall; nothing at workers=1.
- Scope: two driver helpers, ~40 lines; a unit test for the assignment. Risk: LOW (assignment order does
  not change results; per-spell cancellation unchanged). IR alignment: neutral.
- Measurement: breakdown harness `par_eff` and skew at workers=2,5 with `BENCH_BREAKDOWN_CHUNK_MULT=2`.
- Collision: none known (driver chunking; not the emitters).

### C-K. Read contract sockets from the registered topology in phase 8 (remove the JIT reflection)
- Mechanism: `_iter_spell_contract_defaults` reads phase-1 `_requirements` rows and, when they are
  absent (they are reset after every pass), falls back to `inspect.signature(spell.spell)` per occurrence
  on the deferred/JIT 8-11 path. The registered `SpellLocalTopology` carries SPELL_CONTRACT sockets with
  their `contract_key` and survives the reset.
- Evidence: spell_occurrence_graph_analyzer_strategy.py:963-1031; structural_driver.md:24-27;
  phase_03.md (topology descriptors: socket_kind, contract_key).
- Regime: JIT 8-11 (spells not loaded from the cache) and local recompiles; also cold conjure (rows
  present, so no reflection - only the read moves).
- Expected effect: removes a reflection point from phase 8 (closure/IR requirement) and a per-occurrence
  `inspect.signature` on JIT; unmeasured, small.
- Scope: one strategy method. Risk: LOW-MEDIUM (the topology's contract key must equal
  `SpellContract.canonical_key`; phase_03.md says it does). IR alignment: strong (phase 8 stops touching
  user objects). Measurement: existing contract tests; a JIT-path test asserting no `inspect` call.
- Collision: phase 8 (updater_1 / melder_0 override lanes) - same as C-A.

### C-L. Shard phase 5 per root across workers (the serial floor)
- Mechanism: phase 5 builds one blueprint per root sequentially on one worker (~1.4ms June floor); roots
  are independent given the adjacency snapshot; the shared index and the attach loop stay serial.
- Evidence: phase_05.md:12-16, :35-48; June note :197-215 ("compiler-lane shard candidates").
- Regime: cold and warm conjure at workers > 1.
- Expected effect: at workers=5 up to ~1ms of the 1.4ms floor (HYPOTHESIS); nothing at workers=1.
- Scope: phase 5 builder loop and one more chunked phase in the resolution run (opposes C-B's
  barrier reduction: +1 barrier). Risk: MEDIUM (deterministic attach order; PathRegistry per blueprint
  is already per root). IR alignment: neutral-positive (per-root rows are independent by construction).
- Measurement: breakdown harness `root_blueprints` wall vs workers. Collision: none known.
- VERDICT: defer until C-B lands and the per-worker numbers show the floor matters.

### C-M. One closure computation instead of three (strategic)
- Mechanism: phase 3 (per spell, DAG with payloads), phase 5 (per root, blueprint DAG) and phase 8 (per
  root, occurrence graph) each re-derive the dependency closure from registry/topology rows. The IR's
  L2/L3 graph would be computed once per pass and consumed as rows by 5 and 8.
- Evidence: cost_model.md section 2 (derived counts); phase_03.md; phase_05.md; C2 note (phase 8 BFS).
- Regime: cold conjure mainly. Expected effect: unmeasured; bounded by phases 3 + 5 + 8 graph work.
- Scope: LARGE (schema story territory). Risk: HIGH now, LOW after STORY-2. IR alignment: it is the port.
- Measurement: breakdown harness per-phase rows. Collision: phases 5/8 (override lanes).
- VERDICT: strategic; not a tranche candidate before the schema story.

## Ranking per regime (counted and measured evidence only; effect sizes as stated above)
| regime | rank 1 | rank 2 | rank 3 | notes |
| --- | --- | --- | --- | --- |
| cold conjure (fresh process, miss or disabled) | C-A (dead O(N^2) hash in 8) | C-J (LPT chunking, W>1) | C-C (phase-3 DAG rows) | 8-11 own ~70% of phase time (June); C-K and C-B follow |
| warm conjure (.melc full hit) | C-G (snapshot: the only large lever) | C-C | C-B / C-E (trim the 1-7 floor) | import share out of scope by ruling |
| post-conjure bind, local recompile | C-B (one foundation unit, no duplicate CCM rebuild) | C-K | C-C | C-F parked |
| restore (many books) | C-G | C-B | C-C | scales with books; unmeasured |
| cache correctness (all regimes) | C-H | - | - | prerequisite for C-A and C-G |

## Recommended first tranche (small, measurable, inside the epic's boundary, no hot-path reach)
T1 = C-H + C-A + C-B, as one implementation story with three gauntlet-gated tasks:
1. C-H first (determinism test; one serializer) - it is the acceptance test for everything signature-based
   and it protects today's cache; sequence after melder_0's `shared_compiler_executions.py` hunks land.
2. C-A (phase 8: None check first; pass-invariant digest hoisted) - the one counted O(N^2) in the cold
   path; measured by the plan_group busy row; coordinate the file with updater_1 and melder_0.
3. C-B (one foundation unit; phase 7 reduced to its guard) - two barriers and one CCM rebuild fewer per
   conjure and per local recompile, and the hydrate unit shape C-G will need; component map updated.
Why not C-G first: it is the largest win on the warm path but needs four STORY-2 rulings, patch docs and
parity suites; T1 lands the prerequisites (deterministic signatures, one foundation unit) and is
measurable within a day. Why not C-J first: it pays only at workers > 1 and only on the cold path; it is
the natural second tranche together with C-C and C-K.
Falsifying measurement for T1: the breakdown harness at workers=1 and 5 before and after; if plan_group
busy does not fall after C-A and the fused phase's wall is not below the sum of the three, T1 delivered
structure only and the numbers say so.

## Parked, with reasons
- C-D dropped (single conjure per book makes it moot); C-F parked (semantic risk on the meld gate's input);
  C-I folded into whichever tranche opens those files; C-L deferred behind C-B; C-M is the schema story.

## Lane collisions (all flagged in the candidate cells)
- Phase 8 files: updater_1 (`override_occurrence_slicing`, review) and melder_0 (`override_design_melder`,
  review) - C-A, C-K, C-M.
- `shared_compiler_executions.py`: melder_0 (`missing_dependency_sockets`, implementation) - C-H.
- `spellbook_creation_system.py`: possibly melder_0 (step 3 conjure INFO report) - C-B, C-J.
- `caching_system.py` generation number: C-G, C-H (a signature change is a cache reset).
