# Task: Scaffold Frame ACL Subsystem Placeholders

## Metadata
- Task ID: TASK-2026-04-04-scaffold-frame-acl-subsystem-placeholders
- Story: STORY-2026-04-04-frame-acl-subsystem-bootstrap
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-04T21:59:53Z
- Updated: 2026-04-05T17:50:09Z

## Objective
Add the first placeholder frame-scoped ACL subsystem objects and wire them
under the corrected ownership split:
- `Nexus -> FrameACLManager -> frame_name -> FrameACLContainer`
- `FrameACLManager`
- `FrameACLContainer`
- `FrameACLBuilder`
- `FrameACLConfiguration`
- `FrameACLValidator`

## Ticket Contract
- ENTRY_GATE: ACL epic/story are routed and the user has approved the
  manager/container shape for the first placeholder slice.
- EXECUTION_BOUNDARY: placeholder object structure and corrected
  Nexus/descriptor ownership wiring only.
- DEPENDENCIES:
  - tickets/epics/2026-04-02_rift_profile_surface_and_access_model_epic.md
  - tickets/stories/2026-04-04_frame_acl_subsystem_bootstrap_story.md
  - tickets/artifacts/nexus_acl_builder_and_persistence_model.md
  - src/melder/aether/nexus/frame_descriptor.py
- EXIT_GATE: the placeholder objects exist in code, `Nexus` owns the manager,
  the manager owns the frame ACL containers, descriptor creation ensures the
  matching container exists with defaults, and tests prove the one-builder
  object-singleton behavior.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the task starts to pull in
  full propagation/consumer behavior beyond placeholders and ownership.

## Scope Boundaries
- In scope:
  - new placeholder ACL subsystem classes
  - Nexus/descriptor ownership wiring
  - focused unit tests
- Out of scope:
  - full ACL propagation
  - final JSON config schema
  - live Rift/view/codegen integration

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: the placeholder ACL classes are landed, the corrected
  Nexus-owned manager / per-frame container split is wired, and the focused ACL
  placeholder plus Nexus unit surfaces passed.

## Steps / Checklist
- [x] Update the ACL artifact/tickets to reflect the manager/container shape.
- [x] Add placeholder ACL subsystem classes under `src/melder/aether/nexus/`.
- [x] Wire the manager under `Nexus`.
- [x] Ensure descriptor creation also creates the matching ACL container with defaults.
- [x] Add focused unit tests for ownership and one-builder-per-frame behavior.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- placeholder Frame ACL subsystem classes
- descriptor ownership wiring
- focused unit tests

## Files / Paths Impacted
- src/melder/aether/nexus/
- src/melder/aether/nexus/frame_descriptor.py
- tests/unit/melder/aether/
- tests/component/melder/aether/
- codex/context_compass/tickets/tasks/2026-04-04_scaffold_frame_acl_subsystem_placeholders_task.md
- codex/context_compass/attention_board.md
- codex/context_compass/artifact_board.md

## Validation
- Completed:
  - `python -m py_compile src/melder/aether/nexus/frame_acl_configuration.py src/melder/aether/nexus/frame_acl_validator.py src/melder/aether/nexus/frame_acl_builder.py src/melder/aether/nexus/frame_acl_container.py src/melder/aether/nexus/frame_acl_manager.py src/melder/aether/nexus/frame_descriptor_manager.py src/melder/aether/nexus/nexus.py tests/unit/melder/aether/test_frame_acl_subsystem.py`
  - `python -m pytest -q tests/unit/melder/aether/test_frame_acl_subsystem.py`
  - `python -m pytest -q tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_frame_acl_subsystem.py`
  - `python -m py_compile tests/unit/melder/aether/test_frame_acl_configuration.py tests/unit/melder/aether/test_frame_acl_validator.py tests/unit/melder/aether/test_frame_acl_builder.py tests/unit/melder/aether/test_frame_acl_container.py tests/unit/melder/aether/test_frame_acl_manager.py tests/component/melder/aether/test_frame_acl_component.py`
  - `python -m pytest -q tests/unit/melder/aether/test_frame_acl_configuration.py tests/unit/melder/aether/test_frame_acl_validator.py tests/unit/melder/aether/test_frame_acl_builder.py tests/unit/melder/aether/test_frame_acl_container.py tests/unit/melder/aether/test_frame_acl_manager.py tests/component/melder/aether/test_frame_acl_component.py`
  - `python -m pytest -q tests/unit/melder/aether/test_frame_acl_subsystem.py tests/unit/melder/aether/test_frame_acl_configuration.py tests/unit/melder/aether/test_frame_acl_validator.py tests/unit/melder/aether/test_frame_acl_builder.py tests/unit/melder/aether/test_frame_acl_container.py tests/unit/melder/aether/test_frame_acl_manager.py tests/component/melder/aether/test_frame_acl_component.py tests/unit/melder/aether/test_nexus.py`

