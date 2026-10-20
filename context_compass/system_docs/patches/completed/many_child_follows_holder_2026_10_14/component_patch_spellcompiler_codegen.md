# Component patch: SpellCompiler codegen - site-plan lowering and the singleton specializer (many_child_follows_holder_2026_10_14)

## Before / after
- `SitePlanEmission._emit_many`: always emitted `many_store.register_many(sidN, vN, dmN)`; `_emit_miss` emitted the
  innermost-scope prologue (`many_store = meld._spellspace_creations` / `meld._conduit_creations`) when its children
  registered. After: `_emit_many` takes the store expression; `_emit_context(None, ...)` passes `many_store` (the
  top-level prologue is unchanged) and `_emit_context(i, ...)` passes `c{i}`, so a miss's children register
  `c{i}.register_many(sidN, vN, dmN)` and the miss needs no prologue.
- `_install_specializing_door`: specialized any graph with a capturable `unique` step (minus the root-only short
  circuit). After: it also declines, returning the plain instance door, when `rows_feed_many_into_non_many_step(rows)`
  is True.

## Interface deltas
Internal signatures only (see the architecture patch). No public surface.

## State / failure deltas
- A shared site's disposal-bearing `many` children live in the holder's owner's store and are disposed with it.
- A losing thread's children in a cold race (built before the recheck finds the site stored) now live until the
  holder's owner's store is disposed instead of the melding scope (bounded: one set per lost race).
- `purge` of a `many` spell at the owner now also retires children of holders built through narrower scopes - the
  existing explicit-purge semantics, over the store that now holds them.
- A cleaned owner store refuses a child's registration exactly as `register_many` refuses any late publication.

## Dependency / ordering
Children are still placed and built before the site's guard; registration is the same leaf call on another store.

## Validation expectations
The 19 red tests turn green and the 7 controls stay green (GIL off and on); the unit test that pinned the innermost
scope for a miss's child is updated to the holder's store; existing specializer tests still install for graphs
without a `many` edge into a shared step; the full tree stays green.
