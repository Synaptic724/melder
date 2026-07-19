# Task: Strategy - ULID-ordered checkpoint/restore + phase-scheduler-driven parallel restoration

- Completed: 2026-07-18T22:30:00Z
- Summary: Owner accepted Option A ("go ahead and do all this... send it"): ULID = identity
  everywhere (add first-class link identity), order-of-operations = journal sequence, parallel
  replay inside canon stages via reused PhaseScheduler behind a cohort-aware LoadGate. Spawned
  EPIC-2026-07-18-parallel-restore-ulid-identity with stories S1-S4 + active patch lane.

## Metadata
- Task ID: TASK-2026-07-18-checkpoint-restore-ulid-ordering-strategy
- Story: none (owner-initiated design discussion; spawned the parallel-restore epic)
- Status: done
- Owner: cowork
- Agent Name: helper_f
- Priority: p1
- Created: 2026-07-18T22:02:29Z
- Updated: 2026-07-18T22:02:29Z

## Objective
Produce an evidence-backed STRATEGY_DISCUSSION with the owner on: (1) ULID identity coverage for
spellbook / root conduits / linking contracts to establish a global order of operations; (2)
replacing the sequential checkpoint-restore flow with a parallel plan executed by the conjure
phase scheduler; (3) whether the mediator/transaction system can admit multi-threaded restore.

## Ticket Contract
- ENTRY_GATE: owner directive 2026-07-18 ("checkpoints and restores, and ULIDs ... reuse the
  conjure phase scheduler for restoration ... lets talk about this"); helper_f certified.
- EXECUTION_BOUNDARY: read-only investigation of `src/melder/utilities/synchronization/`,
  `src/melder/crystallizer/crystal_loader_system/`, dev_ops transaction manager, ULID sites in
  spellbook/conduit, and relevant `system_docs/` sections. NO code edits in this lane.
- DEPENDENCIES: system_docs/src_architecture.md, system_docs/src_components.md (on-demand
  trigger met: architecture claims required).
- EXIT_GATE: strategy discussion delivered with options + tradeoffs + recommendation; owner
  picks a direction (or parks the lane).
- FAILURE_ESCALATION: DECISION_REQUEST for design forks; CONFLICT if evidence contradicts the
  owner's premise; BLOCKER on unreadable sources.

## Scope Boundaries
- In scope: current restore order-of-operations, ULID coverage today, phase scheduler
  capabilities, mediator threading contract, gap analysis, design options.
- Out of scope: implementation, test authoring, doc patches (follow-up tickets).

## State Transition Event
- from_state: ready
- to_state: in_progress
- transition_reason: owner explicitly opened the discussion; investigation reads are the work.

## Steps / Checklist
- [ ] Read phase_scheduler.py + unit_of_work.py + phase_latch.py (conjure scheduler contract).
- [ ] Read restore_engine.py + load_plan.py + load_admission.py + crystal_loader_system.py.
- [ ] Read transaction_mediator.py + dev_ops_manager.py (mediator threading contract).
- [ ] Trace ULID coverage: ulid_factory/id_builder + spellbook/conduit/spell_index/crystals.
- [ ] Read relevant src_architecture.md / src_components.md sections.
- [ ] Document findings in Notes; deliver STRATEGY_DISCUSSION to owner.

## Deliverables
- STRATEGY_DISCUSSION (objective/constraints/facts/unknowns/options/tradeoffs/recommendation).

## Files / Paths Impacted
- None (read-only lane); this ticket + attention_board row only.

## Validation
- Not run. (Discussion lane; no code changes.)

## Risks / Rollback Notes
- Risk: readable_src_graph.json not read (owner-waived at onboarding; RAISED again in this
  lane for wiring-level claims). Mitigation: claims held to file+symbol evidence or UNKNOWN.

## Applicable Anti-Patterns
- [ ] No implementation from UNKNOWN/HYPOTHESIS (this lane is read-only).
- [ ] No graph-free wiring claims promoted to FACT without source evidence.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] STRATEGY_DISCUSSION delivered
- [ ] Owner direction recorded (DECISION or parked)
- [ ] Board sync on closure

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS: none
- DISPOSITION: n/a
- CLEANUP_TRIGGER: n/a

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- CONTEXT_TOPICS: none
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Append-only; evidence ranges required.

