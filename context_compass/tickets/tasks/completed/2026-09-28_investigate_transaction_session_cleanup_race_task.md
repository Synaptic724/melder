# Task: Align mediator cleanup tests with the supported lifecycle

## Metadata
- Task ID: TASK-2026-09-28-investigate-transaction-session-cleanup-race
- Status: done
- Owner: codex
- Agent Name: workflows_0
- Created: 2026-09-28T11:18:51Z
- Updated: 2026-09-28T11:34:15Z
- Completed: 2026-09-28T11:32:40Z
- Summary: Replaced unsupported simultaneous cleanup expectations with owner-driven lifecycle tests;
  189 mediator unit tests pass. Runtime cleanup/locking unchanged; no version notch.

## Objective
Remove the unsupported simultaneous-destruction expectation and verify owner-driven cleanup,
sequential idempotence, resource ownership and public use-after-clean rejection.

## Ticket Contract
- ENTRY_GATE: Owner supplies the CI failure and requests investigation; prior onboarding remains valid.
- EXECUTION_BOUNDARY: Mediator lifecycle tests and their documentation, source reads for ownership,
  generated artifacts and task records. Runtime lock handling remains unchanged.
- DEPENDENCIES: Current source and Python 3.14 free-threaded environment.
- EXIT_GATE: Unsupported eight-caller cleanup tests replaced with valid lifecycle coverage;
  the focused mediator suite passes and generated artifacts reflect the final test/document changes.
- FAILURE_ESCALATION: Do not swallow arbitrary AttributeError or weaken the concurrent cleanup test.

## Scope Boundaries
- In scope: cleanup idempotence, lock lifetime, directly related cleanup patterns and regression evidence.
- Out of scope: broad cleanup refactors, application runtime changes and the unrelated coroutine warning.

## State Transition Event
- from_state: in_progress
- to_state: done
- transition_reason: Owner clarified the lifecycle contract; corresponding tests and documentation corrected.

## Validation
- Owner CI: one failure because TransactionSession._lock was absent during concurrent cleanup.
- The owner clarified that simultaneous destruction is unsupported, so no runtime race workaround was added.
- Full mediator unit directory: 189 passed on Python 3.14.7, GIL disabled.
- Diff whitespace and test-document index checks pass; documentation preservation has zero lost lines.
- Final generated-asset and LLM bundle checks pass. Full repository CI was not rerun locally.

## Artifact Links
- ARTIFACTS_REQUIRED: true
- ARTIFACT_PATHS:
  - artifacts/transaction_session_cleanup_race_20260928/
- DISPOSITION: retain_as_reference
- CLEANUP_TRIGGER: Retain reproduction and diagnosis evidence after turn-in.

## Context Management
- CONTEXT_MANAGEMENT_REQUIRED: false
- CONTEXT_IDS: none
- IF_UNKNOWN: none

