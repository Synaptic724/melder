# Story: S4 - LoadPlan phase compiler + concurrency-safe parallel RestoreEngine

## Metadata
- Story ID: STORY-2026-07-18-loadplan-phase-compiler
- Epic: EPIC-2026-07-18-parallel-restore-ulid-identity
- Status: in_progress (slice 1/3 landed)
- Owner: cowork
- Agent Name: helper_f
- Priority: p0
- Created: 2026-07-18T22:30:00Z
- Updated: 2026-07-18T22:30:00Z

## Objective
(AMENDED 2026-07-18, owner second ruling: graph planner.) After fold, build a
RestorePlanGraph - DirectedAcyclicWorkGraph over per-entity nodes (config roots, nexus
root, frames, book chains, link rows, clusters, contracts) with recorded dependency edges -
flatten it via an additive topological_levels() verb, and load one scheduler phase per
level on the loader-owned PhaseScheduler inside the cohort span. Entity placement
(including nexus, currently a recorded leaf: restore_engine.py:1035-1094) is graph-derived.
All-or-nothing, never-rehydrate-ULIDs, and shortfall honesty preserved; outcome parity with
the sequential engine (canon baseline) proven by suite; recorded-edge cycles refuse at
admission.

## Ticket Contract
- ENTRY_GATE: S1+S2+S3 landed; restore-engine component patch AND its code_description
  patch (authored at story start - concurrency-sensitive trigger) linked and read.
- EXECUTION_BOUNDARY: restore_engine.py (stage bodies -> unit factories; thread-safe report
  + built-stack), load_admission.py execute_plan (phase registration), crystal_loader_system
  (scheduler ownership + cohort enrollment), tests. Public loader verbs unchanged.
- DEPENDENCIES: component_patch_restore_engine_parallel.md; S1 (link units), S2 (scheduler),
  S3 (cohort gate).
- EXIT_GATE: parity suite green (identical built counts/shortfalls/identity coverage vs
  sequential baseline on the same chain); chaos suite green (mid-phase unit failure ->
  full reverse teardown, nothing leaks); owner measures wall-clock improvement.
- FAILURE_ESCALATION: CONFLICT if parity diverges; BLOCKER on teardown nondeterminism;
  DECISION_REQUEST before relaxing any stage barrier.

## Scope Boundaries
- In scope: phase compilation, unit factories (per-book chain, per-link, per-cluster,
  per-contract), lock-appended built stack, RestoreReport internal lock, parity harness.
- Out of scope: emit batching (measure-first, owner sign-off); head-stage parallelism.

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: component patch authored; final assembly tranche.

## Steps / Checklist
- [ ] Author code_description_patch_restore_engine_parallel.md BEFORE code.
- [ ] Additive DirectedAcyclicWorkGraph.topological_levels() (Kahn by layers; existing
      sort()/execute() untouched - spell compiler suites must stay green unmodified).
- [ ] RestorePlanGraph builder over the folded bundle: nodes + recorded dependency edges
      (book->frame; link->both book-chains; cluster->member chains; contract->chain+frame;
      nexus edges only when the record carries nexus-native constructs).
- [ ] Cycle refusal at admission (BLOCKER verdict path; nothing built).
- [ ] Level -> phase registration; unit factories per node (book node = today's interior
      chain); identity-map reads only from already-passed levels.
- [ ] Thread-safe RestoreReport (one internal lock; describe() unchanged) +
      lock-appended _built_stack (global reverse teardown preserved).
- [ ] Fail-fast: PhaseExecutionError -> mark_failed(stage) -> teardown -> chained raise
      (all-or-nothing law identical to today).
- [ ] Parity + chaos + contention suites (>= 20 tests/100 LOC on the engine deltas).

## Validation
- Not run. Recommended: pytest -m integration -k restore_parity; owner 3.14t run with
  timing comparison on a multi-book world.

## Applicable Anti-Patterns
- [ ] No identity-map read across an unfinished barrier.
- [ ] No snapshotting owned registries into locals without documented correctness need.

## Noting Behavior
- Story notes: cross-task synthesis and gate transitions.

## Notes
- DATETIME: 2026-07-18T23:55:46Z
  TYPE: MEASURE
  CLAIM: Slice 1/3 landed behind the gate law. (1)
    code_description_patch_restore_engine_parallel.md authored FIRST with the full target
    control flow: driver selection via new config key restore_parallel_enabled (FIRST
    LANDING DEFAULTS FALSE - capability ships dark, owner flips after parity greens; the
    flag is the rollback lane), sequential prologue + inline head stages, engine-internal
    plan graph (node/edge law incl. edgeless nexus), level flatten, one scheduler run with
    one phase per level, per-entity unit refactor shared by BOTH drivers (parity by
    construction), thread-safety deltas (report RLock; _build_lock on the built stack;
    3.14t atomic dict law for per-key disjoint writes), cohort span wiring, failure/
    idempotency/non-goal laws. (2) DirectedAcyclicWorkGraph.topological_levels() landed:
    Kahn peeling by layers under the existing graph lock, ascending-id in-level order
    (sort()'s tie law), identical cycle refusal; sort()/execute() untouched. Six component
    regressions: diamond, disjoint components share levels, coarsening-of-sort law, empty +
    singleton, cycle refusal parity, side-effect-free repeatability. (3)
    PhaseScheduler.worker_thread_idents() landed: starts the persistent pool idempotently,
    returns a detached sorted ident list; two regressions (start-once + detachment +
    post-probe run, cleaned refusal). AST + device py_compile green x4. NOTE: a stale
    stage snapshot briefly looked like a device-side revert of the scheduler test file;
    live-file sentinel checks proved all S1-S3 deltas present - staging raced the dir
    cache, no data loss.
  EVIDENCE:
  - system_docs/patches/active/parallel_restore_ulid_identity_2026_07_18/code_description_patch_restore_engine_parallel.md:1-1
  - src/melder/aether/spellbook/spell_compiler/dag/directed_acyclic_work_graph.py:278-343
  - src/melder/utilities/synchronization/phase_scheduler.py:430-465
  - tests/component/melder/spellbook/spell_crafter/dag/test_spellbook_component_dag_graph_core.py:280-420
  IMPACT: Every primitive the parallel driver needs now exists; remaining work is engine
    surgery + loader wiring + parity/chaos suites.
  NEXT: Slice 2/3 - refactor stage loops into per-entity methods, add the plan-graph
    builder + parallel driver to RestoreEngine, thread-safe report/built-stack.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Final assembly: compiles the canon partial order onto the scheduler inside the cohort span.
