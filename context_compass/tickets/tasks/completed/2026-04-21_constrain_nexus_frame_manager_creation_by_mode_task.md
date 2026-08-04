# Task: Constrain NexusFrameManager Creation By Mode
- Completed: 2026-04-22T11:14:18Z
- Summary: Closed during the 2026-04-22 rebaseline after the raw NexusFrameManager mode constraints landed and the focused frame-authoring validation ring stayed green.

## Metadata
- Task ID: TASK-2026-04-21-constrain-nexus-frame-manager-creation-by-mode
- Story: none
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-21T23:12:28Z
- Updated: 2026-04-22T11:14:18Z

## Objective
Constrain the raw `NexusFrameManager` authoring path so `single`,
`indexed`, and `one_per_workspace` behave coherently even when callers use the
manager directly instead of the Rift-scoped Nexus creation APIs.

## Ticket Contract
- ENTRY_GATE: the Rift-facing Nexus frame model is already enforced and the
  remaining gap is isolated to raw manager authoring.
- EXECUTION_BOUNDARY: `NexusFrameManager`, directly affected Nexus docs/tests,
  and this task/patch lane only.
- DEPENDENCIES:
  - tickets/tasks/2026-04-21_refactor_rift_frame_link_api_and_nexus_target_authorization_task.md
  - system_docs/patches/active/nexus_frame_manager_mode_constrained_creation/architecture_patch.md
  - system_docs/patches/active/nexus_frame_manager_mode_constrained_creation/component_patch_nexus_frame_manager.md
- EXIT_GATE: raw manager creation is mode-constrained, the Rift-facing behavior
  remains unchanged, and the focused tests/docs are green/current.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if one-per-workspace raw manager
  creation needs a new owner-carrying public API instead of a fail-fast block.

## Scope Boundaries
- In scope:
  - `NexusFrameManager.create(...)`
  - `NexusFrameManager.create_dynamic_frame(...)`
  - mode-aware raw creation validation
  - focused tests and live docs for this behavior
- Out of scope:
  - auto-provisioning
  - `Rift.create_nexus_frame(...)` semantics
  - wider frame-builder API redesign
  - graph updates

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: the manager constraints, focused docs, and bounded
  validation ring are complete.

## Steps / Checklist
- [ ] Audit the raw manager creation path against the agreed mode semantics.
- [ ] Implement mode-aware validation for raw manager creation.
- [ ] Keep Rift-scoped create/get/list/link behavior unchanged.
- [ ] Update the live docs if the behavior contract changes materially.
- [ ] Add focused tests for single/indexed/one_per_workspace raw creation.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further
      investigation.

## Deliverables
- mode-constrained raw `NexusFrameManager` creation behavior
- focused tests proving the constraints
- updated docs if needed

## Files / Paths Impacted
- src/melder/aether/nexus/nexus_frame_manager.py
- tests/unit/melder/aether/
- tests/component/melder/aether/
- tests/integration/melder/aether/
- codex/context_compass/system_docs/src_architecture.md
- codex/context_compass/system_docs/src_components.md

## Validation
- Not run.
- Recommended commands:
  - `pytest -q tests/unit/melder/aether/test_nexus_frame_manager.py`
  - `pytest -q tests/unit/melder/aether/test_nexus_frame_authoring.py`
  - `pytest -q tests/integration/melder/aether/test_nexus_frame_authoring_integration.py`

