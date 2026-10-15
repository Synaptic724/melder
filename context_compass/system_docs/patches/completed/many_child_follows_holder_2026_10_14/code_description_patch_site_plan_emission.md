# Code description patch: SitePlanEmission child registration (many_child_follows_holder_2026_10_14)

## Control flow
1. `render`: `_emit_context(None, "    ", body)` emits the top-level steps; a disposal-bearing `many` there emits
   `many_store.register_many(...)` and makes the plan emit the innermost-scope prologue (unchanged).
2. `_emit_shared_hit(i, ...)` (unchanged) reads `c{i}` and calls `_miss{i}` on a miss; `_emit_miss(i, ...)` calls
   `_emit_context(i, "    ", children)`.
3. `_emit_context(context, ...)`: for each child placed in `context`, a shared child emits its hit; a `many` child
   calls `_emit_many(index, step, indent, lines, store)` with `store = "many_store"` at top level and
   `store = f"c{context}"` inside a miss. It returns True only when a top-level step read `many_store`.
4. `_emit_many`: construct; when the spell has disposal methods, emit `{store}.register_many(sidN, vN, dmN)`.
5. `_emit_miss`: unresolved-input check, the children, then the guard, recheck, construct and publish into `c{i}`.

## Edge / error semantics
- Nested sites: a child placed in an inner site's miss registers in that inner site's store; a `many` child of a
  `many` step inside a miss registers in the miss's site store (the chain belongs to that holder).
- A pinned shared site (winning override) keeps its miss; its children still register in its `c{i}`.
- Door-held root: the root miss takes no guard but still receives `c{root}`; children register there.

## Invariants / idempotency
Exactly one registration per built child; no change to construction order or lock order.

## Non-goals
No per-object child tracking (purge of a holder does not dispose its children); no change to `register_many`.
