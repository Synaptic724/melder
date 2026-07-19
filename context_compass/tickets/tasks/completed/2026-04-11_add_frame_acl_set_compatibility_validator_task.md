# Task: Add Frame ACL Set Compatibility Validator
- Completed: 2026-04-13T11:43:06Z
- Summary: Closed the ACL bundle compatibility-validator slice after the later ACL work treated it as settled substrate.

## Metadata
- Task ID: TASK-2026-04-11-add-frame-acl-set-compatibility-validator
- Story: STORY-2026-04-11-extend-frame-acl-bundle-with-command-configuration
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-11T11:54:27Z
- Updated: 2026-04-13T11:43:06Z

## Objective
Add a second frame-local validator that checks full ACL bundle compatibility
across `view_configuration`, `command_configuration`, and `codegen_configuration`
and records warnings/errors for suspicious or invalid combinations.

## Ticket Contract
- ENTRY_GATE: the first typed command-config slice is landed and green, and
  the user explicitly approved adding a second compatibility validator inside
  the existing ACL container model.
- EXECUTION_BOUNDARY: compatibility report/validator, container wiring,
  focused tests, and ticket/patch sync only.
- DEPENDENCIES:
  - tickets/stories/2026-04-11_extend_frame_acl_bundle_with_command_configuration_story.md
  - tickets/tasks/2026-04-11_add_frame_acl_command_configuration_and_validation_task.md
  - system_docs/patches/active/frame_acl_set_compatibility_validator/architecture_patch.md
  - system_docs/patches/active/frame_acl_set_compatibility_validator/component_patch_frame_acl_set_compatibility_validator.md
  - system_docs/patches/active/frame_acl_set_compatibility_validator/component_patch_frame_acl_container.md
  - src/melder/aether/nexus/acl/frame_acl_container.py
  - src/melder/aether/nexus/acl/frame_acl_validator.py
  - src/melder/aether/nexus/acl/frame_acl_command_configuration.py
  - tests/unit/melder/aether/
- EXIT_GATE: the frame ACL container owns a compatibility validator, the
  compatibility report captures warnings/errors for bundle mismatches, and the
  focused pytest slice is green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if compatibility checks require
  target-aware command entries first instead of bundle-level checks.

## Scope Boundaries
- In scope:
  - compatibility report object
  - set compatibility validator
  - container ownership/wiring
  - first warning/error rules over the current generic child configs
  - focused unit tests
- Out of scope:
  - target-aware command selectors
  - static/capability runtime execution
  - frontend actionable projection
  - descriptor-level command-member existence checks

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly approved adding a second validator to
  scan the full ACL bundle for compatibility warnings/errors.

## Steps / Checklist
- [ ] Re-open current command-config bundle state and define first-cut
      compatibility rules.
- [ ] Create patch docs for the compatibility-validator slice.
- [ ] Add compatibility report + validator.
- [ ] Wire the validator into `FrameACLContainer`.
- [ ] Add/update focused tests.
- [ ] Record findings, implementation, and validation in `## Notes`.

## Deliverables
- `FrameACLSetCompatibilityValidator`
- compatibility report object
- frame ACL container wiring
- focused tests

## Files / Paths Impacted
- src/melder/aether/nexus/acl/frame_acl_set_compatibility_validator.py
- src/melder/aether/nexus/acl/frame_acl_set_compatibility_report.py
- src/melder/aether/nexus/acl/frame_acl_container.py
- src/melder/utilities/interfaces/interfaces.py
- tests/unit/melder/aether/
- codex/context_compass/attention_board.md
- codex/context_compass/artifact_board.md

## Validation
- Not run.
- Recommended commands:
  - `python -m pytest -q tests/unit/melder/aether/test_frame_acl_set_compatibility_validator.py tests/unit/melder/aether/test_frame_acl_container.py tests/unit/melder/aether/test_frame_acl_manager.py tests/unit/melder/aether/test_nexus.py`

