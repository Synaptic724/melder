# Admission window control flow

## Trigger
Concurrency-sensitive check-then-act defect in ConduitCloud.add_conduit_to_cluster, observed by CI.

## Control flow
Check Cloud lifecycle and frame posture. Enter the Cloud RLock, resolve the target cluster, validate
the root, and refuse a published membership or pending admission. Reserve the conduit id, leave the
Cloud lock, then call add_member. In finally discard the reservation under the Cloud lock. Only a
successful add runs handle_join; both registration/recording and sharing run outside the Cloud lock.

## Errors and rollback
Eligibility errors leave membership unchanged. Every registration exit clears the pending claim;
a failure before publication can be retried. Errors retain existing propagation and recovery;
introduce no membership rollback or broad catch. handle_join failure keeps published membership.

## Invariants and idempotency
Repeated admission is a refusal, not an idempotent success. Parallel calls to any cluster in this
Cloud share the same reservation guard. No Cloud lock is held across add_member or handle_join.

## Non-goals
No registry API changes, nested transaction changes, member teardown redesign or broad refactor.

## Validation focus
A coordination gate holds member writes until eight arrivals: on the broken code those arrivals
are eight writes after empty reads; on the fix they are eight guarded admissions, with the first
member write held pending. Count distinct threads. Pre-resolve discovery so unrelated lookup locking cannot
release the gate. Real membership, registry writes and share transactions remain exercised.
