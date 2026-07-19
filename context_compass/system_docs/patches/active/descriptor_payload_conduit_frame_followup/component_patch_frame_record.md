# component_patch_frame_record

## Purpose
Move `FrameRecord` off flat descriptive posture/topology fields and onto one
required payload field while keeping the frame identity stable.

## Before
- `FrameRecord` stores descriptive frame posture and topology directly in
  top-level fields.

## After
- `FrameRecord` keeps stable identity fields plus one required payload field.
- Constructor fails fast when payload is missing.
- Cleanup cascades into payload cleanup.

## Validation Focus
- fail-fast on empty payload
- cleanup ownership
- frame identity stability
