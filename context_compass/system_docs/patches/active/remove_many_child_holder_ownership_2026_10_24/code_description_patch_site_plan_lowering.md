# code_description_patch_site_plan_lowering

## Metadata
- Patch ID: remove_many_child_holder_ownership_2026_10_24
- Component: Codegen site-plan lowering
- Status: draft
- Owner: Mark (decision); melder_1 (executor)
- Created: 2026-10-24T20:06:55Z
- Updated: 2026-10-24T20:06:55Z

## Trigger Justification
- Why this artifact is required for this component: the change alters generated control flow in every miss that
  builds a disposal-bearing `many` child (where it registers, and what runs after publication).

## Control-Flow Description (Pseudocode Level)
1. `_miss{i}(meld, [ov,] c{i}, args..., v...)`: unresolved-input checks for the context.
2. When a child registers here: `many_store = meld._spellspace_creations`, else `meld._conduit_creations` (the
   prologue a top-level `many` uses).
3. Children: construct each; a disposal-bearing one `many_store.register_many(sidN, vN, dmN)`.
4. Guard (unless door-held), recheck, construct, publish `c{i}` - and return. No adoption call.

## Edge/Error and Rollback Semantics
- Edge case 1: a lost cold race - the loser's children are recorded in its own innermost scope and disposed when
  it ends (before: in the holder's store until that store ended).
- Error behavior 1: a raising holder constructor leaves the children recorded in the innermost scope, as before
  0.2.8235.
- Rollback behavior: none in generated code.

## Invariants and Idempotency Expectations
- Invariant 1: one registration per built child, in exactly one store.
- Idempotency condition 1: unchanged - registration is append-only; disposal runs once per store end.

## Explicit Non-Goals
- Non-goal 1: leasing managed misses (`kids{i}`, `h{i}.adopt`).
- Non-goal 2: the warm plan body.

## Validation Focus Points
- Validation item 1: emitted miss source per shape (plain, door-held root, key-set plan, leasing neighbour).
- Validation item 2: runtime routes, GIL off and on.

## Context / Handoff Summary
- What changed: nothing yet.
- Remaining unknowns: none.
- Next entrypoint: `SitePlanEmission._emit_miss`.
