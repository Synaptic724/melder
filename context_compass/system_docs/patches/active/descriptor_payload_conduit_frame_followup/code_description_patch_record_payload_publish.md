# code_description_patch_record_payload_publish

## Trigger justification
This slice changes conduit/frame publication control flow at the
descriptor/store boundary and introduces the remaining record payload contracts.

## Control-flow description
1. manager normalizes live conduit/frame state into descriptor-safe payloads
2. `ConduitRecord` / `FrameRecord` require non-empty payloads
3. `FrameDescriptor` stores those records without aggregate redesign

## Validation focus points
- payload construction
- fail-fast on empty payload
- one-payload record storage
- descriptor aggregate/index behavior remains stable
