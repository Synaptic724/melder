# Component Patch: FrameACLBuilder

## New Entry Points
- `begin_view_change(...) -> FrameACLViewBuilder`
- `begin_command_change(...) -> FrameACLCommandBuilder`

## New Internal Requirements
- require active typed view draft
- require active typed command draft

## Invariants
- one active draft at a time
- family-specific builders do not bypass generic commit/discard
