# Task: Investigate conduit, spellspace, and spellbook guard and lock bloat
- Completed: 2026-05-30T15:06:13Z
- Summary: Closed by explicit user instruction during the 2026-05-30 compiler-strategy lane reset. This ticket is superseded as an active route by the new execution-strategy compiler direction.


## Metadata
- Task ID: TASK-2026-05-26-investigate-conduit-spellspace-spellbook-guard-and-lock-bloat
- Story: none
- Status: done
- Owner: codex
- Agent Name: guard_check_0
- Priority: p0
- Created: 2026-05-26T22:21:03Z
- Updated: 2026-05-30T15:06:13Z

## Objective
Read `Conduit`, `SpellSpace`, and `Spellbook` in the current source, then map
where lesser conduits are burdened by reporting/control-plane work and where
guard usage or locking looks broader than the runtime contract justifies.

## Ticket Contract
- ENTRY_GATE: the user explicitly requested a source-first investigation of
  `conduit.py`, `spell_space.py`, and `spellbook.py` before any cleanup cuts.
- EXECUTION_BOUNDARY:
  - `src/melder/aether/conduit/conduit.py`
  - `src/melder/aether/conduit/spell_space/spell_space.py`
  - `src/melder/aether/spellbook/spellbook.py`
  - directly required nearby symbols only if one of the three files points at
    them and the claim cannot be resolved locally
  - `codex/context_compass/tickets/tasks/2026-05-26_investigate_conduit_spellspace_spellbook_guard_and_lock_bloat_task.md`
  - `codex/context_compass/attention_board.md`
- DEPENDENCIES:
  - `tickets/tasks/2026-05-23_investigate_spellbook_conduit_devops_dependency_cleanup_task.md`
  - `tickets/tasks/2026-05-23_investigate_single_meld_lock_and_check_cleaned_paths_task.md`
  - `tickets/tasks/2026-05-24_prepare_spellspace_for_pooling_task.md`
- EXIT_GATE: the three-file investigation produces one evidence-backed map of
  lesser-conduit burden, guard surfaces, and lock layering, plus one bounded
  next cleanup target.
- FAILURE_ESCALATION: raise `DECISION_REQUEST` if the investigation cannot stay
  within the three-file boundary without widening into broader dev-ops or meld
  runtime internals.

## Scope Boundaries
- In scope:
  - lesser-conduit responsibilities carried by `Conduit`
  - `SpellSpace` interaction with conduit state and scope bookkeeping
  - `Spellbook` participation in conduit creation/reporting/control-plane work
  - `check_cleaned`, guard, and lock surfaces visible in the three target files
- Out of scope:
  - editing runtime code before the investigation result is reviewed
  - benchmark runs
  - full dev-ops cleanup beyond what the three files reveal directly

## State Transition Event
- from_state: draft
- to_state: in_progress
- transition_reason: the user explicitly requested a bounded investigation of
  guard, lock, and lesser-conduit burden in the three named files.

## Steps / Checklist
- [ ] Read `conduit.py` in bounded chunks and map lesser-conduit state,
      reporting/control-plane coupling, guard surfaces, and lock sites.
- [ ] Read `spell_space.py` in bounded chunks and map scope ownership plus
      lock/guard behavior.
- [ ] Read `spellbook.py` in bounded chunks and map how conjure/root setup
      burdens conduits or lesser-conduit paths.
- [ ] Separate legitimate runtime ownership from probable garbage/overreach.
- [ ] Summarize the highest-value bounded cleanup cut before any edits.
- [ ] Run Ticket Microcycle during execution:
      `Investigate -> Document -> Strategy/Plan -> Document -> Implement ->
      Document -> Validate -> Document`.
- [ ] Document each meaningful finding immediately in `## Notes` before further
      investigation.

## Deliverables
- one evidence-backed map of burden/guard/lock surfaces in the three files
- one bounded recommendation for the first cleanup cut

## Files / Paths Impacted
- `codex/context_compass/tickets/tasks/2026-05-26_investigate_conduit_spellspace_spellbook_guard_and_lock_bloat_task.md`
- `codex/context_compass/attention_board.md`

