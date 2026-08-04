# Task: Add Frame ACL Command Configuration And Validation
- Completed: 2026-04-13T11:43:06Z
- Summary: Closed the first typed command-configuration substrate slice after the later ACL bundle work treated it as settled foundation.

## Metadata
- Task ID: TASK-2026-04-11-add-frame-acl-command-configuration-and-validation
- Story: STORY-2026-04-11-extend-frame-acl-bundle-with-command-configuration
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-11T11:08:44Z
- Updated: 2026-04-13T11:43:06Z

## Objective
Add a typed `FrameACLCommandConfiguration` sibling to the current frame ACL
bundle and extend the validator so command rules are validated separately from
view/codegen rules.

## Ticket Contract
- ENTRY_GATE: the named-contract bundle seam is landed, the ACL design artifact
  already points toward typed sibling configurations, and the user explicitly
  approved starting with command configuration plus validator support.
- EXECUTION_BOUNDARY: command configuration object, bundle wiring, validator
  pass, builder/default serialization support, focused tests, and patch-doc
  sync only.
- DEPENDENCIES:
  - tickets/stories/2026-04-11_extend_frame_acl_bundle_with_command_configuration_story.md
  - tickets/artifacts/nexus_acl_builder_and_persistence_model.md
  - system_docs/patches/active/frame_acl_command_configuration/architecture_patch.md
  - system_docs/patches/active/frame_acl_command_configuration/component_patch_frame_acl_command_configuration.md
  - system_docs/patches/active/frame_acl_command_configuration/component_patch_frame_acl_configuration.md
  - system_docs/patches/active/frame_acl_command_configuration/component_patch_frame_acl_validator.md
  - system_docs/patches/active/frame_acl_command_configuration/component_patch_frame_acl_builder.md
  - src/melder/aether/nexus/acl/frame_acl_configuration.py
  - src/melder/aether/nexus/acl/frame_acl_validator.py
  - src/melder/aether/nexus/acl/frame_acl_builder.py
  - src/melder/utilities/interfaces/interfaces.py
- EXIT_GATE: the frame ACL bundle carries command configuration, validator
  support is live, focused tests pass, and the task is ready for review.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the first cut forces
  independent view/command/codegen selection instead of the bundled model.

## Scope Boundaries
- In scope:
  - `FrameACLCommandConfiguration`
  - default creation and JSON round-trip
  - `FrameACLConfiguration` bundle extension
  - `FrameACLValidator` command validation pass
  - `FrameACLBuilder` wiring
  - focused unit tests
- Out of scope:
  - static runtime execution
  - capability runtime execution
  - cross-config warning/report channel
  - independent per-type bundle selection

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly approved implementing the command ACL
  sibling and validator slice next.

## Steps / Checklist
- [ ] Re-open ACL design artifact and current ACL runtime objects.
- [ ] Create patch docs for the command-config slice.
- [ ] Add `FrameACLCommandConfiguration`.
- [ ] Extend `FrameACLConfiguration` to carry the new sibling.
- [ ] Extend the builder and validator for the new type.
- [ ] Update interfaces and any affected compile metadata paths.
- [ ] Add/update focused tests.
- [ ] Record findings, implementation, and validation in `## Notes`.

## Deliverables
- typed `FrameACLCommandConfiguration`
- extended frame ACL bundle
- validator support for command config
- focused tests

## Files / Paths Impacted
- src/melder/aether/nexus/acl/frame_acl_command_configuration.py
- src/melder/aether/nexus/acl/frame_acl_configuration.py
- src/melder/aether/nexus/acl/frame_acl_validator.py
- src/melder/aether/nexus/acl/frame_acl_builder.py
- src/melder/aether/nexus/acl/frame_acl_compiler.py
- src/melder/utilities/interfaces/interfaces.py
- tests/unit/melder/aether/
- codex/context_compass/attention_board.md
- codex/context_compass/artifact_board.md

## Validation
- Not run.
- Recommended commands:
  - `python -m pytest -q tests/unit/melder/aether/test_frame_acl_container.py tests/unit/melder/aether/test_frame_acl_manager.py tests/unit/melder/aether/test_nexus.py`

