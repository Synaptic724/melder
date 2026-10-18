# Code description patch: one version, one copy (contracted_copy_removal_by_version_2026_10_16)

## Control flow
1. Under the Book lock, read the peer's active map, lookup map and existence set; missing maps raise as today.
2. Walk the active map (index -> copy) for the copy whose own `spell_id` is the version asked for. The index comes
   from the map key, so a cleaned copy's deleted `spell_index` is never read.
3. Found: unregister the by-id entry, pop the index entry and the lookup key, update the existence set as today,
   and keep the key for the mark.
4. Not found: pop the version's parked copy and drop its id; with no parked copy, raise RuntimeError and change
   nothing.
5. After the lock: rule 2's mark for an active removal, the staged-key refresh, the RiskManager unregister.

## Edge and error semantics
- An index unlink calls this once per member, in the member set's order: each member's copy goes, in any order.
- Two active entries never share a version id: a version belongs to one index, and an index has one active copy.

## Invariants and idempotency
- Not idempotent, as before: a second removal of the same version raises.

## Explicit non-goals
- The ward's per-member loop and the half-done unlink it leaves on a raise: unchanged; with every member holding
  its own copy the loop no longer raises on the order.
