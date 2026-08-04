# Task: Extend Capability JSON Harness With Query Helpers
- Completed: 2026-04-13T22:24:59Z
- Summary: Completed the capability-harness query/snapshot expansion after the selected helper matrix landed and the shared Rift integration ring passed.

## Metadata
- Task ID: TASK-2026-04-12-extend-capability-json-harness-with-query-helpers
- Story: STORY-2026-04-12-investigate-capability-rift-space-runtime-model
- Status: done
- Owner: codex
- Priority: p1
- Created: 2026-04-12T22:14:24Z
- Updated: 2026-04-13T22:24:59Z

## Objective
Extend the capability-room JSON integration harness so it exercises the new
read/query spell and conduit snapshot helpers end to end.

## Ticket Contract
- ENTRY_GATE: the spell/query + snapshot helper slice is landed and green on
  the focused unit/runtime ring.
- EXECUTION_BOUNDARY: capability integration harness/tests only, plus runtime
  blocker fixes only if the harness proves one.
- DEPENDENCIES:
  - tests/integration/melder/aether/rift/test_capability_rift_json_testbench_integration.py
  - tickets/tasks/2026-04-12_add_command_level_spell_query_and_snapshot_helpers_task.md
- EXIT_GATE: the capability JSON harness covers the selected query/snapshot
  helpers, and the full `rift/` integration folder is green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the harness exposes a
  broader runtime contract mismatch rather than a test gap.

## Scope Boundaries
- In scope:
  - capability JSON request matrix additions for:
    - `find_spell_id(...)`
    - `find_spell_key(...)`
    - `get_spell_permissions(...)`
    - `snapshot_state(...)`
    - `get_active_spellspace(...)`
  - turn-script additions only when they add real end-to-end value
  - runtime blocker fixes only if the harness proves one
- Out of scope:
  - unrelated runtime feature expansion
  - static harness changes
  - mutation or contract-mutation coverage

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the new query/snapshot helpers exist, so the capability
  JSON harness should cover them before another runtime surface is added.

## Steps / Checklist
- [x] Add single-request capability scenarios for the selected query helpers.
- [x] Add turn-script coverage only if it proves a real end-to-end contract.
- [x] Patch runtime only if a concrete harness blocker appears.
- [x] Run focused integration validation.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- expanded capability JSON request matrix
- optional targeted turn-script additions

## Files / Paths Impacted
- tests/integration/melder/aether/rift/test_capability_rift_json_testbench_integration.py
- codex/context_compass/attention_board.md

## Validation
- Ran:
  - `python -m pytest -q tests/integration/melder/aether/rift/test_capability_rift_json_testbench_integration.py`
  - `python -m pytest -q tests/integration/melder/aether/rift`

## Risks / Rollback Notes
- Risk: adding turn-script coverage where a single-request assertion is enough
  creates low-value matrix bloat.
  Rollback: keep the slice request-matrix focused unless a turn-based flow adds
  real contract value.

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
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: none

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-12T22:14:24Z
  TYPE: PLAN
  CLAIM: The next harness step is the selected read/query helper set, not
    another raw runtime feature. The capability JSON suite already covers
    discovery, topology, activation, and a subset of introspection. The next
    low-risk extension is to add the new direct query/snapshot helpers to the
    request matrix so the same harness proves them end to end.
  EVIDENCE:
  - tests/integration/melder/aether/rift/test_capability_rift_json_testbench_integration.py:1-563
  - src/melder/aether/nexus/rift/rift_space/command_system/command_system.py:920-1047
  IMPACT: We can deepen the capability harness again without widening runtime
    semantics.
  NEXT: add the selected query-helper scenarios to the request matrix and rerun
    the capability integration file.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-12T22:15:50Z
  TYPE: FACT
  CLAIM: The capability request matrix now covers the selected read/query
    helper set:
    - `find_spell_id(...)`
    - `find_spell_key(...)`
    - `get_spell_permissions(...)`
    - `snapshot_state(...)`
    - `get_active_spellspace(...)`
    No new turn-script flow was needed for this slice because single-request
    assertions already proved the end-to-end contract. The only harness
    correction needed was aligning the expected `find_spell_key(...)` value to
    the real lower contract, which normalizes the frame key to lowercase.
  EVIDENCE:
  - tests/integration/melder/aether/rift/test_capability_rift_json_testbench_integration.py:33-247
  - validation_result: `python -m pytest -q tests/integration/melder/aether/rift/test_capability_rift_json_testbench_integration.py` -> find_spell_key returned ('capabilitybench', 'live_spell')
  IMPACT: The capability harness now proves the latest query/snapshot helper
    slice without another unnecessary runtime patch.
  NEXT: record the updated validation totals and return the harness extension
    for review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-12T22:15:50Z
  TYPE: MEASURE
  CLAIM: The widened capability harness now passes with 91 tests, and the full
    shared `rift/` integration folder now passes with 220 tests.
  EVIDENCE:
  - validation_result: `python -m pytest -q tests/integration/melder/aether/rift/test_capability_rift_json_testbench_integration.py` -> 91 passed
  - validation_result: `python -m pytest -q tests/integration/melder/aether/rift` -> 220 passed
  IMPACT: The capability harness now covers discovery, topology, activation,
    and a broader read/query surface on one stable JSON/turn-script bench.
  NEXT: summarize the landed harness expansion and choose the next genuinely
    new capability/runtime seam.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task extends the capability JSON harness with the newly landed query and
snapshot helpers. The extension is now landed and green.
