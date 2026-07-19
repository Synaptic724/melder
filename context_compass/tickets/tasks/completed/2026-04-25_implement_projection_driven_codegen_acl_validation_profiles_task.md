# Task: Implement Projection-Driven Codegen ACL Validation Profiles
- Completed: 2026-04-25T19:08:31Z
- Summary: Closed after the projection-driven codegen ACL slice landed with
  import, builtin, dunder, reflection, recursive-codegen, and `full_access`
  profile support, all green on the focused runtime and ACL/profile rings.

## Metadata
- Task ID: TASK-2026-04-25-implement-projection-driven-codegen-acl-validation-profiles
- Story: STORY-2026-04-25-projection-driven-codegen-acl-validation-profiles
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-25T17:51:02Z
- Updated: 2026-04-25T19:08:31Z

## Objective
Implement projection-driven codegen validation so imports, dangerous builtins,
dunder/reflection behavior, and the codegen namespace contract come from the
selected codegen ACL profile instead of the current hardcoded validator.

## Ticket Contract
- ENTRY_GATE: the user explicitly approved implementation of the codegen ACL
  validation slice, and the required patch docs exist for this runtime change.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/nexus/acl/configurations/profiles/codegen/`
  - `src/melder/aether/nexus/acl/frame_acl_compiled_access_surface.py`
  - `src/melder/aether/nexus/acl/frame_acl_compiler.py`
  - `src/melder/aether/nexus/acl/validator/frame_acl_validator.py`
  - `src/melder/aether/nexus/rift/codegen_system/validation/`
  - `src/melder/aether/nexus/rift/codegen_system/namespace/`
  - `src/melder/aether/nexus/rift/codegen_system/codegen_system.py`
  - `tests/unit/melder/aether/test_nexus.py`
  - directly affected ACL profile/compiler tests under `tests/unit/melder/aether/`
- DEPENDENCIES:
  - `system_docs/patches/active/codegen_acl_validation_profiles/architecture_patch.md`
  - `system_docs/patches/active/codegen_acl_validation_profiles/component_patch_codegen_acl_profiles.md`
  - `system_docs/patches/active/codegen_acl_validation_profiles/component_patch_codegen_validator_and_compiler.md`
  - `system_docs/patches/active/codegen_acl_validation_profiles/code_description_patch_codegen_acl_validation_flow.md`
- EXIT_GATE: valid code is accepted under the selected codegen profile,
  projection-driven import/builtin/meta behavior is enforced, namespace
  exposure matches the agreed room-tool shape, and the focused unit ring is
  green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the selected projection model
  proves insufficient and would force a second policy authority.

## Scope Boundaries
- In scope:
  - codegen profile rule additions for imports/builtins/meta posture
  - compiled access surface extensions
  - validator strategy refactor
  - namespace contract update
  - focused tests
- Out of scope:
  - raw `viewer` / `command` ACL redesign
  - sandboxing / sentinel work
  - broader room-surface redesign

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly wants this implemented now.

## Steps / Checklist
- [ ] Extend codegen profile definitions with import/builtin/meta rule coverage.
- [ ] Extend the codegen ACL validator and compiler to accept and compile those rules.
- [ ] Extend the compiled access surface with validator-facing codegen answers.
- [ ] Refactor codegen validation strategies to consume the selected projection.
- [ ] Update the namespace contract to `viewer`, `command`, `workstation`, `codegen`.
- [ ] Add focused unit coverage for safe/hybrid/permissive/precision behavior.
- [ ] Run focused validation and record results in `## Notes`.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- projection-driven codegen validation
- extended codegen ACL profile/compiler surface
- updated codegen namespace contract
- focused validation results

## Files / Paths Impacted
- codex/context_compass/tickets/tasks/2026-04-25_implement_projection_driven_codegen_acl_validation_profiles_task.md
- codex/context_compass/attention_board.md
- codex/context_compass/artifact_board.md
- src/melder/aether/nexus/acl/configurations/profiles/codegen/
- src/melder/aether/nexus/acl/frame_acl_compiled_access_surface.py
- src/melder/aether/nexus/acl/frame_acl_compiler.py
- src/melder/aether/nexus/acl/validator/frame_acl_validator.py
- src/melder/aether/nexus/rift/codegen_system/validation/
- src/melder/aether/nexus/rift/codegen_system/namespace/
- src/melder/aether/nexus/rift/codegen_system/codegen_system.py
- tests/unit/melder/aether/

