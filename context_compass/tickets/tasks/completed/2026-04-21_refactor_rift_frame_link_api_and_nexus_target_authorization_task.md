# Task: Refactor Rift Frame Link API And Nexus Target Authorization
- Completed: 2026-04-22T11:14:18Z
- Summary: Closed during the 2026-04-22 rebaseline after `create_frame_link(frame_name)` replaced the old target-frame API and Nexus-managed link authorization landed.

## Metadata
- Task ID: TASK-2026-04-21-refactor-rift-frame-link-api-and-nexus-target-authorization
- Story: none
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-21T10:57:00Z
- Updated: 2026-04-22T11:14:18Z

## Objective
Replace the public Rift frame-attachment seam with `create_frame_link(frame_name)`,
remove caller-selected contract-name parameters, and make the attachment flow use
Nexus-managed frame topology rules whenever the targeted frame is Nexus-managed.

## Ticket Contract
- ENTRY_GATE: active board routing exists, the current frame-link/Nexus flow is
  evidenced in source, and the patch-doc set exists for this public API cut.
- EXECUTION_BOUNDARY: `Rift`, `FrameLinkContract`, `NexusFrameManager`,
  `Nexus`, `IRift`, the directly affected tests, and the live
  `src_architecture.md` / `src_components.md` surfaces only.
- DEPENDENCIES:
  - tickets/tasks/2026-04-11_define_frame_scoped_contract_registry_and_rift_binding_model.md
  - tickets/tasks/2026-04-11_propose_multi_contract_frame_policy_implementation_plan.md
  - system_docs/patches/active/rift_frame_link_api_and_nexus_target_enforcement/architecture_patch.md
  - system_docs/patches/active/rift_frame_link_api_and_nexus_target_enforcement/component_patch_rift.md
  - system_docs/patches/active/rift_frame_link_api_and_nexus_target_enforcement/component_patch_nexus.md
  - system_docs/patches/active/rift_frame_link_api_and_nexus_target_enforcement/component_patch_frame_link_contract.md
  - system_docs/patches/active/rift_frame_link_api_and_nexus_target_enforcement/code_description_patch_rift.md
- EXIT_GATE: `target_frame(...)` is removed from the live Rift contract,
  `create_frame_link(frame_name)` is the attachment seam, Nexus-managed frame
  topology rules are enforced during attachment, and the focused tests/docs are
  green/current.
- FAILURE_ESCALATION: record `DECISION_REQUEST` if frame-name-selected ACL
  contract materialization conflicts with the current ACL-chain model or widens
  beyond the bounded AR slice.

## Scope Boundaries
- In scope:
  - `Rift.target_frame(...)` removal
  - `Rift.create_frame_link(frame_name)` addition
  - `FrameLinkContract` constructor/setter simplification
  - Nexus-managed frame authorization during frame-link creation
  - frame-name default contract materialization for attachment
  - direct call-site/test/doc updates
- Out of scope:
  - general ACL registry redesign
  - room/workstation redesign
  - unrelated Nexus frame authoring changes
  - retained historical patch-doc rewrites

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: the API rename, Nexus-managed frame-link authorization
  fix, focused doc/test updates, and bounded validation ring are complete.

## Steps / Checklist
- [ ] Audit the current `Rift`, `FrameLinkContract`, `NexusFrameManager`, and
      `IRift` seam for the exact public/runtime delta.
- [ ] Implement `create_frame_link(frame_name)` and remove the old
      `target_frame(...)` API.
- [ ] Remove caller-provided contract-name selection from the frame-link seam.
- [ ] Ensure frame-link creation uses Nexus-managed frame topology rules when
      the target frame is Nexus-managed.
- [ ] Ensure the selected frame-link contract defaults to the targeted
      `frame_name`.
- [ ] Update the focused tests and live architecture/components docs.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further
      investigation.

## Deliverables
- `Rift.create_frame_link(frame_name)` as the only live frame-link creation API
- simplified `FrameLinkContract` constructor/update surface
- Nexus-enforced attachment behavior for Nexus-managed frames
- updated focused tests
- updated `src_architecture.md` and `src_components.md`

## Files / Paths Impacted
- src/melder/aether/nexus/rift/rift.py
- src/melder/aether/nexus/rift/frame_link/frame_link_contract.py
- src/melder/aether/nexus/nexus_frame_manager.py
- src/melder/aether/nexus/nexus.py
- src/melder/utilities/interfaces/interfaces.py
- tests/unit/melder/aether/
- tests/integration/melder/aether/
- codex/context_compass/system_docs/src_architecture.md
- codex/context_compass/system_docs/src_components.md

## Validation
- Not run.
- Recommended commands:
  - `pytest -q tests/unit/melder/aether/test_frame_link_contract_profiles.py`
  - `pytest -q tests/unit/melder/aether/test_rift_runtime_contracts.py`
  - `pytest -q tests/unit/melder/aether/test_nexus.py -k "frame_link or nexus_frame or target_frame or create_frame_link"`
  - `pytest -q tests/unit/melder/aether/test_nexus_frame_surface_projection.py`
  - `pytest -q tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py`
  - `pytest -q tests/integration/melder/aether/test_nexus_viewer_extended_surface_integration_matrix.py`

## Risks / Rollback Notes
- Risk: forcing frame-name-selected contracts can break frames that only expose
  the reserved `"default"` ACL chain.
  Rollback: materialize a frame-local same-name contract from the current
  selected ACL snapshot during link creation instead of falling back silently.
