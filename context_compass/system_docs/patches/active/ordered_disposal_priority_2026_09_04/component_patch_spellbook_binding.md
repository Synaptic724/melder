# Component patch: Spellbook Core binding inputs

## Purpose and boundary
Spellbook owns configuration, registries, and admission. This delta changes only the disposal
inputs it forwards when creating each active or inactive Spell.

## Before / after
- Before: the first bind chooses one candidate frozenset for every subsequent bind in the book.
- After: each bind forwards its own names, the current configured vocabulary, and priority.
- Remove the first-bind latch from slots, initialization, cleanup, and selection.
- Remove conjure's obsolete latch-conditioned frozenset/flag recheck. Bind establishes metadata once.

## Interface deltas
Public bind and bind_inactive retain their existing parameters and return spell_id.
The internal Bind call gains separate per-spell names and the configured priority bool.
An absent name property on a raw configuration contributes no book names; the priority
property is already guaranteed by the configuration slice.

## State and lifecycle
No new cached policy, lookup map, or lifecycle owner. Existing admitted transaction windows,
staged-member handling, hooks, emissions, and registration remain intact.

## Failure modes
Preserve current input, existence, admission, collision, and index-ownership errors.
Do not add state probes, configuration snapshots, or protections against private mutation.

## Dependencies and ordering
Read the configuration defaults before producer implementation. Match and fingerprint before
the resulting Spell is registered. Existing Spells moved/shared later retain their own metadata.

## Validation
Verify independent active/inactive inputs, both priority modes, raw configuration, fluent
SpellBinder passthrough, and unchanged selected index membership. A conjure smoke check must
accept the new list without introducing a second matching pass.

## Open decisions
None for this producer boundary; replay host-policy decisions stay in the replay task.
