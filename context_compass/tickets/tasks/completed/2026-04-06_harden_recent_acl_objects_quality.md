# Task: Harden Recent ACL Objects Quality
- Completed: 2026-04-06T12:17:44Z
- Summary: Accepted review slice moved out of the active lane during the 2026-04-06 board cleanup after the user advanced to later ACL/frame-surface work.


## Metadata
- Task ID: TASK-2026-04-06-harden-recent-acl-objects-quality
- Story: STORY-2026-04-02-profile-contracts-and-access-boundaries
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-06T00:36:14Z
- Updated: 2026-04-06T12:17:44Z

## Objective
Raise the recent ACL files to the repo’s required quality bar by fixing rich
docstrings, moving `cleanup()` directly under `__init__` where applicable, and
adding lock discipline where grouped mutation or teardown can race in a nogil
runtime.

## Ticket Contract
- ENTRY_GATE: the recent ACL profile/package/config slices are landed and the
  user explicitly called out missing docstrings, cleanup placement, and weak
  thread-safety posture.
- EXECUTION_BOUNDARY: ACL quality hardening only.
- DEPENDENCIES:
  - src/melder/aether/nexus/acl/
  - src/melder/aether/nexus/acl/profiles/
  - src/melder/aether/nexus/frame_acl_manager.py
- EXIT_GATE: touched ACL files have contract-grade docstrings, cleanup ordering
  follows repo rules, and lock usage is justified for grouped mutation/teardown
  only.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the hardening pass exposes a
  deeper ACL contract problem rather than just quality debt.

## Scope Boundaries
- In scope:
  - recent ACL profile package files
  - recent typed ACL config/builder/validator files
  - focused ACL tests as needed for behavioral hardening
- Out of scope:
  - new ACL features
  - compiled access surface
  - viewer integration

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: the task was turned in during the cleanup pass after the user advanced to later ACL/frame-surface work.
## Steps / Checklist
- [x] Harden rich docstrings on touched ACL classes and methods.
- [x] Move `cleanup()` directly under `__init__` where required.
- [x] Add/adjust locks only where grouped mutation or teardown needs them.
- [x] Update focused tests if behavior changes.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further
      investigation.

## Deliverables
- hardened ACL object files
- focused validation

## Files / Paths Impacted
- src/melder/aether/nexus/acl/
- src/melder/aether/nexus/acl/profiles/
- src/melder/aether/nexus/frame_acl_manager.py
- tests/unit/melder/aether/

## Validation
- Completed:
  - `python -m py_compile src/melder/aether/nexus/acl/frame_acl_view_configuration.py src/melder/aether/nexus/acl/frame_acl_codegen_configuration.py src/melder/aether/nexus/acl/frame_acl_builder.py src/melder/aether/nexus/acl/profiles/frame_acl_view_profile.py src/melder/aether/nexus/acl/profiles/frame_acl_codegen_profile.py src/melder/aether/nexus/acl/profiles/frame_acl_profile.py src/melder/aether/nexus/acl/profiles/frame_acl_profile_builder.py src/melder/aether/nexus/acl/frame_acl_configuration.py src/melder/aether/nexus/acl/frame_acl_validator.py`
  - `python -m pytest -q tests/unit/melder/aether/test_frame_acl_profile.py tests/unit/melder/aether/test_frame_acl_builder.py tests/unit/melder/aether/test_frame_acl_configuration.py tests/unit/melder/aether/test_frame_acl_container.py tests/unit/melder/aether/test_frame_acl_validator.py tests/unit/melder/aether/test_nexus_frame_acl_profiles.py`

