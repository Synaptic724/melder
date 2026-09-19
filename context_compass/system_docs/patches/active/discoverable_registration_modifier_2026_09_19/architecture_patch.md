# Architecture Patch: Native registration resolution capability

- Patch ID: discoverable_registration_modifier_2026_09_19
- Status: active
- Agent: updater_0

<!-- BEGIN ENTRY: Native resolvable registration policy -->
## Scope and Non-Goals
Add a native resolvable bool, default True, to active/inactive binding and its Spell record.
S2 establishes admission, identity and inspection only. OVERRIDE_REQUIRED compilation/execution,
Nexus graph projection, crystal replay and final generated-asset qualification belong to S3-S7.
No new lifetime, ownership model, source-body versioning, key namespace or release is introduced.

## Changed Components
| Component | Change |
| --- | --- |
| Binding Pipeline | Bind transports/validates capability, hashes it and stores it on Spell. |
| Spellbook Core | Both bind doors forward native policy; descriptions expose it. |
| Conduit Runtime | Binding facades explicitly forward the same bool. |

## Interfaces and Boundary Deltas
- Spellbook.bind/bind_inactive and Conduit.bind/bind_inactive add resolvable: bool = True.
- Bind.bind/_bind_logic and fingerprint/inspector accept the same flag.
- Spell stores a read-only per-version resolvable property with deterministic cleanup.
- SpellBinder's existing kwargs channel must forward/reset the choice; no extra fluent API is required.
- Explicit False permits a user Protocol definition as a non-resolvable class record; True still refuses.

## Cross-Component Invariants
- Omitted/True binding fingerprints remain byte-for-byte v4-binding compatible.
- False uses v4-binding-non-resolvable as the hash domain, with all other inputs/order unchanged.
- Bool admission rejects coercion before profile construction; independent hashing also validates its input.
- Capability is neither metadata, active/parked state, Existence nor resolution_required.
- Kernel/module/primitive guards and existing naming/lifetime/member checks remain in force.
- No key collision is bypassed and no instance lifecycle is changed by this foundation.

## Migration and Rollout
1. Add regression evidence and native admission/hash/storage.
2. Wire public facades and inspection; prove fluent/inactive/default behavior.
3. Hand native policy to later compiler/runtime/persistence stories.
4. Qualify the integrated feature before release; this patch is not full non-resolution enforcement.

## Rollback
Revert only this patch's source/test changes and regenerate affected documentation/graph assets.
No external state migration or publication occurs here; True identities remain unchanged throughout.

## Validation and Evidence
Use the existing no-GIL environment. Test native field/metadata separation, default/False hash parity,
strict bool validation, direct/decorator/facade/fluent/inactive routes and unchanged refusal boundaries.
Record real test outcomes in the task; do not infer execution support from metadata assertions.

## Ticket Coverage
- Epic: EPIC-2026-09-19-discoverable-non-resolvable-registrations
- Story: STORY-2026-09-19-discoverable-registration-modifier
- Task: TASK-2026-09-19-implement-resolvable-registration-modifier

## Unknowns and Decisions
Owner selected OVERRIDE_REQUIRED and existing version rules. Detailed runtime/graph/replay work remains
in later stories and is explicitly outside this patch's completion claim.
<!-- END ENTRY: Native resolvable registration policy -->
