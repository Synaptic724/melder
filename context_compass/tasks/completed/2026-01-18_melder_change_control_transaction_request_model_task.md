- Completed: 2026-01-19
- Summary: Defined the change-control transaction request model, begin_transaction facade, and scope-key schema/embargo notes.

# Task: Define change-control transaction request model + begin_* APIs

## Metadata
- Task ID: TASK-2026-01-18-melder-change-control-transaction-request-model
- Story: STORY-2026-01-18-melder-post-conjure-binding
- Status: done
- Owner:
- Priority: p1
- Created: 2026-01-18
- Updated: 2026-01-19

## Objective
Define a request model for change-control transactions (type, scope keys,
affected conduits/spellbooks) and add a begin_transaction(type) facade that
submits requests for **admission** when change management is enabled (no queue).

## Scope Boundaries
- In scope:
  - Change request types: bind, link/contract, unlink, transfer ownership,
    mutation (placeholder), cluster share/refresh.
  - Scan requires an active bind transaction (not a standalone transaction type).
  - Scope-key schema used for conflict detection.
  - Stable scope hashing to compare requests deterministically.
  - begin_transaction(type) facade on Spellbook / Conduit / ConduitWard with
    context-manager helpers.
  - Optional enable/disable flag for change management.
- Out of scope:
  - Transaction execution logic.
  - Embargo/conflict resolution logic.
  - Request queues, priority scheduling, SLA/TTL, or DLQ behavior.
  - Any cross-aetheric-frame coordination.

## Steps / Checklist
- [x] Define request type enum + request payload contract.
- [x] Define scope-key schema for each request type.
- [x] Define stable scope hashing (string form + hash) for conflict checks.
- [x] Add begin_transaction(type) API stubs that create/admit requests when enabled.
- [x] Update interfaces for begin_transaction(type) APIs.
- [x] Document implicit embargo behavior for bind/link transactions.
- [x] Document that scan/bind require an active bind transaction.
- [x] Document default behavior when change management is disabled.

## Deliverables
- Change request model + scope-key contract + hashing rules.
- begin_transaction(type) API surface for transaction entrypoints.

## Files / Paths Impacted
- `src/melder/aether/dev_ops/change_control_manager/change_control_manager.py`
- `src/melder/aether/dev_ops/dev_ops_manager.py`
- `src/melder/spellbook/spellbook.py`
- `src/melder/aether/conduit/conduit.py`
- `src/melder/aether/conduit/conduit_ward/conduit_ward.py`
- `src/melder/utilities/interfaces/interfaces.py`

## Validation
- Passed (user-reported).
- Recommended commands:
  - `pytest tests/unit/melder/aether/dev_ops/`

## Risks / Rollback Notes
- Risk: Over-broad scope keys can over-serialize unrelated operations.
  Mitigation: keep scope keys minimal and explicit per request type.

## Done Checklist
- [x] Steps complete and checked off
- [x] Deliverables produced and linked
- [x] Documentation updated (if needed)
- [x] Validation status recorded
- [x] User walkthrough complete and acceptance criteria confirmed

## Context / Handoff Summary
- Create a formal transaction request model and begin_transaction(type) API
  so all mutations can be routed through the change-control **admission gate**
  when enabled (no queue).
  - All callers funnel through the orchestrator admission lock before mutation.
- Request schema (draft):
  - `request_id` (ULID), `request_type`, `created_at`, `initiator_id` (conduit_id)
  - `spellbook_id`, `conduit_ids`, `cluster_id` (as applicable)
  - `scope_keys` (normalized string keys), `scope_hashes` (stable hashes)
  - `binding_keys` / `contract_keys` (normalized tuples)
  - `metadata` (reason, agent/task id, flags)
- Scope-key normalization (draft):
  - `scope:spellbook:<id>`, `scope:conduit:<id>`, `scope:cluster:<id>`
  - `binding:<frame_key>:<binding_key>`
  - `contract:<frame_key>:<binding_key>:<peer_conduit_id>`
  - Stable hash: sort keys, join with `|`, hash with SHA256.
- Scope key helpers were added to the transaction manager (spellbook/conduit/
  cluster/binding/contract) to standardize key creation, but per-request
  scope-key selection is still caller-defined.
- begin_transaction(type) supported types (draft):
  - `bind`, `link`, `unlink`, `transfer_ownership`, `mutation`, `cluster_share`.
- Transaction stories mapped to request types:
  - bind → spellbook scope + binding keys (scan requires active bind transaction).
  - link/contract/unlink → borrower+provider conduit scopes + contract keys.
  - transfer ownership → source+target conduit scopes + spell_index_id.
  - mutation placeholder → spell_index_id scope only (deferred execution).
  - cluster share/refresh → cluster scope + member conduits + spell_index_id.
- Implicit embargo rules (draft): begin_bind blocks link/contract; begin_link
  blocks bind/scan for the affected spellbook/conduits until commit/abort.
## Scope-Key Schema (Current Draft)
- bind: `scope:spellbook:<id>` + `binding:<frame_key>:<binding_key>` (if provided).
- link/unlink: `scope:conduit:<borrower>` + `scope:conduit:<provider>` +
  `contract:<frame_key>:<binding_key>:<provider>`.
- transfer_ownership: `scope:conduit:<source>` + `scope:conduit:<target>` +
  `spell_index:<id>` (placeholder key; finalize once transfer model lands).
- mutation (placeholder): `spell_index:<id>` (single lineage scope).
- cluster_share/refresh: `scope:cluster:<id>` + `scope:conduit:<member>`.
## Implicit Embargo Behavior (Current Draft)
- bind: embargo `scope:spellbook:<id>` and derived binding scopes until commit.
- link/unlink: embargo provider/borrower conduit scopes during contract changes.
- transfer_ownership/mutation: embargo affected spell_index scope only.