- Risk: the rename can miss JSON bench or doc call sites and leave mixed
  `target_frame` / `create_frame_link` vocabulary.
  Rollback: keep the rename sweep bounded to direct verified call sites and run
  focused test rings immediately after.

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
  - system_docs/patches/active/rift_frame_link_api_and_nexus_target_enforcement/architecture_patch.md
  - system_docs/patches/active/rift_frame_link_api_and_nexus_target_enforcement/component_patch_rift.md
  - system_docs/patches/active/rift_frame_link_api_and_nexus_target_enforcement/component_patch_nexus.md
  - system_docs/patches/active/rift_frame_link_api_and_nexus_target_enforcement/component_patch_frame_link_contract.md
  - system_docs/patches/active/rift_frame_link_api_and_nexus_target_enforcement/code_description_patch_rift.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: apply closure disposition after the API cut is accepted.

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-21T10:57:00Z
  TYPE: FACT
  CLAIM: The current frame-link seam is split incorrectly. `Rift.target_frame(...)`
    still accepts caller-selected contract names and validates descriptor/runtime
    posture, but it never asks Nexus whether a targeted Nexus-managed frame is
    actually accessible under `single`, `indexed`, or `one_per_workspace`.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift.py:367-470
  - src/melder/aether/nexus/rift/frame_link/frame_link_contract.py:46-285
  - src/melder/aether/nexus/nexus_frame_manager.py:325-588
  - codex/context_compass/system_docs/src_components.md:2059-2087
  IMPACT: A Rift can currently create a frame link to a Nexus-managed frame name
    without the attachment path itself enforcing the Nexus topology contract.
  NEXT: patch the API boundary so frame-link creation delegates Nexus-managed
    access authorization back through Nexus before the contract is created.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-21T10:57:00Z
  TYPE: FACT
  CLAIM: The current ACL container seeds only the reserved `"default"` chains.
    If the Rift frame-link contract is forced to use `frame_name` as its
    selected contract name, the attachment flow must explicitly materialize a
    same-name ACL contract instead of assuming it already exists.
  EVIDENCE:
  - src/melder/aether/nexus/acl/frame_acl_container.py:61-114
  - src/melder/aether/nexus/acl/frame_acl_container.py:787-827
  - src/melder/aether/nexus/frame_acl_manager.py:320-343
  IMPACT: The public API cut needs one explicit contract-materialization step
    during frame-link creation or the new frame-name-selected contract rule
    will fail against frames that only expose `"default"`.
  NEXT: implement a bounded Rift/Nexus helper that materializes a frame-name
    contract from the current selected ACL snapshot before the frame link is
    created.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-21T10:57:00Z
  TYPE: FACT
  CLAIM: The source-side API cut is now in place. `Rift` exposes
    `create_frame_link(frame_name)`, `FrameLinkContract` is fixed to frame-name
    selection, and Nexus now provides the authorization seam the Rift
    attachment path uses for Nexus-managed frames.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift.py:367-489
  - src/melder/aether/nexus/rift/frame_link/frame_link_contract.py:47-200
  - src/melder/aether/nexus/nexus.py:2094-2127
  - src/melder/aether/nexus/nexus_frame_manager.py:408-443
  IMPACT: The remaining work is no longer design; it is focused call-site/test
    cleanup plus validation of the new frame-name-selected contract behavior.
  NEXT: finish the focused test/doc sweep, then run the bounded pytest ring for
    Rift/Nexus/frame-link behavior.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-21T10:57:00Z
  TYPE: MEASURE
  CLAIM: The first unit validation pass exposed one remaining policy-order bug:
    `Rift.create_frame_link(...)` still applies the generic target-frame
    allow-list to Nexus-managed private frame names, so an authorized
    `one_per_workspace` Nexus frame link is rejected before the Nexus-managed
    topology decision can finish.
  EVIDENCE:
  - src/melder/aether/nexus/rift/rift.py:395-404
  - src/melder/aether/nexus/nexus.py:2443-2450
  - tests/unit/melder/aether/test_nexus.py:4320-4339
  IMPACT: Nexus-managed frames are not yet being treated differently from
    general target frames in the live attachment path, which is the core
    behavior the user asked to fix.
  NEXT: patch `Rift.create_frame_link(...)` so Nexus-managed authorization runs
    first and the generic allow/deny gate only applies to non-managed frames.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-21T10:57:00Z
  TYPE: MEASURE
  CLAIM: The focused validation ring is now green after the policy-order fix.
    The bounded unit and integration suites covering `FrameLinkContract`,
    `Rift`, Nexus frame-link behavior, frame-surface projection, viewer
    matrices, and the static/capability JSON benches all passed.
  EVIDENCE:
  - tests/unit/melder/aether/test_frame_link_contract_profiles.py
  - tests/unit/melder/aether/test_rift_runtime_contracts.py
  - tests/unit/melder/aether/test_nexus.py
  - tests/unit/melder/aether/test_nexus_frame_surface_projection.py
  - tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py
  - tests/integration/melder/aether/test_nexus_viewer_extended_surface_integration_matrix.py
  - tests/integration/melder/aether/rift/test_static_rift_json_testbench_integration.py
  - tests/integration/melder/aether/rift/test_capability_rift_json_testbench_integration.py
  IMPACT: The API rename and Nexus-managed frame-link authorization change are
    now covered across both direct unit contracts and the real room/viewer
    integration harnesses.
  NEXT: summarize the landed contract change for user review and wait for the
    next lane.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task replaces the old `target_frame(...)` attachment seam with a simpler
`create_frame_link(frame_name)` contract and moves Nexus-managed frame access
enforcement into that live attachment path.
