# Code-description patch: Compiler disposal references and cache values

## Trigger justification
Multiple compiler families and cache boundaries must preserve the same ordered policy.
An indiscriminate tuple removal would conflate live ownership with serialized value schemas.

## Control flow
1. Processor resolves each live Spell and assigns its names directly to the runtime record.
2. Generalized single/dual builders pass that record list directly into every corresponding step.
3. Many-only no-overrides arrays hold each step Spell's list without copying the inner names.
4. Solo compiler normalization returns the same nonempty list, preserving its existing empty case.
5. Existing namespace builders keep outer tuples of Spell-list references.
6. IR/hash emitters retain ordered tuple projections; hydration resolves current bound Spells.

## Edge/error behavior and rollback
Empty metadata never enables disposal registration. Preserve existing no-disposal, existence,
construction-error, and override behavior. Restore the six propagation/type edits together if
validation exposes a real contract conflict; do not modify synchronization to repair tests.

## Invariants and idempotency
The list is established at bind and treated as fixed policy. Compiler cleanup does not own its
contents. Cached executable code is rebound to live objects, never reused with stale namespaces.
No post-creation mutation support or new cache version is part of this change.

## Non-goals
No compiler algorithm rewrite, Creations-loop rewrite, crystal/graft changes, or blanket codemod.

## Validation focus
Check exact order and identity at each live handoff, deterministic serialized rows, real
registration from emitted code, repeat compilation/cache reuse, and stored-code hydration.
