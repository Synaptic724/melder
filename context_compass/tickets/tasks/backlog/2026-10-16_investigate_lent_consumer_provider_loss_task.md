# Task: investigate_lent_consumer_provider_loss - a lent contract consumer keeps building after its Book loses the provider

## Metadata
- Task ID: TASK-2026-10-16-investigate_lent_consumer_provider_loss
- Story: none (standalone backlog task; decision D4 of TASK-2026-10-16-recheck_contract_consumers_when_provider_changes)
- Status: draft
- Owner: user
- Agent Name: unassigned
- Agent Role: UNKNOWN
- Priority: p2
- Created: 2026-10-16T11:48:11Z
- Updated: 2026-10-16T11:48:11Z

## Objective
Find out what should happen - and why it does not - when a Book melds a SpellContract consumer that it borrows (a
"lent consumer") after that Book alone has lost the consumer's provider. In the probe, the consumer is owned by Book
O and lent to Book T, and O and T both borrow its provider from a lender L. When T drops its index link to the
provider, or severs its link to L, T keeps building the consumer over the old provider through the fast meld door,
today and with rule 2's marking, although T no longer holds any provider for the contract. Outcome: the intended
behaviour confirmed with the owner, the mechanism explained from the source, and a fix design for the owner's
decision. Investigation only.

## Ticket Contract
- ENTRY_GATE: the owner schedules the task and assigns an agent; an active board row; the probe re-run on the
  then-current tree (rule 2 may have landed by then).
- EXECUTION_BOUNDARY: read-only on `src/`; probes and runs under artifacts/; this ticket's Notes; a patch draft only
  if the owner asks for one.
- DEPENDENCIES: TASK-2026-10-16-recheck_contract_consumers_when_provider_changes (rule 2: a borrower Book marks the
  consumers of a changed copy's key, which reaches consumers the Book owns and not the ones it borrows); its probe
  artifacts/meld_contract_scan_20261015/probe_rule2_lent_consumer.py and runs.
- EXIT_GATE: the owner confirms what a Book should do with a lent consumer whose provider it no longer holds; the
  mechanism is recorded with evidence (which state is per Book, which is per lineage or per spell, and why the
  Book's validation flag drops); a fix design with its cost and its tests - or the owner closes it as intended.
- FAILURE_ESCALATION: DECISION_REQUEST for the intended semantics; CONFLICT if per-Book contract presence cannot be
  represented without a per-meld check.

## Scope Boundaries
- In scope: lent SpellContract consumers; per-Book contract presence against the frame-wide lineage state and the
  per-spell CreationContext; the Book validation flag and the fast meld door for a borrowed spell; the paths that
  take a provider copy away from one Book (uncontract, index unlink, sever, remove-all, a notch's park).
- Out of scope: rule 2's marking of a Book's own consumers; a notch of a provider's dependencies (rule 2's D2); any
  `src/` change before the owner's decision.

## State Transition Event
- from_state: draft
- to_state: draft
- transition_reason: opened in the backlog at the owner's request (chat 2026-10-16, on decision D4: "not sure what
  this is bug make a task for investigation").

## Steps / Checklist
- [ ] Re-run the probe on the current tree, both GIL modes; extend it to an uncontract, a remove-all and a notch of
      the provider while T holds a version-anchored grant.
- [ ] Read why T's flag drops and which state answers T's meld (RiskManager refresh, the lent lineage's state, the
      per-spell context), whole; record it.
- [ ] Ask the owner the intended semantics; draft the fix design and its cost.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence
      before dependent work; no forced body copy.

## Deliverables
- Findings with evidence; the owner's answer on the semantics; a fix design (or a closure as intended).

## Files / Paths Impacted
- context_compass/tickets/tasks/backlog/2026-10-16_investigate_lent_consumer_provider_loss_task.md
- context_compass/artifacts/meld_contract_scan_20261015/ (the probe and its runs; new probes land beside them)

## Validation
- Not run.
- Recommended commands:
  - PYTHONPATH=src:context_compass/artifacts/meld_contract_scan_20261015 python
    context_compass/artifacts/meld_contract_scan_20261015/probe_rule2_lent_consumer.py (GIL off and on)

## Risks / Rollback Notes
- A fix that checks contract presence per meld brings back the cost rule 2 removes (about 1.5 ms a meld); the
  design should mark on the Book's own provider changes instead.

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

- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/meld_contract_scan_20261015/probe_rule2_lent_consumer.py
  - artifacts/meld_contract_scan_20261015/runs/probe_rule2_lent_consumer_gil0.txt
  - artifacts/meld_contract_scan_20261015/runs/probe_rule2_lent_consumer_gil1.txt
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: decided at closure (the files stay in rule 2's evidence folder)

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - per-Book contract presence for a borrowed SpellContract consumer
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Multiple meaningful comments or authorized documents may hold findings directly; no forced
  body copy of every finding is required before ordinary continuation.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Contribution Attribution
- Ticket/Work Author(s): melder_1 (synaptic_python_developer); prose; created 2026-10-16T11:48:11Z; evidence in Notes.
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none yet

## Notes
- DATETIME: 2026-10-16T11:48:11Z
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The case, as probed on the 0.2.8247 tree (Python 3.14.7t, GIL off and on, same results; monkeypatches only).
    Consumer C (a SpellContract consumer) is owned by Book O and lent to Book T; O and T both index-link lender L's
    provider; both meld C (version A). T then drops its index link to the provider, or severs its link to L. T's
    next melds of C still build A, through the fast door (no gate entry): T's validation flag is down, because C's
    lineage is `valid` and T's provider copy is unregistered from RiskManager. Today's per-meld contract scan runs
    only inside the gate, so it never sees this; rule 2's marking reaches only consumers a Book owns, and C is O's.
    With the provider kept, the same lent consumer follows a lender notch in both Books with one rebuild in all
    (its CreationContext is per spell).
  EVIDENCE:
  - context_compass/artifacts/meld_contract_scan_20261015/probe_rule2_lent_consumer.py:1-121
  - context_compass/artifacts/meld_contract_scan_20261015/runs/probe_rule2_lent_consumer_gil0.txt:1-63
  - context_compass/artifacts/meld_contract_scan_20261015/runs/probe_rule2_lent_consumer_gil1.txt:5-67
  - src/melder/aether/conduit/meld/conduit_meld.py:576-580
  - src/melder/aether/aetheric_frame/dev_ops/risk_manager/risk_manager.py:663-701
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:1623-1680
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:1839-1886
  IMPACT: A Book can build a borrowed consumer against a provider it no longer borrows; the scan never closed this,
    so rule 2 neither causes nor fixes it.
  NEXT: When scheduled, re-run the probe on the current tree and read the flag and state path whole.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Backlog draft (2026-10-16T11:48:11Z), opened at the owner's request on rule 2's decision D4; not scheduled, no agent
assigned. Scope: what a Book should do with a lent SpellContract consumer whose provider it no longer holds, why it
keeps building it today (the Book flag drops; lineage state and context are not per Book), and a fix design.
Evidence: the probe and runs in artifacts/meld_contract_scan_20261015/ (Note above). Rule 2 does not change this
case.
Next: (1) the owner schedules it; (2) re-run the probe on the then-current tree; (3) the semantics question and the
fix design.

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
