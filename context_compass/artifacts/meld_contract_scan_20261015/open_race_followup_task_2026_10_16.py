"""Open the backlog task for the meld-vs-notch race the owner split off rule 2, and its artifact row (melder_1).

usage (from context_compass/): python <this script> <UTC now> [--check]
"""
import pathlib
import sys

NOW = sys.argv[1]
CHECK = "--check" in sys.argv[2:]
TASK_ID = "TASK-2026-10-16-order_inflight_borrower_melds_against_notch_fanout"
TICKET = pathlib.Path("tickets/tasks/backlog/2026-10-16_order_inflight_borrower_melds_against_notch_fanout_task.md")
ARTIFACT_BOARD = pathlib.Path("artifact_board.md")
ART = "artifacts/meld_contract_scan_20261015"
CART = "context_compass/" + ART

BODY = f"""# Task: order_inflight_borrower_melds_against_notch_fanout - a borrower meld in flight during a lender's notch must end in a version or a clean refusal

## Metadata
- Task ID: {TASK_ID}
- Story: none (standalone backlog task; split off TASK-2026-10-16-recheck_contract_consumers_when_provider_changes by
  the owner's decision of 2026-10-16)
- Status: draft
- Owner: user
- Agent Name: unassigned
- Agent Role: UNKNOWN
- Priority: p1
- Created: {NOW}
- Updated: {NOW}

## Objective
A meld of a borrower's spell that is in flight while the lender's `notch_spell` parks and reactivates the borrower's
contracted copies must return an object built against a provider version, or raise the clean
SpellbookValidationError refusal - the rule 0.2.8227 set for a meld racing a sever or an uncontract. Today, with the
GIL off, such a meld can return a consumer built with the raw SpellContract default (an AttributeError surfaces
only when the object is used), or raise one of two internal RuntimeErrors. Outcome: the mechanism confirmed on the
then-current tree, the design options with their cost for the owner's decision, then the fix with tests, docs, a
notch and the rebuild.

## Ticket Contract
- ENTRY_GATE: the owner schedules the task and assigns an agent; an active board row; rule 2 has landed (it adds the
  race test, marked xfail with this task's id); the race probes re-run on the then-current tree.
- EXECUTION_BOUNDARY: design phase: read-only on `src/`; probes under artifacts/; patch docs for the owner's approval
  before any `src/` edit. After approval: the files the approved design names - candidates are the Phase 8
  analyzer's contract resolution (a meld-time pass), `Meld._execute_admitted`, the many_only and generalized
  hydrators' manifest lookups, or `Conduit.notch_spell`'s fan-out order and the ward's index emissions - with their
  tests, system docs, the release note, the notch and the rebuild.
- DEPENDENCIES: TASK-2026-10-16-recheck_contract_consumers_when_provider_changes (rule 2: the race test, the marks
  and the meld's catch-up); conduit.py custody (melder_0's TASK-2026-10-16-public_notch_target_for_staged_versions,
  then rule 2's D3 lines); the 0.2.8227 rule and the 0.2.8231 lock rule for the ward's emissions.
- EXIT_GATE: the race test runs without its xfail marker and passes in both GIL modes; the race probe shows no
  unexpected exception over at least 100 GIL-off runs; no meld returns an object built with a SpellContract default;
  warm melds and the notch cost measured before and after; docs, notch, rebuild; the owner accepts.
- FAILURE_ESCALATION: DECISION_REQUEST for the approach (refuse at the failure sites, or order the fan-out under the
  borrowers' frozen gates); CONFLICT if ordering the fan-out inside the notch's window breaks the ward/mediator lock
  order; BLOCKER while conduit.py is held by another lane.

## Scope Boundaries
- In scope: melds of borrower spells whose plan resolves a contracted copy, in flight during a lender notch's
  fan-out (`_deactivate_borrowed_spell`, `ConduitWard._emit_index_notch` and the receivers' contracted-map
  mutators); the three failure sites (Phase 8's missing-provider tolerance at meld time, `_execute_admitted` after a
  failed rebuild, the hydrators' pool lookup of a plan's step ids); the order of the fan-out against the notch
  transaction and the borrowers' creation gates; whether a notch inside one Book races a dependent's in-flight meld
  the same way (not measured yet).
- Out of scope: rule 2's marks and catch-up (they make the next meld correct); the lent-consumer provider loss
  (TASK-2026-10-16-investigate_lent_consumer_provider_loss); `_apply_notch`'s park-before-check order
  (TASK-2026-10-16-notch_seam_checks_incoming_before_parking); conjure's link-later tolerance of a missing provider.

## State Transition Event
- from_state: draft
- to_state: draft
- transition_reason: opened in the backlog at the owner's direction (chat 2026-10-16: on the race-scope question he
  chose "Separate task (Recommended)" after confirming it concerns only contract consumers melded on another thread
  while their provider is being notched).

## Steps / Checklist
- [ ] Re-run probe_rule2_race_rate.py and diag_race_kinds.py on the current tree, GIL off and on; add an in-Book
      probe (a dependent melded on threads while its own Book notches the dependency).
- [ ] Read whole: `Conduit.notch_spell` and its fan-out, `ConduitWard._emit_index_notch`, the receivers' mutators,
      the notch transaction's seal and gate freeze (`NotchTransactionStrategy`), the creation gates a borrower meld
      holds, `Meld._execute_admitted`, the hydrators' `_resolve_spell_lookup` and Phase 8's
      `_allow_missing_contract_providers`; record why the emissions run after the transaction (0.2.8231).
- [ ] Write the design options with their cost and risk (refuse at the three sites, or order the fan-out under the
      borrowers' frozen gates), as patch docs; the owner decides.
- [ ] Build, remove the race test's xfail marker, add the site tests, measure, docs, notch, rebuild.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence
      before dependent work; no forced body copy.

## Deliverables
- The mechanism on the then-current tree, the design options and the owner's decision; then the fix with tests,
  docs, notch and rebuild.

## Files / Paths Impacted
- context_compass/tickets/tasks/backlog/2026-10-16_order_inflight_borrower_melds_against_notch_fanout_task.md
- {CART}/ (the probes and runs; new probes land beside them)
- after approval: the `src/` files the design names, their tests, system docs, release_docs/next_version_release.md

## Validation
- Not run.
- Recommended commands:
  - python -X gil=0 (and -X gil=1)
    {CART}/probe_rule2_race_rate.py <tree> 20
  - python -X gil=0 {CART}/diag_race_kinds.py <tree> 400 140
  - pytest tests/integration/melder/conduit/test_conduit_integration_notch_revalidation.py -k racing (GIL off and on)

## Risks / Rollback Notes
- Refusing at the sites keeps the window (a meld refuses where it could have built the old or the new version) and
  touches compile and hydration paths; ordering the fan-out closes the window but moves lock-sensitive ward
  emissions that 0.2.8231 placed after the transaction on purpose. Measure both; the warm meld must not pay.

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
  - {ART}/diag_race_kinds.py
  - {ART}/probe_rule2_race_rate.py
  - {ART}/runs/diag_race_kinds_before_gil0.txt
  - {ART}/runs/diag_race_kinds_after_gil0.txt
  - {ART}/runs/probe_rule2_race_rate_before_gil0.txt
  - {ART}/runs/probe_rule2_race_rate_after_gil0.txt
  - {ART}/runs/probe_rule2_race_rate_before_gil1.txt
  - {ART}/runs/probe_rule2_race_rate_after_gil1.txt
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: decided at closure (the files stay in rule 2's evidence folder)

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - borrower melds in flight during a lender notch's fan-out
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Multiple meaningful comments or authorized documents may hold findings directly; no forced
  body copy of every finding is required before ordinary continuation.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Contribution Attribution
- Ticket/Work Author(s): melder_1 (synaptic_python_developer); prose; created {NOW}; evidence in Notes.
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none yet

## Notes
- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The race as measured on 2026-10-16 (Python 3.14.7t; the 0.2.8248 tree with melder_0's 0.2.8249 notch
    target, without and with rule 2's build). Four threads meld a borrower's SpellContract consumer while the lender
    notches its provider 20 times between A and B. GIL off, 7 of 20 runs end a thread with an unexpected exception
    on both trees; GIL on, 0 of 20. Kinds (instrumented, 400 runs a tree): AttributeError "'SpellContract' object
    has no attribute 'ping'" (257 before, 242 after), RuntimeError "Cannot build CreationContext before
    spell_codegen_creation exists." (2, 73), RuntimeError "many_only manifest references unknown spell_id" (8, 9),
    one "Spell creation context was not published: the selected builder failed" (after), and before rule 2 the
    retired scan's MeldExecutionError (151). No meld returned B; the first meld after the race returned A in every
    run.
  EVIDENCE:
  - {CART}/runs/probe_rule2_race_rate_before_gil0.txt:1-26
  - {CART}/runs/probe_rule2_race_rate_after_gil0.txt:1-26
  - {CART}/runs/probe_rule2_race_rate_before_gil1.txt:1-24
  - {CART}/runs/probe_rule2_race_rate_after_gil1.txt:1-24
  - {CART}/runs/diag_race_kinds_before_gil0.txt:193-197
  - {CART}/runs/diag_race_kinds_after_gil0.txt:209-213
  IMPACT: The race predates rule 2 at the same rate; rule 2 makes the "Cannot build CreationContext" kind more
    frequent because more melds pass the gate without a forced rebuild.
  NEXT: When scheduled, re-run both probes on the then-current tree.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: {NOW}
  AUTHOR: melder_1
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The mechanism (the first occurrences' timelines and tracebacks). `notch_spell` runs the borrower fan-out
    after `end_transaction`, so a borrower meld can be between its gate and its first execution while the fan-out
    parks and reactivates the copies: (a) a target pass ran Phase 8 while the copy was parked and, in a dynamic
    world, compiled the raw SpellContract default (`_allow_missing_contract_providers`); (b) a pass compiled its plan
    against A, the fan-out parked A, and the cold door's first hydration looked the plan's step ids up in the Book's
    pool, which no longer held A (`_resolve_spell_lookup`); (c) a meld that had passed the gate was admitted after
    another meld's pass failed with the plan cleared, so its context build found no plan - which contradicts
    `_execute_admitted`'s docstring ("never ... builds from a missing plan"; true only when the rebuild succeeded);
    (d) a meld waiting on that failed build raises "was not published".
  EVIDENCE:
  - {CART}/runs/diag_race_kinds_after_gil0.txt:61-86
  - {CART}/runs/diag_race_kinds_after_gil0.txt:87-147
  - {CART}/runs/diag_race_kinds_after_gil0.txt:148-208
  - {CART}/runs/diag_race_kinds_before_gil0.txt:134-192
  - src/melder/aether/conduit/conduit.py:5725-5751
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:1060-1088
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/hydration/many_only_hydrator.py:320-341
  - src/melder/aether/conduit/meld/meld.py:866-929
  IMPACT: One gap - in-flight borrower melds are not ordered against a notch's fan-out - behind four symptoms; (a)
    returns a wrong object silently, which is why the task is p1.
  NEXT: When scheduled, read the fan-out and the notch's gate freeze whole (second checklist step).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Backlog draft ({NOW}), split off rule 2 by the owner's race-scope decision; not scheduled, no agent
assigned.
Scope: a borrower meld in flight during a lender notch's fan-out must end in a version or the clean
SpellbookValidationError refusal (the 0.2.8227 rule), never an object built with the SpellContract default or an
internal RuntimeError. Evidence: the two Notes above; probes and runs in {ART}/.
Rule 2 lands with the race test marked xfail(strict=False) naming this task; removing that marker is part of the exit
gate.
Next: (1) the owner schedules it; (2) re-run the probes, add the in-Book probe; (3) read the fan-out and gates, then
the design options for the owner.

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
"""

