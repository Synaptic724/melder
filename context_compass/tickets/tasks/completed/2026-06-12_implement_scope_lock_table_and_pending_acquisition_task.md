Completed: 2026-06-12T22:21:06Z
Summary: Landed the scope-acquisition control plane (moded lock table,
acquisition-only admission with holder evidence, scope-local pending,
strategy commit deltas, registry fact baselines). Validation green: unit
536/536, component 88/88. Two real defects found and fixed during
validation (condition/lock binding; begin_frame session aliasing guard).

# Task: Implement Scope Lock Table And Pending Acquisition

## Metadata
- Task ID: TASK-2026-06-12-implement-scope-lock-table-and-pending-acquisition
- Story: STORY-2026-06-12-implement-scope-acquisition-control-plane
- Epic: EPIC-2026-05-30-simplify-mediator-root-policy-and-lazy-devops-reporting
- Status: done
- Owner: cowork
- Agent Name: reviewer_0
- Priority: p1
- Created: 2026-06-12T21:42:50Z
- Updated: 2026-06-12T22:21:06Z

## State Transition Event (Closure)
- from_state: in_progress
- to_state: done
- transition_reason: user confirmed acceptance and closure after round-3
  green validation (unit 536/536, component 88/88).
- Timestamp correction note: the three MEASURE notes below were originally
  stamped 22:10/23:05/23:30 against an unchecked clock; actual wall-clock
  rounds ran between ~21:50 and 22:21 UTC. Stamps corrected once; content
  unchanged.

## Objective
Implement slices 1-3 of the scope-acquisition design plus the strategy
commit-delta seam and registry fact baselines, per the patch lane
`devops_scope_acquisition_2026_06_12`.

## Ticket Contract
- ENTRY_GATE: patch artifacts exist and were consumed in required order;
  consumption mapping recorded in `## Notes` before code edits.
- EXECUTION_BOUNDARY: as declared in the parent story (embargo manager,
  orchestrator, mediator, transaction manager/request, strategies, registry,
  dev_ops unit tests, boards, this lane).
- DEPENDENCIES:
  - patch lane docs (architecture/component/code-description)
  - `artifacts/2026-06-05_devops_transaction_control_plane_philosophy.md`
- EXIT_GATE: code landed within boundary; new unit ring written; validation
  status reported truthfully; canonical-doc merge deferred to patch closure.
- FAILURE_ESCALATION: `BLOCKER` on deadlock/lost-wakeup evidence;
  `DECISION_REQUEST` on any boundary expansion.

## Scope Boundaries
- In scope: moded lock table, acquisition admission, scope-local pending,
  request claim modes, strategy claims + commit deltas, fact records, tests.
- Out of scope: config field removal, Nexus policy embargoes, info-strategy
  catalog, audit sampling, canonical doc merge (closure step).

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: user instructed implementation after design approval.

## Steps / Checklist
- [x] Record patch-consumption mapping note.
- [x] Embargo manager: ClaimMode + matrix + try_acquire/acquire-wait/release.
- [x] Orchestrator: admission via acquisition; conflict scan retired.
- [x] Mediator: wait-retry admission loop; coarse FIFO removed.
- [x] Request/manager: scope_claims payload support.
- [x] Strategies: apply_commit_delta seam (base default fact stamping; family
      mode refinement deferred, see notes).
- [x] Registry: fact records + report/get surface.
- [x] Unit ring for matrix/parallel/wait/timeout/deltas/facts.
- [x] Microcycle notes per meaningful finding.

## Deliverables
- Working acquisition control plane within boundary + new unit tests.

