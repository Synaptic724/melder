# Task: Expand Capability JSON Failure And Cleanup Integration Tests
- Completed: 2026-04-24T01:03:27Z
- Summary: Closed during the 2026-04-24 cleanup after the second capability integration tranche was accepted as sufficient.

## Metadata
- Task ID: TASK-2026-04-22-expand-capability-json-failure-and-cleanup-integration-tests
- Story: none
- Status: done
- Owner: codex
- Priority: p0
- Created: 2026-04-22T23:25:46Z
- Updated: 2026-04-24T01:03:27Z

## Objective
Add a second capability-room integration tranche that covers the remaining
gaps: JSON-bench parity for the new workflows, deeper result-binding coverage
across stores, failure-path workstation/target misuse, and cleanup-after-binding
behavior.

## Ticket Contract
- ENTRY_GATE: the first 30-case capability-room integration matrix is landed
  and green, so the remaining gaps are now explicit and bounded.
- EXECUTION_BOUNDARY:
  - capability JSON-bench integration tests
  - capability workstation/cleanup integration tests
  - directly related shared test helpers
  - ticket/board state for this lane
- DEPENDENCIES:
  - tests/integration/melder/aether/test_capability_space_frame_and_workstation_integration.py
  - tests/integration/melder/aether/rift/test_capability_rift_json_testbench_integration.py
  - tests/integration/melder/aether/rift/capability_rift_json_testbench_support.py
  - src/melder/aether/nexus/rift/rift_space/workstation.py
  - src/melder/aether/nexus/rift/command_system/command_system.py
- EXIT_GATE: the four requested gaps are covered by the new test tranche and
  the focused integration run is green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the requested coverage needs
  runtime changes or a broader harness redesign instead of a bounded test
  expansion.

## Scope Boundaries
- In scope:
  - new JSON-bench workflows that mirror the frame/workstation capability lane
  - additional command-result binding coverage across stores
  - failure-path tests for bad target selection, wrong store selection, and
    mixed-frame misuse
  - cleanup-after-binding behavior, especially Nexus-created-frame object
    binding followed by conduit/frame cleanup
  - about 30 additional high-signal integration tests
- Out of scope:
  - unrelated runtime feature work unless a test proves a contract gap
  - static/codegen room coverage
  - broad test-harness rewrites

## State Transition Event
- from_state: in_progress
- to_state: review
- transition_reason: the second 30-case capability tranche is implemented and
  the focused integration ring is green.

## Steps / Checklist
- [x] Read the current capability JSON bench, workstation failure seams, and cleanup behavior.
- [x] Map the four requested contract gaps to concrete integration scenarios.
- [x] Add about 30 additional high-signal integration tests.
- [x] Keep the tests contract-level and non-filler.
- [x] Run the focused integration ring.
- [x] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [x] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- expanded capability JSON/failure/cleanup integration matrix
- focused integration validation result

## Files / Paths Impacted
- tests/integration/melder/aether/
- tests/integration/melder/aether/rift/
- codex/context_compass/attention_board.md

## Validation
- Executed:
  - `python -m pytest -q tests/integration/melder/aether/test_capability_space_frame_and_workstation_integration.py tests/integration/melder/aether/rift/test_capability_rift_json_testbench_integration.py`
- Result:
  - `161 passed, 2 warnings`

## Risks / Rollback Notes
- Risk: the extra 30-test request could turn into filler.
  Rollback: keep the matrix organized around the four real missing seams only.
