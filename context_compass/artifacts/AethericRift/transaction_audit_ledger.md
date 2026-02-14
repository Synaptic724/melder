# 🚧 Ticket: Add Rich Transaction & Audit Ledger to Melder (Bind/Link/Ownership/Permissions/ACL)

## Summary

Melder needs a **first-class transaction system** (an append-only **audit ledger**) that records **everything** that mutates registration state or access/ownership state:

* **Bind/Register** operations (what was registered, by whom/what, with what metadata)
* **Linking** operations (what depends on/links to what; link creation/removal)
* **Permissions / ACL** changes (grant/revoke/modify permissions)
* **Ownership requests & transfers** (request → approve/deny → transfer)
* Full provenance: **what conduit transferred what** (who/what initiated, what path was used, and causal chain)

This is required now for observability/debuggability and later for **ACLs on thread handles** and enforceable permissions.

## Problem

Today, Melder can mutate internal state (bind/link/ownership semantics) without leaving a durable, queryable trail. That creates:

* Weak provenance (hard to answer: *who registered this? why does this exist? when did ownership change?*)
* Poor debugging (can’t reconstruct the chain of events that produced a state)
* No auditability/security posture for future ACL enforcement
* No consistent mechanism to correlate related actions across conduits (caller → container → linkers → transfers)

## Goals

1. Introduce a **Transaction & Audit Ledger** that captures all state-mutating operations.
2. Make all bind/link/permission/ownership actions emit **structured ledger events**.
3. Provide a stable schema enabling:

   * Reconstruction of current state (optional, later)
   * Postmortem analysis / forensic tracing
   * Permission and ownership audit trails
4. Support future: **thread handle ACLs** and recorded enforcement decisions.

## Non-Goals (for this ticket)

* Building a full UI or external dashboard
* A full event-sourced rebuild of all Melder state (we can evolve toward it later)
* Distributed consensus / cross-process replication (keep local-first)

## Definitions

* **Conduit**: any execution pathway/actor that performs a state mutation (API call, tool, agent, thread factory, orchestration layer, etc.).
* **Subject**: the thing being acted on (binding key, provider, link, handle, resource).
* **Actor**: identity performing/initiating the action (human, agent, system component, thread).
* **Transaction**: a correlated sequence of ledger events representing one logical operation (may include nested/child events).

## Requirements

### 1) Event Types (minimum set)

Melder must emit events for:

**Bind / Registration**

* `BIND_REGISTERED`
* `BIND_REPLACED`
* `BIND_REMOVED`
* `BIND_METADATA_UPDATED`

**Linking**

* `LINK_CREATED`
* `LINK_REMOVED`
* `LINK_RESOLVED` (optional, but useful: a resolution decision/trace)

**Ownership**

* `OWNERSHIP_REQUESTED`
* `OWNERSHIP_GRANTED`
* `OWNERSHIP_DENIED`
* `OWNERSHIP_TRANSFERRED`
* `OWNERSHIP_REVOKED` (if applicable)

**Permissions / ACL**

* `PERMISSION_GRANTED`
* `PERMISSION_REVOKED`
* `PERMISSION_MODIFIED`

**Thread Handle ACLs (future compatibility hooks)**

* `HANDLE_ACL_ATTACHED`
* `HANDLE_ACL_UPDATED`
* `HANDLE_ACCESS_CHECKED` (decision: allow/deny + reason)

### 2) Ledger Record Schema (structured)

Each ledger record must include, at minimum:

* `event_id` (unique)
* `ts_utc` (timestamp)
* `event_type`
* `txn_id` (correlation ID for a logical transaction)
* `parent_event_id` (optional; for nested operations)
* `conduit_id` (which conduit executed)
* `actor` (structured identity)
* `subject` (structured identity)
* `object` (optional; “target” or “related entity”)
* `action` (verb + parameters)
* `result` (success/failure)
* `reason` (human-readable)
* `invariants` (optional assertions/checks that were validated)
* `context` (arbitrary structured metadata: repo, host, pid, thread id, request id, agent id, etc.)

**Strong requirement:** records are **machine-queryable** (JSON-like structure), not unstructured text.

### 3) Provenance / Causal Chain

The system must make it possible to answer:

* What conduit initiated the mutation?
* What chain of nested actions occurred beneath it?
* Which prior event created the state being modified?

Minimum mechanism:

* `txn_id` + `parent_event_id` + `object` referencing the prior state/event when applicable.

### 4) Ownership Transfer Semantics

Ownership changes must be explicitly represented as a **two-phase flow**:

1. Request: `OWNERSHIP_REQUESTED`
2. Decision: `OWNERSHIP_GRANTED` or `OWNERSHIP_DENIED`
3. Application: `OWNERSHIP_TRANSFERRED` (must reference request + decision)

This ensures no silent ownership swaps.

### 5) Permission Model Compatibility

Even if enforcement is partial today, ledger must support:

* a named permission set (e.g., `read`, `bind`, `link`, `transfer`, `dispose`, `use_handle`)
* explicit grantor/grantee identities
* scope (global, container, namespace, binding key, handle id)

### 6) Storage & Retrieval

Initial implementation can be local-first with one of:

* In-memory ring buffer + periodic persistence
* Append-only file log (JSONL)
* SQLite table (append-only)

Must provide:

* Query by `txn_id`, `event_type`, time range
* “Explain” view: render a transaction chain in chronological order

### 7) Performance Constraints

Ledger emission must be:

* O(1) append per event
* Non-blocking or minimally blocking under concurrency
* Configurable verbosity (event types on/off, sampling, max size)

### 8) Security / Integrity

* Ledger should be **append-only** by default (no mutation of historical records)
* Optional integrity: hash-chain records (later) so tampering is detectable
* Redaction policy: structured field-level redaction hooks for secrets

## Proposed Architecture (high-level)

* `TransactionManager` (creates `txn_id`, manages nesting)
* `Ledger` (append-only sink)
* `LedgerEvent` (schema model)
* `ConduitContext` (actor/conduit metadata propagated through calls)

**Key design:** any state mutation API must accept or derive a `ConduitContext` + `txn_id`.

## Acceptance Criteria

* All bind/register operations emit ledger events with full subject + conduit metadata
* All link create/remove operations emit ledger events
* Ownership request/decision/transfer are represented as explicit events with references
* Permission grants/revokes emit ledger events
* Can query and print an “explain transaction” trace that shows causal order
* Tests validate:

  * IDs/correlation are preserved
  * Events are emitted in correct sequence
  * Failure paths emit failure events (with reason)

## Test Plan (minimum)

* Unit tests for ledger schema + append ordering
* Unit tests for transaction nesting (parent/child)
* Integration-style tests:

  * bind → link → ownership request → transfer → permission grant
  * verify ledger reconstructs the chain

## Rollout / Migration Notes

* Start by instrumenting core APIs (bind/link/ownership/permission) behind a feature flag
* Default to on (dev), configurable off (prod) if needed
* Add compatibility stubs for future `HANDLE_*` ACL events now (schema support even if no enforcement)

## Open Questions (to resolve during implementation)

* Canonical identity schema for `actor`, `subject`, `object`
* Persistence backend choice (JSONL vs SQLite) and rotation strategy
* Redaction policy and sensitive-field marking
