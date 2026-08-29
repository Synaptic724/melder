# Component Patch: Conduit

## Before
- Conduit exposes spell lookup by current `spell_id`
- Conduit exposes logical lookup helpers that end at current `spell_id`
- no public facade for stable `spell_index_id`

## After
- Conduit exposes a spell lookup facade keyed by stable `spell_index_id`
- facade delegates directly to the owned Spellbook

## Interface Deltas
- new public conduit facade method keyed by `spell_index_id`

## State / Failure Deltas
- missing lineage id returns `None` through the underlying Spellbook lookup path
