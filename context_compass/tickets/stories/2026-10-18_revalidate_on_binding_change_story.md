# Story: revalidate_on_binding_change - a changed binding hash revalidates the spell and its dependents

## Metadata
- Story ID: STORY-2026-10-18-revalidate_on_binding_change
- Epic: EPIC-2026-10-18-spell_identity_is_the_code
- Status: draft
- Owner: user
- Agent Name: melder_0
- Agent Role: synaptic_python_developer
- Priority: p1
- Created: 2026-10-18T11:45:58Z
- Updated: 2026-10-18T16:24:12Z

## User Narrative
As an agent changing how a spell is kept - its lifetime, teardown, address or capability - I want Melder to
revalidate that spell and everything that depends on it, so that no plan, verdict, cache entry or stored object
built for the old binding is used for the new one.

## Value / MRP Alignment
The owner's rule: "if that hash changes we should revalidate the object". A binding change can change what a
spell is built as (existence), how it is torn down (disposal names), who resolves it (address: Phase 3 matches
categories by spellframe) and whether it is built at all (resolvable).

## Ticket Contract
- ENTRY_GATE: S1 and S2 landed; this story's component patch approved; the board row.
- EXECUTION_BOUNDARY: re-registration of a spell_id with another binding hash, the revalidation marks, Creations'
  entry for the spell_id, a binding-change verb; tests and docs.
- DEPENDENCIES: S1, S2; the notch's revalidation marks (0.2.8250).
- EXIT_GATE: every binding change revalidates the spell and its dependents; the store never hands the new binding
  an object built for the old one; the verb works on an active spell whose index holds parked versions.
- FAILURE_ESCALATION: DECISION_REQUEST on the verb's shape and on what happens to the old objects; CONFLICT if
  another lane takes a needed file.

## Requirements (Functional)
- Re-registering a spell_id with a different binding hash retires its verdicts (as `register_index` does), resets
  its compiled plan and gates its lineage, and marks what depends on it downstream, as a notch marks them.
- The store's entry under the spell_id follows the binding: an unchanged existence and disposal list keep it; a
  changed one retires the old entry - its objects stay alive and are torn down with their own disposal list - before
  the new binding builds.
- A verb changes a spell's binding in place and keeps its spell_id (cleanup_spell refuses an active member whose
  index holds parked versions today).
- The managed settings: a settings-only change keeps part A's pool rebind, unless the owner rules otherwise.

## Requirements (Non-Functional)
- No new lock-order edge; warm meld paths unchanged; the marks run with the Book lock free, as the notch's do.

## Scope Boundaries
- In scope: re-registration, revalidation, the store's entry, the binding verb.
- Out of scope: the hashes (S1, S2), the refusals (S4), the migration (S5), pool routing (set aside by the owner).

## State Transition Event
- from_state: (new)
- to_state: draft
- transition_reason: filed under EPIC-2026-10-18-spell_identity_is_the_code on the owner's direction (chat
  2026-10-18); stays draft until S1 and S2 land and its open questions are answered.

## Dependencies / Related Work
- EPIC-2026-10-18-spell_identity_is_the_code
- STORY-2026-10-18-binding_manifest_hash
- STORY-2026-10-18-one_registration_per_object

## Tasks (Implementation Checklist)
- [ ] Task: the component patch (Spellbook, Creations, SpellSystemStates, Conduit's verb).
- [ ] Task: red tests per binding field; implement; docs; notch; the rebuild last.
- [ ] Enforce Ticket Microcycle across all linked tasks.
- [ ] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence.

## Acceptance Criteria
- Changing a spell's existence from many to unique (or back) through the verb builds the new existence at the next
  meld and never returns the old entry; its dependents rebuild.
- Changing its spellframe makes the consumers that matched the old category re-resolve.
- Changing only its managed settings rebinds the pool and rebuilds nothing.

## Validation / Test Plan
- `test_changing_a_spells_existence_revalidates_it_and_its_dependents`,
  `test_a_binding_change_never_serves_the_old_entry`; GIL off and on.

## UX / API / Data Notes
- A new binding verb on Conduit (name and shape in the patch).

## Risks / Mitigations
- Objects of the old binding: kept alive with their own teardown (Melder does not police userland objects).

## Applicable Anti-Patterns
- [ ] No story-state transition without linked task-state evidence.
- [ ] No closure while required tasks remain active or un-routed.
- [ ] No cross-task synthesis claims without ticket-note evidence pointers.

## Open Questions
- The verb's name and shape; which fields revalidate; the old entry's objects; a disposed spell's pool beside a new
  root's pool after a re-registration elsewhere (unproven; from S6).

## Decision Log
- 2026-10-18T11:45:58Z: filed under EPIC-2026-10-18-spell_identity_is_the_code (the epic's DECISION note).
- 2026-10-18T12:01:17Z: melder_1's files are free (M1-28; the epic's FACT note of 2026-10-18T12:01:17Z); the entry gate
  no longer waits on a release.

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
  NEXT: the component patch once S1 and S2 land.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-18T16:24:12Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: For S3, answered by probe (the UNKNOWN in S2's inventory note): under S1 and S2 (the blast-radius
    mirror) a rebind of one class under another existence after `cleanup_spell` keeps its spell_id, and on a
    root the new binding's first meld returns the object the removed definition left in its slot whenever
    both existences are slotted (unique -> unique_per_conduit and unique_per_conduit -> unique:
    second_meld_is_old_object=True); a `many` side builds fresh (unique_per_conduit -> many and
    many -> unique_per_conduit: False). unique -> unique is the case of the 2026-10-03 surviving-product
    ruling. The same with the GIL off and on. Today the existence is in the spell_id, so such a rebind is
    another spell_id and another slot; S1 changes that, and this story decides whether a slotted entry
    follows the new binding (kept per binding hash, or retired on a binding change).
  EVIDENCE:
  - context_compass/artifacts/spell_identity_20261018/blast_radius/probes/probe_same_id_rebind_store.py:1-48
  - context_compass/artifacts/spell_identity_20261018/blast_radius/runs/probe_same_id_rebind_store_gil0.txt:1-5
  - context_compass/artifacts/spell_identity_20261018/blast_radius/runs/probe_same_id_rebind_store_gil1.txt:1-9
  - context_compass/tickets/stories/2026-10-18_binding_manifest_hash_story.md:156-192
  IMPACT: Between S1 and S2's landing and this story's, a rebind under another slotted existence meets the removed
    definition's object: a RISK the epic carries to the release note unless this story lands in the same
    release.
  NEXT: This story's component patch, after S1 and S2.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

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
- Scope: a binding change revalidates the spell and its dependents; the store and a verb follow it.
- State: draft (melder_0); after S1 and S2.
- Next: the component patch once S1 and S2 land.

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
