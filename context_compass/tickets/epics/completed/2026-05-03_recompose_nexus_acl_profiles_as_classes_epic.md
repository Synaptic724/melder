Completed: 2026-05-03T20:55:23Z
Summary: Replaced the function-only ACL preset composition path with shared
interface strategy classes plus dedicated family builders for view, command,
and codegen while preserving the existing tested behaviors.

# Epic: Recompose Nexus ACL Profiles As Classes

## Metadata
- Epic ID: EPIC-2026-05-03-recompose-nexus-acl-profiles-as-classes
- Status: done
- Owner: codex
- Agent Name: codex_0
- Priority: p1
- Created: 2026-05-03T19:52:51Z
- Updated: 2026-05-03T20:55:23Z
- Updated: 2026-05-03T19:52:51Z
- Target Window: 2026-Q2
- Related Program/Initiative: Nexus ACL profile composition and builder cleanup

## Problem / Opportunity
The current Nexus ACL preset surface is heavily module-factory shaped:
- module-level functions return configured profile objects
- validator helpers are spread across function-only modules
- the builder/registry imports recipe modules instead of selecting explicit
  class-based profile/strategy objects

This style is valid, but it weakens object ownership, internal identity,
sentinel coverage, composition clarity, and introspection compared to a
class-based strategy/builder design.

The opportunity is to preserve the same ACL behaviors while recomposing the
profile system into real classes and explicit composition seams that better
match the broader architecture style of the project.

## MRP Alignment (Most Reasonable Product)
The MRP is not "rewrite ACL from scratch."
The MRP is:
- identify how the current profile modules, preset factories, validator helper
  modules, and builder registry should be re-expressed as classes
- preserve behavior
- preserve test coverage or update tests where the composition surface changes
- land on a stronger ownership/composition model without semantic drift

## Ticket Contract
- ENTRY_GATE: the user explicitly requested a new epic to investigate turning
  these module-method profile recipes into real classes.
- EXECUTION_BOUNDARY: Nexus ACL profile composition only, including preset
  profile creation modules, validator profile helpers, builder selection, and
  affected tests.
- DEPENDENCIES:
  - `src/melder/aether/nexus/acl/configurations/profiles/**`
  - `src/melder/aether/nexus/acl/validator/profiles/**`
  - `src/melder/aether/nexus/acl/builder/**`
  - related tests
- EXIT_GATE: the epic holds a concrete design direction for replacing the
  module-factory style with class-based composition while keeping the same
  runtime behaviors.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if preserving behavior requires
  keeping some modules function-based or mixing both models longer than desired.

## Goals (Outcomes)
- Define how ACL preset profiles should become real classes.
- Define how validator profile helpers should become class-based strategies or
  class-owned methods.
- Define how the builder should select and compose those classes.
- Preserve current ACL behavior while improving ownership and introspection.
- Identify which tests need to be preserved, updated, or expanded.

## Non-Goals (Explicit Exclusions)
- Immediate broad refactor of unrelated Nexus or Rift systems.
- Behavior changes to ACL policy semantics as part of the first design cut.
- Rewriting the whole ACL subsystem without staged compatibility planning.

## Scope Boundaries
- In scope:
  - preset profile factory modules
  - profile composition classes
  - validator profile helper modules
  - builder/registry ownership of composition
  - tests covering those surfaces
- Out of scope:
  - unrelated command system or projection changes
  - broad performance tuning
  - unrelated sentinel cleanup

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested a dedicated epic for
  investigating and planning this composition rewrite.

## Success Metrics
- The new composition direction is explicit and class-based.
- Current behaviors remain clearly mapped to future classes/strategies.
- The builder ownership story is clearer than the current module-recipe model.
- The epic is specific enough to stage implementation stories/tasks.

## Requirements (Functional + Non-Functional)
- Functional:
  - map current profile modules to future class surfaces
  - map current validator helper modules to future class/strategy surfaces
  - identify builder/registry changes needed
  - identify test surfaces affected
- Non-functional:
  - preserve behavior
  - improve ownership clarity
  - improve object-level introspection and internal identity
  - keep rollout understandable and staged

## Constraints / Assumptions
- Current module-factory behavior is valid and working; the problem is style,
  ownership, and composition quality, not necessarily correctness.
- The replacement should prefer classes/strategies over function-only modules.
- Tests must anchor the behavior so the rewrite does not drift semantically.

## Dependencies / External References
- `src/melder/aether/nexus/acl/configurations/profiles/`
- `src/melder/aether/nexus/acl/validator/profiles/`
- `src/melder/aether/nexus/acl/builder/`

