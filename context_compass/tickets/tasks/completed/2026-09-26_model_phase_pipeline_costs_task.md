# Task: Model the per-phase cost of the conjure pipeline from source and specify its measurement

- Completed: 2026-09-26T13:27:19Z
- Summary: cost_model.md (counted rows from source plus measured rows from two owner-run sources) gives the
  per-stage cost of phases 1-11 that the candidate ranking drew on. Owner turned in 2026-09-26T13:27:19Z.

## Metadata
- Task ID: TASK-2026-09-26-model-phase-pipeline-costs
- Story: STORY-2026-09-26-phase-pipeline-improvement-plan
- Status: done
- Owner: cowork
- Agent Name: fable_0
- Priority: p1
- Created: 2026-09-26T07:42:51Z
- Updated: 2026-09-26T13:27:19Z

## Objective
Produce `cost_model.md`: for the driver and each phase 1-11, what one conjure costs in passes over the
pool, objects allocated per spell, locks taken, registry writes, barriers and scheduler units, from
source (survey records first, new reads only where the records stop), plus one owner-run command that
yields per-phase timings for the gauntlet's book.

## Ticket Contract
- ENTRY_GATE: Story opened on owner direction; active board row routes here.
- EXECUTION_BOUNDARY: Read-only over `spell_compiler/**` (phases 8 and 11, `dag/dag_node.py`,
  `symbolic_graph/`, `artifact_processor/` and `codegen_planner/` at structure level), the driver
  ranges already surveyed, and `utilities/synchronization/phase_scheduler.py`. Writes limited to this
  ticket, the story, and `artifacts/ir_phase_improvement_20260926/`.
- DEPENDENCIES: artifacts/ir_phase_survey_20260925/ (all records).
- EXIT_GATE: `cost_model.md` exists with a row per stage and evidence ranges; the measurement command
  is specified; status review.
- FAILURE_ESCALATION: BLOCKER if a stage's cost surface cannot be established from source; CONFLICT
  if a cited range is under active edit by another lane.

## Scope Boundaries
- In scope: counted facts (passes, allocations, locks, writes, units, barriers) per stage; the
  scheduler's per-run cost surface; phases 8-11 at the level of what runs per spell and what is
  memoized.
- Out of scope: the meld hot path, any edit under `src/` or `tests/`, running anything.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: Created and routed by fable_0 on the owner's direction (2026-09-26).
- from_state: in_progress
- to_state: review
- transition_reason: C1-C4 complete; cost_model.md exists with a row per stage, evidence ranges and
  the owner-run measurement specified (2026-09-26); exit gate met; awaiting owner acceptance.
- from_state: review
- to_state: done
- transition_reason: Owner turned in fable_0's finished review tickets ("turn in your shit if your done",
  2026-09-26T13:27:19Z); records retained as reference; boards synced.

## Steps / Checklist
- [x] C1: read `utilities/synchronization/phase_scheduler.py` whole (1-500, 501-988): units, chunking,
      barriers, worker handoff, cancellation, per-run allocations. (2026-09-26, DONE; unit_of_work.py and
      phase_latch.py read whole with it)
- [x] C2: read `phases/compiler_phase_8.py` and `compiler_phase_11.py` whole; locate the analyzer,
      processor, planner and codegen entry points and what each memoizes (structure level). (2026-09-26, DONE;
      occurrence strategy read whole)
- [x] C3: read `dag/dag_node.py` whole; count per-node/per-edge allocations and locks for phases 2-3
      (with phase_02.md / phase_03.md). (2026-09-26, DONE)
- [x] C4: write `cost_model.md` (one row per stage; measured column "unmeasured"); specify the owner-run
      per-phase timing command; task -> review. (2026-09-26, DONE)
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- artifacts/ir_phase_improvement_20260926/cost_model.md

## Files / Paths Impacted
- None under `src/` or `tests/`. This ticket, the story, and the artifact directory only.

## Validation
- Not run.
- Recommended commands:
  - (owner-run) `python benchmarks/testing_other_di/profile_phase_scheduler_breakdown.py`
    (env: BENCH_BREAKDOWN_WORKERS, BENCH_BREAKDOWN_REPEATS, BENCH_BREAKDOWN_CHUNK_MULT).

