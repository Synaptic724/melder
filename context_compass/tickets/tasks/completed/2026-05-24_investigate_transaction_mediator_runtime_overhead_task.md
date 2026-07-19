# Task: Investigate TransactionMediator runtime overhead

## Metadata
- Task ID: TASK-2026-05-24-investigate-transaction-mediator-runtime-overhead
- Story: none
- Status: done
- Owner: codex
- Agent Name: mutres_0
- Priority: p1
- Created: 2026-05-24T15:21:52Z
- Updated: 2026-06-01T11:37:34Z

## Objective
Determine how `TransactionMediator` participates in runtime conduit creation
and transaction-changing paths, then identify which parts of that participation
are likely responsible for the slowdown the user is feeling.

## Ticket Contract
- ENTRY_GATE: the user explicitly asked for an investigation into how
  `TransactionMediator` works and whether it is slowing conduit creation and
  transaction-changing operations.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py`
  - `src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py`
  - `src/melder/aether/conduit/conduit.py`
  - `src/melder/aether/conduit/conduit_ward/conduit_ward.py`
  - `src/melder/aether/conduit/conduit_cluster.py`
  - `src/melder/aether/spellbook/spellbook.py`
  - focused measurement helpers or one narrow experiment if needed
  - `codex/context_compass/attention_board.md`
  - this task ticket
- DEPENDENCIES:
  - `tickets/tasks/2026-05-22_scaffold_transaction_mediator_and_session_task.md`
  - `tickets/tasks/2026-05-22_wire_transaction_identity_and_mediator_into_spellbook_and_conduit_task.md`
  - `tickets/tasks/2026-05-22_migrate_bind_transaction_resolution_into_mediator_task.md`
  - `tickets/tasks/2026-05-23_investigate_single_meld_lock_and_check_cleaned_paths_task.md`
- EXIT_GATE: mediator ownership, hot entrypoints, and plausible overhead
  sources are mapped with source evidence, plus at least one focused
  measurement or benchmark-backed finding where needed.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if truthful attribution requires
  a broader profiling/instrumentation cut than a bounded investigation.

## Scope Boundaries
- In scope:
  - mediator ownership and lifecycle
  - runtime callsites that enter mediator on bind/link/cluster/transfer paths
  - whether conduit creation itself talks to mediator or only adjacent
    transaction/dev-ops infrastructure
  - focused measurements where source inspection is insufficient
- Out of scope:
  - implementing mediator performance fixes before attribution is clear
  - broad repo-wide profiling
  - unrelated cleanup/test drift

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly asked for a mediator-overhead
  investigation around conduit creation and transaction-changing paths.

## Steps / Checklist
- [ ] Read mediator ownership/lifecycle and current runtime callsites.
- [ ] Separate conduit-creation overhead from actual mediator start/join/end overhead.
- [ ] Run one focused measurement if the source path alone is not enough.
- [ ] Summarize the likely overhead sources with evidence.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further
      investigation.

## Deliverables
- one evidence-backed mediator runtime path map
- one evidence-backed statement of where mediator is and is not in the hot path
- one bounded performance diagnosis for the user

## Files / Paths Impacted
- `codex/context_compass/tickets/tasks/2026-05-24_investigate_transaction_mediator_runtime_overhead_task.md`
- `codex/context_compass/attention_board.md`
- optional focused experiment or benchmark helper if needed

## Validation
- Not run.
- Possible commands:
  - `rg -n "transaction_mediator|start_transaction|end_transaction|begin_transaction|transaction\\(" src/melder/aether`
  - focused `.venv_new` pytest or experiment runs if needed

## Risks / Rollback Notes
- Risk: the slowdown may be dominated by adjacent dev-ops, registry, or scope
  churn rather than the mediator itself.
- Rollback: keep the finding honest and split “mediator cost” from “same lane,
  different subsystem cost” instead of forcing the blame onto one component.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No blaming mediator for conduit-creation costs unless the code path
      actually enters mediator there.

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
- Note focus: mediator ownership, hot callsites, and one-step continuation.
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
- DATETIME: 2026-05-24T15:21:52Z
  TYPE: PLAN
  CLAIM: The user’s concern is specific: `TransactionMediator` feels like it is
    slowing conduit creation and transaction-changing operations. The first
    thing to prove is where mediator is actually in the runtime path versus
    where adjacent dev-ops, identity, registry, or scope machinery is
    dominating the cost.
  EVIDENCE:
  - user_instruction
  IMPACT: The next step is a source-first runtime path map, not a blind
    benchmark rewrite or a speculative optimization pass.
  NEXT: read `transaction_mediator.py`, the frame owner path, and the runtime
    `begin_transaction` / conduit-creation seams, then write the first
    concrete finding.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-24T15:33:10Z
  TYPE: FACT
  CLAIM: `TransactionMediator` is not on the lesser-conduit creation hot path.
    `Conduit.create_lesser_conduit(...)` acquires the parent conduit lock,
    resolves the current root conduit, constructs a new lesser `Conduit`,
    rewires its root ids and meld resolution conduit id, optionally fires
    conduit lifecycle hooks, and links it into `ConduitWard`. There is no
    mediator lookup or transaction start in that path. The mediator only shows
    up in explicit transaction entry and contract-mutation guard paths later:
    `Conduit.begin_transaction(...)`, `Conduit.end_transaction(...)`, and
    `_require_link_transaction_for_contract(...)`; similarly on the Spellbook
    side through `begin_transaction(...)`, `end_transaction(...)`, and
    session lookups.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:1552-1653
  - src/melder/aether/conduit/conduit.py:1911-2167
  - src/melder/aether/conduit/conduit.py:3503-3538
  - src/melder/aether/spellbook/spellbook.py:2049-2302
  IMPACT: If new conduit creation feels slow, the direct culprit is more
    likely conduit construction, identity/registry attachment, creation-gate
    setup, spellspace/creations/meld wiring, or ward/linkage work, not the
    mediator itself.
  NEXT: build a focused dynamic runtime and measure explicit mediator-owned
    transaction start/end cost separately from conduit creation cost.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-24T15:43:38Z
  TYPE: MEASURE
  CLAIM: The focused microbench cleanly separates conduit creation from
    mediator-owned transaction cost on the current dynamic runtime:
    - lesser conduit create+cleanup roundtrip: about `30.6 us`
    - bind begin+end transaction roundtrip: about `65.1 us`
    - link begin+end transaction roundtrip: about `83.4 us`
    So mediator-era transaction roundtrips are roughly `2.1x` to `2.7x`
    the cost of a bare lesser-conduit create+cleanup roundtrip in this narrow
    test. The cProfile stacks show the dominant transaction path is:
    `Conduit.begin_transaction(...)` -> `Spellbook.begin_transaction(...)`
    or direct mediator start -> `TransactionMediator.start_transaction(...)` ->
    `_start_strategy_transaction(...)` -> `TransactionMediator.begin_transaction(...)`
    -> `ChangeControlManager.admit_request(...)` ->
    `ChangeControlOrchestrator.admit_request(...)`, plus strategy
    `build_start_plan(...)`, embargo open/apply, request building, and end-path
    finalization. In the link case, `cleanable.py:check_cleaned` is still a
    visible contributor (`8460` calls across `60` roundtrips, about `141` per
    roundtrip).
  EVIDENCE:
  - validation_result: focused dynamic microbench comparing lesser-conduit
    create+cleanup vs bind/link transaction roundtrips
  IMPACT: This makes the split concrete:
    - if creating new conduits feels slow, mediator is not the direct cause
    - if transaction-changing operations feel slow, mediator-era admission,
      strategy planning, embargo handling, and finalization are real cost
      centers
  NEXT: summarize the runtime split for the user and recommend the most likely
    optimization targets inside the mediator path instead of blaming conduit
    creation on mediator.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
This task owns the mediator-overhead investigation. The target is to separate
actual mediator cost from adjacent runtime churn before any optimization work
starts.

