# Epic: Parallel checkpoint restore on ULID identity + journal order

## Metadata
- Epic ID: EPIC-2026-07-18-parallel-restore-ulid-identity
- Status: in_progress
- Owner: cowork
- Agent Name: UNASSIGNED (helper_f departed 2026-08-02, owner-directed; lane left ACTIVE)
- Priority: p0
- Created: 2026-07-18T22:30:00Z
- Updated: 2026-07-18T22:30:00Z
- Stories:
  - STORY-2026-07-18-link-identity-journal-rows (S1)
  - STORY-2026-07-18-phase-scheduler-config-seam (S2)
  - STORY-2026-07-18-cohort-aware-load-gate (S3)
  - STORY-2026-07-18-loadplan-phase-compiler (S4)

## Problem / Opportunity
Checkpoint restore is single-threaded by design: one RestoreEngine, one thread, strictly
sequential canon stages, per-entity loops inside each stage
(restore_engine.py:290-321, 549-569). On large worlds this is the dominant load cost. The
owner directive (2026-07-18): restores are "mad slow and sequential" - parallelize them.
Separately, links carry no identity of their own (edge lists inside conduit payloads,
restore_engine.py:1590-1612), which blocks per-link journal rows, precise unlink tombstones,
and independent replay units.

## Context
- ULIDs are identity, not order: new_ulid() is non-monotonic within one ms by documented
  contract (ulid_factory.py:18-20); a same-ms inversion already caused the retention bug.
- Order of operations already exists: journal entries are (sequence, kind, key) with
  strictly increasing unique sequences (persistence_crystal.py:59, 133-155).
- PhaseScheduler (utilities/synchronization/phase_scheduler.py) is a generic persistent-pool
  phase runner: barriers between phases, parallel units within a phase, fail-fast, timeout,
  per-run cancellation. It matches restore's stage DAG exactly.
- The mediator admits cross-thread roots and arbitrates by scope claims
  (transaction_mediator.py:71-79); the LoadGate is the single-thread bottleneck: load
  authority is thread-keyed (transaction_mediator.py:140-143).
- Emit path is safe under parallel builders: one PersistenceSystem RLock serializes every
  record/remove verb (persistence_system.py:44-46, 87).

## MRP Alignment
The core being built: identity everywhere (links gain ULIDs), one order-of-operations truth
(the journal sequence), and a restore that executes the canon partial order with per-entity
parallelism inside stages - preserving the all-or-nothing law, never-rehydrate-ULIDs, and
honest shortfall reporting. No throwaway scaffolding: the scheduler seam and cohort gate are
durable runtime capabilities, not restore-only hacks.

## Ticket Contract
- ENTRY_GATE: owner DECISION 2026-07-18 (Option A accepted); strategy task completed with
  unknowns resolved; patch lane exists and is linked below.
- EXECUTION_BOUNDARY: crystallizer persistence + crystal_loader_system, conduit link verbs +
  conduit crystal, utilities/synchronization (PhaseScheduler, LoadGate), aether load
  authority surface, tests. No public API shape changes without explicit owner sign-off.
- DEPENDENCIES: patch docs under
  system_docs/patches/active/parallel_restore_ulid_identity_2026_07_18/ (entry gate per
  patch_framework_gating.md); S3/S4 additionally require code_description patches BEFORE
  their implementation starts (concurrency-sensitive trigger).
- EXIT_GATE: all four stories landed with regression suites; owner-run 3.14t suite green;
  canonical docs + graph promoted from the patch lane; boards synced.
- FAILURE_ESCALATION: DECISION_REQUEST on any public-API or record-format fork; CONFLICT if
  measured parallel restore is not faster; BLOCKER on gate/emit contention deadlocks.

## Goals
- Links (and linking contracts) become first-class identities with journal rows.
- Restore executes stages as scheduler phases; independent entities rebuild in parallel.
- LoadGate admits a restore cohort instead of exactly one thread.
- All-or-nothing, never-rehydrate-ULIDs, and shortfall honesty preserved unchanged.

## Non-Goals
- No ULID semantic change (no monotonic variant; Option B rejected).
- No record-format migration for old checkpoints beyond additive link rows.
- No parallelism in single-root head stages (aether/crystallizer/MR/nexus).

## Scope Boundaries
- In scope: files listed per story; patch lane docs; tests (unit + component + integration).
- Out of scope: mutation_research lanes, rift/nexus ACL surfaces, spell compiler internals.

## Requirements
- Functional: parity of restore outcomes with the sequential engine on identical chains
  (same built counts, shortfalls, identity-map coverage); link identity round-trips
  checkpoint -> restore -> re-emission.
- Non-functional: 3.14t thread-safety at every touched surface; restore wall-clock improves
  on multi-book worlds (owner-measured); no new module-level state; cleanup discipline per
  synaptic overlay (del posture, logger last).

