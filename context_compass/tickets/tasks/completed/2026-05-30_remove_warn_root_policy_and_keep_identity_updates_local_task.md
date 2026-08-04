# Task: Remove Warn Root Policy And Keep Identity Updates Local

## Metadata
- Task ID: TASK-2026-05-30-remove-warn-root-policy-and-keep-identity-updates-local
- Story: none
- Status: done
- Owner: codex
- Agent Name: searcher_0
- Priority: p1
- Created: 2026-05-30T11:39:57Z
- Updated: 2026-06-01T11:37:34Z

## Objective
Implement the first bounded mediator-policy cleanup slice:
1. remove `warn`,
2. remove the confusing global root-arbitration knobs,
3. keep the `disable_*` flags and wait timeout,
4. preserve the already-landed local-only `DevopsIdentity.update_metadata(...)`
   contract.

## Ticket Contract
- ENTRY_GATE: the current config overlap and eager identity-refresh seams are already evidenced in the active investigation task.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/aetheric_frame/aetheric_frame_configuration.py`
  - `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py`
  - `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py`
  - directly implicated tests/helpers only
  - `codex/context_compass/attention_board.md`
  - this task ticket
- DEPENDENCIES:
  - `tickets/tasks/2026-05-30_investigate_mediator_policy_and_lazy_devops_reporting_task.md`
  - `tickets/tasks/2026-05-24_make_parallel_root_transactions_default_task.md`
- EXIT_GATE: the old `warn` / `allow_multiple_root_transactions` / `change_control_mode` root-arbitration model is removed from the touched runtime/config surface, focused validation is green, and the lane is ready for the next strategy-owned policy slice.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the touched tests prove there is still hidden dependence on the old global root-arbitration surface outside the bounded file set.

## Scope Boundaries
- In scope:
  - root-session policy fields and mediator logic
  - directly implicated frame-posture helpers/tests
  - direct mediator tests
- Out of scope:
  - strategy-owned overlap/queue redesign
  - broader registry/reporting redesign
  - unrelated transaction-family changes

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly asked to start fixing the config/model now that the hot-path identity refresh is removed.

## Steps / Checklist
- [ ] Remove `warn` from the root-session policy surface.
- [ ] Remove the confusing global root-arbitration knobs from frame config and mediator.
- [ ] Keep `disable_*` flags and `max_transaction_wait_time_in_seconds`.
- [ ] Align directly implicated tests/helpers to the new policy surface.
- [ ] Run focused validation.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further implementation.

## Deliverables
- simplified root-session config surface
- aligned mediator logic
- focused green validation ring

## Files / Paths Impacted
- `src/melder/aether/aetheric_frame/aetheric_frame_configuration.py`
- `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py`
- `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py`
- `tests/unit/melder/aether/test_aetheric_frame_configuration.py`
- `tests/unit/melder/aether/dev_ops/change_control_manager/test_transaction_mediator.py`
- `tests/unit/melder/aether/dev_ops/change_control_manager/test_transaction_mediator_expanded.py`
- `tests/_frame_posture_test_support.py`
- `codex/context_compass/attention_board.md`
- this task ticket

## Validation
- Not run.
- Recommended commands:
  - `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\aether\test_aetheric_frame_configuration.py tests\unit\melder\aether\dev_ops\change_control_manager\test_transaction_mediator.py tests\unit\melder\aether\dev_ops\change_control_manager\test_transaction_mediator_expanded.py`

## Risks / Rollback Notes
- Risk: stale tests or helper copies still assume the old root-arbitration fields exist.
  Rollback: keep the change localized and align only directly implicated expectations.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
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
- CLEANUP_TRIGGER: user-directed after the config/model slice is accepted

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
- DATETIME: 2026-05-30T11:39:57Z
  TYPE: PLAN
  CLAIM: The first implementation slice is now narrow and explicit. We are not
    redesigning strategy-owned overlap policy yet. We are only removing the
    confusing global root-arbitration model (`warn`, `change_control_mode`,
    `allow_multiple_root_transactions`) while keeping the `disable_*` flags,
    the wait timeout, and the already-landed local-only identity metadata
    contract.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/aetheric_frame_configuration.py:85-95
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py:171-200
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py:929-972
  - tests/unit/melder/aether/test_aetheric_frame_configuration.py:165-514
  - tests/unit/melder/aether/dev_ops/change_control_manager/test_transaction_mediator.py:82-299
  IMPACT: This gives us a small safe cleanup step before the larger strategy-owned blast-radius redesign.
  NEXT: patch config, mediator, and directly implicated tests/helpers together, then run the focused validation ring.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-30T11:49:12Z
  TYPE: MEASURE
  CLAIM: The bounded config/model slice is landed and the focused ring is
    green. The runtime surface no longer carries `change_control_mode`,
    `allow_multiple_root_transactions`, or `warn` semantics in the touched
    frame config and mediator code. The remaining root-session knob is the
    coarse queue toggle plus its timeout, while the `disable_*` flags remain
    intact. The already-landed local-only `DevopsIdentity.update_metadata(...)`
    contract still holds.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/aetheric_frame_configuration.py:51-72
  - src/melder/aether/aetheric_frame/aetheric_frame_configuration.py:77-194
  - src/melder/aether/aetheric_frame/aetheric_frame_configuration.py:561-583
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py:171-200
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py:68-97
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py:221-287
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py:929-980
  - src/melder/aether/aetheric_frame/dev_ops/devops_identity.py:272-292
  - validation_result: `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\aether\test_aetheric_frame_configuration.py tests\unit\melder\aether\dev_ops\change_control_manager\test_transaction_mediator.py tests\unit\melder\aether\dev_ops\change_control_manager\test_transaction_mediator_expanded.py` -> `80 passed, 1 warning`
  IMPACT: The remaining design problem is no longer stale config overlap. It is
    deciding whether the coarse frame-global queue survives at all, or gets
    moved behind strategy/conflict/embargo-owned overlap logic.
  NEXT: discuss whether the next slice should keep the queue as a coarse
    backpressure tool or move queueing behind strategy-owned overlap analysis.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-30T12:17:00Z
  TYPE: MEASURE
  CLAIM: The explicit registry/event slice is landed and the wider focused ring
    is green too. Spellbook↔root-conduit ownership is now maintained explicitly
    from `AethericFrame.register_root_conduit(...)` /
    `unregister_root_conduit(...)` instead of being derived from identity
    metadata, and live transaction registration now indexes scope keys directly.
    The registry no longer rebuilds spellbook/conduit relations during
    `register_identity(...)`, `unregister_identity(...)`, or `refresh_identity(...)`.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/aetheric_frame.py:261-325
  - src/melder/aether/aetheric_frame/dev_ops/devops_information_registry.py:236-426
  - src/melder/aether/aetheric_frame/dev_ops/devops_information_registry.py:491-612
  - src/melder/aether/aetheric_frame/dev_ops/devops_information_registry.py:936-1107
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py:1015-1044
  - tests/unit/melder/aether/dev_ops/test_devops_information_registry.py:140-170
  - tests/unit/melder/aether/dev_ops/test_devops_information_registry.py:415-470
  - tests/unit/melder/aether/dev_ops/test_devops_information_registry.py:520-569
  - validation_result: `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\aether\test_aetheric_frame_configuration.py tests\unit\melder\aether\dev_ops\test_devops_identity.py tests\unit\melder\aether\dev_ops\test_devops_information_registry.py tests\unit\melder\aether\dev_ops\change_control_manager\test_transaction_mediator.py tests\unit\melder\aether\dev_ops\change_control_manager\test_transaction_mediator_expanded.py` -> `128 passed, 1 warning`
  IMPACT: The mirrored reality is now closer to the intended fast model:
    local-only identity updates, explicit root-conduit ownership edges, and
    scope-aware live transaction indexing without metadata-derived relation scans.
  NEXT: decide whether the next slice removes the remaining coarse queue or
    moves queueing behind strategy/conflict/embargo-owned overlap analysis.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the first bounded runtime cleanup after the hot-path identity
refresh removal: simplify the root-session config/model surface without trying
to solve the full strategy-owned overlap design in the same pass.

