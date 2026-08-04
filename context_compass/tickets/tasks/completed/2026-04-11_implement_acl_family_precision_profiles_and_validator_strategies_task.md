# Task: Implement ACL Family Precision Profiles And Validator Strategies
- Completed: 2026-04-13T11:51:25Z
- Summary: Closed the family-profile precision tranche after the later selector/runtime ACL slices built on it as settled substrate.

## Metadata
- Task ID: TASK-2026-04-11-implement-acl-family-precision-profiles-and-validator-strategies
- Story: STORY-2026-04-11-precision-acl-target-model-and-descriptor-validation
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-12T00:13:32Z
- Updated: 2026-04-13T11:51:25Z

## Objective
Implement the next ACL tranche by adding command profiles, category-local
`precision.py` profile assets for view/command/codegen, and validator-owned
profile strategies so profile semantics are no longer hardcoded inside the ACL
validators.

## Ticket Contract
- ENTRY_GATE: the separate-family ACL chain migration is landed and green, the
  precision ACL investigation lane is documented, and the user explicitly
  approved moving from design into the profile/strategy implementation tranche.
- EXECUTION_BOUNDARY: ACL profile/configuration/builder/validator/compiler
  surfaces, focused tests, patch docs, and ticket/board/artifact sync only.
- DEPENDENCIES:
  - tickets/epics/2026-04-11_precision_acl_targets_and_spell_access_epic.md
  - tickets/stories/2026-04-11_precision_acl_target_model_and_descriptor_validation_story.md
  - tickets/tasks/2026-04-11_investigate_precision_acl_implementation_and_descriptor_validation_task.md
  - tickets/tasks/2026-04-11_refactor_frame_acl_container_to_separate_family_chains_task.md
  - src/melder/aether/nexus/acl/
- EXIT_GATE: command profiles exist, view/command/codegen configs carry base +
  precision profile identity, validator-owned profile strategies are live, the
  compiler consumes base + precision + overrides, and the focused ACL/Nexus
  slice is green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if descriptor-backed precision
  semantics force a broader ACL-schema redesign than this tranche should own.

## Scope Boundaries
- In scope:
  - command base profile family
  - `precision.py` assets for view/command/codegen
  - shared family-config precision-profile identity fields
  - validator-owned profile strategy registry
  - compatibility/compiler merge updates for base + precision + overrides
  - focused ACL/Nexus tests
- Out of scope:
  - new top-level ACL config families
  - upper-layer validator redesign beyond profile-strategy pairing
  - room-mode/runtime ACL enforcement

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user approved implementing the profile-based precision
  model and the paired validator-strategy system.

## Steps / Checklist
- [ ] Stage patch docs and route the new task from the board.
- [ ] Add command base profile support under the new ACL profile tree.
- [ ] Add family-local `precision.py` assets for view/command/codegen.
- [ ] Extend family configs with precision-profile identity fields.
- [ ] Extend the profile builder for command + precision profile registration.
- [ ] Add validator-owned profile strategies and move hardcoded profile checks into them.
- [ ] Extend compatibility/compiler merge order to base + precision + overrides.
- [ ] Add/update focused ACL/Nexus tests.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- command profile family
- `precision.py` profile assets for all three ACL families
- validator profile strategy registry and family strategies
- updated ACL config/builder/compiler flow
- focused tests

## Files / Paths Impacted
- src/melder/aether/nexus/acl/configurations/
- src/melder/aether/nexus/acl/configurations/profiles/
- src/melder/aether/nexus/acl/builder/frame_acl_builder.py
- src/melder/aether/nexus/acl/validator/
- src/melder/aether/nexus/acl/frame_acl_compiler.py
- tests/unit/melder/aether/
- tests/component/melder/aether/
- codex/context_compass/attention_board.md
- codex/context_compass/artifact_board.md

## Validation
- Not run.
- Recommended commands:
  - `python -m pytest -q tests/unit/melder/aether/test_frame_acl_builder.py tests/unit/melder/aether/test_frame_acl_validator.py tests/unit/melder/aether/test_frame_acl_profile.py tests/unit/melder/aether/test_frame_acl_profile_contract_matrix.py tests/unit/melder/aether/test_nexus_frame_acl_profiles.py tests/component/melder/aether/test_frame_acl_compiler_component.py`

