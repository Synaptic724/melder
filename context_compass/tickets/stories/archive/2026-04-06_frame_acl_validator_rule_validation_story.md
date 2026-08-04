# Story: Frame ACL Validator Rule Validation

## Metadata
- Story ID: STORY-2026-04-06-frame-acl-validator-rule-validation
- Epic: EPIC-2026-04-02-rift-profile-surface-and-access-model
- Status: in_progress
- Owner: codex
- Priority: p0
- Created: 2026-04-06T00:11:45Z
- Updated: 2026-04-06T00:11:45Z

## User Narrative
As the project owner, I want the ACL validator to validate the typed
configuration and its rules, so applied ACL config is not treated as valid just
because the frame name matches.

## Value / MRP Alignment
This is the first real enforcement layer on the typed ACL config model. Without
it, the system still accepts structurally wrong rule placements and the typed
config layer is only partially meaningful.

## Ticket Contract
- ENTRY_GATE: the typed ACL configuration layer is landed and the user
  explicitly requested rule-aware validation.
- EXECUTION_BOUNDARY: validator enhancement for typed config/rules only.
- DEPENDENCIES:
  - TASK-2026-04-05-implement-frame-acl-typed-configuration-foundation
  - src/melder/aether/nexus/acl/frame_acl_validator.py
  - src/melder/aether/nexus/acl/frame_acl_configuration.py
- EXIT_GATE: `FrameACLValidator` validates typed child configurations and rule
  placement, and focused tests pass.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if descriptor-backed selector or
  payload validation becomes mandatory for this slice.

## Scope Boundaries
- In scope:
  - rule-aware validation for typed ACL config
  - allowed-operation validation per ruleset family
  - minimum spell payload floor validation
  - focused validator/config/container tests
- Out of scope:
  - descriptor-backed selector validation
  - member-name existence validation
  - compiled access surface

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the typed ACL config layer is landed and the user has
  explicitly requested real rule-aware validation next.

## Tasks (Implementation Checklist)
- [ ] Task: TASK-2026-04-06-implement-frame-acl-validator-rule-validation - implement rule-aware validator checks
- [ ] Keep the design task/artifact aligned to the stronger validator contract.
- [ ] Enforce Ticket Microcycle across the linked task.

## Acceptance Criteria
- `FrameACLValidator` validates typed view/codegen child config objects
- validator rejects unsupported operations in the wrong ruleset family
- validator enforces supported spell payload floor values
- focused tests pass

## Validation / Test Plan
- focused ACL validator tests
- focused container install tests

## Risks / Mitigations
- Risk: validator grows into descriptor-backed policy evaluation too early.
  Mitigation: keep this slice purely structural/rule-family validation.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- whether unsupported operation validation should remain hardcoded in the
  validator or later move into shared config metadata

## Decision Log
- pending

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: n/a

## Notes
- DATETIME: 2026-04-06T00:11:45Z
  TYPE: DECISION
  CLAIM: The next ACL enforcement slice should be rule-aware validator work,
    not the full descriptor-backed compiler path yet. The user explicitly wants
    the validator to validate the typed configuration made from rules. The
    clean bounded version is: validate typed child config presence, validate
    allowed operations per ruleset family, and validate supported
    `minimum_spell_payload_profile_name` values.
  EVIDENCE:
  - src/melder/aether/nexus/acl/frame_acl_validator.py:10-116
  - src/melder/aether/nexus/acl/frame_acl_view_configuration.py:13-212
  - src/melder/aether/nexus/acl/frame_acl_codegen_configuration.py:13-204
  - user_instruction: "the validator should also validate the configuration you made with rules"
  IMPACT: This gives the ACL lane a real enforcement improvement without forcing
    descriptor-backed selector/payload validation yet.
  NEXT: create the implementation task and patch-doc set, then extend
    `FrameACLValidator` and the focused tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Add notes when validator scope pressures move into descriptor-backed
  evaluation.
- Reference child-task evidence instead of duplicating tactical detail.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
This story exists to make the ACL validator rule-aware on top of the landed
typed configuration layer.
