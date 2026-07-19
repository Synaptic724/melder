# Epic: Cluster Leader-Election Transactions (elect/unelect_conduit_cluster_leader)

## Metadata
- Epic ID: EPIC-2026-06-16-cluster-leader-election-transactions
- Status: transaction machinery landed (mediator_builder_0) -- awaiting conduit_cluster.py call sites (compiler_strategy_0) + user 3.14t suite run
- Owner: cowork
- Agent Name: mediator_builder_0
- Priority: p2
- Created: 2026-06-16T22:34:39Z
- Updated: 2026-06-17T23:17:46Z
- Target Window: 2026-Q2
- Related Program/Initiative: unique_per_conduit_cluster team-store
- Depends on / seam from: 2026-06-16_unique_per_conduit_cluster_team_store_epic.md
  (compiler_strategy_0). That epic ships the no-op transaction seam this epic fills.

## Context (why this exists)
The `unique_per_conduit_cluster` team-store keeps one shared instance per cluster
in an elected leader conduit's `Creations`, fronted by a cluster-owned
`cluster_creations` facade. Member roots bind to the facade; the meld door
resolves through it. Electing a leader **binds** the facade to the leader's
store; unelecting (leader leaves / is cleaned) **unbinds** it.

Binding/unbinding the facade while melds are in flight is unsafe: a meld can read
the bound store, run `call_target()` to build an instance, and then find the
store unbound/disposed -- "spell built, nothing to bind to" (chaos / leak /
use-after-clean). `Creations.add_creation` / `get_creation` are lock-free today
(dict-atomic), so nothing serializes a create against a dispose. This is a
multi-conduit, high-footprint coordination problem (it spans every member's
lineage), which a single conduit's own cleanup cannot solve -- it is a mediator
transaction job, in the same family as the existing `cluster_link` transaction.

## What the cluster epic provides (the seam you plug into)
compiler_strategy_0 will ship, in the team-store epic, a **no-op** seam:
- Two transaction names registered with the strategy system:
  `elect_conduit_cluster_leader`, `unelect_conduit_cluster_leader`.
- The cluster call sites that open these transactions at leader bind (first
  join / elect) and unbind (leave / leader cleanup).
- The committed **effect methods** the strategy invokes:
  - `cluster_creations.bind(leader_creations)` (elect)
  - `cluster_creations.unbind()` (unelect) -- nulls the facade's store reference
    only; it never cleans the leader's `Creations` (the leader owns/cleans that).
- A **no-op strategy** for both names that simply runs the effect with no
  coordination (so the cluster system is complete + testable single-threaded).

Your job: replace the no-op strategy with the real coordinated strategy. The
effect methods and call sites do not move; only the strategy body changes.

## Goals
- Implement `elect_conduit_cluster_leader` and `unelect_conduit_cluster_leader` as
  real transaction strategies that make the facade rebind safe under concurrent
  melds, reusing the existing transaction + CreationGate machinery.
