# Story: Describe Spells In Conduit And Spellbook Authoring Dump
- Completed: 2026-04-13T11:43:06Z
- Summary: Completed the small conduit/spellbook authoring dump story after the dedicated owner/facade dump landed.

## Metadata
- Story ID: STORY-2026-04-11-describe-spells-in-conduit-and-spellbook-authoring-dump
- Epic: EPIC-2026-04-11-describe-spells-in-conduit
- Status: done
- Owner: codex
- Priority: p1
- Created: 2026-04-11T10:20:45Z
- Updated: 2026-04-13T11:43:06Z

## User Narrative
As the Rift/static ACL author, I want one small conduit-facing dump of visible
spells and exact ids, so that I can author static ACL entries without digging
through runtime internals.

## Value / MRP Alignment
This story anchors one small but real step in the static-authoring lane:
surface the spell selectors users actually need before static enforcement work
starts.

## Ticket Contract
- ENTRY_GATE: the user explicitly requested the dedicated
  `describe_spells_in_conduit` lane and the implementation task is already in
  review.
- EXECUTION_BOUNDARY: owner/facade dump, focused tests, and review routing
  only.
- DEPENDENCIES:
  - tickets/epics/2026-04-11_describe_spells_in_conduit_epic.md
  - tickets/tasks/2026-04-11_implement_conduit_meld_target_dump_for_acl_authoring.md
- EXIT_GATE: the task is reviewed and the user either accepts the dump or
  redirects the next payload change.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the user wants the payload to
  expand into a live-debug/runtime-inspection surface.

## Requirements (Functional)
- spellbook owns the dump
- conduit facades the dump
- payload includes:
  - `spell_id`
  - `spell_name`
  - `binding_name`
  - `spellframe`
  - `existence`
  - `owner_conduit_id`

## Requirements (Non-Functional)
- deterministic
- small
- authoring-oriented

## Scope Boundaries
- In scope:
  - runtime dump surface
  - unit coverage
  - task routing
- Out of scope:
  - ACL compile/execution logic
  - viewer integration
  - capability/dynamic work

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the implementation task is already landed and awaiting
  review, so this story exists to own that review lane explicitly.

## Dependencies / Related Work
- tickets/epics/2026-04-10_rift_access_modes_static_capability_dynamic_epic.md

## Tasks (Implementation Checklist)
- [x] Task: TASK-2026-04-11-implement-conduit-meld-target-dump-for-acl-authoring
- [x] Enforce Ticket Microcycle across linked task work.

## Acceptance Criteria
- The task sits under a dedicated story/epic named after the API surface.
- The user can review the landed dump from this story.

## Validation / Test Plan
- Focused unit coverage only.

## UX / API / Data Notes
- The dump is for advanced authoring, not a general debug API.

## Risks / Mitigations
- Risk: the story drifts back under generic access-mode notes.
  Mitigation: keep the dedicated lane and route the review through it.

## Applicable Anti-Patterns
- [ ] No story-state transition without task evidence.
- [ ] No closure while the linked task still awaits user acceptance.

## Open Questions
- None beyond payload acceptance right now.

## Decision Log
- Re-homed into a dedicated story after implementation to match the user-picked
  API naming.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: n/a

## Notes
- DATETIME: 2026-04-11T10:20:45Z
  TYPE: DECISION
  CLAIM: The existing review task is being re-homed under a dedicated story
    named after the public API surface instead of leaving it only under the
    broader access-modes story.
  EVIDENCE:
  - user_instruction: "make an epic to implement this, and lets call it describe_spells_in_conduit"
  - tickets/tasks/2026-04-11_implement_conduit_meld_target_dump_for_acl_authoring.md:1-122
  IMPACT: The next review/acceptance conversation now has a direct story anchor.
  NEXT: update the task metadata and board resume hierarchy to point here.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-13T11:43:06Z
  TYPE: DECISION
  CLAIM: This authoring-dump story is complete. The spellbook-owned dump and
    conduit facade exist, the payload stayed small, and no further acceptance
    routing is needed for this narrow surface.
  EVIDENCE:
  - tickets/tasks/completed/2026-04-11_implement_conduit_meld_target_dump_for_acl_authoring.md:1-152
  IMPACT: The story can move to the completed lane and stop occupying active
    planning state.
  NEXT: none.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user

## Noting Behavior
- Note focus: story ownership and acceptance routing.

## Context / Handoff Summary
This story owns review and acceptance of the small conduit/spellbook authoring
dump surface.
