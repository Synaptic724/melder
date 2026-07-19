# Component Patch: RestorePlanGraph compiler + parallel RestoreEngine (S4)

AMENDED 2026-07-18 (owner refinement, second ruling): the planner is GRAPH-DERIVED, not
static kind-stages. Fold -> build a dependency graph of the recorded world -> flatten to
topological LEVELS -> register levels as scheduler phases ("load a flat version of that map
into the phase scheduler"). The canon stage order is no longer the execution plan; it is the
parity baseline the graph must reproduce on today's record shapes.

Lane: parallel_restore_ulid_identity_2026_07_18. Ticket: STORY-2026-07-18-loadplan-phase-compiler.
GATE NOTE: implementation additionally requires
code_description_patch_restore_engine_parallel.md authored at story start -
concurrency-sensitive trigger per patch_framework_gating.md.

## Before
- RestoreEngine drives all nine stages sequentially on one thread with per-entity loops
  inside each stage (restore_engine.py:549-569); RestoreReport is single-writer "no lock by
  contract" (restore_engine.py:36-38); teardown walks an ordered _built_stack in reverse.

## After
- CrystalLoaderSystem owns one persistent PhaseScheduler (S2 seam; crystallizer config
  keys) and enrolls its pool threads into the load-authority cohort (S3) for each span.
- RestorePlanGraph (new, loader-local): after fold, build a DirectedAcyclicWorkGraph over
  per-entity nodes - config roots (aether/crystallizer/MR), nexus root, frames, book
  chains, link rows (S1), clusters, contracts - with edges from RECORDED dependencies:
  book -> its frame; link -> initiator book-chain + target book-chain; cluster -> member
  book-chains; contract -> its conduit's book-chain + frame; nexus -> edges only when the
  record carries nexus-native constructs (today it is a leaf: _replay_nexus rebuilds the
  root alone, restore_engine.py:1035-1094, so placement is graph-derived, not hardcoded).
- Flatten: additive DirectedAcyclicWorkGraph.topological_levels() (Kahn by layers; sort()
  untouched for compiler suites) yields level lists; execute_plan registers ONE scheduler
  phase per level. Barriers = level boundaries; the recorded partial order is preserved by
  construction, and a cycle in recorded edges is an admission BLOCKER (fail before build).
- Unit factories: one unit per node. A BOOK node executes today's interior chain unchanged
  (config freeze -> active binds in bind_order -> conjure -> staged -> notch,
  restore_engine.py:1231-1313). Units read the identity map only for nodes in
  already-passed levels (guaranteed by level edges).
- Concurrency-safe engine state: RestoreReport gains one internal lock (describe() shape
  unchanged); _built_stack becomes lock-appended so global reverse teardown stays
  deterministic; identity map writes go through the report lock.
- Failure law identical: any unit failure -> scheduler fail-fast cancels the run ->
  mark_failed(stage) -> _teardown_built() reverse walk -> RuntimeError chaining the cause.
  The sequential driver remains as a config-selectable fallback lane until owner retirement.

## Interface Deltas
- Public loader verbs unchanged. LoadAdmission.execute_plan gains the graph-compilation
  path (internal). DirectedAcyclicWorkGraph gains additive topological_levels().
  RestoreReport/report kinds unchanged; the report additionally records the level plan
  summary (level count, nodes per level) for diagnostics.

## State / Failure Deltas
- Emit during parallel build serializes on the PersistenceSystem instance RLock
  (persistence_system.py:44-46, 87) - correct by existing contract; accepted contention.
- New failure surface: PhaseTimeoutError on a stalled stage -> same all-or-nothing path.

## Dependency / Ordering
- Depends on S1 (link units), S2 (scheduler), S3 (cohort gate). Lands last behind parity.

## Validation Expectations
- Parity suite: same chain restored sequential vs parallel -> identical built counts,
  shortfalls, identity coverage. Chaos: kill one unit per phase -> full teardown, zero
  leaked units. Contention: multi-book world on 1 vs N workers -> identical outcomes.
  Density >= 20 tests/100 LOC on engine deltas. Owner-run 3.14t with timing comparison.
