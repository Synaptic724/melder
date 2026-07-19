# Component Patch: FrameACLCodegenBuilder

## Before
No family-specific fluent authoring layer existed for codegen ACL drafts.

## After
`FrameACLCodegenBuilder` provides fluent authoring over one active codegen draft.

## Expected Surface
- base profile selection
- precision profile selection
- frame/conduit/spell/capability rule helpers
- import enable/disable
- import allow/deny roots
- builtin allow/deny
- unsafe reflection toggle
- dunder access toggle
- recursive codegen toggle
- commit/discard passthrough

## Ownership
- Borrows the owning `FrameACLBuilder`
- Does not own the persisted configuration chain
- Mutates the active codegen draft in place under lock

## Invariants
- Cannot operate without an active codegen draft
- Returns itself from fluent mutation methods
- Commits through the generic builder
