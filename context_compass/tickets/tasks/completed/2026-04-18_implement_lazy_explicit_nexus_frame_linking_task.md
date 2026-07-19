# Task: Implement Lazy Explicit Nexus Frame Linking
- Completed: 2026-04-19T16:37:39Z
- Summary: Closed during the 2026-04-19 backlog cleanup pass after review/completed-downstream state.


## Metadata
- Task ID: TASK-2026-04-18-implement-lazy-explicit-nexus-frame-linking
- Story: STORY-2026-04-18-investigate-lazy-explicit-nexus-frame-linking
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-18T12:41:23Z
- Updated: 2026-04-19T16:37:39Z

## Objective
Remove eager/default Rift/Nexus frame state and make Nexus-frame realization
lazy and explicit, with no backward compatibility.

## Ticket Contract
- ENTRY_GATE: the investigation task mapped the eager/default frame blast
  radius and the user approved moving into implementation.
- EXECUTION_BOUNDARY: `Rift`, `Nexus`, interfaces, direct unit tests, and the
  minimal source docs needed to keep the new lazy explicit frame model honest.
- DEPENDENCIES:
  - tickets/tasks/2026-04-18_investigate_lazy_explicit_nexus_frame_linking_task.md
  - src/melder/aether/nexus/nexus.py
  - src/melder/aether/nexus/rift/rift.py
  - src/melder/utilities/interfaces/interfaces.py
  - src/melder/aether/nexus/configuration/nexus_configuration.py
  - src/melder/aether/nexus/frame_descriptor_manager.py
  - src/melder/aether/nexus/nexus_frame_record.py
  - tests/unit/melder/aether/test_nexus.py
  - tests/unit/melder/aether/test_rift_runtime_contracts.py
  - codex/context_compass/system_docs/src_architecture.md
  - codex/context_compass/system_docs/src_components.md
- EXIT_GATE: Rift creation is frame-free, Nexus no longer eagerly attaches or
  creates frames during Rift registration, and the focused validation ring is
  green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the refactor requires a
  broader space-target-opening design before the lazy Nexus-frame cut can land.

## Scope Boundaries
- In scope:
  - remove `Rift` constructor/default frame state
  - remove eager Nexus-frame attachment/materialization at Rift creation
  - make Nexus-frame access/create paths explicit/lazy
  - update Rift removal logic
  - rewrite direct tests/docs that still assume eager/default behavior
- Out of scope:
  - full future target-opening redesign
  - event-system replacement
  - broader room/workstation ownership changes

## Steps / Checklist
- [ ] Remove eager/default frame state from `Rift`.
- [ ] Remove eager Nexus-frame attach/create work from `Nexus.create_rift(...)` and `Nexus.add_rift(...)`.
- [ ] Refactor `get_nexus_frame_for_rift(...)` / `create_nexus_frame_for_rift(...)` to the lazy explicit model.
- [ ] Refactor `remove_rift(...)` so it no longer depends on Rift-owned Nexus-frame state.
- [ ] Rewrite focused tests/docs.
- [ ] Validate the focused ring.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- frame-free Rift creation
- lazy explicit Nexus-frame realization
- updated tests/docs
- focused validation evidence

## Validation
- Not run.
- Recommended commands:
  - `python -m pytest -q tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_rift_runtime_contracts.py`

## Risks / Rollback Notes
- Risk: removing all default frame state exposes more hidden viewer/target
  assumptions than the investigation found.
