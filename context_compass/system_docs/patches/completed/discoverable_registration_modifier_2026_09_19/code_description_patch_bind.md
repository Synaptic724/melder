# Code Description Patch: Resolution capability admission

<!-- BEGIN ENTRY: Bool admission and compatible fingerprint branch -->
## Trigger
The Protocol admission gate changes conditionally and the fingerprint gains a capability branch.

## Control Flow
1. Shared bind receives the native bool from direct/decorator/facade transport.
2. Validate the bool before building profile/Spell state; retain unconditional kernel/module protection.
3. Refuse Protocol-as-target when True; let explicit False proceed to normal class reflection.
4. Keep normal lifetime, naming and Protocol spellframe member checks.
5. Hash the same metadata sequence under the True legacy or False domain prefix.
6. Construct Spell with the native bool and complete its normal profile.
7. Spellbook registers active or parked state by the unchanged path.

## Edge/Error and Rollback Semantics
- None, numeric and string substitutes are not booleans; reject rather than coerce.
- A False target still cannot violate kernel registration protection, module policy or unique-only rules.
- Preserve existing bind failure propagation; no new catch-all or alternate registration store.
- Independent fingerprinting validates input even when no Bind instance is involved.

## Invariants and Idempotency
Omitted and explicit True are identical to the current fingerprint. False differs only by hash domain.
The native value cannot be overwritten through public property assignment or confused with metadata.
No mutable per-bind state is added to Bind; decorator closures capture their own bool.

## Non-Goals
No source-body hashing, new source/version registry, runtime override classification or cache schema redesign.

## Validation Focus
Test failure before registration, Protocol False admission/True refusal, all existing target families,
legacy hash identity and effective-input parity. Later S3/S4/S6 tests prove execution and persistence.
<!-- END ENTRY: Bool admission and compatible fingerprint branch -->
