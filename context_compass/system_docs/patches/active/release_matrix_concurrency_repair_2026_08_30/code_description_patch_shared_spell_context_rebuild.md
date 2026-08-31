# Code Description Patch: Shared Spell Context Rebuild

<!-- BEGIN ENTRY: "Double-checked cold context retrieval" -->
## Control Flow
`Spell._get_or_build_creation_context` becomes:

1. Read the spell-owned CounterSwitch.
2. If state is ready (`>= 2`), return the published context without locking.
3. Otherwise acquire `spell._lock`.
4. Re-read switch state and the published context.
5. If revalidation published while waiting, return that context.
6. Resolve the existing CreationContextFactory and delegate to its unchanged
   get-or-build election.
7. Return the built/published context and release the spell lock.

## Edge and Error Semantics
- A missing factory remains a stable RuntimeError.
- A truly missing phase-11 artifact still fails through CreationContextBuilder.
- A transient missing artifact during a valid phase run is no longer observable
  because the phase runner owns the same spell lock.
- Re-entrant dependency behavior remains valid because `spell._lock` is an RLock.

## Test Corrections
- The LoadGate test uses `Event` objects so the holder remains alive, signals
  acquisition, waits for permission, and performs its own `release()`.
- The `many` test stores all three returned objects before comparing identity,
  matching Python's lifetime-scoped `id()` guarantee.
- The unwired Aetheric Mediator churn probe accepts either a successful
  whole-world admission through a quiescent gap or a bounded timeout carrying
  scope/holder evidence; both outcomes must leave no claims or live churners.

## Invariants
- No lock is added to ready-context or executor hot paths.
- No GIL-specific branch is introduced.
- No matrix cell is skipped or marked allowed-to-fail.
- No public behavior or exception contract changes.

## Explicit Non-Goals
- No global lock, context copy, retry loop, sleep-based synchronization, or
  interpreter-specific workaround.
<!-- END ENTRY: "Double-checked cold context retrieval" -->
