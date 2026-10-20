# Component patch: SpellCompiler codegen - misses adopt their children (slotted_lifetime_ownership_2026_10_14)

Component: SpellCompiler and Validation Pipeline (site-plan lowering). Defects D4, D5.

## Before / after
- `SitePlanEmission._emit_miss`: registers each disposal-bearing `many` child placed in the miss with
  `c{i}.register_many(sidN, vN, dmN)` before the build lock (0.2.8235), then rechecks, constructs and publishes the
  holder. After: unchanged up to publication; when the miss has disposal-bearing `many` children, one more line runs
  right after publication, inside the build lock and the `if v{i} is None:` branch:
  `c{i}.adopt_children(sid{i}, v{i}, ((sidA, vA), (sidB, vB),))`, in step order.
- The adopted set is exactly the registered set: the non-shared steps placed in the miss whose spell declares
  disposal methods (nested shared sites adopt their own children in their own misses).

## Interface deltas
None public. Generated misses with disposal-bearing children gain one call; every other emitted line, and every
`_site_plan_executor` body, is byte-identical.

## State / failure deltas
- A holder's children are recorded with the holder (see the Creations patch) the moment it is published.
- Lost race / pinned-override refusal / failing holder constructor: no adoption runs; children stay registered.

## Dependency / ordering
Requires `Creations.adopt_children`. Door-held root misses (no `with` line) adopt at the same point. Plans are
emitted at hydration from manifest rows, so no cache generation moves.

## Validation expectations
Emission diff over representative shapes (normal and override plans, door-held root, nested sites, children with
and without disposal): only misses with disposal-bearing children differ, by the adoption line. Component tests of
0.2.8235 keep passing with the record read from the holder's entry.
