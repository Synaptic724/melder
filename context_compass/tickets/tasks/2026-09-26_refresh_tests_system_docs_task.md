

# Task: tests_architecture and tests_components describe the current suite

## Metadata
- Task ID: TASK-2026-09-26-refresh-tests-system-docs
- Story: none
- Status: in_progress
- Owner: user
- Agent Name: melder_0
- Priority: p2
- Created: 2026-09-26T21:12:25Z
- Updated: 2026-09-26T21:12:25Z

## Objective
`tests_architecture.md` was last updated 2026-06-13 and `tests_components.md` scored 74 (C): most cluster entries do
not name the behavior they protect. Bring the architecture doc current with the suite as it is (layers, markers,
directories, new suites since June) and deepen the component entries, then regenerate both indexes.

## Ticket Contract
- ENTRY_GATE: owner approval (Notes); authoring instructions read; inventory of the suite recorded.
- EXECUTION_BOUNDARY: `system_docs/tests_architecture.md`, `system_docs/tests_components.md` and their indexes.
- DEPENDENCIES: the Phase-5 task's regression test lands first so the docs include it.
- EXIT_GATE: both docs match the tree (paths resolve, counts measured), indexes --check clean, rubric >= 80.
- FAILURE_ESCALATION: BLOCKER if the suite layout contradicts the instructions' section contract.

## Scope Boundaries
- In scope: the two tests documents and their indexes.
- Out of scope: test code changes.

## State Transition Event
- from_state: draft
- to_state: ready
- transition_reason: Owner instruction to fix the reported follow-ups, 2026-09-26T21:12:25Z.

## Steps / Checklist
- [ ] Read tests_architecture_instructions.md and tests_components_instructions.md.
- [ ] Inventory the suite from disk; record drift against both docs.
- [ ] Author, index, verify citations, score.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- Refreshed tests_architecture.md and tests_components.md with current indexes.

## Files / Paths Impacted
- context_compass/system_docs/tests_architecture.md
- context_compass/system_docs/tests_architecture_index.md
- context_compass/system_docs/tests_components.md
- context_compass/system_docs/tests_components_index.md

## Validation
- Not run.

## Risks / Rollback Notes
- The docs are authored; nothing may be generated or asserted without reading the tests.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
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
  - Test suite layout and the protected behavior of each cluster
- IF_UNKNOWN: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-09-26T21:12:25Z
  TYPE: DECISION
  CLAIM: Owner, after the override lane turn-in: "yeah go ahead and fix all that shit and finish up all those things,
    ok fix the rare crash bro thats a correctness issue". This task is one of the three follow-ups melder_0 reported
    (Phase-5 pool race, order-dependent guard test, weak tests system docs); the deleted unroll benchmarks need no
    action (they measured the retired emitter's dict-vs-unroll choice).
  EVIDENCE:
  - tickets/tasks/completed/2026-09-26_build_site_plan_lowering_task.md
  IMPACT: Work is owner-approved; file lists are recorded here before any edit.
  NEXT: Start after the Phase-5 fix: read the two authoring instructions.
  REREAD: REQUIRED
  SCORE_0_TO_10: 7

## Context / Handoff Summary
Opened on the owner's instruction; waits for the Phase-5 task.

## Project-Specific Additions
<!-- BEGIN USER-DEFINED: project_fields -->
<!-- END USER-DEFINED: project_fields -->