## Notes
- DATETIME: 2026-09-28T11:18:51Z
  TYPE: HYPOTHESIS
  CLAIM: A racing cleanup caller may pass the initial cleaned check before another caller deletes
    the lock, then fail on the later lock attribute lookup. Confirm from source before choosing a fix.
  EVIDENCE:
  - tests/unit/melder/aether/aetheric_mediator/test_aetheric_mediator_unit.py:789-812
  IMPACT: A lock cannot serialize cleanup if it disappears before a racing caller acquires it.
  NEXT: Read TransactionSession, its cleanup collaborators and the existing concurrency test setup.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-28T11:23:12Z
  TYPE: DECISION
  CLAIM: Owner challenges the test's premise: mediator cleanup represents application shutdown,
    and concurrent cleanup may be an unrealistic condition rather than a supported runtime contract.
    Investigate actual production ownership before adding retention/guards or treating the test as authority.
    The failing object is a TransactionSession; distinguish that lifetime from the mediator root.
  EVIDENCE:
  - src/melder/aether/aetheric_mediator/transaction_session.py:180-228
  - src/melder/aether/aetheric_mediator/mediator.py:54-104
  - tests/unit/melder/aether/aetheric_mediator/test_aetheric_mediator_unit.py:750-813
  IMPACT: No production fix is assumed. Validate the lifecycle contract and revise invalid tests if appropriate.
  NEXT: Trace session creation, finalization, startup failure and root teardown cleanup ownership.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-28T11:27:48Z
  TYPE: DECISION
  CLAIM: Owner clarified the contract: public live-only methods check cleaned on entry; callers own
    object lifetime. Simultaneous destruction is not promised. The owner considered a lock alias and
    explicitly chose to continue without that runtime overhead. Source agrees on single-root session
    ownership: normal finalization unregisters borrowers and leaves the session to its begin caller;
    begin failure cleans an unreturned session; root teardown cleans outstanding sessions.
  EVIDENCE:
  - src/melder/aether/aetheric_mediator/mediator.py:447-589
  - src/melder/aether/aetheric_mediator/mediator.py:1092-1151
  - src/melder/aether/aetheric_mediator/mediator.py:156-212
  - src/melder/aether/aetheric_mediator/transaction_session.py:180-228
  IMPACT: Correct the tests, not runtime lock lifetime. Retire both the failing session test and its
    adjacent four-component simultaneous-cleanup variant, which impose the same unsupported guarantee.
    Extend sequential idempotence/use-after-clean coverage and verify session-owned records and borrowed holder.
  NEXT: Replace those test expectations and run the mediator unit suite.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-28T11:29:56Z
  TYPE: MEASURE
  CLAIM: Removed the five unsupported parallel-cleanup cases (one session plus four components).
    Expanded sequential idempotence/use-after-clean coverage to InformationRegistry and Mediator.
    Added a session owner-teardown contract that checks owned request/staged disposal, borrowed holder
    survival, no inverse execution and cleaned-state rejection for inspection, mutation and record access.
    The complete aetheric mediator unit directory passes: 189 tests on Python 3.14.7, GIL disabled.
  EVIDENCE:
  - context_compass/artifacts/transaction_session_cleanup_race_20260928/mediator_unit_green.log:1-4
  - tests/unit/melder/aether/aetheric_mediator/test_aetheric_mediator_unit.py:733-804
  IMPACT: Tests exercise the owner-confirmed lifecycle. Runtime cleanup and lock handling are unchanged.
  NEXT: Document the test boundary, rebuild generated outputs, and close this test-only correction.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-09-28T11:32:40Z
  TYPE: FACT
  CLAIM: Documented the supported mediator lifecycle in the test component map, with the updated
    test-file extent measured at 1147 lines. Index is current; the preservation check reports zero
    removed baseline lines. The only code-file change is the test module; runtime source is unchanged.
  EVIDENCE:
  - context_compass/artifacts/transaction_session_cleanup_race_20260928/doc_preservation.json:1-5
  - context_compass/artifacts/transaction_session_cleanup_race_20260928/mediator_unit_green.log:1-4
  IMPACT: The CI assertion now follows the owner's contract instead of expanding it through a synthetic race.
  NEXT: Rebuild/check generated assets and LLM bundles as the final packaging step.
  REREAD: HELPFUL
  SCORE_0_TO_10: 9

- DATETIME: 2026-09-28T11:34:15Z
  TYPE: MEASURE
  CLAIM: Actual package asset runner rebuilt all three families and all checks are OK. LLM builder
    refreshed the tests corpus; src and other remained unchanged. All three LLM output proofs pass.
    Runtime code and its source bundle are unchanged; no lock alias, retained guard or additional
    runtime check was introduced. The test-only correction is complete.
  EVIDENCE:
  - context_compass/artifacts/transaction_session_cleanup_race_20260928/assets_check.log:1-3
  - context_compass/artifacts/transaction_session_cleanup_race_20260928/llm_build.log:1-4
  - context_compass/artifacts/transaction_session_cleanup_race_20260928/llm_check.log:1-3
  IMPACT: Deliver contract-aligned tests and verified generated outputs.
  NEXT: None.
  REREAD: HELPFUL
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Owner clarified serialized teardown after use stops and public cleaned checks on entry. Removed the
five simultaneous-destruction test cases; expanded valid idempotence, record-ownership and use-after-clean
coverage. The mediator unit directory passes all 189 tests. No runtime lock alias, retained lock,
defensive fallback, source change or version notch. Test documentation is current and preserves prior
content. Actual asset/LLM builds and checks completed successfully. No remaining work in this task.