## Acceptance Criteria
- [ ] S1: link/unlink mint ULIDs, journal rows + tombstones fold correctly, restore
      replays links through the identity map with per-link built/shortfall reporting.
- [ ] S2: PhaseScheduler constructible with explicit worker/timeout values (config path
      unchanged for spellbooks); crystallizer owns a restore scheduler instance.
- [ ] S3: LoadGate cohort authority - restore workers pass, foreign threads park; span
      release restores single-thread law; regression proves no foreign leak-through.
- [ ] S4: LoadPlan compiles to phases (frames -> books -> links -> clusters -> contracts);
      per-entity units run parallel; all-or-nothing teardown remains reverse-deterministic;
      RestoreReport is concurrency-safe; parity suite green.
- [ ] Owner runs full 3.14t suite; docs/graph promotion completed.

## Risks / Mitigations
- LoadGate cohort bug leaks foreign transactions into a half-built world -> S3 gets its own
  code_description patch + adversarial regression suite BEFORE implementation.
- Parallel emit contention serializes gains -> acceptable (correctness first); measure, then
  consider batched emission only with owner sign-off.
- Teardown order under parallel build -> single lock-appended built stack preserves global
  reverse order; units record build events atomically.
- Old checkpoints without link rows -> fold falls back to legacy link_targets lists
  (additive compatibility, no migration).

## Validation Plan
- Per story: pytest unit + component suites (density >= 10/100 LOC; >= 20 for gate/engine).
- Integration: multi-book world checkpoint -> parallel restore -> parity assertions vs
  sequential baseline; chaos test: failing unit mid-phase must tear down everything.
- Not run by agent; owner runs on 3.14t. Reports say "Not run." until then.

## Decision Log
- 2026-07-18 Owner: Option A accepted (identity=ULID, order=journal, scheduler reuse).
- 2026-07-18 Owner: rejected ULID-as-order (Option B) per agent recommendation.
- 2026-07-18 Owner (second ruling): total order demoted to "just an idea" - the execution
  plan is a synchronized dependency GRAPH of the recorded world, flattened to levels and
  loaded into the scheduler. S4 amended: RestorePlanGraph on DirectedAcyclicWorkGraph
  (+ additive topological_levels()); entity placement graph-derived. Nexus evidence: its
  replay is currently a dependency leaf (root-only rebuild, restore_engine.py:1035-1094);
  when nexus-native constructs land in the record, the graph reorders it automatically -
  no slot-coding either way.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: owner directive "go ahead and do all this ... send it"; entry gates met.

## Milestones
- [ ] S1 link identity landed with regressions.
- [ ] S2 scheduler seam landed (spellbook lane untouched, proven by existing suites).
- [ ] S3 cohort gate landed behind its code_description patch.
- [ ] S4 compiler + parallel engine landed; parity + chaos suites green.
- [ ] Owner 3.14t run green; patch lane promoted to canonical docs + graph.

## Applicable Anti-Patterns
- [ ] No implementation before the story's required patch artifacts exist and are linked.
- [ ] No defensive locks on hot paths without contract evidence.
- [ ] No silent record-format breaks; additive only.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/parallel_restore_ulid_identity_2026_07_18/architecture_patch.md
  - system_docs/patches/active/parallel_restore_ulid_identity_2026_07_18/component_patch_link_identity_persistence.md
  - system_docs/patches/active/parallel_restore_ulid_identity_2026_07_18/component_patch_phase_scheduler_seam.md
  - system_docs/patches/active/parallel_restore_ulid_identity_2026_07_18/component_patch_load_gate_cohort.md
  - system_docs/patches/active/parallel_restore_ulid_identity_2026_07_18/component_patch_restore_engine_parallel.md
- DISPOSITION: promote_to_documentation
- CLEANUP_TRIGGER: epic closure (merge durable deltas into canonical C-docs + graph)

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false

## Noting Behavior
- Epic notes: program direction, cross-story tradeoffs, tranche order.

## Notes
- DATETIME: 2026-07-18T22:30:00Z
  TYPE: PLAN
  CLAIM: Tranche order S1 -> S2 -> S3 -> S4. S1 is self-contained record-shape work and
    de-risks fold/replay early; S2 is mechanical; S3 is the concurrency-risk core and gets
    its code_description patch + adversarial tests first; S4 assembles. Parity harness
    (sequential vs parallel outcome equivalence) is built in S4 but specified in the
    architecture patch now.
  EVIDENCE:
  - system_docs/patches/active/parallel_restore_ulid_identity_2026_07_18/architecture_patch.md:1-1
  IMPACT: Each story lands independently reviewable; core risk isolated in one lane.
  NEXT: Implement S1.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Owner-accepted program: identity=ULID everywhere (links gain identity), order=journal
sequence, restore parallelized per-entity inside canon stages via PhaseScheduler behind a
cohort-aware LoadGate. Patch lane active; S1 implements first.