- `unelect` must guarantee no meld is mid-create against the leader store when the
  facade is unbound (and when the leader's `Creations` is subsequently disposed).
- No new hot-path locks; the safety comes from the transaction's quiesce window.

## Transaction Contracts (what compiler_strategy_0 wants)

### elect_conduit_cluster_leader(cluster, leader_conduit)
- Purpose: bind the cluster facade to `leader_conduit`'s `Creations`.
- Footprint: the cluster's member conduits (resolve via `ConduitCluster.members`).
- Coordination: LOW. Election transitions the facade from inert (empty) -> active.
  While inert, the cluster door hard-errors, so there are no in-flight cluster
  creates against a store. A light/atomic transaction is acceptable; a full
  lineage drain is not required for elect (call out if you disagree with
  evidence).
- Committed effect: `cluster_creations.bind(leader_conduit._creations)`.

### unelect_conduit_cluster_leader(cluster)
- Purpose: unbind the cluster facade (cluster goes inert; v1 dissolves, no
  transfer).
- Footprint: ALL member lineages of the cluster.
- Coordination: REQUIRED. Before running the effect, **quiesce** every member
  root's lineage so all in-flight melds fully exit. The established primitive is
  `CreationGateController.close_and_wait_until_conduit_lineage_free(root_id, ...)`
  (DevOpsManager owns the controller; revalidation already uses this exact call
  to swap a conduit's resolution safely). The meld door holds a ticket across the
  WHOLE executor (get + `call_target()` + add), so a drain to zero tickets
  guarantees no create is in progress.
- Order: close + drain all member lineages -> run effect
  (`cluster_creations.unbind()`) -> reopen the gates. After reopen, melds resume
  and hard-error (inert), which is correct.
- Idempotence: unbinding an already-empty facade is a no-op.

## Acceptance Criteria
- Under N concurrent member melds of a cluster spell plus a concurrent
  `unelect_conduit_cluster_leader`, there are zero orphaned/leaked instances and
  zero use-after-dispose: every meld either completes into the live store or
  cleanly hard-errors (inert) -- never "built with nowhere to bind." Prove with a
  looped stress test (mirror the 40x concurrent-conjure pattern).
- `elect` then concurrent member melds -> exactly one shared instance per cluster.
- No regression to existing transactions (`cluster_link`, `link`, `unlink`,
  `bind`, `transfer_ownership`).
- No new lock added to `Creations.add_creation` / `get_creation`.

## Implementation Notes (precedent to follow)
- Strategy registration: `transaction_strategy_builder.py` +
  `strategies/*_transaction_strategy.py` (see `cluster_link_transaction_strategy.py`
  for the cluster-domain precedent).
- Quiesce primitive: `CreationGateController` on the frame's `DevOpsManager`
  (`close_and_wait_until_conduit_lineage_free`, `enable_all` / per-gate `open`).
- Transaction entry: `conduit.transaction("cluster_link", conduits=[...])` is the
  existing cluster pattern; the leader transactions follow the same shape with the
  cluster's member set as the footprint.
- Reopen on every exit path (commit, rollback, error) so a failed unelect does not
  leave member lineages permanently gated.

## Open Questions (for mediator_builder_0)
- Q1: rollback semantics if a member lineage drain times out mid-unelect -- abort
  and reopen (leave leader bound), or force-unbind? Lean: abort + reopen (fail
  closed to "still bound"); raise to user.
- Q2: should elect also take a (cheaper) ticket-count check to assert quiescence,
  or trust the inert invariant? Lean: trust inert; assert in a debug check.

## Notes
- DATETIME: 2026-06-16T22:34:39Z
  TYPE: HANDOFF
  AGENT: compiler_strategy_0
  CLAIM: Authored this spec as the mediator-side half of the cluster team-store
    work split. compiler_strategy_0 ships the no-op seam (effect methods + call
    sites + no-op strategy); mediator_builder_0 implements the real coordinated
    strategies per the contracts above. Single shared seam, no overlapping file
    edits between the two epics.
  EVIDENCE:
  - src/melder/utilities/synchronization/creation_gate.py (ticket spans whole executor; close_and_wait_until_free)
  - src/melder/utilities/synchronization/creation_gate_controller.py (close_and_wait_until_conduit_lineage_free)
  - src/melder/aether/aetheric_frame/dev_ops/dev_ops_manager.py:372,472 (revalidation uses the same drain)
  - src/.../change_control_manager/transaction_manager/strategies/cluster_link_transaction_strategy.py (cluster-domain precedent)
  - src/melder/aether/conduit/creations/creations.py (add_creation/get_creation lock-free; cleanup detaches under lock)
  NEXT: mediator_builder_0 picks up after compiler_strategy_0 lands the no-op seam.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Context / Handoff Summary
This epic is the mediator-side half of the `unique_per_conduit_cluster` team-store.
The cluster epic (compiler_strategy_0) builds everything against a no-op
`elect_/unelect_conduit_cluster_leader` transaction seam. This epic
(mediator_builder_0) replaces the no-op with the real coordinated strategies:
`elect` binds the facade (low coordination; inert->active), `unelect` drains every
member lineage via the CreationGateController, then unbinds, then reopens -- so no
meld is ever mid-create against a store being unbound/disposed. Picked up after
the cluster epic lands its seam.

## Design Decision — gate facade + ownership (mediator_builder_0, 2026-06-16T23:39:51Z)
- DATETIME: 2026-06-16T23:39:51Z
  TYPE: DECISION
  CLAIM: Ownership confirmed: DevOpsManager is the single ownership ROOT for the
    operational managers (its own docstring: "one ownership root for operational
    managers that must outlive frame runtime objects"). It OWNS IncidentManager,
    ChangeControlManager, RiskManager, CreationGateController; HOLDS (frame-borrowed)
    SpellSystemStates + DevopsInformationRegistry. So the gate facade belongs owned
    by DevOpsManager, next to the controller it already owns.
    PLAN (deferred-refactor-safe; broader reach-back wiring left as-is per user --
    "works now, refactor later"):
    1) New object ConduitLineageGateOps -- a NARROW facade over CreationGateController
       exposing only what coordinated strategies need:
       - close_and_wait_conduit_lineage(root_id, timeout, interval)  [drain to zero tickets]
       - enable_conduit_lineage(root_id)                              [reopen]
       - disable_conduit_lineage(root_id)                             [close, no wait]
       - count_active_threads_for_conduit_lineage(root_id)           [quiescence assert]
    2) DevOpsManager creates + OWNS it right after CreationGateController
       (dev_ops_manager.py:115). DevOpsManager is the injector (it sees all siblings).
    3) Controller is built AFTER ChangeControlManager (dev_ops_manager.py:107 vs 115),
       so inject the facade POST-construction: DevOpsManager hands it to
       ChangeControlManager (small attach/set_gate_ops), which forwards to
       TransactionMediator -> TransactionStrategyBuilder, joining the shared
       collaborators every strategy already receives (transaction_manager + registry).
       NO drain/policy logic added to ChangeControlManager -- it only forwards the ref
       (same shape it already uses for spell_system_states / registry).
    4) Strategies USE the facade; they never touch the raw controller.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/dev_ops_manager.py:60-116 (ownership root + build order)
  - src/melder/aether/aetheric_frame/dev_ops/dev_ops_manager.py:438-476 (existing lineage drain/enable facade)
  - src/melder/utilities/synchronization/creation_gate_controller.py:557-637 (close_and_wait_until_conduit_lineage_free / get_conduit_lineage_gates / count_active_threads_for_conduit_lineage)
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/transaction_strategy_builder.py (shared-collaborator injection point)
  IMPACT: gives elect/unelect (and any future coordinated strategy) a clean narrow
    handle to conduit-lineage gate coordination, owned by the right object, without
    touching ChangeControlManager policy or the deferred reach-back refactor.
  NEXT: (blocked on compiler_strategy_0 no-op seam) implement ConduitLineageGateOps +
    DevOpsManager injection, then the elect/unelect strategy bodies that use it.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Mediator context snapshot (pre-compaction, mediator_builder_0)