## Risks / Rollback Notes
- Risk: profile semantics remain partly hardcoded in validators and we end up
  with a split brain between profile assets and validation behavior.
  Rollback: keep validation strategies profile-keyed and move all profile-name
  special cases out of the validator body in the same tranche.

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
  - system_docs/patches/active/frame_acl_family_precision_profiles/architecture_patch.md
  - system_docs/patches/active/frame_acl_family_precision_profiles/component_patch_acl_profiles.md
  - system_docs/patches/active/frame_acl_family_precision_profiles/component_patch_frame_acl_validator.md
  - system_docs/patches/active/frame_acl_family_precision_profiles/component_patch_frame_acl_compiler.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: keep until the family-profile precision model is merged into
  canonical ACL docs or intentionally retired.

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-12T00:13:32Z
  TYPE: PLAN
  CLAIM: The next precision ACL tranche should not add a fourth selected config
    family. The separate-family chain model is already the right storage layer.
    The cleaner implementation is:
    1) add the missing command base-profile family
    2) add `precision.py` profile assets for view/command/codegen
    3) keep validation behavior in validator-owned profile strategies
    4) extend configs/merge logic to `base + precision + overrides`
  EVIDENCE:
  - src/melder/aether/nexus/acl/configurations/frame_acl_view_configuration.py:1-466
  - src/melder/aether/nexus/acl/configurations/frame_acl_command_configuration.py:1-422
  - src/melder/aether/nexus/acl/configurations/frame_acl_codegen_configuration.py:1-417
  - src/melder/aether/nexus/acl/configurations/profiles/builder/frame_acl_profile_builder.py:1-319
  - src/melder/aether/nexus/acl/validator/frame_acl_validator.py:1-780
  - src/melder/aether/nexus/acl/validator/compatibility/frame_acl_set_compatibility_validator.py:1-380
  IMPACT: The implementation can stay aligned with the landed separate-family
    chain model and the new ACL tree layout instead of reintroducing another
    top-level selection axis.
  NEXT: add the patch docs and sync board/artifact routing to this task before
    code changes begin.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-12T00:43:23Z
  TYPE: FACT
  CLAIM: The core family-profile tranche is now landed on the focused ACL
    surface. The ACL tree now has:
    - a real command base-profile family
    - `precision.py` assets for view/command/codegen
    - family configs carrying precision-profile identity
    - profile-builder registries for command and precision profiles
    - validator-owned profile strategy registration
    - compiler/compatibility merge logic moving toward `base + precision + overrides`
  EVIDENCE:
  - src/melder/aether/nexus/acl/configurations/profiles/command/frame_acl_command_profile.py:15-15
  - src/melder/aether/nexus/acl/configurations/profiles/builder/frame_acl_profile_builder.py:60-60
  - src/melder/aether/nexus/acl/configurations/frame_acl_view_configuration.py:48-48
  - src/melder/aether/nexus/acl/configurations/frame_acl_command_configuration.py:42-42
  - src/melder/aether/nexus/acl/configurations/frame_acl_codegen_configuration.py:42-42
  - src/melder/aether/nexus/acl/validator/frame_acl_validator.py:55-55
  - src/melder/aether/nexus/acl/validator/compatibility/frame_acl_set_compatibility_validator.py:199-199
  - src/melder/aether/nexus/acl/frame_acl_compiler.py:73-73
  IMPACT: The implementation is no longer design-only. The remaining work is
    widening and stabilizing the public/test surface around the new model.
  NEXT: patch the stale broader expectations and rerun the widened ACL/Nexus
    validation slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-12T00:43:23Z
  TYPE: MEASURE
  CLAIM: The focused profile/validator/compiler ring is green, and the wider
    ACL/Nexus ring is almost green. The focused slice now passes cleanly, and
    the broader unit/component ring is down to three stale expectations that
    still assume command defaults are named `default` instead of the newly
    landed `safe` command profile baseline.
  EVIDENCE:
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_frame_acl_builder.py tests/unit/melder/aether/test_frame_acl_profile.py tests/unit/melder/aether/test_frame_acl_validator.py tests/unit/melder/aether/test_nexus_frame_acl_profiles.py tests/component/melder/aether/test_frame_acl_compiler_component.py` -> 65 passed
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_frame_acl_container.py tests/unit/melder/aether/test_frame_acl_manager.py tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_frame_acl_profile_contract_matrix.py tests/unit/melder/aether/test_frame_acl_command_configuration.py tests/unit/melder/aether/test_frame_acl_configuration.py tests/unit/melder/aether/test_frame_acl_builder.py tests/unit/melder/aether/test_frame_acl_profile.py tests/unit/melder/aether/test_frame_acl_validator.py tests/unit/melder/aether/test_nexus_frame_acl_profiles.py tests/component/melder/aether/test_frame_acl_compiler_component.py` -> 3 failed, 201 passed
  IMPACT: The next step is a narrow test-surface repair, not another design or
    subsystem rewrite.
  NEXT: update the three stale `default` -> `safe` command-profile assertions
    and rerun the widened ring.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-12T00:45:41Z
  TYPE: FACT
  CLAIM: The family-profile precision tranche is now landed in source. The ACL
    subsystem now has:
    - a real command base-profile family
    - `precision.py` assets for view/command/codegen
    - precision profile identity fields on the family configs
    - profile-builder registries for command and precision assets
    - validator-owned family strategy registration
    - compatibility/compiler merge paths using `base + precision + overrides`
    The validator still owns validation behavior, but it now does so through a
    strategy registry instead of hardcoded profile-name branching as the main
    extension mechanism.
  EVIDENCE:
  - src/melder/aether/nexus/acl/configurations/profiles/command/frame_acl_command_profile.py:15-15
  - src/melder/aether/nexus/acl/configurations/profiles/builder/frame_acl_profile_builder.py:60-60
  - src/melder/aether/nexus/acl/configurations/frame_acl_view_configuration.py:48-48
  - src/melder/aether/nexus/acl/configurations/frame_acl_command_configuration.py:42-42
  - src/melder/aether/nexus/acl/configurations/frame_acl_codegen_configuration.py:42-42
  - src/melder/aether/nexus/acl/validator/frame_acl_validator.py:55-55
  - src/melder/aether/nexus/acl/validator/compatibility/frame_acl_set_compatibility_validator.py:199-199
  - src/melder/aether/nexus/acl/frame_acl_compiler.py:73-73
  IMPACT: The precision lane now has a reusable profile/strategy substrate to
    build descriptor-backed selector/member semantics on top of without adding
    another top-level ACL config family.
  NEXT: review the landed family-profile precision model and then decide
    whether the next slice is richer descriptor/member precision semantics or
    more public profile-management surface.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-12T00:45:41Z
  TYPE: MEASURE
  CLAIM: The widened ACL/Nexus validation ring is green after the family-profile
    precision refactor and the small expectation updates around the new `safe`
    command baseline plus precision-aware view payload floors.
  EVIDENCE:
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_frame_acl_container.py tests/unit/melder/aether/test_frame_acl_manager.py tests/unit/melder/aether/test_nexus.py tests/unit/melder/aether/test_frame_acl_profile_contract_matrix.py tests/unit/melder/aether/test_frame_acl_command_configuration.py tests/unit/melder/aether/test_frame_acl_configuration.py tests/unit/melder/aether/test_frame_acl_builder.py tests/unit/melder/aether/test_frame_acl_profile.py tests/unit/melder/aether/test_frame_acl_validator.py tests/unit/melder/aether/test_nexus_frame_acl_profiles.py tests/component/melder/aether/test_frame_acl_compiler_component.py tests/component/melder/aether/test_frame_acl_chain_component_matrix.py tests/integration/melder/aether/test_frame_acl_chain_integration.py tests/integration/melder/aether/test_frame_acl_compiler_integration.py` -> 230 passed
  IMPACT: This tranche is ready for review instead of more migration cleanup.
  NEXT: present the landed model and validation result to the user and wait for
    direction on the next precision/validator layer.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-13T11:51:25Z
  TYPE: DECISION
  CLAIM: The family-profile precision tranche is complete and can move to the
    completed lane. The selector-resolution, `spell_index_id` runtime lookup,
    and command ACL enforcement tasks all depend on this profile/strategy layer
    as settled precision substrate.
  EVIDENCE:
  - tickets/tasks/2026-04-12_implement_spell_selector_resolution_and_spell_index_acl_compilation_task.md:1-145
  - tickets/tasks/2026-04-12_add_spell_index_runtime_lookup_to_spellbook_and_conduit_task.md:1-131
  - tickets/tasks/2026-04-12_implement_command_acl_access_enforcement_in_command_system_task.md:1-146
  IMPACT: This tranche no longer belongs on the active board.
  NEXT: none.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task implements the profile-based precision ACL model over the landed
separate-family chain substrate.
