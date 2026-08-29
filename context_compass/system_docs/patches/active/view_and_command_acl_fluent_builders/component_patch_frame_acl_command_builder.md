# Component Patch: FrameACLCommandBuilder

## Purpose
Provide fluent authoring over one active command-family ACL draft.

## Expected Helper Shape
- profile selection
- precision profile selection
- frame/conduit/spell/member rule setters
- common enable/disable helpers for frame, conduit, and spell operations
- member read/invoke/write/dunder helpers

## Ownership
- borrows `FrameACLBuilder`
- does not own persistence
- mutates the active typed command draft
