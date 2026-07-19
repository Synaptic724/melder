# Component Patch: FrameACLBuilder

## Before
`FrameACLBuilder` only exposed the generic family draft lifecycle.

## After
`FrameACLBuilder` exposes one convenience entrypoint for codegen drafts:
- `begin_codegen_change(...)`

This method still uses the same underlying draft lifecycle:
- begin one codegen draft
- return the fluent codegen builder
- keep commit/discard on the generic builder

## Interface Delta
- Added `begin_codegen_change(...) -> FrameACLCodegenBuilder`
- Added `_require_active_codegen_configuration(...)`
- Added codegen profile/precision-profile mutation helpers used by the fluent
  builder

## Invariants
- At most one active draft session still exists at a time.
- The generic builder remains the owner of draft lifecycle state.