## Risks / Rollback Notes
- Risk: command configuration starts behaving like codegen policy instead of a
  separate permit layer.
  Rollback: keep the first cut focused on a distinct typed config object and a
  separate validator pass only.

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
  - system_docs/patches/active/frame_acl_command_configuration/architecture_patch.md
  - system_docs/patches/active/frame_acl_command_configuration/component_patch_frame_acl_command_configuration.md
  - system_docs/patches/active/frame_acl_command_configuration/component_patch_frame_acl_configuration.md
  - system_docs/patches/active/frame_acl_command_configuration/component_patch_frame_acl_validator.md
  - system_docs/patches/active/frame_acl_command_configuration/component_patch_frame_acl_builder.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: keep until the command-config slice is merged into
  canonical ACL docs or intentionally retired.

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-11T11:18:01Z
  TYPE: MEASURE
  CLAIM: The touched ACL docstrings are now materially stronger. The weakest
    new/changed public surfaces in the command-config slice were upgraded from
    thin rank-2/3 descriptions to contract-first docstrings that now state
    bundle semantics, lifecycle behavior, command-policy separation, and the
    validator/builder obligations around the new command child.
  EVIDENCE:
  - src/melder/aether/nexus/acl/frame_acl_command_configuration.py:11-334
  - src/melder/aether/nexus/acl/frame_acl_configuration.py:49-485
  - src/melder/aether/nexus/acl/frame_acl_validator.py:18-631
  - src/melder/aether/nexus/acl/frame_acl_builder.py:17-219
  - src/melder/utilities/interfaces/interfaces.py:2578-2596
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_frame_acl_command_configuration.py tests/unit/melder/aether/test_frame_acl_configuration.py tests/unit/melder/aether/test_frame_acl_validator.py tests/unit/melder/aether/test_frame_acl_builder.py tests/unit/melder/aether/test_frame_acl_container.py tests/unit/melder/aether/test_frame_acl_manager.py tests/unit/melder/aether/test_nexus.py` -> 135 passed
  IMPACT: The first command-config slice now has both the runtime substrate and
    a docstring quality level that is defensible for a public-library ACL
    surface.
  NEXT: review the command-config cut and choose the next ACL/runtime slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-11T11:18:01Z
  TYPE: FACT
  CLAIM: The first command-config runtime slice is green, but the method-level
    docstrings in the touched ACL files are below the repository quality bar.
    The class docstrings are mostly acceptable, but many public methods and
    property docstrings in the new/changed ACL files sit around rank 2-3 under
    the synaptic docstring rubric because they describe purpose/returns without
    enough contract, lifecycle, or failure detail.
  EVIDENCE:
  - src/melder/aether/nexus/acl/frame_acl_command_configuration.py:11-334
  - src/melder/aether/nexus/acl/frame_acl_configuration.py:49-485
  - src/melder/aether/nexus/acl/frame_acl_validator.py:18-631
  - src/melder/aether/nexus/acl/frame_acl_builder.py:17-204
  - codex/context_compass/agent_onboarding/user_defined/synaptic_python_developer/skills/python/docstrings.md:1-72
  IMPACT: The implementation is functionally correct, but the touched public
    API docs are not yet at the expected contract-first standard for this repo.
  NEXT: harden the touched ACL docstrings before closing or building the next
    ACL/runtime slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-11T11:18:01Z
  TYPE: FACT
  CLAIM: The first typed command-config slice is now landed in source.
    `FrameACLCommandConfiguration` exists as a typed sibling, the root
    `FrameACLConfiguration` bundle now carries `view + command + codegen`,
    `FrameACLValidator` runs a separate command-config validation pass with its
    own operation-family whitelist, builder draft semantics/documentation now
    reflect the preserved command child, and the public ACL interface contract
    now exposes the command-config sibling.
  EVIDENCE:
  - src/melder/aether/nexus/acl/frame_acl_command_configuration.py:11-334
  - src/melder/aether/nexus/acl/frame_acl_configuration.py:49-485
  - src/melder/aether/nexus/acl/frame_acl_validator.py:44-631
  - src/melder/aether/nexus/acl/frame_acl_builder.py:17-147
  - src/melder/utilities/interfaces/interfaces.py:2578-2596
  IMPACT: The named per-frame ACL bundle can now represent command policy as a
    first-class typed child instead of forcing that concern into view/codegen
    discussion only.
  NEXT: run the focused ACL pytest slice and confirm the first command-config
    cut is green.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-11T11:18:01Z
  TYPE: MEASURE
  CLAIM: The focused ACL slice is green. The new command-config object and the
    bundle/validator/test updates pass together with the existing named-contract
    container/manager/Nexus tests.
  EVIDENCE:
  - tests/unit/melder/aether/test_frame_acl_command_configuration.py:10-161
  - tests/unit/melder/aether/test_frame_acl_configuration.py:24-530
  - tests/unit/melder/aether/test_frame_acl_validator.py:35-697
  - tests/unit/melder/aether/test_frame_acl_builder.py:18-324
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_frame_acl_command_configuration.py tests/unit/melder/aether/test_frame_acl_configuration.py tests/unit/melder/aether/test_frame_acl_validator.py tests/unit/melder/aether/test_frame_acl_builder.py tests/unit/melder/aether/test_frame_acl_container.py tests/unit/melder/aether/test_frame_acl_manager.py tests/unit/melder/aether/test_nexus.py` -> 135 passed
  IMPACT: The first command-config substrate cut is ready for review. The next
    decision is whether we keep the next slice on cross-config consistency
    warnings or move directly into static/capability command-policy authoring.
  NEXT: review the command-config cut and pick the next ACL/runtime slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-11T11:08:44Z
  TYPE: PLAN
  CLAIM: The first command-config cut should preserve the bundle model and stay
    narrow. `FrameACLConfiguration` remains the selected named set, and the new
    work is to add `command_configuration` as another typed child plus a
    separate validator pass.
  EVIDENCE:
  - user_instruction: "The FrameACLConfiguration is the set"
  - user_instruction: "go ahead and add the command_Config and its validator counterpart"
  - codex/context_compass/tickets/artifacts/nexus_acl_builder_and_persistence_model.md:257-299
  IMPACT: We can extend the existing ACL shell objects without redoing contract
    selection or jumping into runtime static/capability execution.
  NEXT: write the patch docs, then implement the new typed sibling in the ACL bundle.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-13T11:43:06Z
  TYPE: DECISION
  CLAIM: The first typed command-config slice is complete and can move to the
    completed lane. The later compatibility-validator task and the canonical
    ACL docs now treat the command configuration sibling as settled substrate
    rather than pending review work.
  EVIDENCE:
  - tickets/tasks/2026-04-11_add_frame_acl_set_compatibility_validator_task.md:1-145
  - codex/context_compass/system_docs/src_components.md:631-758
  IMPACT: This command-config substrate task no longer needs active review
    state.
  NEXT: none.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task implements the first typed command-configuration slice inside the
existing named frame ACL bundle model.
