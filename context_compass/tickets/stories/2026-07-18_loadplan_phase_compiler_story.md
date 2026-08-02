# Story: S4 - LoadPlan phase compiler + concurrency-safe parallel RestoreEngine

## Metadata
- Story ID: STORY-2026-07-18-loadplan-phase-compiler
- Epic: EPIC-2026-07-18-parallel-restore-ulid-identity
- Status: review (all 3 slices landed; pending owner 3.14t run)
- Owner: cowork
- Agent Name: UNASSIGNED (helper_f departed 2026-08-02, owner-directed; lane left ACTIVE)
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

- DATETIME: 2026-07-19T08:58:03Z
  TYPE: MEASURE
  CLAIM: REOPEN fix wave applied AND a dedicated regression wave added (29 new tests, 3
    files, all compile()-green on the 3.14t import chain; pytest Not run - device VM is
    CPython 3.11 and the melder package root uses 3.14 deferred annotations, so the owner's
    3.14t run executes them). (1) test_crystallizer_configuration_restore_knobs.py (12):
    the three restore getters default True/4/60000; roots-only config validates with the
    knobs ABSENT from _properties (the exact KeyError-shaped fixture); with_defaults installs
    all three; explicit values + both bool polarities read back; positive-int getter/validate
    discipline on the two int knobs; reload-lane backfills all three AND keeps recorded values
    over defaults; freeze rejection; and an end-to-end bare-activated-config read of the three
    properties the loader now uses (the fix's read path). (2)
    crystal_loader_system/test_restore_plan_levels.py (10): drives _build_plan_levels over
    seeded folded stores and asserts the exact 4-level canon structure plus per-edge parent-
    before-child placement (frame->book, book->link[both endpoints], book->cluster[all
    members], link->contract), unrecorded-frame-edge-not-drawn, edgeless nexus in level 0,
    empty world -> [], and determinism - the compiler path the phantom depends_on kwarg died
    on. (3) dag/test_dag_add_dependency_signature.py (7): pins add_dependency's real
    (parent_key, child_key, *, param_name, socket_kind) contract, parent-first ordering in
    both sort and levels, on-demand node creation, empty-key refusal, AND a direct lock that
    the retired depends_on= kwarg raises TypeError (routed via dict-unpack so no type:ignore
    is needed - synaptic ban honored; zero banned patterns across all three files).
  EVIDENCE:
  - tests/unit/melder/crystallizer/test_crystallizer_configuration_restore_knobs.py:1-1
  - tests/unit/melder/crystallizer/crystal_loader_system/test_restore_plan_levels.py:1-1
  - tests/component/melder/spellbook/spell_crafter/dag/test_dag_add_dependency_signature.py:1-1
  IMPACT: Every REOPEN root cause now has a symptom-named regression that would fail on the
    exact broken code (KeyError on bare activate; TypeError on depends_on=; wrong backfill
    list); the plan-graph shape is pinned so future edge-direction drift is caught at the
    unit layer, not only in the expensive integration parity suite.
  NEXT: Owner reruns 3.14t (the four fixes + these 29 regressions + the existing parity/chaos
    suites); green -> closure walkthrough + patch-lane promotion.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-19T09:11:06Z
  TYPE: MEASURE
  CLAIM: REOPEN fix wave LANDED + full test build-out across all three lanes. Fixes: (a)
    three typed defaulted properties on CrystallizerConfiguration (True/4/60000; house
    checkpoint_interval_minutes pattern) + Crystallizer.activate() reads them - the KeyError
    site is gone; validate() docstring names the new defaults. (b) All 5 engine plan-graph
    edges + 14 DAG-test call sites flipped to the real parent-first add_dependency
    signature; the flatten-law loop unpack renamed child_id/parent_id. (c) reload-lanes
    backfill expectation carries the 3 new schema keys (sorted-order machine-verified).
    Found on re-entry: two owner-side unit suites already landed against the fix
    (test_crystallizer_configuration_restore_knobs.py, 12 rows;
    test_restore_plan_levels.py, 10 rows) - every API contact in both verified against
    source (engine ctor kwargs, empty-fold-at-init seeding, cleanup law, error texts,
    in-level id ordering): SOUND. My additions: 5 loader unit rows
    (configure_restore_scheduler install/disable/replace/invalid/cleanup), a new component
    file (4 rows: roots-only activation wires the default parallel pool - the red-run
    fixture shape at the failing site; polarity False = no pool; explicit knobs reach
    pool.workers/barrier_timeout_ms; deactivate keeps + reactivate replaces), and 1
    integration arc (roots-only config end-to-end parallel restore of a sealed linked
    world: plan summary populated, spellbook=2/link=1 built, gate released). Two of my own
    mid-wave guesses were caught by the verify loop before landing: a phantom
    PhaseScheduler.describe() (real surface: workers/barrier_timeout_ms properties) and a
    wrong "book" built-count kind (real: "spellbook") - both corrected from source reads.
    compile() green x8 across every touched file; line cap clean. pytest Not run - the
    device VM is CPython 3.10 and cannot import the 3.14 deferred-annotation runtime
    (proven: NameError on a TYPE_CHECKING name at import); the whole wave rides the
    owner's 3.14t rerun. Version dev-suffix failure remains RAISED as pre-existing.
  EVIDENCE:
  - src/melder/crystallizer/configuration/crystallizer_configuration.py:365-460
  - src/melder/crystallizer/crystallizer.py:415-435
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:745-810
  - tests/unit/melder/crystallizer/test_crystallizer_configuration_restore_knobs.py:1-321
  - tests/unit/melder/crystallizer/crystal_loader_system/test_restore_plan_levels.py:1-353
  - tests/unit/melder/crystallizer/crystal_loader_system/test_crystal_loader_system.py:565-720
  - tests/component/melder/crystallizer/test_crystallizer_restore_policy_component.py:1-180
  - tests/integration/melder/crystallizer/test_crystallizer_restore_integration.py:2233-2306
  IMPACT: The REOPEN is code-complete with unit + component + integration coverage on
    every fixed surface; the phantom-kwarg and optional-knob regressions can no longer
    land silently.
  NEXT: Owner reruns 3.14t (recommend: pytest tests/unit/melder/crystallizer -q; pytest
    tests/component/melder/spellbook/spell_crafter/dag tests/component/melder/crystallizer
    -q; pytest -m integration -k restore). Green -> closure walkthrough + patch promotion.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-19T09:20:00Z
  TYPE: PLAN
  CLAIM: Owner-directed second safety wave (unit + component + integration), gap-driven:
    (U) RestoreReport concurrency/detachment/state-machine contract has ZERO direct rows
    (the S4 RLock law is only exercised incidentally) - new unit file: lost-update stress
    on record_built/map_identity/add_shortfall, describe() outer detachment + input
    detachment on set_plan_summary/set_preflight, ctor refusals, cleaned refusals,
    translate(), and _teardown_built newest-first best-effort order (raiser mid-stack must
    not stop the pop). (C) The S2+S3 composition - REAL PhaseScheduler pool workers passing
    a REAL held LoadGate - is asserted nowhere outside the full-world arcs; new component
    file beside test_creation_gate_component.py: enrolled idents pass while held, foreign
    thread times out naming the label, release clears membership so the NEXT span's
    un-enrolled unit fails through run_all_phases (fail-fast), holder-passes-alone sanity.
    (I) Three authority/failure arcs the suite lacks: unknown checkpoint id -> KeyError
    INSIDE the span still releases the gate (finally law); reloading a checkpoint over its
    own restored LIVE world fails mid-replay deterministically (named-conduit collision),
    tears down ONLY its own partial units, releases authority, original world intact
    (source-verified: _preflight_host skips world scope by contract - load_admission.py:437,
    so the failure is the replay's own, which is exactly the law worth pinning); and a
    worker_count=1 degenerate-pool parallel restore completes (no barrier/cohort deadlock).
  EVIDENCE:
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:116-341
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:2592-2614
  - src/melder/crystallizer/crystal_loader_system/crystal_loader_system.py:271-298
  - src/melder/crystallizer/crystal_loader_system/load_admission.py:409-470
  - src/melder/utilities/synchronization/load_gate.py:129-392
  IMPACT: Each lane pins a safety law that currently has no dedicated regression: report
    integrity under parallel writers, the worker-admission mechanism itself, and the
    authority-release guarantees on every refusal/failure path.
  NEXT: Land the three files/appends, compile()-verify, MEASURE note, board sync.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-19T09:35:00Z
  TYPE: MEASURE
  CLAIM: Safety wave 2 LANDED, all three lanes. UNIT (new
    test_restore_report_safety.py, 9 rows): record_built under 8-thread contention counts
    exactly (zero lost updates), identity-map + shortfall writers under 12 threads keep
    every row, describe() outer detachment (tampering a payload never writes through),
    set_plan_summary/set_preflight copy their INPUTS, failure state machine
    (failed+stage / complete+None), ctor identity refusals, cleaned-report refuses all 8
    verbs idempotently, _teardown_built pops newest-first THROUGH a raising unit (d-c-b-a
    with c exploding; stack empty, live maps cleared), and 6-thread _record_built_unit
    appends lose nothing. COMPONENT (new test_load_gate_scheduler_cohort_component.py, 3
    rows): REAL pool workers enrolled by the span holder pass wait_for_passage inside
    scheduler units while the gate is HELD, a foreign thread times out naming the span
    label then passes after release; release clears membership so the NEXT span's
    un-enrolled unit surfaces as PhaseExecutionError("level_0") through run_all_phases
    fail-fast; holder-alone passage sanity. INTEGRATION (3 arcs appended): unknown
    checkpoint id raises KeyError inside the span and the gate STILL releases (finally
    law; bind+conjure proceed after); reloading a checkpoint over its own restored LIVE
    world fails mid-replay on the frame's duplicate-conduit-name ValueError (source-
    verified aetheric_frame.py:319; world-scope loads skip host preflight by contract) -
    wrapped RuntimeError, gate released, standing world's alpha/beta still registered via
    the public cloud probe, teardown touched only the failing run's units (frames are
    postured, never stacked - verified: no _record_built_unit("frame") site exists);
    restore_scheduler_workers=1 degenerate pool completes a multi-level parallel restore
    (no barrier/cohort deadlock). compile() green x3; 120-col clean. pytest Not run -
    rides the owner's 3.14t run (device VM is 3.10, cannot import the runtime).
  EVIDENCE:
  - tests/unit/melder/crystallizer/crystal_loader_system/test_restore_report_safety.py:1-330
  - tests/component/melder/utilities/synchronization/test_load_gate_scheduler_cohort_component.py:1-200
  - tests/integration/melder/crystallizer/test_crystallizer_restore_integration.py:2307-2460
  - src/melder/aether/aetheric_frame/aetheric_frame.py:314-319
  IMPACT: The three safety pillars of the parallel program - report integrity under
    parallel writers, worker admission through the gate, and authority release on every
    refusal/failure path - now each carry dedicated regressions.
  NEXT: Owner reruns 3.14t (add: pytest tests/component/melder/utilities/synchronization
    -q); green -> closure walkthrough + patch promotion.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-19T09:55:00Z
  TYPE: PLAN
  CLAIM: Owner-directed wave 3 at fixed scale: 20 unit / 20 component / 10 integration
    rows, depth-first, zero filler. UNIT: new fold-safety file (later-wins, tombstone
    sweeps incl. book-subtree, journal-without-payload honesty, BUG-163 same-window churn
    silence, custody_location + spell_activity routing, contract/cluster eviction,
    nexus_state later-wins, crystallizer boot-slot), new engine-lifecycle file (empty-chain
    completion both drivers, single-use refusal, cleaned refusal, fold shortfalls riding
    describe()), +4 LoadGate rows (nested-acquire refusal, release refusals, 3-member
    concurrent cohort, mid-span withdrawal parks), +2 scheduler rows (explicit-lane timeout
    carries phase_name, ident-count law). COMPONENT: +5 DAG shape rows (wide star, deep
    chain, duplicate-edge set semantics, bulk-vs-individual edge parity, payload identity),
    +4 cohort rows (span repeatability, Aether-verb wiring, aether double-acquire/foreign
    release refusals, cleanup tombstone wakes waiters), +4 policy rows (recorded reload
    drives driver polarity, backfilled defaults reach pool width, configure-while-active
    refusal, record lane undisturbed by pool), new scheduler-pipeline file (barrier law at
    factory time, failed phase gates the next, persistent pool across runs, true 2-thread
    parallelism via shared Barrier), +3 record rows (contract twin in sealed window,
    contract_removed tombstone, cluster twin round trip). INTEGRATION: 2-generation
    re-checkpoint lineage, cluster world parallel restore, staged/selection parity across
    drivers, recorded-policy-twin driving driver selection on reload, formation restore
    under the pool (plan summary at conduit scope), skip_existing formation compose over a
    live world, width-4 chaos (3 books, 1 poisoned), functional borrower meld after
    parallel restore, identity-map completeness over recorded ids, full-vocabulary world
    parity. Every asserted surface source-verified this pass (fold kinds
    restore_engine.py:1103-1162, gate acquire/release refusals load_gate.py:129-334,
    restore_formation skip_existing crystallizer.py:1799-1830, record_built kinds incl.
    cluster_member/contract_detail:2239-2357).
  EVIDENCE:
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:1027-1215
  - src/melder/utilities/synchronization/load_gate.py:129-392
  - src/melder/crystallizer/crystallizer.py:1799-1860
  - tests/integration/melder/crystallizer/test_crystallizer_restore_integration.py:740-800
  IMPACT: Fold truth, gate refusal edges, barrier law, record round trips, and six unseen
    end-to-end lanes gain dedicated regressions at the owner's requested scale.
  NEXT: Land files in bounded slices, compile()-verify each, MEASURE + board sync.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-19T09:50:17Z
  TYPE: MEASURE
  CLAIM: Wave 3 LANDED at the owner's exact scale: 20 unit + 20 component + 10
    integration rows, every asserted surface source-verified before writing. UNIT (20):
    fold-safety file (9: later-wins, spellbook-subtree tombstone sweep, capture-anomaly
    honesty, BUG-163 same-window churn silence [corrected mid-wave to the REAL
    contract_removed vocabulary - conduit_removed does not exist], custody routing +
    activity flips, spell/contract/cluster eviction, nexus_state later-wins + boot slots),
    engine-lifecycle file (5: empty-world completion on BOTH drivers incl. the parallel
    zero-level plan, single-use refusal, cleaned refusal, fold shortfalls riding the
    returned report), +4 LoadGate rows (held-acquire refusals from both threads, release
    pairing refusals, 3-member concurrent passage [rewritten once - first draft carried
    dead scaffolding, purged], label/is_held lifecycle), +2 scheduler rows (explicit-lane
    timeout carries phase_name, ident-count/stability law). COMPONENT (20): +5 DAG (40-wide
    star, 60-deep chain, duplicate-edge set semantics [a doubled edge must not fabricate a
    phantom cycle], bulk-vs-individual parity, payload object identity), +4 cohort (span
    repeatability on one persistent pool, Aether-verb delegation with real hosted
    singletons, double-acquire/foreign-release refusals at the Aether layer, cleanup
    tombstone wakes a REAL parked waiter), +4 policy (recorded polarity drives driver
    selection, backfill floor reaches pool width 4/60000, configure-while-active refusal,
    record lane undisturbed by the owned pool), pipeline file (4: barrier law at factory
    time, failed level gates the next factory, persistent pool across runs, true 2-thread
    parallelism via shared Barrier rendezvous), +3 record (contract twin with both
    endpoints in the sealed window, contract_removed tombstone in the next window,
    cluster twin membership + eviction round trip [emit_cluster_removed verified at
    crystallizer.py:973 before use]). INTEGRATION (10): 2-generation re-checkpoint lineage,
    cluster world parallel rebuild (cluster=1, cluster_member=2), staged-member parity on
    both drivers, recorded-policy-twin -> reload lane -> sequential driver end to end,
    formation restore under the pool (plan + scope-aware clean admission), skip_existing
    formation compose over a live world (unnamed-conjure shortfall, resident survives),
    width-4 three-book chaos (level named, report failed, zero survivors), restored
    borrower MELDS the granted spell through the identity map (the world WORKS), identity-
    map completeness over every recorded structural id incl. the contract ULID with
    never-rehydrate proven per id, and the full-vocabulary superset parity arc (link +
    cluster + grant + staged in ONE world, all outcome surfaces equal across drivers).
    compile() green x10; 120-col clean x10; touched suites now carry 161 test defs.
    pytest Not run - rides the owner's 3.14t run.
  EVIDENCE:
  - tests/unit/melder/crystallizer/crystal_loader_system/test_restore_fold_safety.py:1-330
  - tests/unit/melder/crystallizer/crystal_loader_system/test_restore_engine_lifecycle.py:1-190
  - tests/unit/melder/utilities/synchronization/test_load_gate.py:471-680
  - tests/unit/melder/utilities/synchronization/test_phase_scheduler.py:523-590
  - tests/component/melder/spellbook/spell_crafter/dag/test_spellbook_component_dag_graph_core.py:440-580
  - tests/component/melder/utilities/synchronization/test_load_gate_scheduler_cohort_component.py:190-380
  - tests/component/melder/crystallizer/test_crystallizer_restore_policy_component.py:180-300
  - tests/component/melder/crystallizer/test_crystallizer_record_component.py:277-400
  - tests/component/melder/utilities/synchronization/test_phase_scheduler_pipeline_component.py:1-190
  - tests/integration/melder/crystallizer/test_crystallizer_restore_integration.py:2450-3010
  IMPACT: Fold truth, gate pairing edges, barrier/parallelism laws, record round trips,
    and six previously-unseen end-to-end lanes (lineage, cluster, staged parity, recorded
    polarity, functional meld, full vocabulary) are all pinned at the owner's requested
    density.
  NEXT: Owner reruns 3.14t (previous command set plus pytest
    tests/unit/melder/crystallizer/crystal_loader_system -q); green -> closure walkthrough
    + patch promotion.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-19T10:27:00Z
  TYPE: FACT
  CLAIM: REOPEN wave-3 failure (2) root-caused - the cleaned-conduit husks in
    test_wide_pool_chaos_tears_down_three_book_world expose a REAL production race, not a
    wrong assertion. Chain: (a) PhaseLatch.record_error fires the barrier on the FIRST
    unit failure while sibling units keep RUNNING (documented fail-fast: "without waiting
    for stragglers"); workers never interrupt mid-run bodies - cancel is a pre-run check
    only. (b) _run_single_phase raises PhaseExecutionError immediately; the engine's
    failure handler then runs _teardown_built() on the caller thread WHILE straggler
    _replay_one_book bodies still execute on pool workers. (c) A straggler that passes
    conjure registers its conduit into the frame and LATE-APPENDS to _built_stack; the
    LIFO drain can pop-and-clean that straggler's SPELLBOOK before the conduit lands, then
    pop the late conduit AFTER - _cleanup_normal_conduit step 4 first calls
    _unregister_conduit_spells_from_aether on the already-cleaned book whose _spells was
    del'd, raises AttributeError, the step-4 broad except swallows it, and
    _remove_root_conduit() NEVER RUNS: a cleaned husk stays in frame._conduits (the exact
    observed symptom - dict repr raises "Conduit has already been cleaned"). Alternative
    interleaving (append after drain exits) leaks a LIVE conduit instead. (d)
    _teardown_built's trailing _live_books/_live_conduits .clear() also races straggler
    writes. The 2-book chaos test passes only by race odds (1 straggler vs 2 at width 4);
    both are exposed. Quiesce is implementable: the worker loop reports EVERY dequeued
    unit into its latch exactly once, so "all units reported" is a bounded waitable state.
  EVIDENCE:
  - src/melder/utilities/synchronization/phase_latch.py:83-100
  - src/melder/utilities/synchronization/phase_scheduler.py:712-736
  - src/melder/utilities/synchronization/phase_scheduler.py:594-638
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:2592-2614
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:1810-1819
  - src/melder/aether/conduit/conduit.py:758-765
  - src/melder/aether/spellbook/spellbook.py:379-385
  - src/melder/aether/aetheric_frame/aetheric_frame.py:328-360
  IMPACT: The all-or-nothing law is violated by design under fail-fast: any parallel
    restore that fails a level with sibling units mid-flight can leave cleaned husks (or
    live leaks) registered in the frame. The test is CORRECT and must stand as the
    regression; the fix is production-side.
  NEXT: DECISION_REQUEST to the owner - scheduler quiesce-before-raise (bounded wait for
    all units to report after fail-fast cancel) + step-4 hardening ruling.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-19T10:28:30Z
  TYPE: FACT
  CLAIM: REOPEN wave-3 failure (1) root-caused - my test design flaw, system behaved by
    design. test_skip_existing_formation_composes_over_a_live_world composes the SAME
    formation twice into one frame: the second compose re-binds RestoreAlpha's
    content-stable SHA256 spell id, and Aether registration refuses ("Spell ID collision
    detected") at level_0 BEFORE the conduit-name skip lane can matter. The skip vocabulary
    is conduit names + cluster reuse ONLY (host preflight blockers downgrade to
    "skipped_existing" and arm the engine lanes; verified in execute_plan and
    _preflight_host - spells are never a skip lane). Composing one formation twice into the
    same frame is unsupported by design; the test must collide on the NAME only.
  EVIDENCE:
  - src/melder/crystallizer/crystal_loader_system/load_admission.py:310-505
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:1789-1816
  - tests/integration/melder/crystallizer/test_crystallizer_restore_integration.py:2726-2766
  IMPACT: Test restructure is in-scope and unambiguous; no production change needed for
    this failure.
  NEXT: Restructure per the PLAN note below.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-19T10:30:00Z
  TYPE: PLAN
  CLAIM: Fix plan for both rows. (1) Restructure the skip test to a name-only collision:
    seal "skip-formation" (book binds RestoreAlpha, conduit "keeper"); _fresh_boot(); build
    a LIVE world from a DIFFERENT book binding RestoreGamma with conduit named "keeper"
    (capture its live id); restore_formation("skip-formation", skip_existing=True); assert
    status complete, shortfall reason "conduit_name_taken_built_unnamed" present, the
    resident "keeper" survives as the SAME live conduit id, and the composed world built
    spellbook/conduit counts. (2) Production race (owner ruling required, patch-gated
    concurrency change): add PhaseLatch.wait_all_reported(timeout) (additive verb - second
    event/condition firing when remaining reaches zero) and have _run_single_phase's
    fail-fast error path QUIESCE (bounded by the remaining barrier budget) after
    cancelling the run and BEFORE raising PhaseExecutionError, so no unit body is
    mid-flight when the engine's teardown runs; the timeout path stays preemptive by
    documented contract. Secondary hardening (recommended, same ruling):
    _cleanup_normal_conduit step 4 splits its single try so _remove_root_conduit() runs
    first and each verb fails independently - frame truth must not be hostage to spellbook
    state. Wide-chaos test stays UNCHANGED as the regression.
  EVIDENCE:
  - src/melder/utilities/synchronization/phase_latch.py:64-100
  - src/melder/utilities/synchronization/phase_scheduler.py:700-740
  - src/melder/aether/conduit/conduit.py:756-766
  IMPACT: Row (1) unblocks immediately; row (2) closes the all-or-nothing gap for every
    parallel restore, not just the test.
  NEXT: Land the test restructure now; present the DECISION_REQUEST for (2) in-session.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-19T10:32:00Z
  TYPE: MEASURE
  CLAIM: Skip-lane test restructured to the name-only collision (fix row 1 of the owner's
    red pair). New arrangement: seal "skip-formation" (RestoreAlpha book + conduit
    "keeper"), _fresh_boot(), build the live resident from a DIFFERENT book (RestoreGamma)
    under the SAME name "keeper", then ONE compose with skip_existing=True. Assertions:
    status complete, engine shortfall "conduit_name_taken_built_unnamed" present,
    built_counts spellbook==1/conduit==1, the resident survives as the SAME live id via
    the public cloud verbs (has_conduit_name + get_conduit), and survivor.cleaned is
    False. The double-compose arrangement (same formation twice = same content-stable
    spell SHA re-bound = Aether spell-id collision by design) is retired; the docstring
    now teaches that spells never join the skip vocabulary. Every touched surface
    source-verified: get_conduit raises-not-None (conduit_cloud.py:234-257), Cleanable
    exposes .cleaned (cleanable.py:43), host-blocker downgrade arms the engine lane
    (load_admission.py:355-378 execute_plan). compile() green on the full file; 120-col
    clean; test-def count unchanged at 46. pytest Not run - rides the owner's 3.14t
    rerun (device VM cannot import the 3.14 runtime). Fix row 2 (wide-chaos husks) is a
    REAL production fail-fast race per the 10:27 FACT note: test stands unchanged as the
    regression; scheduler quiesce fix awaits the owner ruling (patch-gated concurrency
    change).
  EVIDENCE:
  - tests/integration/melder/crystallizer/test_crystallizer_restore_integration.py:2726-2790
  - src/melder/aether/aetheric_frame/conduit_cloud.py:234-257
  - src/melder/crystallizer/crystal_loader_system/load_admission.py:355-378
  IMPACT: Red row 1 is code-complete; red row 2 is a ruled decision away from its fix.
  NEXT: Owner rules on the quiesce + step-4 hardening proposal; on approval land the
    patch delta + scheduler/latch change; then owner reruns 3.14t.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-19T10:45:00Z
  TYPE: MEASURE
  CLAIM: Owner-approved fix wave for red row 2 LANDED (investigate-first per directive;
    every surface read before edit). PATCH ARTIFACTS FIRST (gate law):
    code_description_patch_phase_scheduler_quiesce.md (full control flow, edge semantics,
    hung-straggler residual, non-goals), component_patch_conduit_cleanup_frame_truth.md
    (step-4 before/after + ordering-safety evidence), and a dated delta section in
    component_patch_phase_scheduler_seam.md. CODE (all CRLF-preserved, byte-safe): (1)
    PhaseLatch gains _all_reported_event (set at remaining<=0 in BOTH complete and
    record_error) + wait_all_reported(timeout) quiesce verb + contract docstrings;
    termination law verified in source before design - the worker loop reports EVERY
    dequeued unit exactly once and already-done units no-op to complete()
    (run_for_scheduler done()-check read directly). (2) _run_single_phase fail-fast path
    quiesces AFTER cancel+set_exception and BEFORE raising PhaseExecutionError, bounded by
    the same barrier budget; timeout path stays preemptive by documented contract;
    class + method docstrings updated. (3) _cleanup_normal_conduit step 4 split into three
    independent try/excepts with _remove_root_conduit() FIRST - ordering safety
    source-verified (_remove_spells_from_aether works the frame SPELL registry keyed by
    conduit id via frame.unregister_conduit_spells and never reads frame._conduits).
    REGRESSIONS: +2 latch unit rows (quiesce barrier lags the fail-fast wake; cross-thread
    last-report wake), +1 scheduler unit row (Event-sequenced straggler: its final side
    effect is visible BEFORE run_all_phases raises - no sleeps, deterministic), new
    component file test_conduit_component_cleanup_frame_truth.py (2 rows: out-of-order
    book-first teardown leaves frame._conduits/_conduit_ids_by_name empty + public cloud
    probes agree; in-order lane byte-equal guard). The wide-pool chaos integration test
    stands UNCHANGED as the law's regression. Pre-existing conflicts checked: the
    hung-straggler fail-fast unit test (block_event released only in finally) now pays the
    bounded quiesce timeout then raises identically - still passes; the existing
    fail-fast-on-cancel and timeout rows are untouched paths. compile() green x7 (latch,
    scheduler, conduit, 3 test files, integration file); 120-col clean on every touched
    region (5 over-cap lines in conduit.py are pre-existing docstrings far from the edit,
    one with historic mojibake - not touched per no-drive-by law; flagged here). pytest
    Not run - rides the owner's 3.14t rerun.
  EVIDENCE:
  - context_compass/system_docs/patches/active/parallel_restore_ulid_identity_2026_07_18/code_description_patch_phase_scheduler_quiesce.md:1-1
  - context_compass/system_docs/patches/active/parallel_restore_ulid_identity_2026_07_18/component_patch_conduit_cleanup_frame_truth.md:1-1
  - src/melder/utilities/synchronization/phase_latch.py:44-160
  - src/melder/utilities/synchronization/phase_scheduler.py:713-760
  - src/melder/aether/conduit/conduit.py:758-782
  - tests/unit/melder/utilities/synchronization/test_phase_latch.py:72-115
  - tests/unit/melder/utilities/synchronization/test_phase_scheduler.py:300-350
  - tests/component/melder/aether/conduit/test_conduit_component_cleanup_frame_truth.py:1-145
  IMPACT: Both red rows are code-complete: the skip test collides on the name only, and
    the fail-fast unwind can no longer race straggler unit bodies - the husk factory is
    closed at the scheduler seam AND the frame registry is hardened against every other
    out-of-order teardown lane.
  NEXT: Owner reruns 3.14t (previous command set plus pytest
    tests/component/melder/aether/conduit -q); green -> closure walkthrough + patch-lane
    promotion (now including the two new patch docs).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Final assembly: compiles the canon partial order onto the scheduler inside the cohort span.
