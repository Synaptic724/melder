# Task: Add Three-Root Change-Control Transaction Integration

## Metadata
- Task ID: TASK-2026-05-24-add-three-root-change-control-transaction-integration
- Story: none
- Status: done
- Owner: codex
- Agent Name: searcher_0
- Priority: p1
- Created: 2026-05-24T22:00:45Z
- Updated: 2026-06-01T11:37:34Z

## Objective
Add real integration coverage for the live change-control transaction runtime
using **three rooted Spellbooks/Conduits** in one frame so we can show
`disabled`, `strict`, and queued root-session behavior in actual runtime use,
not just mediator-only unit tests.

## Ticket Contract
- ENTRY_GATE: certification is active for `searcher_0`, and this task is routed
  from `attention_board.md` before implementation starts.
- EXECUTION_BOUNDARY:
  - `tests/integration/melder/aether/test_aether_integration_change_control_transactions.py`
  - `codex/context_compass/attention_board.md`
  - this task ticket
- DEPENDENCIES:
  - `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py`
  - `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/bind_transaction_strategy.py`
  - `src/melder/aether/conduit/conduit.py`
  - `src/melder/aether/spellbook/spellbook.py`
- EXIT_GATE:
  - three-root runtime integration coverage exists for `disabled`, `strict`, and queued root bind behavior
  - focused integration validation passes
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the live runtime contract is materially different from the current mediator/strategy unit model and needs a different integration target.

## Scope Boundaries
- In scope:
  - three-root bind transaction integration tests
  - live frame change-control behavior across multiple rooted spellbooks/conduits
- Out of scope:
  - mediator implementation changes
  - lesser conduit transaction behavior
  - link/cluster/transfer integration expansion beyond what is needed for the three-root bind story

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly asked for three roots and to show the transaction behaviors in live runtime tests.

## Steps / Checklist
- [ ] Map the existing change-control integration file and identify the current two-root coverage seams.
- [ ] Add three-root integration coverage for disabled mode overlap.
- [ ] Add three-root integration coverage for strict-mode conflict rejection.
- [ ] Add three-root integration coverage for queued root-session handoff.
- [ ] Run the focused integration file.
- [ ] Summarize the live transaction behavior and any remaining gaps.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further implementation.

## Deliverables
- three-root integration tests in the live change-control integration file
- one focused integration validation result

## Files / Paths Impacted
- `tests/integration/melder/aether/test_aether_integration_change_control_transactions.py`
- `codex/context_compass/attention_board.md`
- this task ticket

## Validation
- Not run.
- Recommended commands:
  - `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q tests\integration\melder\aether\test_aether_integration_change_control_transactions.py`

## Risks / Rollback Notes
- Risk: the mediator unit policy and the live runtime bind path are not identical in the current frame configuration, so one or more requested behaviors may need a different integration setup shape.
  Rollback: keep the integration additions localized to the existing file and fail with direct evidence if the runtime contract differs.

