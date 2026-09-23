# Task: Repair named-conduit discovery failures reported by CI

## Metadata
- Task ID: TASK-2026-09-23-fix-named-conduit-discovery-test-doubles
- Status: done
- Owner: codex
- Agent Name: updater_0
- Created: 2026-09-23T22:33:18Z
- Updated: 2026-09-23T22:37:00Z
- Completed: 2026-09-23T22:37:00Z
- Summary: Corrected two incomplete named-discovery test doubles; both CI failures reproduced
  before repair and 201 affected tests pass afterward. Runtime behavior is unchanged.

## Objective
Diagnose and repair the two named-conduit lookup failures reported on Linux and macOS.

## Ticket Contract
- ENTRY_GATE: Owner supplies failure logs and requests bug repair; route this task before validation.
- EXECUTION_BOUNDARY: Failing Nexus/codegen and capability-discovery tests, their direct contracts,
  focused validation and final asset regeneration. Runtime edits require evidenced runtime defects.
- DEPENDENCIES: Completed named-lesser discovery and same-identity/live-name lookup behavior.
- EXIT_GATE: Both reported failures pass and relevant discovery/ACL regressions remain green.
- FAILURE_ESCALATION: Record any runtime-contract defect; do not add defensive fallbacks for mocks.

## Scope Boundaries
- tests/unit/melder/aether/test_nexus.py
- tests/unit/melder/aether/test_rift_runtime_contracts.py
- Direct command lookup source and existing named-discovery regression suites for investigation.
- No compiler-epic claim, version bump, publication or unrelated coroutine-warning cleanup.
- Finish all source/tracking edits before final asset builders/checks. No separate asset task.

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: Both reported failures are repaired and all 201 affected checks pass.

## Steps / Checklist
- [x] Read both supplied logs and identify the common failure boundary.
- [x] Verify source and test setup, then reproduce the two failures.
- [x] Apply the bounded correction and run relevant compatibility checks.
- [x] Record results and finish tracking before direct final asset generation.

## Validation
Reproduce the two named test node IDs, then run their containing modules and existing named-scope
regressions. Report exact passing/failing results; no full-suite or coverage claim.

## Applicable Anti-Patterns
- [x] No runtime hasattr/getattr workaround for a known Conduit contract.
- [x] No edits after the final asset builders/checks.

## Artifact Links
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS: artifacts/named_discovery_test_repair_20260923/
- DISPOSITION: retain_as_reference

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false

## Noting Behavior
Record the contract diagnosis, minimal repair and observed validation before continuing.

## Notes
- DATETIME: 2026-09-23T22:37:00Z
  TYPE: MEASURE
  CLAIM: Both legacy test doubles now expose the expected live Conduit name. All 201 cases in the
    two unit modules and named-discovery integration/component selection pass. The source guard
    remains unchanged; existing same-shell/name-reuse and authorization regressions still pass.
  EVIDENCE:
  - artifacts/named_discovery_test_repair_20260923/validation.md:1-29
  - artifacts/named_discovery_test_repair_20260923/after.log:1-4
  - tests/unit/melder/aether/test_nexus.py:2113-2195
  - tests/unit/melder/aether/test_rift_runtime_contracts.py:299-353
  IMPACT: The Linux/macOS failures share a fixture cause and are fixed without runtime fallbacks.
    Readback and scoped whitespace checks pass. No version, release-copy or compiler-epic changes.
  NEXT: Run both asset builders and their checks directly as the final operations, then report results.
  REREAD: HELPFUL
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-23T22:34:57Z
  TYPE: FACT
  CLAIM: Both exact CI tests fail locally with the same missing-name AttributeErrors. The shared
    command helper deliberately resolves the authorized published ID and checks its live name to
    reject scope reuse. The two isolated fixtures provide no name at all, unlike real conduits.
  EVIDENCE:
  - artifacts/named_discovery_test_repair_20260923/before.log:1-26
  - src/melder/nexus/rift/command_system/command_system.py:192-291
  - tests/unit/melder/aether/test_nexus.py:2113-2240
  - tests/unit/melder/aether/test_rift_runtime_contracts.py:299-349
  IMPACT: Repair the fixture contracts with name=root and name=alpha respectively. Keep the runtime
    guard intact and qualify existing name-reuse/authorization regressions alongside both modules.
  NEXT: Apply the two fixture corrections with explicit test contracts, then run the focused selection.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-23T22:33:18Z
  TYPE: HYPOTHESIS
  CLAIM: Both supplied CI logs show the same two incomplete test doubles reaching the live-name
    guard: a SimpleNamespace with no name and a bare object. The named-feature guard may be correct
    while those fixtures need updating; verify the actual source and reproduce locally first.
  EVIDENCE:
  - Owner attachments 7aa230a6-bff0-46ca-9b35-26ffe8b3fbcb and 31bf8d6a-b32e-4b86-8f8a-7020ea7dc7a0.
  - tests/unit/melder/aether/test_nexus.py:2114-2192
  - tests/unit/melder/aether/test_rift_runtime_contracts.py:297-349
  IMPACT: Linux and macOS report the same defect class; avoid assuming platform-specific runtime bugs.
  NEXT: Read direct lookup contracts and fixtures, then run the exact two failing tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Completed: two missing-name fixture defects repaired; all 201 affected checks pass. Runtime
lookup guards are unchanged. Retain before/after receipts. Finish with direct asset generation
and checks; no new asset task or repository edit afterward.