## Notes
- DATETIME: 2026-07-18T22:02:29Z
  TYPE: FACT
  CLAIM: Investigation targets located. Conjure phase scheduler lives in
    utilities/synchronization (phase_scheduler.py 732 LOC, unit_of_work.py 396, phase_latch.py
    125) and is consumed by spellbook_creation_system.py. Restore lane: restore_engine.py
    2003 LOC, load_plan.py 285, load_admission.py 574, crystal_loader_system.py 272. Mediator:
    dev_ops change_control_manager transaction_manager (transaction_mediator.py 1249) with
    per-verb strategies (bind/link/cluster_link/conjure/notch/transfer/unlink/unelect).
    ULIDs are minted by utilities/helpers/ulid_factory.new_ulid() via id_builder.
  EVIDENCE:
  - src/melder/utilities/synchronization/phase_scheduler.py:1-1
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:1-1
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py:1-1
  - src/melder/utilities/helpers/ulid_factory.py:30-30
  IMPACT: Discussion can be grounded in the real scheduler/restore/mediator contracts.
  NEXT: Chunked reads of the scheduler + restore + mediator files.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-07-18T22:20:00Z
  TYPE: FACT
  CLAIM: ULIDs are identity, not order, by explicit contract: new_ulid() is 48-bit ms
    timestamp + 80 random bits, "Monotonicity within a single millisecond is NOT guaranteed
    ... Melder only uses these as opaque unique lineage segments." A same-ms ULID inversion
    already caused the retention-eviction bug (fixed by ordering on checkpoint_number).
    Meanwhile the persistence journal ALREADY carries a total order: entries are
    (sequence, kind, key) with strictly-increasing unique sequences per window.
  EVIDENCE:
  - src/melder/utilities/helpers/ulid_factory.py:18-20
  - src/melder/crystallizer/persistence/persistence_crystal.py:59-59
  - src/melder/crystallizer/persistence/persistence_crystal.py:133-155
  IMPACT: "ULID = order of operations" is unsafe as-is; order exists and lives in the journal.
  NEXT: Frame identity-vs-order split in the strategy discussion.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-07-18T22:20:00Z
  TYPE: FACT
  CLAIM: ULID coverage today: Spellbook mints its own ULID (spellbook.py:203), Conduit mints
    per-conjure ULIDs (conduit.py:228), ward reuses its conduit's id (conduit_ward.py:174).
    LINKS have NO identity of their own - recorded only as link_targets edge lists inside
    conduit payloads and replayed by scanning initiators (restore_engine._replay_links).
    Contract/cluster/index ULIDs exist and are translated by the identity map.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:203-203
  - src/melder/aether/conduit/conduit.py:228-228
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:1590-1612
  IMPACT: The genuinely missing piece of the owner's premise is first-class link identity
    (+ link/unlink journal rows), not spellbook/conduit ULIDs - those already exist.
  NEXT: Include link-identity gap in options.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-07-18T22:20:00Z
  TYPE: FACT
  CLAIM: Restore is sequential by design today: single-use RestoreEngine, one thread, canon
    stage order (aether_config -> crystallizer_policy -> MR -> nexus -> frames ->
    books_and_binds -> links -> clusters -> contracts LAST), all-or-nothing reverse-order
    teardown via an ordered _built_stack, fresh identities minted (never-rehydrate-ULIDs),
    re-emission into the active profile during replay. Per book the chain is strictly
    sequential (config freeze -> active binds in bind_order -> conjure -> staged binds ->
    notch selections), but BOOKS are independent of each other, as are links per initiator,
    clusters, and contracts within their stages.
  EVIDENCE:
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:549-569
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:1231-1313
  - src/melder/crystallizer/crystal_loader_system/restore_engine.py:290-321
  IMPACT: The parallelism is per-entity within stages; the stage order itself is the DAG.
  NEXT: Map stages onto PhaseScheduler phases.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-07-18T22:20:00Z
  TYPE: FACT
  CLAIM: PhaseScheduler is a near-perfect shape match: persistent worker pool, phases run in
    registration order with one PhaseLatch barrier per phase, units within a phase run in
    parallel, fail-fast + timeout + per-run cancellation scope, and it is deliberately
    generic ("does not know Spell or DAG internals. It only coordinates UnitOfWork
    instances"). Two couplings block direct reuse: worker/timeout config is read from
    SpellbookConfiguration keys, and instances are spellbook-owned while restore is
    world-scope. The harder blocker is the LoadGate: load authority is
    single-THREAD-keyed ("the loading thread passes free and all other threads park"),
    so scheduler workers would park at the gate their own restore claimed. The mediator
    itself is already multi-thread-native: "Cross-thread root starts are always allowed;
    overlap is decided by scope-claim acquisition at admission".
  EVIDENCE:
  - src/melder/utilities/synchronization/phase_scheduler.py:99-107
  - src/melder/utilities/synchronization/phase_scheduler.py:170-217
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py:71-79
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py:136-144
  IMPACT: Reuse is viable; the enabling work is a cohort-aware LoadGate + a config seam,
    not a new scheduler. RestoreReport/_built_stack also need thread-safe recording
    (report is "no lock by contract" today).
  NEXT: Deliver STRATEGY_DISCUSSION with options A/B/C.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-07-18T22:30:00Z
  TYPE: DECISION
  CLAIM: Owner accepted Option A verbatim ("yeah go ahead and do all this please it makes
    sense because right now checkpoints and restores are mad slow and sequential send it").
    Both design unknowns resolved before spawn: (1) emit path is serialized by the one
    PersistenceSystem instance RLock - every record/remove verb locks, so journal sequence
    allocation stays atomic under parallel builders; (2) the conjure configuration-discipline
    guard reads per-book _configuration._frozen only - no cross-book shared state, so books
    parallelize.
  EVIDENCE:
  - src/melder/crystallizer/persistence/persistence_system.py:44-46
  - src/melder/crystallizer/persistence/persistence_system.py:87-87
  - src/melder/aether/spellbook/spellbook.py:4519-4519
  - src/melder/aether/spellbook/spellbook.py:5798-5803
  IMPACT: Entry conditions for the epic are evidence-backed; no implementation from UNKNOWN.
  NEXT: Epic + S1-S4 stories + patch lane; S1 (link identity) implements first.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Closed owner-accepted. Decision: Option A. Successor lane:
tickets/epics/2026-07-18_parallel_restore_ulid_identity_epic.md (S1 link identity, S2
scheduler config seam, S3 cohort LoadGate, S4 plan compiler + concurrent-safe engine).
Patch lane: system_docs/patches/active/parallel_restore_ulid_identity_2026_07_18/.
