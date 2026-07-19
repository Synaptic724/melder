# Task: Implement Frame ACL Validator Rule Validation
- Completed: 2026-04-06T12:17:44Z
- Summary: Accepted review slice moved out of the active lane during the 2026-04-06 board cleanup after the user advanced to later ACL/frame-surface work.


## Metadata
- Task ID: TASK-2026-04-06-implement-frame-acl-validator-rule-validation
- Story: STORY-2026-04-06-frame-acl-validator-rule-validation
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-06T00:11:45Z
- Updated: 2026-04-06T12:17:44Z

## Objective
Implement rule-aware validation in `FrameACLValidator` for the typed ACL
configuration layer.

## Ticket Contract
- ENTRY_GATE: typed ACL configuration is landed and the user explicitly asked
  for rule-aware validation.
- EXECUTION_BOUNDARY: validator enhancement for typed config/rules only.
- DEPENDENCIES:
  - tickets/tasks/2026-04-05_implement_frame_acl_typed_configuration_foundation.md
  - src/melder/aether/nexus/acl/frame_acl_validator.py
  - src/melder/aether/nexus/acl/frame_acl_configuration.py
  - src/melder/aether/nexus/acl/frame_acl_profile.py
- EXIT_GATE: validator checks typed config child objects, ruleset operation
  families, and supported spell payload floor values; focused tests pass.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if descriptor-backed selector or
  payload validation becomes mandatory for this slice.

## Scope Boundaries
- In scope:
  - typed config structural validation
  - ruleset operation-family validation
  - minimum spell payload floor validation
  - focused validator/config/container tests
- Out of scope:
  - descriptor-backed selector validation
  - member-name existence validation
  - compiled access surface

## State Transition Event
- from_state: review
- to_state: done
- transition_reason: the task was turned in during the cleanup pass after the user advanced to later ACL/frame-surface work.
## Steps / Checklist
- [x] Implement rule-aware validation for typed child configuration objects.
- [x] Implement allowed-operation validation per ruleset family.
- [x] Implement supported payload-floor validation.
- [x] Update focused tests.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further
      investigation.

## Deliverables
- enhanced `FrameACLValidator`
- focused tests

## Files / Paths Impacted
- src/melder/aether/nexus/acl/frame_acl_validator.py
- tests/unit/melder/aether/test_frame_acl_validator.py
- tests/unit/melder/aether/test_frame_acl_container.py

## Validation
- Completed:
  - `python -m py_compile src/melder/aether/nexus/acl/frame_acl_validator.py tests/unit/melder/aether/test_frame_acl_validator.py tests/unit/melder/aether/test_frame_acl_container.py`
  - `python -m pytest -q tests/unit/melder/aether/test_frame_acl_validator.py tests/unit/melder/aether/test_frame_acl_container.py`

## Risks / Rollback Notes
- Risk: the validator enhancement silently grows into descriptor-backed runtime
  evaluation.
  Rollback: keep checks confined to typed configuration structure and rule
  family placement.

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
  - system_docs/patches/active/frame_acl_validator_rules/architecture_patch.md
  - system_docs/patches/active/frame_acl_validator_rules/component_patch_frame_acl_validator.md
  - system_docs/patches/active/frame_acl_validator_rules/code_description_patch_frame_acl_validator.md
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-06T00:11:45Z
  TYPE: PLAN
  CLAIM: The validator is still effectively a frame-name check only. The next
    bounded improvement is to validate the typed configuration we already made:
    - correct typed child config objects
    - allowed operations in the right ruleset families
    - supported spell payload floor values
    without widening yet into descriptor-backed selector/payload validation.
  EVIDENCE:
  - src/melder/aether/nexus/acl/frame_acl_validator.py:10-116
  - src/melder/aether/nexus/acl/frame_acl_view_configuration.py:13-212
  - src/melder/aether/nexus/acl/frame_acl_codegen_configuration.py:13-204
  IMPACT: This is the next clean enforcement step on the typed ACL layer.
  NEXT: create the patch-doc set, then implement the validator checks and align
    focused tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T00:11:45Z
  TYPE: DECISION
  CLAIM: The validator should behave like an active safety test on the typed
    configuration we created, not just a passive type check. So this slice
    should validate:
    1) typed child configuration presence
    2) ruleset-family operation placement
    3) supported spell payload floor values
    4) the seeded `safe` profile assumptions themselves, so if those defaults
       are widened in the wrong places the validator flags it immediately
    This stays short of descriptor-backed selector/member existence validation,
    but it is more than frame-name matching.
  EVIDENCE:
  - user_instruction: "it should be considered like an active test on the config you made so its safe and reasonable"
  - user_instruction: "if specific things are disabled or done wrong it should flag it"
  - src/melder/aether/nexus/acl/frame_acl_profile.py:683-1084
  IMPACT: The validator slice should include semantic checks for the seeded safe
    profile contract, not just generic structural checks.
  NEXT: implement rule-family validation and safe-profile guardrail checks in
    `FrameACLValidator`, then extend focused tests to cover those failures.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T00:15:58Z
  TYPE: FACT
  CLAIM: The validator enhancement is now implemented in code. `FrameACLValidator`
    now validates:
    - typed view/codegen child configuration objects
    - allowed operations per ruleset family
    - supported spell payload floor values
    - safe-profile override guardrails so forbidden operations are not widened
      back open through overrides
    The focused validator and container tests are aligned to that behavior.
  EVIDENCE:
  - src/melder/aether/nexus/acl/frame_acl_validator.py:1-479
  - tests/unit/melder/aether/test_frame_acl_validator.py:1-257
  - tests/unit/melder/aether/test_frame_acl_container.py:1-173
  IMPACT: The typed ACL configuration layer now has a real active validator
    instead of just a frame-name check.
  NEXT: run focused validation and then route the next bounded ACL tranche.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T00:15:58Z
  TYPE: MEASURE
  CLAIM: The rule-aware ACL validator slice is green on the focused validator
    surface. `py_compile` passed on the touched validator and test files, and
    the focused pytest slice passed with 18 tests.
  EVIDENCE:
  - command:python -m pytest -q tests/unit/melder/aether/test_frame_acl_validator.py tests/unit/melder/aether/test_frame_acl_container.py
  IMPACT: The ACL lane now has typed reusable profiles, typed applied config,
    and an active rule-aware validator.
  NEXT: route the next bounded ACL tranche for the compiled access surface over
    payload-backed descriptor records.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task exists to make the ACL validator rule-aware on top of the typed ACL
configuration layer.



