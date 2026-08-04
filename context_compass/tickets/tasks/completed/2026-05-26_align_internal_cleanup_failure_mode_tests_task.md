# Task: Align Internal Cleanup Failure Mode Tests

## Metadata
- Task ID: TASK-2026-05-26-align-internal-cleanup-failure-mode-tests
- Story: none
- Status: done
- Owner: codex
- Agent Name: mutres_0
- Priority: p1
- Created: 2026-05-26T17:04:42Z
- Updated: 2026-06-01T11:05:49Z

## Objective
Align the directly failing dev-ops and spell-system-state tests to the new
internal cleanup contract where cleaned objects may fail via `AttributeError`
or short-circuit no-op behavior instead of always raising `RuntimeError`.

## Ticket Contract
- ENTRY_GATE: the user explicitly directed this slice toward test updates
  rather than re-adding internal guards by default.
- EXECUTION_BOUNDARY:
  - directly failing test files under `tests/unit/melder/aether/dev_ops/**`
  - no runtime code changes unless a truly important reason to restore a guard
    is proven
  - `codex/context_compass/attention_board.md`
  - this task ticket
- DEPENDENCIES:
  - `tickets/tasks/2026-05-26_investigate_spell_system_states_guards_and_lock_usage_task.md`
- EXIT_GATE: the directly implicated test cluster is green and the updated test
  contract is documented truthfully.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if one of the failures proves a
  runtime guard is still required for correctness instead of just old test
  expectations.

## Scope Boundaries
- In scope:
  - cleanup failure-mode assertions
  - internal input-guard assertions now falling through to deeper exceptions
  - directly implicated dev-ops/spell-state unit files
- Out of scope:
  - runtime guard restoration by default
  - broad full-suite churn
  - unrelated dev-ops semantics changes

## State Transition Event
- from_state: draft
- to_state: review
- transition_reason: the directly implicated test cluster is aligned and green.

## Steps / Checklist
- [x] Read the failing assertion blocks from the reported test files.
- [x] Align cleanup failure-mode tests to the internal-only contract.
- [x] Align internal input-guard expectations where guards were intentionally removed.
- [x] Run the directly implicated dev-ops/spell-state cluster.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further
      implementation.

## Deliverables
- aligned test assertions for internal cleanup failure mode
- aligned internal input-guard expectations
- focused validation result

## Files / Paths Impacted
- `tests/unit/melder/aether/dev_ops/change_control_manager/test_change_control_manager.py`
- `tests/unit/melder/aether/dev_ops/change_control_manager/test_conflict_manager.py`
- `tests/unit/melder/aether/dev_ops/change_control_manager/test_embargo_manager.py`
- `tests/unit/melder/aether/dev_ops/change_control_manager/test_orchestrator.py`
- `tests/unit/melder/aether/dev_ops/change_control_manager/test_transaction_manager.py`
- `tests/unit/melder/aether/dev_ops/change_control_manager/test_transaction_session_expanded.py`
- `tests/unit/melder/aether/dev_ops/incident_manager/test_incident.py`
- `tests/unit/melder/aether/dev_ops/incident_manager/test_incident_manager.py`
- `tests/unit/melder/aether/dev_ops/test_dev_ops_manager.py`
- `tests/unit/melder/aether/dev_ops/test_devops_information_registry.py`
- `tests/unit/melder/aether/dev_ops/spell_system_states/test_spell_system_state.py`
- `tests/unit/melder/aether/dev_ops/spell_system_states/test_spell_system_states.py`
- `tests/unit/melder/aether/dev_ops/test_transaction_surface_batch.py`
- `codex/context_compass/attention_board.md`
- `codex/context_compass/tickets/tasks/2026-05-26_align_internal_cleanup_failure_mode_tests_task.md`

