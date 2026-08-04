# Story: Implement Scope-Acquisition Control Plane

## Metadata
- Story ID: STORY-2026-06-12-implement-scope-acquisition-control-plane
- Epic: EPIC-2026-05-30-simplify-mediator-root-policy-and-lazy-devops-reporting
- Status: completed
- Owner: cowork
- Agent Name: reviewer_0
- Priority: p1
- Created: 2026-06-12T21:42:50Z
- Updated: 2026-06-14T16:40:19Z

## User Narrative
As the runtime architect, I want transaction admission to be one cheap
scope-acquisition gate with claim modes and scope-local pending, so that N
agents mutating one frame in parallel are vetted in O(scopes) and only true
overlap ever waits.

## Value / MRP Alignment
This story lands the design converged in the 2026-06-12 mediator discussion:
embargo table as the lock table, moded claims, blocking pending with
wake-on-release, strategy-owned commit deltas, and last-reported fact
baselines. It answers epic milestones 1 and 3 and the philosophy artifact's
admission questions with the smallest coherent system.

## Ticket Contract
- ENTRY_GATE: design approved by user in chat (2026-06-12); philosophy
  artifact and epic dependencies read; patch artifacts exist for
  `devops_scope_acquisition_2026_06_12`.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/embargo_manager/embargo_manager.py`
  - `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/orchestrator/orchestrator.py`
  - `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py`
  - `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_manager.py`
  - `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_request/transaction_request.py`
  - `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/*.py`
  - `src/melder/aether/aetheric_frame/dev_ops/devops_information_registry.py`
  - `tests/unit/melder/aether/dev_ops/change_control_manager/**`
  - this story, its tasks, the patch lane, and board surfaces
- DEPENDENCIES:
  - `artifacts/2026-06-05_devops_transaction_control_plane_philosophy.md`
  - `system_docs/patches/active/devops_scope_acquisition_2026_06_12/architecture_patch.md`
  - `system_docs/patches/active/devops_scope_acquisition_2026_06_12/component_patch_dev_ops_transactions.md`
  - `system_docs/patches/active/devops_scope_acquisition_2026_06_12/code_description_patch_dev_ops_transactions.md`
- EXIT_GATE: lock table with modes is the only admission gate; scope-local
  pending replaces the root FIFO; all four strategies apply commit deltas;
  fact records exist with a report path; new unit ring exists; user accepts.
- FAILURE_ESCALATION: raise `BLOCKER` on any deadlock/lost-wakeup found in
  testing; raise `DECISION_REQUEST` if claim-mode vocabulary needs to grow
  beyond X/S/IX.

## Scope Boundaries
- In scope: slices 1-3 of the agreed design plus commit deltas and fact
  baselines.
- Out of scope: frame-config field removal, policy-owned (Nexus) embargoes,
  information-strategy catalog, audit sampling, new transaction families.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: user instructed implementation of the agreed design
  ("go ahead and implement everything", 2026-06-12).

## Tasks (Implementation Checklist)
- [x] Task: `tickets/tasks/completed/2026-06-12_implement_scope_lock_table_and_pending_acquisition_task.md`
      (closed 2026-06-12T22:21:06Z; unit 536/536, component 88/88; canonical
      delta merged into src_components.md "Transaction Admission Plane";
      src_architecture.md A12 merge deferred - file currently trips binary
      detection, flagged for the doc-drift lane)
- [x] Task: `tickets/tasks/completed/2026-06-13_link_transaction_claim_modes_and_commit_deltas_task.md`
      (link lane: IX spellbooks / X conduits-wards; closed 2026-06-14, green in
      the 3.14t venv).
- [x] Task: `tickets/tasks/completed/2026-06-14_family_claim_modes_bind_cluster_and_unlink_transaction_task.md`
      (bind + cluster_link claim modes; the new unlink/sever transaction; and
      the family-wide decision that relational commit deltas are redundant
      because the link/cluster-membership mirrors are maintained eagerly).
- [x] Task: `tickets/tasks/completed/2026-06-12_remove_queue_flag_and_implement_info_strategy_catalog_task.md`
      (closed 2026-06-12T23:32:08Z; unit 561/561, component 88/88, config
      49/49, integration 65/65; covers BOTH the information-strategy
      catalog + registry audit AND the frame-config queueing-field removal;
      canonical merge done in src_components.md; admission-vocabulary
      clarification recorded: keys are claims, hashes are advisory;
      live-truth probes + audit sampling cadence remain future extensions;
      conftest project-root path fix still not approved/not included).

## Acceptance Criteria
- Admission cost is O(requested scopes) dict operations under one lock.
- Disjoint transactions admit in parallel; S/S-compatible claims admit in
  parallel on the same scope; X collisions wait and wake on release.
- Timeout surfaces blocking scope keys and holder request ids.
- Registry link/cluster/ownership truth is written by strategy commit deltas
  while scopes are held; fact records carry reporter + timestamp.
- Validation: new unit ring written; execution status reported truthfully.

## Risks / Mitigations
- Risk: lost wakeup under the single-condition design.
  Mitigation: full claim re-evaluation per wake; notify_all on every release
  and on cleanup; timeout bounds all waits.
- Risk: self-deadlock from same-thread parallel overlapping roots.
  Mitigation: documented timeout-with-evidence behavior; same-thread nesting
  should join (existing mediator contract).

## Applicable Anti-Patterns
- [ ] No implementation from UNKNOWN/HYPOTHESIS (design promoted via chat
      decisions + patch docs).
- [ ] No silent scope expansion beyond EXECUTION_BOUNDARY.
- [ ] No validation claims without execution.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - `system_docs/patches/active/devops_scope_acquisition_2026_06_12/architecture_patch.md`
  - `system_docs/patches/active/devops_scope_acquisition_2026_06_12/component_patch_dev_ops_transactions.md`
  - `system_docs/patches/active/devops_scope_acquisition_2026_06_12/code_description_patch_dev_ops_transactions.md`
- DISPOSITION: promote_to_documentation
- CLEANUP_TRIGGER: patch closure gates after user acceptance

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
- CONTEXT_TOPICS:
  - scope acquisition admission
  - claim modes and compatibility
  - strategy commit deltas and fact baselines
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-06-12T21:42:50Z
  TYPE: DECISION
  CLAIM: Design locked from the 2026-06-12 user discussion: one acquisition
    gate (embargo = lock table), X/S/IX modes with the classic MGL-style
    matrix, blocking scope-local pending bounded by the existing timeout,
    strategy-owned commit deltas applied while scopes are held, and
    last-reported fact records so routine freshness never runs a strategy.
  EVIDENCE:
  - artifacts/2026-06-05_devops_transaction_control_plane_philosophy.md:261-287
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/embargo_manager/embargo_manager.py:98-217
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/orchestrator/orchestrator.py:339-401
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py:887-939
  IMPACT: Epic milestones 1 and 3 become implementable in one bounded slice.
  NEXT: execute the lock-table task with patch-consumption mapping first.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-06-14T16:40:19Z
  TYPE: DECISION
  CLAIM: The family claim-mode follow-up is complete and the EXIT_GATE clause
    "all four strategies apply commit deltas" is intentionally revised to
    satisfied-by-redundancy: NO strategy needs a relational commit delta because
    the provider->borrower link mirror and the cluster-membership mirror are
    maintained EAGERLY at the mutation site, now race-safe under the
    transaction's held claims; base apply_commit_delta still stamps fact
    baselines. Claim modes shipped: link (IX spellbooks), bind (IX spellbook +
    clusters), cluster_link (IX member spellbooks); transfer was already
    EXCLUSIVE everywhere. A new unlink/sever transaction family was added by
    user direction (sever_link self-admits an `unlink` transaction;
    _remove_contract re-resolves the borrowing side's consumers) -- a deliberate
    expansion of the original "no new transaction families" boundary.
  EVIDENCE:
  - tickets/tasks/completed/2026-06-13_link_transaction_claim_modes_and_commit_deltas_task.md
  - tickets/tasks/completed/2026-06-14_family_claim_modes_bind_cluster_and_unlink_transaction_task.md
  IMPACT: Story checklist follow-up done; commit-delta criterion met by eager
    mirrors, not by adding deltas. Two stale pending-model tests reconciled.
  NEXT: optional dedicated sever re-resolve test; eager->lazy migration; the
    canonical src_components/src_architecture doc merge for the unlink lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-06-14T16:55:00Z
  TYPE: DECISION
  CLAIM: Story CLOSED. All checklist items landed and validated in the 3.14t
    venv. EXIT_GATE reconciled: per-family claim modes shipped (link/bind/
    cluster IX spellbooks; transfer already exclusive; a new unlink/sever
    transaction added by user direction); the "all four strategies apply
    commit deltas" clause is satisfied-by-redundancy because the link +
    cluster-membership mirrors are maintained EAGERLY -- the user confirmed
    eager is the FINAL design (no eager->lazy migration). Added a dedicated
    Step C sever-re-resolve integration test and merged the canonical docs
    (src_components.md "Transaction Admission Plane" + src_architecture.md
    "Aetheric Frame Responsibilities").
  EVIDENCE:
  - tests/integration/melder/conduit/test_conduit_integration_spellspace_hooks.py (test_sever_link_reresolves_borrowing_side_contract_consumers)
  - codex/context_compass/system_docs/src_components.md (Family Claim Modes + unlink transaction)
  - codex/context_compass/system_docs/src_architecture.md:608
  IMPACT: The scope-acquisition control plane is complete: moded admission +
    per-family claim modes + eager mirrors + the unlink/sever transaction,
    documented and tested.
  NEXT: none required. The unrelated concurrent-conjure frame-registry race is
    tracked separately (EPIC-2026-06-14-aether-frame-spell-registry-concurrent-access-race).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Implements the scope-acquisition control plane agreed on 2026-06-12. Patch
lane