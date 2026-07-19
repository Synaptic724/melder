# Task: Enforce Dynamic-Only Nexus Frame Manager Contract
- Completed: 2026-04-26T11:39:24Z
- Summary: Closed after Nexus-managed frame authoring was forced to the
  dynamic-only posture and the focused frame-authoring validation ring was
  green.

## Metadata
- Task ID: TASK-2026-04-20-enforce-dynamic-only-nexus-frame-manager-contract
- Story:
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-20T05:45:38Z
- Updated: 2026-04-26T11:39:24Z

## Objective
Tighten the Nexus frame authoring subsystem so every Nexus-managed frame is
dynamic, AI-native, and Rift-enabled; remove the misleading automatic-mode
surface; and replace weak `Any` typing with the real `IAethericFrame`
contract.

## Ticket Contract
- ENTRY_GATE: the user explicitly approved implementation after a full manual
  read of `nexus_frame_manager.py`, `nexus_frame_configuration.py`, and
  `nexus_frame_builder.py`.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/nexus/nexus_frame_manager.py`
  - `src/melder/aether/nexus/nexus_frame_configuration.py`
  - `src/melder/aether/nexus/nexus_frame_builder.py`
  - directly affected tests in `tests/unit/melder/aether/`
  - this task ticket and `attention_board.md`
- DEPENDENCIES:
  - `src/melder/aether/nexus/nexus_frame_manager.py`
  - `src/melder/aether/nexus/nexus_frame_configuration.py`
  - `src/melder/aether/nexus/nexus_frame_builder.py`
  - `src/melder/utilities/interfaces/interfaces.py`
- EXIT_GATE: Nexus-managed frame authoring no longer exposes automatic-mode
  construction, manager/configuration creation paths hard-enforce
  `dynamic + ai_native_enabled + rift_enabled`, `_frames_by_name` is typed to
  `IAethericFrame`, and the focused frame-authoring/Nexus test ring is green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if enforcing the contract
  requires widening into unrelated Spellbook/Aether frame-posture semantics or
  broader public API migration outside the Nexus-frame subsystem.

## Scope Boundaries
- In scope:
  - Nexus frame manager authoring contract
  - Nexus frame configuration and builder surface
  - typed frame registry and frame-returning method signatures
  - directly affected authoring tests
- Out of scope:
  - lower Melder `SystemState.dynamic` semantics
  - unrelated Nexus stale-method cleanup
  - broader AR/codegen architecture changes

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly wants all Nexus-managed frames forced
  to dynamic, AI-native, and Rift-enabled, and wants `IAethericFrame` used
  instead of `Any`.

## Steps / Checklist
- [ ] Confirm exact authoring blast radius across manager/configuration/builder/tests.
- [ ] Remove automatic Nexus-frame authoring helpers and docs.
- [ ] Enforce dynamic/AI-native/Rift-enabled contract in the configuration and manager.
- [ ] Replace weak `Any` frame registry/return types with `IAethericFrame`.
- [ ] Add or update focused authoring tests for the tightened contract.
- [ ] Run focused validation.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- tightened Nexus-frame contract
- typed `IAethericFrame` manager registry and return surfaces
- focused validation results

## Files / Paths Impacted
- codex/context_compass/tickets/tasks/2026-04-20_enforce_dynamic_only_nexus_frame_manager_contract_task.md
- codex/context_compass/attention_board.md
- src/melder/aether/nexus/nexus_frame_manager.py
- src/melder/aether/nexus/nexus_frame_configuration.py
- src/melder/aether/nexus/nexus_frame_builder.py
- tests/unit/melder/aether/test_nexus_frame_authoring.py

## Validation
- Not run.
- Recommended commands:
  - `python -m pytest -q tests/unit/melder/aether/test_nexus_frame_authoring.py tests/unit/melder/aether/test_nexus.py -k "nexus_frame or create_nexus_frame"`

## Risks / Rollback Notes
- Risk: the subsystem still allows invalid posture through hidden/manual
  configuration mutation or partial create failure.
  Rollback: enforce posture in both configuration and manager create path and
  keep the patch bounded to this subsystem.

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
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-20T05:45:38Z
  TYPE: FACT
  CLAIM: The current Nexus-frame subsystem is internally inconsistent.
    Rift-created Nexus frames already route through dynamic creation, but the
    generic authoring surface still exposes automatic-mode helpers and the
    manager registry is typed as `Dict[str, Any]` instead of the real
    `IAethericFrame` contract.
  EVIDENCE:
  - src/melder/aether/nexus/nexus_frame_manager.py:70-71
  - src/melder/aether/nexus/nexus_frame_manager.py:167-213
  - src/melder/aether/nexus/nexus_frame_manager.py:364-403
  - src/melder/aether/nexus/nexus_frame_configuration.py:123-195
  - src/melder/aether/nexus/nexus_frame_builder.py:84-113
  IMPACT: The subsystem leaks a posture choice that the Rift-facing path has
    already effectively rejected, and the weak `Any` typing hides the real
    frame contract.
  NEXT: patch the manager/configuration/builder surface so Nexus-managed frames
    are dynamic-only and the frame registry uses `IAethericFrame`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-20T05:45:38Z
  TYPE: FACT
  CLAIM: The dynamic-only contract patch is now implemented in the Nexus-frame
    subsystem. The manager registry and frame-returning methods now use
    `IAethericFrame`, the automatic authoring path is removed from the manager,
    configuration, and builder, the configuration and manager both reject
    non-dynamic/non-AI-native/non-Rift-enabled posture, the builder now
    defaults to the only valid Nexus-frame posture, and `create(...)` now
    rolls back manager-owned state if later binding/bootstrap steps fail.
  EVIDENCE:
  - src/melder/aether/nexus/nexus_frame_manager.py:1-733
  - src/melder/aether/nexus/nexus_frame_configuration.py:1-309
  - src/melder/aether/nexus/nexus_frame_builder.py:1-254
  - tests/unit/melder/aether/test_nexus_frame_authoring.py:1-98
  IMPACT: The subsystem now matches the actual agent-usable contract instead of
    exposing contradictory posture choices or weak `Any` typing.
  NEXT: run the focused Nexus-frame authoring and Nexus frame-creation
    validation ring.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-20T05:45:38Z
  TYPE: MEASURE
  CLAIM: The dynamic-only Nexus-frame contract patch is green on syntax and the
    focused frame-authoring/Nexus creation ring.
  EVIDENCE:
  - validation_result: `python -m py_compile src/melder/aether/nexus/nexus_frame_manager.py src/melder/aether/nexus/nexus_frame_configuration.py src/melder/aether/nexus/nexus_frame_builder.py tests/unit/melder/aether/test_nexus_frame_authoring.py` -> success
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_nexus_frame_authoring.py tests/unit/melder/aether/test_nexus.py -k "nexus_frame or create_nexus_frame"` -> `9 passed, 103 deselected`
  IMPACT: The contract tightening is stable enough to return now instead of
    widening into unrelated Nexus or lower Melder posture work.
  NEXT: report the exact API/contract changes and decide whether to continue
    tightening adjacent Nexus-frame surfaces.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-20T05:45:38Z
  TYPE: FACT
  CLAIM: The post-patch review found two stale contract remnants inside the
    touched objects: the builder `__init__` docstring still claimed posture
    fields start unset, and `_bootstrap_root_conduit(...)` still carried an
    impossible automatic-mode branch even though automatic Nexus-managed frames
    are now disallowed. Both are now aligned to the dynamic-only contract.
  EVIDENCE:
  - src/melder/aether/nexus/nexus_frame_builder.py:51-56
  - src/melder/aether/nexus/nexus_frame_configuration.py:65-74
  - src/melder/aether/nexus/nexus_frame_manager.py:803-828
  IMPACT: The touched object docs and code paths now match the actual contract
    instead of preserving stale automatic-mode wording or dead conditional
    logic.
  NEXT: rerun the focused Nexus-frame validation ring after the cleanup pass.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-20T05:45:38Z
  TYPE: FACT
  CLAIM: The collaborator typing cleanup is now aligned with interfaces. The
    manager constructor now requires `INexus`, the builder constructor now
    requires `INexusFrameManager`, and the root-conduit bootstrap path now
    returns `IConduit` instead of `Any`. The touched Nexus-frame files no
    longer carry stray `Any` collaborator typing.
  EVIDENCE:
  - src/melder/utilities/interfaces/interfaces.py:8354-8381
  - src/melder/aether/nexus/nexus_frame_manager.py:1-20
  - src/melder/aether/nexus/nexus_frame_builder.py:1-13
  IMPACT: The Nexus-frame subsystem now exposes explicit collaborator contracts
    instead of hiding them behind weak `Any` annotations.
  NEXT: report the collaborator interface cleanup alongside the dynamic-only
    contract patch.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
This task owns the dynamic-only Nexus-frame contract tightening lane.
