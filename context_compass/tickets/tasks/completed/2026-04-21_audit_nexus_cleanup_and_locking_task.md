# Task: Audit Nexus Cleanup And Locking
- Completed: 2026-04-22T11:14:18Z
- Summary: Closed during the 2026-04-22 rebaseline after the bounded Nexus cleanup/locking audit fix and validation were accepted into the fresh baseline.

## Metadata
- Task ID: TASK-2026-04-21-audit-nexus-cleanup-and-locking
- Story: none
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-21T23:35:09Z
- Updated: 2026-04-22T11:14:18Z

## Objective
Audit the live Nexus-side objects for cleanup ordering, ownership clarity, and
lock usage, then patch only the real cleanup/locking issues that are proven in
source.

## Ticket Contract
- ENTRY_GATE: the current Nexus frame-model and frame-link lanes are complete
  enough that a cross-object cleanup/locking audit will not be invalidated by
  immediate interface churn.
- EXECUTION_BOUNDARY: `src/melder/aether/nexus/**`, directly affected tests,
  and the live architecture/components docs only.
- DEPENDENCIES:
  - tickets/tasks/2026-04-21_constrain_nexus_frame_manager_creation_by_mode_task.md
  - tickets/tasks/2026-04-21_refactor_rift_frame_link_api_and_nexus_target_authorization_task.md
- EXIT_GATE: cleanup order, owned state teardown, and lock usage across the
  Nexus-side objects have been reviewed, findings are documented, and any
  evidence-backed fixes are validated.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if a cleanup/locking issue would
  require widening into non-Nexus subsystems or a broader threading-policy
  change.

## Scope Boundaries
- In scope:
  - Nexus-side objects under `src/melder/aether/nexus/**`
  - cleanup ordering
  - ownership nulling
  - lock usage and unnecessary lock spans
  - focused validation for touched Nexus objects
- Out of scope:
  - non-Nexus global threading policy changes
  - graph refresh
  - unrelated runtime refactors

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: the bounded audit is complete, the real lock-discipline
  issue in `RiftGateController` is fixed and validated, and no broader
  evidence-backed Nexus cleanup rewrite was justified.

## Steps / Checklist
- [ ] Inventory Nexus-side classes, cleanup methods, and lock-bearing objects.
- [ ] Read the high-risk objects in bounded chunks and record findings.
- [ ] Patch only evidence-backed cleanup/locking issues.
- [ ] Run focused validation on the touched Nexus objects.
- [ ] Update live docs if object ownership/cleanup semantics change materially.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further
      investigation.

## Deliverables
- evidence-backed Nexus cleanup/locking audit
- any bounded fixes required by the audit
- focused validation results

