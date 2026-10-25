# Epic: A borrower meld in flight during a lender's notch ends in a version or a clean refusal

## Metadata
- Epic ID: EPIC-2026-10-25-notch_fanout_inflight_melds
- Status: in_progress
- Owner: Mark
- Agent Name: melder_0
- Agent Role: synaptic_python_developer
- Priority: p1
- Created: 2026-10-25T00:16:54Z
- Updated: 2026-10-25T00:48:34Z
- Target Window: set by the owner once the design decision is made
- Related Program/Initiative: rule 2 of the owner's 2026-10-15 direction
  (TASK-2026-10-16-recheck_contract_consumers_when_provider_changes, completed, 0.2.8250), which filed this
  race as known and not fixed

## Problem / Opportunity
With the GIL off, a meld of a borrower's SpellContract consumer that runs while the lender's `notch_spell` fans out
to its borrowers can return the consumer built with the raw SpellContract default - its AttributeError surfaces
only when the object is used - or raise one of the internal RuntimeErrors "Cannot build CreationContext before
spell_codegen_creation exists.", "many_only manifest references unknown spell_id" and "Spell creation context was
not published". melder_1 measured it on 0.2.8248-0.2.8249 (with the GIL off 7 of 20 runs of four meld threads
against 20 notches end a thread so; with it on, 0 of 20) and traced it to one gap: `notch_spell` fans out after its
transaction ends, so a meld already past its gate is not ordered against the park and the reactivation
(src_architecture, Failure Modes and Error Paths: "Known, not fixed"). A consumer built against no provider is
wrong structure handed to an agent, and nothing tells the agent until it calls the object. The owner's ask (chat
2026-10-24): "focus on 2 and 3 make an epic for each and investigate them".

## MRP Alignment (Most Reasonable Product)
Agents iterate on one object through notches while its borrowers keep melding (src_architecture, What Melder Is).
The MRP is a meld racing a notch that ends in a version - the outgoing or the incoming one - or in the clean
SpellbookValidationError refusal the 0.2.8227 rule gives a meld racing a sever, and never in an object built
against no provider or an internal RuntimeError.

## Ticket Contract
- ENTRY_GATE: the owner's ask recorded (Notes, DECISION); the child task moved out of the backlog, assigned to
  melder_0 and routed on attention_board.md; melder_1, its author, told (M0-222).
- EXECUTION_BOUNDARY: now, investigation: read-only on src/ and tests/; runs on a /tmp copy of the 0.2.8267 tree,
  the GIL off and on; runs and the in-Book probe under artifacts/notch_fanout_race_20261025/; findings in the
  task's Notes, the design request here. After the owner's decision: patch docs before any src/ edit, then the
  fix, its tests, docs, notch, release-note entry and the rebuild.
