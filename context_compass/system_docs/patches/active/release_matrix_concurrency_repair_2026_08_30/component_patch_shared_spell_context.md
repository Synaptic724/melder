# Component Patch: Shared Spell Context Rebuild

<!-- BEGIN ENTRY: "CreationContext rebuild synchronization" -->
## Before
- Phase-5 target revalidation clears spell-owned codegen outputs and the
  CreationContext while holding `spell._lock`.
- Another conduit can observe switch state 0 and enter the lock-free factory
  build before phase 11 republishes `spell_codegen_creation`.
- The builder then raises even though revalidation is legitimately in progress.

## After
- State-2 ready-context reads remain the current one-load fast path.
- A state below 2 enters `spell._lock`, rechecks state/context, and delegates to
  the existing factory only when a build is still required.
- A concurrent revalidation owns the same re-entrant lock, so the cold reader
  wakes only after phase publication completes.

## Interface Deltas
None. `Spell._get_or_build_creation_context` keeps its signature and return type.

## State and Failure Deltas
- No new owned state or synchronization primitive.
- The existing spell `RLock` extends to the cold context-rebuild boundary.
- The transient missing-phase-11 RuntimeError is removed from valid concurrent
  revalidation; genuine missing-artifact states still fail in the builder.

## Dependencies and Ordering
- The fast state check occurs before locking.
- The state/context check repeats after locking.
- Factory election/build happens under the spell lock only on the cold path.
- Instance execution occurs after the method returns and is not added to this lock.

## Validation Expectations
- The previously failing three shared/cluster concurrency tests pass repeatedly.
- A forced phase-revalidation window proves a second conduit waits rather than builds early.
- Existing context-factory election, hot-door, many, dynamic, and cleanup suites remain green.
- Both GIL and free-threaded Python 3.14 execute the focused set successfully.
<!-- END ENTRY: "CreationContext rebuild synchronization" -->
