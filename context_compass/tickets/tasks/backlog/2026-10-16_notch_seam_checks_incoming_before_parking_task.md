# Task: notch_seam_checks_incoming_before_parking - the notch seam checks the incoming version before it parks

## Metadata
- Task ID: TASK-2026-10-16-notch_seam_checks_incoming_before_parking
- Story: none (standalone backlog task; found by TASK-2026-10-16-public_notch_target_for_staged_versions)
- Status: draft
- Owner: user
- Agent Name: unassigned
- Agent Role: UNKNOWN
- Priority: p3
- Created: 2026-10-16T12:44:16Z
- Updated: 2026-10-16T12:44:16Z

## Objective
`Spellbook._apply_notch` parks the index's outgoing active version (`_deactivate_owned_spell`) before
`_reactivate_owned_spell` checks that the incoming version is parked in this Book. When that check fails the seam
raises RuntimeError "Owned spell_id not parked for reactivation" with the outgoing version already parked: the index
has no active version until a notch back (probes C4 and C5 of the public_notch_target lane, 0.2.8248). The public
`Conduit.notch_spell` now refuses a foreign target before its transaction and again inside the window
(TASK-2026-10-16-public_notch_target_for_staged_versions), so the path left is a disposal of the target -
`Conduit.cleanup_spell`, which is not admitted through a transaction - landing between that in-window check and the
seam's Book lock, plus any internal caller that passes an unchecked target. Outcome: the seam verifies the incoming
version (parked in this Book, its `spell_index` the index passed) under the Book lock before it parks anything.

## Ticket Contract
- ENTRY_GATE: spellbook.py's holder takes it (melder_1 after the 2026-10-16 handoff; it could ride with that lane's
  D2 edit of `_apply_notch`); an active board row; a component patch for the seam.
- EXECUTION_BOUNDARY: `Spellbook._apply_notch` (the check moved ahead of the park, under the Book lock it already
  takes); its tests; system docs; the release note; one notch; the rebuild last.
- DEPENDENCIES: TASK-2026-10-16-public_notch_target_for_staged_versions (landed first; it owns conduit.py).
- EXIT_GATE: a notch whose incoming version is not parked for the index raises before anything moves (the index keeps
  its active version), including when a disposal of the target races the notch; suites green with the GIL off and on.
- FAILURE_ESCALATION: DECISION_REQUEST if the check needs a lock other than the Book lock the seam already holds.

## Scope Boundaries
- In scope: the seam's ordering (verify, then park, then promote).
- Out of scope: the public facade's checks (done by the predecessor); making `cleanup_spell` transactional.

## State Transition Event
- from_state: draft
- to_state: draft
- transition_reason: created as a draft from the public_notch_target lane's probes ("if you found more bugs just
  add tickets", owner, 2026-10-16).

## Steps / Checklist
- [ ] A holder takes the task (spellbook.py).
- [ ] Red test: a disposal of the parked target between the facade's check and the seam (or a direct seam call with a
      foreign target) leaves the index with its active version; then the reorder; green in both GIL modes.
- [ ] Docs, release note, notch, rebuild last.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence
      before dependent work; no forced body copy.

## Deliverables
- `_apply_notch` checks the incoming version before it parks the outgoing one; a test that pins it.

## Files / Paths Impacted
- src/melder/aether/spellbook/spellbook.py (`_apply_notch`)
- tests under tests/unit/melder/spellbook/ or tests/integration/melder/aether/conduit/

## Validation
- Not run.
- Recommended commands:
  - python -X gil=0 -m pytest <the new test>; python -X gil=1 -m pytest <the new test>

## Risks / Rollback Notes
- The check must stay under the Book lock the seam already holds, or a disposal can still slip between check and park.
- Rollback: revert the seam's hunk.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without delegated acceptance or reserved-owner disposition and board-sync completion.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
Qualified independent reviewer acceptance and direct closure follow shared `ticketing.md`;
this does not make independent review mandatory for every ticket.

- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none of its own; the reproducer is the predecessor's probe, rowed under its folder:
    artifacts/public_notch_target_20261016/probes/probe_notch_target_today.py (cases C4 and C5)
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - the notch seam's ordering (verify, park, promote)
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Multiple meaningful comments or authorized documents may hold findings directly; no forced
  body copy of every finding is required before ordinary continuation.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Contribution Attribution
- Ticket/Work Author(s): melder_0 (synaptic_python_developer); prose; created 2026-10-16T12:44:16Z; evidence in Notes.
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none yet

## Notes
- DATETIME: 2026-10-16T12:44:16Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: `_apply_notch` parks the outgoing version first and only then calls `_reactivate_owned_spell`, whose check
    (the incoming version is the one parked under its id) raises after the park. On 0.2.8248 a public notch to the
    active version of another index (C4) or to another Book's parked version (C5) raised RuntimeError "Owned spell_id
    not parked for reactivation" with the index's active version parked: a meld of it raised KeyError until a notch
    back. `Conduit.cleanup_spell` is not admitted through a transaction, so a disposal of the target can still land
    between the facade's in-window check and the seam's Book lock.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:3826-3967
  - src/melder/aether/spellbook/spellbook.py:1563-1621
  - src/melder/aether/conduit/conduit.py:5853-5876
  - context_compass/artifacts/public_notch_target_20261016/runs/probe_notch_target_today_gil0.txt:1-6
  IMPACT: A failed notch can leave an index without an active version; only the seam can close it under its lock.
  NEXT: A holder of spellbook.py takes the task.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Context / Handoff Summary
- Scope: the notch seam verifies the incoming version before it parks the outgoing one.
- State: draft in the backlog; source revision 0.2.8248 (the public facade's checks land first, in the predecessor).
- Next: a holder of spellbook.py takes it.
- Limits: none run (Not run).

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
