# Architecture Patch: Release-Matrix Concurrency Repair

<!-- BEGIN ENTRY: "Cross-runtime release-matrix correctness" -->
## Objective
Make the supported Python 3.14/3.14t release matrix deterministic by correcting
two invalid identity tests and synchronizing shared-spell CreationContext rebuilds
with conduit-local resolution revalidation.

## Non-Goals
- No removal of GIL or free-threaded matrix cells.
- No public API, existence, lifecycle, or packaging-support change.
- No lock on the state-2 hot CreationContext read or steady-state executor path.
- No redesign of Phase 5-11, LoadGate ownership, or the compiled door system.
- No fairness queue or waiter-priority redesign in the unwired Aetheric Mediator.

## Changed Components
- Spell-owned cold/rebuild CreationContext retrieval.
- LoadGate mediator test choreography.
- `Existence.many` distinct-instance test choreography.
- Focused concurrency regression and release-matrix validation.
- Scheduling-neutral Aetheric Mediator churn probe.

## Invariants
- A ready spell context (`CounterSwitch` state >= 2) remains a lock-free read.
- A missing/invalidated context acquires `spell._lock`, rechecks readiness, and
  only then enters factory election/build.
- Conduit-local Phase 5-11 revalidation already owns `spell._lock`; a competing
  cold context build therefore waits until phase 11 republishes its artifact.
- `Existence.many` continues returning a fresh object per meld. A test must keep
  compared objects alive while asserting identity.
- LoadGate authority belongs to one live holder thread, and that same thread
  performs normal `release()`.
- Python GIL posture remains warning-only; supported metadata remains Python 3.14+.
- With no fairness mechanism, short-lived intent churn may either admit a
  world-exclusive waiter through a gap or produce an evidenced bounded timeout.

## Interface Delta
None. The change is internal synchronization plus test-contract correction.

## Migration Order
1. Add patch contracts and map them to implementation/validation.
2. Add double-checked slow-path locking to Spell context retrieval.
3. Keep the LoadGate holder alive through release in the unit test.
4. Retain `many` instances before comparing identity in the integration test.
5. Add deterministic/repeated regression coverage for shared-spell revalidation.
6. Replace the churn probe's undocumented fairness assertion with its two
   contract-valid outcomes and leak/evidence checks.
7. Run focused 3.14 and 3.14t tests, then supported suites and asset checks.

## Rollback
Revert the Spell slow-path lock and the corresponding test corrections together.
Do not retain a probabilistically green matrix by deleting runtime cells.

## Coverage Matrix
| Contract | Implementation | Validation |
| --- | --- | --- |
| Ready context remains lock-free | `Spell._get_or_build_creation_context` | direct state-2 unit assertion + suite |
| Cold rebuild waits for phase owner | same method | forced-window concurrency regression |
| Foreign root parks behind live holder | mediator test | holder/release event choreography |
| Many objects are distinct while live | resolution break matrix | retained-object identity assertion |
| Both runtimes remain supported | workflow unchanged | Python 3.14 and 3.14t focused/full runs |
| Churn has a bounded honest outcome | Aetheric Mediator test only | admission or evidenced timeout; no leak |
<!-- END ENTRY: "Cross-runtime release-matrix correctness" -->
