# Story: Frame ACL Compiled Access Surface

## Metadata
- Story ID: STORY-2026-04-06-frame-acl-compiled-access-surface
- Epic: EPIC-2026-04-02-rift-profile-surface-and-access-model
- Status: in_progress
- Owner: codex
- Priority: p0
- Created: 2026-04-06T00:11:45Z
- Updated: 2026-04-06T00:11:45Z

## User Narrative
As the project owner, I want the ACL system to compile typed configuration over
payload-backed descriptor records into a downstream access surface, so
`FrameLinkContract` and later viewer/codegen consumers receive effective
answers instead of raw config.

## Value / MRP Alignment
This is the first real consumer-facing ACL output layer. Without it, the ACL
system still stops at config and validation and cannot feed the frame/view
surface meaningfully.

## Ticket Contract
- ENTRY_GATE: typed ACL config and rule-aware validator are landed.
- EXECUTION_BOUNDARY: compiled access surface and compiler only.
- DEPENDENCIES:
  - TASK-2026-04-05-implement-frame-acl-typed-configuration-foundation
  - TASK-2026-04-06-implement-frame-acl-validator-rule-validation
  - src/melder/aether/nexus/frame_descriptor/frame_descriptor.py
  - src/melder/aether/nexus/rift/frame_link/frame_link_contract.py
- EXIT_GATE: one compiled ACL access surface exists over payload-backed
  descriptor records and focused validation passes.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if downstream `FrameLinkContract`
  requirements force a larger viewer-model redesign first.

## Scope Boundaries
- In scope:
  - compiled access surface object
  - compiler over frame/conduit/spell descriptor payloads
  - frame-link contract shaping input
- Out of scope:
  - full viewer implementation
  - live event/update wiring
  - codegen executor integration

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the ACL lane now has enough upstream substrate that the
  next bounded step is compiled access output.

## Tasks (Implementation Checklist)
- [ ] Task: TASK-2026-04-06-implement-frame-acl-compiled-access-surface - implement the compiler and compiled surface
- [ ] Keep the design task/artifact aligned to the compiled surface model.
- [ ] Enforce Ticket Microcycle across the linked task.

## Acceptance Criteria
- compiled ACL access surface object exists
- compiler consumes payload-backed descriptor records plus typed ACL config
- output is suitable to feed `FrameLinkContract`
- focused tests pass

## Validation / Test Plan
- focused compiler/access-surface tests
- no viewer integration sweep in this story by default

## Risks / Mitigations
- Risk: compiled surface leaks raw config instead of effective answers.
  Mitigation: keep it as derived sets/maps/flags only.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- exact mapping between compiled surface and `FrameLinkContract` fields

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
  CLAIM: The next bounded ACL tranche after typed config + validator is the
    compiled access surface over payload-backed descriptor records. The current
    downstream placeholders already tell us the consumer direction:
    `FrameLinkContract` wants effective allowed kinds/commands/metadata, not
    raw ACL config. So the next slice should compile typed ACL config against
    `FrameDescriptor` record payloads into one downstream-facing access surface.
  EVIDENCE:
  - src/melder/aether/nexus/rift/frame_link/frame_link_contract.py:1-138
  - src/melder/aether/nexus/rift/frame_link/frame_link.py:1-164
  - src/melder/aether/nexus/rift/frame_viewer/frame_view.py:1-126
  - user_instruction: "go ahead and do all that stuff"
  IMPACT: The ACL lane now has its next concrete implementation target after the
    current validator slice.
  NEXT: create the compiler task/patch set, then implement the compiled access
    surface over payload-backed descriptor records.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Add notes when compiled-surface scope pressures move into viewer/event work.
- Reference child-task evidence instead of duplicating tactical detail.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
This story exists to compile typed ACL configuration over payload-backed
descriptor records into a downstream access surface for frame-link consumers.
