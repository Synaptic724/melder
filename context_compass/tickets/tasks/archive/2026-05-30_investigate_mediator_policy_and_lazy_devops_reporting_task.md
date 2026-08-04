# Task: Investigate Mediator Policy And Lazy DevOps Reporting

## Metadata
- Task ID: TASK-2026-05-30-investigate-mediator-policy-and-lazy-devops-reporting
- Story: none
- Status: in_progress
- Owner: codex
- Agent Name: searcher_0
- Priority: p1
- Created: 2026-05-30T10:28:39Z
- Updated: 2026-05-30T20:09:30Z

## Objective
Define the smallest correct implementation plan for:
1. replacing the overlapping mediator root-session config surface, and
2. removing eager `DevopsIdentity`-driven registry refresh from the hot path.

## Ticket Contract
- ENTRY_GATE: the user explicitly requested a dedicated epic plus an investigation/plan slice before implementation.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/aetheric_frame/aetheric_frame_configuration.py`
  - `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py`
  - `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py`
  - `src/melder/aether/aetheric_frame/dev_ops/devops_identity.py`
  - `src/melder/aether/aetheric_frame/dev_ops/devops_information_registry.py`
  - directly implicated runtime callsites in `conduit.py` and `conduit_ward.py`
  - `codex/context_compass/attention_board.md`
  - this task ticket
- DEPENDENCIES:
  - `tickets/epics/2026-05-30_simplify_mediator_root_policy_and_lazy_devops_reporting_epic.md`
  - `tickets/tasks/2026-05-23_investigate_spellbook_conduit_devops_dependency_cleanup_task.md`
  - `tickets/tasks/2026-05-24_make_parallel_root_transactions_default_task.md`
- EXIT_GATE: the replacement config model, eager-refresh removal seam, and first implementation order are explicit enough to patch in the next prompt.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the replacement policy still needs a second arbitration layer beyond the current requested two-change slice.

## Scope Boundaries
- In scope:
  - root-session config semantics
  - mediator arbitration logic
  - eager identity refresh call path
  - mediator-owned registry update candidates
- Out of scope:
  - implementation
  - broader transaction-family redesign
  - full reporting-strategy architecture beyond what is needed to plan the first cut

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly wants the plan first and implementation in a later prompt.

## Steps / Checklist
- [ ] Confirm the current root-session policy overlap and exact precedence.
- [ ] Confirm the eager `DevopsIdentity -> DevopsInformationRegistry` refresh path and direct runtime callers.
- [ ] Define the replacement config model.
- [ ] Define the first mediator-owned registry update seam.
- [ ] Write the bounded implementation order for the next prompt.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further investigation.

## Deliverables
- one explicit replacement config model
- one explicit lazy-registry-update ownership plan
- one bounded implementation order for the next prompt

## Files / Paths Impacted
- `codex/context_compass/tickets/tasks/2026-05-30_investigate_mediator_policy_and_lazy_devops_reporting_task.md`
- `codex/context_compass/tickets/epics/2026-05-30_simplify_mediator_root_policy_and_lazy_devops_reporting_epic.md`
- `codex/context_compass/attention_board.md`

## Validation
- Not run.
- Recommended commands:
  - `rg -n "change_control_mode|allow_multiple_root_transactions|queue_competing_root_transactions|max_transaction_wait_time_in_seconds" src/melder/aether/aetheric_frame/aetheric_frame_configuration.py src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py`
  - `rg -n "update_metadata\\(|refresh_identity\\(" src/melder/aether/aetheric_frame/dev_ops/devops_identity.py src/melder/aether/aetheric_frame/dev_ops/devops_information_registry.py src/melder/aether/conduit/conduit.py src/melder/aether/conduit/conduit_ward/conduit_ward.py`

## Risks / Rollback Notes
- Risk: moving registry refresh responsibility off identity updates breaks derived relation maintenance.
  Rollback: keep the current relation rebuild behavior until a specific mediator-owned replacement point is patched.

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
- CLEANUP_TRIGGER: user-directed after the plan is accepted

## Noting Behavior
- Note focus: tactical findings, concrete impacts, and single-step continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-05-30T10:28:39Z
  TYPE: FACT
  CLAIM: The current root-session config surface is overlapping in exactly the
    way the user called out. Root arbitration is spread across
    `change_control_mode`, `allow_multiple_root_transactions`,
    `queue_competing_root_transactions`, and
    `max_transaction_wait_time_in_seconds`, with effective precedence inside
    `_wait_for_turn_locked(...)` rather than in one explicit model.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/aetheric_frame_configuration.py:85-95
  - src/melder/aether/aetheric_frame/aetheric_frame_configuration.py:380-558
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py:929-972
  IMPACT: The first implementation cut should replace this with one clearer root-arbitration policy surface.
  NEXT: pair that replacement model with the eager identity-refresh seam so the next prompt can patch both together.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-30T10:28:39Z
  TYPE: FACT
  CLAIM: `DevopsIdentity.update_metadata(...)` currently forces same-thread
    registry maintenance work. It updates local metadata and then immediately
    calls `DevopsInformationRegistry.refresh_identity(...)`, which takes the
    registry lock and rebuilds metadata-derived spellbook/conduit relations.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/devops_identity.py:272-290
  - src/melder/aether/aetheric_frame/dev_ops/devops_information_registry.py:384-426
  - src/melder/aether/conduit/conduit.py:896-896
  - src/melder/aether/conduit/conduit.py:1549-1549
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:376-376
  - src/melder/aether/conduit/conduit_ward/conduit_ward.py:992-992
  IMPACT: Hot runtime identity updates are coupled to eager registry maintenance today, which is exactly the path we want to remove.
  NEXT: define the replacement mediator-owned registry update point so the next prompt can remove this eager refresh safely.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-30T10:48:19Z
  TYPE: DECISION
  CLAIM: The user rejected my earlier "parallel vs queue" replacement because
    it is still too frame-global. The corrected direction is: root-session
    strategies should own blast-radius policy and risk-tolerance behavior for
    their own transaction families, rather than one mediator-level config
    deciding broad blocking semantics for all work in the frame.
  EVIDENCE:
  - user_instruction
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py:929-972
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/transaction_strategy.py:18-57
  IMPACT: The next plan must stop treating root arbitration as one global
    runtime posture knob. The design target is now a thinner mediator with
    strategy-owned blast-radius / risk-tolerance policy, plus the separate lazy
    registry-update move.
  NEXT: explain the corrected model back to the user and then redefine the
    upcoming implementation slice around strategy-owned policy instead of a new
    global queue/parallel config.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-30T10:52:19Z
  TYPE: FACT
  CLAIM: The current devops configuration surface in
    `AethericFrameConfiguration` is 11 items:
    `change_control_mode`,
    `allow_multiple_root_transactions`,
    `disable_all_transactions_after_conjure`,
    `disable_mutations`,
    `disable_linking`,
    `disable_bind`,
    `disable_conduit_cluster`,
    `disable_transfer_of_ownership`,
    `disable_contract_mutation`,
    `queue_competing_root_transactions`,
    and `max_transaction_wait_time_in_seconds`.
    The eager hot-path issue is localized too: `DevopsIdentity.update_metadata(...)`
    immediately calls `self._registry.refresh_identity(self)`, which rebuilds
    spellbook/conduit relations under the registry lock.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/aetheric_frame_configuration.py:85-95
  - src/melder/aether/aetheric_frame/aetheric_frame_configuration.py:672-795
  - src/melder/aether/aetheric_frame/dev_ops/devops_identity.py:272-290
  - src/melder/aether/aetheric_frame/dev_ops/devops_information_registry.py:384-426
  IMPACT: The immediate code cut can stay very small: define the config surface
    clearly for the user and make `update_metadata(...)` local-only so hot-path
    identity updates stop triggering registry-maintenance work.
  NEXT: patch `devops_identity.py` so `update_metadata(...)` no longer refreshes
    the registry implicitly, then run the direct devops identity/registry unit
    ring.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-30T10:53:07Z
  TYPE: MEASURE
  CLAIM: The runtime hot-path cut is correct, and the only failing validation
    is a stale unit expectation. `py_compile` passed for `devops_identity.py`.
    The direct identity/registry ring then failed in exactly one place:
    `test_devops_identity_update_metadata_merges_and_refreshes_registry`,
    which still asserts the old eager-refresh behavior. Everything else in the
    ring passed.
  EVIDENCE:
  - validation_result: `<local-workspace>\.venv_new\Scripts\python.exe -m py_compile src\melder\aether\aetheric_frame\dev_ops\devops_identity.py`
  - validation_result: `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\aether\dev_ops\test_devops_identity.py tests\unit\melder\aether\dev_ops\test_devops_information_registry.py` -> `1 failed, 47 passed`
  - tests/unit/melder/aether/dev_ops/test_devops_identity.py:318-334
  IMPACT: The code change did what we wanted. The next edit is test alignment
    only, not another runtime adjustment.
  NEXT: patch the one stale identity test to assert local metadata merge
    without implicit registry refresh, then rerun the same ring.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-30T10:53:56Z
  TYPE: MEASURE
  CLAIM: The eager identity-refresh removal is now landed and the narrow
    validation ring is green. `DevopsIdentity.update_metadata(...)` now only
    merges local metadata, while explicit registry refresh still exists through
    `refresh_registry(...)`. The directly implicated identity/registry unit
    files now pass cleanly after aligning one stale test to the new contract.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/devops_identity.py:272-290
  - tests/unit/melder/aether/dev_ops/test_devops_identity.py:315-334
  - validation_result: `<local-workspace>\.venv_new\Scripts\python.exe -m py_compile src\melder\aether\aetheric_frame\dev_ops\devops_identity.py tests\unit\melder\aether\dev_ops\test_devops_identity.py`
  - validation_result: `<local-workspace>\.venv_new\Scripts\python.exe -m pytest -q tests\unit\melder\aether\dev_ops\test_devops_identity.py tests\unit\melder\aether\dev_ops\test_devops_information_registry.py` -> `48 passed, 1 warning`
  IMPACT: The hot-path reporting issue is reduced without yet touching mediator
    policy or the larger config cleanup.
  NEXT: define the replacement devops configuration surface and the mediator-owned
    registry update seam for the next implementation slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-30T10:58:07Z
  TYPE: DECISION
  CLAIM: The user narrowed the mediator-policy direction again. The disable
    flags and timeout remain acceptable. `warn` should be removed. Parallel
    root work should be the normal posture, and queueing should not be a blunt
    frame-global serialization rule. The real concurrency decision should come
    from transaction scope/conflict/embargo analysis, not from treating all
    root transactions as equally blocking.
  EVIDENCE:
  - user_instruction
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py:929-972
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/conflict_manager/conflict_manager.py:46-82
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/embargo_manager/embargo_manager.py:89-170
  IMPACT: The next design answer should stop framing queueing as the primary
    root-arbitration model and instead explain where conflict/embargo should
    own concurrency decisions and where a queue still makes sense as a
    backpressure tool.
  NEXT: answer the current queue/embargo design question directly from the
    current code and then define the next bounded implementation slice.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-30T20:09:30Z
  TYPE: DECISION
  CLAIM: The design boundary is now clearer: information strategies should sit
    beside `DevopsInformationRegistry` and own the first two steps of
    transaction ingress (hydrating/applying mirrored-reality updates and
    producing the current state view needed for planning). That still leaves a
    missing top-down owner for cross-component state transitions, because the
    current system is mostly bottom-up events plus narrow managers. The likely
    direction is to promote the existing change-control orchestration layer into
    a fuller top-down state-transition coordinator while keeping
    `TransactionMediator` as the front-door/session facade.
  EVIDENCE:
  - user_instruction
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/orchestrator/orchestrator.py:339-401
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py:328-431
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/embargo_manager/embargo_manager.py:376-406
  IMPACT: The next architecture slice should stop treating mediator, embargo,
    and conflict as the whole answer. We need one top-down transition owner over
    pending -> admitted -> active -> released, with information strategies
    feeding it current mirrored truth.
  NEXT: explain that top-down + bottom-up split plainly and map the concrete
    state machine and data structures needed for pending ordering, wakeup, and
    timeout behavior.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task exists only to make the next implementation prompt clean. The work
is to define the replacement root-policy model and the mediator-owned lazy
registry update seam, not to patch runtime code yet.
