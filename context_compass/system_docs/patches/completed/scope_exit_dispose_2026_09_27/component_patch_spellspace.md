# Component patch: Creations and SpellSpace - lease flag and finished exits (2026-09-27)

## Before
- A SpellSpace carried no lease state: after managed exit or manual cleanup a kept handle could still `meld` and
  `purge` into the idle shell, and the next lease was served what it built.
- A second `cleanup()` of a manual space released it to the pool again.
- When disposal raised: managed exit skipped hook reset and pool release (space dropped); manual cleanup left the
  space registered and unreleased; permanent cleanup stopped before cleaning its Meld and deleting its fields.
- Cleaning a lesser inside its own managed space drained the thread stack, so the block's exit raised
  SpellSpaceScopeError ("stack corruption").
- Class, pool and meld docstrings promised `reset()`, a version bump and an active-scope check that do not exist.

## After
- `SpellSpace._released` (slot, starts False): `SpellSpacePool.release` sets it; `acquire`/`acquire_untracked`
  clear it; permanent cleanup sets it and keeps it as a documented tombstone.
- `meld` and `purge` first read `_released`; a released space raises SpellSpaceScopeError, a destroyed one the
  cleaned RuntimeError.
- `cleanup()` returns early for a released space; managed recycle, manual cleanup and permanent cleanup run their
  remaining steps in `finally`, so the space is pooled (or destroyed) and then the disposal group propagates.
- `__exit__` of a space released inside the block removes it from the top of the thread stack if it is still there
  (`SpellSpaceThreadState.discard_expected`) and returns. A space destroyed inside the block has already removed
  itself from the destroying thread's stack top in `_cleanup_for_destroy` (before its thread-state reference is
  deleted), so its exit only returns.
- Docstrings describe the lease flag instead of reset/version/active-scope (SpellSpace, SpellSpacePool and
  SpellSpaceMeld, whose `meld` contract also stops routing `many` to the owner conduit).
- Hot-path offsets (owner condition: scope use costs no more than before): `__exit__` runs the managed lane of
  `recycle_from_managed_context` inline, and `SpellSpacePool.release` reads its deque once.

## Interface deltas
- Public: `meld`/`purge` refuse released spaces (SpellSpaceScopeError); exits raise after finishing.
- Private: `_released` slot, `SpellSpaceThreadState.discard_expected(expected)`.

## State and failure deltas
- One bool per SpellSpace. Disposal failures no longer drop or half-destroy a space.

## Dependency and ordering
- Unchanged: disposal before hook reset before pool release; the managed lane stays lock-free and thread-confined.

## Validation expectations
- Component tests for the released refusal, double cleanup, each failing exit and the owner-cleaned-inside case;
  per-step benchmarks for space enter, warm meld and exit.
