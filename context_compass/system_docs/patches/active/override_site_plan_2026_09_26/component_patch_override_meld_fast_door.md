# Component Patch: override melds use the fast meld door (Meld Resolution Runtime)

## Metadata
- Patch ID: override_site_plan_2026_09_26
- Component: Meld Resolution Runtime (ConduitMeld and SpellSpaceMeld front doors; Meld fast-door registry)
- Task: TASK-2026-09-26-build-site-plan-lowering
- Status: active
- Created: 2026-09-26T14:33:53Z

## Before
- The fast meld door serves only id-string melds with no override payload. Every override meld runs the full
  lane: spell-id-pool read, capability and spellspace checks, payload normalization, validation and resolution
  gates, hook and gate reads, context read, then the context's `_overrides_executor(meld, ov)[0]`.
- Measured on the owner's graphs (3.14t, shallow): full-lane override meld 394 ns at ConduitMeld.meld vs 200 ns
  for the override door it ends in; a normal meld skips that lane through the fast door.

## After
- An id-string meld whose payload is a non-empty `dict` reads the same fast-door entry
  `(spell, captured_context, captured_epoch)` and applies the same guard ladder as the normal fast lane: no meld
  hooks, `spell._door_epoch == captured_epoch`, `spell._creation_context is captured_context`, no spellbook-wide
  validation. On a hit it calls the live `captured_context._overrides_executor(self, payload)[0]` (read per hit;
  hydration swaps the slot in place) and runs the pending-cache-emit check. A miss, a `list`/`tuple` payload or an
  empty dict takes today's full lane unchanged.
- The full lane's non-dynamic, no-hook override branch builds the entry after a successful execution when the spell
  has no mutation override, exactly as the no-override branch does; so override-only callers reach the fast lane
  from their second call.

- Conduit.meld (2026-09-26, owner-approved public meld trim): for an automatic conduit and a string `spell_id`
  with no spell/spellframe/binding, the facade reads the meld door's entry itself with the same guard ladder and
  both arms, then continues in the door's positional id lane on a miss (no keyword marshaling); the cleaned check
  is an inline flag test before `check_cleaned()`. Three readers now share one guard ladder: ConduitMeld.meld,
  SpellSpaceMeld.meld and Conduit.meld. Measured solo meld 209 -> 111 ns (3.14t, main thread); from a worker
  thread 556 -> 404 ns.

## Interface / State Deltas
- No public API change. No new lock, state or registry; entries keep the spell-id keyspace (bounded by the
  registry). The payload is passed as given (the full lane's normalization returns non-empty dicts as-is).

## Behavior Deltas
- None under the existing guard contract: the fast lane only runs where the full lane would pass every gate it
  skips (capability and spellspace eligibility are immutable per version; validation is a live guard;
  resolution, hook and context changes bump the door epoch). Override key errors, P2 and root refusals come from
  the same `_overrides_executor`.
- Mutation overrides need a dynamic spell, and dynamic spells never get an entry (their creation gate routes them
  through admission), so a stored mutation override is never skipped.

## Validation Expectations
- Fast-door component tests: dict payloads are served by the fast lane with the payload applied; override-only
  callers build the entry; guard trips (spell hooks, meld hooks, context invalidation, validation required) fall
  to the full lane and run hooks; tuple and empty-dict payloads take the full lane; key errors are unchanged;
  spellspace override melds are served.
- Override suites, conduit and multithreading suites on 3.14t and GIL; override_entry_layers.py and the owner's
  test_overrides_all.py before/after.

## Rollback
- Remove the `elif` override arm and the entry write in the override branch of both front doors.
