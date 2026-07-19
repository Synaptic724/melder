# Frame Viewer Query Flow Code Description Patch

## Control Flow
1. consume attached `FrameView` objects
2. inspect their `FrameLink` contents
3. expose deterministic read/query helpers over:
   - frame names
   - links by frame
   - links by kind
   - link lookup helpers

## Error Semantics
- missing views should fail fast with clear messages
- invalid inputs should fail fast

## Non-Goals
- no fuzzy search
- no mutation
- no direct runtime-object access
