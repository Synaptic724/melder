# Story: Frame ACL Typed Configuration Foundation

## Metadata
- Story ID: STORY-2026-04-05-frame-acl-typed-configuration-foundation
- Epic: EPIC-2026-04-02-rift-profile-surface-and-access-model
- Status: in_progress
- Owner: codex
- Priority: p0
- Created: 2026-04-05T23:51:00Z
- Updated: 2026-04-05T23:51:00Z

## User Narrative
As the project owner, I want the frame-local ACL configuration layer moved off
raw JSON strings and onto typed configuration objects, so the ACL system can
apply the named reusable profiles cleanly and validate them against descriptor
payloads later.

## Value / MRP Alignment
This is the next MRP ACL boundary. The reusable profile substrate is real now,
but the frame-local applied configuration is still a JSON holder. If we do not
replace that now, later validator/compiler work will be forced to translate
through a weak intermediate model.

## Ticket Contract
- ENTRY_GATE: the ACL profile builder/library foundation and named reusable
  profile catalog are landed and the user explicitly asked to continue.
- EXECUTION_BOUNDARY: typed `FrameACLConfiguration`, typed view/codegen child
  configuration objects, builder rewrite, and focused ACL tests only.
- DEPENDENCIES:
  - tickets/tasks/2026-04-05_implement_frame_acl_profile_builder_foundation.md
  - tickets/tasks/2026-04-05_implement_frame_acl_safe_default_profiles_task.md
  - tickets/tasks/2026-04-02_design_profile_contracts_and_access_boundaries_task.md
  - tickets/artifacts/nexus_acl_builder_and_persistence_model.md
- EXIT_GATE: `FrameACLConfiguration` is typed, `FrameACLBuilder` edits typed
  configuration objects instead of JSON strings, and focused validation passes.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if this slice forces the full
  descriptor-backed ACL validator/compiler rewrite immediately.

## Requirements (Functional)
- add typed `FrameACLViewConfiguration`
- add typed `FrameACLCodegenConfiguration`
- make `FrameACLConfiguration` a typed root object
- rework `FrameACLBuilder` to edit typed configuration objects
- keep chain/container ownership intact

## Requirements (Non-Functional)
- preserve current history/rollback shell
- keep configuration serializable for persistence
- stay aligned with the payload-backed descriptor contract

## Scope Boundaries
- In scope:
  - typed ACL configuration classes
  - typed builder draft flow
  - focused configuration/builder/container tests
- Out of scope:
  - full descriptor-backed validator rewrite
  - compiled access surface
  - viewer integration
  - spellbook-level authored selectors

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the ACL reusable profile substrate is landed and the next
  bounded slice is the typed applied configuration layer.

## Tasks (Implementation Checklist)
- [ ] Task: TASK-2026-04-05-implement-frame-acl-typed-configuration-foundation - implement the typed configuration layer
- [ ] Keep the design task/artifact aligned to the typed configuration result.
- [ ] Enforce Ticket Microcycle across the linked task.

## Acceptance Criteria
- typed `FrameACLViewConfiguration` exists
- typed `FrameACLCodegenConfiguration` exists
- `FrameACLConfiguration` uses typed child configuration objects
- `FrameACLBuilder` edits typed configuration objects instead of raw JSON
- focused ACL tests pass

## Validation / Test Plan
- focused ACL configuration, builder, validator, and container unit tests
- no broader ACL/compiler integration sweep in this story by default

## Risks / Mitigations
- Risk: the typed config slice widens into validator/compiler work too early.
  Mitigation: keep this story bounded to applied configuration plus builder
  draft flow.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- whether configuration serialization should persist all effective rulesets or
  preserve a smaller profile+override representation

## Decision Log
- pending

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: n/a

## Notes
- DATETIME: 2026-04-05T23:51:00Z
  TYPE: DECISION
  CLAIM: The next ACL tranche should be the typed applied configuration layer.
    The reusable profile side is already landed, but `FrameACLConfiguration`
    and `FrameACLBuilder` are still a JSON-string model. The correct bounded
    next step is to add typed `FrameACLViewConfiguration` and
    `FrameACLCodegenConfiguration`, make `FrameACLConfiguration` the typed root
    that owns them, and rework the builder to draft typed objects instead of raw
    JSON payload strings.
  EVIDENCE:
  - src/melder/aether/nexus/acl/frame_acl_configuration.py:10-444
  - src/melder/aether/nexus/acl/frame_acl_builder.py:10-192
  - codex/context_compass/tickets/tasks/2026-04-02_design_profile_contracts_and_access_boundaries_task.md:421-472
  - codex/context_compass/tickets/artifacts/nexus_acl_builder_and_persistence_model.md:274-339
  IMPACT: This gives the ACL lane a clean next slice without forcing the full
    validator/compiler rewrite yet.
  NEXT: create the implementation task and patch-doc set, then land the typed
    configuration classes and builder rewrite.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-06T00:00:41Z
  TYPE: FACT
  CLAIM: The typed applied ACL configuration layer is landed and in review.
    The slice added:
    - `FrameACLViewConfiguration`
    - `FrameACLCodegenConfiguration`
    - typed root `FrameACLConfiguration`
    - typed builder draft/apply/commit behavior
    Focused ACL configuration/builder/container/validator tests passed.
  EVIDENCE:
  - tickets/tasks/2026-04-05_implement_frame_acl_typed_configuration_foundation.md:1-190
  IMPACT: The story has now moved the ACL lane off both major placeholder
    layers:
    reusable profile JSON bags and applied configuration JSON bags.
  NEXT: review whether the next bounded slice should move into the
    descriptor-backed validator/compiler path.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Add notes when typed configuration work pressures validator/compiler scope.
- Reference child-task evidence instead of duplicating tactical detail.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
This story exists to land the typed applied ACL configuration layer on top of
the reusable named profile catalog.
