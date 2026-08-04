# Task: Refactor Frame ACL Profile Catalog Into Profiles Package
- Completed: 2026-04-06T12:17:44Z
- Summary: Accepted review slice moved out of the active lane during the 2026-04-06 board cleanup after the user advanced to later ACL/frame-surface work.


## Metadata
- Task ID: TASK-2026-04-06-refactor-frame-acl-profile-catalog-into-profiles-package
- Story: STORY-2026-04-05-frame-acl-profile-builder-foundation
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-06T00:11:45Z
- Updated: 2026-04-06T12:17:44Z

## Objective
Refactor the ACL profile catalog into a real `acl/profiles/` package so rules,
rulesets, builder, and the named `safe` / `hybrid` / `permissive` profiles
exist as explicit modules/objects instead of being buried inline in one file.

## Ticket Contract
- ENTRY_GATE: the reusable ACL profile foundation and named profile catalog are
  landed, and the user explicitly requested that they live in a real profiles
  package with visible profile objects.
- EXECUTION_BOUNDARY: ACL profile catalog package refactor only.
- DEPENDENCIES:
  - tickets/tasks/2026-04-05_implement_frame_acl_profile_builder_foundation.md
  - tickets/tasks/2026-04-05_implement_frame_acl_safe_default_profiles_task.md
  - src/melder/aether/nexus/acl/frame_acl_profile.py
- EXIT_GATE: rules, rulesets, builder, and named profile modules live under
  `src/melder/aether/nexus/acl/profiles/`, focused validation passes, and the
  manager/Nexus imports are aligned.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the refactor forces broad ACL
  configuration/compiler changes in the same slice.

## Scope Boundaries
- In scope:
  - `acl/profiles/` package
  - rule/ruleset modules
  - view/codegen profile modules
  - named `safe` / `hybrid` / `permissive` profile modules
  - builder module
  - import rewiring
  - focused ACL profile tests
- Out of scope:
  - typed config rewrite
  - validator/compiler logic changes
  - viewer integration

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: the task was turned in during the cleanup pass after the user advanced to later ACL/frame-surface work.
## Steps / Checklist
- [x] Create the `acl/profiles/` package and move the catalog classes into it.
- [x] Add explicit named profile modules for `safe`, `hybrid`, and `permissive`.
- [x] Rewire manager/Nexus imports.
- [x] Update focused tests.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further
      investigation.

## Deliverables
- real ACL profiles package
- explicit named profile modules
- focused tests

## Files / Paths Impacted
- src/melder/aether/nexus/acl/profiles/
- src/melder/aether/nexus/frame_acl_manager.py
- src/melder/aether/nexus/nexus.py
- tests/unit/melder/aether/test_frame_acl_profile.py
- tests/unit/melder/aether/test_frame_acl_manager.py
- tests/unit/melder/aether/test_nexus_frame_acl_profiles.py

## Validation
- Completed:
  - `python -m py_compile src/melder/aether/nexus/acl/profiles/frame_acl_rule.py src/melder/aether/nexus/acl/profiles/frame_acl_ruleset.py src/melder/aether/nexus/acl/profiles/frame_acl_view_profile.py src/melder/aether/nexus/acl/profiles/frame_acl_codegen_profile.py src/melder/aether/nexus/acl/profiles/frame_acl_profile.py src/melder/aether/nexus/acl/profiles/frame_acl_profile_builder.py src/melder/aether/nexus/acl/profiles/view/safe_profile.py src/melder/aether/nexus/acl/profiles/view/hybrid_profile.py src/melder/aether/nexus/acl/profiles/view/permissive_profile.py src/melder/aether/nexus/acl/profiles/codegen/safe_profile.py src/melder/aether/nexus/acl/profiles/codegen/hybrid_profile.py src/melder/aether/nexus/acl/profiles/codegen/permissive_profile.py src/melder/aether/nexus/frame_acl_manager.py src/melder/aether/nexus/nexus.py src/melder/aether/nexus/acl/frame_acl_configuration.py src/melder/aether/nexus/acl/frame_acl_builder.py src/melder/aether/nexus/acl/frame_acl_view_configuration.py src/melder/aether/nexus/acl/frame_acl_codegen_configuration.py src/melder/aether/nexus/acl/frame_acl_validator.py tests/unit/melder/aether/test_frame_acl_profile.py tests/unit/melder/aether/test_frame_acl_builder.py tests/unit/melder/aether/test_frame_acl_configuration.py tests/unit/melder/aether/test_frame_acl_container.py tests/unit/melder/aether/test_frame_acl_validator.py tests/unit/melder/aether/test_nexus_frame_acl_profiles.py`
  - `python -m pytest -q tests/unit/melder/aether/test_frame_acl_profile.py tests/unit/melder/aether/test_frame_acl_builder.py tests/unit/melder/aether/test_frame_acl_configuration.py tests/unit/melder/aether/test_frame_acl_container.py tests/unit/melder/aether/test_frame_acl_validator.py tests/unit/melder/aether/test_nexus_frame_acl_profiles.py`

