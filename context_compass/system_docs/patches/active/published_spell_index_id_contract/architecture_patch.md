# Architecture Patch: Published Spell Index Id Contract

## Patch Scope and Non-Goals
Scope:
- rename the published stable spell lineage field from `lineage_id` to
  `spell_index_id`
- keep the underlying meaning unchanged

Non-goals:
- renaming unrelated internal lineage variables
- adding compatibility aliases
- changing ACL behavior beyond the published identifier name

## Changed-Components Matrix
| component | change |
|---|---|
| `SpellRecord` | rename published stable identity field |
| `FrameDescriptorManager` | publish the field under the new constructor name |
| `FrameViewer` and general spell/frame views | emit `spell_index_id` instead of `lineage_id` |

## Interface and Boundary Deltas
- public descriptor/viewer outputs now use `spell_index_id`
- the value still comes from `spell.spell_index.id`

## Cross-Component Invariants
- canonical record key remains `(origin_spellbook_id, spell_id)`
- stable SpellIndex identity remains published alongside `spell_id`
- public output must not mix `lineage_id` and `spell_index_id`

## Migration / Rollout Order
1. rename `SpellRecord` field and constructor argument
2. rename descriptor-manager publish callsite
3. rename viewer/view-profile output fields and comparisons
4. update focused tests and docs

## Rollback Strategy
- revert the field name back to `lineage_id` everywhere on the published/viewer
  surface if the sweep cannot be completed coherently in one tranche

## Validation Expectations and Evidence Plan
- focused descriptor/viewer tests should stay green after the rename

## Ticket Coverage Map
- task:
  - `tickets/tasks/2026-04-11_rename_published_spell_lineage_id_to_spell_index_id_task.md`

## Unknowns and Decision Requests
- none for this slice
