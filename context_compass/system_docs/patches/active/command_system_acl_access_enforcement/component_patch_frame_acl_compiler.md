# Component Patch: FrameACLCompiler

## Before
- compiler emits broad `allowed_commands`
- no explicit frame/conduit/spell command enablement outputs

## After
- compiler emits command enablement for:
  - frame
  - conduit ids
  - spell index ids

## Interface Deltas
- compiled surface adds command enablement fields
- spell command outputs are keyed by `spell_index_id`

## State / Failure Deltas
- command runtime can now fail fast from compiled ACL state instead of only from
  missing runtime objects