## Validation
- Ran:
  - `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\aether\dev_ops\change_control_manager\test_change_control_manager.py tests\unit\melder\aether\dev_ops\change_control_manager\test_conflict_manager.py tests\unit\melder\aether\dev_ops\change_control_manager\test_embargo_manager.py tests\unit\melder\aether\dev_ops\change_control_manager\test_orchestrator.py tests\unit\melder\aether\dev_ops\change_control_manager\test_transaction_manager.py tests\unit\melder\aether\dev_ops\change_control_manager\test_transaction_session_expanded.py tests\unit\melder\aether\dev_ops\incident_manager\test_incident.py tests\unit\melder\aether\dev_ops\incident_manager\test_incident_manager.py tests\unit\melder\aether\dev_ops\test_dev_ops_manager.py tests\unit\melder\aether\dev_ops\test_devops_information_registry.py tests\unit\melder\aether\dev_ops\spell_system_states\test_spell_system_state.py tests\unit\melder\aether\dev_ops\spell_system_states\test_spell_system_states.py tests\unit\melder\aether\dev_ops\test_transaction_surface_batch.py`
- Result:
  - `323 passed, 1 warning`

## Risks / Rollback Notes
- Risk: some tests now deliberately allow `AttributeError`, which encodes the
  new “dead internal object may crash hard” posture.
  Rollback: re-tighten only if we later choose to restore deterministic cleaned
  guards for specific high-value surfaces.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No closure without acceptance confirmation and board-sync completion.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [x] Validation status recorded
- [x] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [x] Notes quality maintained (`SCORE_0_TO_10` >=
      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: ticket closure

## Noting Behavior
- Note focus: direct failure-mode drift, direct test alignment, and one-step
  continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-06-01T11:05:49Z
  TYPE: DECISION
  CLAIM: The user explicitly accepted this lane as complete and requested that
    it be turned in and moved out of active routing.
  EVIDENCE:
  - user_instruction
  IMPACT: This ticket is now closed and should no longer appear in active
    board routing.
  NEXT: none
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
- DATETIME: 2026-05-26T17:04:42Z
  TYPE: FACT
  CLAIM: The failing cluster split into two categories: cleaned-object tests
    that still required `RuntimeError`, and internal input-guard tests that
    still required `ValueError`. The updated internal contract is:
    - cleaned dev-ops/spell-state objects may now fail via `RuntimeError` or
      `AttributeError`
    - some no-op branches can return safely after cleanup if they never touch
      torn state
    - internal bad-input calls may now fall through to `AttributeError`
      instead of fail-fast `ValueError`
  EVIDENCE:
  - user_provided_failure_output
  - tests/unit/melder/aether/dev_ops/spell_system_states/test_spell_system_states.py:974-983
  - tests/unit/melder/aether/dev_ops/test_dev_ops_manager.py:100-229
  IMPACT: This lets the test surface match the new internal-library posture
    without forcing runtime guard restoration.
  NEXT: keep using the current focused test cluster as the validation ring for
    further internal guard shedding in dev-ops/state objects.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-26T17:04:42Z
  TYPE: MEASURE
  CLAIM: The directly implicated dev-ops/spell-state failure cluster is green
    after test alignment. Current focused result: `323 passed, 1 warning`.
  EVIDENCE:
  - validation_result: `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\aether\dev_ops\change_control_manager\test_change_control_manager.py tests\unit\melder\aether\dev_ops\change_control_manager\test_conflict_manager.py tests\unit\melder\aether\dev_ops\change_control_manager\test_embargo_manager.py tests\unit\melder\aether\dev_ops\change_control_manager\test_orchestrator.py tests\unit\melder\aether\dev_ops\change_control_manager\test_transaction_manager.py tests\unit\melder\aether\dev_ops\change_control_manager\test_transaction_session_expanded.py tests\unit\melder\aether\dev_ops\incident_manager\test_incident.py tests\unit\melder\aether\dev_ops\incident_manager\test_incident_manager.py tests\unit\melder\aether\dev_ops\test_dev_ops_manager.py tests\unit\melder\aether\dev_ops\test_devops_information_registry.py tests\unit\melder\aether\dev_ops\spell_system_states\test_spell_system_state.py tests\unit\melder\aether\dev_ops\spell_system_states\test_spell_system_states.py tests\unit\melder\aether\dev_ops\test_transaction_surface_batch.py`
  IMPACT: The current runtime edits do not require immediate guard restoration
    to keep this local dev-ops/state test surface green.
  NEXT: if more failures appear elsewhere, use them to decide whether to
    restore any deterministic cleaned-guard semantics selectively.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task is a bounded test-alignment slice for the new internal cleanup
failure mode across dev-ops and spell-state objects. The directly implicated
cluster is green without runtime guard restoration.

