# Architecture Patch: Info-Strategy Catalog + Queue-Flag Removal

## Metadata
- Patch ID: devops_info_catalog_and_queue_removal_2026_06_12
- Status: active
- Owner: cowork / reviewer_0
- Task: TASK-2026-06-12-remove-queue-flag-and-implement-info-strategy-catalog
- Created: 2026-06-12T23:19:18Z
- Targets: `system_docs/src_architecture.md` (frame configuration surface;
  DevOps information plane)

## Delta 1: `queue_competing_root_transactions` is removed everywhere
The frame-posture flag retired by the scope-acquisition plane
(`devops_scope_acquisition_2026_06_12`, completed) is now removed from the
whole system rather than kept as a documented no-op:
- `AethericFrameConfiguration`: ctor param, slot, validation, property,
  fluent setter `with_queue_competing_root_transactions`, `with_defaults`
  reset, `matches_posture` comparison, and `describe_posture` key are gone.
- `AethericFrame` configuration merge no longer copies the flag.
- `ChangeControlManager` no longer reads it from frame configuration.
- `TransactionMediator`: ctor param, slot, `configure(...)` kwarg, and
  `describe()` key are gone. `configure` now takes only
  `max_transaction_wait_time_in_seconds`.
Architectural meaning: root admission policy has exactly one knob — the
scope-wait bound. There is no queueing mode; overlap is the only
serialization criterion.

## Delta 2: the DevOps information plane gains its strategy catalog
`DevopsInformationStrategyBuilder` now registers a default catalog at
construction and counts successful executions per strategy name. The
catalog (new package
`src/melder/aether/aetheric_frame/dev_ops/information_strategies/`):
- `transaction_activity_view` — live transaction ids along one axis
  (identity, scope key, or transaction type).
- `cluster_fanout` — cluster membership fan-out for one conduit or one
  cluster.
- `transfer_blast_radius` — full relational impact set for transferring one
  conduit (owner, siblings, borrowers, providers, clusters).
- `frame_operational_view` — one-shot frame-wide rollup (population,
  ownership/link/cluster shape, transaction pressure, fact coverage).
- `registry_consistency_audit` — symmetry audit over every bidirectional
  map and transaction reverse index; any asymmetry is evidence a write
  bypassed the transaction plane.
Every result (except the audit) carries a uniform `freshness` block built
from the fact-record baselines, with an optional `max_age_in_seconds`
tolerance that yields `stale_regions` + a `fresh` verdict. This implements
the control-plane economy: callers check the baseline first and only
re-derive when cold or stale.

## Delta 3: registry exposes one same-instant relationship snapshot
`DevopsInformationRegistry.snapshot_relationship_maps()` (additive) returns
all twelve forward/reverse maps copied under one lock acquisition, with
identity tuple keys rendered as "kind:id". This is the read surface for
deep views and audits; strategies never touch registry privates.

## Boundaries
- Live-runtime-truth probes (verifying mirrored maps against real runtime
  objects) are out of scope until probe contracts exist on runtime classes.
- Strategy execution remains caller-paid; nothing in the runtime invokes
  the catalog automatically.
