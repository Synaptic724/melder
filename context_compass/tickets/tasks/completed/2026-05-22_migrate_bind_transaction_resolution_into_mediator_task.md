# Task: Migrate Bind Transaction Resolution Into Mediator

## Metadata
- Task ID: TASK-2026-05-22-migrate-bind-transaction-resolution-into-mediator
- Story: STORY-2026-05-22-define-spellindex-transfer-and-registration-semantics
- Status: done
- Owner: codex
- Agent Name: mutres_0
- Priority: p0
- Created: 2026-05-22T20:22:30Z
- Updated: 2026-06-01T11:37:34Z

## Objective
Move `bind` transaction resolution into change-control land so the mediator
owns bind transaction start/end resolution, while `Spellbook` becomes a thin
bind submitter plus local bind-state owner.

## Ticket Contract
- ENTRY_GATE: the full pytest suite is green, the user explicitly approved a
  bind-only cut, and the current `Spellbook` transaction seam is known to be
  too heavy.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/**`
  - `src/melder/aether/spellbook/spellbook.py`
  - `src/melder/aether/spellbook/spellbook_creation_system.py`
  - directly implicated bind tests only
- DEPENDENCIES:
  - `tickets/tasks/2026-05-22_wire_transaction_identity_and_mediator_into_spellbook_and_conduit_task.md`
  - `tickets/tasks/2026-05-22_stabilize_full_pytest_suite_after_transaction_wiring_task.md`
  - `tickets/tasks/2026-05-22_remove_transaction_migration_compat_and_owned_introspection_task.md`
- EXIT_GATE: bind transaction start/end resolution lives in the mediator,
  `Spellbook` bind transaction code is materially thinner, and focused plus
  full-suite pytest validation are green.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the bind-only cut proves it
  cannot be isolated from link/transfer migration without architectural
  widening.

## Scope Boundaries
- In scope:
  - bind-only transaction resolution
  - mediator-side bind request resolution
  - mediator-managed bind lifecycle callbacks
  - thinning bind transaction logic in `Spellbook`
- Out of scope:
  - link transaction migration
  - transfer transaction migration
  - cluster transaction migration

## State Transition Event
- from_state: ready
- to_state: in_progress
- transition_reason: the user explicitly redirected the lane to a bind-only
  mediator-resolution cut and asked to avoid widening into other transaction
  kinds.

## Steps / Checklist
- [ ] Add a bind resolver path in the mediator / change-control land.
- [ ] Move bind transaction lifecycle callbacks out of `Spellbook` choreography.
- [ ] Thin `Spellbook` bind transaction start/end down to identity + local bind state.
- [ ] Update directly implicated tests/stubs.
- [ ] Run focused bind/mediator validation.
- [ ] Rerun the full pytest suite.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before
      further investigation.

## Deliverables
- mediator-side bind transaction resolution
- thinner `Spellbook` bind transaction seam
- updated bind-focused tests
- full-suite green validation

## Files / Paths Impacted
- `codex/context_compass/tickets/tasks/2026-05-22_migrate_bind_transaction_resolution_into_mediator_task.md`
- `codex/context_compass/attention_board.md`
- `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/**`
- `src/melder/aether/spellbook/spellbook.py`
- `src/melder/aether/spellbook/spellbook_creation_system.py`
- directly implicated bind tests only

## Validation
- Not run.
- Recommended commands:
  - `./.venv_new/Scripts/python.exe -m pytest -q tests/unit/melder/aether/dev_ops/change_control_manager/test_transaction_mediator.py tests/unit/melder/spellbook/test_spellbook.py tests/integration/melder/spellbook/test_spellbook_integration_core.py`
  - `./.venv_new/Scripts/python.exe -m pytest -q`

## Risks / Rollback Notes
- Risk: bind-local pending-state cleanup and change-control commit hooks may
  currently overlap.
  Rollback: keep structural/dirty consequences in change-control land and use
  bind callbacks only for local pending-state initialization/cleanup.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No widening bind cleanup into link/transfer logic in the same pass.

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
- DISPOSITION: delete_on_close
- CLEANUP_TRIGGER: ticket closure

## Noting Behavior
- Note focus: bind-specific transaction-resolution facts, impacts, and one-step continuation.
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
- DATETIME: 2026-05-22T20:22:30Z
  TYPE: PLAN
  CLAIM: The next correct cut is bind-only. The current `Spellbook`
    transaction seam is too heavy, but we do not need to solve link or
    transfer now. The mediator already has enough live-session plumbing to own
    bind resolution if we add a bind resolver path and bind lifecycle callback
    registration on the change-control side.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py:343-490
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py:678-771
  - src/melder/aether/spellbook/spellbook.py:2403-2715
  - src/melder/aether/spellbook/spellbook_creation_system.py:424-426
  IMPACT: We can reduce the bind seam without committing to the wider
    transaction migration yet, and we can keep the change-control default
    structural validator/dirty marker as the real post-bind consequence layer.
  NEXT: implement a mediator bind resolver plus bind lifecycle callback
    registration and thin the Spellbook bind path around that.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-22T21:41:53Z
  TYPE: FACT
  CLAIM: The current bind seam is already partly mediator-owned, but the
    `Spellbook` surface is still mixed. Bind start already routes through
    `TransactionMediator.start_transaction(...)`, while staged bind-key updates
    still go straight to `ChangeControlManager.update_staged_request(...)`, and
    `begin_transaction(...)` still carries unreachable bind-era local code
    (`_begin_binding_transaction(...)`) after the early bind return.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:2257-2475
  - src/melder/aether/spellbook/spellbook.py:2711-2758
  - src/melder/aether/spellbook/spellbook.py:3035-3035
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py:556-583
  IMPACT: The next narrow cleanup is to make the bind path talk only to the
    mediator boundary and strip the dead bind-era local scaffolding, without
    widening into strategy behavior yet.
  NEXT: add one mediator-side staged-update helper for identity-scoped active
    bind sessions, switch `_try_update_staged_binding_keys(...)` over to it,
    and delete the unreachable bind-era local transaction remnants in
    `Spellbook`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-22T21:41:53Z
  TYPE: FACT
  CLAIM: The bind-side `Spellbook` seam is now thinner without touching
    strategy behavior. `Spellbook` no longer reaches through to
    `ChangeControlManager.update_staged_request(...)` for bind metadata; it now
    extends active bind staging through a new mediator-owned
    `update_transaction_for_identity(...)` helper, and the unreachable
    `_begin_binding_transaction(...)` branch in generic `begin_transaction(...)`
    is removed.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py:556-609
  - src/melder/aether/spellbook/spellbook.py:2257-2392
  - src/melder/aether/spellbook/spellbook.py:2711-2754
  IMPACT: We now have the bind path set up at the mediator boundary, so the
    next conversation can focus purely on strategy resolution and embargo
    policy instead of more `Spellbook` change-request plumbing.
  NEXT: stop implementation here and align on the bind strategy contract:
    blast radius, blocked transaction kinds, same-thread recursion, and
    cross-thread queue/deny rules.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-22T23:05:36Z
  TYPE: PLAN
  CLAIM: The remaining bind-family cleanup is local to `Spellbook`. Now that
    bind strategy resolution is registry-driven, direct `Spellbook.bind()` and
    `scan()` can open the bind-family transaction themselves when no active
    bind session exists, while explicit `begin_binding_transaction()` remains
    a thin wrapper over the same mediator boundary.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/bind_transaction_strategy.py:1-115
  - src/melder/aether/spellbook/spellbook.py:2334-2582
  - src/melder/aether/spellbook/spellbook.py:2864-3049
  IMPACT: This gets the public spellbook bind/scan surface much closer to the
    intended thin shape without widening into link or transfer strategy work.
  NEXT: add bind-family start/end helpers in `Spellbook` and let direct
    `bind()` / `scan()` auto-enter that path when needed.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-22T23:05:36Z
  TYPE: FACT
  CLAIM: Bind-family strategy resolution is now registry-driven and direct
    spellbook-level `bind()` / `scan()` no longer require the caller to open a
    binding transaction window first. `BindTransactionStrategy` now resolves
    affected conduits and the live Spellbook object through the registry, and
    direct `Spellbook.bind()` / `scan()` auto-enter the same mediator-owned
    bind-family transaction path when no active bind session exists.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/bind_transaction_strategy.py:1-122
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/transaction_strategy_builder.py:1-100
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py:1122-1179
  - src/melder/aether/spellbook/spellbook.py:2334-2582
  - src/melder/aether/spellbook/spellbook.py:2819-3060
  IMPACT: The direct public bind/scan surface is much closer to the intended
    thin model, and bind/scan is now the first strategy slice that actually
    consumes the new registry instead of just storing passive topology data.
  NEXT: rerun the narrow compile-surface check, then stop for review before
    widening into more spellbook cleanup or other transaction families.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-22T23:05:36Z
  TYPE: MEASURE
  CLAIM: The direct spellbook bind/scan surface now auto-enters the
    mediator-owned bind-family transaction path when needed. The bind strategy
    is registry-driven, the registry query surface is in place, and the whole
    touched slice still passes the narrow `py_compile` sanity check.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:2334-2582
  - src/melder/aether/spellbook/spellbook.py:2819-3060
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/bind_transaction_strategy.py:1-122
  - src/melder/aether/aetheric_frame/dev_ops/devops_information_registry.py:490-892
  IMPACT: Bind/scan is now the first real registry-driven transaction family
    and the direct public spellbook surface is materially thinner than the
    earlier hybrid model.
  NEXT: stop for review unless you want the next cleanup slice to remove more
    generic bind wrappers or widen into another transaction family.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-23T10:09:55Z
  TYPE: DECISION
  CLAIM: The next bind-only cut is to simplify the bind strategy instead of
    widening automatic-mode behavior. The user accepted the bind blast radius
    of spellbook + conjured root conduit + ward + cluster memberships, but
    correctly rejected the current strategy shape as too generic and too
    computationally noisy. The builder should behave like a real strategy
    registry, and bind strategy should follow the real one-spellbook /
    one-root-conduit runtime shape rather than expanding like a generic
    multi-conduit topology planner.
  EVIDENCE:
  - user_instruction
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/bind_transaction_strategy.py:1-163
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/transaction_strategy_builder.py:1-114
  - src/melder/aether/spellbook/spellbook.py:3721-3809
  - src/melder/aether/conduit/conduit.py:230-258
  IMPACT: The implementation boundary is now: make the builder hold a real
    strategy registry, add a fast bind path that branches on pre-conjure vs
    post-conjure, and compute affected identities/scopes with sets and direct
    lookups instead of broad spellbook fanout.
  NEXT: patch the bind strategy and strategy builder only, then rerun a narrow
    compile sanity check before wider validation.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-23T10:13:57Z
  TYPE: FACT
  CLAIM: The bind strategy is now aligned to the real runtime shape instead of
    a generic topology expander. `TransactionStrategyBuilder` now behaves like
    a real strategy registry by registering strategy classes into an internal
    map at construction time. `BindTransactionStrategy` now has two explicit
    fast paths:
    - pre-conjure: spellbook-only scope and spellbook transaction-owner locks
    - post-conjure: spellbook + one paired root conduit + paired conduit ward +
      cluster memberships for that root conduit
    The post-conjure path resolves one paired conduit directly and raises if
    the registry violates the one-spellbook/one-root-conduit bind assumption.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/transaction_strategy_builder.py:35-154
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/bind_transaction_strategy.py:47-286
  - src/melder/aether/aetheric_frame/dev_ops/devops_information_registry.py:510-541
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_manager.py:261-284
  IMPACT: Bind-family planning is now much cheaper and much more obvious to
    read, and the builder is finally a real registry of strategies instead of
    an `if bind` branch masquerading as a strategy system.
  NEXT: review the simplified bind strategy and decide whether to run focused
    pytest around the bind-family transaction path.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-23T10:13:57Z
  TYPE: MEASURE
  CLAIM: The simplified bind strategy and registry-backed builder pass a narrow
    syntax sanity check. `py_compile` succeeded for the touched strategy/helper
    files:
    `bind_transaction_strategy.py`, `transaction_strategy_builder.py`,
    `transaction_manager.py`, and `devops_information_registry.py`.
  EVIDENCE:
  - validation_result: `python -m py_compile src\\melder\\aether\\aetheric_frame\\dev_ops\\change_control_manager\\transaction_manager\\strategies\\bind_transaction_strategy.py src\\melder\\aether\\aetheric_frame\\dev_ops\\change_control_manager\\transaction_manager\\strategies\\transaction_strategy_builder.py src\\melder\\aether\\aetheric_frame\\dev_ops\\change_control_manager\\transaction_manager\\transaction_manager.py src\\melder\\aether\\aetheric_frame\\dev_ops\\devops_information_registry.py`
  IMPACT: The strategy refactor is structurally clean and ready for behavioral
    review or focused pytest.
  NEXT: summarize the landed bind-strategy boundary and choose whether to widen
    into focused tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9
- DATETIME: 2026-05-23T10:13:57Z
  TYPE: PLAN
  CLAIM: The next narrow cleanup is the builder file itself. The user
    explicitly called out `transaction_strategy_builder.py` as low-effort code:
    it still uses `Any` in places where the real transaction type and strategy
    contract are known, and its docstrings do not explain the registry role
    deeply enough for future re-entry.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/transaction_strategy_builder.py:1-154
  IMPACT: This is a contained readability/type-contract cleanup that does not
    need wider runtime edits. We can replace `Any` with the real transaction
    and strategy types, and make the file explain the registry semantics and
    builder-owned collaboration surface properly.
  NEXT: patch only `transaction_strategy_builder.py`, then rerun a narrow
    compile sanity check.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-23T10:13:57Z
  TYPE: DECISION
  CLAIM: The strategy contract should use a real abstract base, not a
    `Protocol`. This is an explicit runtime strategy family with deliberate
    registration and dispatch rules, so an `ABC` is the right abstraction
    surface for future strategy classes.
  EVIDENCE:
  - user_instruction
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/transaction_strategy_builder.py:1-286
  IMPACT: The next file-level cleanup is small and local: replace the
    `Protocol` contract with an abstract base and make `BindTransactionStrategy`
    inherit from it.
  NEXT: add the abstract base, update `BindTransactionStrategy`, update the
    builder typing/imports, then rerun the narrow compile check.
  REREAD: REQUIRED
  SCORE_0_TO_10: 9

## Context / Handoff Summary
This is the bind-only migration lane. The goal is not to finish the whole
transaction redesign here; it is to move bind resolution into the mediator so
the `Spellbook` bind seam stops owning transaction choreography.

