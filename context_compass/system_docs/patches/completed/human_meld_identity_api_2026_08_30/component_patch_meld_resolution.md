# Component Patch: Meld Resolution Public Facades

<!-- BEGIN ENTRY: "Conduit and SpellSpace identity dispatch" -->
## Before
- Public positional strings are forwarded unchanged and interpreted internally as spell IDs.
- Human name resolution requires `spell_name=`.
- Raw class references dominate beginner examples.

## After
- Public `spell_id=` forwards directly into the internal positional ID lane.
- Public positional strings are converted to internal `spell_name=` lookup.
- Non-string `spell` values retain concrete class/function/Protocol behavior.
- Both values supplied together raise a stable `ValueError`.
- Public `override=` forwards the same dict/list/tuple payload to internal
  `spell_override=` without translation or copying.

## Interface Deltas
- Rename public keyword `spell_name` to `spell_id` on `Conduit.meld` and `SpellSpace.meld`.
- Rename public keyword `spell_override` to `override` on `Conduit.meld`,
  `SpellSpace.meld`, and `CapabilityCommandSystem.meld`.
- Keep internal abstract/concrete Meld signatures unchanged.

## State and Failure Deltas
- No new owned state.
- One new caller failure: simultaneous `spell` and `spell_id`.
- No override error or payload-shape change; only the public keyword changes.
- Existing ID/name `KeyError` behavior remains owned by the internal door.

## Dependencies and Ordering
- Normalize public inputs before dynamic CreationGate admission.
- Delegate after normalization through the same mode-specific path as before.
- Do not alter CreationContext, SpellInputUtils, Creations, or SpellIndex.

## Validation Expectations
- Real human names resolve with default and named bindings.
- Real bind-returned SHA ids resolve via `spell_id=`.
- Concrete class and spellframe forms remain green.
- Conduit and SpellSpace parity is explicit.
- Dict/list/tuple override paths retain behavior through all three public surfaces.
- Zero public `.meld(..., spell_override=...)` callers remain.
<!-- END ENTRY: "Conduit and SpellSpace identity dispatch" -->
