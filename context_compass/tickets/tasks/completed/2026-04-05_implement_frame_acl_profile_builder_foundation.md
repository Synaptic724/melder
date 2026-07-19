# Task: Implement Frame ACL Profile Builder Foundation
- Completed: 2026-04-06T12:17:44Z
- Summary: Accepted review slice moved out of the active lane during the 2026-04-06 board cleanup after the user advanced to later ACL/frame-surface work.


## Metadata
- Task ID: TASK-2026-04-05-implement-frame-acl-profile-builder-foundation
- Story: STORY-2026-04-05-frame-acl-profile-builder-foundation
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-05T22:48:24Z
- Updated: 2026-04-06T12:17:44Z

## Objective
Implement the manager-owned ACL profile builder/library foundation by adding
typed ACL rules/rulesets, typed view/codegen profiles, a composed
`FrameACLProfile`, and `FrameACLManager` ownership of the new builder/library.

## Ticket Contract
- ENTRY_GATE: the ACL design task has documented the typed configuration
  direction and the user explicitly approved starting with the profile-builder
  foundation.
- EXECUTION_BOUNDARY: ACL profile builder/library, rules/rulesets, manager
  ownership, and focused tests only.
- DEPENDENCIES:
  - tickets/tasks/2026-04-02_design_profile_contracts_and_access_boundaries_task.md
  - src/melder/aether/nexus/acl/frame_acl_profile.py
  - src/melder/aether/nexus/frame_acl_manager.py
- EXIT_GATE: `FrameACLManager` owns the builder/library, default view/codegen
  profiles are seeded, typed rules/rulesets exist, and focused validation
  passes.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if this slice forces
  `FrameACLConfiguration` typed-root work now.

## Scope Boundaries
- In scope:
  - ACL rule objects
  - ACL ruleset objects
  - typed view/codegen profiles
  - composed frame ACL profile object
  - manager-owned profile builder/library
  - focused ACL profile/manager tests
- Out of scope:
  - full `FrameACLConfiguration` rewrite
  - validator rewrite against descriptor payloads
  - ACL compiler/access-surface implementation
  - viewer integration

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: the task was turned in during the cleanup pass after the user advanced to later ACL/frame-surface work.
## Steps / Checklist
- [x] Implement typed ACL rule and ruleset classes.
- [x] Implement typed view/codegen ACL profile classes.
- [x] Implement composed `FrameACLProfile`.
- [x] Implement manager-owned ACL profile builder/library with default
      registration.
- [x] Update focused tests.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further
      investigation.

## Deliverables
- ACL rule and ruleset classes
- ACL view/codegen profile classes
- manager-owned profile builder/library
- focused tests

## Files / Paths Impacted
- src/melder/aether/nexus/acl/frame_acl_profile.py
- src/melder/aether/nexus/frame_acl_manager.py
- tests/unit/melder/aether/test_frame_acl_profile.py
- tests/unit/melder/aether/test_frame_acl_manager.py

## Validation
- Completed:
  - `python -m py_compile src/melder/aether/nexus/acl/frame_acl_profile.py src/melder/aether/nexus/frame_acl_manager.py src/melder/aether/nexus/nexus.py tests/unit/melder/aether/test_frame_acl_profile.py tests/unit/melder/aether/test_frame_acl_manager.py tests/unit/melder/aether/test_nexus_frame_acl_profiles.py`
  - `python -m pytest -q tests/unit/melder/aether/test_frame_acl_profile.py tests/unit/melder/aether/test_frame_acl_manager.py tests/unit/melder/aether/test_nexus_frame_acl_profiles.py`

