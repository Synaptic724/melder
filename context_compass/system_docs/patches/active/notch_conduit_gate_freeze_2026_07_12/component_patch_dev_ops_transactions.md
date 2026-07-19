# Component Patch: DevOps Transactions (notch freeze + on_end dispatch)

## Patch ID
notch_conduit_gate_freeze_2026_07_12

## Component
Transaction admission plane: `NotchTransactionStrategy`,
`TransactionMediator`, `ConduitLineageGateOps`, `Conduit.notch_spell`.

## Before
- Notch strategy `on_start`/`on_end` are no-ops; the notch seal excludes
  other transactions only. A meld-side validator (no claims, conduit gate
  ticket held across the whole meld) can straddle the swap; its verdict
  writes key by live `selected_spell_id` -> lands on the promoted member
  (probe-proven poison).
- Strategy `on_end` dispatch fires ONLY from
  `end_transaction_for_identity` (finally) and the
  `_start_strategy_transaction` failure path. Callers using plain
  `end_transaction` (notch conduit.py:3993, unelect cluster :885) never
  fire on_end on success -> the unelect gate freeze leaks closed gates.
- `ConduitLineageGateOps` has terminal close+drain
  (`close_and_wait_conduit_lineage`) and reopen only; no park-mode verb.

## After
- `NotchTransactionStrategy.build_start_plan` adds
  `normalized_metadata["quiesce_root_conduit_ids"] = tuple(sorted(conduit_ids))`
  (the same sealed set: owner conduit + registry borrowers/providers).
- `NotchTransactionStrategy.on_start`: reads
  `metadata["conduit_lineage_gate_ops"]` (absent -> return, unelect
  precedent) and calls `quiesce_conduit_lineage(root_id)` per id -
  park + drain, 30s default per gate; a timeout raises -> mediator
  start-failure path aborts the transaction and (via finalize dispatch)
  reopens.
- `NotchTransactionStrategy.on_end`: reopens every quiesced lineage via
  `enable_conduit_lineage` (fail-closed; runs on commit, abort, or error).
- `ConduitLineageGateOps.quiesce_conduit_lineage(root_conduit_id, timeout=30.0, interval=0.1)`:
  delegates to the controller's new park-mode
  `close_and_drain_conduit_lineage`.
- `Conduit.notch_spell` metadata gains
  `"conduit_lineage_gate_ops": self._aetheric_frame.dev_ops_manager.conduit_lineage_gate_ops`.
- `TransactionMediator._finalize_root_session` dispatches strategy
  `on_end` exactly once per root end in a finally (identity present +
  strategy family registered guards, mirroring
  `_apply_strategy_commit_delta`); the two old dispatch sites are
  removed.
- UNELECT FREEZE HEALED in the same lane (owner: "go fix the next
  defect"): `UnelectConduitClusterLeaderTransactionStrategy.on_start`
  switches from the TERMINAL `close_and_wait_conduit_lineage` to the
  park-mode `quiesce_conduit_lineage` - in-window melds now park and
  resume instead of raising, and the gates stay reopenable (open()
  cannot clear terminal closure by design; the terminal verb remains
  for shutdown consumers). Combined with the finalize on_end dispatch,
  the unelect freeze now opens AND closes correctly on every path.

## State/Failure Deltas
- New failure surface: quiesce timeout in on_start -> RuntimeError ->
  session aborted, gates reopened by the finalize dispatch. Teach-grade
  message names the lineage root.
- on_end failures propagate loudly from finalize (context-chained if a
  commit/abort exception is already in flight); gates-left-closed is
  always loud, never silent.

## Dependency/Ordering
- Requires the gate/controller park-mode verbs (component patch
  synchronization_gates) to land first.
- on_start runs AFTER admission (claims held) and BEFORE the domain swap;
  on_end runs at root finalize AFTER commit/abort. One-way order:
  claims -> gate freeze -> domain -> commit -> on_end reopen -> release.

## Validation Expectations
- Strategy unit rows: plan carries quiesce ids; on_start quiesces exactly
  those ids through a recording fake facade; on_end reopens them; absent
  facade -> both no-op.
- Mediator unit rows: on_end fires exactly once on commit; exactly once
  on abort; not at all for raw `begin_frame` sessions (no identity); the
  bind-wrapper identity-end path no longer double-fires.
- Acceptance: the lineage race probe flips green.