- unelect strategy: footprint = cluster member root-conduit ids, carried in the
  transaction METADATA (call site passes them). on start (scopes held): for each
  member root -> facade.close_and_wait_conduit_lineage(root) [drain]; committed
  effect: cluster_creations.unbind(); on EVERY exit path (commit/abort/error):
  facade.enable_conduit_lineage(root) [reopen]. Q1: drain timeout -> abort + reopen,
  leader stays bound (fail-closed).
- elect strategy: low coordination (inert->active; cluster door hard-errors while
  inert, no in-flight creates). Light/atomic; Q2: trust inert, assert quiescence in
  a debug check only. Committed effect: cluster_creations.bind(leader._creations).
- meld ticket model: a meld holds its gate ticket across the WHOLE executor
  (get + call_target + add), so drain-to-zero guarantees no create is mid-flight.
- DEPENDENCY: compiler_strategy_0 ships the no-op seam (2 registered tx names
  elect_/unelect_conduit_cluster_leader + bind/unbind effect methods + call sites +
  no-op strategy) in 2026-06-16_unique_per_conduit_cluster_team_store_epic.md; this
  epic swaps the no-op for the real coordinated strategies.
- ALSO DONE this session (mediator backend, all green): scope-acquisition plane;
  claim modes (link/bind/cluster IX spellbooks; transfer exclusive); unlink (A/B/C);
  3 SpellIndex transactions notch/add_to_index/remove_from_index (seal = spellbook X
  + conduit X + binding X; add seals both sides) -- member-store seams handed to
  general_0 (tickets/tasks/2026-06-14_spell_index_transactions_backend_task.md).
  Mediator epic closed (tickets/epics/completed/2026-05-30_simplify_mediator_root_policy_and_lazy_devops_reporting_epic.md).

## Progress — gate facade foundation landed (mediator_builder_0, 2026-06-17T22:41:43Z)
- DATETIME: 2026-06-17T22:41:43Z
  TYPE: FACT
  CLAIM: ConduitLineageGateOps built and owned by DevOps (unblocked foundation;
    independent of the no-op seam). NEW: src/melder/aether/aetheric_frame/dev_ops/
    conduit_lineage_gate_ops.py -- narrow facade over CreationGateController
    (close_and_wait_conduit_lineage / enable_conduit_lineage /
    disable_conduit_lineage / count_active_tickets_for_conduit_lineage; by-ref,
    no lifecycle, slots + registration-guard sentinel). DevOpsManager now creates
    + owns it right after CreationGateController, dels it in cleanup, and exposes
    it via the conduit_lineage_gate_ops property. py_compile OK (sandbox);
    awaiting user venv run. Disposal note: gate cleanup already wired
    (Conduit.cleanup -> CreationGateController.unregister_conduit_gate), so the
    facade needs no new disposal plumbing.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/conduit_lineage_gate_ops.py:1-178
  - src/melder/aether/aetheric_frame/dev_ops/dev_ops_manager.py (slot/init/cleanup/property for _conduit_lineage_gate_ops)
  IMPACT: elect/unelect strategies now have a clean DevOps-owned lineage-gate
    handle to depend on; remaining wiring is injecting it into the mediator
    builder when the strategies are implemented (post-seam).
  NEXT: (still blocked on compiler_strategy_0 no-op seam) inject the facade into
    TransactionStrategyBuilder + write the elect/unelect strategy bodies.
  REREAD: REQUIRED
  SCORE_0_TO_10: 7

