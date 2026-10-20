# ConduitCloud admission

## Purpose and boundary
The frame-owned Cloud admits normal roots to its clusters. It owns cluster discovery, while the
cluster publishes membership through its DevOps identity and owns sharing.

## Before and after
Before: get_clusters_for_conduit and add_member are separate lock windows. Every contender can
read an empty index, then all register successfully; two target clusters can both retain the id.
After: cluster lookup, normal-root check, eligibility and a pending-id reservation run under one
Cloud RLock. add_member (including recording) and handle_join run after that lock is released.

## Interface delta
No new arguments or return values. An already-clustered root raises the existing exclusivity
ValueError even when calls overlap; losers execute no add_member or handle_join.

## State and lifecycle
Cloud owns a set of pending conduit ids, guarded by its existing RLock. A registration's finally
removes its reservation, even on failure; cleanup clears and deletes the set. Membership still
belongs to the existing cluster/registry. Callers quiesce Cloud operations before cleanup, as before.

## Failure modes
Remove duplicate successful admissions and cross-cluster membership caused by two empty reads.
Existing frame-posture, root-state, missing-cluster and cleaned-state errors remain.

## Dependencies and ordering
Reserve before leaving the Cloud lock, publish membership before releasing the reservation, and open
CLUSTER_JOIN afterwards. Never hold the Cloud lock while calling add_member: its record emission can
invoke a user store handler, which must be able to read Cloud from another thread.

## Validation
The forced schedule must reject seven of eight callers and leave exactly one cluster and matching
DevOps edge. Registration and sharing callbacks permit Cloud reads; a failed registration permits
retry. The original ordinary contention test and existing cluster lifecycle checks must pass.

## Unknowns
Share failure rollback and ordering against concurrent leaves are unchanged and outside this repair.
