# Task: The test maps describe the refused-save tests of 0.2.8266

## Metadata
- Task ID: TASK-2026-10-24-document_refused_cache_save_tests
- Story: none (standalone backlog task; a follow-up of TASK-2026-10-24-cache_file_write_failure_fails_meld)
- Status: draft
- Owner: user
- Agent Name: unassigned
- Agent Role: UNKNOWN
- Priority: p3
- Created: 2026-10-24T21:32:03Z
- Updated: 2026-10-24T21:32:03Z

## Objective
The test system documents (tests_architecture, tests_components) describe the tests the best-effort cache save
added at 0.2.8266. The fix lane left them out while melder_2's CI set held both documents (M2-28); that set
landed on 2026-10-24 (M2-31):
- tests/component/melder/aether/conduit/test_conduit_component_refused_cache_save_does_not_fail_meld.py - eight
  cases (five tests, three of them over a refused rename and a refused temp write) through every kind of meld door
  with the save refused: the meld returns its object, a managed lease comes back, a spellspace meld returns;
- tests/unit/melder/utilities/test_caching_system_refused_save.py - eleven `CachingSystem` save tests: the bool, no
  temp file left behind, the Windows-only rename retry and its budget, one WARNING per bundle, the per-writer temp
  name, a refused temp write or folder, a temp file that cannot be removed;
- six new cases in tests/unit/melder/spellbook/test_cache_runtime_verification.py: the Book's save seam (the flag
  left cleared, no retry until cache is staged again), the explicit save (True when written, False when refused,
  through `Spell.emit_cache_file()` too) and the conjure-end save.

## Ticket Contract
- ENTRY_GATE: the owner schedules it; an active board row; both tests documents re-read after the lanes that edit
  them last (melder_1's 0.2.8267 landing among them).
- EXECUTION_BOUNDARY: tests_architecture.md, tests_components.md and their indexes - the entries for the three
  files above; no test, src, version or release-note change; the asset rebuild last.
- DEPENDENCIES: TASK-2026-10-24-cache_file_write_failure_fails_meld (completed, 0.2.8266).
- EXIT_GATE: each file has its entry under the tests documents' instructions; both indexes regenerated and
  --check OK; the content-preservation gate met; the rebuild's two checks OK.
- FAILURE_ESCALATION: CONFLICT when another lane holds the tests documents; DECISION_REQUEST when an entry needs
  a section the instructions do not provide.

## Scope Boundaries
- In scope: the three files' entries in both tests documents.
- Out of scope: changing the tests; the src documents, which carry the fix since 0.2.8266.

## State Transition Event
- from_state: draft
- to_state: draft
- transition_reason: created as a parked follow-up at the fix's closure, as its plan recorded (Notes 22 and 28 of
  TASK-2026-10-24-cache_file_write_failure_fails_meld); no lane is opened.

## Steps / Checklist
- [ ] The owner schedules it; a board row; both tests documents and their instructions re-read.
- [ ] Slice the sections holding the neighbouring cache and meld-door tests; write the three entries.
- [ ] Both indexes regenerated, --check, the content-preservation diff; the rebuild last.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence
      before dependent work; no forced body copy.

## Deliverables
- The three entries in tests_components, and in tests_architecture where its sections call for them.

## Files / Paths Impacted
- context_compass/system_docs/tests_architecture.md and its index
- context_compass/system_docs/tests_components.md and its index

## Validation
- Not run.
- Recommended commands:
  - `python context_compass/tools/system_documents/index_document.py --doc context_compass/system_docs/tests_components.md --check`
  - the same for tests_architecture.md

## Risks / Rollback Notes
- Low: documentation only. Count the cases from the files at pickup rather than from this ticket.

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
  - none
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: none

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS:
  - none
- CONTEXT_TOPICS:
  - none
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Multiple meaningful comments or authorized documents may hold findings directly; no forced
  body copy of every finding is required before ordinary continuation.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Contribution Attribution
- Ticket/Work Author(s): melder_0 (synaptic_python_developer); prose; this ticket, at the closure of
  TASK-2026-10-24-cache_file_write_failure_fails_meld; 2026-10-24.
- Published By: UNKNOWN (local repository; not published)
- Independent Review: none requested

## Notes
- DATETIME: 2026-10-24T21:32:03Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The three files exist at 0.2.8266 with the counts in the Objective (five component tests, three over
    two failure steps; eleven CachingSystem tests; six new Book and Spell cases), green the GIL off and on
    in the fix's F6 runs; the fix deferred their tests-document entries (its Notes 22 and 28).
  EVIDENCE:
  - tests/component/melder/aether/conduit/test_conduit_component_refused_cache_save_does_not_fail_meld.py:271-434
  - tests/unit/melder/utilities/test_caching_system_refused_save.py:1-485
  - tests/unit/melder/spellbook/test_cache_runtime_verification.py:315-364
  - tests/unit/melder/spellbook/test_cache_runtime_verification.py:561-617
  - tests/unit/melder/spellbook/test_cache_runtime_verification.py:679-704
  - context_compass/tickets/tasks/completed/2026-10-24_cache_file_write_failure_fails_meld_task.md:713-731
  - context_compass/tickets/tasks/completed/2026-10-24_cache_file_write_failure_fails_meld_task.md:886-906
  IMPACT: The test maps miss three files of a landed fix until this task runs.
  NEXT: The owner schedules it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 7

## Context / Handoff Summary
Draft, parked: the entries for the three refused-save test files of 0.2.8266 (Objective). Waits for the owner's
scheduling and for the shared tests documents to be free. Evidence: the FACT note above and the fix ticket.

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
