# Task: Implement Capability Rift JSON Testbench
- Completed: 2026-04-13T22:24:59Z
- Summary: Completed the reusable capability JSON/turn-script integration harness after the scenario matrix landed and the shared Rift integration folder passed.

## Metadata
- Task ID: TASK-2026-04-12-implement-capability-rift-json-testbench
- Story: STORY-2026-04-12-investigate-capability-rift-space-runtime-model
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-12T21:07:21Z
- Updated: 2026-04-13T22:24:59Z

## Objective
Implement one reusable capability-room integration harness under
`tests/integration/melder/aether/rift/`, drive it through JSON-like API
requests and turn scripts, and use it to validate the new shared
manual-runtime command surface on both automatic and dynamic underlying frames.

## Ticket Contract
- ENTRY_GATE: the capability room model, focused capability operation slice,
  and shared command-surface expansion are already landed and green.
- EXECUTION_BOUNDARY: capability integration harness, driver, tests, and
  runtime-only blocker fixes if the harness exposes a real missing seam.
- DEPENDENCIES:
  - tests/integration/melder/aether/rift/
  - src/melder/aether/nexus/rift/
  - src/melder/aether/conduit/
  - src/melder/spellbook/
  - tickets/tasks/2026-04-12_expand_shared_command_system_manual_runtime_surface_task.md
- EXIT_GATE: the capability-room integration testbench exists, the JSON/turn
  driver exists, and the capability scenario matrix is green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the requested capability
  matrix exposes a broader runtime contract gap rather than a harness gap.

## Scope Boundaries
- In scope:
  - `tests/integration/melder/aether/rift/` capability harness/support module
  - JSON-like request driver and multistep turn scripts
  - automatic/dynamic capability scenario matrix
  - runtime blocker fixes only if the harness proves a missing seam
- Out of scope:
  - static harness refactor unless required by a concrete blocker
  - codegen/dynamic-room integration coverage
  - unrelated runtime feature expansion

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the shared capability command surface is landed and the
  next coherent slice is real integration coverage over the new room behavior.

## Steps / Checklist
- [x] Implement the reusable capability runtime harness.
- [x] Implement the JSON-like request + turn-script driver.
- [x] Implement the capability scenario matrix.
- [x] Patch runtime only if a concrete harness blocker appears.
- [x] Run focused integration validation.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- capability-room harness/support module
- capability JSON request driver
- capability integration scenario matrix

## Files / Paths Impacted
- tests/integration/melder/aether/rift/
- codex/context_compass/attention_board.md

## Validation
- Ran:
  - `python -m py_compile tests/integration/melder/aether/rift/capability_rift_json_testbench_support.py tests/integration/melder/aether/rift/test_capability_rift_json_testbench_integration.py`
  - `python -m pytest -q tests/integration/melder/aether/rift/test_capability_rift_json_testbench_integration.py`
  - `python -m pytest -q tests/integration/melder/aether/rift`

## Risks / Rollback Notes
- Risk: the capability matrix degenerates into many near-duplicate cases
  instead of proving distinct runtime contracts.
  Rollback: keep one reusable harness and one parametrized scenario model so
  every row asserts a real room/runtime difference.
- Risk: the harness exposes a runtime contract mismatch rather than a pure test
  gap.
  Rollback: patch only the proved blocker inside this lane and record the
  contract delta in notes before continuing.

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
- DATETIME: 2026-04-12T21:07:21Z
  TYPE: PLAN
  CLAIM: The next capability slice is integration coverage, not more blind API
    expansion. The shared command surface is already in place, and the static
    Rift JSON bench proved the right testing pattern: one reusable harness,
    JSON-like single-step requests, multistep turn scripts, and a large
    scenario matrix. The clean move is a dedicated `CapabilityRiftJsonBench`
    that exercises the new direct command methods on both automatic and
    dynamic frames.
  EVIDENCE:
  - tests/integration/melder/aether/rift/static_rift_json_testbench_support.py:1-446
  - tests/integration/melder/aether/rift/test_static_rift_json_testbench_integration.py:1-628
  - tickets/tasks/2026-04-12_expand_shared_command_system_manual_runtime_surface_task.md:1-155
  IMPACT: The next pass can prove the real capability room contract end to end
    before we add more API.
  NEXT: build the dedicated capability harness/support module under
    `tests/integration/melder/aether/rift/` and start the JSON-driven matrix.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-12T21:13:27Z
  TYPE: FACT
  CLAIM: The capability harness exposed two real command/runtime contracts that
    needed to be reflected in the testbench. First, command methods use the
    class-level `CommandSystem._aether`, so the integration harness must
    rebind that singleton per test run or command lookups hit a cleaned
    Aether. Second, the shared command conduit inventory includes the published
    lesser conduit, so command-level conduit id/count queries return both root
    conduits plus the initial lesser conduit. The harness also confirmed that
    capability spell getters return `ISpell` metadata objects, not created
    runtime instances, and that cluster methods are not dynamic-gated while
    conduit linking is.
  EVIDENCE:
  - tests/integration/melder/aether/rift/capability_rift_json_testbench_support.py:1-406
  - tests/integration/melder/aether/rift/test_capability_rift_json_testbench_integration.py:1-545
  - src/melder/aether/nexus/rift/rift_space/command_system/command_system.py:402-1076
  - src/melder/aether/conduit/conduit.py:2303-2349
  - src/melder/aether/conduit/conduit.py:2874-2999
  IMPACT: The capability integration matrix is now aligned to the real runtime
    contract instead of a guessed one.
  NEXT: record the green validation result and return the capability harness
    for review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-12T21:13:27Z
  TYPE: MEASURE
  CLAIM: The capability-room JSON testbench is green both in isolation and in
    the full shared `rift/` integration folder. The new capability suite adds
    26 single-request JSON scenarios and 25 five-step turn-script scenarios for
    a total of 51 new integration tests, and the full `rift/` folder now
    passes with 180 tests.
  EVIDENCE:
  - validation_result: `python -m py_compile tests/integration/melder/aether/rift/capability_rift_json_testbench_support.py tests/integration/melder/aether/rift/test_capability_rift_json_testbench_integration.py` -> success
  - validation_result: `python -m pytest -q tests/integration/melder/aether/rift/test_capability_rift_json_testbench_integration.py` -> 51 passed
  - validation_result: `python -m pytest -q tests/integration/melder/aether/rift` -> 180 passed
  IMPACT: Capability now has reusable end-to-end integration coverage on the
    same JSON/turn-script pattern as static.
  NEXT: summarize the landed capability harness and decide whether the next
    slice is more shared command helpers or another capability/runtime feature.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the capability-room integration harness and JSON/turn-script
matrix on top of the new shared command surface. The harness is now landed and
green on both the focused capability file and the full `rift/` integration ring.
