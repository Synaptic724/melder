# Task: Wire elect/unelect cluster-leader transaction call sites (Phase 3 Step E)

## Metadata
- Task ID: TASK-2026-06-17-cluster-leader-election-call-sites
- Epic: EPIC-2026-06-16-unique-per-conduit-cluster-team-store
- Companion epic: EPIC-2026-06-16-cluster-leader-election-transactions (mediator_builder_0)
- Status: in_progress
- Owner: cowork
- Agent Name: compiler_strategy_0
- Priority: p2
- Created: 2026-06-17T23:57:47Z
- Updated: 2026-06-17T23:57:47Z

## Objective
Fire `elect_conduit_cluster_leader` on cluster leader election and
`unelect_conduit_cluster_leader` on leader leave/teardown from
`conduit_cluster.py`, passing the exact metadata the landed strategies read, so
the cluster team-store facade binds/unbinds inside the mediator's coordinated
transaction. This is Step E of the team-store epic Phase 3; the strategies
themselves are landed by mediator_builder_0.

## Ticket Contract
- ENTRY_GATE: active board row + this ticket; plan approved by user before any
  code edit (synaptic strict approval-loop).
- EXECUTION_BOUNDARY: `src/melder/aether/conduit/conduit_cluster.py` call sites
  only (Step E). Steps A-D (door route, route-key, finalize-step store source,
  liveness probe) are separate Phase 3 work, tracked but not in this ticket's
  edit boundary unless the user widens scope.
- DEPENDENCIES: landed enum/builder/mediator entries (do NOT re-add) +
  `cluster_creations.bind/unbind` (landed) + `ConduitLineageGateOps` (landed).
- EXIT_GATE: call sites compile; user-run 3.14t suite green (sandbox is 3.10,
  cannot run); no regression to `cluster_link`/`link`/`unlink`/`bind`/
  `transfer_ownership`.
- FAILURE_ESCALATION: DECISION_REQUEST for the open scope/lock/election asks;
  BLOCKER if opener-in-seal-set or capability-grant turns out to reject the
  transaction.

## Scope Boundaries
- In scope: the `handle_join` elect call site and the `handle_leave`/leader-
  teardown unelect call site in `conduit_cluster.py`; `master_conduit_id`
  bookkeeping; metadata assembly.
- Out of scope (this ticket): Steps A-D door wiring, Phase 4 cleanup-notify seam
  from Conduit teardown, Phase 5 tests/docs. (Tracked in the epic.)

## Landed machinery (verified; do NOT re-add)
- Enum: `ChangeTransactionType.ELECT_CONDUIT_CLUSTER_LEADER` /
  `UNELECT_CONDUIT_CLUSTER_LEADER` (transaction_request.py:44-45).
- Builder registration (transaction_strategy_builder.py:61,64,372,376).
- Mediator allow-list (transaction_mediator.py:600-601).
- Strategies (elect_/unelect_conduit_cluster_leader_transaction_strategy.py).
- Facade `ClusterCreations.bind/unbind` (cluster_creations.py).
- `DevOpsManager.conduit_lineage_gate_ops` -> `ConduitLineageGateOps`
  (dev_ops_manager.py:233; conduit_lineage_gate_ops.py:119,156).

## Metadata contract (CORRECTED 2026-06-18 per mediator_builder_0 NOTICE)
Strategies are ENVELOPE-ONLY (scope-seal + drain/reopen via the DevOps gate
facade). They do NOT touch cluster_creations. ConduitCluster calls
`cluster_creations.bind/unbind` ITSELF inside the held transaction window
(between start_transaction and end_transaction), like
`Spellbook.notch_spell` -> `_apply_notch` (spellbook.py:2577-2587).
- elect: metadata `{member_conduit_ids}`. Seals member conduits EXCLUSIVE; no
  drain (inert invariant). Call site does `cluster_creations.bind(leader._creations)`
  inside the window.
- unelect: metadata `{member_conduit_ids, member_root_conduit_ids,
  conduit_lineage_gate_ops}`. Seals + on_start drains every member root lineage
  via the gate facade + on_end reopens (fail-closed). Call site does
  `cluster_creations.unbind()` inside the window.
- DROPPED from strategy metadata: `cluster_creations`, `leader_creations`.

