# component_patch_conduit_record

## Purpose
Move `ConduitRecord` off flat descriptive fields and onto one required payload
field while keeping the conduit identity key stable.

## Before
- `ConduitRecord` stores descriptive conduit detail directly in top-level
  fields.

## After
- `ConduitRecord` keeps only stable identity/ownership fields plus one required
  payload field.
- Constructor fails fast when payload is missing.
- Cleanup cascades into payload cleanup.

## Validation Focus
- fail-fast on empty payload
- cleanup ownership
- record identity stability
