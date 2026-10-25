# Task: order_inflight_borrower_melds_against_notch_fanout - a borrower meld in flight during a lender's notch must end in a version or a clean refusal

## Metadata
- Task ID: TASK-2026-10-16-order_inflight_borrower_melds_against_notch_fanout
- Story: none; parent EPIC-2026-10-25-notch_fanout_inflight_melds (split off
  TASK-2026-10-16-recheck_contract_consumers_when_provider_changes by the owner's decision of 2026-10-16)
- Status: ready
- Owner: user
- Agent Name: melder_0
- Agent Role: synaptic_python_developer
- Priority: p1
- Created: 2026-10-16T15:54:20Z
- Updated: 2026-10-25T13:02:02Z

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
- to_state: in_progress
- transition_reason: the owner's ask (chat 2026-10-24), "focus on 2 and 3 make an epic for each and investigate them",
  scheduled it under EPIC-2026-10-25-notch_fanout_inflight_melds; melder_0 re-measures it on 0.2.8267
  and puts the design choice to the owner.

- from_state: in_progress
- to_state: ready
- transition_reason: design 2 decided and planned (PLAN note); the owner holds implementation until he schedules
  it (chat 2026-10-25T12:08Z: "just design it but don't do any work on the notch_fanout race").

## Steps / Checklist
- [x] Re-run probe_rule2_race_rate.py and diag_race_kinds.py on 0.2.8267
      (EPIC-2026-10-25-notch_fanout_inflight_melds), GIL off and on; add an in-Book probe (a dependent melded on
      threads while its own Book notches the dependency).
- [x] Read whole: `Conduit.notch_spell` and its fan-out, `ConduitWard._emit_index_notch`, the receivers' mutators,
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
- context_compass/tickets/tasks/2026-10-16_order_inflight_borrower_melds_against_notch_fanout_task.md
- context_compass/artifacts/notch_fanout_race_20261025/ (the re-measure's runs and the in-Book probe)
- context_compass/artifacts/meld_contract_scan_20261015/ (the probes and their 2026-10-16 runs; rule 2's evidence)
- after approval: the `src/` files the design names, their tests, system docs, release_docs/next_version_release.md

## Validation
- Not run.
- Recommended commands:
  - python -X gil=0 (and -X gil=1)
    context_compass/artifacts/meld_contract_scan_20261015/probe_rule2_race_rate.py <tree> 20
  - python -X gil=0 context_compass/artifacts/meld_contract_scan_20261015/diag_race_kinds.py <tree> 400 140
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
  - artifacts/meld_contract_scan_20261015/diag_race_kinds.py
  - artifacts/meld_contract_scan_20261015/probe_rule2_race_rate.py
  - artifacts/meld_contract_scan_20261015/runs/diag_race_kinds_before_gil0.txt
  - artifacts/meld_contract_scan_20261015/runs/diag_race_kinds_after_gil0.txt
  - artifacts/meld_contract_scan_20261015/runs/probe_rule2_race_rate_before_gil0.txt
  - artifacts/meld_contract_scan_20261015/runs/probe_rule2_race_rate_after_gil0.txt
  - artifacts/meld_contract_scan_20261015/runs/probe_rule2_race_rate_before_gil1.txt
  - artifacts/meld_contract_scan_20261015/runs/probe_rule2_race_rate_after_gil1.txt
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
- Ticket/Work Author(s): melder_1 (synaptic_python_developer); prose; created 2026-10-16T15:54:20Z; evidence in Notes.
  melder_0 (synaptic_python_developer); investigation and evidence; from 2026-10-25 (Notes).
- Published By: UNKNOWN (a local ticket file; not published)
- Independent Review: none yet

## Notes
- DATETIME: 2026-10-16T15:54:20Z
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
  - context_compass/artifacts/meld_contract_scan_20261015/runs/probe_rule2_race_rate_before_gil0.txt:1-26
  - context_compass/artifacts/meld_contract_scan_20261015/runs/probe_rule2_race_rate_after_gil0.txt:1-26
  - context_compass/artifacts/meld_contract_scan_20261015/runs/probe_rule2_race_rate_before_gil1.txt:1-24
  - context_compass/artifacts/meld_contract_scan_20261015/runs/probe_rule2_race_rate_after_gil1.txt:1-24
  - context_compass/artifacts/meld_contract_scan_20261015/runs/diag_race_kinds_before_gil0.txt:193-197
  - context_compass/artifacts/meld_contract_scan_20261015/runs/diag_race_kinds_after_gil0.txt:209-213
  IMPACT: The race predates rule 2 at the same rate; rule 2 makes the "Cannot build CreationContext" kind more
    frequent because more melds pass the gate without a forced rebuild.
  NEXT: When scheduled, re-run both probes on the then-current tree.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-10-16T15:54:20Z
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
  - context_compass/artifacts/meld_contract_scan_20261015/runs/diag_race_kinds_after_gil0.txt:61-86
  - context_compass/artifacts/meld_contract_scan_20261015/runs/diag_race_kinds_after_gil0.txt:87-147
  - context_compass/artifacts/meld_contract_scan_20261015/runs/diag_race_kinds_after_gil0.txt:148-208
  - context_compass/artifacts/meld_contract_scan_20261015/runs/diag_race_kinds_before_gil0.txt:134-192
  - src/melder/aether/conduit/conduit.py:5725-5751
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:1060-1088
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/hydration/many_only_hydrator.py:320-341
  - src/melder/aether/conduit/meld/meld.py:866-929
  IMPACT: One gap - in-flight borrower melds are not ordered against a notch's fan-out - behind four symptoms; (a)
    returns a wrong object silently, which is why the task is p1.
  NEXT: When scheduled, read the fan-out and the notch's gate freeze whole (second checklist step).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-25T00:16:54Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Scheduled under EPIC-2026-10-25-notch_fanout_inflight_melds at the owner's ask (chat 2026-10-24),
    "focus on 2 and 3 make an epic for each and investigate them";
    melder_0 takes it over from melder_1, its author (M0-222). The re-measure, on a /tmp copy of the 0.2.8267 tree:
    (1) probe_rule2_race_rate.py <tree> 20 with the GIL off and on, and diag_race_kinds.py <tree> 400 140 with it
    off; (2) the race test (-k racing) in both modes; (3) the in-Book probe this task asks for: a dependent melded
    on four threads while its own Book notches the dependency; (4) a whole read of `Conduit.notch_spell` and its
    fan-out, `ConduitWard._emit_index_notch`, the receivers' contracted-map mutators, the notch transaction's seal
    and gate freeze, the creation gates a borrower meld holds, `Meld._execute_admitted`, the hydrators'
    `_resolve_spell_lookup` and Phase 8's `_allow_missing_contract_providers`, with why the emissions run after the
    transaction (0.2.8231); (5) both designs costed - refuse at the three sites, or order the fan-out under the
    borrowers' frozen gates.
  EVIDENCE:
  - context_compass/artifacts/meld_contract_scan_20261015/probe_rule2_race_rate.py:1-97
  - context_compass/artifacts/meld_contract_scan_20261015/diag_race_kinds.py:1-178
  - tests/integration/melder/conduit/test_conduit_integration_notch_revalidation.py:626-675
  IMPACT: The owner chooses the design on today's mechanism and cost, not on the 0.2.8249 measurement.
  NEXT: Copy the 0.2.8267 tree to /tmp and run the rate probe, the GIL off and on.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T00:27:10Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: Re-measured on a /tmp copy of the 0.2.8267 working tree (git 9f240166f), Python 3.14.7 free-threaded.
    probe_rule2_race_rate.py <tree> 20: GIL off, 10 of 20 runs end a thread with an unexpected exception (12x
    AttributeError "'SpellContract' object has no attribute 'ping'", 6x RuntimeError "Cannot build
    CreationContext before spell_codegen_creation exists."); no meld returned B, the first meld after each race
    returned A. GIL on, 0 of 20. diag_race_kinds.py <tree> 400 150: GIL off, 200 of 400 runs end a thread
    unexpected - 265x the SpellContract AttributeError, 75x the CreationContext RuntimeError, 11x RuntimeError
    "many_only manifest references unknown spell_id", and 1x RuntimeError "No-overrides codegen step schema
    references unknown spell_id" (a sibling of the many_only kind, from the generalized/no-overrides hydrator;
    not seen on 2026-10-16). The race reproduces unchanged at 0.2.8267; the retired scan's MeldExecutionError
    melder_1 saw before rule 2 is gone, as expected.
  EVIDENCE:
  - artifacts/notch_fanout_race_20261025/runs/probe_rule2_race_rate_0_2_8267_gil0.txt:1-30
  - artifacts/notch_fanout_race_20261025/runs/probe_rule2_race_rate_0_2_8267_gil1.txt:24-27
  - artifacts/notch_fanout_race_20261025/runs/diag_race_kinds_0_2_8267_gil0.txt:211-216
  IMPACT: The race holds at the same rate on today's tree, so the design decision rests on current behaviour.
  NEXT: Confirm the mechanism at today's lines (next note).
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T00:27:10Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: melder_1's mechanism holds at 0.2.8267, read at today's lines. `Conduit.notch_spell` calls
    `mediator.end_transaction(expected_type="notch", success=True)` and only THEN, outside the transaction,
    runs the borrower fan-out - `_deactivate_borrowed_spell(outgoing_id)`, `_activate_borrowed_spell(...)` and
    `ConduitWard._emit_index_notch(...)` - so a borrower meld already past its creation gate is not ordered
    against the park and the reactivate. The diag timelines show exactly that interleave (a meld's pass-done /
    ctx-built landing between deactivate and reactivate). The two sites melder_1 named are confirmed: Phase 8's
    `_allow_missing_contract_providers` (site a, the raw SpellContract default compiled while a copy is parked)
    and the many_only hydrator's `_resolve_spell_lookup`, which raises "many_only manifest references unknown
    spell_id" when a plan names a parked version (site b); the new 4th kind is the same site b in the
    no-overrides hydrator. The two designs (refuse at the sites, or order the fan-out under the borrowers'
    frozen gates) are unchanged; the whole-read of the fan-out and gates and the in-Book probe are the next
    tranche before the design is costed for the owner.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:5792-5801
  - src/melder/aether/spellbook/spell_compiler/codegen_creation_system/strategies/many_only/hydration/many_only_hydrator.py:321-340
  - src/melder/aether/spellbook/spell_compiler/spell_analyzer/strategies/spell_occurrence_graph_analyzer_strategy.py:1073-1088
  - artifacts/notch_fanout_race_20261025/runs/diag_race_kinds_0_2_8267_gil0.txt:5-35
  IMPACT: The fix is one of the two designs, after the owner decides; no src edit before patch docs.
  NEXT: Read the fan-out and the gates whole and add the in-Book probe, then cost the two designs for the owner.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T00:48:34Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: MEASURE
  CLAIM: The in-Book probe this task asked for, run on the /tmp copy of 0.2.8267 (the probe is new:
    context_compass/artifacts/notch_fanout_race_20261025/probes/probe_inbook_notch_race.py): the integration file's one-Book chain
    (QChain -> PChain -> IDep, all `many`,
    dynamic, caching off) with DepB staged on IDep's index; four threads meld QChain while the main thread
    notches IDep 20 times between DepA and DepB, ending on DepA. GIL off: 0 of 20 runs and 0 of 100 runs end a
    thread with an unexpected exception (100 runs: 662272 melds returned DepA's tag, 869 DepB's, no refusals,
    and every first meld after the race returned DepA's). GIL on: 0 of 20. So a notch inside one Book does
    not race its dependents' in-flight melds; the race is specific to the borrower fan-out.
  EVIDENCE:
  - context_compass/artifacts/notch_fanout_race_20261025/runs/probe_inbook_notch_race_0_2_8267_gil0_100runs.txt:1-108
  - context_compass/artifacts/notch_fanout_race_20261025/runs/probe_inbook_notch_race_0_2_8267_gil0_20runs.txt:1-28
  - context_compass/artifacts/notch_fanout_race_20261025/runs/probe_inbook_notch_race_0_2_8267_gil1_20runs.txt:1-28
  IMPACT: It answers the scope question the task left open (In scope: whether a notch inside one Book races the same
    way): it does not, so the fix concerns borrowers only.
  NEXT: Record why (the fan-out read, next note).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-25T00:48:34Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: Read whole at 0.2.8267. The notch transaction already seals the borrowers and freezes their runtime:
    `NotchTransactionStrategy.build_start_plan` extends the EXCLUSIVE seal from the acting conduit to every
    conduit linked to it (its borrowers and providers, from the DevOps registry) and stashes exactly that set
    as the quiesce footprint; `on_start` quiesces each of those lineages' CreationGates (new melds park,
    in-flight melds drain to zero) and `on_end` reopens them at root finalize, which `end_transaction` runs.
    `Conduit.notch_spell` calls `end_transaction(success=True)` and only then runs the borrower fan-out
    (`_deactivate_borrowed_spell`, `_activate_borrowed_spell`, `ConduitWard._emit_index_notch`), so the
    fan-out runs with the borrowers' gates open again - the window the race lives in. In one Book everything a
    notch changes (the seam, the lineage marks of rule 2's D2) runs before `on_end`, which is why the in-Book
    probe shows nothing. The fan-out starts no transaction and touches no gate: each step takes the borrower
    Book's lock for the map change, releases it, then marks through SpellSystemStates (registry -> state ->
    RiskManager); the ward emission takes ward -> contract -> borrower Book, the order sever takes.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:5652-5804
  - src/melder/aether/conduit/conduit.py:6308-6337
  - src/melder/aether/conduit/conduit.py:6339-6382
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:2322-2387
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/notch_transaction_strategy.py:113-219
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/notch_transaction_strategy.py:272-304
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/notch_transaction_strategy.py:307-325
  - src/melder/aether/spellbook/spellbook.py:1717-1794
  - src/melder/aether/spellbook/spellbook.py:1796-1868
  - src/melder/aether/spellbook/spellbook.py:5682-5733
  IMPACT: The freeze that would close the window is already in place; the fan-out only runs outside it.
  NEXT: Cost the two designs against this (next note).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-25T00:48:34Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: TRADEOFF
  CLAIM: Design 2, order the fan-out inside the frozen window: run the three fan-out calls before
    `end_transaction(success=True)`, while the borrowers' gates are drained. It removes all four failure kinds
    at their one cause, reuses the freeze already there, matches what an in-Book notch already does (0 of 100),
    and leaves warm melds untouched. Costs to settle in its patch doc: (i) a fan-out error inside the window
    ends the transaction failed while the Book's switch stands - undo the switch with the Spellbook's existing
    refused-notch reversal, or let it stand and raise (today a fan-out error after the window leaves the same
    half-state, so neither is a regression); (ii) borrowers' melds stay parked for the fan-out's duration too
    (a Book map change and the marks per peer; rule 2 measured the notch walk at 0.2-0.5 ms per 200
    dependents), only while a notch runs; (iii) a lock audit for one case - a thread holding a borrower Book's
    lock while melding on a sealed conduit would park at the frozen gate while the fan-out waits for that lock;
    (iv) the commit hooks (structural validator, dirty marker) then run after the fan-out; (v) the 0.2.8231
    threading note on `_emit_index_notch` and src_architecture's sequences change.
    Design 1, refuse at the failure sites: make each of the four kinds the clean SpellbookValidationError -
    Phase 8's missing-provider tolerance at meld time (conjure's link-later tolerance stays), the many_only and
    no-overrides hydrators' unknown-spell_id lookups (with a re-plan), `Meld._execute_admitted` after a failed
    rebuild, and the waiter of a failed build. It keeps the window: a meld racing a notch refuses where a meld
    a moment later builds the new version, which is weaker than an in-Book notch, and it is four changes in
    compile, hydration and meld code, each with its own tests. Recommendation: design 2.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:5652-5804
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/notch_transaction_strategy.py:272-304
  IMPACT: The owner chooses between closing the window (2) and making racing melds refuse cleanly (1).
  NEXT: Put the choice to the owner (next note).
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-25T00:48:34Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION_REQUEST
  CLAIM: For the owner: design 2 (order the fan-out inside the notch's frozen window; recommended) or design 1
    (refuse cleanly at the four failure sites)? With design 2, the patch doc also proposes how a fan-out error
    inside the window ends (recommended: undo the switch with the existing refused-notch reversal, so a notch
    either stands with its borrowers moved or leaves everything as it was).
  EVIDENCE: context_compass/tickets/tasks/2026-10-16_order_inflight_borrower_melds_against_notch_fanout_task.md:1-306
  IMPACT: No src edit until the owner chooses; then patch docs, red tests, the fix, measurements, notch and rebuild.
  NEXT: Ask the owner.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-10-25T00:48:34Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: M1-61 (melder_1's NOTICE, 2026-10-25T00:40:05Z, consumed here), answering M0-222: melder_1 holds none of
    conduit.py, conduit_ward.py, meld.py or the hydrators. Its S2 story
    (STORY-2026-10-17-notch_moves_signature_by_incoming_key_only, research now) may later need conduit.py's
    `remove_from_spell_index` besides spellbook.py and spell_index.py, and melder_1 will ask before touching
    conduit.py. This task's design 2 edits `Conduit.notch_spell` in the same file: whichever lands second
    re-reads the file and remaps its citations.
  EVIDENCE: context_compass/tickets/stories/2026-10-17_notch_moves_signature_by_incoming_key_only_story.md:350-363
  IMPACT: conduit.py is free for this task's fix today; the two lanes coordinate before either edits it.
  NEXT: Before a conduit.py edit, check melder_1's board row and ask.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-25T03:01:26Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: M1-62 (melder_1's NOTICE, 2026-10-25T02:47:38Z, ACK requested; consumed here, ACK in M0-224): melder_1
    opens STORY-2026-10-25-probe_and_purge_reach_every_version and will edit meld.py (purge discovery, a by-id
    lookup), conduit_meld.py, spellspace_meld.py, spellbook.py and the purge and probe docstrings of conduit.py and
    spell_space.py - tests first, src after its patch docs - notching above 0.2.8268. melder_0 holds neither
    conduit.py nor meld.py today: this task waits on the owner's design choice, and its design 2 edits
    `Conduit.notch_spell` and the meld's catch-up. Whichever lane edits second re-reads the files and remaps its
    citations, and melder_0 asks melder_1 before this task's first edit of either file.
  EVIDENCE:
  - context_compass/tickets/stories/2026-10-25_probe_and_purge_reach_every_version_story.md:34-38
  - context_compass/tickets/tasks/2026-10-16_order_inflight_borrower_melds_against_notch_fanout_task.md:380-394
  IMPACT: No custody conflict now; notches go in landing order (D-10's included).
  NEXT: Before this task's first conduit.py or meld.py edit, check melder_1's board row and ask.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-25T09:08:41Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: M1-67 (melder_1's NOTICE, 2026-10-25T08:40:52Z, consumed here): melder_1 holds spell_index.py, bind.py,
    spellbook.py, lookup_container.py, aetheric_frame.py, conduit.py (docstrings), restore_engine.py,
    graft_runner.py, README.md and 35 tests that stage versions under another signature, for
    STORY-2026-10-17-notch_moves_signature_by_incoming_key_only (S2), and notches above D-10. Either design here
    changes when `Conduit.notch_spell` runs its borrower fan-out, so this task's fix touches conduit.py; it is
    waiting on the owner's design choice and needs none of those files now. M0-228 tells melder_1 so, and that D-10
    has landed and been rebuilt at 0.2.8270.
  EVIDENCE:
  - context_compass/tickets/stories/2026-10-17_notch_moves_signature_by_incoming_key_only_story.md
  - context_compass/tickets/tasks/2026-10-16_order_inflight_borrower_melds_against_notch_fanout_task.md:396-413
  IMPACT: When the owner picks a design, the fix agrees custody of conduit.py with melder_1 before its first edit.
  NEXT: The owner chooses the design (2 recommended) and assigns an implementer.
  REREAD: REQUIRED
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-25T11:22:22Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: DECISION
  CLAIM: The owner's decision (chat 2026-10-25T11:17Z, answering the DECISION_REQUEST): design 2 - run the
    borrower fan-out inside the notch's frozen window, so a borrower meld already past its gate is ordered
    against the park and the reactivation. melder_0 implements it after D-20 lands (the owner's same message:
    "finish the D-20 and its epic"); conduit.py custody is agreed with melder_1 (S2) before the first edit, and
    the patch docs come before any src/ edit.
  EVIDENCE:
  - context_compass/tickets/tasks/2026-10-16_order_inflight_borrower_melds_against_notch_fanout_task.md:365-380
  IMPACT: The design question is closed; the fix is scheduled behind D-20.
  NEXT: After D-20: ask melder_1 for conduit.py, then the patch docs for design 2.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

- DATETIME: 2026-10-25T12:10:50Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: PLAN
  CLAIM: Design 2 implementation plan, recorded for whoever implements it; the owner (chat 2026-10-25T12:08Z): "just
    design it but don't do any work on the notch_fanout race". (1) In `Conduit.notch_spell`, move the borrower fan-
    out (`_deactivate_borrowed_spell`, `_activate_borrowed_spell`, `ConduitWard._emit_index_notch`) to run before
    `end_transaction(success=True)`, while `NotchTransactionStrategy` holds the sealed footprint and the borrowers'
    CreationGates are quiesced (`on_start`) - the freeze `on_end` releases. (2) A fan-out error inside the window:
    undo the switch with the Spellbook's existing refused-notch reversal, end the transaction failed and re-raise,
    so a notch either stands with every borrower moved or leaves everything as it was. (3) Lock audit before the
    edit: a thread holding a borrower Book's lock while melding on a sealed conduit would park at the frozen gate
    while the fan-out waits for that lock - prove no such path (or take the Book lock inside the gate order) and pin
    it with a test. (4) Order changes to carry: the commit hooks (structural validator, dirty marker) then run after
    the fan-out; the 0.2.8231 threading note on `_emit_index_notch`; src_architecture's notch sequence. (5) Tests:
    the existing race test (-k racing) and probe_rule2_race_rate.py / diag_race_kinds.py must show 0 of the four
    failure kinds over 20+ runs with the GIL off; a symptom-named test that a meld racing a notch returns the
    outgoing or the incoming version, never a raw-default consumer; the fan-out-error reversal test. Measure park
    time per notch (rule 2: 0.2-0.5 ms per 200 dependents). (6) Custody: conduit.py is shared - melder_1 (S2) and
    melder_3 (store slots, with melder_1's OK) touch it; agree custody first, patch docs before src. No src/ or test
    edit has been made for this task.
  EVIDENCE:
  - context_compass/tickets/tasks/2026-10-16_order_inflight_borrower_melds_against_notch_fanout_task.md:304-360
  IMPACT: The design is complete and handed off; implementation waits for the owner to schedule it.
  NEXT: The owner schedules the implementation (any agent); it starts with the lock audit and the patch docs.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Scheduled 2026-10-25 under EPIC-2026-10-25-notch_fanout_inflight_melds (the owner's ask); in_progress, melder_0
(taken over from melder_1, its author; M0-222). Scope: a borrower meld in flight during a lender notch's fan-out must
end in a version or the clean SpellbookValidationError refusal, never an object built with the SpellContract default
or an internal RuntimeError. State: re-measured on 0.2.8267 - the race reproduces (GIL off 10 of 20 and 200 of 400
runs; GIL on 0), a fourth kind joined the three; a notch inside one Book does not race (0 of 100); the cause is the
fan-out running after `end_transaction` reopens the borrowers' gates, which the notch already drains for its window.
Both designs are costed (TRADEOFF note); design 2 is recommended. Waiting on: the owner's choice (DECISION_REQUEST).
Then: patch docs for the chosen design, red tests (the race test without its xfail marker), the fix, measurements,
notch and rebuild.

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