## Milestones (Track Progress)
- [ ] Milestone 1: map current module-recipe surfaces to desired class surfaces
- [ ] Milestone 2: define builder/strategy ownership for profile composition
- [ ] Milestone 3: define test preservation/update plan

## Stories (Required to Complete)
- [ ] Story: define class-based replacements for ACL preset profile modules
- [ ] Story: define class-based replacements for validator helper modules
- [ ] Story: define builder/registry composition plan and affected test plan

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: inventory all function-only ACL profile and validator modules
- [ ] Task: map current behaviors to future class/strategy ownership
- [ ] Task: identify tests that encode current module-factory behavior

## Acceptance Criteria (Epic Done)
- A class-based composition direction is documented.
- The current module-factory behavior is fully mapped to future class/strategy
  ownership.
- The builder/registry changes are clear enough to implement in bounded tasks.
- Test implications are explicit.

## Risks / Mitigations
- Risk: the rewrite overcorrects style and accidentally changes ACL semantics.
  Mitigation: keep the first epic strictly investigative and behavior-preserving.
- Risk: some factory modules turn out to be acceptable as functions.
  Mitigation: record exceptions explicitly rather than forcing dogma.

## Applicable Anti-Patterns
- [ ] No premature code rewrite without a behavior map.
- [ ] No style cleanup that loses ownership of current ACL semantics.
- [ ] No broad refactor without identifying the impacted tests first.

## Validation / Test Approach
- Design-only in this epic.
- Validation is a clear behavior-preserving class-composition plan plus a test
  impact map.

## Rollout / Adoption Plan
- First inventory and classify the current function-only modules.
- Then define the replacement class/strategy surfaces.
- Then stage bounded implementation stories/tasks with test updates.

## Open Questions
- Which current factory modules should become classes directly versus
  classmethods on existing profile types?
- Should validators become strategy objects, class-owned static/class methods,
  or a hybrid?
- How much compatibility scaffolding should exist during the transition?

## Decision Log
- 2026-05-03T19:52:51Z: Opened to investigate replacing module-factory ACL
  profile composition with class-based strategy/builder composition while
  preserving current behavior.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Notes