## Risks / Rollback Notes
- Risk: import churn leaks into unrelated ACL layers.
  Rollback: keep the refactor bounded to the reusable profile catalog surface.

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
  - system_docs/patches/active/frame_acl_profile_catalog_refactor/architecture_patch.md
  - system_docs/patches/active/frame_acl_profile_catalog_refactor/component_patch_acl_profiles_package.md
  - system_docs/patches/active/frame_acl_profile_catalog_refactor/component_patch_frame_acl_manager.md
  - system_docs/patches/active/frame_acl_profile_catalog_refactor/code_description_patch_acl_profile_catalog.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-06T00:11:45Z
  TYPE: DECISION
  CLAIM: The current ACL profile catalog organization is too hidden. The rules,
    rulesets, builder, and named profiles are real now, but they still live
    inline inside one file. The user explicitly wants them visible as a real
    package with explicit `safe`, `hybrid`, and `permissive` profile objects.
    The next bounded refactor should move the catalog into `acl/profiles/`
    without widening into config/compiler work.
  EVIDENCE:
  - src/melder/aether/nexus/acl/frame_acl_profile.py:370-1957
  - user_instruction: "make a folder for them in ACL called profiles and actually store them somewhere"
  - user_instruction: "I want to see safe_profile, permissive_profile, hybrid profile"
  IMPACT: The catalog becomes inspectable and maintainable instead of being
    hidden inside one implementation file.
  NEXT: create the patch-doc set, then move the catalog into `acl/profiles/`
    and rewire the focused imports/tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T00:11:45Z
  TYPE: PLAN
  CLAIM: The patch-doc consumption mapping for this package-refactor slice is
    now explicit. `architecture_patch.md` maps to keeping the refactor bounded
    to the reusable ACL profile catalog only. The
    `component_patch_acl_profiles_package.md` doc maps to the new
    `acl/profiles/` package layout and explicit named profile modules. The
    `component_patch_frame_acl_manager.md` doc maps to manager/Nexus import
    rewiring. The `code_description_patch_acl_profile_catalog.md` doc maps to
    preserving the existing manager-owned builder behavior while moving the
    catalog into explicit modules.
  EVIDENCE:
  - codex/context_compass/system_docs/patches/active/frame_acl_profile_catalog_refactor/architecture_patch.md:1-19
  - codex/context_compass/system_docs/patches/active/frame_acl_profile_catalog_refactor/component_patch_acl_profiles_package.md:1-13
  - codex/context_compass/system_docs/patches/active/frame_acl_profile_catalog_refactor/component_patch_frame_acl_manager.md:1-13
  - codex/context_compass/system_docs/patches/active/frame_acl_profile_catalog_refactor/code_description_patch_acl_profile_catalog.md:1-12
  IMPACT: The refactor can stay confined to package organization and imports
    without silently widening into config/compiler changes.
  NEXT: sync the artifact board to this task, then move the catalog into the
    real `acl/profiles/` package and update focused imports/tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T00:11:45Z
  TYPE: FACT
  CLAIM: The concrete interface gap in the current ACL catalog is real and
    narrow. The main offender is `FrameACLBuilder.__init__(container: object)`,
    and there are no ACL-specific Protocol contracts yet in the shared
    interfaces file for rules, rulesets, reusable profiles, composed profiles,
    or the builder. So this refactor should not only move the catalog into
    `acl/profiles/`; it should also add and use Protocol contracts for the ACL
    profile layer instead of leaving `object`-typed seams behind.
  EVIDENCE:
  - src/melder/aether/nexus/acl/frame_acl_builder.py:49-49
  - src/melder/utilities/interfaces/interfaces.py:2230-2360
  IMPACT: The package refactor should include ACL-specific Protocols and should
    remove the `object` seam from the builder path.
  NEXT: add ACL profile Protocols in the shared interfaces file, then move the
    catalog into `acl/profiles/` and rewire imports/tests to those protocols.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T00:36:14Z
  TYPE: FACT
  CLAIM: The ACL profile catalog package refactor is landed and green on the
    focused ACL surface. The catalog now lives under `acl/profiles/` with:
    - dedicated rule/ruleset modules
    - dedicated reusable view/codegen profile modules
    - explicit named profile modules under:
      - `profiles/view/`
      - `profiles/codegen/`
    - a dedicated profile builder module
    Runtime and focused tests now import from that package, and there are no
    remaining live imports from the old monolithic ACL profile module.
  EVIDENCE:
  - src/melder/aether/nexus/acl/profiles/frame_acl_rule.py:1-164
  - src/melder/aether/nexus/acl/profiles/frame_acl_ruleset.py:1-207
  - src/melder/aether/nexus/acl/profiles/frame_acl_view_profile.py:1-257
  - src/melder/aether/nexus/acl/profiles/frame_acl_codegen_profile.py:1-159
  - src/melder/aether/nexus/acl/profiles/frame_acl_profile.py:1-151
  - src/melder/aether/nexus/acl/profiles/frame_acl_profile_builder.py:1-257
  - src/melder/aether/nexus/acl/profiles/view/safe_profile.py:1-99
  - src/melder/aether/nexus/acl/profiles/codegen/safe_profile.py:1-77
  - command:python -m pytest -q tests/unit/melder/aether/test_frame_acl_profile.py tests/unit/melder/aether/test_frame_acl_builder.py tests/unit/melder/aether/test_frame_acl_configuration.py tests/unit/melder/aether/test_frame_acl_container.py tests/unit/melder/aether/test_frame_acl_validator.py tests/unit/melder/aether/test_nexus_frame_acl_profiles.py
  IMPACT: The reusable ACL catalog is now physically structured the way the user
    asked for and is easier to inspect and extend.
  NEXT: review whether the next ACL slice should be docstring/quality hardening
    across the new package or move directly into the compiled access surface.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task exists to turn the ACL profile catalog into a real `acl/profiles/`
package with visible named profile modules.



