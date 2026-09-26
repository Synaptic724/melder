# code_description_patch_creations

## Metadata
- Patch ID: creation_slot_build_guards_2026_09_25
- Component: Creations store and emitted build blocks
- Status: promoted to src_architecture and src_components 2026-09-25; archived
- Owner: user (implementation: melder_0)
- Created: 2026-09-25T22:50:59Z
- Updated: 2026-09-25T23:28:41Z

## Trigger Justification
- Concurrency and idempotency-sensitive change (lock discipline across generated code).

## Control-Flow Description (Pseudocode Level)
1. Build block for a slotted non-unique existence:
       inst = store._creations.get(sid)            # warm hit, no lock (unchanged)
       if inst is None:
           with store.slot_guard(sid):             # only builders of this slot wait
               inst = store._creations.get(sid)    # recheck
               if inst is None:
                   inst = build()                  # dependency steps take THEIR guards
                   store.add_creation(sid, inst)   # leaf: store lock, cleaned check, both dicts
2. Unique: same shape with `spell._lock` in place of `store.slot_guard(sid)` (unchanged).
3. slot_guard: `g = guards.get(sid)`; on miss `g = guards.setdefault(sid, RLock())` (atomic).
4. Purge (slotted non-unique): slot guard -> store lock detach -> release -> dispose.
5. Publish into a cleaned store: release the store lock, run the object's disposal methods, raise
   RuntimeError.

## Edge/Error and Rollback Semantics
- Same-thread re-entry (door then root step, or nested meld of the same slot) is allowed: RLock.
- Constructor failure releases the guard; nothing is published; retry builds again (unchanged).

## Invariants and Idempotency Expectations
- At most one constructor call per slot per store lifetime (between clears).
- Store lock never held across user code; guard map entries are never removed while the store lives.

## Explicit Non-Goals
- No change to warm-path reads, routing, or hook ordering.

## Validation Focus Points
- 11 existing regression cases plus unique -> many -> unique_per_conduit.
- Purge waits for an in-flight build of the same slot.

## Context / Handoff Summary
- What changed: described above.
- Remaining unknowns: none.
- Next entrypoint: creations.py.
