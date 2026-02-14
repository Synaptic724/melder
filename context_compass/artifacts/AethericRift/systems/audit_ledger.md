# Transaction and Audit Ledger (System)

## Status
- Status: draft
- Tags: PROPOSED / UNKNOWN

## Purpose (PROPOSED)
Provide an append-only, queryable audit trail for state-mutating operations that
matter for governance and debugging:
- bind/register
- linking
- permissions/ACL changes
- ownership requests/transfers
- (future) handle/ObjectRef access checks

## Proposed Requirements (PROPOSED)
- Structured, machine-queryable events (not just log lines).
- Correlated transactions:
  - txn_id for a logical operation
  - parent_event_id for nesting/causal chains
- Provenance:
  - which "conduit"/actor initiated the change
  - what was modified
  - why (reason)
- Append-only by default; future integrity options (hash chain).

## Event Types (PROPOSED)
Minimum set from the draft:
- BIND_REGISTERED / BIND_REPLACED / BIND_REMOVED / BIND_METADATA_UPDATED
- LINK_CREATED / LINK_REMOVED / LINK_RESOLVED (optional)
- OWNERSHIP_REQUESTED / OWNERSHIP_GRANTED / OWNERSHIP_DENIED
- OWNERSHIP_TRANSFERRED / OWNERSHIP_REVOKED (if applicable)
- PERMISSION_GRANTED / PERMISSION_REVOKED / PERMISSION_MODIFIED
- HANDLE_ACL_ATTACHED / HANDLE_ACL_UPDATED / HANDLE_ACCESS_CHECKED (future hooks)

## Record Schema (PROPOSED)
Minimum fields from the draft:
- event_id, ts_utc, event_type
- txn_id, parent_event_id (optional)
- conduit_id
- actor, subject, object (optional)
- action (verb + params)
- result (success/failure), reason
- invariants (optional)
- context (structured metadata: host/pid/thread/request/agent)

## Storage Options (UNKNOWN)
Draft options:
- in-memory ring buffer + persistence
- append-only JSONL
- append-only SQLite table

## Open Questions (UNKNOWN)
- Canonical identity schema for actor/subject/object (esp. for "who" in AI usage).
- Persistence backend choice and rotation strategy.
- Redaction policy for secrets/sensitive fields.
- Where ConduitContext/txn_id comes from (thread-local vs explicit parameter vs wrapper injection).

## Sources
- `context_compass/artifacts/transaction_audit_ledger.md`

