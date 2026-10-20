# Code description patch: holder-owned children (slotted_lifetime_ownership_2026_10_14)

## Control flow (emitted miss, cold path)
1. Unresolved-input refusal (unchanged).
2. Children: each `many` child placed in the miss is constructed; a disposal-bearing one is registered with
   `c{i}.register_many(sidN, vN, dmN)` (unchanged, before the build lock).
3. Build lock (unless the door holds it), recheck, P2 refusal when pinned (unchanged).
4. On a miss of the slot: construct the holder, publish it (`add_creation` or the lock-free store), then
   `c{i}.adopt_children(sid{i}, v{i}, ((sidN, vN), ...))`.
5. `Creations.adopt_children` under the store lock: verify the slot holds this holder, move each child from its
   bucket (identity scan from the end) into the holder's `HolderDisposalEntry`, drop emptied buckets.

## Edge / error semantics
- Lost cold race, P2 refusal or a raising holder constructor: step 4 never runs; the children stay in their buckets
  (tracked, disposed with the store) exactly as in 0.2.8235.
- The store was cleaned between publication and adoption: `adopt_children` returns; the cleanup already detached
  and disposes both registries (children through their bucket record).
- A child purged by a concurrent `many` purge before adoption is skipped (already disposed by that purge).
- A holder without disposal methods gets a record with `methods=[]` so its children are still disposed with it.

## Ordering
Whole-store disposal stays newest-first by dict position: the holder's record keeps the position of its publication
(a tuple replaced in place) or is inserted right after it; disposing it runs the holder's methods, then its children
newest-first, so a holder that uses a child in its own disposal still finds it open.

## Invariants / idempotency
Each child is either in exactly one bucket or in exactly one holder record, never both; adoption of the same child
twice cannot happen (one publication per slot, under the build lock).

## Non-goals
`many` children of a top-level `many` root (no holder) and objects shared between a holder and the plan's top level
keep the innermost-scope registration (unchanged).
