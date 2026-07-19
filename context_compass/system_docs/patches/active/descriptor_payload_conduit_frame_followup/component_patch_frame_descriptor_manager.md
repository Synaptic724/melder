# component_patch_frame_descriptor_manager

## Purpose
Update the direct conduit/frame publication path so the descriptor manager
constructs payload objects first, then stores them through the records.

## Before
- `_publish_conduit_record(...)` constructs a flat `ConduitRecord`.
- `_publish_frame_record(...)` constructs a flat `FrameRecord`.

## After
- manager builds descriptor-safe conduit/frame payloads
- manager stores those payloads on the records
- empty payloads fail fast before record publication

## Validation Focus
- payload construction correctness
- fail-fast on empty payloads
- no `FrameDescriptor` aggregate redesign
