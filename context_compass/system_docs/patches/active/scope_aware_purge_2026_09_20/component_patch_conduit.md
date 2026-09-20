# Conduit purge facade contract

## Purpose and boundary
Conduit is the user-facing execution scope; its Meld already carries the caller identity/stores.

## Before and after
Expose additive purge forwarding without changing existing meld or whole-conduit cleanup.

## Interface deltas
purge(spell=None, *, spell_id=None, spellframe=None, binding_name=None, purge_all=True) -> int.
Default removes all matching entries. False and instance-reference targets are explicitly not implemented.
Strings are logical names; spell_id is explicit machine identity. Reject simultaneous spell/spell_id.

## State and lifecycle
Check cleaned state, normalize identity as meld does, then delegate. No scope exit, recycle,
registration deletion, compiler invalidation or new hot-path gate.

## Failure modes
Propagate lookup, authority and disposal failures from their owners. No partial unbinding.

## Dependencies and ordering
Creations primitive and shared Meld discovery precede this thin facade.

## Validation
Root/lesser forwarding, all selectors, cleaned scope, authority refusal, re-meld and pool reuse.

## Unknowns
None for the additive facade.
