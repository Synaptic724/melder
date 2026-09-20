# Component Patch: Binding Pipeline

<!-- BEGIN ENTRY: Bind admission and Spell capability -->
## Purpose and Boundary
Bind reflects a candidate, validates registration policy, fingerprints the result and creates a Spell.
Spell retains immutable registration facts while later systems manage execution and lifetime.

## Before and After
Before: resolvable passed through generic kwargs is inert metadata and has no native identity meaning.
After: the native bool is validated and passed to fingerprinting and a read-only Spell.resolvable property.
The ordinary path remains True. A False Protocol definition may be reflected; True still rejects it.

## Interface Deltas
- Add resolvable=True to Bind.bind, _bind_logic, spell_id_inspector and sha256_profile.
- Add a keyword-only native parameter and private slot/property to Spell.
- False fingerprints use a separate domain prefix; True keeps the exact original sequence.
- Invalid non-bool values raise an explicit TypeError. No truthiness/string coercion.

## State and Lifecycle
Store one bool per Spell. Its lifecycle follows the record, including deletion on cleanup.
Keep metadata, activity, existence, user_created_object and creation stores independent.
Do not introduce a live setter or reuse another state flag for this capability.

## Failure Deltas
False can cross the Protocol-target refusal only; it cannot cross kernel/module protection or existing
Protocol spellframe member validation. Existing callable/instance unique-only constraints remain unchanged.
Inspector/hash input validation is independent because tools call those APIs without binding.

## Dependencies and Order
Read S1 admission/identity evidence. Implement hashing/storage before public forwarding tests go green.
Keep ordered disposal inputs and the resolved effective spell name identical between inspector and bind.

## Validation
Test a fixed legacy class profile fingerprint, omitted versus explicit True equality, False separation,
constructor-signature sensitivity, native read-only field and metadata isolation. Use real bind profiles
for class/Protocol/callable/instance cases, retaining current refusal tests as compatibility checks.

## Unknowns
S3/S4 must consume this field before claiming runtime non-resolution. S6 must record/replay it explicitly.
<!-- END ENTRY: Bind admission and Spell capability -->
