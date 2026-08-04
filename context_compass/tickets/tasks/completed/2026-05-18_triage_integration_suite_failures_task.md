# Task: triage integration suite failures

- Completed: 2026-05-22T00:19:54Z
- Summary: Closed during board cleanup after the integration-suite triage lane was removed from active routing.


## Metadata
- Task ID: TASK-2026-05-18-triage-integration-suite-failures
- Story: none
- Status: done
- Owner: codex
- Agent Name: mypy_0
- Priority: p0
- Created: 2026-05-18T18:33:40Z
- Updated: 2026-05-22T00:19:54Z

## Objective
Run the current integration pytest suite without code changes, collect the live
failure set, and classify what is a real product/runtime bug versus broader
infrastructure or import-cycle breakage that should be raised instead of
patched blindly.

## Ticket Contract
- ENTRY_GATE: the user explicitly asked for an integration-suite validation
  pass and asked that no random fixes be made
- EXECUTION_BOUNDARY:
  - `tests/integration/`
  - directly implicated source files only for evidence gathering after failures
- DEPENDENCIES:
  - active test environment in `.venv_new`
- EXIT_GATE: the integration-suite failure set is captured and grouped into
  actionable buckets with evidence-backed raises where appropriate
- FAILURE_ESCALATION: raise `BLOCKER` or `DECISION_REQUEST` if the dominant
  failures come from broad repo breakage or stupid infrastructure issues rather
  than one bounded product bug

## Scope Boundaries
- In scope:
  - running `tests/integration`
  - collecting and classifying failures
  - reading directly implicated code after failures land
- Out of scope:
  - patching code before the failure set is understood
  - random opportunistic fixes outside the observed failures

## Steps / Checklist
- [ ] run the full integration pytest ring without edits
- [ ] capture the first failure buckets and dominant breakpoints
- [ ] distinguish product bugs from stupid infrastructure/import-cycle failures
- [ ] document findings in `## Notes` before any code change discussion
- [ ] raise the bad buckets to the user before implementation
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Validation
- Planned:
  - `.\.venv_new\Scripts\pytest.exe -q tests\integration`

## Notes
- DATETIME: 2026-05-18T18:33:40Z
  TYPE: FACT
  CLAIM: The user requested a pure triage pass first: run the integration suite,
    do not patch randomly, and raise broad or stupid failure buckets before any
    implementation work.
  EVIDENCE:
  - user_request: current chat instruction on 2026-05-18
  IMPACT: This lane is validation-first and patching is intentionally blocked
    until the live failure set is understood.
  NEXT: run the full `tests\integration` pytest ring untouched and record the
    dominant failure buckets.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-18T18:34:55Z
  TYPE: MEASURE
  CLAIM: The integration suite does not reach runtime behavior yet. The run is
    stopping in collection with one dominant bucket: `ModuleNotFoundError` for
    repo-local `tests.*` imports (`tests.integration`, `tests.mocks`,
    `tests._frame_posture_test_support`, `tests._codegen_system_support`,
    `tests.experimentation`).
  EVIDENCE:
  - tests/integration/melder/aether/rift/test_capability_rift_json_testbench_integration.py:14-14
  - tests/integration/melder/aether/test_aether_integration_change_control_transactions.py:15-15
  - tests/integration/melder/aether/test_capability_space_frame_and_workstation_integration.py:18-18
  - tests/integration/melder/crystallizer/test_synthetic_module_integration.py:5-5
  - validation_result: `.\.venv_new\Scripts\pytest.exe -q tests\integration` -> `58 errors during collection`
  IMPACT: This is not a scattered product-bug surface yet; the suite is blocked
    by test import-path/package resolution before actual integration logic runs.
  NEXT: inspect `tests/conftest.py` and the `tests/` package layout to prove why
    `tests.*` imports are unresolved in the current environment.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Active validation-first task for the current integration-suite breakage sweep.
