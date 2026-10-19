# Story: one_registration_per_object - an object already registered is refused, whatever the bind signature

## Metadata
- Story ID: STORY-2026-10-18-one_registration_per_object
- Epic: EPIC-2026-10-18-spell_identity_is_the_code
- Status: draft
- Owner: user
- Agent Name: melder_0
- Agent Role: synaptic_python_developer
- Priority: p1
- Created: 2026-10-18T11:45:58Z
- Updated: 2026-10-19T00:49:20Z

## User Narrative
As an agent, I want Melder to refuse registering an object it already holds - under any name, existence or as a
staged version - so that one object is one spell and nothing is built twice for it.

## Value / MRP Alignment
The owner: "you could register the same object n number of times for each existence this is a correctness bug big
time". With S1 the same object has one spell_id, so the existing collision check refuses it; this story makes the
refusal complete across every registration path and makes its message say what happened.

## Ticket Contract
- ENTRY_GATE: S1 landed; this story's component patch approved; the board row.
- EXECUTION_BOUNDARY: the registration paths (bind, bind_inactive, add_to_spell_index, scan_bind, restore and graft
  through them) and the refusal message; tests and docs.
- DEPENDENCIES: S1.
- EXIT_GATE: a second registration of one object is refused on every path with nothing registered; one active
  object per address still holds; moving a registration between indexes still works.
- FAILURE_ESCALATION: CONFLICT if another lane takes spellbook.py.

## Requirements (Functional)
- bind, bind_inactive and add_to_spell_index (and scan_bind, restore and graft through them) refuse a spell_id
  already registered under the existing spell-id regime - per process by default, per frame under per-frame ids;
  the owner: the scope is not part of this change - with nothing registered.
- The message names the existing registration (its frame, Book, address, index, active or parked) and the remedy:
  change its binding with S3's verb, or move it with add_to_spell_index / remove_from_spell_index.
- One active object per address stays (the frame's signature claim).

## Requirements (Non-Functional)
- The refusal adds no lock and no meld-path work.

## Scope Boundaries
- In scope: the registration paths and the refusal message.
- Out of scope: the hashes (S1, S2), revalidation (S3), the migration (S5).

## State Transition Event
- from_state: draft
- to_state: draft
- transition_reason: parked in the backlog by the owner (the epic's DECISION note of the turn-in,
  2026-10-19T00:49:20Z): the epic turned in after S1 and S2 landed.

## Dependencies / Related Work
- EPIC-2026-10-18-spell_identity_is_the_code
- STORY-2026-10-18-spell_id_hashes_the_object_code
- STORY-2026-10-18-revalidate_on_binding_change

## Tasks (Implementation Checklist)
- [ ] Task: the component patch (Spellbook's registration paths, the message).
- [ ] Task: red tests per path; implement; docs; notch; the rebuild last.
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence.

## Acceptance Criteria
- Binding a class under a second name, binding it with another existence and staging it as a version are each
  refused with the new message, and nothing is registered.
- A class bound in a second frame is refused under process-wide ids and accepted under per-frame ids.
- A second registration of an object whose version sits alone in an index `remove_from_spell_index`
  minted is refused - in another Book of its frame (M4b) and in another frame under process-wide ids
  (M5b) - as 0.2.8259 made it (STORY-2026-10-17-minted_index_missing_from_frame_registry; M1-42).

## Validation / Test Plan
- `test_registering_the_same_class_twice_is_refused_whatever_the_binding`; per path; GIL off and on.

## UX / API / Data Notes
- **Breaking change** (with S5): one class can no longer be registered twice to get two objects; use subclasses.

## Risks / Mitigations
- Tests and users that bind one object twice: counted and moved in S5.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- None: the scope follows the existing spell-id regime (owner, 2026-10-18: not part of this change).

## Decision Log
- 2026-10-18T11:45:58Z: filed under EPIC-2026-10-18-spell_identity_is_the_code (the epic's DECISION note).
- 2026-10-18T12:01:17Z: melder_1's files are free (M1-28; the epic's FACT note of 2026-10-18T12:01:17Z); the entry gate
  no longer waits on a release.
- 2026-10-18T12:15:14Z: the scope question withdrawn - the existing spell-id regime stands (owner; the epic's
  DECISION note).
- 2026-10-19T00:49:20Z: parked in tickets/stories/backlog/ on the owner's word; the epic turned in after S1 and
  S2 landed (the epic's DECISION note).

## Artifact Links (Optional)
Qualified independent reviewer acceptance and direct closure follow shared `ticketing.md`;
this does not make independent review mandatory for every ticket.

- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none yet (the design's probes are rowed under the epic)
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: rows are added when this story produces its own artifacts

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - a spell's identity (its code) versus its binding (how it is kept)
- IF_UNKNOWN: none

## Contribution Attribution
- Ticket/Work Author(s): melder_0 (synaptic_python_developer); prose; filed 2026-10-18T11:45:58Z.
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none yet

## Notes
- DATETIME: 2026-10-18T11:45:58Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Filed from the owner's direction (the epic's DECISION note of 2026-10-18T11:45:58Z); the evidence it
    starts from is the epic's FACT note and its probes. Nothing in src/ moves before this story's component patch is
    approved.
  EVIDENCE: context_compass/tickets/epics/2026-10-18_spell_identity_is_the_code_epic.md:220-270
  IMPACT: The scope, requirements and acceptance above are the plan the patch docs refine.
  NEXT: the component patch once S1 lands.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-19T00:49:20Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Parked in tickets/stories/backlog/ on the owner's word (S4): the identity epic turned in after S1
    (0.2.8257) and S2 (0.2.8258) landed; this story waits there, with S6 and the configurables epic, for the
    owner to take the identity work up again. Status stays draft.
    M1-42: melder_1's 0.2.8259 fixed the minted-index gap, so a second registration of a version alone
    in a minted index is refused (M4b, M5b); both join its acceptance criteria.
  EVIDENCE:
  - context_compass/tickets/epics/completed/2026-10-18_spell_identity_is_the_code_epic.md:1037-1055
  - context_compass/tickets/stories/completed/2026-10-17_minted_index_missing_from_frame_registry_story.md:3-9
  IMPACT: Nothing in this story is started; its scope, requirements and acceptance stand as written.
  NEXT: the owner's word; then the component patch (the refusal naming the existing registration).
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: cross-task synthesis, dependency flow, and state-transition logic.
- Add notes when task routing changes, gate decisions are made, or risks shift.
- Reference child-task notes for evidence instead of duplicating tactical detail.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.
- Multiple meaningful comments may hold evidence directly; no forced body copy before ordinary
  continuation. Current scope/state/decisions/handoff stay coherent at material transitions.

## Context / Handoff Summary
- Scope: one object, one registration, on every path, with a clear refusal.
- State: draft, parked in the backlog (the owner, 2026-10-19): the identity epic turned in after
  S1 (0.2.8257) and S2 (0.2.8258) landed.
- Next: the owner's word; then the component patch (the refusal naming the existing registration).

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->

<!--
Anything this project needs on every ticket of this kind goes in the region
above: extra fields, a compliance checklist, a link to a local convention.

The region is yours. An upgrade replaces every other line of this template with
the new version's text and carries this region across untouched, so a local
addition here is not a divergence you re-resolve on every upgrade - which is
what editing the rest of the template would cost you.
-->