## Risks / Rollback Notes
- Risk: adding locks indiscriminately makes the design worse.
  Rollback: only keep locks where grouped mutation/cleanup or multi-step state
  transitions need them.

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
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-06T00:36:14Z
  TYPE: FACT
  CLAIM: The recent ACL objects are below the repo’s documentation and
    concurrency bar. The package refactor and typed configuration slices landed,
    but the current files still have weak/minimal method docstrings, some
    classes still do not place `cleanup()` directly under `__init__`, and lock
    usage needs a deliberate pass in light of nogil semantics.
  EVIDENCE:
  - src/melder/aether/nexus/acl/frame_acl_view_configuration.py:1-212
  - src/melder/aether/nexus/acl/frame_acl_codegen_configuration.py:1-204
  - src/melder/aether/nexus/acl/frame_acl_builder.py:1-184
  - src/melder/aether/nexus/acl/profiles/frame_acl_view_profile.py:1-257
  - user_instruction: "Also in all the systems you made and things you made there are almost no docstrings fix that shit"
  - user_instruction: "cleanup should also be positioned below init in all objects"
  - user_instruction: "locks are required when grouped mutations happen"
  IMPACT: The next ACL slice should be quality hardening, not more feature work.
  NEXT: inspect the recent ACL files one-by-one and harden docstrings,
    cleanup ordering, and lock usage where justified.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T00:36:14Z
  TYPE: FACT
  CLAIM: The quality debt is now concrete rather than vague. The ACL package
    refactor is structurally fine, but the new ACL files still have:
    - many terse/minimal property and helper docstrings
    - `cleanup()` placed after classmethods or later methods in several files
    - missing grouped-state locks in the typed config objects where multiple
      fields are mutated or torn down together in a nogil runtime
    - at least one weak seam that still needed an interface-first cleanup
      (`FrameACLBuilder.__init__(container: object)`, already identified)
  EVIDENCE:
  - src/melder/aether/nexus/acl/frame_acl_view_configuration.py:1-212
  - src/melder/aether/nexus/acl/frame_acl_codegen_configuration.py:1-204
  - src/melder/aether/nexus/acl/frame_acl_configuration.py:1-364
  - src/melder/aether/nexus/acl/frame_acl_builder.py:1-184
  - src/melder/aether/nexus/acl/profiles/frame_acl_view_profile.py:1-257
  - src/melder/aether/nexus/acl/profiles/frame_acl_profile_builder.py:1-257
  IMPACT: The hardening pass needs to touch the typed config layer and the new
    profiles package, not just one file.
  NEXT: harden the typed config files first (`FrameACLViewConfiguration`,
    `FrameACLCodegenConfiguration`, `FrameACLConfiguration`, `FrameACLBuilder`),
    then the package files.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T00:36:14Z
  TYPE: MEASURE
  CLAIM: The ACL hardening pass is green on the focused ACL surface. The typed
    config/builder files were rewritten with richer contract docstrings,
    cleanup placement directly under `__init__`, and lock usage around grouped
    mutation/cleanup where justified in a nogil runtime. The reusable profile
    package was also pointed at Protocol-friendly seams and the focused ACL
    test surface still passed with 50 tests.
  EVIDENCE:
  - src/melder/aether/nexus/acl/frame_acl_view_configuration.py:1-212
  - src/melder/aether/nexus/acl/frame_acl_codegen_configuration.py:1-204
  - src/melder/aether/nexus/acl/frame_acl_builder.py:1-214
  - src/melder/aether/nexus/acl/profiles/frame_acl_view_profile.py:1-294
  - src/melder/aether/nexus/acl/profiles/frame_acl_codegen_profile.py:1-196
  - src/melder/aether/nexus/acl/profiles/frame_acl_profile.py:1-151
  - src/melder/aether/nexus/acl/profiles/frame_acl_profile_builder.py:1-266
  - command:python -m pytest -q tests/unit/melder/aether/test_frame_acl_profile.py tests/unit/melder/aether/test_frame_acl_builder.py tests/unit/melder/aether/test_frame_acl_configuration.py tests/unit/melder/aether/test_frame_acl_container.py tests/unit/melder/aether/test_frame_acl_validator.py tests/unit/melder/aether/test_nexus_frame_acl_profiles.py
  IMPACT: The recent ACL files are no longer carrying the obvious quality debt
    the user called out, and the next ACL slice can focus back on behavior.
  NEXT: review whether the next ACL slice should be the compiled access surface
    or another targeted ACL contract fix.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task exists to bring the recent ACL files up to the repo’s docstring,
cleanup, and thread-safety standard.