## Validation
- Not run.
- Recommended commands:
  - `rg -n "check_cleaned|_lock|RLock|Lock|guard|lesser|spellspace" src/melder/aether/conduit/conduit.py src/melder/aether/conduit/spell_space/spell_space.py src/melder/aether/spellbook/spellbook.py`

## Risks / Rollback Notes
- Risk: some seemingly excessive guards/locks may be covering real dynamic-mode
  or cleanup-order invariants that are only obvious after reading nearby helper
  calls. The investigation has to distinguish burden from required ownership.

## Applicable Anti-Patterns
- [ ] No status transition without evidence-backed transition reason.
- [ ] No implementation/validation from `UNKNOWN` or `HYPOTHESIS`.
- [ ] No cleanup edits before the burden/guard/lock map is explicit.

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
- Note focus: lesser-conduit burden, guard/lock breadth, and one-step
  continuation.
- Add a `## Notes` entry after each meaningful finding before continuing.
- Keep notes append-only; correct history only for factual errors.
- Promote `UNKNOWN` to `FACT` only with direct evidence pointers.

## Notes
- DATETIME: 2026-05-26T22:21:03Z
  TYPE: PLAN
  CLAIM: The user wants a source-first investigation of three concrete files
    before any cleanup proposal: `Conduit`, `SpellSpace`, and `Spellbook`.
    The target is not generic performance theory; it is the concrete runtime
    burden on lesser conduits plus any garbage guard or lock surfaces that are
    wider than the visible contract justifies.
  EVIDENCE:
  - user_instruction
  IMPACT: The next step is to read the three files directly, record the first
    evidence-backed burden/guard/lock finding, and keep the scope bounded.
  NEXT: read `conduit.py` first because it is the obvious owner of lesser
    conduit state and the most likely place where reporting and lock layering
    accumulate.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-26T22:21:03Z
  TYPE: FACT
  CLAIM: `Conduit` currently makes lesser conduits carry much more than a
    narrow child-runtime surface. The shared constructor always creates and
    attaches dev-ops identity, spellspace state, creations, a spellspace pool,
    meld, and Nexus-facing publication state before the lesser/normal split is
    meaningfully narrowed. On the reuse/cleanup side, pooled lesser conduits
    still run spellspace cleanup, dev-ops identity refresh, and Nexus publish
    updates, and freshly created lesser conduits are immediately opened,
    linked, identity-refreshed, and Nexus-published.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:141-338
  - src/melder/aether/conduit/conduit.py:339-548
  - src/melder/aether/conduit/conduit.py:742-1099
  - src/melder/aether/conduit/conduit.py:1389-1767
  IMPACT: The first likely cleanup seam is structural: separate lesser-conduit
    runtime obligations from normal-conduit obligations earlier, instead of
    constructing nearly the full normal surface and then mutating it down with
    state switches and cleanup branches.
  NEXT: read the `Spellbook` conjure/root setup and `SpellSpace` ownership
    surfaces to confirm which of these burdens are imposed externally versus
    self-inflicted inside `Conduit`.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-26T22:21:03Z
  TYPE: FACT
  CLAIM: `SpellSpace` is comparatively narrow, while `Spellbook` mostly acts as
    a delegator and frame-level coordinator rather than the direct source of
    lesser-conduit bloat. `SpellSpace` owns one lock for cleanup/reset
    idempotence, validates only active-scope usage before delegating to `Meld`,
    and otherwise just clears spellspace instances and unregisters from the
    registry/pool. `Spellbook` does carry frame-level dev-ops identity and
    RiskManager registration helpers, but its public `conjure(...)` path
    largely hands root-conduit construction off to `SpellbookCreationSystem`,
    and its `create_new_preset_spellbook()` upgrade hook is a thin wrapper.
  EVIDENCE:
  - src/melder/aether/conduit/spell_space/spell_space.py:1-188
  - src/melder/aether/spellbook/spellbook.py:151-267
  - src/melder/aether/spellbook/spellbook.py:2887-3367
  - src/melder/aether/spellbook/spellbook.py:3101-3230
  - src/melder/aether/spellbook/spellbook.py:3543-3699
  IMPACT: The first cleanup cut should not start by trimming `SpellSpace`.
    The heaviest lesser-conduit burden still appears to be self-owned inside
    `Conduit`, with `Spellbook` contributing mainly root-frame identity/risk
    coordination rather than deep child-conduit baggage.
  NEXT: read the directly required root-conduit builder path
    (`SpellbookCreationSystem`) only far enough to confirm what extra
    reporting/control-plane work it injects into `Conduit` construction.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-26T22:21:03Z
  TYPE: FACT
  CLAIM: The root-conduit construction path confirms that the main burden is
    injected once and then amplified by `Conduit`, not duplicated by
    `Spellbook`. `SpellbookCreationSystem` freezes/binds config, builds a new
    conduit id, resolves the frame-owned `CreationGateController` through
    `DevOpsManager`, resolves the live frame, and then calls the concrete
    `Conduit(...)` constructor with that frame-owned control-plane surface.
    After that point, the heavier child-runtime shape comes from
    `Conduit` itself, because the same constructor path is reused for lesser
    conduits and then mutated by state flags and post-construction rewiring.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook.py:2943-3068
  - src/melder/aether/spellbook/spellbook.py:3573-3583
  - src/melder/aether/spellbook/spellbook_creation_system.py:49-75
  - src/melder/aether/spellbook/spellbook_creation_system.py:152-213
  - src/melder/aether/spellbook/spellbook_creation_system.py:319-389
  - src/melder/aether/conduit/conduit.py:141-338
  - src/melder/aether/conduit/conduit.py:1620-1755
  IMPACT: The first cleanup cut should target `Conduit` construction/state
    splitting, not `Spellbook` ceremony. `Spellbook` is mostly passing in
    frame-owned services; `Conduit` is where lesser conduits are turned into
    near-full runtime objects and then trimmed with conditional behavior.
  NEXT: summarize the evidence-backed cleanup target to the user: split lesser
    conduit construction/ownership from normal conduit construction before
    trimming individual locks or guards.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-26T22:28:25Z
  TYPE: ALIGNMENT_CHECK
  CLAIM: The intended target contract for lesser conduits is not fully proven
    by the three-file read alone. What is evidenced is the current code shape
    and the local docstring-level contract that lesser conduits inherit parent
    Spellbook/configuration/frame services, cannot establish external links or
    register new spells, and own a conduit-local creation gate. Whether that
    contract is itself wrong, incomplete, or transitional still needs user or
    broader design confirmation.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:1624-1629
  - src/melder/aether/conduit/spell_space/spell_space.py:23-42
  - user_feedback
  IMPACT: I should not present "bloated" as a fact about intended design. The
    defensible claim is narrower: current code makes lesser conduits responsible
    for more subsystems than their local stated contract obviously requires.
  NEXT: state that distinction plainly to the user and ask for the intended
    lesser-conduit contract if they want the cleanup recommendation anchored to
    target architecture rather than current-code shape.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-26T22:28:25Z
  TYPE: FACT
  CLAIM: The direct dev-ops read strengthens the earlier conclusion but narrows
    it more precisely. The frame-level dev-ops layer is intentionally broad:
    `DevOpsManager` owns risk, change-control, incidents, and the
    `CreationGateController`; `SpellSystemStates` owns both frame-wide lineage
    state and per-conduit resolution state; `DevopsInformationRegistry` owns a
    large topology/transaction mirror and derives spellbook<->conduit relations
    from identity metadata; `DevopsIdentity` is not a passive label, it is an
    active adapter that can refresh registry state and publish conduit/cluster
    relations. That means when `Conduit` eagerly creates identity objects,
    attaches them to the registry, refreshes metadata, rebinds lineage gates,
    and republishes during pooling/upgrade/create-lower flows, it is dragging a
    real frame-control-plane subsystem through the lesser-conduit lifecycle,
    not just carrying a lightweight tag.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/dev_ops_manager.py:1-409
  - src/melder/aether/aetheric_frame/dev_ops/devops_identity.py:1-474
  - src/melder/aether/aetheric_frame/dev_ops/devops_information_registry.py:1-1106
  - src/melder/aether/aetheric_frame/dev_ops/risk_manager/risk_manager.py:1-482
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:1-1314
  - src/melder/aether\aetheric_frame\dev_ops\spell_system_states\conduit_resolution_state.py:1-696
  - src/melder/aether/conduit/conduit.py:243-323
  - src/melder/aether/conduit/conduit.py:359-375
  - src/melder/aether/conduit/conduit.py:866-897
  - src/melder/aether/conduit/conduit.py:1390-1434
  - src/melder/aether/conduit/conduit.py:1487-1566
  - src/melder/aether/conduit/conduit.py:1624-1755
  IMPACT: The defensible claim is now stronger: even without knowing the final
    intended lesser-conduit contract, current lesser-conduit lifecycle code is
    coupled to a heavy frame-control-plane surface. The first cleanup cut still
    points at separating lesser-conduit runtime shape from this dev-ops-rich
    normal-conduit path before trimming individual locks.
  NEXT: answer the user with the direct-devops-read correction and keep the
    recommendation grounded in current-code coupling rather than guessed target
    design.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-26T22:28:25Z
  TYPE: FACT
  CLAIM: The deeper internal read shows the dev-ops side is not thin scaffolding.
    The lower layers behind `DevOpsManager` include a real admission/orchestration
    system (`ChangeControlManager`, conflict manager, embargo manager,
    orchestrator, transaction manager, transaction mediator, transaction session,
    and transaction strategies), plus a broad topology/transaction mirror in
    `DevopsInformationRegistry` and conduit-local validation gating in
    `RiskManager` and `ConduitResolutionState`. Because `Conduit` eagerly wires
    identity, gate-controller lineage rebinding, risk-linked resolution state,
    and registry refresh/publication into lesser-conduit create/pool/upgrade
    flows, those child flows are coupled to a genuinely heavy control-plane seam,
    not a trivial metadata surface.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/change_control_manager.py:1-1453
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/orchestrator/orchestrator.py:1-504
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_manager.py:1-472
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py:1-1131
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_session.py:1-428
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/bind_transaction_strategy.py:1-322
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/link_transaction_strategy.py:1-188
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/cluster_link_transaction_strategy.py:1-209
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/transaction_strategy_builder.py:1-289
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/transfer_ownership_transaction_strategy.py:1-557
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/conflict_manager/conflict_manager.py:1-108
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/embargo_manager/embargo_manager.py:1-410
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_request/transaction_request.py:1-128
  - src/melder/aether/aetheric_frame/dev_ops/incident_manager/incident_manager.py:1-194
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_states.py:1-1314
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/spell_system_state.py:1-518
  - src/melder/aether/aetheric_frame/dev_ops/spell_system_states/conduit_resolution_state.py:1-696
  - src/melder/aether/aetheric_frame/dev_ops/risk_manager/risk_manager.py:1-482
  - src/melder/aether/conduit/conduit.py:243-323
  - src/melder/aether/conduit/conduit.py:359-375
  - src/melder/aether/conduit/conduit.py:1390-1434
  - src/melder/aether/conduit/conduit.py:1487-1566
  - src/melder/aether/conduit/conduit.py:1624-1755
  IMPACT: The cleanup target is now sharper: if lesser conduits are supposed
    to stay lightweight, they should not be forced through so much transaction,
    registry, and risk-linked control-plane participation on construction,
    reuse, and promotion.
  NEXT: summarize the internal-read result back to the user and separate
    “heavy because current control plane is real” from “wrong because intended
    lesser-conduit contract may be narrower.”
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-26T22:28:25Z
  TYPE: DECISION
  CLAIM: The user explicitly widened the investigation to Nexus, specifically
    the reporting/publication path for lesser conduits. That is a real scope
    expansion beyond the original three-file boundary, but it is now the
    correct next step because the current hypothesis is about whether lesser
    conduit reporting to Nexus is hot-path garbage worth stripping.
  EVIDENCE:
  - user_instruction
  - src/melder/aether/conduit/conduit.py:359-375
  - src/melder/aether/conduit/conduit.py:481-530
  - src/melder/aether/conduit/conduit.py:1624-1755
  IMPACT: The next read set must include the Nexus-side conduit publication and
    descriptor ownership surfaces before making any recommendation about
    stripping reporting/publication work from lesser conduits.
  NEXT: read `nexus.py`, `frame_descriptor_manager.py`, and the conduit-record
    publication helpers those conduit methods delegate into.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