- Rollback: keep the cut bounded and fail fast rather than adding compatibility
  shims.

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
- DATETIME: 2026-04-18T12:41:23Z
  TYPE: PLAN
  CLAIM: This implementation cut removes eager/default frame state all at once:
    `Rift` stops storing frame/default fields, `Nexus` stops attaching frames
    during Rift creation, and explicit Nexus-frame request paths become the only
    place where topology policy is applied and frames may be realized.
  EVIDENCE:
  - tickets/tasks/2026-04-18_investigate_lazy_explicit_nexus_frame_linking_task.md:58-112
  - user_instruction: "ok go ahead and implement this"
  IMPACT: The lane is now implementation-ready without reopening the same
    planning argument.
  NEXT: patch `Rift`, then `Nexus`, then interfaces/tests/docs, then validate.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-18T14:17:49Z
  TYPE: FACT
  CLAIM: The lazy explicit Nexus-frame linking refactor is now implemented.
    `Rift` no longer stores eager Nexus/default frame state, `Nexus.create_rift(...)`
    no longer seeds or attaches frames during Rift creation/registration, frame
    realization now happens only through explicit `get_nexus_frame(...)` /
    `create_nexus_frame(...)` request paths, indexed access now requires an
    explicit frame name, and `Nexus.remove_rift(...)` detaches by topology-aware
    Nexus-record inspection instead of Rift-owned Nexus-frame state. The stale
    `default_target_frame_name` config knob was removed in the same pass because
    the runtime no longer uses it.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift.py:27-190
  - src/melder/aether/nexus/rift/rift.py:365-543
  - src/melder/aether/nexus/rift/rift.py:842-885
  - src/melder/aether/nexus/nexus.py:682-755
  - src/melder/aether/nexus/nexus.py:1590-1645
  - src/melder/aether/nexus/nexus.py:1846-1894
  - src/melder/aether/nexus/nexus.py:2043-2220
  - src/melder/aether/nexus/nexus.py:2790-2814
  - src/melder/aether/nexus/configuration/nexus_configuration.py:60-84
  - src/melder/aether/nexus/configuration/nexus_configuration.py:252-323
  - src/melder/utilities/interfaces/interfaces.py:6450-6488
  - src/melder/utilities/interfaces/interfaces.py:7604-7642
  - tests/unit/melder/aether/test_rift_runtime_contracts.py:160-285
  - tests/unit/melder/aether/test_nexus.py:534-545
  - tests/unit/melder/aether/test_nexus.py:3591-4285
  - tests/unit/melder/aether/test_nexus_configuration.py:165-304
  - tests/unit/melder/aether/test_aetheric_frame_configuration.py:136-147
  - tests/unit/melder/aether/test_nexus_frame_surface_projection.py:294-373
  - tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py:136-185
  - tests/integration/melder/aether/test_nexus_viewer_extended_surface_integration_matrix.py:145-242
  - tests/integration/melder/aether/test_nexus_viewer_general_helper_integration_matrix.py:115-122
  - codex/context_compass/system_docs/src_architecture.md:448-462
  - codex/context_compass/system_docs/src_components.md:525-535
  - codex/context_compass/system_docs/src_components.md:1844-1854
  IMPACT: Rift creation is now frame-free, and the remaining frame-link design
    can continue from explicit request paths instead of old eager/default
    scaffolding.
  NEXT: record the green validation result and return this lane for review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-18T14:17:49Z
  TYPE: MEASURE
  CLAIM: The focused lazy-linking validation ring is green.
  EVIDENCE:
  - validation_result: `python -m py_compile src/melder/aether/nexus/rift/rift.py src/melder/aether/nexus/nexus.py src/melder/aether/nexus/configuration/nexus_configuration.py src/melder/utilities/interfaces/interfaces.py tests/unit/melder/aether/test_rift_runtime_contracts.py tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_nexus_configuration.py tests/unit/melder/aether/test_aetheric_frame_configuration.py tests/unit/melder/aether/test_nexus_frame_surface_projection.py tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py tests/integration/melder/aether/test_nexus_viewer_extended_surface_integration_matrix.py tests/integration/melder/aether/test_nexus_viewer_general_helper_integration_matrix.py tests/integration/melder/aether/rift/static_rift_json_testbench_support.py tests/integration/melder/aether/rift/capability_rift_json_testbench_support.py` -> success
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_rift_runtime_contracts.py tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_nexus_configuration.py tests/unit/melder/aether/test_aetheric_frame_configuration.py tests/unit/melder/aether/test_nexus_frame_surface_projection.py tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py tests/integration/melder/aether/test_nexus_viewer_extended_surface_integration_matrix.py tests/integration/melder/aether/test_nexus_viewer_general_helper_integration_matrix.py tests/integration/melder/aether/rift/test_static_rift_json_testbench_integration.py tests/integration/melder/aether/rift/test_capability_rift_json_testbench_integration.py` -> 451 passed
  IMPACT: The no-compat runtime cut is stable enough to review before the next
    frame-contract or event-system lane.
  NEXT: return the task for acceptance and then choose the next Rift structural
    cut.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-18T14:17:49Z
  TYPE: FACT
  CLAIM: A small post-implementation cleanup pass removed the actual leftover
    compatibility junk from `rift.py`: the dead `_aether` slot/import/type
    references are gone, the `engage_frame(...)` alias is gone, and the stale
    constructor/runtime docstrings were tightened to match the new frame-free
    Rift model. The remaining `_aether` usage inside `CommandSystem` and
    `StaticFrameViewer` is real live runtime dependency, not leftover shims.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift.py:1-92
  - src/melder/aether/nexus/rift/rift.py:430-480
  - validation_result: `python -m py_compile src/melder/aether/nexus/rift/rift.py tests/unit/melder/aether/test_rift_runtime_contracts.py` -> success
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_rift_runtime_contracts.py tests/unit/melder/aether/test_nexus.py` -> 124 passed
  IMPACT: The lazy-linking lane no longer leaves obvious dead alias/scaffold
    junk in the core `Rift` runtime file.
  NEXT: return the lane for acceptance and then move to the next Rift cleanup
    or event-system slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
This task owns the actual no-compat implementation for lazy explicit
Nexus-frame linking.