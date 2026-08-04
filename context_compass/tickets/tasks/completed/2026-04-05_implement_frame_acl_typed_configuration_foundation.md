# Task: Implement Frame ACL Typed Configuration Foundation
- Completed: 2026-04-06T12:17:44Z
- Summary: Accepted review slice moved out of the active lane during the 2026-04-06 board cleanup after the user advanced to later ACL/frame-surface work.


## Metadata
- Task ID: TASK-2026-04-05-implement-frame-acl-typed-configuration-foundation
- Story: STORY-2026-04-05-frame-acl-typed-configuration-foundation
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-05T23:51:00Z
- Updated: 2026-04-06T12:17:44Z

## Objective
Implement typed `FrameACLConfiguration`, typed `FrameACLViewConfiguration`,
typed `FrameACLCodegenConfiguration`, and the corresponding builder rewrite off
raw JSON strings.

## Ticket Contract
- ENTRY_GATE: the reusable ACL profile builder/catalog is landed and the user
  explicitly asked to continue.
- EXECUTION_BOUNDARY: typed ACL configuration classes, builder draft flow, and
  focused ACL tests only.
- DEPENDENCIES:
  - tickets/tasks/2026-04-05_implement_frame_acl_profile_builder_foundation.md
  - tickets/tasks/2026-04-05_implement_frame_acl_safe_default_profiles_task.md
  - src/melder/aether/nexus/acl/frame_acl_configuration.py
  - src/melder/aether/nexus/acl/frame_acl_builder.py
  - src/melder/aether/nexus/acl/frame_acl_container.py
- EXIT_GATE: typed frame ACL configuration classes exist, the builder edits them
  instead of raw JSON strings, and focused validation passes.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if descriptor-backed validator
  work becomes mandatory for this slice.

## Scope Boundaries
- In scope:
  - typed `FrameACLViewConfiguration`
  - typed `FrameACLCodegenConfiguration`
  - typed root `FrameACLConfiguration`
  - builder draft/commit rewrite
  - focused ACL configuration/builder/container tests
- Out of scope:
  - descriptor-backed validator rewrite
  - compiled access surface
  - viewer integration
  - spellbook selector model

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: the task was turned in during the cleanup pass after the user advanced to later ACL/frame-surface work.
## Steps / Checklist
- [x] Implement typed `FrameACLViewConfiguration`.
- [x] Implement typed `FrameACLCodegenConfiguration`.
- [x] Rework `FrameACLConfiguration` into a typed root object.
- [x] Rework `FrameACLBuilder` to edit typed configuration objects.
- [x] Update focused tests.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further
      investigation.

## Deliverables
- typed ACL configuration classes
- typed builder draft flow
- focused tests

## Files / Paths Impacted
- src/melder/aether/nexus/acl/frame_acl_configuration.py
- src/melder/aether/nexus/acl/frame_acl_builder.py
- src/melder/aether/nexus/acl/frame_acl_container.py
- tests/unit/melder/aether/test_frame_acl_configuration.py
- tests/unit/melder/aether/test_frame_acl_builder.py
- tests/unit/melder/aether/test_frame_acl_container.py
- tests/unit/melder/aether/test_frame_acl_validator.py

## Validation
- Completed:
  - `python -m py_compile src/melder/aether/nexus/acl/frame_acl_view_configuration.py src/melder/aether/nexus/acl/frame_acl_codegen_configuration.py src/melder/aether/nexus/acl/frame_acl_configuration.py src/melder/aether/nexus/acl/frame_acl_builder.py src/melder/aether/nexus/acl/frame_acl_container.py src/melder/aether/nexus/acl/frame_acl_validator.py tests/unit/melder/aether/test_frame_acl_configuration.py tests/unit/melder/aether/test_frame_acl_builder.py tests/unit/melder/aether/test_frame_acl_container.py tests/unit/melder/aether/test_frame_acl_validator.py`
  - `python -m pytest -q tests/unit/melder/aether/test_frame_acl_configuration.py tests/unit/melder/aether/test_frame_acl_builder.py tests/unit/melder/aether/test_frame_acl_container.py tests/unit/melder/aether/test_frame_acl_validator.py`

