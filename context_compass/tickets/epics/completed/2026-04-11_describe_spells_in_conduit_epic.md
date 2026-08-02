# Epic: Describe Spells In Conduit
- Completed: 2026-04-13T11:43:06Z
- Summary: Completed the small conduit-facing ACL authoring dump epic after the spellbook-owned dump and conduit facade landed.

## Metadata
- Epic ID: EPIC-2026-04-11-describe-spells-in-conduit
- Status: done
- Owner: codex
- Priority: p1
- Created: 2026-04-11T10:20:45Z
- Updated: 2026-04-13T11:43:06Z
- Target Window: 2026-Q2
- Related Program/Initiative: Rift static ACL authoring support

## Problem / Opportunity
Static ACL authoring needs one conduit-facing way to inspect the spell targets
that are actually visible inside a conduit/spellbook runtime. Without that
surface, users have to infer:
- logical targeting fields
- exact `spell_id` values
- conduit ownership

from lower-level runtime objects or ad hoc inspection code.

## MRP Alignment (Most Reasonable Product)
The MRP outcome is small and explicit:
- `Spellbook.describe_spells_in_spellbook(...)` owns the dump
- `Conduit.describe_spells_in_conduit(...)` facades it
- the payload stays limited to ACL-authoring fields only

## Ticket Contract
- ENTRY_GATE: the user explicitly requested a dedicated implementation lane
  named around `describe_spells_in_conduit` and asked for the spellbook-owned
  companion method as `describe_spells_in_spellbook`.
- EXECUTION_BOUNDARY: authoring dump only, plus focused tests and ticket sync.
- DEPENDENCIES:
  - tickets/epics/2026-04-10_rift_access_modes_static_capability_dynamic_epic.md
  - tickets/artifacts/2026-04-08_rift_access_modes_static_capability_dynamic_model.md
  - src/melder/spellbook/spellbook.py
  - src/melder/aether/conduit/conduit.py
- EXIT_GATE: the conduit-facing authoring dump is implemented, tested, and
  routed under this dedicated epic.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the dump needs to expose
  internal live-creation diagnostics instead of the smaller authoring payload.

## Goals (Outcomes)
- Give the authoring dump its own durable lane.
- Keep the owner/facade split explicit.
- Keep the payload useful for ACL authoring without leaking debug-only fields.

## Non-Goals (Explicit Exclusions)
- Static runtime enforcement.
- ACL registry redesign.
- Viewer changes.
- Capability/dynamic runtime work.

## Scope Boundaries
- In scope:
  - spellbook-owned dump
  - conduit facade
  - focused tests
  - ticket routing
- Out of scope:
  - static ACL execution
  - meld lookup redesign
  - endpoint packaging

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user asked for a dedicated epic named around
  `describe_spells_in_conduit` after the runtime slice was already implemented.

## Success Metrics
- The runtime has one stable authoring dump surface.
- The task is no longer hanging only under the generic access-modes lane.

## Requirements (Functional + Non-Functional)
- Functional:
  - expose `describe_spells_in_spellbook(...)`
  - expose `describe_spells_in_conduit(...)`
  - include the authoring field set only
- Non-functional:
  - deterministic ordering
  - rich docstrings
  - focused regression tests

## Constraints / Assumptions
- `Spellbook._spell_id_pool` is the right visible spell set.
- `Spell` already carries the authoring fields.
- `Meld` is not the owner of this dump.

## Dependencies / External References
- tickets/artifacts/2026-04-08_rift_access_modes_static_capability_dynamic_model.md

## Milestones (Track Progress)
- [x] Milestone 1: define owner/facade split
- [x] Milestone 2: implement conduit/spellbook dump
- [x] Milestone 3: user review and acceptance

## Stories (Required to Complete)
- [x] Story: STORY-2026-04-11-describe-spells-in-conduit-and-spellbook-authoring-dump

## Tasks (Cross-Cutting or Epic-Level)
- [x] Task: TASK-2026-04-11-implement-conduit-meld-target-dump-for-acl-authoring

## Acceptance Criteria (Epic Done)
- The dedicated authoring-dump lane exists.
- Runtime implementation and focused tests are linked beneath it.
- The user accepts the dump shape or redirects it.

## Risks / Mitigations
- Risk: the dump grows into a runtime-debug surface.
  Mitigation: keep the payload scoped to selector and ownership fields only.

## Applicable Anti-Patterns
- [ ] No epic-state transition without story/task evidence.
- [ ] No closure while the linked task is still awaiting user acceptance.

## Validation / Test Approach
- Focused unit tests over `Spellbook` and `Conduit` only.

## Rollout / Adoption Plan
- Keep the dump small.
- Use it as the authoring surface for static ACL work next.

## Open Questions
- Should the payload ever include more than the current selector/ownership set?

## Decision Log
- This epic was created after implementation so the lane name matches the
  user-directed surface instead of hiding under the broader access-modes lane.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: n/a

## Notes
- DATETIME: 2026-04-11T10:20:45Z
  TYPE: DECISION
  CLAIM: The conduit authoring dump is being re-homed under a dedicated epic
    named after the user-facing surface, even though the broader static/capability/dynamic
    access-mode epic still exists. This keeps the small runtime slice easy to
    find and review.
  EVIDENCE:
  - user_instruction: "make an epic to implement this, and lets call it describe_spells_in_conduit"
  - tickets/tasks/2026-04-11_implement_conduit_meld_target_dump_for_acl_authoring.md:1-122
  IMPACT: Review and follow-on ACL authoring work can route through a lane
    named after the actual API surface instead of a generic parent epic only.
  NEXT: create the child story and re-home the existing review task under it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-13T11:43:06Z
  TYPE: DECISION
  CLAIM: This small authoring-dump epic is complete. The owner/facade split is
    explicit, the focused implementation and tests are landed, and no broader
    static/capability lane still depends on this epic remaining active.
  EVIDENCE:
  - tickets/stories/completed/2026-04-11_describe_spells_in_conduit_and_spellbook_authoring_dump_story.md:1-95
  - tickets/tasks/completed/2026-04-11_implement_conduit_meld_target_dump_for_acl_authoring.md:1-152
  IMPACT: The epic can move to the completed lane.
  NEXT: none.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Closure Confirmation
- [x] Work walkthrough shared with user
- [x] Acceptance criteria confirmed by user

## Noting Behavior
- Note focus: lane ownership, routing, and acceptance state.
- Keep runtime details in the linked task unless the lane boundary changes.

## Context / Handoff Summary
This epic exists so the authoring dump can be found and reviewed under the
surface name the user chose: `describe_spells_in_conduit`.