## Risks / Rollback Notes
- Risk: placeholder classes grow fake behavior that locks in the wrong model.
  Rollback: keep them small and structural.

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
  - system_docs/patches/active/frame_acl_subsystem_bootstrap/architecture_patch.md
  - system_docs/patches/active/frame_acl_subsystem_bootstrap/component_patch_frame_acl_manager.md
  - system_docs/patches/active/frame_acl_subsystem_bootstrap/component_patch_frame_acl_container.md
  - system_docs/patches/active/frame_acl_subsystem_bootstrap/component_patch_frame_acl_builder.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-04T22:47:18Z
  TYPE: FACT
  CLAIM: The ACL placeholder lane now has the broader mixed unit/component
    coverage tranche you asked for. Beyond the original placeholder file, the
    ACL subsystem now has dedicated unit files for configuration, validator,
    builder, container, and manager behavior, plus a component file that mixes
    ACL and descriptor lifecycle through the Nexus facade. The combined focused
    ACL/Nexus unit/component tranche passed together.
  EVIDENCE:
  - tests/unit/melder/aether/test_frame_acl_subsystem.py:1-155
  - tests/unit/melder/aether/test_frame_acl_configuration.py:1-90
  - tests/unit/melder/aether/test_frame_acl_validator.py:1-58
  - tests/unit/melder/aether/test_frame_acl_builder.py:1-126
  - tests/unit/melder/aether/test_frame_acl_container.py:1-143
  - tests/unit/melder/aether/test_frame_acl_manager.py:1-98
  - tests/component/melder/aether/test_frame_acl_component.py:1-66
  - command:python -m pytest -q tests/unit/melder/aether/test_frame_acl_subsystem.py tests/unit/melder/aether/test_frame_acl_configuration.py tests/unit/melder/aether/test_frame_acl_validator.py tests/unit/melder/aether/test_frame_acl_builder.py tests/unit/melder/aether/test_frame_acl_container.py tests/unit/melder/aether/test_frame_acl_manager.py tests/component/melder/aether/test_frame_acl_component.py tests/unit/melder/aether/test_nexus.py
  IMPACT: The placeholder ACL subsystem is no longer covered by a couple of
    narrow tests. The object graph now has broad unit/component coverage for
    creation, reuse, mutation-session flow, history, validation, cleanup, and
    facade-triggered propagation behavior.
  NEXT: keep the task in review unless you want an integration-layer ACL test
    tranche on top of this broader unit/component coverage.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-04T22:20:26Z
  TYPE: FACT
  CLAIM: The placeholder ACL slice still had one lifecycle hole after the first
    landing: frame removal could drop the Nexus frame record through
    `check_for_aetheric_frame(...)`, but the matching frame ACL container was
    not being removed. The facade should own that propagation too so the frame
    ACL state does not outlive the frame itself.
  EVIDENCE:
  - src/melder/aether/nexus/nexus.py:1022-1053
  - src/melder/aether/nexus/acl/frame_acl_manager.py:1-118
  IMPACT: The ACL subsystem needs one more cleanup path before the placeholder
    slice can be considered lifecycle-coherent.
  NEXT: add frame ACL container removal on frame-detach and test it through the
    ACL manager and the Nexus frame-detach facade path.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-04T22:20:26Z
  TYPE: FACT
  CLAIM: The placeholder ACL subsystem slice is now landed with the corrected
    ownership split. `Nexus` owns `FrameACLManager`, the manager owns
    `frame_name -> FrameACLContainer`, descriptor creation now also ensures the
    matching frame ACL container exists with defaults, and the container owns
    the per-frame builder/configuration/validator/history placeholders. The
    focused ACL placeholder and Nexus unit surfaces both passed after the wire-up.
  EVIDENCE:
  - src/melder/aether/nexus/frame_acl_configuration.py:1-206
  - src/melder/aether/nexus/frame_acl_validator.py:1-105
  - src/melder/aether/nexus/frame_acl_builder.py:1-164
  - src/melder/aether/nexus/frame_acl_container.py:1-177
  - src/melder/aether/nexus/frame_acl_manager.py:1-141
  - src/melder/aether/nexus/frame_descriptor_manager.py:1-628
  - src/melder/aether/nexus/nexus.py:1-1730
  - tests/unit/melder/aether/test_frame_acl_subsystem.py:1-119
  - command:python -m pytest -q tests/unit/melder/aether/test_frame_acl_subsystem.py
  - command:python -m pytest -q tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_frame_acl_subsystem.py
  IMPACT: The ACL lane now has a real runtime foothold instead of just patch
    docs and artifact language, and the ownership split matches the corrected
    model you selected.
  NEXT: review the placeholder object shape and decide the next ACL step:
    builder methods/schema semantics, validator expansion, or propagation rules.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-04T21:59:53Z
  TYPE: PLAN
  CLAIM: The first placeholder ACL slice should codify the corrected ownership
    chain and nothing more:
    `Nexus -> FrameACLManager -> frame_name -> FrameACLContainer ->
    {builder, configuration, validator, history}`. The builder should be
    object-singleton per frame container and returned by that container each
    time, not recreated ad hoc. Descriptor creation should also ensure the
    matching frame ACL container exists and is initialized with defaults.
  EVIDENCE:
  - user_instruction: "FrameACLContainer can hold history of different configurations and the builder and anything else we might need to hold in there"
  - user_instruction: "there is only 1 builder and we make it a object based singleton"
  - user_instruction: "Nexus owns the FrameACLManager and then it owns inside it all those other objects"
  IMPACT: We can start code without pretending to have solved the final ACL
    propagation engine, and we avoid confusing the descriptor with the direct
    owner of ACL manager state.
  NEXT: add the placeholder classes, keep the manager on `Nexus`, and wire the
    container creation to descriptor creation events.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task exists to scaffold the first frame-scoped ACL subsystem objects and
wire them under the corrected Nexus/descriptor boundary. The placeholder
classes are now landed and the task is in review pending acceptance or the next
ACL refinement slice.