## Risks / Rollback Notes
- Risk: compatibility rules collapse intentional read-only visibility into hard
  failures.
  Rollback: keep those cases as warnings only and reserve hard failures for
  structurally contradictory combinations.

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
  - system_docs/patches/active/frame_acl_set_compatibility_validator/architecture_patch.md
  - system_docs/patches/active/frame_acl_set_compatibility_validator/component_patch_frame_acl_set_compatibility_validator.md
  - system_docs/patches/active/frame_acl_set_compatibility_validator/component_patch_frame_acl_container.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: keep until compatibility validation is merged into canonical
  ACL docs or intentionally retired.

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-11T12:00:46Z
  TYPE: FACT
  CLAIM: The second ACL validator slice is now landed in source. The runtime
    has a detached `FrameACLSetCompatibilityReport`, a
    `FrameACLSetCompatibilityValidator` that resolves effective profile
    semantics through the shared ACL profile builder, container ownership for
    the new validator, and manager wiring that injects the shared profile
    builder into each container so compatibility warnings reflect real bundled
    policy instead of override-only guesses.
  EVIDENCE:
  - src/melder/aether/nexus/acl/frame_acl_set_compatibility_report.py:8-8
  - src/melder/aether/nexus/acl/frame_acl_set_compatibility_validator.py:26-26
  - src/melder/aether/nexus/acl/frame_acl_set_compatibility_validator.py:127-127
  - src/melder/aether/nexus/acl/frame_acl_set_compatibility_validator.py:294-294
  - src/melder/aether/nexus/acl/frame_acl_container.py:118-118
  - src/melder/aether/nexus/acl/frame_acl_container.py:269-284
  - src/melder/aether/nexus/acl/frame_acl_container.py:340-341
  - src/melder/aether/nexus/acl/frame_acl_container.py:482-483
  - src/melder/aether/nexus/frame_acl_manager.py:236-236
  - src/melder/utilities/interfaces/interfaces.py:2594-2642
  IMPACT: The frame-local ACL subsystem can now validate typed child configs
    and full bundle compatibility separately, which is the right foundation
    for later static/capability command authoring.
  NEXT: run the focused compatibility-validator pytest slice and confirm the
    container/manager integration stays green.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-11T12:00:46Z
  TYPE: MEASURE
  CLAIM: The focused compatibility-validator slice is green. The new report
    object, direct compatibility-validator warnings/errors, container wiring,
    and manager/Nexus integration all pass together with the existing command
    config and bundle tests.
  EVIDENCE:
  - tests/unit/melder/aether/test_frame_acl_set_compatibility_validator.py:26-191
  - tests/unit/melder/aether/test_frame_acl_container.py:11-327
  - tests/unit/melder/aether/test_frame_acl_manager.py:1-292
  - tests/unit/melder/aether/test_nexus.py:1-1462
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_frame_acl_set_compatibility_validator.py tests/unit/melder/aether/test_frame_acl_container.py tests/unit/melder/aether/test_frame_acl_manager.py tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_frame_acl_command_configuration.py tests/unit/melder/aether/test_frame_acl_configuration.py tests/unit/melder/aether/test_frame_acl_validator.py tests/unit/melder/aether/test_frame_acl_builder.py` -> 141 passed
  IMPACT: The second validator is ready for review. The next clean move is to
    make command configuration target-aware and then build the static/capability
    command authoring surface on top of both validators.
  NEXT: review the compatibility-validator cut and choose the next ACL/runtime
    slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-11T11:54:27Z
  TYPE: PLAN
  CLAIM: The next clean ACL slice is a second validator that scans the full
    selected bundle for compatibility. The current child validator stays
    responsible for per-type schema/ruleset checks, and the new validator owns
    cross-set warnings/errors.
  EVIDENCE:
  - user_instruction: "use SetCompatibilityValidator"
  - user_instruction: "build that into the system and set it up just like the other validator"
  - user_instruction: "we should build a broader validation system that checks all 3 in the set"
  IMPACT: We can extend the container model cleanly without changing named
    bundle selection or mixing child validation with compatibility logic.
  NEXT: write patch docs and implement the report/validator plus container wiring.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-13T11:43:06Z
  TYPE: DECISION
  CLAIM: The compatibility-validator slice is complete and can move to the
    completed lane. Later ACL work now builds on the bundle-level report and
    validator rather than treating them as pending review substrate.
  EVIDENCE:
  - tickets/tasks/completed/2026-04-11_add_frame_acl_command_configuration_and_validation_task.md:1-177
  - codex/context_compass/system_docs/src_components.md:631-758
  IMPACT: This validator task no longer needs active review state.
  NEXT: none.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task adds the second validator for full ACL bundle compatibility inside
the existing frame-local container model.
