# Cluster admission atomicity

Patch id: cluster_admission_atomic_2026_10_19
Author: expert_1, synaptic_python_developer

## Scope and non-goals
Restore the existing one-cluster-per-conduit admission contract at the Cloud boundary. No API,
transaction strategy, store ownership, leave behavior or share rollback redesign.

## Changed-components matrix
| Component | Delta |
| --- | --- |
| AethericFrame Services / ConduitCloud | Reserve each pending admission under the Cloud RLock. |

## Interfaces and boundaries
Existing signatures and ValueError text stay intact. Exactly one competing add succeeds; all other
adds of that conduit refuse, whether targeting the same cluster or different clusters.

## Cross-component invariants
Eligibility checks both published membership and pending admission under the Cloud RLock. Reserve
the conduit id before releasing that lock. Register the member outside it, then release the pending
claim in finally, after the DevOps membership edge is published. Recording and sharing can call
outward; neither runs with the Cloud lock held. Registry membership reads are leaf operations.

## Migration order
Force the read-before-add race in the existing integration test; capture red results. Serialize
the admission window with a pending-id reservation, verify callbacks and failed-registration retry,
run green regressions and runtime tiers, then update documents and assets.

## Rollback
Revert only this task's source/test/document delta if qualification fails. No persisted data or
configuration migration is introduced.

## Validation and evidence
Eight competitors, same cluster and two clusters: one success, seven exclusivity ValueErrors,
one coherent membership/registry and shares only on the winner. Preserve existing join/leave tests.

## Ticket coverage
TASK-2026-10-19-fix_cluster_duplicate_add_concurrency owns implementation, verification and closure.

## Unknowns and decisions
No unresolved design decision on this admission path. Concurrent deletion, leave and failed fan-out
retain their existing lifecycle semantics; no new claim of whole-entry/exit transactional atomicity.
