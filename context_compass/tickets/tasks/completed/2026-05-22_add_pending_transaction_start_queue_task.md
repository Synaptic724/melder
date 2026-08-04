Completed: 2026-05-23T19:26:44Z
Summary: Added the queued competing-root-start path with FIFO drain proof on both unit and
real component surfaces.
Summary: Closed by user cleanup request after the queue semantics were validated and absorbed
into later mediator/runtime work.

# Task: Add Pending Transaction Start Queue

## Metadata
- Task ID: TASK-2026-05-22-add-pending-transaction-start-queue
- Story: STORY-2026-05-22-define-spellindex-transfer-and-registration-semantics
- Status: done
- Owner: codex
- Agent Name: mutres_0
- Priority: p1
- Created: 2026-05-22T17:03:00Z
- Updated: 2026-05-23T19:26:44Z

## Objective
Add a queued pending-start path to `TransactionMediator` so competing threads
can wait for their turn instead of always throwing immediately, using a
condition-based queue and frame-configured timeout.

## Ticket Contract
- ENTRY_GATE: the user explicitly requested a pending-start queue and pointed
  to `CreationGate` as the reference model.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/*`
  - `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py`
  - `src/melder/aether/aetheric_frame/aetheric_frame_configuration.py`
  - focused unit/component tests under the existing change-control test surfaces
- DEPENDENCIES:
  - `tickets/tasks/2026-05-22_add_frame_change_control_configuration_flags_task.md`
  - `tickets/tasks/2026-05-22_scaffold_transaction_mediator_and_session_task.md`
  - `tickets/tasks/2026-05-22_validate_transaction_mediator_unit_and_component_task.md`
- EXIT_GATE: the mediator can queue competing root starts, wait up to the
  configured timeout, and hand the slot to the next waiting thread after root
  finalization; focused tests are green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if queueing semantics force an
  incompatible change to strict/warn/disabled policy meaning.

## Scope Boundaries
- In scope:
  - pending-start spec object
  - mediator wait queue and condition signaling
  - frame-config queue flag + timeout
  - focused tests
- Out of scope:
  - full runtime wiring into Spellbook/Conduit
  - capability matrix redesign
  - transfer/link/cluster migration

## State Transition Event
- from_state: ready
- to_state: in_progress
- transition_reason: the user explicitly requested queued waiting for
  competing root starts instead of immediate throw-only behavior.

## Steps / Checklist
- [x] Add queueing config to `AethericFrameConfiguration`.
- [x] Add pending-start wait queue to `TransactionMediator`.
- [x] Add focused tests for timeout, FIFO wakeup, and turn-taking.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before
      further investigation.

## Deliverables
- queue-enabled mediator path
- queue config defaults and timeout
- focused unit/component validation

## Files / Paths Impacted
- `codex/context_compass/tickets/tasks/2026-05-22_add_pending_transaction_start_queue_task.md`
- `codex/context_compass/attention_board.md`
- `src/melder/aether/aetheric_frame/aetheric_frame_configuration.py`
- `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py`
- `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_session.py`
- `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py`
- `tests/unit/melder/aether/dev_ops/change_control_manager/test_transaction_mediator.py`
- `tests/component/melder/aether/dev_ops/change_control_manager/test_change_control_manager_component.py`

## Validation
- Ran:
  - `pytest -q tests/unit/melder/aether/test_aetheric_frame_configuration.py`
  - `pytest -q tests/unit/melder/aether/dev_ops/change_control_manager/test_transaction_mediator.py`
  - `pytest -q tests/component/melder/aether/dev_ops/change_control_manager/test_change_control_manager_component.py`

## Risks / Rollback Notes
- Risk: queueing before admission can drift from strict/warn semantics if the
  precedence rules are not explicit.
  Rollback: keep queueing behind an explicit frame-config flag and preserve the
  current strict throw path when queueing is disabled.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No runtime entrypoint rewiring in the queueing slice.

## Done Checklist
- [ ] Steps complete and checked off
- [ ] Deliverables produced and linked
- [ ] Documentation updated (if needed)
- [ ] Validation status recorded
- [ ] Unknown-first discipline followed (`UNKNOWN` promoted to `FACT` only with evidence)
- [ ] Notes quality maintained (`SCORE_0_TO_10` >=
-      `workflow.ticket_microcycle.minimum_note_score`)
- [ ] Applicable anti-pattern checks are clear or escalated with evidence.
- [ ] Acceptance criteria reviewed with user and confirmed
- [ ] Board sync completed for successor routing or closure anchor update.

## Artifact Links (Optional)
- ARTIFACTS_REQUIRED: false
- ARTIFACT_PATHS:
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: ticket closure

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-05-22T17:03:00Z
  TYPE: FACT
  CLAIM: `CreationGate` is the right local reference for the wait semantics,
    not for transaction identity. Its model is: close/open admission state,
    condition-style waiting through an event, explicit ticket accounting, and a
    timeout-based drain path. For the transaction queue we want the same broad
    shape but with a pending-start queue ahead of admission: wait first, admit
    second, and wake the next queued contender after the root session
    finalizes. That keeps embargo/in-flight state honest while still allowing
    turn-taking between threads.
  EVIDENCE:
  - src/melder/utilities/synchronization/creation_gate.py:1-306
  - src/melder/utilities/synchronization/creation_gate_controller.py:1-798
  - tests/unit/melder/utilities/synchronization/test_creation_gate.py:1-296
  - tests/unit/melder/utilities/synchronization/test_creation_gate_controller.py:1-527
  IMPACT: The queue should be implemented inside `TransactionMediator` as a
    pending-start wait structure with timeout and wakeup, not by prematurely
    admitting and embargoing waiting requests.
  NEXT: add the queue config surface and implement a mediator-local pending
    start wait queue using a condition.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-22T17:09:00Z
  TYPE: MEASURE
  CLAIM: The queued pending-start slice is landed and the focused ring is green
    (`48 passed`). `AethericFrameConfiguration` now carries
    `queue_competing_root_transactions` and
    `max_transaction_wait_time_in_seconds`, the frame posture merge path carries
    them into the live frame-owned config, and `TransactionMediator` now uses a
    condition-based FIFO pending-start queue that waits before admission is
    turned into a live root session. Focused tests now cover:
    - queued single waiter turn-taking,
    - timeout when the active root never finishes,
    - real component turn-taking on a frame-owned manager.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/aetheric_frame_configuration.py:1-420
  - src/melder/aether/aetheric_frame/aetheric_frame.py:420-446
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py:153-188
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py:1-420
  - tests/unit/melder/aether/test_aetheric_frame_configuration.py:1-240
  - tests/unit/melder/aether/dev_ops/change_control_manager/test_transaction_mediator.py:1-320
  - tests/component/melder/aether/dev_ops/change_control_manager/test_change_control_manager_component.py:500-620
  IMPACT: Competing root transactions can now wait their turn instead of only
    failing immediately, while the queue still preserves the "wait first,
    admit second" rule.
  NEXT: get user review on the queueing slice, then wire the first live
    Spellbook/Conduit transaction entry path to use the mediator instead of the
    scalar local state.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-22T17:14:00Z
  TYPE: MEASURE
  CLAIM: The queue proof is now stronger. Focused tests now include a
    five-waiter unit proof that queued root starts drain one by one in FIFO
    order with `max_active == 1`, plus a real component proof that five worker
    threads queue behind one active root session and are allowed through one at
    a time on the frame-owned mediator surface. The updated focused ring is
    green (`36 passed` for mediator + component queue tests).
  EVIDENCE:
  - tests/unit/melder/aether/dev_ops/change_control_manager/test_transaction_mediator.py:150-258
  - tests/component/melder/aether/dev_ops/change_control_manager/test_change_control_manager_component.py:500-634
  IMPACT: We now have direct proof that the pending-start queue handles more
    than one waiter and preserves one-at-a-time root admission under
    contention.
  NEXT: answer from the observed five-thread queue behavior and move on when
    directed.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This is the queued competing-root-start slice requested after the mediator
foundation and broader validation were already green.