- Risk: cleanup-after-binding may expose a real runtime ambiguity around how
  workstation-held references are supposed to behave after conduit/frame
  disposal.
  Rollback: prove the actual current behavior and stop if it needs runtime
  design work.

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
- [ ] Acceptance criteria reviewed with user and confirmed
- [x] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
  - none
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-04-22T23:25:46Z
  TYPE: PLAN
  CLAIM: This task exists to make the second capability-room expansion
    explicit and bounded. The remaining requested gaps are now concrete:
    JSON-bench parity, deeper result-binding coverage, failure-path workstation
    misuse, and cleanup-after-binding behavior.
  EVIDENCE:
  - user_instruction: "the new workflow is not mirrored into the JSON capability bench yet"
  - user_instruction: "I did not stress command-result binding across more store types beyond the most useful object/method/result paths"
  - user_instruction: "I did not add failure-path capability tests around bad target selection, wrong store selection, or mixed-frame misuse in the workstation layer"
  - user_instruction: "I did not test cleanup-after-binding deeply enough in this lane yet"
  IMPACT: The next tranche can stay focused on the real holes instead of widening blindly.
  NEXT: read the current capability JSON bench plus the workstation and cleanup seams.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-22T23:25:46Z
  TYPE: DECISION
  CLAIM: The cleanest implementation is three bounded matrices:
    - 10 new JSON-bench scenarios to mirror the new workflow and store-binding
      behavior through the existing turn-script harness
    - 10 direct capability integration cases for richer result-binding and
      failure-path workstation misuse
    - 10 direct capability integration cases for cleanup-after-binding behavior
      across default-frame and Nexus-created-frame flows
  EVIDENCE:
  - tests/integration/melder/aether/rift/capability_rift_json_testbench_support.py:52-205
  - tests/integration/melder/aether/rift/test_capability_rift_json_testbench_integration.py:296-384
  - src/melder/aether/nexus/rift/command_system/command_system.py:2677-2730
  - src/melder/aether/nexus/rift/rift_space/workstation.py:296-351
  - src/melder/aether/nexus/rift/rift_space/workstation.py:431-523
  IMPACT: We can hit the requested 30-test expansion without inventing a new
    harness or widening into runtime edits.
  NEXT: extend the capability JSON bench support first, then add the two new
    direct integration matrices.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-04-22T23:25:46Z
  TYPE: FACT
  CLAIM: The first run of the second tranche found two test-layer mismatches.
    The mixed-frame conduit/spell failure cases are blocked earlier by command
    ACL disable than by not-found errors, and the JSON capability bench still
    builds Nexus in default single-frame mode, so explicit named
    `create_nexus_frame(frame_name=...)` scenarios cannot work there until the
    bench opts into indexed mode.
  EVIDENCE:
  - test_run_output: `Command access to conduit ... is disabled in frame 'ops'`
  - test_run_output: `Command access to spell lineage ... is disabled in frame 'ops'`
  - tests/integration/melder/aether/rift/capability_rift_json_testbench_support.py:231-244
  - test_run_output: `ValueError: Shared Nexus mode only exposes the shared frame.`
  IMPACT: The fix is bounded to test expectations plus the JSON bench config;
    no runtime behavior change is implied by these failures.
  NEXT: patch the two error-match expectations and switch the JSON capability
    bench to indexed Nexus mode for the explicit named-frame scenarios.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-04-22T23:25:46Z
  TYPE: MEASURE
  CLAIM: The second capability-room expansion is green. The lane now covers
    the four previously missing seams with about 30 additional integration
    cases: 10 new JSON-bench scenarios, 10 direct failure/result-binding
    scenarios, and 10 cleanup-after-binding scenarios.
  EVIDENCE:
  - tests/integration/melder/aether/test_capability_space_frame_and_workstation_integration.py:1-1045
  - tests/integration/melder/aether/rift/test_capability_rift_json_testbench_integration.py:1-1146
  - tests/integration/melder/aether/rift/capability_rift_json_testbench_support.py:1-394
  - test_run_output: `161 passed, 2 warnings`
  IMPACT: The capability-room integration surface now covers the requested JSON
    parity, deeper store binding, failure paths, and cleanup-after-binding
    behavior as one coherent lane.
  NEXT: review the second capability tranche and decide whether it is
    sufficient or whether another capability/workstation seam should be added.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the second capability-room integration expansion lane. The new
JSON/failure/cleanup tranche is implemented and review-ready.
