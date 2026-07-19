# component_patch_spell_record

## Component purpose and boundary in current architecture
`SpellRecord` is the canonical descriptor-owned spell record stored inside
`FrameDescriptor`.

## Before/after behavior summary
- Before:
  - `SpellRecord` stores split spell-profile shards:
    - `binding_profile`
    - `resolution_profile`
    - `detailed_profile`
- After:
  - `SpellRecord` stores one `payload` field
  - identity/ownership fields stay intact
  - payload is required and fail-fast when missing

## Validation expectations
- constructor rejects empty payload
- cleanup nulls payload
- record key behavior stays unchanged
