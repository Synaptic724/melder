# Task: Extend Capability JSON Harness With Meld Helpers
- Completed: 2026-04-13T22:24:59Z
- Summary: Completed the capability-harness meld-helper expansion after activation, reuse, and follow-on introspection coverage landed end to end.

## Metadata
- Task ID: TASK-2026-04-12-extend-capability-json-harness-with-meld-helpers
- Story: STORY-2026-04-12-investigate-capability-rift-space-runtime-model
- Status: done
- Owner: codex
- Priority: p1
- Created: 2026-04-12T21:37:23Z
- Updated: 2026-04-13T22:24:59Z

## Objective
Extend the capability-room JSON integration harness so it exercises the new
shared `meld(...)` and `meld_existing_spell(...)` command helpers end to end.

## Ticket Contract
- ENTRY_GATE: the command-level meld-helper slice is landed and green on the
  focused unit/runtime ring.
- EXECUTION_BOUNDARY: capability integration harness/tests only, plus runtime
  blocker fixes only if the harness proves one.
- DEPENDENCIES:
  - tests/integration/melder/aether/rift/test_capability_rift_json_testbench_integration.py
  - tickets/tasks/2026-04-12_add_command_level_meld_helpers_task.md
- EXIT_GATE: the capability JSON harness covers `meld(...)` and
  `meld_existing_spell(...)`, and the full `rift/` integration folder is green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the harness exposes a
  broader runtime contract mismatch rather than a test gap.

## Scope Boundaries
- In scope:
  - capability JSON request matrix additions for meld helpers
  - capability turn-script coverage for activated objects
  - runtime blocker fixes only if the harness proves one
- Out of scope:
  - static harness changes unless a concrete shared-driver blocker appears
  - unrelated runtime feature expansion
  - codegen/dynamic-room coverage

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the new command-level meld helpers exist, so the
  capability harness should exercise them before we add more runtime surface.

## Steps / Checklist
- [x] Add single-request capability scenarios for `meld(...)` and `meld_existing_spell(...)`.
- [x] Add multistep turn-script coverage over activated objects.
- [x] Patch runtime only if a concrete harness blocker appears.
- [x] Run focused integration validation.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- expanded capability JSON request matrix
- expanded capability turn-script matrix

## Files / Paths Impacted
- tests/integration/melder/aether/rift/test_capability_rift_json_testbench_integration.py
- codex/context_compass/attention_board.md

## Validation
- Ran:
  - `python -m py_compile tests/integration/melder/aether/rift/test_capability_rift_json_testbench_integration.py`
  - `python -m pytest -q tests/integration/melder/aether/rift/test_capability_rift_json_testbench_integration.py`
  - `python -m pytest -q tests/integration/melder/aether/rift`

## Risks / Rollback Notes
- Risk: the new scenarios duplicate behavior already covered by unit tests
  instead of proving real end-to-end use through the JSON harness.
  Rollback: keep the new scenarios centered on JSON dispatch and multistep
  object use, not just direct helper return values.

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
- DATETIME: 2026-04-12T21:37:23Z
  TYPE: PLAN
  CLAIM: The next meaningful capability integration step is not more topology
    coverage. It is exercising the new command-level `meld(...)` and
    `meld_existing_spell(...)` helpers through the same JSON/turn-script
    harness pattern already used for the rest of the capability room. That
    gives us end-to-end proof that the corrected command surface can activate a
    spell and then use the resulting object over multiple turns.
  EVIDENCE:
  - tests/integration/melder/aether/rift/test_capability_rift_json_testbench_integration.py:1-545
  - src/melder/aether/nexus/rift/rift_space/command_system/command_system.py:1067-1164
  IMPACT: We can deepen the capability harness without touching unrelated
    runtime surface area.
  NEXT: add request-matrix and turn-script scenarios for `meld(...)` and
    `meld_existing_spell(...)`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-12T21:39:40Z
  TYPE: FACT
  CLAIM: The capability JSON harness now exercises the new shared activation
    helpers directly. The request matrix covers both `command.meld(...)` and
    `command.meld_existing_spell(...)`, and the turn-script matrix now proves
    that a capability room can activate a spell, bind the resulting object into
    workstation, execute against it across turns, and re-resolve it through the
    reuse-only helper.
  EVIDENCE:
  - tests/integration/melder/aether/rift/test_capability_rift_json_testbench_integration.py:33-237
  - tests/integration/melder/aether/rift/test_capability_rift_json_testbench_integration.py:240-440
  IMPACT: The capability harness now proves the full manual runtime flow around
    the new command-level meld helpers instead of only proving topology and
    metadata surfaces.
  NEXT: record the green validation result and return the harness extension for review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-12T21:39:40Z
  TYPE: MEASURE
  CLAIM: The capability harness extension is green both in isolation and in
    the full shared `rift/` integration folder. The capability file now passes
    with 65 tests, and the full `tests/integration/melder/aether/rift` folder
    now passes with 194 tests.
  EVIDENCE:
  - validation_result: `python -m py_compile tests/integration/melder/aether/rift/test_capability_rift_json_testbench_integration.py` -> success
  - validation_result: `python -m pytest -q tests/integration/melder/aether/rift/test_capability_rift_json_testbench_integration.py` -> 65 passed
  - validation_result: `python -m pytest -q tests/integration/melder/aether/rift` -> 194 passed
  IMPACT: The new activation-helper behavior is now locked into the same
    end-to-end capability harness that already covered topology and discovery.
  NEXT: summarize the landed capability harness extension and choose the next
    capability/runtime feature slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-12T21:51:46Z
  TYPE: FACT
  CLAIM: The same capability harness has now been widened one step further to
    cover a subset of the new read/query introspection helpers as well. The
    request matrix now includes:
    - `get_lesser_conduit(...)`
    - `describe_spells_in_conduit(...)`
    - `get_resolution_state(...)`
    and the turn-script matrix now proves post-link direction introspection via:
    - `get_initiated_conduits(...)`
    - `get_provider_conduits(...)`
    - `get_initiated_conduit(...)`
    - `get_provider_conduit(...)`
  EVIDENCE:
  - tests/integration/melder/aether/rift/test_capability_rift_json_testbench_integration.py:33-516
  IMPACT: Capability integration now covers topology, activation, and a useful
    subset of runtime introspection on the same JSON/turn-script surface.
  NEXT: record the updated validation totals and return the harness extension
    for review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-12T21:51:46Z
  TYPE: MEASURE
  CLAIM: The widened capability harness now passes with 81 tests, and the full
    shared `rift/` integration folder now passes with 210 tests.
  EVIDENCE:
  - validation_result: `python -m pytest -q tests/integration/melder/aether/rift/test_capability_rift_json_testbench_integration.py` -> 81 passed
  - validation_result: `python -m pytest -q tests/integration/melder/aether/rift` -> 210 passed
  IMPACT: The capability harness is now deep enough that the next feature slice
    can focus on genuinely new runtime surface instead of obvious coverage gaps.
  NEXT: summarize the landed capability harness expansion and choose the next
    capability/runtime feature slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task extends the capability JSON harness to cover the new shared meld
helpers end to end. It now also covers a subset of the new read/query
introspection helpers, and the extension is green.
