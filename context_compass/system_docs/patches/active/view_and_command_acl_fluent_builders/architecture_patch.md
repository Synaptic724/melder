# Architecture Patch: View And Command ACL Fluent Builders

## Objective
Add family-specific fluent builders for the view and command ACL families while
keeping the current frame/container/configuration lifecycle intact.

## Non-Goals
- No codegen builder redesign.
- No compiler or validator behavior changes.
- No generic metaprogrammed builder framework.

## Changed Components
- `FrameACLBuilder`
- `FrameACLViewBuilder`
- `FrameACLCommandBuilder`
- focused builder tests

## Invariants
- `FrameACLBuilder` remains the draft lifecycle owner.
- Family-specific builders only wrap an active family draft.
- Commit/discard still flow through the generic builder.
