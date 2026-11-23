# component_patch_creations

## Metadata
- Patch ID: failed_late_bind_unwind_2026_11_22
- Component: Creations - `Creations.forget_slot`
- Status: implemented at 0.2.8316; merged
- Owner: Mark (accountable); melder_0 (synaptic_python_developer)
- Created: 2026-11-23T10:14:18Z
- Updated: 2026-11-23T11:20:00Z

## Component Purpose and Boundary
- Current boundary: a store gives up a slot only by disposing it (purge, a clear, cleanup) or by moving it (extract);
  its shelf index changes only in `_note_slot` and `cleanup`.
- Target boundary: `forget_slot(key)` takes one slot out - the live entry, its disposal record and its shelf entry -
  without disposing the object, for a caller that filed it and must take it back (the unwind of an existing object
  bound in a refused window).

## Before/After Behavior Summary
- Before: an unwind could not take back an existing object's slot without disposing the caller's object.
- After: the slot, its disposal record and its shelf entry are gone; the object is untouched and is the caller's; the
  slot guard stays (guards are never removed while the store is live).

## Interface Deltas
- `Creations.forget_slot(key: str) -> bool`: True when a slot was held under the key and removed; False otherwise.

## State and Lifecycle Deltas
- The shelf index gains a second writer: `forget_slot` removes the key from its shelf (and drops an emptied shelf) and
  its shape, under the store lock.

## Failure Mode Deltas
- None: a cleaned store answers False.

## Dependency and Ordering Constraints
1. Runs under the store lock, a leaf; takes nothing under it and runs no user code.

## Validation Expectations
- After `forget_slot`, the count, the purge and the live probe of the spell id do not see the slot; the object's
  disposal methods have not run; a later filing of the key files it afresh.
