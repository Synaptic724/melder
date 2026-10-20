# Task: Investigate purge leaving a holder's many children registered until the store ends

## Metadata
- Task ID: TASK-2026-10-14-investigate_purge_leaves_holder_children_registered
- Story: none - D5 of EPIC-2026-10-14-slotted_lifetime_ownership_fixes (opened by
  TASK-2026-10-14-audit_slotted_lifetime_ownership, done)
- Status: done
- Owner: user
- Agent Name: melder_1
- Agent Role: synaptic_python_developer
- Priority: p2
- Created: 2026-10-14T18:40:43Z
- Updated: 2026-10-15T01:32:52Z

- Completed: 2026-10-15T01:32:52Z
- Summary: D5 of EPIC-2026-10-14-slotted_lifetime_ownership_fixes, notched 0.2.8238 (release note: "A `many`
  dependency is disposed with the object that holds it"): purging a holder disposes the `many` children recorded with
  it; kept as landed with the owner's acceptance. Turned in by owner directive.

## Objective
`Creations.purge` detaches and disposes only the purged spell id's entries. Proven on 0.2.8235 (p5): five
purge-and-meld cycles of a per-conduit holder dispose five holders and none of their disposal-bearing `many`
children, which all stay registered in the root's store until its teardown - the store grows with every
cycle and each child is disposed long after its holder. This is open question 1 of
EPIC-2026-10-14-many_child_follows_holder, now with a reproducer. Find how a purge could reach the holder's
children and lay out options for the owner's epic.

The owner's rule this is checked against: a holder's `many` children belong to the holder; when the holder is
disposed, so are they.

## Ticket Contract
- ENTRY_GATE: the epic's board row routes it; the reproducer is rerun on the current tree; red tests fail before
  any src edit; the epic's patch docs are written, linked and mapped.
- EXECUTION_BOUNDARY: the code paths below, the fix, its tests and docstrings (owner directive 2026-10-14: fix it
  under EPIC-2026-10-14-slotted_lifetime_ownership_fixes); system docs, release note and notch with the epic.
- DEPENDENCIES: TASK-2026-10-14-audit_slotted_lifetime_ownership (the probe and its runs);
  EPIC-2026-10-14-many_child_follows_holder (0.2.8235).
- EXIT_GATE: root cause recorded; red tests red before and green after the fix, GIL off and on; the probe case
  clean; no warm meld path change; the owner accepts.
- FAILURE_ESCALATION: DECISION_REQUEST for every behaviour that is a design choice; BLOCKER if the reproducer no
  longer fails on the current tree (record it and stop).

## Scope Boundaries
- In scope: the defect named in the objective, its code paths and every caller that shares the cause.
- Out of scope: the fix itself; the other audit findings (their own tasks).

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: opened from the audit with a reproducer that fails on 0.2.8235, GIL off and on (owner directive,
  chat 2026-10-14: "make a task to investigate it and then we'll turn it into an epic").
- from_state: ready
- to_state: in_progress
- transition_reason: the epic's tranche reached D5 (code re-read, fix shape recorded, 2026-10-14).
- from_state: in_progress
- to_state: review
- transition_reason: the fix landed with its red tests green GIL off and on; the lane's full tree is green GIL off and
  on at 0.2.8240 and the change is promoted into the system docs (epic Notes 2026-10-14T23:39:45Z and
  2026-10-15T00:00:12Z); the owner accepts.
- from_state: review
- to_state: done
- transition_reason: the owner accepted the lane and directed the turn-in (owner, chat 2026-10-15: "ok cool turn it
  all in if your done").


## Steps / Checklist
- [x] Read purge's detach and disposal path and what the store records of each child's holder.
- [x] Write a red test from the probe's p5 (children disposed with their purged holder; nothing accumulates).
- [x] Lay out options (shared with TASK-2026-10-14-investigate_transfer_leaves_holder_children_behind: children
      recorded per holder) and the purge-with-instance case, for the owner.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Root cause with evidence, red tests, and fix options for the owner's epic.

## Files / Paths Impacted
- `src/melder/aether/conduit/creations/creations.py`
- `src/melder/aether/conduit/meld/conduit_meld.py` (purge door)
- `tests/` (red tests, when the investigation runs)

## Validation
- Reproducer run on 0.2.8235 (Python 3.14.7t, GIL off and on, identical): see Notes.
- Not run: anything else (the investigation has not started).
- Reproduce (from a tree root with src/ and tests/):
  `PYTHONPATH=src:. python context_compass/artifacts/slotted_lifetime_audit_20261014/probe_lifetime_owners.py p5`

## Risks / Rollback Notes
- Investigation only; nothing to roll back.

## Applicable Anti-Patterns
- [x] No status transition without evidence-backed transition reason.
- [x] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [x] No closure without delegated acceptance or reserved-owner disposition and board-sync completion.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
- [x] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded
- [x] Board sync completed for successor routing or closure anchor update.

## Open Questions
- Landed as yes (0.2.8238): purging a holder disposes the `many` children recorded with it, after it.
  Offered to the owner (2026-10-14) to revert purge to leaving them registered; kept as landed
  unless he says otherwise.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/slotted_lifetime_audit_20261014/ (the probe and its runs, shared with the audit task)
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: decided when the owner's epic closes

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - UNKNOWN
- CONTEXT_TOPICS:
  - a purged holder's many children
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Contribution Attribution
- Ticket/Work Author(s): melder_1 (synaptic_python_developer); prose and evidence; the whole ticket; initial revision
  2026-10-14T18:40:43Z; the reproducer is the audit's probe. The rule and the directive are the owner's.
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none yet

## Notes
- DATETIME: 2026-10-14T18:40:43Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Opened from TASK-2026-10-14-audit_slotted_lifetime_ownership with a reproducer: probe case(s)
    p5 fail the owner's rule on 0.2.8235 as described in the Objective, with identical output GIL off and
    on. The code paths below were read in full during the audit; the root-cause analysis, red tests and fix options
    are this task's work.
  EVIDENCE:
  - src/melder/aether/conduit/creations/creations.py:858-960
  - src/melder/aether/conduit/creations/creations.py:961-1074
  - context_compass/artifacts/slotted_lifetime_audit_20261014/runs/probe_lifetime_owners_all_gil0.txt:49-52
  - context_compass/artifacts/slotted_lifetime_audit_20261014/probe_lifetime_owners.py:1-608
  IMPACT: The defect is real on today's tree; the owner can turn this task into an epic.
  NEXT: Rerun the reproducer on the current tree, then read the paths in Steps and record the root cause.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-14T18:55:12Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner turned the audit's tasks into one fix lane and put it first ("all these need to be fixed
    go ahead and target all these fixes since you have context first"); this task is now the epic's D5
    and covers the fix as well as the investigation (Ticket Contract updated).
  EVIDENCE: context_compass/tickets/epics/2026-10-14_slotted_lifetime_ownership_fixes_epic.md:147-159
  IMPACT: Investigation, red tests and the fix land here; docs, notes and the notch go with the epic's pass.
  NEXT: Wait for the epic's tranche order (D6 verdict, patch docs), then rerun the reproducer.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-14T19:23:31Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: Root cause re-read: `Creations.purge` detaches only the purged spell id's live entry and its disposal record,
    and the holder's children sit in their own spell's bucket (0.2.8235), so they stay registered and undisposed until
    the store ends. Fix: the holder-owned children record decided in D4 - purge detaches the holder's
    `HolderDisposalEntry` and disposes the holder, then its children, outside the locks, with one O(1) lookup.
    The purge count stays the purged target's own count (children are not the target's entries).
  EVIDENCE:
  - src/melder/aether/conduit/creations/creations.py:858-1020
  - context_compass/tickets/tasks/2026-10-14_investigate_transfer_leaves_holder_children_behind_task.md:158-184
  IMPACT: D5 lands with D4's representation; one red test per case (p5).
  NEXT: Write the epic's patch docs, then red tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-14T20:29:11Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Red tests written and run on the 0.2.8237 scratch tree (Python 3.14.7t), identical GIL off and on: 8 failed,
    2 controls passed. D5's six fail for the defect: a purge of a per-conduit, plain (no own disposal method),
    spellspace or owner-purged unique holder leaves its child open (closes 0) and registered; a failing child disposal
    is not raised by the purge (DID NOT RAISE); a many purge of the child spell counts 2 and closes a live holder's
    child. The teardown-order control (holder closed before its child) passes, as it must before and after the fix.
  EVIDENCE:
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/landing/test_conduit_integration_holder_children_lifetime_0_2_8238.py:197-344
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/landing/test_conduit_integration_holder_children_lifetime_0_2_8238.py:402-415
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/runs/red_d4_d5_holder_children_0_2_8237_gil0.txt:1-21
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/runs/red_d4_d5_holder_children_0_2_8237_gil1.txt:1-21
  IMPACT: The entry gate for the 0.2.8238 src edit is met for D5 (red before the fix, the right reason).
  NEXT: Map the creations, codegen and holder-children patch sections to the implementation steps, then edit src.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-14T20:53:11Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Landed as 0.2.8238 (repo and scratch identical). `Creations` records a holder's adopted children in a
    `HolderDisposalEntry`; purge detaches it with the holder and disposes holder then children newest-first (count
    unchanged); the emitted miss adopts after publication. The red module is 10/10 green GIL off and on; the probe's
    p5 reports 5 holders and 5 children closed, none left registered. Creations units (14), lowering units (3 new, 1
    extended) and the door-held unit pass; the 0.2.8235 many-child tests now read the holder record (13 updated, the
    reason in their helpers). Chunks green on the scratch tree: unit/comp/int aether, int conduit, unit/comp/int
    spellbook and the crystallizer chunks (GIL 0), aether/conduit/spellbook again at GIL 1; repo set 633 passed (GIL 1).
  EVIDENCE:
  - src/melder/aether/conduit/creations/creations.py:53-115
  - src/melder/aether/conduit/creations/creations.py:985-1069
  - src/melder/aether/conduit/creations/creations.py:1082-1187
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/runs/probe_t4_t4b_p5_0_2_8238_gil0.txt:19-22
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/runs/d45_scratch_final_gil0.txt:1-7
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/runs/d45_scratch_final_gil1.txt:1-3
  IMPACT: D5 is fixed; disposal failures of the children surface from the holder's purge.
  NEXT: Run the full tree at the end of the pass, then the owner's review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-15T00:07:24Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Status to review. D5 (0.2.8238) holds at the end of the lane's pass: the audit probe's p5 shows five purged
    holders and their five children closed and none left registered; the full tree is green GIL off and on at
    0.2.8240; the system docs carry the holder-record invariant, the purge failure mode and the Creations Disposal
    Pipeline rule. The owner has not yet answered the offer to revert purge to leaving the children registered; D5
    stays as landed meanwhile.
  EVIDENCE:
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/runs/probe_lifetime_owners_all_0_2_8240_gil0.txt:48-51
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/runs/full_tree_0_2_8240_gil0.txt:1-28
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/runs/full_tree_0_2_8240_gil1.txt:1-20
  - context_compass/system_docs/src_architecture.md:974-986
  - context_compass/system_docs/src_architecture.md:1775-1778
  - context_compass/system_docs/src_components.md:6634-6657
  IMPACT: The task waits for the owner's acceptance of purge disposing the children.
  NEXT: The owner accepts D5 as landed or asks for the revert.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-15T01:32:52Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: Turned in. The owner accepted the lane and directed the turn-in (owner, chat 2026-10-15: "ok cool turn it all
    in if your done"); D5 is notched 0.2.8238 (release note: "A `many` dependency is disposed with the object that
    holds it"): purging a holder disposes the `many` children recorded with it; kept as landed with the owner's
    acceptance. Status done, completion summary written, ticket moved to tasks/completed; the board syncs run with the
    epic's closure.
  EVIDENCE:
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/runs/full_tree_0_2_8240_gil0.txt:1-33
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/runs/full_tree_0_2_8240_gil1.txt:1-25
  - context_compass/artifacts/slotted_lifetime_fixes_20261014/runs/rebuild_0_2_8240.txt:1-40
  IMPACT: Closed; nothing of this task stays open.
  NEXT: None.
  REREAD: HELPFUL
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Done (2026-10-15T01:32:52Z). D5: notched 0.2.8238 (release note: "A `many` dependency is disposed with the object that
holds it"): purging a holder disposes the `many` children recorded with it; kept as landed with the owner's
acceptance. Turned in by owner directive with EPIC-2026-10-14-slotted_lifetime_ownership_fixes; commit and push are
the owner's.

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