## Risks / Rollback Notes
- `phase_scheduler.py` is outside `spell_compiler/**`; it is read because the driver's per-run cost
  lives there (expansion recorded in the story's boundary).
- Another lane edits `spell_compiler/**` now; ranges are dated and re-verified before reuse.

## Applicable Anti-Patterns
- [x] No status transition without evidence-backed transition reason.
- [x] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [x] No closure without acceptance confirmation and board-sync completion.
- [x] No cost claim from a name or docstring; each count cites the code that allocates or locks.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
- [x] Acceptance criteria reviewed with user and confirmed
- [x] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/ir_phase_improvement_20260926/
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: Story closure.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: per-phase cost surface; scheduler cost; measurement command.
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-09-26T07:42:51Z
  TYPE: PLAN
  CLAIM: Read order C1 scheduler, C2 phases 8 and 11, C3 dag_node, then C4 the cost model. Survey
    records supply phases 1-7 and the drivers; no surveyed source is re-read.
  EVIDENCE:
  - src/melder/utilities/synchronization/phase_scheduler.py:1-988
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_8.py:1-123
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_11.py:1-127
  - src/melder/aether/spellbook/spell_compiler/dag/dag_node.py:1-239
  IMPACT: Bounds the reading to about 1,500 new lines.
  NEXT: C1: phase_scheduler.py 1-500.
  REREAD: REQUIRED
  SCORE_0_TO_10: 7

- DATETIME: 2026-09-26T08:03:51Z
  TYPE: FACT
  CLAIM: C1 read whole (phase_scheduler.py 988, unit_of_work.py 522, phase_latch.py 253). Scheduler cost
    surface per conjure: TWO `run_all_phases` runs (structural: requirements_symbolic, local_frame,
    validation, chunked; resolution: root_blueprints, system_validation, change_control single units
    plus plan_group chunked, skipped on a full hit), so 6 or 7 `_run_single_phase` calls. Each phase
    allocates one `PhaseLatch` (Lock + 2 Events + list), one `factory()` call, one queue put per unit
    and ONE control-thread `Event.wait` (control -> worker -> control handoff); the clean path then
    reads `uow.exception()` per unit (Future condition lock each). Each `UnitOfWork` costs a Future
    (`Future.__init__`: Condition + lists) plus its own RLock; `run_for_scheduler` is lock-free and
    reports once. Each run replaces the `CancellationEventSignal`. Workers: N daemon threads spawned
    once per Spellbook (`phase_scheduler_workers_per_spellbook`), joined only at cleanup; units always
    execute on workers (inline workers==1 path tried and REVERTED for the control contract). Barrier
    timeout from `phase_scheduler_barrier_timeout_milliseconds`. The owner's 2026-09-25 cProfile dump
    DOES carry worker frames (`run_for_scheduler` 6 calls, `PhaseLatch.wait` 6 calls 19.0ms cum),
    consistent with 3.12+ cProfile riding sys.monitoring across threads; the pre-compaction note that
    phase bodies are invisible on the main thread is WRONG and is corrected in cost_model.md.
  EVIDENCE:
  - src/melder/utilities/synchronization/phase_scheduler.py:221-315
  - src/melder/utilities/synchronization/phase_scheduler.py:683-756
  - src/melder/utilities/synchronization/phase_scheduler.py:758-906
  - src/melder/utilities/synchronization/phase_scheduler.py:913-974
  - src/melder/utilities/synchronization/unit_of_work.py:156-218
  - src/melder/utilities/synchronization/unit_of_work.py:458-522
  - src/melder/utilities/synchronization/phase_latch.py:125-187
  - artifacts/ir_phase_survey_20260925/structural_driver.md:17-32
  - artifacts/ir_phase_survey_20260925/resolution_driver.md:17-27
  - benchmarks/testing_other_di/results/real_world_gauntlet_melder.prof
  IMPACT: Fixes the scheduler's counted cost per conjure (6-7 barriers, 6-7 thread handoffs, one
    latch and one signal set per phase, one Future+RLock per unit) and shows the owner's dump can
    attribute per-phase time without a new harness.
  NEXT: C2: read compiler_phase_8.py (123) and compiler_phase_11.py (127) whole, then the analyzer
    strategy entry; note the memoization surface.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-09-26T08:06:27Z
  TYPE: FACT
  CLAIM: C2 read whole: compiler_phase_8.py, compiler_phase_11.py, spell_analyzer.py, the occurrence
    graph strategy (1187), the processor, planner and codegen-creation entry facades. Phase 8 per pass:
    one pool walk (`phase8_spell_walk`) and one graph-shape row build over every local topology and
    contracted map (`phase8_graph_shape_rows`), both memoized in `analysis_pass_cache`. Phase 8 per
    root: `_build_root_blueprint_rows` TWICE (fast key and signature), then `hash_codegen_signature`
    over the root rows PLUS the pool-wide spell/topology/contract rows, i.e. one pool-sized pickle
    and sha256 per spell (O(spells^2) per pass); the skip check that this key serves compares
    `_occurrence_graph_analysis is not None` LAST, and phase 5's attach nulls that slot on every pass
    (`_cleanup_occurrence_analysis_artifacts` at all three attach points), so on the conjure path the
    key and signature are computed and never hit; no other module reads the two slots (grep). The
    graph build is a BFS over the root's closure: per occurrence one topology lookup, one
    `extend_path` per socket target, one contract-defaults scan reading phase-1 `_requirements`
    rows, falling back to `inspect.signature(spell.spell)` when the rows are absent (they are reset
    after every pass, so the deferred/JIT 8-11 path reflects at meld time), plus a second BFS for
    ordered nodes outside the root path. Phases 9, 10 and 11 have NO skip or memo: each rebuilds
    model, plan and creation per spell per pass (previous object cleaned); phase 11 lazily imports
    the codegen subtree once per process under a class lock and builds a `CodegenCreationSystem`
    per phase object. Phases 8-11 gate on `spell.resolvable`; existing-creation roots no-op in 8.
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_8.py:74-123
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_11.py:48-127
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/spell_analyzer.py:99-162
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:118-253
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:267-372
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:374-508
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:580-658
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:719-858
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:860-1031
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_5.py:182-216
  - src/melder/aether/spellbook/spell_compiler/phases/compiler_phase_5.py:546-554
  - src/melder/aether/spellbook/spell_compiler/spell_compiler_artifact.py:304-324
  - src/melder/aether/spellbook/spell_compiler/artifact_processor/spell_artifact_processor.py:62-105
  - src/melder/aether/spellbook/spell_compiler/codegen_planner/spell_codegen_planner.py:61-123
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/codegen_creation_system.py:56-126
  IMPACT: Two counted wastes for the cost model: a pool-sized hash per spell that cannot hit on conjure,
    and a phase-8 reflection point on the JIT path; phases 9-11 are full rebuilds by construction, so
    their cost scales with spells x plan size and only the creation cache (full hit) avoids them.
  NEXT: C3: read dag/dag_node.py whole; count per-node/per-edge allocations and locks for phases 2-3
    against phase_02.md and phase_03.md.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T08:07:45Z
  TYPE: FACT
  CLAIM: C3 read: dag_node.py whole plus the graph's constructor, add_node, add_dependency and
    topological_sort. Per `DirectedAcyclicWorkGraph`: one ULID mint, one RLock, two dicts. Per node:
    a `DagNode` with two sets, one list, two dicts, no lock. Per edge: the graph RLock is acquired
    three times (add_dependency, then add_node twice, re-entrant), two set adds, one dict entry, one
    setdefault set, one `_socket_kinds` entry keyed by node pair. Phase 3 builds one such DAG per
    spell per conjure with live Spell payloads (phase_03.md); phase 5 builds another per root with
    payload None (phase_05.md); phase 8 builds the occurrence graph per root (C2 note): three
    materializations of one closure per conjure, plus phase 2's symbolic graph with one RLock per
    edge (phase_02.md). The phase-3 DAG object stored as `Spell.dependency_graph` has ONE reader in
    src outside Spell itself: the phase-4 presence strategy's `is None` warning check; cleanup and
    `_add_build_details` are the only other touches (grep). Eight test files reference it (49 hits).
  EVIDENCE:
  - src/melder/aether/spellbook/spell_compiler/dag/dag_node.py:45-83
  - src/melder/aether/spellbook/spell_compiler/dag/dag_node.py:159-198
  - src/melder/aether/spellbook/spell_compiler/dag/directed_acyclic_work_graph.py:56-68
  - src/melder/aether/spellbook/spell_compiler/dag/directed_acyclic_work_graph.py:122-221
  - src/melder/aether/spellbook/spell_compiler/dag/directed_acyclic_work_graph.py:255-296
  - src/melder/aether/spellbook/spell_compiler/validation/strategies/resolution_frame_presence_strategy.py:90-103
  - src/melder/aether/spellbook/spell.py:1443-1480
  - artifacts/ir_phase_survey_20260925/phase_02.md:49-52
  - artifacts/ir_phase_survey_20260925/phase_03.md:24-32
  - artifacts/ir_phase_survey_20260925/phase_05.md:35-48
  IMPACT: Gives the allocation and lock counts per node and edge for the cost model and promotes the
    "drop the phase-3 DAG object" candidate from UNKNOWN to source-backed: its only production reader
    is a presence check that the value rows (`Spell.dependencies`) can satisfy.
  NEXT: C4: pull the per-phase MEASURE rows (June breakdown; the 2026-09-25 cProfile dump) and write
    cost_model.md; then task -> review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-26T08:12:10Z
  TYPE: FACT
  CLAIM: C4 done: cost_model.md written (121 lines): regimes table, a counted row per stage (driver,
    scheduler, phases 1-11, cache load, first-meld hydration) with allocations, locks, registry writes
    and memo/skip surface, a MEASURE table from the two owner-run sources, the by-regime split, the
    owner-run command (`profile_phase_scheduler_breakdown.py` with its three env knobs; warm-path
    split needs a caching-enabled harness mode that does not exist), seven structural observations
    for candidates.md, and the UNKNOWNs. Headline measured facts: warm profiled conjure 44.2ms of
    which phases 1-7 are ~20ms and the cached-context load 22ms is ~19ms one-time import; cold
    unprofiled plan_group ~14.2ms busy of ~20ms phase time (June); scheduler handoff ~0.3ms over 6
    barriers. Task 1 exit gate met: row per stage with evidence, measurement specified. "Not run."
  EVIDENCE:
  - artifacts/ir_phase_improvement_20260926/cost_model.md:1-121
  - tickets/tasks/completed/2026-06-12_phase_scheduler_v2_persistent_pool_task.md:164-232
  - benchmarks/testing_other_di/results/real_world_gauntlet_melder.prof
  - benchmarks/testing_other_di/profile_phase_scheduler_breakdown.py:1-40
  - benchmarks/testing_other_di/profile_phase_scheduler_breakdown.py:256-283
  IMPACT: Task 2 can rank candidates against counted and measured cost per regime without re-reading
    the compiler; the cold-path lever is 8-11, the warm-path lever is 1-7 plus the import.
  NEXT: Task 1 -> review; open task 2 (candidates, ranking, one STRATEGY_DISCUSSION on the epic).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