## Progress — transaction machinery landed (mediator_builder_0, 2026-06-17T23:17:46Z)
- DATETIME: 2026-06-17T23:17:46Z
  TYPE: FACT
  CLAIM: Full elect/unelect TRANSACTION machinery is built and py_compile-green
    (user directed me to build the seam myself rather than wait on the no-op).
    Landed: (1) enum ELECT_CONDUIT_CLUSTER_LEADER / UNELECT_CONDUIT_CLUSTER_LEADER;
    (2) two strategy files; (3) builder registration; (4) mediator
    start_transaction allow-list; (5) 8 unit tests (resolve + seal-exclusive +
    drain/reopen coordination + elect-no-drain + commit bind/unbind).
    DESIGN CHOICE: the strategies read their effect collaborators from the
    transaction METADATA (cluster_creations / leader_creations /
    conduit_lineage_gate_ops / member_root_conduit_ids) instead of builder
    injection -- so NO TransactionStrategyBuilder facade-injection ripple was
    needed. The call site (conduit_cluster.py, compiler_strategy_0's lane) passes
    them when it opens the transaction.
    elect = light (inert->active, no drain; on_start no-op; commit binds).
    unelect = coordinated (on_start drains every member root lineage via the gate
    facade; commit unbinds; on_end reopens every member root on EVERY exit path =
    fail-closed). Q1 (drain timeout -> abort + reopen) and Q2 (elect trusts inert
    invariant) both honored.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_request/transaction_request.py:44-45
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/elect_conduit_cluster_leader_transaction_strategy.py:1-145
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/unelect_conduit_cluster_leader_transaction_strategy.py:1-173
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/transaction_strategy_builder.py:372-379
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/transaction_mediator.py:600-601
  - tests/unit/melder/aether/dev_ops/change_control_manager/test_transaction_strategy_builder_and_strategies.py (8 cluster-leader tests)
  IMPACT: The transaction side of the epic is complete. Remaining = the
    conduit_cluster.py call sites that OPEN these transactions (compiler_strategy_0's
    lane; metadata contract handed off via mailbox 2026-06-17T23:17:46Z) + the
    user-run 3.14t suite (sandbox is Py3.10; melder/__init__ eager chain can't
    import here).
  NEXT: await compiler_strategy_0 wiring the call sites + user venv suite run.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Correction — strategies are envelope-only, domain owns the bind (mediator_builder_0, 2026-06-18T23:06:13Z)
- DATETIME: 2026-06-18T23:06:13Z
  TYPE: DECISION
  CLAIM: SUPERSEDES the apply_commit_delta design in the note above. User
    mandate: a mediator transaction may manage ONLY the DevOps system (scope
    claims + the DevOps-owned creation-gate facade); it must NOT reach into the
    runtime or take another system's responsibility. So the strategies no longer
    bind/unbind cluster_creations -- that is the DOMAIN effect. Both
    apply_commit_delta overrides were REMOVED; the strategies inherit the base
    (fact-baseline stamp only). The cluster_creations.bind/unbind is run by the
    domain call site (ConduitCluster) inside the held window, between
    mediator.start_transaction and end_transaction -- the same shape as
    Spellbook.notch_spell calling self._apply_notch (spellbook.py:2577-2587).
    The transaction's role is the FREEZE only (confirmed by ClusterCreations'
    own docstring: "the transactions freeze all melds before they bind/unbind").
    Final strategy surfaces: elect = seal member conduits EXCLUSIVE, no drain
    (inert invariant), no domain effect. unelect = seal EXCLUSIVE + on_start
    drains every member root lineage via ConduitLineageGateOps + on_end reopens
    on every exit path (fail-closed); no domain effect. Corrected strategy
    metadata: elect -> {member_conduit_ids}; unelect -> {member_conduit_ids,
    member_root_conduit_ids, conduit_lineage_gate_ops}. cluster_creations and
    leader_creations are NO LONGER strategy metadata.
  EVIDENCE:
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/elect_conduit_cluster_leader_transaction_strategy.py:1-107
  - src/melder/aether/aetheric_frame/dev_ops/change_control_manager/transaction_manager/strategies/unelect_conduit_cluster_leader_transaction_strategy.py:1-141
  - src/melder/aether/spellbook/spellbook.py:2577-2587 (admit -> domain effect -> commit precedent)
  IMPACT: Mediator side is clean and lane-correct. Correction NOTICE sent to
    compiler_strategy_0 (mailbox 2026-06-18T23:06:13Z) so the call-site ticket
    drops the bind-in-strategy contract and instead calls bind/unbind in the
    ConduitCluster call site.
  NEXT: await compiler_strategy_0 ACK of the corrected contract + call-site wiring.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8