## Risks / Rollback Notes
- Risk: blocking raw one-per-workspace creation may expose that callers need a
  new owner-aware builder/create path.
  Rollback: fail fast now and stage a dedicated owner-aware authoring lane
  rather than faking ownership in the raw manager path.

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
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/nexus_frame_manager_mode_constrained_creation/architecture_patch.md
  - system_docs/patches/active/nexus_frame_manager_mode_constrained_creation/component_patch_nexus_frame_manager.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: apply closure disposition after review.

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-21T23:12:28Z
  TYPE: PLAN
  CLAIM: The remaining gap is below the Rift-facing Nexus API. The mode-aware
    get/create/list/link behavior is already enforced for Rifts, but the raw
    `NexusFrameManager.create(...)` path is still more permissive than the
    agreed `single` / `indexed` / `one_per_workspace` model.
  EVIDENCE:
  - src/melder/aether/nexus/nexus.py:2022-2146
  - src/melder/aether/nexus/nexus_frame_manager.py:173-281
  - src/melder/aether/nexus/nexus_frame_manager.py:364-631
  IMPACT: We need one more manager-level constraint pass so direct authoring
    cannot bypass the mode semantics we already enforce at the Rift layer.
  NEXT: inspect the current tests around frame authoring and decide the exact
    fail-fast rules for raw `single` and `one_per_workspace` creation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-21T23:12:28Z
  TYPE: FACT
  CLAIM: The current source already formalizes mode-aware behavior for the
    Rift-facing Nexus paths, but raw manager authoring is still unconstrained
    by `nexus_frame_mode`. Existing direct-manager tests are also mostly
    indexed-only, so the raw `single` and `one_per_workspace` behavior is not
    locked down yet.
  EVIDENCE:
  - src/melder/aether/nexus/nexus.py:2022-2146
  - src/melder/aether/nexus/nexus_frame_manager.py:173-281
  - src/melder/aether/nexus/nexus_frame_manager.py:364-631
  - tests/unit/melder/aether/test_nexus_frame_manager.py:163-287
  - tests/component/melder/aether/test_nexus_frame_authoring_component.py:53-74
  - tests/integration/melder/aether/test_nexus_frame_authoring_integration.py:172-195
  IMPACT: We can close the behavior gap with one bounded manager validation
    helper and a small amount of focused authoring coverage.
  NEXT: implement fail-fast raw creation rules for `single` and
    `one_per_workspace`, then add the missing test coverage.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-21T23:12:28Z
  TYPE: MEASURE
  CLAIM: The first validation pass exposed the necessary separation inside the
    manager: blocking all `one_per_workspace` manager creation also blocks the
    internal Rift-scoped `create_frame_for_rift(...)` path, because that path
    still reuses the raw `create(...)` body to realize the private frame.
  EVIDENCE:
  - src/melder/aether/nexus/nexus_frame_manager.py:364-456
  - tests/component/melder/aether/test_nexus_frame_authoring_component.py:122-325
  - tests/integration/melder/aether/test_nexus_frame_authoring_integration.py:37-333
  IMPACT: The manager needs two paths, not one: public raw authoring must be
    mode-constrained, while the internal Rift-scoped creation path must bypass
    that public raw-creation gate after it has already resolved topology.
  NEXT: split the shared creation body into a private helper so
    `create_frame_for_rift(...)` can realize private frames without reopening
    the public raw manager seam.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-21T23:12:28Z
  TYPE: MEASURE
  CLAIM: The bounded validation ring is green after splitting the shared
    realization body from the public raw manager gate. Public raw creation is
    now mode-constrained, while the internal Rift-scoped path still realizes
    private `one_per_workspace` frames correctly.
  EVIDENCE:
  - src/melder/aether/nexus/nexus_frame_manager.py:173-335
  - src/melder/aether/nexus/nexus_frame_manager.py:364-489
  - codex/context_compass/system_docs/src_architecture.md:474-482
  - codex/context_compass/system_docs/src_components.md:509-518
  - tests/unit/melder/aether/test_nexus_frame_manager.py
  - tests/component/melder/aether/test_nexus_frame_authoring_component.py
  - tests/integration/melder/aether/test_nexus_frame_authoring_integration.py
  IMPACT: The frame-manager layer now matches the explicit-creation,
    mode-enforced behavior model we agreed on without breaking Rift-scoped
    Nexus-frame creation.
  NEXT: review the landed mode constraints and decide whether you want a
    follow-on owner-aware builder lane or another Nexus behavior slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task closes the remaining Nexus frame-model gap by constraining raw
manager creation to the same mode semantics already enforced for Rift-facing
access and targeting.
