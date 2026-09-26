# Cost model: the conjure pipeline (driver, scheduler, phases 1-11, cache load, hydration)

Recorded 2026-09-26 by fable_0 (STORY-2026-09-26-phase-pipeline-improvement-plan, task 1, steps C1-C4).
Status: COMPLETE. Evidence tiers: SOURCE (read this session: `utilities/synchronization/phase_scheduler.py`,
`unit_of_work.py`, `phase_latch.py`, `phases/compiler_phase_8.py`, `compiler_phase_11.py`,
`spell_analyzer/spell_analyzer.py`, `spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py`,
`dag/dag_node.py`, the graph, processor, planner and codegen-creation entry methods); RECORD (the survey
records under `artifacts/ir_phase_survey_20260925/`, each COMPLETE); MEASURE (owner-run, cited below). Counted
facts are from source; timings are measured only where a MEASURE row says so, otherwise "unmeasured".
Ranges without a file are into the file named in the same cell. Nothing here was executed: "Not run."

## 1. Regimes (what runs when)
| regime | driver path | phases that run | what is skipped | record |
| --- | --- | --- | --- | --- |
| cold conjure (fresh process, cache disabled or miss) | `conjure` -> structural run -> resolution run -> emit envelope | 1-4 per spell; 5, 6, 7 once; 8-11 per resolvable spell (fused `plan_group`) | nothing | structural_driver.md, resolution_driver.md |
| warm conjure (`.melc` full hit) | same, `force_skip_plan_phases=True`; lazy `CreationContext` per cached spell | 1-4 per spell; 5, 6, 7 once | 8-11; verdict enforcement | resolution_driver.md:17-31 |
| mixed hit | as cold for the missing spells; cached spells load lazily | 1-7; 8-11 for every eligible spell (skip is all-or-nothing per run) | none of the phases | resolution_driver.md:17-27 |
| post-conjure bind (dynamic) | `run_post_conjure_structural_phases` | 1-4 sequentially, new spells only (no scheduler) | 5-11 until a gate fires | structural_driver.md:42-47 |
| meld-time local recompile (gated lineage) | `run_resolution_phases_for_target_spell` | 5-7 local, then 8-11 for the target | frame-wide 5-7 | structural_driver.md:48-56 |
| deferred / JIT plan | `run_deferred_resolution_phases_for_target_spell` | 8-11 for one spell | 1-7 | structural_driver.md:53-55 |
| first meld after a hit | hydration seam (`generalized_binding_resolver`) | executor factory build (`compile`) | - | resolution_driver.md:45-66 |

