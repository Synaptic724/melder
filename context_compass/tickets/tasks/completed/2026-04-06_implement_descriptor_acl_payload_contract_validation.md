# Task: Implement Descriptor ACL Payload Contract Validation
- Completed: 2026-04-09T11:31:39Z
- Summary: Made descriptor payload contracts explicit and gated viewer projection on descriptor-aware ACL validation.


## Metadata
- Task ID: TASK-2026-04-06-implement-descriptor-acl-payload-contract-validation
- Story: STORY-2026-04-06-validate-descriptor-acl-payload-contracts-and-collapse-frame-view
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-06T16:52:25Z
- Updated: 2026-04-09T11:31:39Z

## Objective
Make descriptor payload contracts explicit and validate them against the chosen
ACL configuration before viewer creation or other consumer-facing projection.

## Ticket Contract
- ENTRY_GATE: the impact investigation is accepted and the implementation order
  still starts with payload validation.
- EXECUTION_BOUNDARY: descriptor payload contract identity and ACL validation
  only.
- DEPENDENCIES:
  - tickets/tasks/2026-04-06_investigate_frame_view_removal_impacts_and_payload_contract_gates.md
  - src/melder/aether/nexus/frame_descriptor/
  - src/melder/aether/nexus/acl/frame_acl_view_configuration.py
  - src/melder/aether/nexus/acl/frame_acl_validator.py
  - src/melder/aether/nexus/frame_descriptor_manager.py
  - src/melder/aether/nexus/nexus.py
- EXIT_GATE: descriptor payload contracts are explicit, mismatches raise, and
  viewer creation is gated on successful validation.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the descriptor substrate
  cannot express the needed payload contract without a larger redesign.

## Scope Boundaries
- In scope:
  - payload contract identity/version fields
  - ACL-side required payload contract fields
  - validator wiring
  - viewer-creation gate
  - focused tests
- Out of scope:
  - `FrameView` removal
  - viewer runtime simplification
  - codegen behavior

## Steps / Checklist
- [ ] Define payload contract identity on descriptor payloads.
- [ ] Extend ACL view configuration with required payload contract fields.
- [ ] Extend validator to compare descriptor truth to ACL requirements.
- [ ] Gate viewer creation on successful validation.
- [ ] Add/update focused tests.

## Deliverables
- explicit payload contract fields
- descriptor<->ACL validation
- focused tests

## Validation
- Completed:
  - `python -m py_compile <local-workspace>\src\melder\utilities\interfaces\interfaces.py <local-workspace>\src\melder\spellbook\spell_crafter\spell_examiner\profiles\general_profile.py <local-workspace>\src\melder\spellbook\spell_crafter\spell_examiner\profiles\detailed_profile.py <local-workspace>\src\melder\aether\nexus\frame_descriptor\spell_descriptor_payload.py <local-workspace>\src\melder\aether\nexus\frame_descriptor\conduit_descriptor_payload.py <local-workspace>\src\melder\aether\nexus\frame_descriptor\frame_descriptor_payload.py <local-workspace>\src\melder\aether\nexus\acl\profiles\frame_acl_view_profile.py <local-workspace>\src\melder\aether\nexus\acl\frame_acl_view_configuration.py <local-workspace>\src\melder\aether\nexus\acl\frame_acl_validator.py <local-workspace>\src\melder\aether\nexus\frame_descriptor_manager.py <local-workspace>\src\melder\aether\nexus\frame_acl_manager.py <local-workspace>\src\melder\aether\nexus\nexus.py <local-workspace>\tests\unit\melder\aether\test_frame_acl_profile.py <local-workspace>\tests\unit\melder\aether\test_frame_acl_validator.py <local-workspace>\tests\unit\melder\aether\test_nexus_frame_surface_projection.py`
  - `python -m pytest -q tests\unit\melder\aether\test_frame_acl_profile.py tests\unit\melder\aether\test_frame_acl_validator.py tests\unit\melder\aether\test_nexus_frame_surface_projection.py`
  - `python -m pytest -q tests\unit\melder\aether\test_frame_acl_configuration.py tests\unit\melder\aether\test_frame_acl_container.py tests\unit\melder\aether\test_frame_acl_manager.py tests\unit\melder\aether\test_frame_acl_profile.py tests\unit\melder\aether\test_frame_acl_validator.py tests\unit\melder\aether\test_nexus_frame_surface_projection.py`