## Wiring facts (verified)
- `Conduit.transaction(type, *, conduits=..., metadata=...)` is the entry; metadata
  flows straight into `build_start_plan` (conduit.py:2477+).
- gate ops reachable from any member: `member._aetheric_frame.dev_ops_manager.conduit_lineage_gate_ops`
  (conduit.py:227; aetheric_frame.py:385; dev_ops_manager.py:233).
- member root ids: `Conduit._root_conduit_id` (conduit.py:248-250).
- leader store: `leader._creations` (conduit.py:256).
- member ids / live members: `ConduitCluster.members` + `_resolve_conduit_by_id`.

## Open decisions (for the user — DECISION_REQUEST)
- D1 SCOPE: Step E only (call sites; feature stays inert until A-D), or full
  Phase 3 (A-E) so cluster spells actually resolve through the facade?
- D2 (Step A, only if D1=full): create-once lock choice — (a) route locks the
  leader `Creations._lock` [recommended, byte-for-byte lineage] vs (b) add
  `get_or_create_once` to the facade. Never add a lock to the facade.
- D3 ELECTION (epic Q1): confirm v1 first-join-as-leader.
- D4 (epic Q3): owner-left cluster stays inert until deleted — confirm.
- D5 RISK: opener conduit is inside its own EXCLUSIVE seal set; confirm mediator
  admits same-identity opener (verify against same-thread nested-join admission).
- D6 RISK: cluster `DevopsIdentity.available_transactions=("cluster_link",)` —
  confirm elect/unelect are authorized for the opener (mediator allow-list vs
  per-identity capability grant); may require adding the two names.

## Steps / Checklist
- [x] Investigate epic + companion epic + landed strategies + call-site host.
- [ ] User approves scope (D1) + decisions D2-D6.
- [ ] Implement elect call site in `handle_join` (first-join leader).
- [ ] Implement unelect call site in `handle_leave` / leader teardown.
- [ ] (If D1=full) Steps A-D in a separate ticket/lane.
- [ ] Validate: user-run 3.14t suite (report "Not run." here until then).

## Files / Paths Impacted
- src/melder/aether/conduit/conduit_cluster.py (call sites)

## Validation
- Not run. (Sandbox is Py3.10; the repo is 3.14t. Recommended for the user:
  `pytest tests/unit/melder/aether/conduit -q`, plus the cluster integration
  suite once Steps A-E land.)

## Risks / Rollback Notes
- Call-site-only change; rollback = revert the two call sites. No new locks.
- Do not swallow exceptions at these sites (unlike the cluster_link sites);
  fail-fast so the transaction's on_end reopen runs (fail-closed).

## Notes
- DATETIME: 2026-06-17T23:57:47Z
  TYPE: HANDOFF
  CLAIM: Consumed inbound handoff from mediator_builder_0 (cluster-leader-election
    machinery landed; my lane = conduit_cluster.py call sites). Confirmed the
    enum/builder/mediator entries already exist (won't re-add) and captured the
    exact elect/unelect metadata contracts. This maps to team-store epic Phase 3
    Step E; Steps A-D still gate the feature actually turning on.
  EVIDENCE:
  - src/.../transaction_manager/strategies/elect_conduit_cluster_leader_transaction_strategy.py:1-144
  - src/.../transaction_manager/strategies/unelect_conduit_cluster_leader_transaction_strategy.py:1-172
  - src/melder/aether/conduit/conduit_cluster.py (no elect/unelect call sites yet; cluster_creations never bound)
  - codex/context_compass/tickets/epics/2026-06-16_unique_per_conduit_cluster_team_store_epic.md (PHASE 3 HANDOFF section)
  IMPACT: Defines a tight, evidence-backed call-site lane with the open decisions
    the user must settle before any edit.
  NEXT: Get user decisions D1-D6, then wire the two call sites.
  REREAD: REQUIRED
  SCORE_0_TO_10: 8

## Context / Handoff Summary
Step E of the team-store epic: wire elect (first-join) / unelect (leader leave)
transactions from conduit_cluster.py with the landed strategies' metadata
contracts. Strategies, enum, builder, mediator allow-list, facade bind/unbind,
and the gate-ops facade are all landed. Remaining: confirm scope (E-only vs full
Phase 3) + decisions D2-D6, then implement the two call sites. No edits until
approved.
