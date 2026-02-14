# Change-Control + DevOps Object Map (Review)

## Scope
- Single aetheric frame only; no cross-frame coordination.
- Change-control is rule-based admission + embargo/conflict checks (no queues/executors).
- Objects follow Cleanable lifecycle with explicit cleanup/nulling.

## Core Objects and Responsibilities
### Aether + DevOps
- `Aether` (`src/melder/aether/aether.py`)
  - Owns per-frame `DevOpsManager`.
  - Facades `_get_change_control_manager(...)` and `_revalidate_dirty_roots(conduit_id, ...)`.
- `DevOpsManager` (`src/melder/aether/dev_ops/dev_ops_manager.py`)
  - Owns `IncidentManager`, `ChangeControlManager`, `SpellSystemStates`.
  - Facades `revalidate_dirty_roots(conduit_id, ...)`.

### Change-Control Stack
- `ChangeControlManager` (`src/melder/aether/dev_ops/change_control_manager/change_control_manager.py`)
  - Owns: transaction manager, conflict manager, embargo manager, orchestrator.
  - Tracks: in-flight request, staged mutation, pending changes, component-of index and dirty roots (per conduit).
  - Facades admission (`admit_request`), staged updates (`update_staged_request`),
    commit/abort, and revalidation (`revalidate_dirty_roots(conduit_id, ...)`).
- `ChangeControlOrchestrator` (`src/melder/aether/dev_ops/change_control_manager/orchestrator/orchestrator.py`)
  - Serialized admission gate and staged mutation registry.
  - Executes commit/abort hooks outside the admission lock.
- `ChangeControlTransactionManager` (`src/melder/aether/dev_ops/change_control_manager/transaction_manager/transaction_manager.py`)
  - Builds immutable requests, tracks in-flight requests, link mirror registry, audit hooks.
  - Provides scope key helpers (spellbook/conduit/cluster/binding/contract).
- `ChangeControlConflictManager` (`src/melder/aether/dev_ops/change_control_manager/conflict_manager/conflict_manager.py`)
  - Detects scope overlap using `scope_hashes` or `scope_keys`.
- `ChangeControlEmbargoManager` (`src/melder/aether/dev_ops/change_control_manager/embargo_manager/embargo_manager.py`)
  - Tracks embargoes by scope + owner, supports open/close/extend/advisory lookup.
- `ChangeControlTransactionRequest` / `ChangeControlAdmissionResult`
  (`src/melder/aether/dev_ops/change_control_manager/transaction_request/transaction_request.py`)
  - Immutable request and admission payloads.
- `ChangeControlStagedMutation`
  (`src/melder/aether/dev_ops/change_control_manager/orchestrator/staged_mutation.py`)
  - Staged metadata for an admitted request (scope/binding/contract keys, etc.).

### Conduit/Spellbook Surfaces
- `Spellbook.begin_transaction(...)` (`src/melder/spellbook/spellbook.py`)
  - Creates `ChangeControlTransactionRequest` for bind/link/transfer/mutation/cluster_link.
  - Adds spellbook/conduit scope keys and forwards to change-control admission.
- `Conduit.begin_transaction(...)` (`src/melder/aether/conduit/conduit.py`)
  - Validates conduit list for link transactions and forwards to Spellbook.
- `Spellbook` contract updates (`_add_contracted_spell`, `_remove_contracted_spell`,
  `_clear_contracted_spells_for_conduit`)
  - Refresh staged contract keys for active link requests.
- `Spellbook` link mirror wiring (`_create_link_contract`, `_sever_link_contract`)
  - Registers/unregisters borrower->provider entries in the transaction manager.
- `SpellCrafter` change-control integration (`src/melder/spellbook/spell_crafter/spell_crafter.py`)
  - Rebuilds component-of index and registers revalidator for dirty roots (conduit-scoped, owned roots only).

## Integration Paths (Call Flows)
- Admission:
  - `Conduit.begin_transaction` → `Spellbook.begin_transaction`
  - `ChangeControlManager.admit_request` → `Orchestrator.admit_request`
  - `ConflictManager.find_conflicts` + `EmbargoManager.find_embargoes`
  - `TransactionManager.add_in_flight` + `EmbargoManager.open_embargo`
- Staged metadata refresh:
  - `Spellbook._try_update_staged_*` → `ChangeControlManager.update_staged_request`
  - `Orchestrator.update_staged` + `EmbargoManager.extend_embargoes`
- Commit/abort:
  - `Spellbook.end_transaction` → `ChangeControlManager.commit_staged_request`
  - `Orchestrator.commit` or `Orchestrator.abort`
- Dirty-root lifecycle:
  - `SpellCrafter` rebuilds component-of index per conduit
  - `ChangeControlManager.revalidate_dirty_roots(conduit_id, ...)` invoked via `DevOpsManager`

## Ownership / Cleanup Boundaries
- `DevOpsManager` cleans `IncidentManager`, `ChangeControlManager`, `SpellSystemStates`.
- `ChangeControlManager` cleans all sub-managers and clears dirty/pending registries.
- Each sub-manager (`TransactionManager`, `ConflictManager`, `EmbargoManager`, `Orchestrator`)
  is `Cleanable` and nulls internal state on cleanup.

## Notes / Open Points
- Link mirror registry is owned by `TransactionManager` and updated via Spellbook
  link contract lifecycle. Admission currently uses explicit scope keys and
  conduit ids; link mirror data is informational unless promoted by policy.
- Dirty-root revalidation is mediated through `ChangeControlManager` and the
  SpellCrafter-registered callback.
