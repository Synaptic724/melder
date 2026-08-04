# Task: Implement Static Rift JSON Testbench
- Completed: 2026-04-13T11:20:06Z
- Summary: Closed the reusable static-room integration harness task after the later multistep and usability slices confirmed the bench as the settled static test foundation.

## Metadata
- Task ID: TASK-2026-04-12-implement-static-rift-json-testbench
- Story: STORY-2026-04-12-build-static-rift-json-testbench
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-12T17:45:00Z
- Updated: 2026-04-13T11:20:06Z

## Objective
Implement one reusable static-room integration harness under
`tests/integration/melder/aether/rift/`, drive it through JSON-like API
requests, and use it to validate a large scenario matrix.

## Ticket Contract
- ENTRY_GATE: the user explicitly requested a large reusable static-room
  testbench and approved reusing one object system with variations.
- EXECUTION_BOUNDARY: integration test harness, driver, and tests only.
- DEPENDENCIES:
  - tests/integration/melder/aether/
  - src/melder/aether/nexus/rift/
  - src/melder/aether/conduit/
  - src/melder/spellbook/
- EXIT_GATE: the static-room integration testbench exists, the JSON-like
  driver exists, and the scenario matrix is green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the requested matrix size
  forces low-value filler instead of meaningful scenarios.

## Scope Boundaries
- In scope:
  - `tests/integration/melder/aether/rift/` folder
  - reusable harness/support module
  - JSON-like request driver
  - large scenario matrix
- Out of scope:
  - capability-mode coverage
  - dynamic/codegen coverage
  - runtime code changes unless a harness blocker is found

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested a large reusable
  static-room integration testbench.

## Steps / Checklist
- [x] Implement the reusable static runtime harness.
- [x] Implement the JSON-like request driver.
- [x] Implement the scenario matrix.
- [x] Run focused integration validation.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- `tests/integration/melder/aether/rift/` folder
- static-room harness/support module
- JSON-like driver
- large integration scenario matrix

## Files / Paths Impacted
- tests/integration/melder/aether/rift/
- codex/context_compass/attention_board.md

## Validation
- Ran:
  - `python -m py_compile tests/integration/melder/aether/rift/static_rift_json_testbench_support.py tests/integration/melder/aether/rift/test_static_rift_json_testbench_integration.py`
  - `python -m pytest -q tests/integration/melder/aether/rift`

## Risks / Rollback Notes
- Risk: the matrix becomes quantity theater instead of meaningful coverage.
  Rollback: keep one reusable harness and one parametrized scenario model so
  every row still represents a real contract difference.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [x] Applicable anti-pattern checks are clear or escalated with evidence.
- [x] Acceptance criteria reviewed with user and confirmed
- [x] Board sync completed for successor routing or closure anchor update.

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
- DATETIME: 2026-04-12T17:45:00Z
  TYPE: FACT
  CLAIM: The repo already has the right integration-testing pattern to copy.
    Existing Nexus/Rift integration matrices create real Spellbook/Conduit/Nexus/Rift
    objects and then drive viewer behavior through small helper layers. The
    new static testbench should reuse that approach, but move the reusable
    setup and JSON-like request dispatch into a dedicated `rift/` integration
    folder.
  EVIDENCE:
  - tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py:1-166
  - tests/integration/melder/aether/test_nexus_viewer_extended_surface_integration_matrix.py:1-385
  - tests/integration/melder/aether/test_nexus_viewer_general_helper_integration_matrix.py:1-196
  - tests/mocks/spellbook/core_classes.py:1-220
  IMPACT: We do not need to invent a new test philosophy. We just need a
    dedicated static-room harness and a bigger scenario matrix.
  NEXT: implement the harness under `tests/integration/melder/aether/rift/`
    and start the JSON-driven matrix on top of it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-12T17:52:00Z
  TYPE: FACT
  CLAIM: The harness design is now explicit enough to implement. The repo
    already proves the relevant pattern: real Spellbook/Conduit/Nexus/Rift
    setup plus matrix-style parametrization. The right testbench shape is:
    1) one reusable `StaticRiftJsonBench`
    2) two real benches for `automatic` and `dynamic` target-frame postures
    3) one JSON dispatcher with placeholder resolution for manifest/object refs
    4) one 100-row read-only scenario matrix over viewer/command/discovery
       behavior
    5) a small set of focused workstation mutation tests on top
  EVIDENCE:
  - tests/integration/melder/aether/test_nexus_frame_surface_projection_integration.py:1-166
  - tests/integration/melder/aether/test_nexus_viewer_extended_surface_integration_matrix.py:1-385
  - tests/integration/melder/aether/test_nexus_viewer_general_helper_integration_matrix.py:1-196
  - src/melder/aether/conduit/conduit.py:527-617
  - src/melder/aether/nexus/rift/frame_viewer/static_frame_viewer.py:1-337
  IMPACT: The implementation can stay high-signal and large without falling
    into 100 handwritten filler tests.
  NEXT: build the harness/support module, then add the matrix and the focused
    workstation mutation tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-12T18:10:00Z
  TYPE: FACT
  CLAIM: The static-room integration testbench is now landed under
    `tests/integration/melder/aether/rift/`. The support module builds a real
    static runtime harness with Spellbook, root + lesser Conduit, Nexus, Rift,
    StaticRiftSpace, static viewer, static command, and workstation surfaces.
    The JSON driver dispatches requests with:
    - `surface`
    - `method`
    - `args`
    - `kwargs`
    and resolves manifest/object placeholders so requests look like LLM-style
    API payloads.
  EVIDENCE:
  - tests/integration/melder/aether/rift/static_rift_json_testbench_support.py:1-446
  - tests/integration/melder/aether/rift/test_static_rift_json_testbench_integration.py:1-628
  IMPACT: Static behavior now has one reusable end-to-end integration harness
    instead of only focused unit/runtime seams.
  NEXT: record the validation result and return the harness for review.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-12T18:10:00Z
  TYPE: MEASURE
  CLAIM: The new static-room integration folder is green. The suite now proves:
    - 100 JSON-driven request-matrix scenarios over viewer, command, Rift, and
      cloud surfaces
    - 4 focused workstation/lesser-conduit interaction tests
    for a total of 104 integration tests in the new `rift/` folder.
  EVIDENCE:
  - validation_result: `python -m py_compile tests/integration/melder/aether/rift/static_rift_json_testbench_support.py tests/integration/melder/aether/rift/test_static_rift_json_testbench_integration.py` -> success
  - validation_result: `python -m pytest -q tests/integration/melder/aether/rift` -> 104 passed
  IMPACT: Static now has a durable reusable integration testbench, not just
    local contract tests.
  NEXT: summarize the landed harness and let the user decide whether to expand
    it further or move on to capability.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-13T11:20:06Z
  TYPE: DECISION
  CLAIM: The reusable static-room JSON testbench is complete and can move to
    the completed lane. The later multistep scripts and static usability work
    use it as the stable integration foundation, and the user explicitly asked
    for finished older tickets to be cleaned up.
  EVIDENCE:
  - tests/integration/melder/aether/rift/static_rift_json_testbench_support.py:145-245
  - tests/integration/melder/aether/rift/test_static_rift_json_testbench_integration.py:922-1075
  - codex/context_compass/system_docs/tests_architecture.md:121-137
  IMPACT: The static harness task no longer needs to remain on the active
    board.
  NEXT: none.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task implements the static-room integration harness and JSON-like matrix
driver under `tests/integration/melder/aether/rift/`.