- DATETIME: 2026-05-26T22:28:25Z
  TYPE: FACT
  CLAIM: The Nexus reporting path is active on lesser-conduit lifecycle
    transitions, and the descriptor side does real work. `Conduit` calls Nexus
    publish/remove helpers for `lesser` and `pooled_lesser` states; Nexus
    delegates to `FrameDescriptorManager`, which accepts those states, walks
    peer links, resolves parent conduit id, computes lineage depth, builds a
    `ConduitDescriptorPayload`, wraps it in a `ConduitRecord`, upserts it into
    the frame descriptor, and then ensures the frame ACL container on both
    publish and remove. So the lesser-conduit hot path is not just paying one
    function call; it is paying passive-ingest descriptor upkeep plus ACL-side
    container maintenance.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:625-704
  - src/melder/aether/conduit/conduit.py:359-375
  - src/melder/aether/conduit/conduit.py:481-530
  - src/melder/aether/conduit/conduit.py:1624-1755
  - src/melder/nexus/nexus.py:980-1026
  - src/melder/nexus/frame_descriptor_manager.py:309-461
  - src/melder/nexus/frame_descriptor/conduit_record.py:1-121
  - src/melder/nexus/frame_descriptor/conduit_descriptor_payload.py:1-110
  - src/melder/nexus/frame_descriptor/frame_descriptor.py:201-250
  IMPACT: If the goal is to trim hot-path garbage from lesser conduits, Nexus
    publication/removal is a concrete removal or deferment candidate, because
    the published payload is descriptor metadata rather than execution-critical
    runtime state.
  NEXT: explain the exact lesser-conduit -> Nexus payload and upkeep path to
    the user so we can decide whether to remove it entirely or just move it off
    the immediate create/pool/cleanup path.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-26T22:28:25Z
  TYPE: PLAN
  CLAIM: The first bounded implementation cut is now explicit. We are not
    removing lesser-conduit creation publication itself. We are removing only
    the pool-transition churn:
    1. no Nexus publish on return-to-pool
    2. no dev-ops identity refresh on return-to-pool
    3. no Nexus publish when reactivating a pooled lesser
    4. no dev-ops identity refresh when reactivating a pooled lesser
    5. preserve object state transitions so pooled shells still become
       `pooled_lesser` when idle and `lesser` when active again
  EVIDENCE:
  - user_instruction
  - src/melder/aether/conduit/conduit.py:359-375
  - src/melder/aether/conduit/conduit.py:1678-1755
  - src/melder/nexus/frame_descriptor_manager.py:309-380
  IMPACT: The edit can stay local to `Conduit` plus focused tests. No Nexus or
    dev-ops internals need to change for this first cut.
  NEXT: patch `conduit.py` and the directly implicated lifecycle/passive-ingest
    tests.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-26T23:13:39Z
  TYPE: MEASURE
  CLAIM: `Conduit.create_lesser_conduit()` is now structurally split into one
    fresh-create branch and one pooled-reactivation branch, with one shared
    hook/link tail. Hook behavior is preserved, fresh lessers still publish to
    Nexus, and pooled lessers still reactivate into `lesser` state without
    Nexus publish or dev-ops identity refresh churn.
  EVIDENCE:
  - src/melder/aether/conduit/conduit.py:1625-1757
  - tests/unit/melder/aether/conduit/test_conduit_lifecycle.py:614-676
  - validation_result: .\\.venv_new\\Scripts\\python.exe -m pytest -q tests\\unit\\melder\\aether\\conduit\\test_conduit_lifecycle.py
  IMPACT: The method now has concrete lifecycle branches instead of duplicated
    hook/no-hook branches, so the next cleanup discussion can target redundant
    field assignments directly instead of fighting the old structure first.
  NEXT: review the restructured method, then decide which of the remaining
    branch-local assignments should be removed next.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-26T23:13:39Z
  TYPE: FACT
  CLAIM: Making `nexus_publish_enabled` a required `Conduit.__init__` input is
    a real cross-cutting constructor refactor, not a one-line cleanup. There
    are two production creation surfaces to change: root conduit creation in
    `SpellbookCreationSystem._build_conduit(...)` and fresh lesser creation in
    `Conduit.create_lesser_conduit(...)`. The bigger semantic change is on the
    spellbook side: `_publish_nexus_state_for_conjure(...)` currently computes
    publishability and then mutates the already-constructed root conduit's
    `_nexus_publish_enabled` field. If the field becomes init-only, the
    publishability decision must move earlier in the conjure flow and the
    helper/tests that currently assert post-construction mutation must be
    rewritten. Test impact is also broad because direct `Conduit(...)`
    construction is used in multiple unit fixtures and files.
  EVIDENCE:
  - src/melder/aether/spellbook/spellbook_creation_system.py:347-359
  - src/melder/aether/conduit/conduit.py:1693-1706
  - src/melder/aether/conduit/conduit.py:1735-1748
  - src/melder/aether/spellbook/spellbook.py:3387-3425
  - tests/unit/melder/spellbook/test_spellbook.py:2069-2088
  - tests/unit/melder/aether/conduit/conftest.py:297-425
  - tests/unit/melder/aether/conduit/test_conduit_contracts.py:77-77
  - tests/unit/melder/aether/conduit/test_conduit_configuration_and_hooks.py:117-117
  - tests/unit/melder/aether/conduit/test_conduit_lifecycle.py:92-92
  - tests/unit/melder/aether/conduit/test_conduit_lifecycle.py:649-649
  - tests/unit/melder/aether/conduit/test_conduit_transactions.py:61-61
  IMPACT: If we do this, the right implementation is to make Nexus
    publishability an explicit conjure-time decision and constructor input, not
    a later side-effect. The refactor is manageable, but it is not just adding
    one required parameter.
  NEXT: explain the exact required production and test changes before touching
    the constructor contract.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10