## Validation
- Not run. (Agent environment cannot execute the repo's Python 3.14t ring.)
- Recommended commands:
  - `pytest tests/unit/melder/aether/dev_ops -q`
  - `pytest tests/unit/melder/aether/dev_ops/change_control_manager -q`

## Risks / Rollback Notes
- Rollback per patch doc: revert this patch id's commits; orchestrator revert
  alone restores the conflict-scan path.

## Applicable Anti-Patterns
- [ ] No implementation from UNKNOWN/HYPOTHESIS.
- [ ] No silent boundary expansion.
- [ ] No validation claims without execution.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - `system_docs/patches/active/devops_scope_acquisition_2026_06_12/architecture_patch.md`
  - `system_docs/patches/active/devops_scope_acquisition_2026_06_12/component_patch_dev_ops_transactions.md`
  - `system_docs/patches/active/devops_scope_acquisition_2026_06_12/code_description_patch_dev_ops_transactions.md`
- DISPOSITION: promote_to_documentation
- CLEANUP_TRIGGER: patch closure gates

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
- CONTEXT_TOPICS:
  - scope acquisition implementation
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, single-step continuation.
- Append-only; evidence ranges required; UNKNOWN-first discipline.

## Notes
- DATETIME: 2026-06-12T21:42:50Z
  TYPE: PLAN
  CLAIM: Patch-consumption mapping (required before code edits).
    architecture_patch "Migration and Rollout Order" steps 1-7 map to the
    checklist items in this task one-to-one; component_patch "Dependency and
    Ordering Constraints" fixes the landing order (lock table -> orchestrator
    -> mediator -> claims/deltas -> facts -> tests); code_description_patch
    fixes the matrix truth table, the acquisition loop shape, the
    release/notify contract, commit-delta ordering (after session pipeline,
    before orchestrator commit), and the non-goals (no per-scope conditions,
    no FIFO fairness, no async pending). Validation maps to component_patch
    "Validation Expectations" items 1-7.
  EVIDENCE:
  - system_docs/patches/active/devops_scope_acquisition_2026_06_12/architecture_patch.md:60-72
  - system_docs/patches/active/devops_scope_acquisition_2026_06_12/component_patch_dev_ops_transactions.md:55-75
  - system_docs/patches/active/devops_scope_acquisition_2026_06_12/code_description_patch_dev_ops_transactions.md:20-60
  IMPACT: Entry gate satisfied; implementation may begin.
  NEXT: implement the embargo-manager lock table.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-06-12T22:10:00Z
  TYPE: FACT
  CLAIM: Implementation landed within boundary. The embargo manager is now a
    moded lock table (ClaimMode X/S/IX, static matrix, atomic all-or-nothing
    try_acquire with holder evidence, wait_for_release condition,
    release_owner wake-on-release, cleanup notifies waiters). Orchestrator
    admission is one acquisition under its lock; the conflict scan is retired
    (conflict_manager retained for signature compatibility). The mediator
    replaced the coarse root FIFO with _admit_with_scope_wait (build once,
    admit, wait scope-locally on blocking-scope evidence, retry, bounded by
    max_transaction_wait_time_in_seconds; timeout names blocking scopes and
    holders). Requests carry scope_claims (validated via ClaimMode in
    build_request). TransactionStrategy gained a concrete apply_commit_delta
    default that stamps registry fact records while scopes are held,
    dispatched from _finalize_root_session between the session commit
    pipeline and orchestrator commit. DevopsInformationRegistry gained
    DevopsFactRecord storage with report_fact/get_fact_record/
    list_fact_records and per-key generation increments.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/embargo_manager/embargo_manager.py:19-96
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/embargo_manager/embargo_manager.py:215-345
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/orchestrator/orchestrator.py:378-425
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py:440-484
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py:887-955
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/transaction_strategy.py:117-186
  - src/melder/aether/aetheric_frame/dev_ops/devops_information_registry.py:44-70
  - tests/unit/melder/aether/dev_ops/change_control_manager/test_scope_acquisition.py:1-120
  IMPACT: Epic milestones 1 and 3 are implemented for the basic family set;
    admission is O(requested scopes) and parallel-by-default.
  NEXT: user runs the dev_ops unit ring; reconcile legacy mediator/
    orchestrator/embargo tests that assert the retired FIFO/conflict-scan
    internals.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-06-12T22:10:00Z
  TYPE: UNKNOWN
  CLAIM: Three follow-ups intentionally out of this slice. (1) Family claim
    refinement: strategies emit no scope_claims yet (everything defaults
    EXCLUSIVE) because flipping bind to S-on-spellbook requires verifying
    spellbook-side concurrent-bind safety (outside boundary). (2) Relational
    commit deltas: link/cluster plans carry no edge direction or
    share/unshare intent, so deltas stamp facts only; runtime callers must
    enrich metadata before write-through of provider/borrower/cluster edges.
    (3) Legacy tests asserting FIFO/conflict-scan internals
    (test_transaction_mediator*.py, test_orchestrator.py,
    test_embargo_manager.py, test_conflict_manager.py) will need
    reconciliation against the new admission contract once the suite runs.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/link_transaction_strategy.py:115-139
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/cluster_link_transaction_strategy.py:121-145
  IMPACT: None block the landed slice; each is a bounded follow-up task.
  NEXT: run validation, then open the family-refinement follow-up task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-06-12T21:55:00Z
  TYPE: MEASURE
  CLAIM: Validation round 1 (user-run, Python 3.14t venv): new ring 27/27
    passed in 0.57s. Full dev_ops ring 529 passed / 7 failed in 1.18s. Six
    failures were the predicted legacy-contract assertions (reason strings,
    FIFO queue semantics, `_pending_root_starts` poke) and are now reconciled
    to the acquisition contract. One failure was a REAL DEFECT caught by
    `test_embargo_manager_cleanup_rechecks_cleaned_inside_lock`: the manager
    `Condition` binds its lock at construction, so notify/wait under a
    rebound `_lock` raised "cannot notify on un-acquired lock". Fixed by
    waiting/notifying under the condition's own context in cleanup,
    release_owner, and wait_for_release. Also hardened the mediator scope
    wait with bounded 1s slices so a notification landing between an
    admission attempt and the wait self-heals within one second instead of
    the full deadline.
  EVIDENCE:
  - user-run pytest output (2026-06-12, 7 failed / 529 passed)
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/embargo_manager/embargo_manager.py:160-180
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py:949-955
  - tests/unit/melder/aether/dev_ops/change_control_manager/test_transaction_mediator.py:132-310
  - tests/unit/melder/aether/dev_ops/change_control_manager/test_change_control_manager.py:635-664
  - tests/unit/melder/aether/dev_ops/change_control_manager/test_change_control_transactions.py:703-710
  IMPACT: The acquisition slice is validated except for the re-run; legacy
    unit assertions now encode the new admission contract.
  NEXT: user re-runs the dev_ops unit ring, then the component and
    integration change-control suites (they reference the deprecated queue
    flag and may assert blocking behavior).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-06-12T22:05:00Z
  TYPE: MEASURE
  CLAIM: Validation round 2 (user-run): dev_ops unit ring fully green
    (536/536). Component suite 81/88 with 7 failures, triaged: (a) two were
    this lane's contract assertions, reconciled (hash-only requests admit -
    keys are the admission vocabulary; embargo rejections now name the
    holder); (b) three were PRE-EXISTING stale tests from the May-30 policy
    removal - `change_control_mode` no longer exists on
    `AethericFrameConfiguration` and `configure(...)` takes two kwargs, so
    the queue-turn-taking test has been red since that removal; rewritten as
    scope-driven turn-taking on the frame-owned mediator; (c) the two
    cross-thread same-root begin_frame tests exposed a PRE-EXISTING session
    aliasing hazard (begin_frame silently overwrote the hosted session for an
    already-hosted request id) - fixed in the mediator with a fail-fast guard
    naming the owning thread, which also restores those tests as written;
    (d) two transaction-surface tests were PRE-EXISTING casualties of the
    eager metadata-derived ownership rebuild removal - the registry
    explicitly does not derive spellbook<->conduit edges from identity
    metadata, so the test helper now registers ownership explicitly, matching
    the explicit-topology philosophy. Integration suite has a PRE-EXISTING
    collection error (`ModuleNotFoundError: tests.mocks`) unrelated to this
    lane.
  EVIDENCE:
  - user-run pytest output (2026-06-12, component 7 failed / 81 passed)
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py:314-336
  - src/melder/aether/aetheric_frame/dev_ops/devops_information_registry.py:600-604
  - tests/component/melder/aether/dev_ops/change_control_manager/test_change_control_manager_component.py:515-620
  - tests/component/melder/aether/dev_ops/change_control_manager/test_transaction_surface_component.py:56-70
  IMPACT: Two real defects found and fixed by validation (condition/lock
    binding, session aliasing); the remaining failures were inherited debt
    now reconciled.
  NEXT: user re-runs unit + component dev_ops suites; integration
    `tests.mocks` import error stays flagged for its owning lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-06-12T22:18:00Z
  TYPE: MEASURE
  CLAIM: Validation round 3 (user-run): dev_ops unit ring 536/536 and
    component ring 88/88, both fully green. The integration collection error
    is root-caused as pre-existing infrastructure: `tests/conftest.py` adds
    `src/` to `sys.path` but not the project root, so `from tests.mocks...`
    resolves only under `python -m pytest` (CWD on path); bare `pytest`
    cannot import it. One-line conftest fix flagged for its owning lane.
  EVIDENCE:
  - user-run pytest output (2026-06-12, 536 passed; 88 passed)
  - tests/conftest.py:7-13
  IMPACT: Exit-gate validation items are satisfied for this task; remaining
    integration-run confirmation depends on the conftest path fix.
  NEXT: user decision on task closure (closure sync + patch-doc merge into
    canonical system_docs) versus keeping the lane open for follow-ups.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
First implementation task of the scope-acquisition story. Code, unit ring,
two real defect fixes (condition/lock binding; begin_frame session aliasing
guard), and legacy/component test reconciliation are landed within boundary.
Round 3: unit 536/536 and component 88/88 fully green. Integration
collection error is pre-existing conftest path infrastructure, flagged.
Awaiting user closure decision; closure runs board sync plus patch-doc merge
into canonical docs per the patch gating contract.