## Applicable Anti-Patterns
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No drive-by refactors outside the live change-control integration file.
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
- CLEANUP_TRIGGER: user-directed after the live three-root transaction behavior is accepted

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
- DATETIME: 2026-05-24T22:00:45Z
  TYPE: PLAN
  CLAIM: The user wants the root-session transaction policy shown in the real runtime with **three rooted Spellbooks/Conduits**, not just at the mediator unit layer. The requested behaviors are disabled-mode overlap, strict-mode conflict rejection, and queued root-session handoff.
  EVIDENCE:
  - user_request: current thread
  - tests/unit/melder/aether/dev_ops/change_control_manager/test_transaction_mediator.py:61-228
  - tests/integration/melder/aether/test_aether_integration_change_control_transactions.py:85-222
  IMPACT: The next slice is to extend the existing live change-control integration file instead of widening into mediator implementation or new test harness infrastructure.
  NEXT: map the current two-root integration coverage seams in the existing file and add three-root versions for the requested runtime behaviors.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-24T22:00:45Z
  TYPE: FACT
  CLAIM: The live integration file already covers two important pieces with **two roots**: disabled mode allows overlapping bind requests, and strict-mode conflict admission rejects overlapping bind requests. The missing runtime proof is the **three-root** version plus the queued root-session behavior; warn-mode root coexistence is still only mediator-unit coverage today.
  EVIDENCE:
  - tests/integration/melder/aether/test_aether_integration_change_control_transactions.py:162-222
  - tests/unit/melder/aether/dev_ops/change_control_manager/test_transaction_mediator.py:92-228
  IMPACT: The cheapest real-runtime cut is to extend the existing integration file with three-root disabled, strict, and queued cases instead of inventing a new harness or widening into mediator code.
  NEXT: add three-root helper setup plus those three integration tests in the existing file and run the focused integration file.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-24T22:00:45Z
  TYPE: MEASURE
  CLAIM: The three-root live runtime slice is landed and the focused integration file is green. The file now proves three rooted Spellbooks/Conduits in one frame for: disabled-mode overlapping bind admission, strict-mode rejection of overlapping bind requests, and queued FIFO root-session handoff across three roots. Warn-mode root coexistence is still covered only at the mediator unit layer.
  EVIDENCE:
  - tests/integration/melder/aether/test_aether_integration_change_control_transactions.py
  - validation_result: `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q tests\integration\melder\aether\test_aether_integration_change_control_transactions.py`
  IMPACT: We now have real runtime proof for the three requested root-session behaviors without widening into mediator implementation changes.
  NEXT: if needed, add a separate three-root warn-mode integration case; otherwise use this file as the live reference for root-session bind behavior.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-24T22:00:45Z
  TYPE: FACT
  CLAIM: The current disabled-mode integration proves overlapping three-root bind sessions on the same thread, but it does not prove that other threads are not being blocked by the mediator root-session gate. Same-thread multi-root starts already bypass `_wait_for_turn_locked(...)` through the `allow_same_thread_parallel=True` path in `TransactionMediator.begin_transaction(...)`, so we still need one true cross-thread disabled-mode check with distinct scopes to prove the gate is actually out of the way.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py:469-472
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py:945-966
  - tests/integration/melder/aether/test_aether_integration_change_control_transactions.py:162-192
  IMPACT: Without a threaded disabled-mode integration, we would be overstating what the current runtime proof actually covers.
  NEXT: add one three-thread disabled-mode integration with distinct scope keys and release gating so all three roots must enter before teardown is allowed.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-24T22:00:45Z
  TYPE: MEASURE
  CLAIM: The cross-thread disabled-mode proof is now landed too. With `TransactionMediator.configure(change_control_mode="disabled", allow_multiple_root_transactions=False, queue_competing_root_transactions=False, ...)`, three rooted Spellbooks on three different threads all enter bind transactions with distinct scope keys before teardown is released, and the frame transaction manager reports all three requests in flight at once. That proves the mediator root-session gate is not serializing them in disabled mode; admission is allowed to proceed to actual conflict scope evaluation instead.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py:945-966
  - tests/integration/melder/aether/test_aether_integration_change_control_transactions.py
  - validation_result: `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q tests\integration\melder\aether\test_aether_integration_change_control_transactions.py`
  IMPACT: We can now answer the policy question from live runtime proof: mediator `disabled` means the global root-session gate is bypassed, but this is still a frame-global policy, not a bind-only or strategy-local queue rule.
  NEXT: explain the two different “disabled” concepts clearly and call out that transaction queueing is currently global at the mediator layer, not per strategy family.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-24T22:00:45Z
  TYPE: MEASURE
  CLAIM: The live integration file now covers the non-disabled runtime questions too. In `warn` mode, three rooted Spellbooks on three threads all enter bind transactions without queueing and the transaction manager reports three in-flight requests at once, which proves parallel root sessions are allowed without disabling the mediator. In queued mode, a root bind on one thread blocks a root link on another thread until the bind root exits, which proves queueing is global at the mediator root-session layer rather than bind-only or strategy-local.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py:945-966
  - tests/integration/melder/aether/test_aether_integration_change_control_transactions.py
  - validation_result: `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q tests\integration\melder\aether\test_aether_integration_change_control_transactions.py`
  IMPACT: We now have real runtime proof for all the policy questions that mattered: disabled really bypasses the gate, warn allows parallel roots without disabling the mediator, and queueing is a frame-global root-session policy that blocks other transaction families too.
  NEXT: summarize the current mediator policy model clearly: root-session gate first, strategy planning second, so per-family queueing is not a feature today.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task exists to prove the live root-session transaction behavior in the
actual runtime using three rooted spellbooks/conduits in one frame, specifically
for disabled, strict, and queued bind-family behavior.

