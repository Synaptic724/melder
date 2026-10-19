# Story: spell_id_migration - every spell_id moves once, and nothing breaks silently

## Metadata
- Story ID: STORY-2026-10-18-spell_id_migration
- Epic: EPIC-2026-10-18-spell_identity_is_the_code
- Status: draft
- Owner: user
- Agent Name: melder_0
- Agent Role: synaptic_python_developer
- Priority: p2
- Created: 2026-10-18T11:45:58Z
- Updated: 2026-10-19T00:49:20Z

## User Narrative
As a user upgrading Melder, I want the one-time move of every spell_id handled - caches, records, research history,
tests and docs - so that nothing silently breaks and every change is documented.

## Value / MRP Alignment
Every spell_id changes once with S1. The creation cache, the Crystallizer record, MutationResearch's history and the
suite all hold spell_ids; each needs a defined path, and the change is one Breaking release-note entry.

## Ticket Contract
- ENTRY_GATE: S1-S4's patches approved; this story's component patch approved; the board row.
- EXECUTION_BOUNDARY: the cache generation, the record version and restore/graft mapping, research history, the
  tests that bind one object twice, the system documents, the graph, README and the release note.
- DEPENDENCIES: S1-S4; the owner's call on records holding one object twice.
- EXIT_GATE: an old cache is cold once; an old record restores with mapped ids or reports what it cannot rebuild;
  the suite is green with the GIL off and on; docs, notch and the rebuild with both checks OK.
- FAILURE_ESCALATION: DECISION_REQUEST on the record policy; CONFLICT if another lane takes a needed file.

## Requirements (Functional)
- A cache generation retires every bundle written under the old ids.
- The record's version moves; restore and graft map recorded ids to the new ones; a record that registered one
  object twice rebuilds the first and reports the rest as a shortfall, or refuses (the owner's call).
- MutationResearch history recorded under old spell_ids is mapped or marked, as the patch decides.
- Tests that bind one object twice move to two objects; every managed and fingerprint test moves to the new rule.
- Docs: the system documents, the graph, README and the release note (Breaking: every spell_id moves; one object,
  one spell; a binding change revalidates).

## Requirements (Non-Functional)
- The migration adds no runtime cost after the first cold conjure.

## Scope Boundaries
- In scope: caches, records, research history, tests and docs.
- Out of scope: the hashes (S1, S2), revalidation (S3), the refusals (S4).

## State Transition Event
- from_state: draft
- to_state: draft
- transition_reason: parked in the backlog by the owner (the epic's DECISION note of the turn-in,
  2026-10-19T00:49:20Z): the epic turned in after S1 and S2 landed.

## Dependencies / Related Work
- EPIC-2026-10-18-spell_identity_is_the_code
- STORY-2026-10-18-spell_id_hashes_the_object_code
- STORY-2026-10-18-one_registration_per_object

## Tasks (Implementation Checklist)
- [ ] Task: the component patch (CachingSystem, RecordVersion, RestoreEngine, GraftRunner, MutationResearch).
- [ ] Task: count the tests that bind one object twice (a prototype run).
- [ ] Task: implement; docs; release note; notch; the rebuild last.
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence.

## Acceptance Criteria
- A world recorded before the change restores (mapped ids) or reports exactly what it could not rebuild.
- A cache written before the change is cold once and rewritten.

## Validation / Test Plan
- `test_a_record_from_before_the_identity_change_restores_with_mapped_ids`; the whole tree with the GIL off and on.

## UX / API / Data Notes
- **Breaking change**: every spell_id moves once.

## Risks / Mitigations
- Research lanes keyed by old ids lose their residency join: the patch decides mapping or marking.

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- None open: the record policy for one object registered twice is the owner's call - restore the first
  and file a shortfall per dropped duplicate (the epic's DECISION note of 2026-10-18T14:14:10Z).

## Decision Log
- 2026-10-18T11:45:58Z: filed under EPIC-2026-10-18-spell_identity_is_the_code (the epic's DECISION note).
- 2026-10-18T12:01:17Z: melder_1's files are free (M1-28; the epic's FACT note of 2026-10-18T12:01:17Z); the entry gate
  no longer waits on a release.
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
  NEXT: the component patch with the others'.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-19T00:49:20Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Parked in tickets/stories/backlog/ on the owner's word (S5): the identity epic turned in after S1
    (0.2.8257) and S2 (0.2.8258) landed; this story waits there, with S6 and the configurables epic, for the
    owner to take the identity work up again. Status stays draft.
    Its open question is answered (the owner, the epic's DECISION note of 2026-10-18T14:14:10Z: restore
    the first, a shortfall per dropped duplicate), so Open Questions says so.
  EVIDENCE:
  - context_compass/tickets/epics/completed/2026-10-18_spell_identity_is_the_code_epic.md:1037-1055
  - context_compass/tickets/epics/completed/2026-10-18_spell_identity_is_the_code_epic.md:465-490
  IMPACT: Nothing in this story is started; its scope, requirements and acceptance stand as written.
  NEXT: the owner's word; then the component patch (records holding one object twice restore the first).
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
- Scope: the one-time move of every spell_id.
- State: draft, parked in the backlog (the owner, 2026-10-19): the identity epic turned in after
  S1 (0.2.8257) and S2 (0.2.8258) landed.
- Next: the owner's word; then the component patch (records holding one object twice restore the first).

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
