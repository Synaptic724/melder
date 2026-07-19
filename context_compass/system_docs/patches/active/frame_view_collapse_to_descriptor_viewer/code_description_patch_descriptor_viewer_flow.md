# Code Description Patch: Descriptor-Driven Viewer Flow

## Control Flow
1. Resolve descriptor for each target frame.
2. Resolve current ACL configuration for each frame.
3. Validate configuration against descriptor payload contracts.
4. Compile ACL access surface for each frame.
5. Build viewer-owned target/grouping/summary data directly from:
   - descriptor truth
   - compiled ACL visibility
6. Expose viewer tools through `FrameViewerProfile`.

## Key Behavior
- Frame payload, conduit payload, and spell payload visibility stay filtered by
  compiled ACL output.
- Viewer methods are responsible for shaping the returned data, but not for
  widening hidden fields/sections.

## Explicit Non-Goals
- no raw object acquisition
- no codegen execution
- no hidden second snapshot layer recreated under another name
