# Architecture patch: ordered disposal configuration and producers

## Patch scope and non-goals
- Patch ID: ordered_disposal_priority_2026_09_04
- Configuration, producers, and compiler propagation are implemented; current scope adds Creations storage.
- Replay ownership remains a separate task.
- This slice retains the established list through compilation; full record/replay remains pending.
- No new locks, snapshots of disposal lists, dependencies, root flags, or publication changes.

## Changed-components matrix
| Component | Current slice | Later work, not implemented here |
| --- | --- | --- |
| Spellbook Configuration and System State | Bool schema/default, fluent setter, reload accounting | Bind consumes the selected priority |
| Spellbook Core | Forward both groups and priority at each active/inactive bind; retire shared candidate latch | Existing admission, indexes, and lifecycle remain unchanged |
| Binding Pipeline | Resolve both ordered groups and hash/store the resolved list | Consumers retain the resulting policy |
| Compiler | Retain Spell list in processor, plans, and solo namespace bindings | Preserve serialized/hash tuples and all existing executor algorithms |
| Creations | Retain names through registration, extraction, and restoration | Preserve invocation, reverse traversal, and error handling |
| Crystallizer / Nexus | Generic paths unchanged | Verify transport and ordered replay |

## Interface and boundary deltas
- Register `enforce_priority_disposal_methods` as bool, default False before any validation.
- Add `with_enforce_priority_disposal_methods(enabled=True) -> SpellbookConfiguration`.
- True places the complete matching book block first; False places it last.
- Book order owns overlaps in both modes; only spell-only names form the other block.
- The setter stores policy only. It neither matches methods nor invokes disposal.
- Raw and cleared configurations expose False through the ordinary property API.
- The flag remains configurable during assembly; freeze prevents subsequent writes.
- Spellbook forwards explicit names, configured names, and priority separately to Bind.
- Bind establishes the matching book block, then inserts distinct spell-only names before
  or after it according to priority. One owned result list is hashed and retained by Spell.
- Spell retains that resolved list; its optional constructor default creates a fresh empty list.
- Inspector parity uses resolved ordered names; the hash helpers do not apply book policy.
- Compiler runtime records, generalized steps, many-only metadata, and solo namespaces borrow
  the established Spell list. They do not create a second inner collection.
- Serialized IR and hash tuples remain value boundaries; order is preserved in those values.
- Creations in-memory transfer payloads retain raw objects and their established list references.
  This transfer is not a serialization boundary and does not create new policy values.

## Cross-component invariants
- Supplied configurations are adopted before validation, so default availability is an init concern.
- Default loading preserves explicit values. Do not seed a write-once value that prevents opt-in.
- Book configuration payloads carry the flag through their existing generic scalar path.
- Missing recorded defaults remain visible in reload's `backfilled` report, including eager False.
- The bind SHA consumes the final resolved order at the existing fingerprint boundary.
- Live instance ownership, transaction admission, and cleanup algorithms remain unchanged.
- Missing names and non-class profiles retain the existing matching scope; no new reflection.
- Retire conjure's obsolete frozenset/flag recheck; do not replace it with private-mutation guards.
- Compiler cleanup clears only its own outer containers, never borrowed disposal lists.
- Creations teardown drops entry references without clearing borrowed method lists. Empty
  supplied lists retain identity; omitted optional metadata still uses an empty list.
- Cached executor hydration resolves current bound Spells; serialized names do not become
  a competing live policy source. No new cache format or invalidation mechanism is introduced.

## Migration / rollout order
1. Establish the configuration contract and focused tests.
2. Implement schema/default/fluent/reload changes in the configuration owner.
3. Run configuration unit/component and owner-side reload tests.
4. Consume the producer contracts, then wire/test both bind paths and Spell list storage.
5. Carry and verify the same list through compiler families and cold/cached execution.
6. Complete Creations/replay and public documentation/assets under their existing tasks.

## Rollback strategy
Revert a producer change coherently across forwarding, matching, storage, and its tests.
The verified configuration slice can remain independently installed.
No stored record is rewritten and no user/other-agent change is reverted.
Compiler rollback restores metadata/type and inline-registration changes together; retained schema tuples
remain unchanged in either direction. Do not roll back the verified producer slice.

## Validation expectations and evidence plan
- Default False before `.with_defaults()`/validation and after `clear_properties()`.
- Explicit True/False, fluent self-return, defaults preservation, validation, and freeze refusal.
- Old record missing the flag reports False as backfilled; recorded True/False is not backfilled.
- Preserve existing configuration name order and set-once name behavior.
- Test default/True priority, empty/overlapping/missing names, independent binds, active/staged
  members, inspector parity, retained list ownership, and real cross-process hash stability.
- Compiler tests cover record/plan sharing, both generalized builders, standalone many-only,
  solo override variants, registration inputs, cleanup of outer carriers, and cached hydration.
- Source evidence: `src/melder/aether/spellbook/configuration/spellbook_configuration.py`.
- Adoption evidence: `src/melder/aether/spellbook/spellbook.py:5423-5475`.

## Ticket coverage map
- Epic: EPIC-2026-09-02-ordered-live-spell-disposal.
- Story: STORY-2026-09-04-ordered-disposal-binding.
- Contract task: TASK-2026-09-04-ordered-disposal-patch-contract (configuration and producer gates).
- Configuration: TASK-2026-09-04-disposal-priority-configuration (implemented/in review).
- Producer implementation: TASK-2026-09-04-ordered-disposal-bind-and-spell.
- Compiler implementation: TASK-2026-09-04-ordered-disposal-compiler-propagation.
- Creations implementation: TASK-2026-09-04-ordered-disposal-creations.
- Generic transport verification: TASK-2026-09-04-disposal-configuration-roundtrip (later).
- Runtime, replay, docs/assets, and end-to-end tasks retain their prerequisite gates.

## Unknowns and decision requests
No unresolved choice blocks configuration. Differing-host graft policy/recorded SHA joins
remain scoped to the replay task and do not justify changes to this configuration slice.
