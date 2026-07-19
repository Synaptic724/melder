# Story: S4 - LoadPlan phase compiler + concurrency-safe parallel RestoreEngine

## Metadata
- Story ID: STORY-2026-07-18-loadplan-phase-compiler
- Epic: EPIC-2026-07-18-parallel-restore-ulid-identity
- Status: review (all 3 slices landed; pending owner 3.14t run)
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
- DATETIME: 2026-07-19T00:34:32Z
  TYPE: MEASURE
  CLAIM: Slices 2+3 landed; S4 code-complete. Slice 2 (restore_engine.py, +~560 lines):
    RestoreReport gained an internal RLock (all mutators/readers; describe() +"plan" key);
    engine gained borrowed scheduler collaborator + _build_lock'd _record_built_unit (all
    5 append sites routed); _ensure_frame_postured's check-then-act serialized (fresh-frame
    double-posture race); five per-entity methods extracted (frames/book/link/cluster/
    contract - both drivers share them, parity by construction); restore() dispatches to
    _restore_sequential (byte-preserved canon chain) or _restore_parallel (inline head ->
    _build_plan_levels on DirectedAcyclicWorkGraph -> one phase per level, heavy-first ->
    identical all-or-nothing failure law naming the failed level). OWNER INTERVENTIONS
    honored mid-slice: (a) getattr probe on phase exceptions REMOVED - explicit
    (PhaseExecutionError, PhaseTimeoutError) catch reading .phase_name off the owned
    contract; (b) two extraction leftovers (loop `continue` at function level in
    _replay_one_cluster/_replay_one_contract) fixed to `return` - caught because device
    py_compile runs full compile(); ast.parse does NOT check loop-control legality -
    verification upgraded to compile() everywhere. Slice 3: loader owns the pool
    (configure_restore_scheduler installed at Crystallizer.activate from frozen config),
    cohort enrollment via _enroll_restore_cohort (release clears membership by S3 law -
    withdrawal ceremony struck), execute_plan passes the borrowed scheduler through,
    restore_parallel_enabled key DEFAULTS TRUE (owner polarity ruling 2026-07-19:
    "no stupid shims" - parallel IS the driver; False = sequential fallback). Parity
    regression (same sealed multi-book/link/contract world, both drivers: identical
    built_counts, sorted shortfalls, identity-map key set; plan summary present only on
    parallel; gate released after) + chaos regression (poisoned conduit in a 2-book chain
    on a real 2-worker pool: RuntimeError names level_N, frame holds zero conduits).
    Device py_compile green x5. pytest Not run - the whole epic rides the owner's 3.14t
    run.
  EVIDENCE:
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:1-2614
  - src/melder/crystallizer/crystal_loader_system/crystal_loader_system.py:1-1
  - src/melder/crystallizer/crystallizer.py:407-430
  - tests/integration/melder/crystallizer/test_crystallizer_restore_integration.py:2023-2232
  IMPACT: The epic's full capability is landed: identity everywhere, order from the
    journal, graph-derived parallel replay behind the cohort gate, parallel as the driver.
  NEXT: Owner runs 3.14t (recommend: pytest tests/unit/melder/utilities/synchronization/
    -q, pytest tests/component/melder/spellbook/spell_crafter/dag -q, pytest -m
    integration -k restore); green -> closure walkthrough + patch-lane promotion into
    canonical C-docs/graph.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-19T01:20:00Z
  TYPE: MEASURE
  CLAIM: REOPEN - owner 3.14t run RED (23 failed / 120 errors). Root-caused to four rows,
    three mine: (a) Crystallizer.activate() read the three restore knobs with unconditional
    get_property - KeyError for every fixture that activates a configuration built without
    with_defaults(); that violates validate()'s documented defaulted-optional contract. Fix:
    three typed defaulted properties on CrystallizerConfiguration (house pattern:
    checkpoint_interval_minutes) and activate() reads them. (b)
    DirectedAcyclicWorkGraph.add_dependency's real signature is (parent_key, child_key, *,
    param_name, socket_kind) - the depends_on kwarg I called NEVER existed (signature
    guessed, not read: an Unknowns-Gate violation). Every parallel restore failed at
    plan_graph and the 5 edge-drawing DAG tests failed on the same TypeError. Fix:
    parent-first calls at 5 engine sites + 12 test sites. (c) reload-lanes backfill
    expectation updated: the three new schema keys legitimately join the with_defaults
    backfill floor. (d) test_package_version_reexport_appends_dev_suffix is PRE-EXISTING
    and unrelated: src/melder/__init__.py:45 appends ".dev0" only under DEBUG_MODE while
    the test expects "-dev" unconditionally; last touched by 693eaf588 (pre-epic). RAISED
    to the owner, not fixed (scope law).
  EVIDENCE:
  - src/melder/crystallizer/crystallizer.py:421-437
  - src/melder/crystallizer/configuration/crystallizer_configuration.py:442-462
  - src/melder/aether/spellbook/spell_compiler/dag/directed_acyclic_work_graph.py:161-168
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:751-805
  - tests/component/melder/spellbook/spell_crafter/dag/test_spellbook_component_dag_graph_core.py:313-433
  - tests/unit/melder/aether/test_configuration_reload_lanes.py:246-252
  - src/melder/__init__.py:45-45
  IMPACT: All four target surfaces identified with source evidence before edits; the config
    fix is the documented optionality surface (typed properties), not a probe or fallback.
  NEXT: Land the fix wave in one bounded slice, compile()-verify every touched file, commit
    byte-safe, hand back for the owner rerun.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Final assembly: compiles the canon partial order onto the scheduler inside the cohort span.
