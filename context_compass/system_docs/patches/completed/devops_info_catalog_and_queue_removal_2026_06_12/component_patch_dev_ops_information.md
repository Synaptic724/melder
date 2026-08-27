# Component Patch: DevOps Information Strategies + Config Surface

## Metadata
- Patch ID: devops_info_catalog_and_queue_removal_2026_06_12
- Status: active
- Owner: cowork / reviewer_0
- Task: TASK-2026-06-12-remove-queue-flag-and-implement-info-strategy-catalog
- Created: 2026-06-12T23:19:18Z
- Targets: `system_docs/src_components.md` (DevOps Control Plane component;
  Transaction Admission Plane component; AethericFrameConfiguration rows)

## Component: DevOps Information Strategies (NEW)
- Path: `src/melder/aether/aetheric_frame/dev_ops/information_strategies/`
- Files:
  - `information_strategy_support.py` — `InformationFreshnessInspector`
    (static): `normalize_region` (folds "scope:" keys onto fact-record
    region form), `build_freshness_view` (per-region baselines, ages,
    optional staleness verdict), `read_optional_max_age` (metadata
    tolerance validation).
  - `transaction_activity_view_strategy.py` — axis-selected live activity
    (identity_kind+identity_id | scope_key | transaction_type); returns
    sorted transaction ids + count + freshness for the touched region.
  - `cluster_fanout_strategy.py` — exactly one of conduit_id | cluster_id;
    conduit form unions members across all of the conduit's clusters into
    `sibling_conduit_ids`; cluster form lists `member_conduit_ids`.
  - `transfer_blast_radius_strategy.py` — requires conduit_id; returns
    owning spellbook, sibling conduits, borrowers, providers, clusters,
    `blast_radius_size`, freshness over target + owner + related conduits.
  - `frame_operational_view_strategy.py` — no required metadata; rollup of
    identity counts by kind, spellbook/conduit/link/cluster shape,
    transaction counts by type, fact-record coverage by family; freshness
    spans every reported region.
  - `registry_consistency_audit_strategy.py` — symmetry audit across
    ownership, link, cluster pairs and transaction scope/type/identity
    reverse indexes; returns `consistent`, `finding_count`, `findings`
    ({check, detail}), `checked_pairs`. No metadata required; never
    mutates.
- All strategies: static `execute(*, devops_information_registry,
  metadata) -> Dict`, ids-only detached payloads, no live objects.

## Component: DevopsInformationStrategyBuilder (UPDATED)
- Registers the five-strategy default catalog at construction
  (`_register_default_strategies`); later `register_strategy` calls under
  the same normalized name override defaults.
- New slot `_execution_counts_by_name`; `execute` increments the counter
  only after the strategy returns (failures do not count).
- New surface: `get_execution_count(name) -> int`,
  `list_execution_counts() -> Dict[str, int]` (detached copy).

## Component: DevopsInformationRegistry (UPDATED, additive)
- New method `snapshot_relationship_maps()` — one-lock detached snapshot of
  spellbook/conduit ownership, provider/borrower links, cluster membership,
  and all transaction reverse indexes; identity tuple keys rendered
  "kind:id"; set values rendered as sorted tuples.

## Component: AethericFrameConfiguration / TransactionMediator (UPDATED)
- `queue_competing_root_transactions` removed end to end (ctor, slot,
  validation, property, fluent setter, with_defaults, matches_posture,
  describe_posture; frame merge; CCM wiring; mediator ctor/slot/
  configure/describe). `TransactionMediator.configure` signature is now
  `configure(*, max_transaction_wait_time_in_seconds)`.
- Wait-bound docstrings now describe scope-acquisition waiting, not
  queueing.

## Test surfaces
- New ring: `tests/unit/melder/aether/dev_ops/test_devops_information_strategies.py`
  (23 tests: catalog registration, counters, five strategies, freshness
  inspector, injected-drift audit detection).
- Reconciled for flag removal: `test_aetheric_frame_configuration.py`,
  `test_transaction_mediator.py` (3 tests renamed to scope-contract
  framing), `test_transaction_mediator_expanded.py` (describe test),
  `test_change_control_manager_component.py`,
  `tests/_frame_posture_test_support.py`.
- Integration `test_aether_integration_change_control_transactions.py`:
  four pre-scope-contract tests rewritten (disjoint-parallel,
  overlap-timeout, shared-scope serialization, cross-family scope
  conflict); retired warn-mode duplicate deleted.
  `test_conduit_integration_concurrency.py` helper updated.

## Merge instructions
- Fold "DevOps Information Strategies" as a new `### Component:` section in
  `src_components.md` after the DevOps Control Plane component; fold the
  builder/registry/config updates into their existing sections.
