# Code Description Patch: RestorePlanGraph compiler + parallel RestoreEngine (S4)

Lane: parallel_restore_ulid_identity_2026_07_18.
Ticket: STORY-2026-07-18-loadplan-phase-compiler.
Concurrency-sensitive entry-gate artifact required before ANY S4 engine/loader code.

## Control Flow (target)

1. DRIVER SELECTION. RestoreEngine gains an optional constructor collaborator
   `scheduler: Optional[PhaseScheduler]`. `restore()` dispatches: scheduler None ->
   today's sequential body, UNTOUCHED (the parity baseline and the rollback lane);
   scheduler present -> the graph-planned parallel driver. Selection is owned by the
   loader through the new CrystallizerConfiguration key `restore_parallel_enabled`
   (bool). FIRST LANDING DEFAULTS FALSE: the capability ships dark, the owner flips one
   config value after the parity suite greens on 3.14t. Rollback = the same flag.
2. SEQUENTIAL PROLOGUE (both drivers, unchanged): fold -> preflight -> admission
   refusal on blockers. Then, parallel driver only: sequential HEAD replay INLINE on the
   loading thread - aether_configuration, crystallizer_policy, mutation_research
   (process-global config roots; single-unit, no parallelism to win).
3. PLAN GRAPH. Engine-internal builder over the folded stores constructs one
   DirectedAcyclicWorkGraph: node keys "kind:key" with descriptor payloads -
   nexus:root (edgeless today; placement becomes graph-derived the moment the record
   carries nexus-native edges), frame:<name>, book:<spellbook_id>, link:<a>-><b>,
   cluster:<cluster_id>, contract:<contract_id>. Edges (dependency -> dependent):
   frame -> its books; book -> links touching its conduits (both endpoints); book ->
   clusters containing its conduits; book(+frame) -> contracts on its conduits; link ->
   its contract-detail node when the folded contract carries details (details re-grant
   after the edge exists). A cycle raises at plan time: mark_failed("plan_graph"),
   NOTHING built, teach-grade RuntimeError (admission-style refusal).
4. FLATTEN. New additive DirectedAcyclicWorkGraph.topological_levels(): Kahn peeling by
   layers under the existing graph lock; level N = all nodes whose dependencies live in
   levels < N; deterministic in-level order (node id sort, matching topological_sort's
   tie law); same cycle error as topological_sort. sort()/execute() untouched.
5. EXECUTE. One scheduler run for the whole plan: for each level, register one phase
   ("level_0", "level_1", ...) whose factory builds one UnitOfWork per node via
   create_unit_of_work (run-scoped cancellation). Heavy-first in-level enqueue order:
   book nodes before frame/link/cluster/contract nodes (makespan heuristic; barriers
   unchanged). run_all_phases() drives level barriers; PhaseLatch fail-fast + timeout
   semantics apply per level.
6. UNITS call the SAME per-entity bodies the sequential driver uses. S4 refactors the
   stage loops into per-entity methods - _replay_one_frame, _replay_one_book (the
   existing per-book interior chain verbatim: config freeze -> active binds in
   bind_order -> conjure -> staged binds -> selections), _replay_one_link (S1 identity
   mapping included), _replay_one_cluster, _replay_one_contract - and BOTH drivers call
   them. Parity by construction, not by parallel-only reimplementation.
7. FAILURE. PhaseExecutionError / PhaseTimeoutError / PhaseSchedulerError ->
   mark_failed("level_N") -> _teardown_built() (global reverse build order) -> chained
   RuntimeError. All-or-nothing law identical to the sequential driver. Scheduler run
   cancellation guarantees no unit starts after the first failure's barrier wake.
8. COHORT SPAN (loader). CrystalLoaderSystem owns one lazily-constructed persistent
   PhaseScheduler (S2 explicit lane; workers/timeout from the crystallizer config keys),
   cleaned in loader cleanup BEFORE borrowed derefs. Load verbs, inside the existing
   acquire_load_authority span: scheduler.worker_thread_idents() (new additive verb:
   starts the pool if needed, returns detached ident list) -> aether.enroll_load_worker
   per ident -> execute -> finally: withdraw per ident, release authority. Enrollment
   failures abort the load BEFORE any replay (authority released by the existing
   finally).

## Thread-Safety Deltas

- RestoreReport: gains one internal RLock in __slots__; every mutator
  (record_built/add_shortfall/map_identity/set_preflight/mark_*) and describe()/
  translate() lock it. Shape of describe() unchanged; "no lock by contract" docstring
  law REWRITTEN to name the lock (single-writer contract retired with the parallel
  driver).
- Engine build bookkeeping: _built_stack appends under one new engine _build_lock -
  append order IS teardown order, so ordering is lock-serialized. _live_books /
  _live_conduits / _live_indexes writes are per-key disjoint across units; under 3.14t
  the builtin dict's internal lock makes single-key put/get atomic (owner's runtime
  law), and cross-level reads happen only after the producing level's barrier - no
  additional locks, documented in the engine docstring.
- Identity-map reads by units (links/clusters/contracts resolving endpoints) occur only
  in levels strictly after the producing book level - guaranteed by graph edges, not by
  discipline.
- Re-emission during parallel replay serializes on the PersistenceSystem instance RLock
  (existing contract); cross-entity emission order is run-nondeterministic and
  fold-irrelevant (later-wins per key; each twin is a complete self-snapshot).

## Edge / Error Semantics

- Empty plan (no frames/books/links/clusters/contracts): zero level phases; prologue +
  report complete (parity with sequential on empty worlds).
- Scheduler misconfiguration (workers/timeout invalid) surfaces at loader construction
  time (S2 validation), never mid-replay.
- Cohort enrollment after cleanup / outside span: S3 refusals propagate as load
  failures before replay starts.
- A unit raising OperationCancelledError after a sibling failure reports as cancelled
  (scheduler law), not as a second failure; the first cause chains.

## Idempotency

- Engine stays single-use (`restore()` raises on a second call) in BOTH drivers.
- topological_levels() is side-effect-free and repeatable; plan build is pure over the
  folded stores.

## Explicit Non-Goals

- No emit batching; no head-stage parallelism; no barrier relaxation between levels.
- No public loader verb changes (load_checkpoint / restore_formation_record shapes fixed).
- No spell-compiler DAG behavior changes (sort/execute byte-identical; levels additive).
- No retirement of the sequential driver (owner decision, later).

## Validation Expectations

- DAG: topological_levels unit rows (linear chain, diamond, disjoint components,
  singleton, cycle refusal, determinism, sort() untouched proof).
- Scheduler: worker_thread_idents rows (starts pool once, detached list, stable across
  runs, cleaned refusal).
- Parity: same sealed chain -> sequential driver vs parallel driver -> identical
  built_counts, shortfalls, identity-map key set (multi-book world with links,
  clusters, contracts).
- Chaos: injected per-level unit failure (impossible policy / poisoned payload per
  kind) -> full reverse teardown, zero leaked frames/conduits, cause chained, report
  failed at the right level.
- Cohort: parallel load with a foreign thread probing root transactions mid-replay ->
  foreign parks; workers pass; post-release single-thread law restored.
- Density >= 20 tests/100 LOC on engine deltas. Owner-run 3.14t; agent reports
  "Not run." throughout.
