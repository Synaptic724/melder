# Story: Frame ACL Profile Builder Foundation

## Metadata
- Story ID: STORY-2026-04-05-frame-acl-profile-builder-foundation
- Epic: EPIC-2026-04-02-rift-profile-surface-and-access-model
- Status: in_progress
- Owner: codex
- Priority: p0
- Created: 2026-04-05T22:48:24Z
- Updated: 2026-04-05T22:48:24Z

## User Narrative
As the project owner, I want the ACL profile side moved off generic JSON-holder
details and onto a real manager-owned profile builder/library, so view/codegen
profiles can be composed and extended cleanly before deeper ACL configuration
work lands.

## Value / MRP Alignment
This is an MRP foundation slice. If reusable ACL profiles remain ad hoc JSON
bags, the next typed configuration work will start from the wrong substrate and
the ACL system will drift immediately.

## Ticket Contract
- ENTRY_GATE: the ACL design task has rebased onto the payload-backed
  descriptor contract and the user explicitly approved starting the profile
  builder foundation.
- EXECUTION_BOUNDARY: ACL profile builder/library, typed ACL rules/rulesets,
  view/codegen profile objects, manager ownership, and focused tests only.
- DEPENDENCIES:
  - TASK-2026-04-02-design-profile-contracts-and-access-boundaries
  - TASK-2026-04-05-implement-frame-acl-profile-builder-foundation
- EXIT_GATE: `FrameACLManager` owns a real ACL profile builder/library with
  default view/codegen profiles, typed rule/ruleset objects exist, and focused
  validation passes.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if this slice forces
  `FrameACLConfiguration` typed-root implementation earlier than planned.

## Requirements (Functional)
- add a manager-owned ACL profile builder/library similar in spirit to
  `SpellExaminer`
- add typed ACL rule and ruleset objects
- add typed view/codegen profile objects
- add a composed `FrameACLProfile`
- seed default view/codegen profiles automatically

## Requirements (Non-Functional)
- keep the existing manager/container/chain shell intact
- no full ACL configuration rewrite in this story
- keep the foundation extendable for later typed configuration work

## Scope Boundaries
- In scope:
  - ACL rule objects
  - ACL ruleset objects
  - view/codegen profile objects
  - manager-owned profile builder/library
  - profile registry tests
- Out of scope:
  - `FrameACLConfiguration` typed-root migration
  - validator rewrite against descriptor payloads
  - `FrameLinkContract` implementation
  - full ACL application/compiler logic

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly approved starting the ACL profile
  builder foundation after the payload-backed descriptor substrate stabilized.

## Dependencies / Related Work
- tickets/tasks/2026-04-02_design_profile_contracts_and_access_boundaries_task.md
- tickets/artifacts/nexus_acl_builder_and_persistence_model.md

## Tasks (Implementation Checklist)
- [ ] Task: TASK-2026-04-05-implement-frame-acl-profile-builder-foundation - implement the profile builder/library foundation
- [ ] Task: TASK-2026-04-05-implement-frame-acl-safe-default-profiles - encode the first safe default rule content
- [ ] Enforce Ticket Microcycle across the linked task.
- [ ] Keep the retained ACL artifact aligned to the live foundation.

## Acceptance Criteria
- manager-owned ACL profile builder/library exists
- default view/codegen profiles are seeded automatically
- typed ACL rules/rulesets exist in code
- focused ACL profile/manager tests pass

## Validation / Test Plan
- focused ACL profile and manager unit tests
- no broader Nexus/ACL integration sweep in this story by default

## Risks / Mitigations
- Risk: this slice accidentally rewrites `FrameACLConfiguration` too early.
  Mitigation: keep configuration/chain JSON-holder mechanics intact in this
    story and move only the reusable profile side.
- Risk: rules become arbitrary freeform payloads again.
  Mitigation: introduce typed rule/ruleset objects now.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- whether default rules should be empty-ceiling permissive or conservative
- whether profile composition should store names only or object refs plus names

## Decision Log
- pending

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: n/a

## Notes
- DATETIME: 2026-04-05T22:48:24Z
  TYPE: DECISION
  CLAIM: The next ACL implementation slice should start on the reusable profile
    side, not on the live frame configuration chain. The existing shell already
    has the right ownership objects (`FrameACLManager`, `FrameACLContainer`,
    `FrameACLConfigurationChain`), but the reusable profile layer is still a
    generic JSON-holder model. The user has now approved starting with a real
    manager-owned profile builder/library that mirrors the SpellExaminer-style
    registry pattern while keeping view/codegen profiles separate.
  EVIDENCE:
  - src/melder/aether/nexus/acl/frame_acl_profile.py:370-543
  - src/melder/aether/nexus/frame_acl_manager.py:14-535
  - codex/context_compass/tickets/tasks/2026-04-02_design_profile_contracts_and_access_boundaries_task.md:420-472
  - user_instruction: "lets build a dam Profile Builder class that hosts both the ACLViewProfiles and the ACLCodegen Profiles held in 2 different dictionaries"
  IMPACT: This gives the ACL lane one bounded implementation slice that does not
    force the full typed configuration rewrite yet.
  NEXT: create the implementation task and patch-doc set, then land the
    builder/library, rules, rulesets, and default profile seeding.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-05T23:00:19Z
  TYPE: FACT
  CLAIM: The first ACL profile-builder implementation slice is landed and in
    review. The reusable profile side is now typed instead of being a generic
    JSON-holder strategy registry:
    - typed `FrameACLRule` / `FrameACLRuleSet`
    - typed `FrameACLViewProfile`
    - typed `FrameACLCodegenProfile`
    - composed `FrameACLProfile`
    - manager-owned `FrameACLProfileBuilder` with default view/codegen profile
      seeding
    Focused ACL profile/manager/Nexus profile tests passed.
  EVIDENCE:
  - tickets/tasks/2026-04-05_implement_frame_acl_profile_builder_foundation.md:1-190
  IMPACT: The next ACL slice can move into typed
    `FrameACLConfiguration` / `FrameACLViewConfiguration` work without starting
    from generic reusable JSON payload holders.
  NEXT: review whether the next bounded slice should be typed
    `FrameACLConfiguration` / builder rewrite or another ACL contract
    refinement pass.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-05T23:51:00Z
  TYPE: FACT
  CLAIM: The reusable ACL profile foundation now has real named default
    content, not just typed empty scaffolding. The manager-owned builder seeds
    `safe`, `hybrid`, and `permissive` for both view and codegen, those
    profiles have curated rule content, ACL profiles carry version metadata,
    and the focused ACL profile/manager/Nexus profile tests passed.
  EVIDENCE:
  - tickets/tasks/2026-04-05_implement_frame_acl_safe_default_profiles_task.md:1-180
  IMPACT: The story is now complete enough to hand the next slice a meaningful
    reusable ACL profile ladder instead of an empty placeholder default.
  NEXT: review whether the next bounded slice should move into typed
    `FrameACLConfiguration` / `FrameACLViewConfiguration`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Acceptance criteria confirmed by user
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Add notes when the profile builder/model direction changes or when scope
  pressures move into typed configuration work.
- Reference child-task evidence instead of duplicating tactical detail.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.

## Context / Handoff Summary
This story exists to land the manager-owned ACL profile builder/library
foundation so later typed `FrameACLViewConfiguration` work starts from a real
reusable profile substrate instead of generic JSON holders.