## Risks / Rollback Notes
- Risk: serialization and builder state split in incompatible ways.
  Rollback: keep the root chain metadata stable and focus changes on the child
  configuration payload objects.

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
  - system_docs/patches/active/frame_acl_typed_configuration/architecture_patch.md
  - system_docs/patches/active/frame_acl_typed_configuration/component_patch_frame_acl_configuration.md
  - system_docs/patches/active/frame_acl_typed_configuration/component_patch_frame_acl_builder.md
  - system_docs/patches/active/frame_acl_typed_configuration/code_description_patch_frame_acl_configuration.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-05T23:51:00Z
  TYPE: PLAN
  CLAIM: The next ACL implementation slice should move the frame-local applied
    configuration layer off raw JSON strings. The reusable profile catalog is
    already landed, so now `FrameACLConfiguration` should become a typed root
    object that owns:
    - `FrameACLViewConfiguration`
    - `FrameACLCodegenConfiguration`
    while `FrameACLBuilder` should draft and commit those typed objects instead
    of string payloads.
  EVIDENCE:
  - src/melder/aether/nexus/acl/frame_acl_configuration.py:10-444
  - src/melder/aether/nexus/acl/frame_acl_builder.py:10-192
  - codex/context_compass/tickets/tasks/2026-04-02_design_profile_contracts_and_access_boundaries_task.md:441-472
  IMPACT: This is the clean next boundary before the validator/compiler grows
    into descriptor-backed ACL evaluation.
  NEXT: create the patch-doc set, then rewrite the configuration and builder
    classes plus their focused tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-05T23:51:00Z
  TYPE: PLAN
  CLAIM: The patch-doc consumption mapping for this typed configuration slice
    is now explicit. `architecture_patch.md` maps to the rule that the
    chain/container shell stays intact while the applied configuration payload
    changes. `component_patch_frame_acl_configuration.md` maps to introducing
    typed root/view/codegen configuration objects in
    `frame_acl_configuration.py`. `component_patch_frame_acl_builder.md` maps to
    rewriting builder draft/edit/commit behavior off raw JSON strings and onto
    typed configuration objects in `frame_acl_builder.py`. The
    `code_description_patch_frame_acl_configuration.md` doc maps to the new
    typed configuration lifecycle and focused test validation.
  EVIDENCE:
  - codex/context_compass/system_docs/patches/active/frame_acl_typed_configuration/architecture_patch.md:1-19
  - codex/context_compass/system_docs/patches/active/frame_acl_typed_configuration/component_patch_frame_acl_configuration.md:1-13
  - codex/context_compass/system_docs/patches/active/frame_acl_typed_configuration/component_patch_frame_acl_builder.md:1-13
  - codex/context_compass/system_docs/patches/active/frame_acl_typed_configuration/code_description_patch_frame_acl_configuration.md:1-12
  IMPACT: The code cut can stay bounded to typed applied configuration and the
    builder rewrite without silently widening into validator/compiler work.
  NEXT: rewrite `frame_acl_configuration.py`, then rewrite
    `frame_acl_builder.py`, then align the focused configuration/builder tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T00:00:41Z
  TYPE: FACT
  CLAIM: The typed applied ACL configuration layer is now implemented in code.
    The slice adds:
    - `FrameACLViewConfiguration`
    - `FrameACLCodegenConfiguration`
    - typed root `FrameACLConfiguration`
    and rewrites `FrameACLBuilder` to draft typed configuration objects and
    apply a composed `FrameACLProfile` directly. The focused configuration,
    builder, container, and validator tests are aligned to the typed model.
  EVIDENCE:
  - src/melder/aether/nexus/acl/frame_acl_view_configuration.py:13-212
  - src/melder/aether/nexus/acl/frame_acl_codegen_configuration.py:13-204
  - src/melder/aether/nexus/acl/frame_acl_configuration.py:44-364
  - src/melder/aether/nexus/acl/frame_acl_builder.py:17-184
  - tests/unit/melder/aether/test_frame_acl_configuration.py:1-316
  - tests/unit/melder/aether/test_frame_acl_builder.py:1-187
  IMPACT: The ACL subsystem no longer depends on raw JSON strings for the
    applied configuration layer, which clears the next path into descriptor-
    backed validator/compiler work.
  NEXT: run focused validation and then review whether the next ACL slice is
    the validator rewrite against payload-backed descriptor records.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T00:00:41Z
  TYPE: MEASURE
  CLAIM: The typed applied ACL configuration slice is green on the focused ACL
    config surface. `py_compile` passed on the touched runtime and test files,
    and the focused pytest slice passed with 32 tests.
  EVIDENCE:
  - command:python -m pytest -q tests/unit/melder/aether/test_frame_acl_configuration.py tests/unit/melder/aether/test_frame_acl_builder.py tests/unit/melder/aether/test_frame_acl_container.py tests/unit/melder/aether/test_frame_acl_validator.py
  IMPACT: The ACL lane now has both a reusable named profile substrate and a
    typed applied configuration layer.
  NEXT: review whether the next bounded ACL tranche should target the
    descriptor-backed validator/compiler path.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task exists to land the typed applied ACL configuration layer on top of the
reusable named profile catalog.