## 2. Counted cost per stage (one conjure of N spells, R resolvable roots, W workers)
| stage | when | unit shape | per-conjure work counted from source | allocations and locks | registry / runtime writes | memo or skip | evidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| driver: conjure | every conjure | control thread | CONJURE transaction; freeze config; cache classification (`_build_conjure_cache_state`: live id set vs cached ids); TWO scheduler runs; `cleanup_phase_artifacts_after_resolution`; ownership wiring; envelope emit | one `SpellCompilerSystem` per run (compiler + validator with 13 strategies), a THIRD one built only to reset artifacts; per run a fresh `resolution_pass_cache`, `validation_pass_cache`, `analysis_pass_cache` | conduit id mint; envelope file (temp + atomic replace) | classification decides only 8-11 | structural_driver.md:17-32, :36-40; resolution_driver.md:17-31; cache_seam.md |
| scheduler | every run (2 per conjure) | 6 or 7 `_run_single_phase` calls: 3 structural (chunked, <= W units), 3 single-unit (5, 6, 7), `plan_group` chunked (<= 2W units; empty on a full hit) | per phase: `factory()`, one `PhaseLatch`, one queue put per unit, ONE control-thread `Event.wait` (control -> worker -> control), per-unit `uow.exception()` post-scan; per run a new `CancellationEventSignal`; `clear_phases` | per phase: Lock + 2 Events + list; per unit: `Future` (Condition + lists) + one `RLock`; W daemon threads spawned once per Spellbook, joined at cleanup | none | units always run on workers (inline path reverted) | phase_scheduler.py:683-756, :758-906, :913-974; unit_of_work.py:156-218, :458-522; phase_latch.py:125-187 |
| phase 1 requirements | per spell, fused with 2 | chunk unit | BORROWED from the bind-time profile when the spell id matches (no reflection); else `inspect.signature` + annotation evaluation in the user module | per parameter row 13 slots + one RLock; one RLock per requirements object | artifact only | idempotent when `_requirements` set; reset after every pass | phase_01.md; structural_driver.md:22-24 |
| phase 2 symbolic graph | per spell, fused with 1 | same unit | pure function of the phase-1 rows | one graph + one edge per parameter, one RLock each (N+1 locks per spell) | artifact only | none; reset after every pass | phase_02.md:49-52 |
| phase 3 local frame | per spell, hard barriers both sides | chunk unit | one query over `_spell_id_pool` through the pass candidate index (built once per pass, keyed on `id()`; disabled when any pool object or frame has a custom `__eq__`, then a `==` scan per dependency); SpellMap defaults always scan; one DAG per spell | per DAG: ULID + RLock + 2 dicts; per node 2 sets + list + 2 dicts; per edge 3 re-entrant lock acquisitions + 2 set adds + 2 dict entries; topological sort (heap, sorted dependents) | `update_dependencies` (reverse edges; gates and dirties the lineage), `register_local_topology` (rebuilds two reverse indexes), `Spell._add_build_details` (stores the DAG, invalidates the creation context), Nexus publication | pass index only | phase_03.md; dag_node.py:45-83, :159-198; directed_acyclic_work_graph.py:56-68, :122-221, :255-296 |
| phase 4 validation | per spell, behind the phase-3 barrier | chunk unit | 13 strategies in registry order over one context; cross-spell reads of other spells' phase-1 rows and phase-3 topologies; `contract_provider_map` and `binding_resolution_graph` built once per pass | result + issue objects (Cleanable) | lineage validity: `clear_dirty(time.time())` + valid / gated `contract_unvalidated` / invalid | skip rule never fires in a conjure (phase 3 gates first) | phase_04.md |
| phase 5 root blueprints | once per conjure, lead spell | single unit | adjacency over registry private fields; roots; one blueprint per structural root plus one per owned non-root; BFS socket overlay interning paths into `PathRegistry`; `SpellSystemIndex` of value nodes | per blueprint: a second `DirectedAcyclicWorkGraph` (ULID + RLock) with payload None; per node one `SpellSystemNode` (Cleanable); lazily built `DagIndex` | per OWNED spell: attach index + blueprint, `requires_spellspace_request`; invalidates occurrence analysis, codegen outputs and the creation context; CCM `rebuild_component_of` + `set_revalidator` | none | phase_05.md:35-48, :50-60 |
| phase 6 system validation | once per conjure, lead spell | single unit | 23 strategy instances built fresh per run; reads every pool spell's `_is_broken` and phase-4 presence; verdict only | verdict + diagnostics objects, shared onto EVERY artifact | per conduit `ConduitResolutionState`: two validity maps (bulk), diagnostics (cloned), `clear_conduit_dirty(time.time())`; RiskManager fan-out per changed id | none | phase_06.md:21-31, :44-58 |
| phase 7 change control | once per conjure, lead spell | single unit | filters owned roots (two throwaway `CompilerPhase5()` instances), `rebuild_component_of` AGAIN (second time this conjure), `set_revalidator` (no-op: phase 5 registered it) | two phase-5 objects; CCM maps rebuilt | CCM component-of map (clears dirty state twice per conjure) | guard on the revalidator only | phase_07.md:15-22, :29-44 |
| phase 8 occurrence analysis | per resolvable root, fused in `plan_group` | chunk unit | per pass: one sorted pool walk and one graph-shape row build over every topology and contracted map (memoized in `analysis_pass_cache`); per root: `_build_root_blueprint_rows` twice, `hash_codegen_signature` over root rows PLUS the pool-wide rows (pool-sized pickle + sha256 per root), BFS over the closure (topology lookup, `extend_path` per socket target, contract-defaults scan of phase-1 rows or `inspect.signature` when absent), second BFS for ordered nodes off the root path, edge/topology/fallback counts | occurrence dict + deque + 3 sets per root; `SpellOccurrenceGraphAnalysis` (Cleanable); one `SpellAnalyzer` + strategy builder per pass | artifact: `_occurrence_graph_analysis`, fast key, input signature | skip check compares key, signature AND `_occurrence_graph_analysis is not None` LAST; phase 5 nulls that slot every pass, so the key work never pays on conjure | compiler_phase_8.py:74-123; spell_occurrence_graph_analyzer_strategy.py:118-253, :267-372, :374-508, :719-858, :860-1031; compiler_phase_5.py:182-216 |
| phase 9 processor | per resolvable root, same unit | chunk unit | shell model from spell facts + analyzer graph (depth/width walk over the occurrence graph), every registered processor strategy in order | `SpellCodegenModel` (Cleanable); previous model cleaned | artifact `_spell_codegen_model` | NONE: always rebuilds | spell_artifact_processor.py:62-105; driver.md (closed at the call level) |
| phase 10 planner | per resolvable root, same unit | chunk unit | discovery over the model, one plan strategy applied | `SpellCodegenPlan` (Cleanable); previous plan cleaned | artifact `_spell_codegen_plan` | NONE: always rebuilds; planner subtree imported lazily ("~11ms") | spell_codegen_planner.py:61-123; driver.md |
| phase 11 codegen creation | per resolvable root, same unit | chunk unit | discovery over model + plan, ordered creation strategies, emit + `compile` of the executor lanes, step-row export (memoized on the plan) | `SpellCodegenCreation` (Cleanable); code objects; one `CodegenCreationSystem` per phase object, subtree imported once per process (~28ms, 77 modules) | artifact `_spell_codegen_creation`; conjure-end cache export | NONE per spell; the creation cache (full hit) is the only skip | compiler_phase_11.py:48-127; codegen_creation_system.py:56-126; driver.md |
| cache load (full hit) | after ownership wiring | control thread | per cached spell: `get_spell_payload` (nested marshal), manifest validate, three COLD doors, `CreationContext.load_cached`; ZERO phase 1-7 reads | one `CreationContext` + gate per spell; one-time lazy import of the strategy cache modules | `resolution_complete`, `resolution_required`, `_door_epoch` | already cache-driven | resolution_driver.md:33-45 |
| hydration (first meld) | per spell on first meld | meld thread | binding resolver: `spellbook._spell_id_pool[id]` per step spell id and `artifact._root_blueprint_phase5.path_registry`; `get_or_build_executor_factory` compiles the lanes | executor factories; code objects | executor published on the context | executor factory cache | resolution_driver.md:46-66 |