- DATETIME: 2026-05-27T01:05:23Z
  TYPE: MEASURE
  CLAIM: The pool layer is now simplified without changing the direct caller
    contract. `ConduitPool.return_lesser_conduit(...)` no longer scans for
    duplicate idle entries and now uses a shared private-pool release helper.
    `SpellSpacePool.release(...)` now uses the same private-pool release path,
    and the base class now exposes a one-step decay helper for those private
    pool callers instead of forcing them through the full public release path.
  EVIDENCE:
  - src/melder/utilities/general_base/abstract_elastic_pool.py:141-370
  - src/melder/aether/conduit/conduit_pool.py:82-134
  - src/melder/aether/conduit/spell_space/spell_space_pool.py:14-97
  - validation_result: .\\.venv_new\\Scripts\\python.exe -m pytest -q tests\\unit\\melder\\utilities\\data_structures\\test_abstract_elastic_pool.py tests\\unit\\melder\\aether\\conduit\\test_conduit_pool.py tests\\unit\\melder\\aether\\conduit\\spell_space\\test_spell_space_pool.py tests\\unit\\melder\\aether\\conduit\\spell_space\\test_spell_space.py
  IMPACT: Both pools now share the same lighter private release behavior, and
    the obvious linear duplicate scan is gone from the conduit pool return path.
  NEXT: review whether the remaining generic elastic policy (`stretch`,
    `settle`, multi-step decay) should stay in the base or be simplified
    further for these private runtime pools.
  REREAD: REQUIRED
  SCORE_0_TO_10: 10

## Context / Handoff Summary
Investigation lane opened for `conduit.py`, `spell_space.py`, and
`spellbook.py` only. No runtime edits yet. Next action is a bounded read of
`conduit.py` followed by evidence-backed notes before expanding further.
