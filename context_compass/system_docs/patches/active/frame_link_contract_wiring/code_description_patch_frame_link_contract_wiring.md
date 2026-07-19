# Frame Link Contract Wiring Code Description Patch

## Control Flow
1. start from descriptor truth plus compiled ACL access output
2. optionally narrow the frame-scoped contract through a downstream
   `FrameLinkContractProfile`
3. build derived frame/conduit/spell link metadata from the visible sections
4. create view-safe `FrameLink` objects
5. assemble them into one `FrameView`

## Error Semantics
- type mismatches should fail fast
- missing visible descriptor records should fail fast because the compiled ACL
  output is expected to align with descriptor truth

## Non-Goals
- no incremental update/diff engine
- no `FrameViewer` query strategy logic
- no binding/execution behavior