Derived counts per conjure (from the table): DAG-shaped closures are materialized THREE times (phase-3 DAG
per spell with live payloads, phase-5 blueprint DAG per root, phase-8 occurrence graph per root) plus phase
2's edge objects; the lineage registry is gated and dirtied by phase 3 and cleared by phase 4 for every spell
on every conjure; the CCM component-of map and dirty sets are rebuilt twice; the RiskManager fan-out fires for
every per-conduit validity change written by phase 6.

## 3. Measured (owner-run; two sources; nothing re-run here)
| stage | June breakdown harness, unprofiled (2026-06-12) | cProfile gauntlet dump (2026-09-25) | caveats |
| --- | --- | --- | --- |
| whole conjure | setup disabled 23.6ms; warm setup 9.4ms; warm conjure 6.1ms (medians) | `Spellbook.conjure` 44.2ms cum | dump is a profiled, warm, full-hit run on the 3.14 free-threaded build (GIL enabled per the epic's MEASURE note); profiler inflation ~3x vs June |
| structural run (1-4) | "tiny" (multiplier 1 kept because finer chunks made it slower) | 11.0ms: phase 1 0.50ms/29, phase 2 0.46ms/29, phase 3 5.07ms/29 (`_build_local_frame_dag` 4.37ms), phase 4 4.06ms/29 | 29 spells; one chunk per phase (workers=1 in that run) |
| phase 5 | ~1.4ms (serial floor) | 5.0ms (`run_frame_wide`) | single unit |
| phase 6 | ~0.7ms (serial floor) | 3.16ms | single unit |
| phase 7 | not separated | < 0.15ms | single unit |
| plan_group (8-11) | ~14.2ms busy of ~20ms phase time; wall 14.8 / 9.9 / 5.2ms at workers 1/2/5; chunk_mult 2 -> 4.42ms | skipped (full hit) | 2.46x load skew at workers=5 with contiguous chunks; RequestRoot ~2.3ms vs ~0.1ms leaves |
| scheduler control overhead | "no longer the dominant setup cost" | `run_all_phases` 0.12ms tot; `_run_single_phase` 0.06ms tot; latch wait 19.04ms cum vs unit bodies 18.73ms cum: ~0.3ms of handoff over 6 barriers | thread-spawn moved to Spellbook teardown (2.3ms `PhaseScheduler.cleanup`) |
| cache classification | - | `_build_conjure_cache_state` 0.75ms | - |
| cache load (full hit) | - | 22.05ms for 29 payloads, of which ~19ms is `_find_and_load` (2 imports) inside `load_creation_context_lazy`: one-time import; ~3ms of per-spell work | module cost is out of scope by owner ruling |
| bind | - | `Spellbook.bind` 17.97ms/29 (0.62ms each; `Bind.bind` 7.67ms) | outside the epic; the level-0 capture lives here |
| first-meld hydration | - | `_hydrate_once` 27.4ms/17; `get_or_build_executor_factory` 24.2ms; `builtins.compile` 46 calls 14.3ms | outside conjure; pays once per spell per process |
| cleanup of artifacts | - | `cleanup_phase_artifacts_after_resolution` 0.41ms | builds a throwaway compiler system |
Sources: `tickets/tasks/completed/2026-06-12_phase_scheduler_v2_persistent_pool_task.md:164-232` (MEASURE
notes; harness `benchmarks/testing_other_di/profile_phase_scheduler_breakdown.py`, 29 classes, repeats 5,
caching disabled); `benchmarks/testing_other_di/results/real_world_gauntlet_melder.prof` (pstats query by
function name; `test_real_world_gauntlet_cprofile.py`, 25 iterations). The dump's cumtime interleaves across
threads (the gauntlet `cleanup` frame carries the run); the per-phase rows above are the leaf-side functions
and are internally consistent (structural 11.0 = 0.5 + 0.46 + 5.07 + 4.06 + chunk overhead).
CORRECTION to the pre-compaction note: the dump DOES carry worker-thread frames (`run_for_scheduler` 6 calls,
`PhaseLatch.wait` 6 calls, phase bodies attributed), so per-phase attribution needs no new harness on 3.12+.

## 4. Where the time goes, by regime (measured where a row above says so, else counted)
- Cold conjure: plan_group 8-11 owns ~70% of phase time at workers=1 (June); 5-7 serial floor ~2.1ms; 1-4
  small. Phases 8-11 are full rebuilds per root by construction (no memo below the creation cache).
- Warm conjure (full hit): 1-7 compute ~20ms of the 44ms profiled conjure (~45%); the remainder is the
  one-time strategy-module import and per-spell context publication. Unprofiled: 6.1ms total, split
  unmeasured (the breakdown harness disables caching; see section 5 for the warm variant).
- Post-conjure bind and local recompile: 1-4 sequential for the new spells, then 5-7 frame-wide again on the
  next gate; the JIT 8-11 path re-reflects in phase 8 because the phase-1 rows were reset (C2 note).
- Restore: conjure through the public path per book; the same 1-7 cost times the number of books, plus
  ULID re-minting; unmeasured.

## 5. Owner-run measurement (the command that yields per-phase timings for the gauntlet's book)
- Command (native free-threaded interpreter, repository root):
  `python benchmarks/testing_other_di/profile_phase_scheduler_breakdown.py`
  Env knobs: `BENCH_BREAKDOWN_WORKERS` (default `1,2,5`), `BENCH_BREAKDOWN_REPEATS` (default 5),
  `BENCH_BREAKDOWN_CHUNK_MULT` (default `1`). Output: per-phase barrier wall vs summed worker busy time,
  unit counts, per-spell durations inside chunks, `par_eff` for multi-unit phases. Contract: caching
  disabled, so 8-11 always run; fresh Aether per cycle; 29 binds (profile_phase_scheduler_breakdown.py:1-40,
  :256-283).
- Warm-path split (1-7 vs cache load on a full hit): the harness has no caching-enabled mode; the
  existing dump already attributes it under the profiler (section 3). A caching-enabled toggle in the
  harness is a benchmarks/ edit (owner-run or owner-approved), not requested here.
- Status: Not run. Recorded numbers are the two owner-run sources above.

## 6. Structural observations the candidates draw on (counted, not judged here)
1. Phase 8 computes a pool-sized signature per root that cannot hit on the conjure path (phase 5 nulls the
   analysis every pass; the None check is last). Reordering the check or memoizing the pass-invariant hash
   removes O(spells^2) work per cold conjure.
2. The phase-3 DAG object has one production reader (a presence warning) and is rebuilt per spell per
   conjure with live payloads; `Spell.dependencies` carries the ids the runtime uses.
3. Phases 5 and 7 both rebuild the component-of map and clear dirty state; phase 7's revalidator call is a
   no-op; three single-unit phases cost three barriers and three thread handoffs per run.
4. Phases 1-4 reset their artifacts after every pass and re-run on every conjure although their inputs
   (bind-time facts) and outputs (registry rows) are unchanged for unchanged spells; the dormant phase 2-5
   export already defines the row schema (summary.md D2/D3).
5. Phase 6 fans out RiskManager callbacks and phase 3/4 gate-then-clear the lineage for every spell on every
   conjure, including full hits; the meld gate reads the same registry rows.
6. Each run builds a compiler system (13 validation strategies) and each phase-6 run 23 strategy objects; a
   third compiler system exists only to reset artifacts.
7. The JIT 8-11 path reflects (`inspect.signature`) in phase 8 when phase-1 rows are absent.

## 7. UNKNOWN (with where to look)
- Exact per-spell cost split inside the structural run at workers > 1 (chunk overhead vs body): the
  breakdown harness output (owner-run).
- Phase 9/10 strategy internals (3,087 and 5,574 lines): what each strategy walks; read when a candidate
  needs a per-strategy count.
- Whether `SpellAnalyzerStrategyBuilder` / the processor and planner builders construct strategy instances
  per call or per builder: `spell_analyzer_strategy_builder.py`, `spell_artifact_processor_strategy_builder.py`.
- Whether the warm-path 1-7 compute is dominated by phase 3 (pool query + DAG) or phase 4 (13 strategies)
  when unprofiled: the breakdown harness at workers=1 gives the per-phase wall.
