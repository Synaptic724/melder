# Architecture patch: ordered disposal configuration and producers

## Patch scope and non-goals
- Patch ID: ordered_disposal_priority_2026_09_04
- Configuration is implemented; current executable scope adds Spellbook, Bind, and Spell producers.
- The epic's later compiler, Creations, and replay ownership changes remain separate.
- This slice establishes ordered bind metadata; full cache/record/replay guarantees remain pending.
- No new locks, snapshots of disposal lists, dependencies, root flags, or publication changes.

## Changed-components matrix
| Component | Current slice | Later work, not implemented here |
| --- | --- | --- |
| Spellbook Configuration and System State | Bool schema/default, fluent setter, reload accounting | Bind consumes the selected priority |
| Spellbook Core | Forward both groups and priority at each active/inactive bind; retire shared candidate latch | Existing admission, indexes, and lifecycle remain unchanged |
| Binding Pipeline | Resolve both ordered groups and hash/store the resolved list | Consumers retain the resulting policy |
| Compiler / Creations | Unchanged | Preserve the established list to actual disposal |
| Crystallizer / Nexus | Generic paths unchanged | Verify transport and ordered replay |

## Interface and boundary deltas
- Register `enforce_priority_disposal_methods` as bool, default False before any validation.
- Add `with_enforce_priority_disposal_methods(enabled=True) -> SpellbookConfiguration`.
- True requests matching book names first; False requests spell-specific names first.
- The setter stores policy only. It neither matches methods nor invokes disposal.
- Raw and cleared configurations expose False through the ordinary property API.
- The flag remains configurable during assembly; freeze prevents subsequent writes.
- Spellbook forwards explicit names, configured names, and priority separately to Bind.
- Bind walks the preferred group first and retains each matching name once in an owned list.
- Spell retains that resolved list; its optional constructor default creates a fresh empty list.
- Inspector parity uses resolved ordered names; the hash helpers do not apply book policy.

## Cross-component invariants
- Supplied configurations are adopted before validation, so default availability is an init concern.
- Default loading preserves explicit values. Do not seed a write-once value that prevents opt-in.
- Book configuration payloads carry the flag through their existing generic scalar path.
- Missing recorded defaults remain visible in reload's `backfilled` report, including eager False.
- The bind SHA consumes the final resolved order at the existing fingerprint boundary.
- Live instance ownership, transaction admission, and cleanup algorithms remain unchanged.
- Missing names and non-class profiles retain the existing matching scope; no new reflection.
- Retire conjure's obsolete frozenset/flag recheck; do not replace it with private-mutation guards.

## Migration / rollout order
1. Establish the configuration contract and focused tests.
2. Implement schema/default/fluent/reload changes in the configuration owner.
3. Run configuration unit/component and owner-side reload tests.
4. Consume the producer contracts, then wire/test both bind paths and Spell list storage.
5. Complete runtime/replay and public documentation/assets under their existing tasks.

## Rollback strategy
Revert a producer change coherently across forwarding, matching, storage, and its tests.
The verified configuration slice can remain independently installed.
No stored record is rewritten and no user/other-agent change is reverted.

## Validation expectations and evidence plan
- Default False before `.with_defaults()`/validation and after `clear_properties()`.
- Explicit True/False, fluent self-return, defaults preservation, validation, and freeze refusal.
- Old record missing the flag reports False as backfilled; recorded True/False is not backfilled.
- Preserve existing configuration name order and set-once name behavior.
- Test default/True priority, empty/overlapping/missing names, independent binds, active/staged
  members, inspector parity, retained list ownership, and real cross-process hash stability.
- Source evidence: `src/melder/aether/spellbook/configuration/spellbook_configuration.py`.
- Adoption evidence: `src/melder/aether/spellbook/spellbook.py:5423-5475`.

## Ticket coverage map
- Epic: EPIC-2026-09-02-ordered-live-spell-disposal.
- Story: STORY-2026-09-04-ordered-disposal-binding.
- Contract task: TASK-2026-09-04-ordered-disposal-patch-contract (configuration and producer gates).
- Configuration: TASK-2026-09-04-disposal-priority-configuration (implemented/in review).
- Producer implementation: TASK-2026-09-04-ordered-disposal-bind-and-spell.
- Generic transport verification: TASK-2026-09-04-disposal-configuration-roundtrip (later).
- Runtime, replay, docs/assets, and end-to-end tasks retain their prerequisite gates.

## Unknowns and decision requests
No unresolved choice blocks configuration. Differing-host graft policy/recorded SHA joins
remain scoped to the replay task and do not justify changes to this configuration slice.