## Risks / Rollback Notes
- Risk: the current placeholder JSON-holder API leaks too far into the new
  foundation and prevents typed composition.
  Rollback: keep legacy compatibility out of scope and replace the profile side
  cleanly inside this bounded slice.

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
  - system_docs/patches/active/frame_acl_profile_builder_foundation/architecture_patch.md
  - system_docs/patches/active/frame_acl_profile_builder_foundation/component_patch_frame_acl_profile.md
  - system_docs/patches/active/frame_acl_profile_builder_foundation/component_patch_frame_acl_manager.md
  - system_docs/patches/active/frame_acl_profile_builder_foundation/code_description_patch_frame_acl_profile_builder.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-05T22:48:24Z
  TYPE: PLAN
  CLAIM: The active ACL implementation slice should start by replacing the
    generic reusable profile layer, not the live frame configuration chain.
    `FrameACLManager` should own a SpellExaminer-style ACL profile builder/
    library with two registries:
    - view profiles by name
    - codegen profiles by name
    seeded with `"default"` in both. `FrameACLProfile` should become the
    composed object that points at one view profile and one codegen profile plus
    future local overrides. Typed rule/ruleset objects should be introduced now
    so the foundation is not another JSON-holder layer.
  EVIDENCE:
  - src/melder/aether/nexus/acl/frame_acl_profile.py:370-543
  - src/melder/aether/nexus/frame_acl_manager.py:14-535
  - codex/context_compass/tickets/tasks/2026-04-02_design_profile_contracts_and_access_boundaries_task.md:420-472
  - user_instruction: "build a Profile Builder class that hosts both the ACLViewProfiles and the ACLCodegen Profiles held in 2 different dictionaries"
  IMPACT: The next code cut can stay bounded and useful without forcing the
    full typed configuration migration yet.
  NEXT: create the patch-doc set, then rewrite the ACL profile layer and
    manager ownership model.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-05T22:48:24Z
  TYPE: PLAN
  CLAIM: The patch-doc consumption mapping for this ACL foundation slice is now
    explicit. `architecture_patch.md` maps to the non-goals and the rule that
    the existing manager/container/chain shell remains intact. The
    `component_patch_frame_acl_profile.md` doc maps to the typed rule/ruleset,
    typed view/codegen profile, and composed `FrameACLProfile` rewrite inside
    `frame_acl_profile.py`. The `component_patch_frame_acl_manager.md` doc maps
    to manager ownership of the new profile builder/library plus default
    registration mechanics. The
    `code_description_patch_frame_acl_profile_builder.md` doc maps to default
    profile seeding, composition flow, and focused test validation.
  EVIDENCE:
  - codex/context_compass/system_docs/patches/active/frame_acl_profile_builder_foundation/architecture_patch.md:1-19
  - codex/context_compass/system_docs/patches/active/frame_acl_profile_builder_foundation/component_patch_frame_acl_profile.md:1-13
  - codex/context_compass/system_docs/patches/active/frame_acl_profile_builder_foundation/component_patch_frame_acl_manager.md:1-13
  - codex/context_compass/system_docs/patches/active/frame_acl_profile_builder_foundation/code_description_patch_frame_acl_profile_builder.md:1-12
  IMPACT: The code cut can stay bounded to the reusable profile layer and
    manager ownership model without silently widening into typed configuration
    or validator/compiler work.
  NEXT: rewrite `frame_acl_profile.py`, update `frame_acl_manager.py`, and
    align the focused ACL profile/manager tests to the new model.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-05T22:48:24Z
  TYPE: FACT
  CLAIM: The ACL profile builder foundation is now implemented in code.
    `frame_acl_profile.py` now contains typed `FrameACLRule`,
    `FrameACLRuleSet`, `FrameACLViewProfile`, `FrameACLCodegenProfile`,
    a composed `FrameACLProfile`, and a manager-style
    `FrameACLProfileBuilder` that seeds default view/codegen profiles.
    `FrameACLManager` now owns that builder/library and can register reusable
    view/codegen profiles plus compose/register `FrameACLProfile` objects from
    them. The focused ACL profile and Nexus facade tests are aligned to the new
    model.
  EVIDENCE:
  - src/melder/aether/nexus/acl/frame_acl_profile.py:370-1084
  - src/melder/aether/nexus/frame_acl_manager.py:14-735
  - tests/unit/melder/aether/test_frame_acl_profile.py:1-276
  - tests/unit/melder/aether/test_nexus_frame_acl_profiles.py:1-65
  IMPACT: The reusable ACL profile side is no longer a generic JSON-holder
    strategy registry, which means later typed configuration work now has a real
    profile substrate to build on.
  NEXT: run focused py_compile/pytest for the ACL profile and manager surface,
    then fix any fallout.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-05T23:00:19Z
  TYPE: MEASURE
  CLAIM: The ACL profile builder foundation is green on the focused ACL
    surface. `py_compile` passed on the touched runtime and test files, and the
    focused pytest slice passed with 21 tests. The slice now has typed
    `FrameACLRule` / `FrameACLRuleSet`, typed view/codegen profiles, a composed
    `FrameACLProfile`, a manager-owned `FrameACLProfileBuilder` seeded with
    default profiles, and aligned manager/Nexus facade tests.
  EVIDENCE:
  - src/melder/aether/nexus/acl/frame_acl_profile.py:370-1084
  - src/melder/aether/nexus/frame_acl_manager.py:14-735
  - command:python -m pytest -q tests/unit/melder/aether/test_frame_acl_profile.py tests/unit/melder/aether/test_frame_acl_manager.py tests/unit/melder/aether/test_nexus_frame_acl_profiles.py
  IMPACT: The ACL subsystem now has a real reusable profile substrate, so the
    next design/implementation phase can move into typed
    `FrameACLConfiguration` work without starting from generic JSON-holder
    profiles.
  NEXT: review the ACL profile builder foundation with the user and decide
    whether the next slice is typed `FrameACLConfiguration` / builder rewrite
    or another ACL contract refinement pass.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task exists to land the manager-owned ACL profile builder/library
foundation as the next bounded ACL implementation slice.



