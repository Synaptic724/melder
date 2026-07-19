# Architecture Patch: Frame ACL Separate Family Chains

## Objective
Replace the current frame-global ACL chain plus sidecar named-registry model
with a coherent frame-local registry of named version chains for view,
command, and codegen independently.

## Non-Goals
- no precision configuration implementation in this patch
- no room-mode policy changes
- no precision configuration implementation in this patch

## Changed Components
- `FrameACLContainer`
- `FrameACLConfigurationChain`
- `FrameACLBuilder`
- `FrameACLManager`
- `Nexus`
- `FrameLinkContract`

## Invariants
- a frame container owns separate named registries for:
  - view
  - command
  - codegen
- Rift/Nexus selection resolves one current view config, one current command
  config, and one current codegen config per frame
- same-name selection remains allowed, but is not required
- the assembled ACL snapshot remains the compiler/viewer input

## Interface Deltas
- frame container moves from one frame-global chain plus static named configs
  to three named family-chain registries
- builder targets one family + contract name per draft session
- manager/Nexus frame ACL operations become family-aware where history,
  current, or rollback semantics matter
- FrameLinkContract stores per-frame ACL selection across the three families

## Migration Order
1. refactor container ownership to separate family chains
2. refactor builder draft/commit to target one family chain
3. add per-frame ACL selection
4. refactor manager/Nexus facades and assembled snapshot creation
5. wire downstream cache invalidation and live viewer refresh
6. update focused tests

## Rollback
Rollback is code-level only for this patch. Do not attempt mixed hybrid state.

## Ticket Coverage Matrix
- task: `tickets/tasks/2026-04-11_refactor_frame_acl_container_to_separate_family_chains_task.md`