STATE 2026-09-26T07:42:51Z: in progress. Resume at C1: `phase_scheduler.py` 1-500, then 501-988.
STATE 2026-09-26T08:03:51Z: re-onboarded after compaction; C1 done and noted (pre-compaction reads were
unrecorded and were redone). Resume at C2: `phases/compiler_phase_8.py` whole, `compiler_phase_11.py` whole,
then the analyzer entry.
STATE 2026-09-26T08:06:27Z: C2 done and noted. Resume at C3: `dag/dag_node.py` whole (239), then the DAG graph class it
belongs to if phase_03.md leaves the per-edge lock count open; write the C3 note; then C4 cost_model.md.
STATE 2026-09-26T08:07:45Z: C3 done and noted. Resume at C4: read the June MEASURE note
(tickets/tasks/completed/2026-06-12_phase_scheduler_v2_persistent_pool_task.md:164-232) and query the owner's
cProfile dump for per-phase rows; write artifacts/ir_phase_improvement_20260926/cost_model.md; task -> review.
STATE 2026-09-26T08:12:10Z: C4 done; task 1 in REVIEW (cost_model.md complete). Nothing further to read here; task 2
(candidates.md, ranking, one epic strategy note) carries the story on.
STATE 2026-09-26T13:27:19Z: DONE. Owner turned in the ticket; record retained under artifacts/; closed with its story.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
