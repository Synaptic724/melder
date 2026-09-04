# Architecture patch: ordered disposal priority, configuration slice

## Patch scope and non-goals
- Patch ID: ordered_disposal_priority_2026_09_04
- Current executable scope: SpellbookConfiguration and its focused tests only.
- The epic's later Bind/Spell, compiler, Creations, and replay changes remain separate.
- No runtime ordering guarantee is introduced by this configuration-only slice.
- No new locks, snapshots of disposal lists, dependencies, root flags, or publication changes.

## Changed-components matrix
| Component | Current slice | Later work, not implemented here |
| --- | --- | --- |
| Spellbook Configuration and System State | Bool schema/default, fluent setter, reload accounting | Bind consumes the selected priority |
| Binding Pipeline | Unchanged | Resolve both ordered groups and hash/store the resolved list |
| Compiler / Creations | Unchanged | Preserve the established list to actual disposal |
| Crystallizer / Nexus | Generic paths unchanged | Verify transport and ordered replay |

## Interface and boundary deltas
- Register `enforce_priority_disposal_methods` as bool, default False before any validation.
- Add `with_enforce_priority_disposal_methods(enabled=True) -> SpellbookConfiguration`.
- True requests matching book names first; False requests spell-specific names first.
- The setter stores policy only. It neither matches methods nor invokes disposal.
- Raw and cleared configurations expose False through the ordinary property API.
- The flag remains configurable during assembly; freeze prevents subsequent writes.

## Cross-component invariants
- Supplied configurations are adopted before validation, so default availability is an init concern.
- Default loading preserves explicit values. Do not seed a write-once value that prevents opt-in.
- Book configuration payloads carry the flag through their existing generic scalar path.
- Missing recorded defaults remain visible in reload's `backfilled` report, including eager False.
- Live instance ownership, bind fingerprints, and cleanup algorithms are unchanged in this slice.

## Migration / rollout order
1. Establish the configuration contract and focused tests.
2. Implement schema/default/fluent/reload changes in the configuration owner.
3. Run configuration unit/component and owner-side reload tests.
4. Prepare later component contracts before touching their source; then wire Bind/Spell.
5. Complete runtime/replay and public documentation/assets under their existing tasks.

## Rollback strategy
Revert only this slice's new flag, setter, default accounting, and associated assertions.
No stored record is rewritten and no user/other-agent change is reverted.

## Validation expectations and evidence plan
- Default False before `.with_defaults()`/validation and after `clear_properties()`.
- Explicit True/False, fluent self-return, defaults preservation, validation, and freeze refusal.
- Old record missing the flag reports False as backfilled; recorded True/False is not backfilled.
- Preserve existing configuration name order and set-once name behavior.
- Source evidence: `src/melder/aether/spellbook/configuration/spellbook_configuration.py`.
- Adoption evidence: `src/melder/aether/spellbook/spellbook.py:5423-5475`.

## Ticket coverage map
- Epic: EPIC-2026-09-02-ordered-live-spell-disposal.
- Story: STORY-2026-09-04-ordered-disposal-binding.
- Contract task: TASK-2026-09-04-ordered-disposal-patch-contract (configuration gate only).
- Implementation: TASK-2026-09-04-disposal-priority-configuration.
- Generic transport verification: TASK-2026-09-04-disposal-configuration-roundtrip (later).
- Runtime, replay, docs/assets, and end-to-end tasks retain their prerequisite gates.

## Unknowns and decision requests
No unresolved choice blocks configuration. Differing-host graft policy/recorded SHA joins
remain scoped to the replay task and do not justify changes to this configuration slice.
