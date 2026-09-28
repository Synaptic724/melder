# Component patch: Cleanable cleanup contexts propagate cleanup errors (2026-09-27)

## Before
- `_CleanupContext.__exit__` and `_AsyncCleanupContext.__aexit__` called the owner's cleanup at most once and
  swallowed any exception it raised (`except Exception: pass`).

## After
- The owner reference is dropped first, then cleanup runs once; its exception propagates. With a failing block the
  cleanup error rises with the block's exception as its context. The block's exception is never suppressed.

## Interface deltas
- Behavioural only: `using_cleanup()` and `async_using_cleanup()` no longer hide cleanup failures. No in-repo caller.

## Validation expectations
- Unit tests: propagation, at-most-once across repeated exits, block exception kept as context, async twin.