## Notes
- DATETIME: 2026-04-06T16:52:25Z
  TYPE: PLAN
  CLAIM: This task must land before `FrameView` removal because the current
    system still relies on a weak string-mapped payload contract.
  EVIDENCE:
  - tickets/tasks/2026-04-06_investigate_frame_view_removal_impacts_and_payload_contract_gates.md:1-125
  IMPACT: The viewer-collapse task should remain blocked until this task is
    complete.
  NEXT: wait for acceptance of the investigation pass, then implement payload
    contract validation first.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-06T17:05:00Z
  TYPE: FACT
  CLAIM: The implementation path is now concrete. The current validator is only
    structural and is called during container insert/commit. The descriptor
    payload interfaces only require `profile_name`, not `profile_version`, and
    the spell profile objects also only expose `profile_name`. So the first
    payload-validation tranche needs to:
    1) make payload version part of the descriptor contract
    2) extend `FrameACLViewConfiguration` / `FrameACLViewProfile` with explicit
       payload contract expectations
    3) add descriptor-aware validation on top of the current structural ACL
       validation
    4) gate `Nexus.create_frame_view(...)` on that descriptor-aware validation
  EVIDENCE:
  - src/melder/utilities/interfaces/interfaces.py:2170-2279
  - src/melder/spellbook/spell_crafter/spell_examiner/profiles/general_profile.py:26-150
  - src/melder/spellbook/spell_crafter/spell_examiner/profiles/detailed_profile.py:30-236
  - src/melder/aether/nexus/acl/frame_acl_validator.py:17-258
  - src/melder/aether/nexus/frame_acl_manager.py:434-468
  - src/melder/aether/nexus/nexus.py:1477-1660
  IMPACT: The implementation scope is now precise enough to patch without
    guessing.
  NEXT: patch payload/version identity into spell/frame/conduit payloads and
    the ACL view config/profile surface first.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T17:11:00Z
  TYPE: FACT
  CLAIM: The payload-contract validation slice is now in code. Descriptor
    payloads and spell profiles now carry `profile_version`, ACL view
    profiles/configurations now carry explicit required frame/conduit payload
    contracts plus a versioned minimum spell payload floor, the ACL validator
    can now validate a configuration against `FrameDescriptor` truth, the
    descriptor manager rejects unsupported published payload contracts, and
    `Nexus.create_frame_view(...)` now gates projection on that
    descriptor-aware validation before compile/cache return.
  EVIDENCE:
  - src/melder/utilities/interfaces/interfaces.py:2170-2279
  - src/melder/spellbook/spell_crafter/spell_examiner/profiles/general_profile.py:26-180
  - src/melder/spellbook/spell_crafter/spell_examiner/profiles/detailed_profile.py:30-236
  - src/melder/aether/nexus/frame_descriptor/spell_descriptor_payload.py:77-222
  - src/melder/aether/nexus/frame_descriptor/conduit_descriptor_payload.py:9-79
  - src/melder/aether/nexus/frame_descriptor/frame_descriptor_payload.py:8-109
  - src/melder/aether/nexus/acl/profiles/frame_acl_view_profile.py:11-259
  - src/melder/aether/nexus/acl/frame_acl_view_configuration.py:14-392
  - src/melder/aether/nexus/acl/frame_acl_validator.py:17-481
  - src/melder/aether/nexus/frame_descriptor_manager.py:30-774
  - src/melder/aether/nexus/frame_acl_manager.py:25-585
  - src/melder/aether/nexus/nexus.py:1477-1522
  IMPACT: The descriptor and ACL layers now have a real contract gate instead
    of only a loose string-section match.
  NEXT: run the focused compile/validator/projection tests and confirm the
    first tranche is stable enough to review before removing `FrameView`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T17:11:00Z
  TYPE: MEASURE
  CLAIM: The focused payload-contract tranche is green. The compile sanity
    pass succeeded on the touched source/test files, and the focused pytest
    slice covering ACL profiles, ACL validator behavior, and the Nexus
    projection gate passed cleanly with 39 tests green. The only warnings were
    the known GIL-enabled runtime warning and pytest cache access-denied noise.
  EVIDENCE:
  - tests/unit/melder/aether/test_frame_acl_profile.py:1-270
  - tests/unit/melder/aether/test_frame_acl_validator.py:1-401
  - tests/unit/melder/aether/test_nexus_frame_surface_projection.py:1-380
  - command:python -m py_compile <local-workspace>\src\melder\utilities\interfaces\interfaces.py <local-workspace>\src\melder\spellbook\spell_crafter\spell_examiner\profiles\general_profile.py <local-workspace>\src\melder\spellbook\spell_crafter\spell_examiner\profiles\detailed_profile.py <local-workspace>\src\melder\aether\nexus\frame_descriptor\spell_descriptor_payload.py <local-workspace>\src\melder\aether\nexus\frame_descriptor\conduit_descriptor_payload.py <local-workspace>\src\melder\aether\nexus\frame_descriptor\frame_descriptor_payload.py <local-workspace>\src\melder\aether\nexus\acl\profiles\frame_acl_view_profile.py <local-workspace>\src\melder\aether\nexus\acl\frame_acl_view_configuration.py <local-workspace>\src\melder\aether\nexus\acl\frame_acl_validator.py <local-workspace>\src\melder\aether\nexus\frame_descriptor_manager.py <local-workspace>\src\melder\aether\nexus\frame_acl_manager.py <local-workspace>\src\melder\aether\nexus\nexus.py <local-workspace>\tests\unit\melder\aether\test_frame_acl_profile.py <local-workspace>\tests\unit\melder\aether\test_frame_acl_validator.py <local-workspace>\tests\unit\melder\aether\test_nexus_frame_surface_projection.py
  - command:python -m pytest -q tests\unit\melder\aether\test_frame_acl_profile.py tests\unit\melder\aether\test_frame_acl_validator.py tests\unit\melder\aether\test_nexus_frame_surface_projection.py
  IMPACT: The first ordered tranche is stable enough to stop and review before
    starting the `FrameView` removal cut.
  NEXT: review this payload-validation slice with the user, then proceed to
    `FrameView` removal only if accepted.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T17:14:00Z
  TYPE: MEASURE
  CLAIM: The broader ACL typed-config slice is also green after the payload
    contract additions. The wider unit run covering ACL configuration,
    container, manager, profile, validator, and Nexus frame-surface projection
    all passed cleanly with 72 tests green. The warnings were unchanged and
    non-blocking.
  EVIDENCE:
  - tests/unit/melder/aether/test_frame_acl_configuration.py:1-340
  - tests/unit/melder/aether/test_frame_acl_container.py:1-250
  - tests/unit/melder/aether/test_frame_acl_manager.py:1-330
  - tests/unit/melder/aether/test_frame_acl_profile.py:1-270
  - tests/unit/melder/aether/test_frame_acl_validator.py:1-401
  - tests/unit/melder/aether/test_nexus_frame_surface_projection.py:1-380
  - command:python -m pytest -q tests\unit\melder\aether\test_frame_acl_configuration.py tests\unit\melder\aether\test_frame_acl_container.py tests\unit\melder\aether\test_frame_acl_manager.py tests\unit\melder\aether\test_frame_acl_profile.py tests\unit\melder\aether\test_frame_acl_validator.py tests\unit\melder\aether\test_nexus_frame_surface_projection.py
  IMPACT: The payload-contract additions did not just pass the narrow validator
    slice; they also held across the typed ACL configuration shell objects.
  NEXT: stop at this tranche boundary and wait for approval before starting the
    `FrameView` removal cut.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
The first implementation task is now complete and ready for review. The next
ordered slice is `FrameView` removal and direct `FrameViewer` rewiring.

