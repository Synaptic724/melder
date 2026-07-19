# Task: fix capability rift cloud automatic expectation

Completed: 2026-05-19T17:29:27Z
Summary: Closed per user instruction before final completion. Latest lane state remains below.


## Metadata
- Task ID: TASK-2026-05-18-fix-capability-rift-cloud-automatic-expectation
- Story: none
- Status: done
- Owner: codex
- Agent Name: mypy_2
- Priority: p1
- Created: 2026-05-18T14:55:23Z
- Updated: 2026-05-19T17:29:27Z

## Objective
Fix the capability Rift JSON integration expectations for automatic frames so they
match the current frame-owned `ConduitCloud` contract.

## Ticket Contract
- ENTRY_GATE: the reproduced failures are
  `automatic_command_get_conduit_cloud`,
  `automatic_cloud_count_conduits`, and
  `automatic_cloud_list_conduit_names`
  in `test_capability_rift_json_request_matrix`.
- EXECUTION_BOUNDARY:
  - `tests/integration/melder/aether/rift/test_capability_rift_json_testbench_integration.py`
  - supporting source evidence only:
    - `tests/integration/melder/aether/rift/capability_rift_json_testbench_support.py`
    - `src/melder/aether/conduit_cloud.py`
    - `src/melder/aether/nexus/rift/command_system/capability_command_system.py`
- DEPENDENCIES:
  - current capability JSON bench runtime
  - frame-owned `ConduitCloud` behavior
- EXIT_GATE:
  - the targeted automatic cloud request cases are green
  - the request matrix expects the current frame-owned cloud contract
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if source evidence shows automatic
  capability frames should still expose an empty cloud

## Scope Boundaries
- In scope:
  - capability JSON request expectations for cloud object/count/name on automatic frames
- Out of scope:
  - runtime `ConduitCloud` semantics
  - unrelated capability JSON scenarios after this drift is corrected

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the reproduced failures are a bounded integration expectation
  drift against the live `ConduitCloud` contract

## Steps / Checklist
- [ ] confirm the live bench/runtime contract for automatic-frame cloud access
- [ ] patch the integration expectation to the current contract
- [ ] rerun the targeted capability cloud request cases
- [ ] continue to the next failure only after documenting the result
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- a narrow capability JSON expectation fix for cloud access on automatic frames

## Files / Paths Impacted
- `tests/integration/melder/aether/rift/test_capability_rift_json_testbench_integration.py`

## Validation
- Not run.
- Recommended commands:
  - `.\.venv_new\Scripts\python.exe -m pytest -vv -x --tb=long tests\integration\melder\aether\rift\test_capability_rift_json_testbench_integration.py -k "automatic_command_get_conduit_cloud or automatic_cloud_count_conduits or automatic_cloud_list_conduit_names"`

## Risks / Rollback Notes
- Low risk. This lane should remain integration-expectation only unless source
  evidence contradicts the frame-owned cloud contract.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
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
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: n/a

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-05-18T14:55:23Z
  TYPE: FACT
  CLAIM: The capability JSON cloud failures are integration expectation drift,
    not a runtime regression. The bench conjures named `left` and `right` root
    conduits for both automatic and dynamic frames, and `ConduitCloud` now
    reports the frame-owned root-conduit registry directly rather than a
    dynamic-only side registry.
  EVIDENCE:
  - tests/integration/melder/aether/rift/capability_rift_json_testbench_support.py:125-154
  - tests/integration/melder/aether/rift/capability_rift_json_testbench_support.py:342-366
  - src/melder/aether/conduit_cloud.py:17-27
  - src/melder/aether/conduit_cloud.py:182-220
  - tests/integration/melder/aether/rift/test_capability_rift_json_testbench_integration.py:949-964
  IMPACT: The automatic cloud assertions are stale and are blocking the next integration slice.
  NEXT: normalize the automatic cloud expectations to the live frame-owned cloud
    contract, then rerun the targeted request cases.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-18T14:55:23Z
  TYPE: PLAN
  CLAIM: The smallest truthful fix is to stop branching cloud expectations on
    `bench.dynamic_frame` for these request cases. The harness always creates
    named `left` and `right` root conduits, and the cloud contract now exposes
    those frame-owned roots in both automatic and dynamic modes.
  EVIDENCE:
  - tests/integration/melder/aether/rift/capability_rift_json_testbench_support.py:125-154
  - tests/integration/melder/aether/rift/test_capability_rift_json_testbench_integration.py:949-964
  IMPACT: This keeps the fix narrow to the stale expectation without touching
    runtime behavior.
  NEXT: patch the three cloud expectation branches and rerun the targeted cases.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
Active capability JSON lane for the cloud expectation drift on automatic frames.
Current evidence points to a test-only fix.
