# Component Patch: FrameACLViewBuilder

## Purpose
Provide fluent authoring over one active view-family ACL draft.

## Expected Helper Shape
- profile selection
- precision profile selection
- frame/conduit/spell/member rule setters
- common visibility helpers aligned to the view profile vocabulary
- member allow/deny helpers by exact name or pattern

## Ownership
- borrows `FrameACLBuilder`
- does not own persistence
- mutates the active typed view draft
