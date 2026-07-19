# component_patch_frame_descriptor_manager

## Component purpose and boundary in current architecture
`FrameDescriptorManager` owns the direct publish/store path into
`FrameDescriptor`.

## Before/after behavior summary
- Before:
  - spell publication normalizes split spell-profile shards and builds
    `SpellRecord(binding_profile=..., resolution_profile=..., detailed_profile=...)`
- After:
  - spell publication builds one sanitized spell descriptor payload
  - stores it through `SpellRecord(payload=...)`
  - fail-fast if the spell payload cannot be published

## Validation expectations
- spell publication stores one payload field
- general profiles are rejected or otherwise blocked from publication per the
  accepted contract
- frame/conduit publication paths remain unchanged in this slice
