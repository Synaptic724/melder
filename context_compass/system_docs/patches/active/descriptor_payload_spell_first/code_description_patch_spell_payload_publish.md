# code_description_patch_spell_payload_publish

## Trigger justification
This slice changes the spell publication control flow at the descriptor/store
boundary and introduces the first descriptor payload contract.

## Control-flow description
1. spell profile is normalized at publication time
2. profile exports one descriptor-safe spell payload
3. `FrameDescriptorManager` builds `SpellRecord(payload=...)`
4. `FrameDescriptor` stores and indexes the record normally

## Validation focus points
- payload sanitization
- fail-fast on empty payload
- `SpellRecord` one-payload storage
- descriptor aggregate/index behavior remains stable
