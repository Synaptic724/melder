# Task: Make Parallel Root Transactions Default

## Metadata
- Task ID: TASK-2026-05-24-make-parallel-root-transactions-default
- Story: none
- Status: done
- Owner: codex
- Agent Name: searcher_0
- Priority: p1
- Created: 2026-05-24T22:45:02Z
- Updated: 2026-06-01T11:37:34Z

## Objective
Turn the mediator root-session gate off by default so multi-threaded rooted
transactions are allowed in the normal runtime, while keeping explicit queue
and reject controls available when a frame posture turns them on.

## Ticket Contract
- ENTRY_GATE: certification is active for `searcher_0`, and this task is routed
  from `attention_board.md` before implementation starts.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/aetheric_frame/aetheric_frame_configuration.py`
  - directly implicated tests that assert the old default
  - `codex/context_compass/attention_board.md`
  - this task ticket
- DEPENDENCIES:
  - `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py`
  - `tests/integration/melder/aether/test_aether_integration_change_control_transactions.py`
- EXIT_GATE:
  - default frame posture allows multiple root transactions
  - explicit queue/reject paths still work when enabled manually
  - focused validation passes
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if additional root-gating callsites exist outside the frame posture default seam.

## Scope Boundaries
- In scope:
  - default frame posture for root-session gating
  - directly implicated unit/integration expectations
- Out of scope:
  - redesign of strategy-owned suppression
  - removal of queue/reject runtime support
  - removal of `warn` as a mode

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly wants the mediator root gate turned off by default until the finer-grained policy model is fixed.

## Steps / Checklist
- [ ] Verify the root-session gate is controlled by `allow_multiple_root_transactions` in the frame posture default.
- [ ] Change the default frame posture to allow parallel root transactions.
- [ ] Update directly implicated tests that assert the old default.
- [ ] Run focused validation for frame configuration, mediator/unit expectations, and live change-control integration.
- [ ] Summarize the resulting default runtime behavior.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further implementation.

## Deliverables
- updated default frame posture for root-session gating
- focused validation result

## Files / Paths Impacted
- `src/melder/aether/aetheric_frame/aetheric_frame_configuration.py`
- directly implicated tests
- `codex/context_compass/attention_board.md`
- this task ticket

## Validation
- Not run.
- Recommended commands:
  - `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\aether\dev_ops\change_control_manager\test_transaction_mediator.py tests\integration\melder\aether\test_aether_integration_change_control_transactions.py`

## Risks / Rollback Notes
- Risk: stale tests or docs still assume the old root-gating default.
  Rollback: keep the change localized to the frame default seam and patch only the directly implicated expectations.

## Applicable Anti-Patterns
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No drive-by refactors outside the default posture seam.
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
- CLEANUP_TRIGGER: user-directed after the default runtime behavior is accepted

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-06-01T11:37:34Z
  TYPE: DECISION
  CLAIM: The user explicitly accepted this remaining active lane for closure and
    requested that it be turned in and moved to the completed task set.
  EVIDENCE:
  - user_instruction
  IMPACT: This task is closed and should no longer route active work on the
    attention board.
  NEXT: none
  REREAD: HELPFUL
  SCORE_0_TO_10: 8
- DATETIME: 2026-05-24T22:45:02Z
  TYPE: PLAN
  CLAIM: The user does not want the current root-session gate killing normal multi-threaded work by default. The meaningful temporary fix is to make `allow_multiple_root_transactions` the default frame posture, which makes the mediator root gate step aside in normal runtime while preserving the explicit queue/reject controls for frames that opt into them.
  EVIDENCE:
  - user_request: current thread
  - src/melder/aether/aetheric_frame/aetheric_frame_configuration.py:85-95
  - src/melder/aether/aetheric_frame/aetheric_frame_configuration.py:571-583
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py:945-959
  IMPACT: This turns the current global root gate off by default without ripping out the mediator session layer or the explicit queue/reject controls.
  NEXT: patch the frame default, then update the directly implicated tests and rerun focused validation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-24T22:45:02Z
  TYPE: MEASURE
  CLAIM: The default frame posture now allows multiple root transactions. `AethericFrameConfiguration` constructor defaults and `with_defaults()` both set `allow_multiple_root_transactions=True`, so the mediator root-session gate now steps aside in normal runtime unless a frame explicitly turns queue/reject behavior on. The directly implicated frame-config and live change-control integration rings are green.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/aetheric_frame_configuration.py:85-95
  - src/melder/aether/aetheric_frame/aetheric_frame_configuration.py:571-583
  - tests/unit/melder/aether/test_aetheric_frame_configuration.py
  - validation_result: `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\aether\test_aetheric_frame_configuration.py tests\integration\melder\aether\test_aether_integration_change_control_transactions.py`
  IMPACT: The normal runtime no longer treats parallel rooted transactions as globally dangerous by default, while explicit queue/reject controls still remain available for frames that choose to enable them.
  NEXT: if you want, the next cleanup is to collapse the confusing `change_control_mode` surface and move toward one cleaner root arbitration policy plus strategy-scoped suppression.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task exists to make parallel rooted transactions the default runtime
behavior by changing the frame posture default rather than by deleting the
mediator or its explicit queue/reject controls.