ROW = (f"| tickets/tasks/backlog/2026-10-16_order_inflight_borrower_melds_against_notch_fanout_task.md | "
       f"{ART}/diag_race_kinds.py | defect_reproducer | backlog | retain_as_reference | "
       "The meld-vs-notch race classifier (kinds, first tracebacks, timelines) with probe_rule2_race_rate.py and "
       "their runs (runs/diag_race_kinds_*_gil0.txt, runs/probe_rule2_race_rate_*_gil*.txt); rerun on the current "
       f"tree when the task is scheduled. | {NOW} | HELPFUL |")
ANCHOR = "<!-- END USER-DEFINED: active_artifacts -->"


def check_lengths(text, path):
    bad = [l for l in text.split("\n")
           if len(l) > 120 and not l.startswith("|") and not l.startswith("# Task:")
           and not (l.startswith("  - ") and " " not in l[4:])]
    assert not bad, (path, bad)


assert not TICKET.exists(), TICKET
check_lengths(BODY, TICKET)
board = ARTIFACT_BOARD.read_bytes().decode("utf-8")
assert b"\r" not in ARTIFACT_BOARD.read_bytes()
assert board.count(ANCHOR) == 1
assert "order_inflight_borrower_melds_against_notch_fanout" not in board
board = board.replace(ANCHOR, ROW + "\n" + ANCHOR, 1)
for path, content in ((TICKET, BODY), (ARTIFACT_BOARD, board)):
    print(("CHECK " if CHECK else "WRITE ") + str(path), len(content.split("\n")))
    if not CHECK:
        path.write_bytes(content.encode("utf-8"))