## Validation
- Not run.
- Recommended commands:
  - `python -m pytest -q tests/unit/melder/aether/test_nexus.py -k "codegen"`
  - `python -m pytest -q tests/unit/melder/aether/test_frame_acl_codegen_* tests/unit/melder/aether/test_frame_acl_compiler_contracts.py tests/unit/melder/aether/test_frame_acl_validator.py`

## Risks / Rollback Notes
- Risk: validator changes drift into a second policy authority.
  Rollback: keep all validator-facing answers compiled from the selected
  projection and reject any shadow policy model.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - system_docs/patches/active/codegen_acl_validation_profiles/architecture_patch.md
  - system_docs/patches/active/codegen_acl_validation_profiles/component_patch_codegen_acl_profiles.md
  - system_docs/patches/active/codegen_acl_validation_profiles/component_patch_codegen_validator_and_compiler.md
  - system_docs/patches/active/codegen_acl_validation_profiles/code_description_patch_codegen_acl_validation_flow.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: merge into canonical docs or explicitly supersede

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and the next single
  implementation or validation step.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-25T17:51:02Z
  TYPE: FACT
  CLAIM: The current validator and namespace contract are the real blockers.
    `CodegenValidator` still hardcodes strategy behavior and returns
    `codegen_validation_not_implemented` on a clean script, while
    `CodegenNamespaceConfiguration` still exposes the old
    `rift/space/viewer/workstation/command/target/frame_name` contract instead
    of the later agreed room-tool shape.
  EVIDENCE:
  - src/melder/aether/nexus/rift/codegen_system/validation/codegen_validator.py:43-48
  - src/melder/aether/nexus/rift/codegen_system/codegen_system.py:299-318
  - src/melder/aether/nexus/rift/codegen_system/namespace/codegen_namespace_configuration.py:12-85
  - tests/unit/melder/aether/test_nexus.py:2084-2102
  - tests/unit/melder/aether/test_nexus.py:2305-2339
  IMPACT: The implementation has to touch validator acceptance and namespace
    composition together instead of treating them as separate cleanup items.
  NEXT: extend the codegen ACL/compiler surface so the validator can read
    import/builtin/meta answers from the selected projection.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-25T17:51:02Z
  TYPE: FACT
  CLAIM: The existing ACL stack is already close to what we need. Codegen
    profiles already separate frame, conduit, spell, and capability rulesets,
    the frame ACL validator already enforces per-family allowed operations, and
    the compiler already collapses codegen operations into
    `CompiledFrameACLAccessSurface.allowed_commands`.
  EVIDENCE:
  - src/melder/aether/nexus/acl/configurations/profiles/codegen/safe_profile.py:9-60
  - src/melder/aether/nexus/acl/configurations/profiles/codegen/permissive_profile.py:9-60
  - src/melder/aether/nexus/acl/validator/frame_acl_validator.py:117-140
  - src/melder/aether/nexus/acl/validator/frame_acl_validator.py:1077-1110
  - src/melder/aether/nexus/acl/frame_acl_compiler.py:458-473
  IMPACT: We can extend the existing rule/compiler model instead of inventing a
    second execution-policy object.
  NEXT: implement import/builtin/meta rule compilation and wire the validator to
    read the selected projection directly.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-25T18:11:15Z
  TYPE: FACT
  CLAIM: The runtime slice is now landed. Codegen profiles now carry
    import/builtin/meta rules through the existing ruleset model, the compiled
    access surface now carries validator-facing codegen answers, the validator
    now accepts clean scripts instead of returning `not_implemented`, and the
    namespace contract now exposes `viewer`, `command`, `workstation`, and
    `codegen` plus a builtins map derived from the selected projection.
  EVIDENCE:
  - src/melder/aether/nexus/acl/configurations/profiles/codegen/hybrid_profile.py:61-96
  - src/melder/aether/nexus/acl/configurations/profiles/codegen/permissive_profile.py:52-67
  - src/melder/aether/nexus/acl/frame_acl_compiler.py:186-249
  - src/melder/aether/nexus/acl/frame_acl_compiled_access_surface.py:34-39
  - src/melder/aether/nexus/rift/codegen_system/codegen_system.py:397-441
  - src/melder/aether/nexus/rift/codegen_system/namespace/codegen_namespace_configuration.py:25-35
  - src/melder/aether/nexus/rift/codegen_system/namespace/codegen_namespace_builder.py:10-23
  - src/melder/aether/nexus/rift/codegen_system/validation/codegen_validator.py:168-178
  IMPACT: Codegen validation is now projection-driven in substance rather than
    structurally present but behaviorally stubbed.
  NEXT: return the landed slice for review and decide whether to close this
    task or keep iterating on deeper codegen ACL composition.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-25T18:11:15Z
  TYPE: MEASURE
  CLAIM: The focused codegen runtime ring and the direct ACL/compiler/profile
    ring are both green.
  EVIDENCE:
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_nexus.py -k "codegen"` -> `35 passed, 112 deselected`
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_frame_acl_codegen_safe_profile.py tests/unit/melder/aether/test_frame_acl_codegen_hybrid_profile.py tests/unit/melder/aether/test_frame_acl_codegen_permissive_profile.py tests/unit/melder/aether/test_frame_acl_codegen_validation_profiles.py tests/unit/melder/aether/test_frame_acl_compiler_contracts.py -k "codegen or permissive_codegen_profile_expands_allowed_commands"` -> `9 passed, 13 deselected`
  IMPACT: The slice is stable enough to review without another blind pass.
  NEXT: sync the routing state and return the implementation outcome to the user.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-25T18:11:15Z
  TYPE: FACT
  CLAIM: One real gap remains inside the new projection-driven slice.
    `unsafe_reflection` is now compiled into the codegen access surface, but
    there is still no dedicated validator strategy consuming it, and
    `precision` still inherits a near-hybrid import posture rather than
    exposing a meaningfully narrower import set.
  EVIDENCE:
  - src/melder/aether/nexus/rift/codegen_system/validation/strategies/codegen_attribute_access_strategy.py:21-102
  - src/melder/aether/nexus/acl/frame_acl_compiled_access_surface.py:340-359
  - src/melder/aether/nexus/acl/configurations/profiles/codegen/stdlib_import_sets.py:44-80
  IMPACT: The current slice is good enough for review, but not yet complete if
    we want the next obvious validator/profile features finished.
  NEXT: add a reflection policy strategy and narrow the `precision` import set.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-25T18:11:15Z
  TYPE: FACT
  CLAIM: The second refinement tranche is now landed. `unsafe_reflection` is
    consumed by a dedicated validator strategy, and `precision` now narrows the
    import allowlist by intersection so it is meaningfully tighter than
    `hybrid` instead of collapsing back into the broader base import set.
  EVIDENCE:
  - src/melder/aether/nexus/rift/codegen_system/validation/strategies/codegen_reflection_policy_strategy.py:1-89
  - src/melder/aether/nexus/rift/codegen_system/validation/codegen_validator.py:20-24
  - src/melder/aether/nexus/acl/configurations/profiles/codegen/stdlib_import_sets.py:44-62
  - src/melder/aether/nexus/acl/frame_acl_compiler.py:531-542
  - src/melder/aether/nexus/acl/frame_acl_compiler.py:643-676
  IMPACT: The projection-driven codegen ACL slice is now materially more complete:
    imports, builtins, dunder, and reflection all have real validator/runtime
    posture, and `precision` has a distinct import identity.
  NEXT: return the landed slice for review and decide whether to close this
    task or continue into deeper codegen ACL features.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-25T18:11:15Z
  TYPE: MEASURE
  CLAIM: The refined codegen runtime ring and the direct ACL/compiler/profile
    ring are both green after the reflection and precision follow-on.
  EVIDENCE:
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_nexus.py -k "codegen"` -> `37 passed, 112 deselected`
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_frame_acl_codegen_safe_profile.py tests/unit/melder/aether/test_frame_acl_codegen_hybrid_profile.py tests/unit/melder/aether/test_frame_acl_codegen_permissive_profile.py tests/unit/melder/aether/test_frame_acl_codegen_validation_profiles.py tests/unit/melder/aether/test_frame_acl_compiler_contracts.py -k "codegen or permissive_codegen_profile_expands_allowed_commands"` -> `10 passed, 13 deselected`
  IMPACT: The current focused slice is stable enough to review without another
    blind refinement pass.
  NEXT: sync the routing state and return the outcome to the user.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-25T18:11:15Z
  TYPE: FACT
  CLAIM: Recursive codegen posture is now explicit and enforced. The codegen
    ACL family now carries `recursive_codegen`, the compiled access surface now
    exposes that answer, and the namespace no longer exposes the raw internal
    system. It now exposes a small `codegen` wrapper that enforces recursive
    codegen permission at runtime while defaulting nested calls to the current
    frame.
  EVIDENCE:
  - src/melder/aether/nexus/acl/configurations/profiles/codegen/permissive_profile.py:52-68
  - src/melder/aether/nexus/acl/frame_acl_compiler.py:208-214
  - src/melder/aether/nexus/acl/frame_acl_compiled_access_surface.py:40-40
  - src/melder/aether/nexus/rift/codegen_system/namespace/codegen_control_surface.py:1-138
  - src/melder/aether/nexus/rift/codegen_system/validation/strategies/codegen_recursive_control_strategy.py:1-88
  IMPACT: The `codegen` namespace object is now governed by the selected
    projection instead of leaking the raw internal system and leaving recursive
    behavior implicit.
  NEXT: return the landed slice for review and decide whether to close this
    task or continue into deeper meta-policy features.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-25T18:11:15Z
  TYPE: MEASURE
  CLAIM: The recursive-codegen follow-on is green in both the runtime codegen
    ring and the direct ACL/compiler/profile ring.
  EVIDENCE:
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_nexus.py -k "codegen"` -> `40 passed, 112 deselected`
  - validation_result: `python -m pytest -q tests/unit/melder/aether/test_frame_acl_codegen_safe_profile.py tests/unit/melder/aether/test_frame_acl_codegen_hybrid_profile.py tests/unit/melder/aether/test_frame_acl_codegen_permissive_profile.py tests/unit/melder/aether/test_frame_acl_codegen_validation_profiles.py tests/unit/melder/aether/test_frame_acl_compiler_contracts.py -k "codegen or permissive_codegen_profile_expands_allowed_commands or recursive_codegen"` -> `12 passed, 13 deselected`
  IMPACT: The current phase is stable enough to review without another blind
    pass.
  NEXT: sync the routing state and return the recursive-codegen outcome.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-25T18:11:15Z
  TYPE: FACT
  CLAIM: The deeper meta-policy follow-on is also landed. Reflection denial now
    catches aliased module calls and imported helper names, and the codegen
    profile stack now includes a distinct `full_access` profile above
    `permissive` so `permissive` can stay broadly useful without becoming the
    unconstrained top-end posture.
  EVIDENCE:
  - src/melder/aether/nexus/rift/codegen_system/validation/strategies/codegen_reflection_policy_strategy.py:31-171
  - src/melder/aether/nexus/acl/configurations/profiles/codegen/full_access_profile.py:1-114
  - src/melder/aether/nexus/acl/configurations/profiles/builder/frame_acl_profile_builder.py:7-18
  - tests/unit/melder/aether/test_nexus.py:2728-2802
  - tests/unit/melder/aether/test_frame_acl_codegen_full_access_profile.py:1-31
  IMPACT: The codegen ACL slice is now materially beyond the original direct
    helper checks and the profile ladder has a real unconstrained top-end.
  NEXT: return the fuller slice for review and decide whether to close it or
    continue into yet-deeper meta/inspection policy.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the bounded projection-driven codegen ACL validation
implementation lane.