- DEPENDENCIES: TASK-2026-10-16-recheck_contract_consumers_when_provider_changes (completed, 0.2.8250: the marks,
  the meld's catch-up and the race test marked xfail with the task's id); the 0.2.8227 rule (a meld racing a sever
  refuses cleanly) and the 0.2.8231 lock rule (the ward's emissions run after the transaction); custody of
  conduit.py, conduit_ward.py, meld.py and the hydrators, asked for before any edit (no active board row names
  them today); tests_components.md is held by melder_2 until its turn-in (M2-38, recorded in
  EPIC-2026-10-25-codegen_room_policy_defects).
- EXIT_GATE: the child task closed with its exit gate met; src_architecture's "Known, not fixed" entry replaced by
  the fix's invariant; board and artifact sync.
- FAILURE_ESCALATION: DECISION_REQUEST for the design; CONFLICT if ordering the fan-out inside the notch window
  breaks the ward or mediator lock order; BLOCKER while a file the fix needs is held by another lane.

## Goals (Outcomes)
- The race re-measured on 0.2.8267, the GIL off and on, and its in-Book variant (a dependent melded while its own
  Book notches the dependency) measured for the first time.
- The mechanism read whole at today's lines and the two designs costed - refuse at the failure sites, or order the
  fan-out under the borrowers' frozen gates - for the owner's decision.
- After the decision: no meld in flight during a notch returns an object built with a SpellContract default or
  raises an internal RuntimeError, in either GIL mode.

## Non-Goals (Explicit Exclusions)
- Rule 2's marks and the meld's catch-up: they make the next meld correct and stay as they are.
- The lent consumer's Book-local provider loss (TASK-2026-10-16-investigate_lent_consumer_provider_loss, backlog)
  and the seam's park-before-check order (TASK-2026-10-16-notch_seam_checks_incoming_before_parking, backlog).
- Conjure's link-later tolerance of a missing provider.

## Scope Boundaries
- In scope: melds of borrower spells whose plan resolves a contracted copy, in flight during a lender notch's
  fan-out; the three failure sites; the order of the fan-out against the notch transaction and the borrowers'
  creation gates; the in-Book variant.
- Out of scope: the Non-Goals above.

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the owner's ask (chat 2026-10-24),
  "focus on 2 and 3 make an epic for each and investigate them" - 3 being the in-flight borrower
  meld racing a lender's notch fan-out.

## Success Metrics
- Both race probes and the race test run on 0.2.8267, the GIL off and on, and recorded in the task.
- The owner's design decision recorded before any src/ edit.
- After the fix: the race test passes without its xfail marker in both GIL modes, and the race probe shows no
  unexpected exception over at least 100 GIL-off runs (the task's exit gate).

## Requirements (Functional + Non-Functional)
- Functional: after the decision, the task's exit gate.
- Non-functional: a warm meld pays nothing measurable; a notch's cost is measured before and after the fix.

## Constraints / Assumptions
- Device git is read-only for agents; the owner commits.
- Runs use /tmp copies of the tree only.
- UNKNOWN until re-measured: whether the 0.2.8249 rate and kinds hold at 0.2.8267, and whether the in-Book variant
  races at all.

## Dependencies / External References
- context_compass/artifacts/meld_contract_scan_20261015/ (the race probes and their 2026-10-16 runs; rule 2's evidence)
- tests/integration/melder/conduit/test_conduit_integration_notch_revalidation.py (the race test)

## Milestones (Track Progress)
- [x] Milestone 1: re-measured - both probes, the race test and the in-Book probe run on 0.2.8267 (task Notes).
- [ ] Milestone 2: decided - the owner chooses the design (this epic's Notes).
- [ ] Milestone 3: fixed - the task lands with its patch docs, tests, measurements, notch and rebuild.

## Stories (Required to Complete)
- none: the race is one deliverable and stays a task (Tasks).

## Tasks (Cross-Cutting or Epic-Level)
- [ ] Task: TASK-2026-10-16-order_inflight_borrower_melds_against_notch_fanout - re-measure, read the fan-out and
      the gates, cost the designs, then the fix.
- [ ] Task: Verify Ticket Microcycle enforcement on the task.

## Acceptance Criteria (Epic Done)
- The child task closed with its exit gate met, or closed on the owner's word.
- src_architecture's "Known, not fixed" entry replaced; the release note carries the fix.
- Board and artifact sync done.

## Risks / Mitigations
- Refusing at the sites keeps the window (a meld refuses where it could have built either version) and touches
  compile and hydration paths; ordering the fan-out closes the window but moves ward emissions that 0.2.8231 placed
  after the transaction on purpose. Both are costed before the owner is asked.
- A race probe is statistical: a rate over too few runs hides a regression; the exit gate asks for 100 runs.

## Applicable Anti-Patterns
- [ ] No epic-state transition without task-level evidence.
- [ ] No closure while a child task is incomplete or unaccepted.
- [ ] No program claims without source evidence from task notes.
- [ ] No src/ edit before the owner's answer and the patch docs.

## Validation / Test Approach
- probe_rule2_race_rate.py <tree> 20 and diag_race_kinds.py <tree> 400 140 from rule 2's evidence folder, and the
  race test (-k racing), on a /tmp copy, the GIL off and on; the in-Book probe beside them.
- Not run until recorded in the task's Notes.

## Rollout / Adoption Plan
- The fix ships with an entry in the running release note. No persisted state, cache generation or record version
  is expected to move (UNKNOWN until the design is written).

## Open Questions
- The design (DECISION_REQUEST, Notes): design 2, order the fan-out inside the notch's frozen window (recommended),
  or design 1, refuse cleanly at the four failure sites.
- Answered by measurement on 2026-10-25: a notch inside one Book does not race its dependents' in-flight melds
  (0 of 100 runs; the task's MEASURE note).

## Decision Log
- 2026-10-25: the epic opened on the owner's ask; its child is melder_1's existing backlog task.

## Artifact Links (Optional)
Qualified independent reviewer acceptance and direct closure follow shared `ticketing.md`;
this does not make independent review mandatory for every ticket.

- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/notch_fanout_race_20261025/ (this epic's runs and the in-Book probe; created with the first runs)
  - artifacts/meld_contract_scan_20261015/ (the race probes and their 2026-10-16 runs; rule 2's)
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: decided at closure; rule 2's folder stays with rule 2.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - none
- IF_UNKNOWN: none

## Contribution Attribution
- Ticket/Work Author(s): melder_0 (synaptic_python_developer); prose; this epic; 2026-10-25.
- Published By: UNKNOWN (local repository; not published)
- Independent Review: none requested

## Notes
- DATETIME: 2026-10-25T00:16:54Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner's ask (chat 2026-10-24): "focus on 2 and 3 make an epic for each and investigate them" - 3 being
    the in-flight borrower meld racing a lender's notch fan-out (p1: one of its outcomes returns a wrong object
    silently). This epic takes melder_1's backlog task
    TASK-2026-10-16-order_inflight_borrower_melds_against_notch_fanout as its child, moved to tickets/tasks/,
    in_progress for melder_0 (melder_1 told by M0-222), and keeps the two related backlog tasks out (the lent
    consumer's provider loss; the seam's park-before-check order). The investigation is read-only on src/ and
    tests/, runs on a /tmp copy of 0.2.8267 with the GIL off and on, adds the in-Book probe the task asks for,
    and ends in one DECISION_REQUEST: refuse at the failure sites, or order the fan-out under the borrowers'
    frozen gates.
  EVIDENCE:
  - context_compass/tickets/tasks/2026-10-16_order_inflight_borrower_melds_against_notch_fanout_task.md:1-255
  - context_compass/system_docs/src_architecture.md:2372-2382
  IMPACT: The design is put to the owner with today's mechanism and cost, not the 0.2.8249 measurement.
  NEXT: Run probe_rule2_race_rate.py, diag_race_kinds.py and the race test on the /tmp copy, the GIL off and on.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T00:48:34Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION_REQUEST
  CLAIM: Milestone 1 is met (the child task's MEASURE, FACT and TRADEOFF notes): the race reproduces at 0.2.8267,
    a notch inside one Book does not race, and the cause is the borrower fan-out running after the notch's
    frozen window reopens the borrowers' gates. For the owner: design 2 (move the fan-out inside the frozen
    window; recommended - one cause, the freeze already exists, warm melds untouched) or design 1 (refuse
    cleanly at the four failure sites; keeps the window).
  EVIDENCE: context_compass/tickets/tasks/2026-10-16_order_inflight_borrower_melds_against_notch_fanout_task.md:1-403
  IMPACT: The fix waits on this one choice.
  NEXT: Ask the owner.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Closure Confirmation
- [ ] Work walkthrough shared with user
- [ ] Criteria, required tests/reviews and delegated acceptance or reserved-owner disposition recorded
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.

## Noting Behavior
- Note focus: program-level direction, cross-story tradeoffs, and tranche order.
- Add notes when priorities, sequencing, or scope boundaries change.
- Reference story/task evidence instead of duplicating tactical execution logs.
- Keep notes append-only and preserve UNKNOWN-first promotion discipline.
- Multiple meaningful comments may hold evidence directly; no forced body copy before ordinary
  continuation. Current scope/state/decisions/handoff stay coherent at material transitions.

## Context / Handoff Summary
Scope: the in-flight borrower meld racing a lender's notch fan-out (p1), in one child task. State: in_progress,
melder_0. Milestone 1 met: the race reproduces at 0.2.8267 (GIL off 10 of 20 and 200 of 400; GIL on 0), an in-Book
notch does not race (0 of 100), and the cause is the fan-out running after the notch's frozen window ends. Waiting
on: the owner's choice of design (Notes; Open Questions). Then: patch docs, red tests, the fix, notch and rebuild.

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
