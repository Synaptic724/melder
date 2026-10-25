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
- Updated: 2026-10-25T00:48:34Z

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
  through `Spell.emit_cache_file()` too) and the conjure-end save;
- tests/integration/melder/conduit/test_conduit_integration_windows_held_cache_bundle.py - four Windows-only
  integration tests (TASK-2026-10-24-windows_held_cache_bundle_test, after 0.2.8267; skipped elsewhere): the save
  against a rename Windows itself refuses while the bundle is held open - the premise, a hold that ends within the
  retries, one that outlasts them, and a meld through a refused save.

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
- In scope: the four files' entries in both tests documents.
- Out of scope: changing the tests; the src documents, which carry the fix since 0.2.8266.

## State Transition Event
- from_state: draft
- to_state: draft
- transition_reason: created as a parked follow-up at the fix's closure, as its plan recorded (Notes 22 and 28 of
  TASK-2026-10-24-cache_file_write_failure_fails_meld); no lane is opened.

## Steps / Checklist
- [ ] The owner schedules it; a board row; both tests documents and their instructions re-read.
- [ ] Slice the sections holding the neighbouring cache and meld-door tests; write the four entries.
- [ ] Both indexes regenerated, --check, the content-preservation diff; the rebuild last.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Record meaningful attributed findings in supported Notes/comments or authorized linked evidence
      before dependent work; no forced body copy.

## Deliverables
- The four entries in tests_components, and in tests_architecture where its sections call for them.

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
  - context_compass/tickets/tasks/completed/2026-10-24_cache_file_write_failure_fails_meld_task.md:714-732
  - context_compass/tickets/tasks/completed/2026-10-24_cache_file_write_failure_fails_meld_task.md:887-907
  IMPACT: The test maps miss three files of a landed fix until this task runs.
  NEXT: The owner schedules it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-24T22:24:45Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: M1-55 (melder_1's NOTICE, 2026-10-24T22:16:36Z, consumed here): at 0.2.8267 the tests maps count the two
    0.2.8266 regression modules (test_conduit_component_refused_cache_save_does_not_fail_meld.py,
    test_caching_system_refused_save.py) among their 863 modules, and no tests_components cluster lists them
    yet; melder_1's handoff entry names them. Cataloguing them is this draft's work, and the Windows-only file of
    TASK-2026-10-24-windows_held_cache_bundle_test joins the list when it lands.
  EVIDENCE: context_compass/system_docs/tests_components.md:3914-3931
  IMPACT: The entries go into the clusters the tests documents name; the module counts there are already right.
  NEXT: The owner schedules it.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-24T23:03:28Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: The Windows-only file landed (untracked until the owner commits it): four integration tests, skipped off
    Windows and passing on the owner's machine, the GIL off and on; melder_1's rebuild took it into the LLM
    bundles' tests corpus (M1-59). It is the Objective's fourth entry. With it the integration tier holds one
    `test_*.py` module more than the tests documents' last recount (178 among 185 `.py` files; 863 in the three
    tiers), so the counts are recounted at pickup.
  EVIDENCE:
  - tests/integration/melder/conduit/test_conduit_integration_windows_held_cache_bundle.py:1-594
  - context_compass/system_docs/tests_components.md:616-617
  - context_compass/system_docs/tests_architecture.md:481-482
  IMPACT: The draft's scope grows by one file and the two documents' module counts by one.
  NEXT: The owner schedules it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 7

- DATETIME: 2026-10-25T00:48:34Z
  AUTHOR: melder_0
  AUTHOR_ROLE: synaptic_python_developer
  TYPE: FACT
  CLAIM: M2-39 (melder_2's NOTICE, 2026-10-25T00:40:40Z; also recorded in
    EPIC-2026-10-25-codegen_room_policy_defects): after melder_2's recount of the tests maps at its turn-in,
    test_conduit_integration_windows_held_cache_bundle.py is in no tests_components cluster yet (melder_2's
    2026-10-25 handoff entry names it). Cataloguing it is this draft's work, with the two 0.2.8266 modules
    M1-55 named; tests_components.md is free now that melder_2 has turned in.
  EVIDENCE: context_compass/tickets/stories/completed/2026-10-24_testpypi_trusted_publishing_and_provenance_story.md:1-8
  IMPACT: The draft's scope is confirmed by the latest recount; recount the tiers at pickup.
  NEXT: The owner schedules it.
  REREAD: HELPFUL
  SCORE_0_TO_10: 7

## Context / Handoff Summary
Draft, parked: the entries for the three refused-save test files of 0.2.8266 and the Windows-only test file that
followed (Objective). Waits for the owner's scheduling and for the shared tests documents to be free. Evidence: the
FACT notes above and the fix ticket.

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
