# Architecture Patch: Spell Index Runtime Lookup

## Objective
Add a runtime lookup path for stable `spell_index_id` values through Spellbook
and Conduit so ACL-compiled lineage outputs have a direct runtime consumer.

## Non-Goals
- no command-system integration in this patch
- no ACL/compiler changes in this patch
- no broader runtime lookup redesign

## Changed Components
- `Spellbook`
- `Conduit`
- public interfaces

## Invariants
- lookup is based on stable SpellIndex lineage id
- once a matching `SpellIndex` object is found, the runtime resolves the spell
  directly through existing Spellbook index-based helpers
- no second spell-id hop is required after the index object is resolved

## Interface Deltas
- Spellbook gains public lookup by `spell_index_id`
- Conduit gains a facade lookup by `spell_index_id`

## Migration Order
1. add Spellbook lookup
2. add Conduit facade
3. update interfaces
4. add focused tests

## Rollback
Rollback is code-level only for this patch. Do not keep a half-state where one
surface exposes spell-index lookup and the other does not.

## Ticket Coverage Matrix
- task: `tickets/tasks/2026-04-12_add_spell_index_runtime_lookup_to_spellbook_and_conduit_task.md`