- DATETIME: 2026-05-03T19:52:51Z
  TYPE: PLAN
  CLAIM: The current ACL profile/validator surface is working but is composed
    in a style the user does not want to keep. The first step is to map the
    current module-level recipe and validator helper behavior into future
    class-based composition seams before any code rewrite happens.
  EVIDENCE:
  - user_instruction: "we want to turn these things into real classes not module methods and how we should compose all this stuff and update the tests"
  IMPACT: The next move is investigative and architectural, not immediate code
    churn.
  NEXT: use this epic as the durable anchor for the class-composition plan.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-03T19:52:51Z
  TYPE: MEASURE
  CLAIM: The first family-only implementation slice is now landed for **view**.
    The four view preset modules were converted from module-level factory
    functions into concrete strategy classes, a dedicated
    `FrameACLViewProfileBuilder` with `load_defaults()` now owns registration
    and selection of those strategies, `FrameACLProfileBuilder` now uses that
    family builder for view profile construction, and the targeted view-related
    pytest ring passed without changing command or codegen yet.
  EVIDENCE:
  - src/melder/aether/nexus/acl/configurations/profiles/view/frame_acl_view_profile_strategy.py:1-23
  - src/melder/aether/nexus/acl/configurations/profiles/view/frame_acl_view_profile_builder.py:1-135
  - src/melder/aether/nexus/acl/configurations/profiles/view/safe_profile.py:1-81
  - src/melder/aether/nexus/acl/configurations/profiles/view/hybrid_profile.py:1-68
  - src/melder/aether/nexus/acl/configurations/profiles/view/permissive_profile.py:1-66
  - src/melder/aether/nexus/acl/configurations/profiles/view/precision.py:1-66
  - src/melder/aether/nexus/acl/configurations/profiles/view/frame_acl_view_profile.py:164-256
  - src/melder/aether/nexus/acl/configurations/profiles/builder/frame_acl_profile_builder.py:1-420
  - validation_result:
    `python -m pytest -q tests/unit/melder/aether/test_frame_acl_view_safe_profile.py tests/unit/melder/aether/test_frame_acl_view_hybrid_profile.py tests/unit/melder/aether/test_frame_acl_view_permissive_profile.py tests/unit/melder/aether/test_frame_acl_profile_builder.py` -> `12 passed`
  IMPACT: The view family now demonstrates the exact class-based strategy +
    family builder pattern the user wanted, and command/codegen can follow it
    one family at a time.
  NEXT: if this slice is accepted, repeat the same composition pattern for the
    command family next.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-03T20:32:22Z
  TYPE: FACT
  CLAIM: The first view-family slice left its strategy protocol in a
    view-local file, but the project's shared interface seam is
    `src/melder/utilities/interfaces/interfaces.py`. That makes the current
    placement weaker than the intended ownership model and inconsistent with
    the component map.
  EVIDENCE:
  - src/melder/aether/nexus/acl/configurations/profiles/view/frame_acl_view_profile_strategy.py:1-19
  - src/melder/utilities/interfaces/interfaces.py:1-443
  - codex/context_compass/system_docs/src_components.md:Information Sources
  - user_instruction: "bro move the protocol to the interface file don't keep it in the view folder"
  IMPACT: The next bounded fix is to move `IFrameACLViewProfileStrategy` into
    the shared interfaces file and patch only the direct import consumers in
    the view family and top-level builder.
  NEXT: move the protocol into `src/melder/utilities/interfaces/interfaces.py`,
    update imports, then rerun the targeted syntax and view pytest checks.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-03T20:33:58Z
  TYPE: DECISION
  CLAIM: The view-family strategy contract has now been moved into the shared
    interfaces seam. `IFrameACLViewProfileStrategy` lives in
    `src/melder/utilities/interfaces/interfaces.py`, the direct view-family
    consumers now import it from there, and the old view-local protocol file
    has been removed.
  EVIDENCE:
  - src/melder/utilities/interfaces/interfaces.py:2467-2493
  - src/melder/aether/nexus/acl/configurations/profiles/view/frame_acl_view_profile_builder.py:1-22
  - src/melder/aether/nexus/acl/configurations/profiles/view/safe_profile.py:1-6
  - src/melder/aether/nexus/acl/configurations/profiles/view/hybrid_profile.py:1-6
  - src/melder/aether/nexus/acl/configurations/profiles/view/permissive_profile.py:1-6
  - src/melder/aether/nexus/acl/configurations/profiles/view/precision.py:1-6
  IMPACT: The first class-based view slice now uses the repo's real shared
    interface surface instead of a local one-off protocol file, which keeps
    the ownership model cleaner before command/codegen follow the same pattern.
  NEXT: run targeted compile and pytest validation for the moved interface
    seam.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-03T20:34:43Z
  TYPE: MEASURE
  CLAIM: The shared-interface move is validated. The targeted compile pass
    succeeded for the moved interface plus its direct consumers, and the same
    four view-related pytest modules still pass. The only lingering search hit
    for the old module path is a stale `__pycache__` entry, not live source.
  EVIDENCE:
  - validation_result:
    `python -m py_compile "src/melder/utilities/interfaces/interfaces.py" "src/melder/aether/nexus/acl/configurations/profiles/view/frame_acl_view_profile_builder.py" "src/melder/aether/nexus/acl/configurations/profiles/view/safe_profile.py" "src/melder/aether/nexus/acl/configurations/profiles/view/hybrid_profile.py" "src/melder/aether/nexus/acl/configurations/profiles/view/permissive_profile.py" "src/melder/aether/nexus/acl/configurations/profiles/view/precision.py" "src/melder/aether/nexus/acl/configurations/profiles/view/frame_acl_view_profile.py" "src/melder/aether/nexus/acl/configurations/profiles/builder/frame_acl_profile_builder.py"`
  - validation_result:
    `python -m pytest -q tests/unit/melder/aether/test_frame_acl_view_safe_profile.py tests/unit/melder/aether/test_frame_acl_view_hybrid_profile.py tests/unit/melder/aether/test_frame_acl_view_permissive_profile.py tests/unit/melder/aether/test_frame_acl_profile_builder.py` -> `12 passed`
  - search_result:
    `src/melder/aether/nexus/acl/configurations/profiles/view/__pycache__/frame_acl_view_profile_strategy.cpython-313.pyc`
  IMPACT: The first view-family slice now matches the intended shared-interface
    seam without breaking the existing behavior or the targeted tests.
  NEXT: if you want to keep going, the next bounded family is command using the
    same pattern.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-03T20:41:21Z
  TYPE: PLAN
  CLAIM: The next bounded family slice is `command`, and its real coverage
    surface is slightly different from view. There are no dedicated
    `test_frame_acl_command_*_profile.py` files per preset module; instead the
    command family is covered through `test_frame_acl_command_profile.py`, the
    top-level `test_frame_acl_profile_builder.py`, and the existing fluent
    `test_frame_acl_command_builder.py` path. The clean move is therefore to
    mirror the view pattern with a shared command strategy interface, one
    command family builder, command-classmethod rewiring, top-level builder
    rewiring, and only those real tests.
  EVIDENCE:
  - src/melder/aether/nexus/acl/configurations/profiles/command/safe_profile.py:1-40
  - src/melder/aether/nexus/acl/configurations/profiles/command/hybrid_profile.py:1-40
  - src/melder/aether/nexus/acl/configurations/profiles/command/permissive_profile.py:1-40
  - src/melder/aether/nexus/acl/configurations/profiles/command/precision.py:1-40
  - src/melder/aether/nexus/acl/configurations/profiles/command/frame_acl_command_profile.py:116-153
  - src/melder/aether/nexus/acl/configurations/profiles/builder/frame_acl_profile_builder.py:85-118
  - tests/unit/melder/aether/test_frame_acl_command_profile.py:1-127
  - tests/unit/melder/aether/test_frame_acl_profile_builder.py:1-194
  - tests/unit/melder/aether/test_frame_acl_command_builder.py:1-89
  IMPACT: The command rewrite can stay tightly scoped and does not need fake
    new test surfaces invented just to mimic the earlier view tranche.
  NEXT: patch the command family using the same class-based strategy +
    family-builder pattern as view, then rerun the targeted command/profile
    builder pytest ring.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-03T20:44:21Z
  TYPE: DECISION
  CLAIM: The command family is now rewritten to the same class-based strategy
    + family-builder pattern as view. A shared
    `IFrameACLCommandProfileStrategy` now lives in the central interfaces file,
    the four command preset modules now export concrete strategy classes, a
    dedicated `FrameACLCommandProfileBuilder` owns `load_defaults()` and
    command strategy selection, `FrameACLCommandProfile` classmethods now build
    through those strategies, and the top-level `FrameACLProfileBuilder` now
    owns and exposes the dedicated command family builder.
  EVIDENCE:
  - src/melder/utilities/interfaces/interfaces.py:2484-2510
  - src/melder/aether/nexus/acl/configurations/profiles/command/safe_profile.py:1-55
  - src/melder/aether/nexus/acl/configurations/profiles/command/hybrid_profile.py:1-56
  - src/melder/aether/nexus/acl/configurations/profiles/command/permissive_profile.py:1-56
  - src/melder/aether/nexus/acl/configurations/profiles/command/precision.py:1-54
  - src/melder/aether/nexus/acl/configurations/profiles/command/frame_acl_command_profile_builder.py:1-135
  - src/melder/aether/nexus/acl/configurations/profiles/command/frame_acl_command_profile.py:116-153
  - src/melder/aether/nexus/acl/configurations/profiles/builder/frame_acl_profile_builder.py:1-175
  - tests/unit/melder/aether/test_frame_acl_profile_builder.py:1-111
  IMPACT: The second family now follows the same ownership model as view, and
    command is no longer relying on module-level preset factory functions for
    the reusable profile path.
  NEXT: run targeted compile and pytest validation for the new command family
    seam.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-03T20:45:03Z
  TYPE: MEASURE
  CLAIM: The command-family rewrite is validated. The targeted compile pass
    succeeded for the moved command strategy seam and its direct consumers, and
    the real command/profile-builder pytest ring still passes. The only stale
    references to the old `create_*_command_profile` names are bytecode hits in
    `__pycache__`, not live source.
  EVIDENCE:
  - validation_result:
    `python -m py_compile "src/melder/utilities/interfaces/interfaces.py" "src/melder/aether/nexus/acl/configurations/profiles/command/safe_profile.py" "src/melder/aether/nexus/acl/configurations/profiles/command/hybrid_profile.py" "src/melder/aether/nexus/acl/configurations/profiles/command/permissive_profile.py" "src/melder/aether/nexus/acl/configurations/profiles/command/precision.py" "src/melder/aether/nexus/acl/configurations/profiles/command/frame_acl_command_profile_builder.py" "src/melder/aether/nexus/acl/configurations/profiles/command/frame_acl_command_profile.py" "src/melder/aether/nexus/acl/configurations/profiles/builder/frame_acl_profile_builder.py"`
  - validation_result:
    `python -m pytest -q tests/unit/melder/aether/test_frame_acl_command_profile.py tests/unit/melder/aether/test_frame_acl_command_builder.py tests/unit/melder/aether/test_frame_acl_profile_builder.py` -> `23 passed`
  - search_result:
    `src/melder/aether/nexus/acl/configurations/profiles/command/__pycache__/...`
  IMPACT: The second family now matches the view-family ownership model
    without breaking the existing command or profile-builder behavior.
  NEXT: if you want to continue, the next family boundary is codegen.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-03T20:54:31Z
  TYPE: DECISION
  CLAIM: The codegen family is now rewritten to the same class-based strategy
    + family-builder pattern as the earlier view and command slices. A shared
    `IFrameACLCodegenProfileStrategy` now lives in the central interfaces file,
    the five codegen preset modules now export concrete strategy classes
    (`safe`, `hybrid`, `permissive`, `full_access`, `precision`), a dedicated
    `FrameACLCodegenProfileBuilder` owns `load_defaults()` and codegen
    strategy selection, `FrameACLCodegenProfile` classmethods now build
    through those strategies, and the top-level `FrameACLProfileBuilder` now
    owns and exposes the dedicated codegen family builder.
  EVIDENCE:
  - src/melder/utilities/interfaces/interfaces.py:2512-2538
  - src/melder/aether/nexus/acl/configurations/profiles/codegen/safe_profile.py:1-82
  - src/melder/aether/nexus/acl/configurations/profiles/codegen/hybrid_profile.py:1-107
  - src/melder/aether/nexus/acl/configurations/profiles/codegen/permissive_profile.py:1-85
  - src/melder/aether/nexus/acl/configurations/profiles/codegen/full_access_profile.py:1-126
  - src/melder/aether/nexus/acl/configurations/profiles/codegen/precision.py:1-102
  - src/melder/aether/nexus/acl/configurations/profiles/codegen/frame_acl_codegen_profile_builder.py:1-138
  - src/melder/aether/nexus/acl/configurations/profiles/codegen/frame_acl_codegen_profile.py:119-209
  - src/melder/aether/nexus/acl/configurations/profiles/builder/frame_acl_profile_builder.py:1-185
  - tests/unit/melder/aether/test_frame_acl_profile_builder.py:1-150
  IMPACT: All three ACL profile families now follow one consistent object-owned
    strategy/builder composition model instead of mixing class-based and
    module-factory surfaces.
  NEXT: run targeted compile and pytest validation for the new codegen family
    seam, then close the epic if the last family validates cleanly.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-03T20:55:23Z
  TYPE: MEASURE
  CLAIM: The codegen-family rewrite is validated. The targeted compile pass
    succeeded for the new codegen strategy seam and its direct consumers, and
    the real codegen/profile-builder pytest ring still passes. The only stale
    references to the old `create_*_codegen_profile` names are bytecode hits in
    `__pycache__`, not live source.
  EVIDENCE:
  - validation_result:
    `python -m py_compile "src/melder/utilities/interfaces/interfaces.py" "src/melder/aether/nexus/acl/configurations/profiles/codegen/safe_profile.py" "src/melder/aether/nexus/acl/configurations/profiles/codegen/hybrid_profile.py" "src/melder/aether/nexus/acl/configurations/profiles/codegen/permissive_profile.py" "src/melder/aether/nexus/acl/configurations/profiles/codegen/full_access_profile.py" "src/melder/aether/nexus/acl/configurations/profiles/codegen/precision.py" "src/melder/aether/nexus/acl/configurations/profiles/codegen/frame_acl_codegen_profile_builder.py" "src/melder/aether/nexus/acl/configurations/profiles/codegen/frame_acl_codegen_profile.py" "src/melder/aether/nexus/acl/configurations/profiles/builder/frame_acl_profile_builder.py"`
  - validation_result:
    `python -m pytest -q tests/unit/melder/aether/test_frame_acl_codegen_profile.py tests/unit/melder/aether/test_frame_acl_codegen_safe_profile.py tests/unit/melder/aether/test_frame_acl_codegen_hybrid_profile.py tests/unit/melder/aether/test_frame_acl_codegen_permissive_profile.py tests/unit/melder/aether/test_frame_acl_codegen_full_access_profile.py tests/unit/melder/aether/test_frame_acl_profile_builder.py` -> `25 passed`
  - search_result:
    `src/melder/aether/nexus/acl/configurations/profiles/codegen/__pycache__/...`
  IMPACT: All three ACL profile families now follow the same shared-interface +
    family-builder composition model, and the epic acceptance target is met.
  NEXT: close this epic and remove its active routing row from
    `attention_board.md`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user
- [x] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: behavior mapping, class/strategy ownership, builder ownership,
  and test preservation.
- Add notes when the replacement composition direction becomes clearer.
- Keep notes append-only and preserve UNKNOWN-first discipline.

## Context / Handoff Summary
This epic owns the plan for replacing function-only Nexus ACL profile/validator
modules with class-based composition while preserving current behavior.