## Files / Paths Impacted
- src/melder/aether/nexus/**
- tests/unit/melder/aether/
- tests/component/melder/aether/
- tests/integration/melder/aether/
- codex/context_compass/system_docs/src_architecture.md
- codex/context_compass/system_docs/src_components.md

## Validation
- Not run.
- Recommended commands:
  - `pytest -q tests/unit/melder/aether -k "nexus"`
  - `pytest -q tests/component/melder/aether -k "nexus"`
  - `pytest -q tests/integration/melder/aether -k "nexus"`

## Risks / Rollback Notes
- Risk: cleanup-order or locking fixes can easily widen into adjacent AR
  surfaces if the ownership boundary is not kept tight.
  Rollback: keep the audit evidence-first and patch only the Nexus object set
  directly implicated by the finding.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-21T23:35:09Z
  TYPE: PLAN
  CLAIM: This lane is a bounded Nexus-side audit, not a speculative threading
    rewrite. The target is the live Nexus object set under
    `src/melder/aether/nexus/**`, with focus on cleanup ordering, ownership
    nulling, and lock usage after the recent frame-manager and frame-link work.
  EVIDENCE:
  - user_instruction: "go over all the nexus objects and make sure we got good cleanup order and properly setup everything"
  - user_instruction: "ensure that we're properly locking things no excessive locking just track the object usages"
  IMPACT: The audit must inventory first, then patch only real issues rather
    than reopening broad Nexus design work.
  NEXT: inventory Nexus-side classes, cleanup methods, and lock-bearing objects
    to identify the high-risk review set.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-21T23:35:09Z
  TYPE: FACT
  CLAIM: The inventory shows a clear high-risk review set for cleanup/locking:
    `Nexus`, `FrameACLManager`, `FrameDescriptorManager`,
    `NexusFrameManager`, and `FrameACLContainer`. Those are the Nexus-side
    objects that own long-lived registries/maps and coordinate cleanup of other
    objects. The rest of the Nexus tree is mostly narrower config/value objects
    or downstream room/viewer surfaces.
  EVIDENCE:
  - src/melder/aether/nexus/nexus.py:57-105
  - src/melder/aether/nexus/frame_acl_manager.py:35-95
  - src/melder/aether/nexus/frame_descriptor_manager.py:28-103
  - src/melder/aether/nexus/nexus_frame_manager.py:22-77
  - src/melder/aether/nexus/acl/frame_acl_container.py:29-103
  IMPACT: We can review the real ownership/cleanup/locking risk first instead
    of diffusing effort across every small Nexus-adjacent class.
  NEXT: read the cleanup bodies and main lock-bearing mutation paths for those
    five high-risk objects in bounded chunks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-21T23:35:09Z
  TYPE: FACT
  CLAIM: `RiftGateController` is the first real lock-discipline outlier. Its
    class docstring says registry mutation is serialized by the controller
    `RLock`, but the live implementation only uses that lock in `cleanup()`.
    The register/unregister/get/count paths mutate or read the same registry
    without the controller lock, which leaves duplicate-registration checks and
    cleanup races semantically unprotected.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_gate_controller/rift_gate_controller.py:8-24
  - src/melder/aether/nexus/rift/rift_gate_controller/rift_gate_controller.py:44-55
  - src/melder/aether/nexus/rift/rift_gate_controller/rift_gate_controller.py:85-237
  IMPACT: This is a real mismatch between the documented concurrency contract
    and the live implementation, and it affects a Nexus-owned control-plane
    object that multiple Rift lifecycle paths touch.
  NEXT: patch `RiftGateController` so registry reads and writes actually use the
    controller lock and cleanup snapshots child gates before cleaning them.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-21T23:35:09Z
  TYPE: MEASURE
  CLAIM: The bounded validation ring is green after the `RiftGateController`
    lock-discipline fix. The focused gate/controller/Nexus tests passed, and
    the broader high-risk manager review did not expose another cleanup or
    locking issue strong enough to justify a wider rewrite.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_gate_controller/rift_gate_controller.py:44-237
  - src/melder/aether/nexus/nexus.py:217-310
  - src/melder/aether/nexus/frame_acl_manager.py:104-254
  - src/melder/aether/nexus/frame_descriptor_manager.py:107-169
  - src/melder/aether/nexus/nexus_frame_manager.py:79-335
  - tests/unit/melder/aether/test_rift_gate.py
  - tests/unit/melder/aether/test_nexus.py
  - tests/unit/melder/aether/test_rift_runtime_contracts.py
  - tests/unit/melder/aether/test_rift_space.py
  - tests/unit/melder/aether/test_static_rift_space.py
  IMPACT: The live Nexus-side audit now has one concrete fix and one bounded
    conclusion: the remaining high-risk manager/container cleanup paths look
    consistent enough to leave alone until a stronger source-backed issue
    appears.
  NEXT: review the audit result and decide whether you want a deeper sweep into
    the downstream room/viewer surfaces or a different Nexus lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-21T23:35:09Z
  TYPE: FACT
  CLAIM: The controller snapshot tuples I introduced are not necessary for this
    object. The user explicitly wants direct under-lock iteration here, and for
    this narrow controller registry path we can remove the extra allocation and
    keep the iteration under the controller lock instead.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift_gate_controller/rift_gate_controller.py:44-57
  - src/melder/aether/nexus/rift/rift_gate_controller/rift_gate_controller.py:164-237
  - user_instruction: "remove that tuple shit everywhere"
  IMPACT: The controller keeps the lock-discipline fix, but drops the
    unnecessary snapshot allocations and returns to direct registry iteration.
  NEXT: patch the controller methods to iterate the live registry under the
    controller lock and rerun the focused gate/controller validation ring.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task audits Nexus-side objects for cleanup ordering and lock usage after
the recent Nexus behavior/model changes, then patches only evidence-backed
issues. The one concrete fix was in `RiftGateController`; no wider Nexus
cleanup rewrite was justified by the bounded high-risk review.
