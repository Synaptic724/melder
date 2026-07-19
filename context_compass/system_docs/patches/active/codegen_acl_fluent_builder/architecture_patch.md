# Architecture Patch: Codegen ACL Fluent Builder

## Objective
Add a dedicated codegen-family fluent ACL builder without replacing the current
frame/container/configuration architecture.

## Non-Goals
- No new ACL storage model.
- No view or command fluent builder in this slice.
- No compiled-access-surface behavior changes.

## Changed Components
- `FrameACLBuilder`
- `FrameACLCodegenBuilder`
- focused builder tests

## Invariants
- `FrameACLContainer` remains the owner of builder lifecycle and commit paths.
- `FrameACLBuilder` remains the generic draft session owner.
- `FrameACLCodegenBuilder` is only a fluent layer over an active codegen draft.
- Committed results remain `FrameACLCodegenConfiguration` revisions.

## Migration Order
1. Add the family-specific fluent builder file.
2. Wire `FrameACLBuilder.begin_codegen_change(...)`.
3. Validate with focused unit tests.

## Rollback
If the fluent layer proves unstable, remove the family-specific entrypoint and
fall back to the existing generic builder draft path.
