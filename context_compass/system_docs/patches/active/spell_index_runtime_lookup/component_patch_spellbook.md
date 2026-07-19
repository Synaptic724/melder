# Component Patch: Spellbook

## Before
- Spellbook can find a lineage object by logical signature
- Spellbook can resolve a spell from a `SpellIndex` object internally
- no public lookup by stable `spell_index_id`

## After
- Spellbook exposes a stable-lineage lookup by `spell_index_id`
- the implementation scans local and contracted `SpellIndex` attachments and
  then uses existing index-based spell resolution helpers

## Interface Deltas
- new public lookup method keyed by `spell_index_id`

## State / Failure Deltas
- missing lineage id returns `None` instead of fabricating a spell-id path
