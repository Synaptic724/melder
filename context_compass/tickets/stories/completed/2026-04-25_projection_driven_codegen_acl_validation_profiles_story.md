# Story: Projection-Driven Codegen ACL Validation Profiles
- Completed: 2026-04-25T19:08:31Z
- Summary: Closed after the bounded projection-driven codegen ACL validation
  lane landed and validated green, including imports, builtins, dunder,
  reflection, recursive codegen, and the `full_access` profile.

## Metadata
- Story ID: STORY-2026-04-25-projection-driven-codegen-acl-validation-profiles
- Epic: EPIC-2026-04-25-projection-driven-codegen-acl-validation-profiles
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-25T17:51:02Z
- Updated: 2026-04-25T19:08:31Z

## User Narrative
As an engineer, I want `CodegenSystem` validation to consume the selected
codegen ACL projection directly, so that imports, builtins, dunder/reflection
rules, and the namespace contract follow the actual profile selected for the
frame.

## Value / MRP Alignment
This keeps codegen useful for real work while making validation honest and
projection-driven.

## Ticket Contract
- ENTRY_GATE: the user approved implementation and the focused codegen ACL lane
  has one active epic plus patch docs.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/nexus/acl/configurations/profiles/codegen/`
  - `src/melder/aether/nexus/acl/frame_acl_compiled_access_surface.py`
  - `src/melder/aether/nexus/acl/frame_acl_compiler.py`
  - `src/melder/aether/nexus/acl/validator/frame_acl_validator.py`
  - `src/melder/aether/nexus/rift/codegen_system/validation/`
  - `src/melder/aether/nexus/rift/codegen_system/namespace/`
  - `tests/unit/melder/aether/test_nexus.py`
- DEPENDENCIES:
  - `tickets/tasks/2026-04-25_implement_projection_driven_codegen_acl_validation_profiles_task.md`
  - patch docs under `system_docs/patches/active/codegen_acl_validation_profiles/`
- EXIT_GATE: the selected task is landed and validated.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the runtime needs a wider ACL
  subsystem redesign.

## Tasks (Implementation Checklist)
- [ ] Task: TASK-2026-04-25-implement-projection-driven-codegen-acl-validation-profiles
- [ ] Enforce Ticket Microcycle during implementation.

## Acceptance Criteria
- Codegen validation no longer returns `not_implemented` for a clean accepted
  script.
- Imports/builtins/dunder/reflection posture is profile-driven.
- Namespace contract is updated to the agreed room-tool shape.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/codegen_acl_validation_profiles/architecture_patch.md
  - system_docs/patches/active/codegen_acl_validation_profiles/component_patch_codegen_acl_profiles.md
  - system_docs/patches/active/codegen_acl_validation_profiles/component_patch_codegen_validator_and_compiler.md
  - system_docs/patches/active/codegen_acl_validation_profiles/code_description_patch_codegen_acl_validation_flow.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: merge into canonical docs or explicitly supersede

## Notes
- DATETIME: 2026-04-25T17:51:02Z
  TYPE: PLAN
  CLAIM: The implementation lane is bounded: extend the codegen ACL rule model
    for imports/builtins/meta behavior, compile those answers into the existing
    compiled access surface, refactor the validator to consume the selected
    projection, and update the namespace contract to the agreed room-tool set.
  EVIDENCE:
  - src/melder/aether/nexus/rift/codegen_system/validation/codegen_validator.py:33-110
  - src/melder/aether/nexus/acl/validator/frame_acl_validator.py:117-140
  - src/melder/aether/nexus/acl/frame_acl_compiler.py:113-140
  - src/melder/aether/nexus/rift/codegen_system/namespace/codegen_namespace_configuration.py:12-85
  IMPACT: The story can be implemented without a broader ACL redesign.
  NEXT: execute the task with patch-gated edits and focused tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-25T18:11:15Z
  TYPE: FACT
  CLAIM: The selected task is now landed and green. The story's contract is
    materially satisfied: projection-driven imports/builtins/meta validation is
    real, the namespace contract is updated, and permissive codegen is broad
    enough to execute import/eval style work in the focused unit ring.
  EVIDENCE:
  - tickets/tasks/2026-04-25_implement_projection_driven_codegen_acl_validation_profiles_task.md:90-141
  - tests/unit/melder/aether/test_nexus.py:2676-2764
  - tests/unit/melder/aether/test_frame_acl_codegen_validation_profiles.py:57-164
  IMPACT: This story is in review state rather than active implementation.
  NEXT: return the landed slice to the user and decide whether to close this
    story or keep it open for another refinement pass.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-25T18:11:15Z
  TYPE: FACT
  CLAIM: The follow-on refinement is also landed: reflection posture is now
    validated explicitly, and `precision` now has a narrower import contract
    than `hybrid`.
  EVIDENCE:
  - tickets/tasks/2026-04-25_implement_projection_driven_codegen_acl_validation_profiles_task.md:142-163
  - tests/unit/melder/aether/test_nexus.py:2704-2782
  - tests/unit/melder/aether/test_frame_acl_codegen_validation_profiles.py:108-131
  IMPACT: The story is now a fuller review slice rather than just the initial
    projection-wiring pass.
  NEXT: return the story for review and closure direction.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-25T18:11:15Z
  TYPE: FACT
  CLAIM: Recursive codegen posture is now part of the same landed story. The
    `codegen` namespace object is a wrapper surface with projection-driven
    recursive permission, and permissive codegen now allows recursive execution
    while safe/hybrid/precision deny it.
  EVIDENCE:
  - tickets/tasks/2026-04-25_implement_projection_driven_codegen_acl_validation_profiles_task.md:164-185
  - tests/unit/melder/aether/test_nexus.py:2768-2848
  IMPACT: This story now covers imports, builtins, dunder, reflection,
    namespace shape, and recursive codegen posture as one coherent slice.
  NEXT: return the story for review and closure direction.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-25T18:11:15Z
  TYPE: FACT
  CLAIM: The story also now owns the deeper meta-policy pass and the new
    `full_access` profile. Reflection denial is no longer limited to obvious
    direct module helpers, and the codegen profile ladder now differentiates
    `permissive` from an unconstrained top-end posture.
  EVIDENCE:
  - tickets/tasks/2026-04-25_implement_projection_driven_codegen_acl_validation_profiles_task.md:186-207
  - tests/unit/melder/aether/test_nexus.py:2728-2802
  IMPACT: This story now covers imports, builtins, dunder, reflection,
    recursive codegen, and the `full_access` top-end profile as one coherent
    implementation slice.
  NEXT: return the story for review and closure direction.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This story owns the bounded codegen ACL validation implementation lane.
